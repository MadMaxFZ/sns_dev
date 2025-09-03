"""	sim_objects.py:
        This module defines a simulated Newtonian particle class (SimParticle)
        and derived class that simulates celestial bodies (SimPlanet), and
        a derived class that simulates maneuverable spacecraft (SimShip).
"""
from abc import ABC, abstractmethod

from astropy import units as u
from poliastro.bodies import *
from poliastro.constants import J2000_TDB as T0
from poliastro.core.propagation.base import func_twobody
from poliastro.ephem import Ephem
from poliastro.twobody import Orbit
from poliastro.twobody.propagation import CowellPropagator
from poliastro.util import time_range

from util import *

FPS = 60


@abstractmethod
class SimParticle(ABC):
    """ Defines the SimParticle class
        model a particle with a radius, mass, and a state of linear motion
    """
    # keep a dictionary of all SimParticle instances
    # ?? How does this affect the subclasses ??
    _count =0

    def __init__(self,
                 position=base_vec3.copy(),
                 velocity=base_vec3.copy(),
                 radius=1,
                 mass=1,
                 epoch=T0,
                 *args,
                 **kwargs,
                 ):
        """
            Initialize a SimParticle instance.
        Args:
            position:
            velocity:
            radius:
            mass:
            epoch:
        """
        # unique instance label
        super(SimParticle, self).__init__()
        SimParticle._count += 1
        self._id = "obj" + "{:05d}".format(SimParticle._count)
        self._sts = "not configured"    # status (e.g., "at rest", "moving", "flying") use ENUM here
        self._epo = epoch               # timestamp of observation
        self._pos = position            # position
        self._vel = velocity            # velocity
        self._rad = radius              # radius
        self._mss = mass                # mass
        self._acc = base_vec3.copy()    # acceleration
        self._att = base_quat
        self._rot = base_quat
        self._attractor = None
        self._body = None
        self._epochs = None
        self._ephem = None
        self._orbit = None

        # SimParticle._system.update({self._id: self})  # add new instance into system dict

    def f(self, t0, u_, k):
        du_kep = func_twobody(t0, u_, k)

        return du_kep

    def get_new_orbit(self, dt):
        if dt.ndim == 0:                        # needs to be a Quantity to work with ndim
            new_orb = self._orbit.propagate(dt, method=CowellPropagator(f=self.f))

            return new_orb

        # TODO:: figure out if this is necessary or even makes sense...
        #        this will only produce a set of orbits that will exist at that later time
        elif dt.ndim == 1:
            new_orbs = [self._orbit.propagate(t, method=CowellPropagator(f=self.f)) for t in dt]

            return new_orbs

        else:
            raise TypeError("'dt' argument must be scalar or 1-D vector")

    @property
    def pos(self):
        return self._pos

    @property
    def vel(self):
        return self._vel

    @property
    def mass(self):
        return self._mss

    @property
    def orbit(self):
        return self._orbit

    @property
    def ephem(self):
        return self._ephem

    @property
    def attractor(self):
        return self._attractor


# ---------------------------------------------------------------------------------------
class SimPlanet(SimParticle):
    """ Defines the SimPlanet subclass of SimParticle,
        a celestial body with state derived from JPL ephemeris,
        generally exhibiting Keplerian motion only.
    """

    # not sure if another class variable is needed

    def __init__(self,
                 body_data,                       # This must be data for ONE Body
                 # attitude=quat_type(1, 0, 0, 0),
                 # rotation=quat_type(1, 0, 0, 0),
                 *args,
                 **kwargs):
        """
            Initialize a SimPlanet instance.
        Args:
            body:
            *args:
            **kwargs:
        """

        super(SimPlanet, self).__init__(*args, **kwargs)
        self._data = body_data
        body = self._data['body_obj']
        if body:    # and issubclass(type(body), Body):
            self._body = body
            self._o_per = self._data['o_period']
            self._id = self._id + self._body.name
            if self._body.parent:
                self._attractor = self._body.parent

            self._epochs = time_range(start=T0,
                                      periods=int(self._o_per / (60 * 60 * 24 * u.s)),
                                      end=T0 + self._o_per
                                      )
            self._epo = self._epochs[0]
            self._full_ephem = Ephem.from_body(body=self._body,
                                               epochs=self._epochs,
                                               # *,  # not sure what this should be
                                               attractor=self._attractor,
                                               plane=Planes.EARTH_ECLIPTIC
                                               )
            self._orbit = Orbit.from_ephem(attractor=self._attractor,
                                           ephem=self._full_ephem,
                                           epoch=self._epochs[0]
                                           )
            # self._full_ephem = self.get_new_ephem(epochs=self._epochs)

        else:
            raise TypeError("'body' argument must be of type Body")

    def f(self, t0, u_, k):
        du_kep = func_twobody(t0, u_, k)

        return du_kep

    def get_new_ephem(self, epochs=None):
        if self._body.parent:
            _plane = Planes.EARTH_ECLIPTIC
            if self._attractor == Earth:
                _plane = Planes.EARTH_EQUATOR

            if epochs is None:
                epochs = self._epochs

            new_ephem = Ephem.from_orbit(self._orbit,
                                         epochs,
                                         plane=_plane,
                                         )

            return new_ephem

        else:
            return None

    def get_state_set(self, ephem=None, epochs=None, **kwargs):
        if not epochs:
            epochs = time_range(start=self._epochs[0],
                                periods=FPS,
                                spacing=u.s / FPS,
                                format='jd',
                                scale='tdb'
                                )

        if not ephem:
            ephem = self.get_new_ephem(epochs=epochs)

        new_states = [eph.rv(epochs, **kwargs) for eph in ephem if self._body.parent]

        return new_states

    @property
    def body(self):
        return self._body


# ---------------------------------------------------------------------------------------
class SimShip(SimParticle):
    """ Defines the SimShip subclass of SimParticle
        a spacecraft body orbiting one of the SimPlanet objects,
        has capability to perform Maneuvers to modify its orbit,
        and thus change its parent body.
    """

    def __init__(self, parent=Earth, *args, **kwargs):
        super(SimShip, self).__init__(*args, **kwargs)

    def f(self, t0, u_, k):
        du_kep = func_twobody(t0, u_, k)

        return du_kep

    def perturb(self, t0, state, k):
        # compute perturbation based upon current state

        return [0., 0., 0.]

    def f(self, t0, u_, k):
        du_kep = func_twobody(t0, u_, k)
        ax, ay, az = self.perturb(t0, u_, k)
        du_ad = np.array([0., 0., 0., ax, ay, az])

        return du_kep + du_ad

    def get_new_orbit(self, dt):
        if dt.ndim == 0:                        # needs to be a Quantity to work with ndim
            return self._orbit.propagate(dt, method=CowellPropagator(f=self.f))

        elif dt.ndim == 1:
            return [self._orbit.propagate(t, method=CowellPropagator(f=self.f)) for t in dt]

        else:
            raise TypeError("'dt' argument must be scalar or 1-D vector")


# ---------------------------------------------------------------------------------------
if __name__ == "__main__":
    from cfg_data import SystemDataStore as ref_data
    print("Hello World!")
    r_dat = ref_data()
    sb = SimPlanet(body_data=r_dat.body_data('Earth'))
    print(sb.__dir__())
