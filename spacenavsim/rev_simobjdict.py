#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from concurrent.futures import ThreadPoolExecutor

import numpy as np
from astropy.coordinates import solar_system_ephemeris
from astropy.time import Time

from sim_objects import SimParticle, SimPlanet
from sns_config import SystemDataStore


class SimObjectDict(dict):

    def __init__(self, epoch=None, data=None, ref_data=None, body_names=None, use_multi=False, auto_up=False):
        super().__init__()
        solar_system_ephemeris.set("jpl")
        if data:
            self.data = {name: self._validate_sim_obj(simbody) for name, simbody in data.items()}
        else:
            self.data = {}

        if ref_data:
            if isinstance(ref_data, SystemDataStore):
                print('<sys_data> input is valid...')
            else:
                print('Bad <sys_data> input... Reverting to defaults...')
                ref_data = SystemDataStore()
        else:
            ref_data = SystemDataStore()

        self.ref_data = ref_data
        self._sys_primary = None
        self._dist_unit = self.ref_data.dist_unit
        self._vec_type = self.ref_data.vec_type
        self._valid_body_names = self.ref_data.body_names

        if body_names:
            self._current_body_names = tuple([n for n in body_names if n in self._valid_body_names])
        else:
            self._current_body_names = tuple(self._valid_body_names)

        self._body_count = len(self._current_body_names)
        self._sys_rel_pos = np.zeros((self._body_count, self._body_count), dtype=self._vec_type)
        self._sys_rel_vel = np.zeros((self._body_count, self._body_count), dtype=self._vec_type)
        self._bod_tot_acc = np.zeros((self._body_count,), dtype=self._vec_type)
        if epoch:
            self._sys_epoch = epoch
        else:
            self._sys_epoch = Time(self.ref_data.default_epoch, format='jd', scale='tdb')

        self._base_t = 0
        self._t1 = 0
        self.USE_AUTO_UPDATE_STATE = auto_up
        self._IS_POPULATED = False
        self._HAS_INIT = False
        self._IS_UPDATING = False
        self._USE_LOCAL_TIMER = False
        self._USE_MULTIPROC = False
        self.executor = ThreadPoolExecutor(max_workers=6)

    def __setitem__(self, name, sim_obj):
        self.data[name] = self._validate_sim_obj(sim_obj)

    def __getitem__(self, name):
        return self.data[name]

    @staticmethod
    def _validate_sim_obj(sim_obj):
        if not issubclass(sim_obj, SimParticle):
            raise TypeError("SimObject expected")
        return sim_obj

    def update_state(self, epoch):
        self._base_t = self._t1
        _tx = Time.perf_counter()

        if self._USE_MULTIPROC:
            futures = (self.executor.submit(sb.get_upstate, epoch=epoch) for sb in self.data.values())
            for future in futures:
                future.result()
        else:
            [sb.get_upstate(epoch) for sb in self.data.values()]

        self._t1 = Time.perf_counter()
        update_time = self._t1 - self._base_t
        print(f'\n\t\t> Frame Rate: {1 / update_time:.4f} FPS (1/{update_time:.4f})\n' f'  Model updated in {self._t1 - _tx:.4f} seconds...')
        self.has_updated.emit(update_time)

    def set_parentage(self):
        self._sys_primary = None
        for sb in self.data.values():
            if sb.body.parent:
                sb.parent = self.data[sb.body.parent.name]
            else:
                self._sys_primary = sb

    def get_attribute_list(self, attribute_name):
        """Return a list of the specified attribute from each SimObject in the dictionary."""
        return [getattr(sb, attribute_name, None) for sb in self.data.values()]

    def perform_batch_operation(self, operation, *args, **kwargs):
        """Perform a batch operation on all SimObject instances."""
        for sb in self.data.values():
            operation(sb, *args, **kwargs)

    @property
    def num_bodies(self):
        return len(self.data.keys())

    @property
    def primary(self):
        return self._sys_primary

    # Dynamic attribute access for properties
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in self.data:
            return self.data[name]
        else:
            raise AttributeError(f"'SimObjectDict' object has no attribute '{name}'")


if __name__ == "__main__":
    bodies = {"Earth": SimPlanet(), "Mars": SimPlanet()}
    simbody_dict = SimObjectDict(bodies)

    # Example usage
    positions = simbody_dict.get_attribute_list('pos')
    print(positions)

    # Dynamic attribute access
    earth_pos = simbody_dict.Earth.pos
    mars_pos = simbody_dict.Mars.pos
    print(f"Earth Position: {earth_pos}")
    print(f"Mars Position: {mars_pos}")