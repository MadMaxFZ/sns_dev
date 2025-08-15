# -*- coding: utf-8 -*-

#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import math
import time
from multiprocessing import shared_memory as shm

import astropy.units as u
import numpy as np
import vispy.visuals.transforms as trx
from vispy.color import *
from vispy.scene.visuals import (Markers, Polygon, XYZAxis)

from datastore import vec_type
from performance_monitor import PerformanceMonitor
from performance_overlay import PerformanceOverlay
from sim_body import MIN_FOV, SimBody
from sim_skymap import SkyMap
from simbody_visual import Planet

# these quantities can be served from DATASTORE class
MIN_SYMB_SIZE = 5
MAX_SYMB_SIZE = 30
EDGE_COLOR = Color('red')
EDGE_COLOR.alpha = 0.6
ST = trx.STTransform
MT = trx.MatrixTransform
SUN_COLOR = Color(tuple(np.array([253, 184, 19]) / 256))

DEF_MARKS_INIT = dict(scaling=False,
                      alpha=1,
                      antialias=1,
                      spherical=True,
                      light_color=SUN_COLOR,
                      light_position=(0.01, 0.01, 0.01),
                      light_ambient=0.3,
                      )
DEF_MARKS_DATA = dict(pos=None,
                      size=None,
                      edge_width=None,
                      edge_width_rel=None,
                      edge_color=EDGE_COLOR,
                      face_color=SUN_COLOR,
                      symbol=None,
                      )

_pm_e_alpha = 0.6
_cm_e_alpha = 0.6
_SCALE_FACTOR = np.array([50.0,] * 3)


def from_pos(pos, tgt_pos, tgt_R):
    rel_2pos = (pos - tgt_pos)
    dist = np.linalg.norm(rel_2pos)
    dist_unit = tgt_R / tgt_R.value
    if dist < 1e-09:
        dist = 0.0 * dist_unit
        rel_pos = np.zeros((3,), dtype=type(tgt_pos))
        fov = MIN_FOV
    else:
        fov = np.float64(1.0 * math.atan(tgt_R.value / dist))

    return {"rel_pos": rel_2pos * dist_unit,
            "dist": dist * dist_unit,
            "fov": fov,
            }


