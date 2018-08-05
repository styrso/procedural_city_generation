from __future__ import division
import numpy as np
from procedural_city_generation.polygons.Polygon2D import Polygon2D
from procedural_city_generation.additional_stuff.Singleton import Singleton
import matplotlib.pyplot as plt
import procedural_city_generation.polygons.construct_polygons as cp

singleton=Singleton("polygons")

def p_in_poly(poly, point):
    x, y = point
    n = len(poly)
    inside = False

    p1x, p1y = poly[0][0]
    for i in range(n+1):
        p2x, p2y = poly[i % n][0]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def getBlock(wedges, vertex_list):
    '''Calculate block to be divided into lots, as well as street polygons'''

    old_vertices = [vertex_list[wedge.b] for wedge in wedges]
    old_poly = Polygon2D([v.coords for v in old_vertices])

    new_vertices = []
    polylist = []
    last2 = []

    for i in range(len(old_vertices)):

        # Calculate position of new vertex
        alpha = wedges[i-1].alpha
        a, b, c = old_vertices[i-2], old_vertices[i-1], old_vertices[i]
        v1 = a.coords - b.coords
        v2 = c.coords - b.coords
        n1 = np.array((-v1[1], v1[0]))/np.linalg.norm(v1)
        n2 = np.array((v2[1], -v2[0]))/np.linalg.norm(v2)

        # Change lengths of normal vectors depending on whether each
        # edge is a minor road or a main road
        if b.minor_road or a.minor_road:
            n1 *= singleton.minor_factor
        else:
            n1 *= singleton.main_factor
        if b.minor_road or c.minor_road:
            n2 *= singleton.minor_factor
        else:
            n2 *= singleton.main_factor

        # Check if current vertex is dead end
        if not 0 - 0.001 < alpha < 0 + 0.001:
            # Not a dead end: move edges which share this vertex
            # inwards along their normal vectors, find intersection
            try:
                intersection = np.linalg.solve(np.array(((v1), (v2))).T, (b.coords+n2)-(b.coords+n1))
            except np.linalg.LinAlgError:
                raise Exception(str(v1)+", "+str(v2), "angle: "+str(wedges[i-1].alpha))
            new = b.coords + n1 + intersection[0]*v1
            # Check if new vertex is in old polygon
            if p_in_poly(old_poly.edges, new):
                # Append new vertex to lot polygon
                new_vertices.append(new)
                these2 = [b.coords, new]
                if last2:
                    street_vertices = last2 + these2
                    polylist.append(Polygon2D(street_vertices, poly_type="road"))
                last2 = these2[::-1]
            else:
                # New vertex not in polygon, return old polygon as street polygon
                return [old_poly]
        else:
            # Dead end: determine two new vertices by adding the two normals
            # to current vector, then check if these are in old polygon
            new1, new2 = b.coords + n1, b.coords + n2
            if p_in_poly(old_poly.edges, new1) and p_in_poly(old_poly.edges, new2):
                new_vertices += [new1, new2]
                if last2:
                    street_vertices = last2 + [b.coords, new1]
                    polylist.append(Polygon2D(street_vertices, poly_type="road"))
                    street_vertices = [b.coords, new2, new1]
                    polylist.append(Polygon2D(street_vertices, poly_type="road"))
                last2 = [new2, b.coords]

            else:
                old_poly.poly_type="road"
                return [old_poly]
    street_vertices = last2 + [old_vertices[-1].coords, new_vertices[0]]
    polylist.append(Polygon2D(street_vertices, poly_type="road"))

    # All new vertices are in old polygon: append block polygon
    block_poly = Polygon2D(new_vertices)
    if block_poly.area < singleton.max_area:
        block_poly.poly_type="lot"
    polylist.append(block_poly)
    return polylist


if __name__ == "__main__":
    polys, vertices = cp.main()
    for p in getBlock(polys[1], vertices):
        p.selfplot()
    plt.show()


