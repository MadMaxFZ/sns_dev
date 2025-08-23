
#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import math
import sys

import numpy as np
from astropy.time import Time
from astropy.units import Quantity as u
from pathlib2 import Path
from PIL import Image
from poliastro.constants import J2000_TDB
from pyquaternion import Quaternion
from vispy.geometry.meshdata import MeshData
from vispy.util.quaternion import Quaternion

"""------------------------  UTILITY FUNCTIONS --------------------------------------------"""
P = Path("c:")
DEF_TEX_FNAME = P / "../resources/textures/2k_5earth_daymap.png"

def quat_to_rpy(quat):
    if quat is not None and type(quat) == Quaternion:
        # quat.w = abs(quat.w)
        t0 = +2.0 * (quat.w * quat.x + quat.y * quat.z)
        t1 = +1.0 - 2.0 * (quat.x * quat.x + quat.y * quat.y)
        yaw_x = round(math.atan2(t0, t1) * 180 / math.pi, 4)

        t2 = +2.0 * (quat.w * quat.y - quat.z * quat.x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = round(math.asin(t2) * 180 / math.pi - 90, 4)

        t3 = +2.0 * (quat.w * quat.z + quat.x * quat.y)
        t4 = +1.0 - 2.0 * (quat.y * quat.y + quat.z * quat.z)
        roll_z = round(math.atan2(t3, t4) * 180 / math.pi, 4)

        # if yaw_x >= 180:
        #     yaw_x -= 360
        # elif yaw_x <= -180:
        #     yaw_x += 360
        #
        # if roll_z >= 180:
        #     roll_z -= 360
        # elif roll_z <= -180:
        #     roll_z += 360

        return yaw_x, pitch_y, roll_z

    return None


def to_rpy_str(quat):
    yaw_x, pitch_y, roll_z = quat_to_rpy(quat)

    eul_str = str("R: " + pad_plus(f'{roll_z:5.4}') +
                  "\nP: " + pad_plus(f'{pitch_y:5.4}') +
                  "\nY: " + pad_plus(f'{yaw_x:5.4}'))

    return eul_str


def get_texture_data(fname=DEF_TEX_FNAME):
    with Image.open(fname) as im:
        print(fname, im.format, f"{im.size}x{im.mode}")
        return im.copy()


def toTD(epoch=None):
    """
        This function converts an epoch into julian date since epoch and
    Parameters
    ----------
    epoch

    Returns
    -------

    """
    d = (epoch - J2000_TDB).jd
    T = d / 36525
    return dict(T=T, d=d)


def earth_rot_elements_at_epoch(epoch):
    """"""
    T, d = list(toTD(epoch).values())
    _T = T
    return 0, 90 - 23.5, (d - math.floor(d)) * 360.0


def t_since_ref(epoch=None, ref=J2000_TDB):
    """"""
    if epoch is None:
        epoch = Time.now()

    t_since = epoch - ref
    # calculate dt of epoch and J2000
    rot_T = (t_since / 36525.0).value  # dt in centuries
    rot_d = t_since.to(u.day).value  # dt in days
    return rot_T, rot_d


# taken from https://goshippo.com/blog/measure-real-size-any-python-object by Wissam Jarjoui
def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


def _latitude(rows=4, cols=8, radius=1, offset=False):
    verts = np.empty((rows + 1, cols, 3), dtype=np.float32)

    # compute vertices
    phi = (np.arange(rows + 1) * np.pi / rows).reshape(rows + 1, 1)
    s = radius * np.sin(phi)
    verts[..., 2] = radius * np.cos(phi)
    th = ((np.arange(cols) * 2 * np.pi / cols).reshape(1, cols))
    if offset:
        # rotate each row by 1/2 column
        th = th + ((np.pi / cols) * np.arange(rows + 1).reshape(rows + 1, 1))
    verts[..., 0] = s * np.cos(th)
    verts[..., 1] = s * np.sin(th)
    # remove redundant vertices from top and bottom
    verts = verts.reshape((rows + 1) * cols, 3)[cols - 1:-(cols - 1)]

    # compute faces
    faces = np.empty((rows * cols * 2, 3), dtype=np.uint32)
    rowtemplate1 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[1, 0, 0]])) % cols) +
                    np.array([[0, 0, cols]]))
    rowtemplate2 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[1, 0, 1]])) % cols) +
                    np.array([[0, cols, cols]]))
    for row in range(rows):
        start = row * cols * 2
        faces[start:start + cols] = rowtemplate1 + row * cols
        faces[start + cols:start + 2 * cols] = rowtemplate2 + row * cols
    # cut off zero-area triangles at top and bottom
    faces = faces[cols:-cols]

    # adjust for redundant vertices that were removed from top and bottom
    vmin = cols - 1
    faces[faces < vmin] = vmin
    faces -= vmin
    vmax = verts.shape[0] - 1
    faces[faces > vmax] = vmax
    return MeshData(vertices=verts, faces=faces)


