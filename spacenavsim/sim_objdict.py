# sim_objdict.py
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from astropy.constants.codata2018 import G
from astropy.coordinates import solar_system_ephemeris
from astropy.time import Time
from cfg_data import data_store as ref_data
from sim_objects import SimParticle, SimPlanet
from util import measure_execution_time


class SimObjectDict(dict):

    def __init__(self,
                 epoch=None,
                 cfg_dat=None,
                 use_multi=False,
                 auto_up=False
                 ):
        """

        :param epoch:
        :param cfg_dat:
        :param use_multi:
        :param auto_up:
        """
        if not cfg_dat:
            cfg_dat = ref_data

        super(SimObjectDict, self).__init__()
        solar_system_ephemeris.set("jpl")
        self.T0 = cfg_dat.DEF_EPOCH0
        self._sys_primary = None
        # self._dist_unit = cfg_dat.dist_unit
        self._vec_type = cfg_dat.vec_type
        self._valid_body_names = cfg_dat.body_names
        self._body_count = 0
        self._sys_rel_pos = None
        self._sys_rel_vel = None
        self._bod_tot_acc = None
        self._USE_MULTIPROC = cfg_dat._USE_MULTIPROC
        self._base_t = 0
        self._t1 = 0
        self.executor = ThreadPoolExecutor(max_workers=6)
        if epoch:
            self._sys_epoch = epoch
        else:
            self._sys_epoch = Time(cfg_dat.DEF_EPOCH0, format='jd', scale='tdb')

    # -------------------------------------------------------------------------------------------------------
    def _renew_rel_arrays(self):
        """

        :return:
        """
        self._body_count = len(self)
        self._sys_rel_pos = np.zeros((self._body_count, self._body_count), dtype=self._vec_type)
        self._sys_rel_vel = np.zeros((self._body_count, self._body_count), dtype=self._vec_type)
        self._bod_tot_acc = np.zeros((self._body_count,), dtype=self._vec_type)

    # -------------------------------------------------------------------------------------------------------
    def _set_rel_arrays(self):
        """

        :return:
        """
        # iterate over body_count X body_count to get rel pos and vel between bodies
        # also compute total acceleration on each body due to all other bodies
        for i, k1 in enumerate(self.items()):
            self._bod_tot_acc[i] = 0
            for j, k2 in enumerate(self.items()):
                if i < j:       # relative position
                    self._sys_rel_pos[i][j] = k1.pos - k2.pos
                elif j > i:     # relative velocity
                    self._sys_rel_vel[i][j] = k1.vel - k2.vel
                else:
                    self._bod_tot_acc[i] += G * k2.mass / pow(self._sys_rel_pos[i][j], 2)

    # -------------------------------------------------------------------------------------------------------
    def _get_rel_arrays(self):
        """

        :return:
        """
        return (self._sys_rel_pos,
                self._sys_rel_vel,
                self._bod_tot_acc)

    # -------------------------------------------------------------------------------------------------------
    @staticmethod
    def _validate_sim_obj(sim_obj):
        """

        :param sim_obj:
        :return:
        """
        if not issubclass(type(sim_obj), SimParticle):
            raise TypeError("SimPlanet expected")

        return sim_obj

    # -------------------------------------------------------------------------------------------------------
    @measure_execution_time
    def update_orbits(self, epoch):
        """

        :param epoch:
        :return:
        """
        new_orbits = None
        if self._USE_MULTIPROC:
            futures = [self.executor.submit(sb.get_new_orbit, epoch)
                       for sb in self.values() if sb.attractor]
            for future in futures:
                future.result()
        else:
            new_orbits = [sb.get_new_orbit(epoch) for sb in self.values() if sb._attractor]

        return new_orbits

    # -------------------------------------------------------------------------------------------------------
    def get_new_ephems(self, epochs=None):
        """

        :param epochs:
        :return:
        """
        new_ephems = [sb.get_new_ephem(epochs) for sb in self.values() if sb.attractor]
        # [print(f"{len(eph.rv()[0])}\n") for eph in new_ephems]

        return new_ephems

    # -------------------------------------------------------------------------------------------------------
    @measure_execution_time
    def get_state_sets(self, T0=None, epochs=None, FPS=60, span=1):
        """

        :param T0:
        :param epochs:
        :param FPS:
        :param span:
        :return:
        """
        if epochs:
            _ephems = self.get_new_ephems(epochs)

        else:
            if T0 is None:
                T0 = self.T0

            _ephems = self.get_new_ephems(time_range(start=T0,
                                                     periods=FPS,
                                                     end=T0 + span * u.hr))

        state_sets = [sb.get_state_set(ephem=_ephems) for sb in self.values() if sb.body[00]]

        return state_sets

    # -------------------------------------------------------------------------------------------------------
    def set_parentage(self):
        """

        :return:
        """
        self._sys_primary = None
        for sb in self.values():
            print(type(sb))
            if sb.body.parent:
                sb.parent = sb.body.parent.name
            else:
                self._sys_primary = sb

    # -------------------------------------------------------------------------------------------------------
    def get_attribute_list(self, attribute_name):
        """

        :param attribute_name:
        :return:
        """
        """Return a list of the specified attribute from each SimObject in the dictionary."""
        return [getattr(sb, attribute_name, None) for sb in self.values()]

    # -------------------------------------------------------------------------------------------------------
    def perform_batch_operation(self, operation, *args, **kwargs):
        """

        :param operation:
        :param args:
        :param kwargs:
        :return:
        """
        """Perform a batch operation on all SimObject instances."""
        for sb in self.values():
            operation(sb, *args, **kwargs)

    # -------------------------------------------------------------------------------------------------------
    @property
    def num_bodies(self):
        return len(self.keys())

    @property
    def primary(self):
        return self._sys_primary

    def __setitem__(self, obj_name: str, sim_obj):
        self.update({obj_name: self._validate_sim_obj(sim_obj)})
        # super().__setitem__(obj_name, sim_obj)
        self._renew_rel_arrays()

    def __delitem__(self, obj_name):
        # super().__delitem__(obj_name)
        self._renew_rel_arrays()

    def __getitem__(self, obj_name):
        return super().__getitem__(obj_name)

    # Dynamic attribute access for properties
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in self.keys():
            return self[name]
        else:
            raise AttributeError(f"'SimObjectDict' object has no attribute '{name}'")


# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    from poliastro.util import time_range
    from astropy import units as u

    bod_names = ref_data.body_names
    sod = SimObjectDict(cfg_dat=ref_data)
    for name in bod_names:
        sb = SimPlanet(body_data=ref_data.body_data(name))
        sod[name] = sb

    third_rock = sod['Earth']
    print(third_rock)
    # sod.set_parentage()
    kick = sod.update_orbits(1 * u.s)
    time_span = time_range(1 * u.s, periods=10, spacing=1 * u.s , format='jd', scale='tdb')
    print(time_span)
    projections = [sod.update_orbits(t * u.s) for t in range(10)]
    # [[print(o) for o in p] for p in projections]
    for _ in range(100):
        setz = sod.get_state_sets()

    # Tests for SimObjectDict class
    def test_sim_object_dict_initialization():
        # Test initialization with default parameters
        sod = SimObjectDict()
        assert sod.T0 == ref_data.DEF_EPOCH0
        assert sod._sys_primary is None
        assert sod._body_count == 0
        assert sod._sys_rel_pos is None
        assert sod._sys_rel_vel is None
        assert sod._bod_tot_acc is None

        # Test initialization with custom parameters
        epoch = Time('2025-01-01', format='iso', scale='tdb')
        sod = SimObjectDict(epoch=epoch, cfg_dat=ref_data)
        assert sod._sys_epoch == epoch
        assert sod.T0 == ref_data.DEF_EPOCH0

    def test_sim_object_dict_set_item():
        # Test adding a SimPlanet object to the dictionary
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Earth'] = earth
        assert 'Earth' in sod
        assert sod['Earth'] == earth

        # Test adding an invalid object
        try:
            sod['Invalid'] = 'not a SimParticle'
        except TypeError as e:
            assert str(e) == "SimPlanet expected"

    def test_sim_object_dict_del_item():
        # Test removing an item from the dictionary
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Earth'] = earth
        del sod['Earth']
        assert earth not in sod

    def test_sim_object_dict_get_item():
        # Test getting an item from the dictionary
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Earth'] = earth
        assert sod['Earth'] == earth

    def test_sim_object_dict_get_attribute_list():
        # Test getting a list of attributes from all objects in the dictionary
        sun = SimPlanet(body_data=ref_data.body_data('Sun'))
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        mars = SimPlanet(body_data=ref_data.body_data('Mars'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Sun'] = sun
        sod['Earth'] = earth
        sod['Mars'] = mars
        positions = sod.get_attribute_list('pos')
        assert len(positions) == 3
        assert positions[0].all == sun.pos.all
        assert positions[0].all == earth.pos.all
        assert positions[1].all == mars.pos.all

    def test_sim_object_dict_perform_batch_operation():
        # Test performing a batch operation on all objects in the dictionary
        sun = SimPlanet(body_data=ref_data.body_data('Sun'))
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        mars = SimPlanet(body_data=ref_data.body_data('Mars'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Sun'] = sun
        sod['Earth'] = earth
        sod['Mars'] = mars

        def example_operation(obj, factor):
            obj._vel *= factor

        sod.perform_batch_operation(example_operation, 2)
        assert np.allclose(sun._vel, sun._vel * 2)
        assert np.allclose(earth._vel, earth._vel * 2)
        assert np.allclose(mars._vel, mars._vel * 2)

    def test_sim_object_dict_update_orbits():
        # Test updating the orbits of all objects in the dictionary
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Earth'] = earth
        new_orbits = sod.update_orbits(1 * u.s)
        assert len(new_orbits) == 1
        assert new_orbits[0] is not None

    def test_sim_object_dict_get_new_ephems():
        # Test getting new ephemerides for all objects in the dictionary
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Earth'] = earth
        new_ephems = sod.get_new_ephems()
        assert len(new_ephems) == 1
        assert new_ephems[0] is not None

    def test_sim_object_dict_get_state_sets():
        # Test getting state sets for all objects in the dictionary
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Earth'] = earth
        state_sets = sod.get_state_sets()
        assert len(state_sets) == 1
        assert state_sets[0] is not None

    def test_sim_object_dict_set_parentage():
        # Test setting parentage for all objects in the dictionary
        sun = SimPlanet(body_data=ref_data.body_data('Sun'))
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        mars = SimPlanet(body_data=ref_data.body_data('Mars'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Sun'] = sun
        sod['Earth'] = earth
        sod['Mars'] = mars
        sod.set_parentage()
        assert sod._sys_primary == sun

    def test_sim_object_dict_dynamic_attribute_access():
        # Test dynamic attribute access
        earth = SimPlanet(body_data=ref_data.body_data('Earth'))
        sod = SimObjectDict(cfg_dat=ref_data)
        sod['Earth'] = earth
        assert sod.Earth == earth
        try:
            _ = sod.Invalid
        except AttributeError as e:
            assert str(e) == "'SimObjectDict' object has no attribute 'Invalid'"

    # Run all tests
    test_sim_object_dict_initialization()
    test_sim_object_dict_set_item()
    test_sim_object_dict_del_item()
    test_sim_object_dict_get_item()
    test_sim_object_dict_get_attribute_list()
    test_sim_object_dict_perform_batch_operation()
    test_sim_object_dict_update_orbits()
    test_sim_object_dict_get_new_ephems()
    test_sim_object_dict_get_state_sets()
    test_sim_object_dict_set_parentage()
    test_sim_object_dict_dynamic_attribute_access()

    print("All tests passed! SWEEET!!")
