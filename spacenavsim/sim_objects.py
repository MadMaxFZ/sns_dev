"""	sim_objects.py:
        This module defines a simulated Newtonian particle class (SimParticle)
        and derived class that simulates celestial bodies (SimPlanet), and
        a derived class that simulates maneuverable spacecraft (SimShip).
"""
from abc import ABC, abstractmethod

from astropy import units
from astropy.time import TimeDelta
from poliastro.bodies import *
from poliastro.constants import J2000_TDB as T0
from poliastro.ephem import Ephem
from poliastro.twobody import Orbit
from poliastro.util import time_range

from cfg_data import SystemDataStore as ref_data
from util import *


class SimParticle(ABC):
    """ Defines the SimParticle class
        model a particle with a radius, mass, and a state of linear motion
    """
    # keep a dictionary of all SimParticle instances
    # ?? How does this affect the subclasses ??
    _system = {}

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
        self._id = "obj" + "{:05d}".format(len(SimParticle._system))
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
        self._bod = None
        self._epochs = None
        self._ephem = None
        self._orbit = None

        super(SimParticle, self).__init__(*args, **kwargs)
        SimParticle._system.update({self._id: self})  # add new instance into system dict

    @abstractmethod
    def init_ephem(self):
        return None

    @abstractmethod
    def init_orbit(self):
        return None

    @abstractmethod
    def get_upstate(self, dt):
        """
            Returns a state based upon the current state and accelerations over time dt.
            Subclasses will most likely need to override this method.

            Args:
                dt: dt is TimeDelta, increment from current epoch
        """
        # apply acceleration
        # TODO:: model accel with a function over a time segment?

        if type(dt) == TimeDelta:
            _vel = self._vel + self._acc * dt
            _pos = self._pos + _vel * dt
            _epo = self._epo + dt

            # apply torque
            # TODO:: model torque with a function over a time segment?
            # self._rot += self._trq * dt
            # self._att += self._rot * dt 	# double check quat math here

            return _pos, _vel, _epo

        else:
            raise TypeError("Argument MUST be a TimeDelta...")


# ---------------------------------------------------------------------------------------
class SimBody(SimParticle):
    """ Defines the SimPlanet subclass of SimParticle,
        a celestial body with state derived from JPL ephemeris,
        generally exhibiting Keplerian motion only.
    """

    # not sure if another class variable is needed

    def __init__(self,
                 body_data,
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
        super(SimBody, self).__init__(*args, **kwargs)
        self._data = body_data
        body = self._data['body_obj']
        if body and issubclass(type(body), Body):
            self._bod = body
            self._id = self._id + self._bod.name
            # the following two 2/8are computed using rot_func()

            if self._bod.parent:
                self._attractor = self._bod.parent

        else:
            raise TypeError("'body' argument must be of type Body")

        # TODO:: set linear range of time coordinates over orbital period
        self._o_per = self._data['o_period']
        self._epochs = self.init_epochs()
        self._ephem = self.init_ephem()
        self._orbit = self.init_orbit()
        print("initiated")

    def init_epochs(self):
        return time_range(start=T0, periods=int((self._o_per / (units.s * 60 * 60 * 24)).value), end=T0 + self._o_per)

    def init_ephem(self):
        return Ephem.from_body(body=self._bod,
                               epochs=self._epochs,  # must define these
                               # *,  # not sure what this should be
                               attractor=self._attractor,
                               plane=Planes.EARTH_ECLIPTIC
                               )

    def init_orbit(self):
        return Orbit.from_ephem(attractor=self._attractor,
                                ephem=self._ephem,
                                epoch=self._epochs[0]
                                )

    def get_upstate(self, dt):
        """
            Return
        """
        pass

    @property
    def body(self):
        return self._bod


# update poliastro orbit here


# ---------------------------------------------------------------------------------------
class SimShip(SimParticle):
    """ Defines the SimShip subclass of SimParticle
        a spacecraft body orbiting one of the SimPlanet objects,
        has capability to perform Maneuvers to modify its orbit,
        and thus change its parent body.
    """

    def __init__(self, parent=Earth, *args, **kwargs):
        super(SimShip, self).__init__(*args, **kwargs)

    # add ship attributes here

    def get_upstate(self, dt):
        # update from poliastro and user inputs
        pass


# ---------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("Hello World!")
    r_dat = ref_data()
    sb = SimBody(r_dat.body_data['Earth'])
    print(sb.__dir__())
