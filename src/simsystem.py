#!#  Copyright 2025 Max Smith Whitten

#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
#  associated documentation files (the “Software”), to deal in the Software without restriction,
#  including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#
# simsystem.py
import logging
import time
from multiprocessing import shared_memory as shm

import psygnal
from astropy.time import Time, TimeDeltaSec

# from sim_object import SimObject
from sim_body import SimBody
# from sim_ship import SimShip
from simobj_dict import SimObjectDict

# from simbod_dict import SimBodyDict
# from simshp_dict import SimShipDict

# from poliastro.bodies import Body
# from PyQt5.QtCore import QObject

logging.basicConfig(filename="../logs/sns_sysmod.log",
                    level=logging.ERROR,
                    format="%(funcName)s:\t\t%(levelname)s:%(asctime)s:\t%(message)s",
                    )


class SimSystem(SimObjectDict):
    """
    """
    initialized = psygnal.Signal(list)
    panel_data = psygnal.Signal(list, list)

    def __init__(self, buff0=None, buff1=None, *args, **kwargs):
        """
            Initialize the star system model. Two Queues are passed to provide
            communication with the main process along with two shared memory buffers.

        Parameters
        ----------
        buff0, buff1    : Two shared memory buffers of the same correct size

        """
        self._t0 = self._base_t = time.perf_counter()
        super(SimSystem, self).__init__([], *args, **kwargs)
        self._t1 = time.perf_counter()
        self._t0 = self._t1
        print(f'SimSystem declaration took {(self._t1 - self._base_t) * 1e-06:.4f} seconds...')
        # TODO :: Instead of using the following tuple, simply collect the essential fields,
        #         then collect one or more of the orbital elements type. 'rad0' is static.
        self._model_fields2agg = ('rad0', 'pos', 'rot', 'radius',
                                  'elem_coe_', 'elem_pqw_', 'elem_rv',
                                  'is_primary',
                                  )

        # TODO :: move the remainder of this method into its own method to be called once the
        #         bodies to be included the system have been selected.

        #   this method loads up all the default planets with no argument
        self.load_from_names()
        #   run an initial cycle of the states to make sure something is there
        self.update_state(self.epoch)

        #   determine the bytes needed to hold one body state
        self._state_size = self.data['Earth'].state.nbytes

        #   create two areas of shared memory unless proper buffers are provided
        if buff0 and buff1:
            if isinstance(buff0, shm.SharedMemory) and isinstance(buff1, shm.SharedMemory):
                if (buff0.size != self.num_bodies * self._state_size) or (buff0.size != self.num_bodies * self._state_size):
                    print(f"WARNING: one or more buffers are not the correct size !!! Setting defaults...")
                    buff0, buff1 = self._get_shm_buffs()

            else:
                buff0, buff1 = self._get_shm_buffs()
                raise Exception(f"ERROR. Type {type(buff0)} or {type(buff1)} is not shm.SharedMemory !!!\n",
                                f"Setting defaults...")

        else:
            print(f"WARNING: No memory buffer provided !!!\n>>>>>>>> I suppose we must generate one...")
            buff0, buff1 = self._get_shm_buffs()

        self._membuffs = [buff0, buff1]
        self._curr_buff = 0
        self._state_buffers = None

    # def __del__(self):
    #     """ Make sure the SharedMemory gets deallocated
    #     """
    #
        # [buff.close() for buff in self._membuffs]
        # [buff.unlink() for buff in self._membuffs]

    def load_from_names(self, names=None):
        """ Load the bodies into the system from a list of names.
            If no names are provided, the default set of bodies is loaded.
        Parameters
        ----------
        names   : list of str, optional
                  The names of the bodies to be loaded. If not provided, the default set is used.
        """
        if names is None:
            names = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']

        for name in names:
            self.add_body(name)

        self._num_bodies = len(self.data)
        self._state_size = self.data['Earth'].state.nbytes

        self.initialized.emit([self.num_bodies, self._state_size])

        # TODO: move this function up into SimSystem class
        """
            This method creates one or more SimBody objects based upon the provided list of names.
            CONSIDER: Should this be a class method that returns a SimSystem() when given names?

        Parameters
        ----------
        _body_names :

        Returns
        -------
        nothing     : Leaves the model usable with SimBody objects loaded
        """
        if _body_names is None:
            self._current_body_names = self._valid_body_names
        else:
            self._current_body_names = (n for n in _body_names
                                        if n in self._valid_body_names)

        # populate the list with SimBody objects
        self.data.clear()
        [self.data.update({body_name: SimBody(body_data=self.ref_data.body_data[body_name],
                                              vizz_data=self.ref_data.vizz_data()[body_name])})
         for body_name in self._current_body_names]

        self._body_count = len(self.data)
        # self._sys_primary = [sb for sb in self.data.values() if sb.body.parent is None][0]
        self.set_parentage()
        self._IS_POPULATED = True

        self.update_state(epoch=self._sys_epoch)
        self._HAS_INIT = True
        # self.set_field_dict()


    def _get_shm_buffs(self):
        """ Create two shared memory buffers according to the number of bodies present and
            the size of state information for each body.

            ReturnsS bo, b1 are two equally sized shared memory buffers,
            explicitly destroyed in __del__
        """
        b0 = shm.SharedMemory(create=True,
                              name="state_buff0",
                              size=self.num_bodies * self._state_size)
        b1 = shm.SharedMemory(create=True,
                              name="state_buff1",
                              size=self.num_bodies * self._state_size)
        return b0, b1

    def get_agg_fields(self, field_ids):
        # res = {'primary_name': self.system_primary.name}
        res = {}
        for f_id in field_ids:
            agg = {}
            [agg.update({sb.name: self.get_sbod_field(sb, f_id)})
             for sb in self.data.values()]
            res.update({f_id: agg})

        return res

    def get_sbod_field(self, _simbod, field_id):
        """
            This method retrieves the values of a particular field for a given SimBody object.
            Uses the field_id key to indicate which property to return.
        Parameters
        ----------
        _simbod             : SimBody            The SimBody object for which the field value is to be retrieved.
        field_id            : str                The field for which the value is to be retrieved.

        Returns
        -------
        simbod.<field_id>   : float or list       The value of the field for the given SimBody object.
        """
        match field_id:
            case 'attr_':
                return _simbod.attr

            case 'elem_coe_':
                return _simbod.elem_coe

            case 'elem_pqw_':
                return _simbod.elem_pqw

            case 'elem_rv_':
                return _simbod.elem_rv

            case 'radius':
                return _simbod.radius

            case 'pos':
                return _simbod.pos

            case 'rot':
                return _simbod.rot

            case 'axes':
                return _simbod.axes

            case 'track_data':
                return _simbod.track

            case 'radius':
                return _simbod.radius

            case 'is_primary':
                return _simbod.is_primary

            case 'parent_name':
                if _simbod.body.parent:
                    return _simbod.body.parent.name

            case 'tex_data':
                # TODO: Add a condition to check if texture data exists in an existing Planet visual.
                #       If it exists, return its texture data. Otherwise return the default texture data.
                return self.ref_data.vizz_data(name=_simbod.name)['tex_data']

            # these elements can should live in the viewer
            case 'body_alpha':
                return _simbod.body_alpha

            case 'track_alpha':
                return _simbod.track_alpha

            case 'body_mark':
                return _simbod.body_mark

            case 'body_color':
                return _simbod.body_color

        pass

    '''===== PROPERTIES ==========================================================================================='''

    @property
    def epoch(self):
        return self._sys_epoch

    @epoch.setter
    def epoch(self, new_epoch):
        if new_epoch:
            if type(new_epoch) == Time:
                self._sys_epoch = new_epoch

            elif type(new_epoch) == TimeDeltaSec:
                self._sys_epoch += new_epoch

        if self.USE_AUTO_UPDATE_STATE:
            self.update_state(self._sys_epoch)

    @property
    def dist_unit(self):
        return self._dist_unit

    @property
    def positions(self):
        """
        Returns
        -------
        dict    :   a dictionary of the positions of the bodies in the system keyed by name.
        """
        return dict.fromkeys(list(self.data.keys()),
                             [sb.pos for sb in self.data.values()])

    @property
    def radii(self):
        """
        Returns
        -------
        res    :   a dictionary of the mean radius of the bodies in the system keyed by name.
        """
        res = {}
        [res.update({sb.name: sb.radius}) for sb in self.data.values()]
        return res

    @property
    def body_names(self):
        return tuple(self.data.keys())

    @property
    def system_primary(self):
        return self._sys_primary

    @property
    def tracks_data(self):
        """
        Returns
        -------
        dict    :   a dictionary of the orbit tracks of the bodies in the system keyed by name.
        """
        res = {}
        [res.update({k: self.data[k].track}) for k in self.data.keys() if not self.data[k].is_primary]

        return res

    @property
    def body_color(self):
        res = {}
        return res

    @property
    def body_alpha(self):
        res = {}
        return res

    @property
    def track_color(self):
        res = {}
        return res

    @property
    def body_mark(self):
        res = {}
        return res


'''==============================================================================================================='''
if __name__ == "__main__":
    def main():
        ref_time = time.perf_counter()

        model = SimSystem({})
        model.load_from_names()
        init_time = time.perf_counter()

        model.update_state(model.epoch)
        done_time = time.perf_counter()

        # print(f"Setup time: {((init_time - ref_time) / 1e+09):0.4f} seconds")
        # print(f'Update time: {((done_time - init_time) / 1e+09):0.4f} seconds')

        print(f"Setup time: {(init_time - ref_time)} seconds")
        print(f'Update time: {(done_time - init_time)} seconds')


    main()
