
import time as systime
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from astropy.coordinates import solar_system_ephemeris
from astropy.time import Time

from cfg_data import data_store as ref_data
from sim_objects import SimParticle, SimPlanet


class SimObjectDict(dict):

    def __init__(self,
                 epoch=None,
                 cfg_dat=None,
                 use_multi=False,
                 auto_up=False
                 ):
        if not cfg_dat:
            cfg_dat = ref_data

        super(SimObjectDict, self).__init__()
        solar_system_ephemeris.set("jpl")
        self._sys_primary = None
        # self._dist_unit = cfg_dat.dist_unit
        # self._vec_type = cfg_dat.vec_type
        self._valid_body_names = cfg_dat.body_names
        self._body_count = 0
        self._sys_rel_pos = None
        self._sys_rel_vel = None
        self._bod_tot_acc = None
        self._USE_MULTIPROC = cfg_dat._USE_MULTIPROC

        if epoch:
            self._sys_epoch = epoch
        else:
            self._sys_epoch = Time(cfg_dat.DEF_EPOCH0, format='jd', scale='tdb')

        self._base_t = 0
        self._t1 = 0
        self.executor = ThreadPoolExecutor(max_workers=6)

    def __setitem__(self, obj_name: str, sim_obj):
        self.update({obj_name: self._validate_sim_obj(sim_obj)})
        super().__setitem__(obj_name, sim_obj)
        self._set_rel_arrays()

    def __delitem__(self, obj_name):
        super().__delitem__(obj_name)
        self._set_rel_arrays()

    def __getitem__(self, obj_name):
        return super().__getitem__(obj_name)

    def _set_rel_arrays(self):
        self._body_count = len(self)
        self._sys_rel_pos = np.zeros((self._body_count, self._body_count), dtype=self._vec_type)
        self._sys_rel_vel = np.zeros((self._body_count, self._body_count), dtype=self._vec_type)
        self._bod_tot_acc = np.zeros((self._body_count,), dtype=self._vec_type)

    @staticmethod
    def _validate_sim_obj(sim_obj):
        if not issubclass(type(sim_obj), SimParticle):
            raise TypeError("SimPlanet expected")

        return sim_obj

    # TODO:: rework the timing code here into a decorator!!
    def update_orbits(self, epoch):
        self._base_t = self._t1
        _tx = systime.perf_counter()

        new_orbits = None
        if self._USE_MULTIPROC:
            futures = [self.executor.submit(sb.get_new_orbit, epoch)
                       for sb in self.values() if sb.attractor]
            for future in futures:
                future.result()
        else:
            new_orbits = [sb.get_new_orbit(epoch) for sb in self.values() if sb._attractor]

        self._t1 = systime.perf_counter()
        update_time = self._t1 - self._base_t
        print(f'\n\t\t> Frame Rate: {1 / update_time:.6f} FPS (1/{update_time:.4f})\n'
              f'' f'  Orbits updated in {self._t1 - _tx:.6f} seconds...')

        return new_orbits

    def get_new_ephems(self, epochs=None):
        new_ephems = [sb.get_new_ephem(epochs) for sb in self.values()]
        return new_ephems

    def get_state_sets(self):
        state_sets = [sb.get_state_set(ephem=sb._ephem) for sb in self.values()]
        return state_sets

    def set_parentage(self):
        self._sys_primary = None
        for sb in self.values():
            print(type(sb))
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

    from poliastro.util import time_range
    from astropy import units as u

    ref_dat = ref_data()
    bod_names = ref_dat.body_names
    sod = SimObjectDict(cfg_dat=ref_dat)
    for name in bod_names:
        sb = SimPlanet(body_data=ref_dat._datastore['BODY_PARAM'][name])
        sod[name] = sb

    third_rock = sod['Earth']
    print(third_rock)
    # sod.set_parentage()
    kick = sod.update_orbits(1 * u.s)
    time_span = time_range(1 * u.s, periods=10, spacing=1 * u.s , format='jd', scale='tdb')
    print(time_span)
    projections = [sod.update_orbits(t * u.s) for t in range(10)]
    [[print(o) for o in p] for p in projections]
    print(sod.get_state_sets()[0:-1][0][0])