def _oblate_sphere(rows=4, cols=None, radius=(1200,) * 3, offset=False):
    verts = np.empty((rows + 1, cols + 1, 3), dtype=np.float32)
    tcrds = np.empty((rows + 1, cols + 1, 2), dtype=np.float32)
    norms = np.linalg.norm(verts)

    # compute vertices
    phi = (np.arange(rows + 1) * np.pi / rows).reshape(rows + 1, 1)
    s = radius[0] * np.sin(phi)
    verts[..., 2] = radius[2] * np.cos(phi)
    th = ((np.arange(cols + 1) * 2 * np.pi / cols).reshape(1, cols + 1))
    # if offset:
    #     # rotate each row by 1/2 column
    #     th = th + ((np.pi / cols) * np.arange(rows+1).reshape(rows+1, 1))
    verts[..., 0] = s * np.cos(th)
    verts[..., 1] = s * np.sin(th)
    tcrds[..., 0] = th / (2 * np.pi)
    tcrds[..., 1] = 1 - phi / np.pi
    # remove redundant vertices from top and bottom
    verts = verts.reshape((rows + 1) * (cols + 1), 3)  # [cols:-cols]
    tcrds = tcrds.reshape((rows + 1) * (cols + 1), 2)  # [cols:-cols]

    # compute faces
    rowtemplate1 = (((np.arange(cols).reshape(cols, 1) + np.array([[1, 0, 0]])) % (cols + 2)) +
                    np.array([[0, 0, cols + 1]]))
    rowtemplate2 = (((np.arange(cols).reshape(cols, 1) + np.array([[1, 0, 1]])) % (cols + 2)) +
                    np.array([[0, cols + 1, cols + 1]]))
    # print(rowtemplate1.shape, "\n", rowtemplate2.shape)
    faces = np.empty((rows * cols * 2, 3), dtype=np.uint32)
    for row in range(rows):
        start = row * cols * 2
        if row != 0:
            faces[start:start + cols] = rowtemplate1 + row * (cols + 1)
        if row != rows - 1:
            faces[start + cols:start + (2 * cols)] = rowtemplate2 + row * (cols + 1)
    faces = faces[cols:-cols]

    edges = MeshData(vertices=verts, faces=faces).get_edges()
    eclrs = np.zeros((len(edges), 4), dtype=np.float32)
    eclrs[np.arange(len(edges)), :] = (1, 1, 1, 1)

    return dict(verts=verts,
                norms=norms,
                faces=faces,
                edges=edges,
                ecolr=eclrs,
                tcord=tcrds,
                )


def round_off(val, n_digits=3):
    factor = pow(10, n_digits)
    try:
        data_unit = val / val.value
        res = (int(val.value * factor) / factor) * data_unit

    except AttributeError:
        res = val

    return res


def show_it(value):
    # print(f"VAL: {value}, TYPE(VAL): {type(value)}")
    pass


def to_bold_font(value: str):
    if value:
        ante = "<html><head/><body><p><span style=\" font-weight:600;\">"
        post = "</span></p></body></html>"

        return ante + str(value) + post

    return ""


def pad_plus(value):
    if value:
        res = value
        if float(value) > 0:
            res = "+" + value

        return res

    else:
        return ''


