#  Copyright <YEAR> <COPYRIGHT HOLDER>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import numpy as np
from vispy.scene import SceneCanvas
from vispy.scene.cameras import FlyCamera

# Create a canvas
canvas = SceneCanvas(keys='interactive')

# Create a camera
camera = FlyCamera(fov=60)

# Attach the camera to the canvas
canvas.camera = camera


# Function to make the camera aim at a specific point
def aim_camera_at_point(point):
    # Get the current camera position
    camera_pos = camera.center

    # Calculate the direction vector from camera position to the target point
    direction = point - camera_pos

    # Calculate the rotation quaternion
    rotation_quat = quaternion_from_vector_to_vector(np.array([0, 0, 1]), direction)

    # Update the camera rotation
    camera.rotation1 = rotation_quat


# Helper function to calculate quaternion from one vector to another
def quaternion_from_vector_to_vector(v1, v2):
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    axis = np.cross(v1, v2)
    angle = np.arccos(np.dot(v1, v2))
    return quaternion_from_axis_angle(axis, angle)


# Helper function to create quaternion from axis-angle representation
def quaternion_from_axis_angle(axis, angle):
    norm_axis = axis / np.linalg.norm(axis)
    half_angle = angle / 2
    w = np.cos(half_angle)
    xyz = norm_axis * np.sin(half_angle)
    return np.array([w, *xyz])


# Example target point
target_point = np.array([0, 0, 0])

# Aim the camera at the target point
aim_camera_at_point(target_point)

# Show the canvas
canvas.show()

# Run the application
canvas.app.run
