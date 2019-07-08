from matplotlib import pyplot as plt
from scipy.spatial import ConvexHull
from matplotlib.path import Path
import matplotlib.patches as patches
import operator as op
from random import random, randint


def length(vect):
    return sum(map(lambda x: x**2, vect)) ** (.5)


def normalize(vect):
    _length = sum(map(lambda x: x**2, vect))
    _inv_length = _length ** (-.5)
    return tuple(map(_inv_length.__mul__, vect))


def draw_hull(points, margin, axes=None, **kwargs):
    """
    Draw a convex hull with a tunable margin around a set of points.
    kwargs are passed to the patches function when generating patches that are
    then added as an artist to axes.
    """
    if kwargs.get('do_disturb', True):
        for i in range(len(points)):
            x, y = points[i]
            x = x * (1 + 0.01*randint(-1, 1)*random())
            y = y * (1 + 0.01*randint(-1, 1)*random())
            points[i] = (x, y)
    if not axes:
        axes = plt.gca()
    margin = float(margin)
    curve_span = kwargs.pop('curve_span', margin)
    _att = kwargs.pop('attenuation', 1.5)
    if len(points) == 1:
        from matplotlib.patches import Circle
        circ = Circle(points[0], radius=margin, **kwargs)
        axes.add_artist(circ)
    else:
        outer_points = []
        operations = []
        if len(points) == 2:
            point_idxs = 2 * list(range(2))
        else:
            hull = ConvexHull(points)
            point_idxs = hull.vertices
        for _i in range(len(point_idxs)):
            p0 = points[point_idxs[_i-2]]
            p1 = points[point_idxs[_i-1]]
            p2 = points[point_idxs[_i]]
            l1 = tuple(map(op.sub, p1, p0))
            _l1_o = (l1[1], -l1[0])
            l1_o_n = normalize(_l1_o)
            l1_margin = tuple(map(margin.__mul__, l1_o_n))
            p1_side = tuple(map(op.add, p1, l1_margin))
            p1_side = tuple(map(op.add, p1, l1_margin))
            outer_points.append(p1_side)
            l2 = tuple(map(op.sub, p2, p1))
            _l2_o = (l2[1], -l2[0])
            l2_o_n = normalize(_l2_o)
            l2_margin = tuple(map(margin.__mul__, l2_o_n))
            p1_side2 = tuple(map(op.add, p1, l2_margin))
            p1_p2_dist = length(tuple(map(op.__sub__, p1_side2, p1_side)))
            l1_n = normalize(l1)
            l1_ext = tuple(map(
                (curve_span * (p1_p2_dist / (2 * margin)) ** _att).__mul__,
                l1_n
                ))
            p1_side_ext = tuple(map(op.add, p1_side, l1_ext))
            outer_points.append(p1_side_ext)
            l2_n = normalize(l2)
            l2_ext = tuple(map(
                (-curve_span * (p1_p2_dist / (2 * margin)) ** _att).__mul__,
                l2_n
                ))
            p1_side_ext2 = tuple(map(op.add, p1_side2, l2_ext))
            outer_points.append(p1_side_ext2)
            outer_points.append(p1_side2)
            operations.extend(
                    [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                    )
        outer_points.append(outer_points[0])
        operations.append(Path.CLOSEPOLY)
        operations[0] = Path.MOVETO
        hull_path = Path(outer_points, operations, closed=True)
        axes.add_artist(patches.PathPatch(hull_path, **kwargs))
