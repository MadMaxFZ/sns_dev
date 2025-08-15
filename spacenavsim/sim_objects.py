"""
MIT License

Copyright (c) 2025 Max Smith Whitten

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""	sim_objects.py:
        This module defines a simulated Newtonian particle class (SimParticle)
        and derived class that simulates celestial bodies (SimPlanet), and
        a derived class that simulates maneuverable spacecraft (SimShip).
"""
#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import numpy as np
from ABC import ABC
from poliastro.bodies import *
from poliastro.constants import J2000_TDB
from pyquaternion import Quaternion as quat

base_vec2 = np.zeros(2)
base_vec3 = np.zeros(3)
base_vec4 = np.zeros(4)
base_quat = quat(1.0, 0.0, 0.0, 0.0)
vec2_type = type(base_vec2)
vec3_type = type(base_vec3)
vec4_type = type(base_vec4)
quat_type = type(base_quat)


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
                 epoch=J2000_TDB,
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

        super(SimParticle, self).__init__(*args, **kwargs)
        SimParticle._system.update({self._id: self})  # add new instance into system dict


    def update_state(self, dt):
        """
            update the state either by a time interval 'dt'

        Args:
            dt: dt is TimeDelta, increment from current epoch
        """
        # apply acceleration
        # TODO:: model accel with a function over a time segment?

        if type(dt) == TimeDelta:
            self._vel += self._acc * dt
            self._pos += self._vel * dt

            # apply torque
            # TODO:: model torque with a function over a time segment?

            # self._rot += self._trq * dt
            # self._att += self._rot * dt 	# double check quat math here
            self._epo += dt

        else:
            raise TypeError("Argument must be a TimeDelta...")


    # ?? emit signal here to indicate update ??


# ---------------------------------------------------------------------------------------
class SimPlanet(SimParticle):
    """ Defines the SimPlanet subclass of SimParticle,
        a celestial body with state derived from JPL ephemeris,
        generally exhibiting Keplerian motion only.
    """

    # not sure if another class variable is needed

    def __init__(self,
                 body=None,
                 attitude=quat_type(1, 0, 0, 0),
                 rotation=quat_type(1, 0, 0, 0),
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

        if body and type(body) == Body:
            self._bod = body
            self._id = self._id + self._bod.name
        else:
            raise TypeError("body must be defined AND be of type Body")

        self._att = attitude  # attitude
        self._rot = rotation  # rotation rate
        self._trq = quat_type(1, 0, 0, 0)  # torque

    # construct poliastro orbit here

    def update_state(self, dt):
        pass


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

    def update_state(self, dt):
        # update from poliastro and user inputs
        pass


# ---------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("Hello World!")
    mammylist = [1, 2, 3]
    mammylist[0] = 4
    print(mammylist)
