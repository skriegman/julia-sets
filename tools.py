import numpy as np
from scipy.ndimage.measurements import label


def julia_set(c=-0.4 + 0.6j, height=50, width=50, zoom=1.5, max_iterations=100):
    x = np.linspace(-zoom, zoom, width).reshape((1, width))
    y = np.linspace(-zoom, zoom, height).reshape((height, 1))
    z = x + 1j * y
    c = np.full(z.shape, c)
    div_time = np.zeros(z.shape, dtype=int)
    m = np.full(c.shape, True, dtype=bool)
    for i in range(max_iterations):
        z[m] = z[m]**2 + c[m]
        m[np.abs(z) > 2] = False
        div_time[m] = i
    return div_time


def make_one_shape_only(output_state):
    """Find the largest continuous arrangement of True elements after applying boolean mask.
    Avoids multiple disconnected softbots in simulation counted as a single individual.
    Parameters
    ----------
    output_state : numpy.ndarray
        Network output
    Returns
    -------
    part_of_ind : bool
        True if component of individual
    """
    if np.sum(output_state) == 0:
        return output_state

    # find coordinates
    array = output_state > 0
    labeled, ncomponents = label(array)

    largest_count = 0
    largest_label = 0
    for n in range(ncomponents+1):
        this_count = np.sum(labeled == n)
        vox_count = np.sum(array[labeled == n])
        if (this_count > largest_count) and (vox_count > 0):
            largest_label = n
            largest_count = this_count

    return labeled == largest_label


