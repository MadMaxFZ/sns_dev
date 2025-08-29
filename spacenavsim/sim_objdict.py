
import time as systime
from concurrent.futures import ThreadPoolExecutor

import astropy.units as u
import numpy as np
from astropy.coordinates import solar_system_ephemeris
from astropy.time import Time

from cfg_data import SystemDataStore as ref_data
from sim_objects import SimBody, SimParticle


class SimObjectDict(dict):

    def __init__(self,
                 epoch=None,
                 ref_data=None,
                 use_multi=False,
                 auto_up=False
                 ):
        super(SimObjectDict, self).__init__()
        solar_system_ephemeris.set("jpl")
        # if data:
        #     self.data = {name: self._validate_sim_obj(simbody) for name, simbody in data.items()}
        # else:
        #     self.data = {}
        #
        # if ref_data:
        #     if isinstance(ref_data, SystemDataStore):
        #         print('<sys_data> input is valid...')
        #     else:
        #         print('Bad <sys_data> input... Reverting to defaults...')
        #         ref_data = SystemDataStore()
        # else:
        #     ref_data = SystemDataStore()
        #
        # self.ref_data = ref_data
        self._sys_primary = None
        self._dist_unit = ref_data.dist_unit
        self._vec_type = ref_data.vec_type
        self._valid_body_names = ref_data.body_names
        self._body_count = 0
        self._sys_rel_pos = None
        self._sys_rel_vel = None
        self._bod_tot_acc = None
        self._USE_MULTI = ref_data._USE_MULTIPROC

        # if body_names:
        #     self._current_body_names = tuple([n for n in body_names if n in self._valid_body_names])
        # else:
        #     self._current_body_names = tuple(self._valid_body_names)

        if epoch:
            self._sys_epoch = epoch
        else:
            self._sys_epoch = Time(ref_data.DEF_EPOCH0, format='jd', scale='tdb')

        self._base_t = 0
        self._t1 = 0
        self.executor = ThreadPoolExecutor(max_workers=6)

    def __setitem__(self, name, sim_obj):
        self.update({name: self._validate_sim_obj(sim_obj)})
        self._set_rel_arrays()

    def __delitem__(self, name):
        super(SimObjectDict, self).__delitem__(name)
        self._set_rel_arrays()

    def __getitem__(self, name):
        return self[name]

    def _set_rel_arrays(self):
        self._body_count = len(self)
        self._sys_rel_pos = np.zeros((self._body_count, self._body_count), dtype=self._vec_type)
        self._sys_rel_vel = np.zeros((self._body_count, self._body_count), dtype=self._vec_type)
        self._bod_tot_acc = np.zeros((self._body_count,), dtype=self._vec_type)

    @staticmethod
    def _validate_sim_obj(sim_obj):
        if not issubclass(type(sim_obj), SimParticle):
            raise TypeError("SimObject expected")

        return sim_obj

    def update_state(self, epoch):
        self._base_t = self._t1
        _tx = systime.perf_counter()

        if self._USE_MULTI:
            futures = (self.executor.submit(sb.get_upstate, epoch)
                       for sb in self.values())
            for future in futures:
                future.result()
        else:
            [sb.get_upstate(epoch) for sb in self.values()]

        self._t1 = systime.perf_counter()
        update_time = self._t1 - self._base_t
        print(f'\n\t\t> Frame Rate: {1 / update_time:.6f} FPS (1/{update_time:.4f})\n'
              f'' f'  Model updated in {self._t1 - _tx:.6f} seconds...')
        # self.has_updated.emit(update_time)

    def set_parentage(self):
        self._sys_primary = None
        for sb in self.values():
            if sb.body.parent:
                sb.parent = sb.body.parent.name
            else:
                self._sys_primary = sb

    def get_attribute_list(self, attribute_name):
        """Return a list of the specified attribute from each SimObject in the dictionary."""
        return [getattr(sb, attribute_name, None) for sb in self.values()]

    def perform_batch_operation(self, operation, *args, **kwargs):
        """Perform a batch operation on all SimObject instances."""
        for sb in self.values():
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
        elif name in self.keys():
            return self[name]
        else:
            raise AttributeError(f"'SimObjectDict' object has no attribute '{name}'")


if __name__ == "__main__":
   ref_dat = ref_data()
   bod_names = ref_dat.body_names
   sod = SimObjectDict(ref_data=ref_dat)
   for name in bod_names:
       sb = SimBody(body_data=ref_dat.body_data[name])
       sod[name] = sb

   sod.set_parentage()
   sod.update_state(10 * u.s)
   print(sod.get_attribute_list('_vel'))