def to_vector_str(vec, hdrs=None):
    if vec is not None:
        # print(f'{type(vec)}')
        if not hdrs:
            hdrs = ('X:', '\nY:', '\nZ:')
        # vec = vec.value
        vec_str = str(hdrs[0] + pad_plus(f'{vec[0]:5.4}') +
                      hdrs[1] + pad_plus(f'{vec[1]:5.4}') +
                      hdrs[2] + pad_plus(f'{vec[2]:5.4}'))

        return vec_str

    return ""


def to_quat_str(quat):
    if quat is not None:
        # print(f'{type(quat)}')
        quat_str = str("X: " + f'{quat.x:5.4}' +
                       "\nY: " + f'{quat.y:5.4}' +
                       "\nZ: " + f'{quat.z:5.4}' +
                       "\nW: " + f'{quat.w:5.4}')

        return quat_str

    return ""



# log_config = {
#     "version": 1,
#     "formatters": {
#         "logformatter": {
#             "format":
#                 "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s",
#         },
#         "traceformatter": {
#             "format":
#                 "%(asctime)s:%(process)s:%(levelname)s:%(filename)s:"
#                 "%(lineno)s:%(name)s:%(funcName)s:%(message)s",
#         },
#     },
#     "handlers": {
#         "loghandler": {
#             "class": "logging.FileHandler",
#             "level": logging.DEBUG,
#             "formatter": "logformatter",
#             "filename": "app.log",
#         },
#         "tracehandler": {
#             "class": "logging.FileHandler",
#             "level": autologging.TRACE,
#             "formatter": "traceformatter",
#             "filename": "trace.log",
#         },
#     },
#     "loggers": {
#         "my_module.MyClass": {
#             "level": autologging.TRACE,
#             "handlers": ["tracehandler", "loghandler"],
#         },
#     },
# }


if __name__ == "__main__":
    pass
    # def main():
    #     # logging.debug("-------->> RUNNING SYSTEM_DATASTORE() STANDALONE <<---------------")
    #
    #     dict_store = SystemDataStore()

        # print("dict store:", dict_store)
        # print(dict_store.body_data["Earth"])
        #
        # with open("_data_store.pkl", "wb") as f:
        #     pickle.dump(dict_store, f)
        #
        # print("Pickling completed....")
        # print("Recovering pickle...")
        #
        # with open("_data_store.pkl", "rb") as f:
        #     data_recover = pickle.load(f)
        #
        # print("dict recovery:", data_recover)
        # print(data_recover.body_data["Earth"])
        #
        # if type(dict_store) == type(data_recover):
        #     print("pickle/unpickle successful!!!")
        # else:
        #     print("Something didn't match....")

        # exit()


    # main()

"""
    The following moons of the Solar System are tidally locked:
        Mercury:    (3-2 spin-orbit resonance)
        
        Earth:      Moon
        
        Mars:       Phobos
                    Deimos
        
        Jupiter:    Io
                    Europa
                    Ganymede
                    Callisto
                    Amalthea
                    Himalia
                    Elara
                    Pasiphae
                    Metis
                    Adrastea
                    Thebe
        
        Saturn:     Titan
                    Enceladus
                    Pan
                    Atlas
                    Prometheus
                    Pandora
                    Epimetheus
                    Janus
                    Mimas
                    Telesto
                    Tethys
                    Calypso
                    Dione
                    Rhea
                    Iapetus
                    - Daphnis
                    - Aegaeon
                    - Methone
                    - Anthe
                    - Pallene
                    - Helene
                    - Polydeuces
                    Hyperion    (rotates chaotically)
        
        Uranus:     Miranda
                    Ariel
                    Umbriel
                    Titania
                    Oberon
                    - Cordelia
                    - Ophelia
                    - Bianca
                    - Cressida
                    - Desdemona
                    - Juliet
                    - Portia
                    - Rosalind
                    - Cupid
                    - Belinda
                    - Perdita
                    - Puck
                    - Mab
        
        Neptune:    Proteus
                    Triton
                    - Naiad
                    - Thalassa
                    - Despina
                    = Galatea
                    - Larissa
        
        Pluto:      Charon      (mutually locked)
        
        Eris:       Dysnomia    (mutually locked)

        Orcus:      Vanth       (mutually locked)
"""
