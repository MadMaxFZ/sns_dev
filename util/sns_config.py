#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import logging.config
import os
import pickle

from datastore import earth_rot_elements_at_epoch, get_texture_data
from pathlib2 import Path
from poliastro.bodies import *
from poliastro.constants import J2000_TDB
from poliastro.core.fixed import *
from poliastro.frames.fixed import *
from poliastro.frames.fixed import MoonFixed as LunaFixed

P = Path("c:")
SNS_SOURCE_PATH = P / '_Projects' / 'sns_dev' / 'src'  # "c:\\_Projects\\sns2\\src\\"
os.chdir(SNS_SOURCE_PATH)

# logging.basicConfig(filename=SNS_SOURCE_PATH / "../logs/sns_defs.log",
#                     level=logging.ERROR,
#                     format="%(funcName)s:\t%(levelname)s:%(asctime)s:\t%(message)s",
#                     )

#   Here's a few dreadful global variables
DEF_UNITS = u.km
DEF_EPOCH0 = J2000_TDB

PICKL_FNAME = P / "_data_store.pkl"
vec_type = type(np.zeros((3,), dtype=np.float64))
# DEF_CAM_STATE = {'center': (-8.0e+08, 0.0, 0.0),
#                  'scale_factor': 0.5e+08,
#                  'rotation1': Quaternion(-0.5, +0.5, -0.5, -0.5),
#                  }


