#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#
import logging

logging.basicConfig(filename="../logs/sns_simobj.log",
                    level=logging.ERROR,
                    format="%(funcName)s:\t\t%(levelname)s:%(asctime)s:\t%(message)s",
                    )

import numpy as np
from poliastro.constants import J2000_TDB
from astropy import units as u
from astropy.time import Time
from abc import ABC

VEC_TYPE = type(np.zeros((3,), dtype=np.float64))
MIN_SIZE = 0.001  # * u.km
BASE_DIMS = np.ndarray((3,), dtype=np.float64)


class SimObject(ABC):
    """
        This is a base class for SimBody, SimShip and any
        other gravitationally affected objects in the sim.
        This base class exists to contain the necessary data to
        define an object's orbital state about a parent attractor object.
        This will allow for celestial bodies and maneuverable spacecraft to
        operate within a common model while allowing for subclasses that can
        have differing behaviors and specific attributes.

    """
    epoch0 = J2000_TDB.jd
    system = {}
    base_dist_unit = u.km
    # created = pyqtSignal(str)
    _fields = ('attr',
               'pos',
               'rot',
               'elem',
               )

    def __init__(self, *args, **kwargs):
        self._name       = ""
        self._dist_unit  = self.base_dist_unit
        super(SimObject, self).__init__(*args, **kwargs)
        self._epoch      = Time(SimObject.epoch0,
                                format='jd',
                                scale='tdb')
        self._state      = np.zeros((3,), dtype=VEC_TYPE)

    @property
    def name(self):
        return self._name

    @property
    def r(self):
        return self._state[0] * self._dist_unit

    @property
    def v(self):
        return self._state[1] * self._dist_unit / u.s

    @property
    def pos(self):
        return self._state[0] * self._dist_unit

    @property
    def rot(self):
        return self._state[2]

    @property
    def state(self):
        return self._state

    @property
    def dist2parent(self):
        return np.linalg.norm(self.pos) # * self._dist_unit

    @property
    def vel(self):
        """
        TODO:  make this a property that returns the velocity of the body relative to system primary
        Returns
        -------
        velocity of body relative to its parent body
        """
        return self._state[1] * self._dist_unit / u.s


if __name__ == "__main__":
    def main():
        pass
        #     sb = SimBody(body_data=sys_data.body_data(bod_name))
        #     sb.update_state(sb)
        # print(sb.orbit)


    main()
    print("SimObject doesn't really do much as an abstract base class...")