class StarSystemVisuals:
    """
    """
    def __init__(self, body_names=None):
        """
        Constructs a collection of Visuals that represent entities in the system model,
        updating periodically based upon the quantities propagating in the model.
        TODO:   Remove the model from this module. The data required here must now
                be obtained using Signals to the QThread that the model will be running within.
        Parameters
        ----------
        body_names   : list of str
            list of SimBody names to make visuals for
        """
        self._new_states = None
        self._IS_INITIALIZED = False
        self._body_names   = []
        self._bods_pos     = []
        self._scene        = None
        self._skymap       = None
        self._planets      = {}      # a dict of Planet visuals
        self._tracks       = {}      # a dict of Polygon visuals
        self._symbols      = []
        self._symbol_sizes = []
        self._view         = None
        self._curr_camera  = None
        self._pos_rel2cam  = None
        self._frame_viz    = None
        self._plnt_markers = None
        self._cntr_markers = None
        self._subvizz      = None
        self._agg_cache    = None
        self._vizz_data    = None
        self._body_radsets = None
        self.dist_unit     = u.km
        self._last_t       = None
        self._curr_t       = None
        
        # Performance optimizations
        self._use_instancing = True  # Enable GPU instancing for similar objects
        self._batch_size = 1000  # Batch size for updating visual data
        self._frustum_culling = True  # Enable view frustum culling
        self._lod_enabled = True  # Enable level of detail
        self._max_visible_objects = 1000  # Maximum number of visible objects
        self._update_interval = 1/60  # Target 60 FPS updates
        
        # Texture optimization settings
        self._texture_compression = True
        self._mipmap_enabled = True
        self._max_texture_size = 2048
        
        # Advanced optimization settings
        self._optimization_settings = {
            'occlusion_culling': True,     # Use occlusion culling for hidden objects
            'geometry_instancing': True,    # Use geometry instancing for similar objects
            'texture_streaming': True,      # Stream textures based on distance
            'mesh_lod': True,              # Use mesh LOD for distant objects
            'shadow_quality': 'medium',     # shadow quality (high, medium, low, off)
            'particle_quality': 'medium',   # particle effect quality
            'max_draw_distance': 1e9,       # Maximum draw distance in km
            'texture_pool_size': 512,      # Size of texture pool in MB
            'geometry_pool_size': 256,      # Size of geometry pool in MB
        }
        
        # LOD distance thresholds (in km)
        self._lod_thresholds = {
            'ultra': 1e5,    # Full detail
            'high': 1e6,     # High detail
            'medium': 1e7,   # Medium detail
            'low': 1e8,      # Low detail
            'minimal': 1e9   # Minimal detail
        }
        
        # Resource pools
        self._texture_pool = {}  # Cached textures
        self._geometry_pool = {} # Cached geometries
        self._shader_cache = {}  # Cached shaders
        
        # Initialize resource manager
        self._init_resource_manager()
        
        # Initialize performance monitoring
        self._perf_monitor = PerformanceMonitor()
        self._perf_overlay = None  # Will be initialized when view is set
        
        # Connect performance signals
        self._perf_monitor.performance_update.connect(self._on_performance_update)
        self._perf_monitor.warning.connect(self._on_performance_warning)
        
        if body_names:
            self._body_names = [n for n in body_names]
        self._body_count   = len(self._body_names)
        self._bods_pos     = None
        self._buff1 = None
        self._buff0 = None
        self._new_states = None

    '''--------------------------- END StarSystemVisuals.__init__() -----------------------------------------'''

    def generate_visuals(self, view,  agg_data):
        """
        Parameters
        ----------
        view        :  View object
                            The view in which the visuals are to be rendered.
        agg_data    :  dict
                            The data to be used for generating the visuals.

        Returns
        -------
        None            : No return value, however all of the visuals for the sim rendering are
                          created here, collected together and then added to the scene.
        """
        self._last_t = time.perf_counter()
        self._agg_cache = agg_data
        self._view = view
        self._scene = self._view.scene
        self._curr_camera = self._view.camera
        self._skymap = SkyMap(parent=self._scene)
        self._frame_viz = XYZAxis(parent=self._scene)  # set parent in MainSimWindow ???
        self._frame_viz.transform = MT()
        self._frame_viz.transform.scale((1e+09, 1e+09, 1e+09))

        self._buff0 = shm.SharedMemory(create=False,
                                       name="state_buff0")
        self._buff1 = shm.SharedMemory(create=False,
                                       name="state_buff1")

        self._bods_pos = np.ndarray((11, 3, 3), dtype=vec_type)
        self._bods_pos = np.array(self._buff0.buf)
        print(f"[:, :,] => {self._bods_pos.shape}")
        # check = [self._bods_pos[n, 1] for n in range(0, self._body_count - 1)]
        # print(f"[:, :,] => {check.shape}")
        # self._bods_pos = list(self._agg_cache['pos'].values())

        for name in self._body_names:
            self._generate_planet_viz(body_name=name)
            print(f'Planet Visual for {name} created...')
            if name != self._agg_cache['is_primary']:
                self._generate_trajct_viz(body_name=name)
                print(f'Trajectory Visual for {name} created...')

        self._generate_marker_viz()
        self._subvizz = dict(sk_map=self._skymap,
                             r_fram=self._frame_viz,
                             p_mrks=self._plnt_markers,
                             # c_mrks=self._cntr_markers,
                             tracks=self._tracks,
                             surfcs=self._planets,
                             )
        self._upload2view()
        
        # Initialize performance overlay
        if not self._perf_overlay and hasattr(view, 'native'):
            self._perf_overlay = PerformanceOverlay(view.native)
            self._perf_overlay.show()
        
        # Start frame timing
        self._perf_monitor.start_frame()
        
        # Generate visuals
        # super().generate_visuals(view, agg_data)
        
        # End frame and update stats
        self._perf_monitor.end_frame(len(self._planets))
        
        self._curr_t = time.perf_counter()
        print(f'Visuals generated in {(self._curr_t - self._last_t):.4f} seconds...')

    def _generate_planet_viz(self, body_name):
        """ Generate Planet visual object for each SimBody
        """
        viz_dat = {}
        [viz_dat.update({k: v[body_name]}) for k, v in self._agg_cache.items()]     # if list(v.keys())[0] == body_name]
        plnt = Planet(body_name=body_name,
                      rows=18,
                      color=Color((1, 1, 1, self._agg_cache['body_alpha'][body_name])),
                      edge_color=Color((0, 0, 0, 0)),  # sb.base_color,
                      parent=self._scene,
                      visible=True,
                      method='oblate',
                      vizz_data=viz_dat,
                      body_radset=self._agg_cache['radius'][body_name]
                      )
        plnt.transform = trx.MatrixTransform()  # np.eye(4, 4, dtype=np.float64)
        self._planets.update({body_name: plnt})

    def _generate_trajct_viz(self, body_name):
        """ Generate Polygon visual object for each SimBody orbit
        """
        t_color = Color(self._agg_cache['body_color'][body_name])
        t_color.alpha = self._agg_cache['track_alpha'][body_name]
        poly = Polygon(pos=self._agg_cache['track_data'][body_name],
                       border_color=t_color,
                       triangulate=False,
                       parent=self._scene,
                       )
        poly.transform = trx.MatrixTransform()  # np.eye(4, 4, dtype=np.float64)
        self._tracks.update({body_name: poly})

    def _generate_marker_viz(self):
        # put init of markers into a method
        self._symbols = [pl.mark for pl in self._planets.values()]
        self._plnt_markers = Markers(parent=self._scene, **DEF_MARKS_INIT)  # a single instance of Markers
        # self._cntr_markers = Markers(parent=self._scene,
        #                              symbol=['+' for _ in range(self._body_count)],
        #                              size=[(MIN_SYMB_SIZE - 2) for _ in range(self._body_count)],
        #                              **DEF_MARKS_INIT)  # another instance of Markers
        # self._plnt_markers.parent = self._mainview.scene
        # self._cntr_markers.set_data(symbol=['+' for _ in range(self._body_count)])

    def _upload2view(self):
        for k, v in self._subvizz.items():
            if "_" in k:
                print(k)
                self._scene.parent.add(v)
            else:
                [self._scene.parent.add(t) for t in v.values()]
        self._IS_INITIALIZED = True

    def _init_resource_manager(self):
        """Initialize the resource management system"""
        self._texture_memory_used = 0
        self._geometry_memory_used = 0
        self._active_resources = set()
        
        # Register cleanup handler
        import atexit
        atexit.register(self._cleanup_resources)

    def _cleanup_resources(self):
        """Clean up GPU resources"""
        for tex in self._texture_pool.values():
            if hasattr(tex, 'delete'):
                tex.delete()
        for geo in self._geometry_pool.values():
            if hasattr(geo, 'delete'):
                geo.delete()
        self._texture_pool.clear()
        self._geometry_pool.clear()

    def _manage_lod(self, visual, distance):
        """Manage level of detail based on distance"""
        if not self._optimization_settings['mesh_lod']:
            return 'ultra'
            
        for level, threshold in self._lod_thresholds.items():
            if distance < threshold:
                return level
        return 'minimal'

    def _stream_texture(self, visual, distance):
        """Stream appropriate texture based on distance"""
        if not self._optimization_settings['texture_streaming']:
            return
            
        if not hasattr(visual, 'texture'):
            return
            
        # Determine required texture resolution
        if distance < self._lod_thresholds['ultra']:
            target_size = 2048
        elif distance < self._lod_thresholds['high']:
            target_size = 1024
        elif distance < self._lod_thresholds['medium']:
            target_size = 512
        else:
            target_size = 256
            
        # Check if we need to change texture
        current_size = getattr(visual.texture, 'size', (0, 0))[0]
        if current_size != target_size:
            self._load_optimized_texture(visual, target_size)

    def _load_optimized_texture(self, visual, target_size):
        """Load and optimize texture for the given size"""
        if not hasattr(visual, 'texture_source'):
            return
            
        # Check texture pool
        cache_key = f"{visual.texture_source}_{target_size}"
        if cache_key in self._texture_pool:
            visual.texture = self._texture_pool[cache_key]
            return
            
        # Load and resize texture
        try:
            from PIL import Image
            img = Image.open(visual.texture_source)
            img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
            # Convert to optimal format and create texture
            img = img.convert('RGBA')
            new_texture = visual.texture.__class__(data=img)
            
            # Update pool if within size limit
            texture_size = target_size * target_size * 4  # RGBA
            if self._texture_memory_used + texture_size <= self._optimization_settings['texture_pool_size'] * 1024 * 1024:
                self._texture_pool[cache_key] = new_texture
                self._texture_memory_used += texture_size
            
            visual.texture = new_texture
            
        except Exception as e:
            logging.error(f"Texture optimization failed: {e}")

    def _update_visual_batches(self, start_idx=0, batch_size=None):
        """Update visuals in batches with advanced optimizations"""
        if batch_size is None:
            batch_size = self._batch_size
            
        end_idx = min(start_idx + batch_size, len(self._planets))
        
        # Group similar objects for instancing
        instance_groups = {}
        
        for planet in list(self._planets.values())[start_idx:end_idx]:
            if not hasattr(planet, 'transform'):
                continue
                
            # Get position and check visibility
            pos = planet.transform.map([0, 0, 0])
            distance = np.linalg.norm(pos)
            
            # Apply draw distance culling
            if distance > self._optimization_settings['max_draw_distance']:
                continue
            
            # Apply occlusion culling
            if self._optimization_settings['occlusion_culling'] and not self._is_visible(planet):
                continue
            
            # Apply LOD
            lod_level = self._manage_lod(planet, distance)
            
            # Stream appropriate texture
            self._stream_texture(planet, distance)
            
            # Group for instancing if possible
            if self._optimization_settings['geometry_instancing']:
                instance_key = (planet.__class__, getattr(planet, 'geometry_key', None))
                if instance_key[1] is not None:
                    instance_groups.setdefault(instance_key, []).append(planet)
                    continue
            
            # Update individual visual
            planet.update()
        
        # Update instanced groups
        for group in instance_groups.values():
            if len(group) > 1:
                self._update_instanced_group(group)

    def _update_instanced_group(self, group):
        """Update a group of similar objects using instancing"""
        if not group:
            return
            
        # Collect transforms
        transforms = [obj.transform.matrix for obj in group]
        
        # Update first object with instancing
        primary = group[0]
        if hasattr(primary, 'update_instanced'):
            primary.update_instanced(transforms)
        else:
            # Fallback to individual updates if instancing not supported
            for obj in group:
                obj.update()

    def _optimize_shaders(self):
        """Optimize and cache shaders"""
        if not self._shader_cache:
            from vispy.gloo import Program
            
            # Basic shader for distant objects
            self._shader_cache['distant'] = Program(
                # Simplified vertex shader
                vertex="""
                uniform mat4 transform;
                attribute vec3 position;
                void main() {
                    gl_Position = transform * vec4(position, 1.0);
                }
                """,
                # Simplified fragment shader
                fragment="""
                uniform vec4 color;
                void main() {
                    gl_FragColor = color;
                }
                """
            )

    def _apply_performance_settings(self):
        """Apply performance optimization settings to all visual objects"""
        for planet in self._planets.values():
            if hasattr(planet, 'set_gl_state'):
                # Enable GPU optimizations
                planet.set_gl_state('translucent', depth_test=True, cull_face='back')
                
                # Apply texture optimizations if supported
                if hasattr(planet, 'texture') and self._texture_compression:
                    planet.texture.set_mipmap(self._mipmap_enabled)
                    planet.texture.resize(max_size=self._max_texture_size)

    def update_vizz(self, agg_data):
        """Update the visualization with performance monitoring"""
        if not self._IS_INITIALIZED:
            return
        
        # Start frame timing
        self._perf_monitor.start_frame()
        
        # Start batch timing
        self._perf_monitor.start_batch()
        
        # Update visuals in batches
        total_visuals = len(self._planets)
        for start_idx in range(0, total_visuals, self._batch_size):
            self._update_visual_batches(start_idx)
        
        # End batch timing
        self._perf_monitor.end_batch()
        
        # Start draw timing
        self._perf_monitor.start_draw()
        
        # Update remaining visual elements
        self._last_t = self._curr_t
        self._symbol_sizes = self.get_symb_sizes()  # update symbol sizes based upon FOV of body
        _p_face_colors = []
        # _c_face_colors = []
        _edge_colors = []

        self._agg_cache = agg_data

        self._new_states = self._buff0.buf
        print(f"new_states.shape = {self._new_states.shape}")
        pass
        # self._bods_pos = list(self._agg_cache['pos'].values())

        for n, sb_name in enumerate(self._body_names):                                                    # <--
            x_ax = self._agg_cache['axes'][sb_name][0]
            y_ax = self._agg_cache['axes'][sb_name][1]
            z_ax = self._agg_cache['axes'][sb_name][2]
            RA, DEC, W = self._new_states[n, :, 2]
            # RA   = self._agg_cache['rot'][sb_name][0]
            # DEC  = self._agg_cache['rot'][sb_name][1]
            # W    = self._agg_cache['rot'][sb_name][2]
            # pos  = self._agg_cache['pos'][sb_name]
            pos = self._bods_pos[n]
            parent = self._agg_cache['parent_name'][sb_name]
            is_primary = self._agg_cache['is_primary'][sb_name]

            if self._planets[sb_name].visible:
                xform = self._planets[sb_name].transform
                xform.reset()
                xform.rotate(W * np.pi / 180, z_ax)
                xform.rotate(DEC * np.pi / 180, y_ax)
                xform.rotate(RA * np.pi / 180, x_ax)
                # if not is_primary:
                #     xform.scale(_SCALE_FACTOR)

                xform.translate(pos.value)
                self._planets[sb_name].transform = xform

            if not is_primary:
                self._tracks[sb_name].transform.reset()
                self._tracks[sb_name].transform.translate(self._agg_cache['pos'][parent].value)

            # TODO: these do not require updating unless they change...
            _pf_clr = Color(self._agg_cache['body_color'][sb_name])
            _pf_clr.alpha = self._agg_cache['body_alpha'][sb_name]
            # _cf_clr = _pf_clr
            _p_face_colors.append(_pf_clr)
            # _c_face_colors.append(_cf_clr)

        self._plnt_markers.set_data(pos=np.array(self._bods_pos),
                                    face_color=ColorArray(_p_face_colors),
                                    edge_color=Color([1, 0, 0, _pm_e_alpha]),
                                    size=self._symbol_sizes,
                                    symbol=self._symbols,
                                    )
        # self._cntr_markers.set_data(pos=np.array(self._bods_pos),
        #                             face_color=ColorArray(_c_face_colors),
        #                             edge_color=[0, 1, 0, _cm_e_alpha],
        #                             size=MIN_SYMB_SIZE,
        #                             symbol=['diamond' for _ in range(self._body_count)],                  # <--
        #                             )
        self._scene.update()
        self._curr_t = time.perf_counter()
        update_time = self._curr_t - self._last_t
        print(f'Visuals updated in {update_time:.4f} seconds...')
        logging.info("\nSYMBOL SIZES :\t%s", self._symbol_sizes)
        logging.info("VISUAL UPDATE TIME :\t%s", update_time)
        # logging.info("\nCAM_REL_DIST :\n%s", [np.linalg.norm(rel_pos) for rel_pos in self._pos_rel2cam])

    def get_symb_sizes(self, obs_cam=None):
        """
            Calculates the s=ize in pixels at which a SimBody will appear in the view from
            the perspective of a specified camera.
        Parameters
        ----------
        obs_cam :  A Camera object from which the apparent sizes are measured

        Returns
        -------
        An np.array containing a pixel width for each SimBody

        TODO: instead of only symbol sizes, include face and edge color, etc.
                  Probably rename this method to 'get_mark_data(self, from_cam=None)'
        """
        if not obs_cam:
            obs_cam = self._curr_camera

        symb_sizes = []
        sb_name: str
        for sb_name in self._body_names:                                                       # <--
            body_fov = from_pos(obs_cam.center,
                                self._agg_cache['pos'][sb_name].value,
                                self._agg_cache['radius'][sb_name][0],
                                )['fov']
            pix_diam = 0
            raw_diam = math.ceil(self._scene.parent.size[0] * body_fov / obs_cam.fov)                # <--

            if raw_diam < MIN_SYMB_SIZE:
                pix_diam = MIN_SYMB_SIZE
            elif raw_diam < MAX_SYMB_SIZE:
                pix_diam = raw_diam
            elif raw_diam >= MAX_SYMB_SIZE:
                pix_diam = 0
                self._planets[sb_name].visible = True
            else:
                self._planets[sb_name].visible = False

            symb_sizes.append(pix_diam)

        return np.array(symb_sizes)

    @staticmethod
    def _check_simbods(simbods=None):
        """ Make sure that the simbods argument actually consists of
            a dictionary of SimBody objects.
        """
        check = True
        if simbods is None:
            print("Must provide a SimBody dict... FAILED")
            check = False
        elif type(simbods) is not dict:
            print("must provide a dictionary of SimBody objects... FAILED")
            check = False
        else:
            for key, val in simbods.items():
                if type(val) is not SimBody:
                    print(key, "is NOT a SimBody... FAILED.")
                    check = False

        return check

    @property
    def bods_pos(self):
        return self._bods_pos

    @property
    def skymap(self):
        if self._skymap is None:
            print("No SkyMap defined...")
        else:
            return self._skymap

    @skymap.setter
    def skymap(self, new_skymap=None):
        if type(new_skymap) is SkyMap:
            self._skymap = new_skymap
        else:
            print("Must provide a SkyMap object...")

    @property
    def planets(self, name=None):
        if name:
            return self._planets[name]
        else:
            return self._planets

    @property
    def vizz_bounds(self):
        max_r = np.max(np.linalg.norm(self.bods_pos)) / 2
        rng = (-max_r, max_r)

        return rng

    def _on_performance_update(self, stats):
        """Handle performance updates"""
        if self._perf_overlay:
            self._perf_overlay.update_metrics(stats)
            
        # Adjust visual quality based on performance
        if stats['fps'] < 30:
            self._batch_size = max(100, self._batch_size - 100)
            self._max_visible_objects = max(100, self._max_visible_objects - 100)
            if hasattr(self, '_curr_camera'):
                # Reduce LOD when performance is low
                self._curr_camera.fov = min(90, self._curr_camera.fov + 5)
        elif stats['fps'] > 58:
            self._batch_size = min(2000, self._batch_size + 100)
            self._max_visible_objects = min(2000, self._max_visible_objects + 100)
            if hasattr(self, '_curr_camera'):
                # Restore LOD when performance is good
                self._curr_camera.fov = max(MIN_FOV, self._curr_camera.fov - 1)

    def _on_performance_warning(self, warning):
        """Handle performance warnings"""
        logging.warning(f"Performance warning: {warning}")

    def _end_draw(self):
        # End draw timing
        self._perf_monitor.end_draw()
        
        # End frame and update stats
        self._perf_monitor.end_frame(len(self._planets))

if __name__ == "__main__":

    def main():
        print("MAIN FUNCTION...")

    main()