class SystemDataStore:
    """ The purpose of this class is to provide a set of bodies to use as a default.
        A dict is constructed with three primary items:

            SYS_PARAMS
            BODY_PARAMS
            VIZZ_PARAMS

        The BODY and VIZZ parameters are dicts with the body names as a key,
        with each containing it's own set of parameters.
        The SYS parameters are just a few global values.
    """
    def __init__(self):
        """ Collect and construct a dict to contain the basic default parameters for
            a standard set of body object in the simulation.
            The basic technique is that a series of lsts, each with a parameter for each body,
            are recombined into a dictionary where the body is the key with the parameters for
            that body are grouped beneath it. The TYPE and MARK fields are determined according
            to the parent of the body.
        """
        self._dist_unit  = DEF_UNITS
        self._body_names = None
        self._datastore  = self._setup_datastore()

    def _setup_datastore(self):
        # attempt to read pickle file
        # TODO:: FIX THIS!! I erased .pkl file, yet the code indicated it loaded data from disk...
        if PICKL_FNAME.exists():
            with open(PICKL_FNAME, 'rb') as f:
                print("Loaded existing pickle file...")
                return pickle.load(f)

        # if the file doesn't exist, generate the data
        else:
            print("Existing pickle file not found. Generating a new one...")
            # attempt to write pickle file
            try:
                _data = self._generate_datastore()
                with open("_data_store.pkl", 'wb') as f:
                    pickle.dump(_data, f)
                    print("New pickle file created...")

                return _data

            except IOError:
                print("Could not write pickle file...")

    def _generate_datastore(self):
        DEF_EPOCH = DEF_EPOCH0  # default epoch

        # System Parameters dict
        SYS_PARAMS = dict(sys_name="Sol",
                          def_epoch=DEF_EPOCH,
                          dist_unit=self._dist_unit,
                          periods=365,
                          spacing=24 * 60 * 60 * u.s,  # one Earth day (in seconds)
                          fps=60,
                          n_samples=365,
                          )
        _tex_path = "../resources/textures/"  # directory of texture image files for windows
        _def_tex_fname = "2k_ymakemake_fictional.png"
        _tex_fnames = []  # list of texture filenames (will be sorted)
        _tex_dat_set = {}  # dist of body name and the texture data associated with it
        _body_params = {}  # dict of body name and the static parameters of each
        _vizz_params = {}  # dict of body name and the semi-static visual parameters
        _type_count = {}  # dict of body types and the count of each typE
        _viz_assign = {}  # dict of visual names to use for each body
        _body_count = 0  # number of available bodies

        # all built-ins from poliastro
        _body_set: list[Body] = [Sun,
                                 Mercury,
                                 Venus,
                                 Earth,
                                 Moon,
                                 Mars,
                                 Jupiter,
                                 Saturn,
                                 Uranus,
                                 Neptune,
                                 Pluto,
                                 # TODO: Find textures and rotational elements for the outer system moons,
                                 #       otherwise apply a default condition
                                 # Phobos,
                                 # Deimos,
                                 # Europa,
                                 # Ganymede,
                                 # Enceladus,
                                 # Titan,
                                 # Titania,
                                 # Triton,
                                 # Charon,
                                 ]
        self._body_names = tuple([bod.name for bod in _body_set])

        # orbital periods of bodies
        _o_per_set = [11.86 * u.year,
                      87.97 * u.d,
                      224.70 * u.d,
                      365.26 * u.d,
                      27.3 * u.d,
                      686.98 * u.d,
                      11.86 * u.year,
                      29.46 * u.year,
                      84.01 * u.year,
                      164.79 * u.year,
                      248 * u.year,
                      ]

        # reference frame fixed to planet surfaces
        _frame_set = [SunFixed,
                      MercuryFixed,
                      VenusFixed,
                      ITRS,
                      LunaFixed,
                      MarsFixed,
                      JupiterFixed,
                      SaturnFixed,
                      UranusFixed,
                      NeptuneFixed,
                      None,
                      ]

        # rotational elements as function of time
        _rot_set = [sun_rot_elements_at_epoch,
                    mercury_rot_elements_at_epoch,
                    venus_rot_elements_at_epoch,
                    earth_rot_elements_at_epoch,
                    moon_rot_elements_at_epoch,
                    mars_rot_elements_at_epoch,
                    jupiter_rot_elements_at_epoch,
                    saturn_rot_elements_at_epoch,
                    uranus_rot_elements_at_epoch,
                    neptune_rot_elements_at_epoch,
                    moon_rot_elements_at_epoch,
                    ]

        # body color values in RGBA (0...255)
        _color_RGB = [[253, 184, 19],  # base color for each body
                      [26, 26, 26],
                      [230, 230, 230],
                      [47, 106, 105],
                      [50, 50, 50],
                      [153, 61, 0],
                      [176, 127, 53],
                      [176, 143, 54],
                      [95, 128, 170],
                      [54, 104, 150],
                      [255, 255, 255],
                      ]
        _colorset_rgb = np.array(_color_RGB) / 256

        # indices of body type for each body
        # TODO: Discover primary body and hierarchy tree instead of this

        _type_set = (0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1,)

        #   default visual elements to use on which bodies (not used)
        _viz_keys = ("reticle", "nametag", "refframe", "ruler",
                     "surface", "oscorbit", "radvec", "velvec",)
        _com_viz = [_viz_keys[1], _viz_keys[2], _viz_keys[4]]
        _xtr_viz = [_viz_keys[5], _viz_keys[6], _viz_keys[7]]
        _xtr_viz.extend(_com_viz)
        [_viz_assign.update({name: _xtr_viz}) for name in self._body_names]
        _viz_assign['Sun'] = _com_viz

        # get listing of texture filenames
        _tex_dirlist = os.listdir(_tex_path)
        for i in _tex_dirlist:
            if "png" in i:
                _tex_fnames.append(i)  # add PNG type files to list
        # _tex_fnames = _tex_fnames.sort()  # it doesn't like this sort()
        _tex_fnames = tuple(_tex_fnames)  # the tuple locks in the order of sorted elements

        # indices of texture filenames for each body
        _tex_idx = (0, 1, 3, 10, 17, 11, 12, 13, 15, 16, 17,
                    # 21, 21, 21, 21, 21, 21, 21, 21, 21,
                    )

        # types of bodies in simulation
        _body_types = ("star",
                       "planet",
                       "moon",
                       "ship",
                       )

        # Markers symbol to be used for each body type
        _body_mark = ('star',
                      'o',
                      'diamond',
                      'triangle',
                      )

        for idx in range(len(self._body_names)):  # idx = [0..,len(_body_names)-1]
            _bod_name = self._body_names[idx]
            _body = _body_set[idx]
            _bod_prnt = _body.parent

            logging.debug(f">LOADING STATIC DATA for {str(_bod_name)}")

            # configure texture data
            try:
                _tex_fname = _tex_path + _tex_fnames[_tex_idx[idx]]  # get path of indexed filename
            except IndexError:
                _tex_fname = _tex_path + _def_tex_fname

            # the textures should be loaded later on
            _tex_dat_set.update({_bod_name: get_texture_data(fname=_tex_fname)})
            logging.debug(f"_tex_dat_set[{str(idx)}] = {str(_tex_fname)}")

            # configure radius data
            if _body.parent is None:
                R  = _body.R
                Rm = Rp = R
            else:
                R  = _body.R
                Rm = _body.R_mean
                Rp = _body.R_polar

            # define parent of body
            if _body.parent is None:
                _parent_name = None
            else:
                _parent_name = _body.parent.name

            # a dict of ALL body data EXCEPT the viz_dict{}
            _body_data = dict(body_name=_bod_name,  # build the _body_params dict
                              body_obj=_body,
                              parent_name=_parent_name,
                              r_set=(R, Rm, Rp),
                              fixed_frame=_frame_set[idx],
                              rot_func=_rot_set[idx],
                              o_period=_o_per_set[idx].to(u.s),
                              body_type=_body_types[_type_set[idx]]
                              )

            # a dict of the initial visual parameters
            _vizz_data = dict(body_color=_colorset_rgb[idx],
                              body_alpha=1.0,
                              track_alpha=0.6,
                              body_mark=_body_mark[_type_set[idx]],
                              fname_idx=_tex_idx[idx],
                              tex_fname=_tex_fnames[_tex_idx[idx]],
                              tex_data=_tex_dat_set[_bod_name],  # _tex_dat_set[idx],
                              viz_names=_viz_assign[_bod_name],
                              )
            _vizz_params.update({_bod_name: _vizz_data})

            # try this one? (All paramters for a body under its name key)
            _body_params.update({_bod_name: [_body_data, _vizz_params]})

            # configure the body type
            if _body_data['body_type'] not in _type_count.keys():  # identify types of bodies
                _type_count[_body_data['body_type']] = 0
            _type_count[_body_types[_type_set[idx]]] += 1  # count members of each type
            idx += 1
            _body_count += 1

        # This makes sure that all sets are of the same length so each body is completely defined.
        _check_sets = [
            len(_body_set),
            len(_colorset_rgb),
            len(_frame_set),
            len(_rot_set),
            len(_tex_idx),
            len(_type_set),
            len(self._body_names),
            len(_tex_dat_set.keys()),
            len(_tex_fnames),
        ]
        print("Check sets = ", _check_sets)
        assert _check_sets == ([_body_count, ] * (len(_check_sets) - 1) + [100, ])
        print("\t>>>check sets check out!")
        logging.debug("STATIC DATA has been loaded and verified...")
        logging.debug("ALL data for the system have been collected...!")
        # compile all the data into a master dict structure
        return dict(DFLT_EPOCH=DEF_EPOCH,
                    SYS_PARAMS=SYS_PARAMS,
                    TEX_FNAMES=_tex_fnames,
                    TEXTR_PATH=_tex_path,
                    TEXTR_DATA=_tex_dat_set,
                    BODY_COUNT=_body_count,
                    BODY_NAMES=self._body_names,
                    COLOR_DATA=_colorset_rgb,
                    TYPE_COUNT=_type_count,
                    BODY_PARAM=_body_params,
                    # VIZZ_PARAM=_vizz_params,
                    )

    """ ---------------------  PROPERTIES  ---------------------------------------- """

    @property
    def dist_unit(self):
        return self._dist_unit

    @property
    def vec_type(self):
        return type(np.zeros((3,), dtype=np.float64))

    @property
    def default_epoch(self):
        return self._datastore['DFLT_EPOCH']

    @property
    def system_params(self):
        return self._datastore['SYS_PARAMS']

    @property
    def body_count(self):
        return len(self.body_names)

    @property
    def body_names(self):
        # list of body names available in sim, cast to a tuple to preserve order
        return tuple([name for name in self._body_names])

    @property
    def body_data(self, name=None):
        res = None
        if not name:
            res = self._datastore['BODY_PARAM']
        elif name in self.body_names:
            res = self._datastore['BODY_PARAM'][name]

        return res

    def vizz_data(self, name=None):
        res = None
        if not name:
            res = self._datastore['VIZZ_PARAM']
        elif name in self.body_names:
            res = self._datastore['VIZZ_PARAM'][name]

        return res

    @property
    def texture_path(self):
        return self._datastore['TEXTR_PATH']

    @property
    def texture_fname(self, name=None):
        res = None
        if name is None:
            res = self._datastore['TEX_FNAMES']
        elif name in self.body_names:
            res = self._datastore['BODY_PARAM'][name]['tex_fname']

        return res

    @property
    def texture_data(self, name=None):
        res = None
        if name is None:
            res = self._datastore['TEXTR_DATA']
        elif name in self.body_names:
            res = self._datastore['BODY_PARAM'][name]['tex_data']

        return res

    @property
    def data_store(self):
        return self._datastore

    @property
    def model_data_group_keys(self):
        return tuple(['attr_', 'elem_coe', 'elem_pqw', 'elem_rv', 'syst_', 'vizz_'])

