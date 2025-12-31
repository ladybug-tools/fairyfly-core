# coding: utf-8
"""Dragonfly Context Shade."""
from __future__ import division
import re
import math

from ladybug_geometry.geometry3d import Point3D, LineSegment3D, Polyline3D, Plane

from ._base import _Base
from .search import get_attr_nested
from .properties import BoundaryProperties
import fairyfly.writer.boundary as writer


class Boundary(_Base):
    """A Context Shade object defined by an array of Face3Ds and/or Mesh3Ds.

    Args:
        geometry: An array of ladybug_geometry LineSegment3D objects
            that together represent a type of boundary in a construction detail.
        identifier: Text string for a unique Boundary ID. Must be a UUID in the
            format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx. If None, a UUID will
            automatically be generated. (Default: None).

    Properties:
        * identifier
        * display_name
        * therm_uuid
        * full_id
        * parent
        * has_parent
        * geometry
        * vertices
        * length
        * min
        * max
        * center
        * user_data
    """
    __slots__ = ('_geometry', '_parent')

    def __init__(self, geometry, identifier=None):
        """Initialize Boundary."""
        _Base.__init__(self, identifier)  # process the identifier

        # process the geometry
        if not isinstance(geometry, tuple):
            geometry = tuple(geometry)
        assert len(geometry) > 0, 'Boundary must have at least one geometry.'
        for l_geo in geometry:
            assert isinstance(l_geo, LineSegment3D), 'Expected ladybug_geometry ' \
                'LineSegment3D. Got {}'.format(type(l_geo))
        self._geometry = geometry
        self._parent = None  # _parent will be set when Boundary is added to an object
        self._properties = BoundaryProperties(self)  # properties for extensions

    @classmethod
    def from_dict(cls, data):
        """Initialize an Boundary from a dictionary.

        Args:
            data: A dictionary representation of an Boundary object.
        """
        # check the type of dictionary
        assert data['type'] == 'Boundary', 'Expected Boundary dictionary. ' \
            'Got {}.'.format(data['type'])
        # serialize the geometry
        geometry = []
        for l_geo in data['geometry']:
            if l_geo['type'] == 'LineSegment3D':
                geometry.append(LineSegment3D.from_dict(l_geo))
            else:  # it is a polyline
                verts = tuple(Point3D.from_array(pt) for pt in data['vertices'])
                if len(verts) == 2:
                    geometry.append(LineSegment3D.from_end_points(*l_geo))
                else:
                    poly_geo = Polyline3D(verts)
                    geometry.extend(poly_geo.segments)
        # create the Boundary
        bound = cls(geometry, data['identifier'])
        if 'display_name' in data and data['display_name'] is not None:
            bound.display_name = data['display_name']
        if 'user_data' in data and data['user_data'] is not None:
            bound.user_data = data['user_data']
        if data['properties']['type'] == 'BoundaryProperties':
            bound.properties._load_extension_attr_from_dict(data['properties'])
        return bound

    @classmethod
    def from_vertices(cls, vertices, identifier=None):
        """Create a Boundary from vertices with each vertex as an iterable of 3 floats.

        Args:
            vertices: A list of lists where each sub-list represents a line segment
                or polyline with 2 or more vertices. Each vertex is represented
                as an iterable of three (x, y, z) floats.
            identifier: Text string for a unique Shape ID. Must be a UUID in the
                format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx. If None, a UUID will
                automatically be generated. (Default: None).
        """
        geometry = []
        for l_geo in vertices:
            verts = tuple(Point3D.from_array(pt) for pt in l_geo)
            if len(verts) == 2:
                geometry.append(LineSegment3D.from_end_points(*verts))
            else:
                poly_geo = Polyline3D(verts)
                geometry.extend(poly_geo.segments)
        return cls(geometry, identifier)

    @property
    def parent(self):
        """Get the parent object if assigned. None if not assigned.

        The parent object is typically a GlazingSystem.
        """
        return self._parent

    @property
    def has_parent(self):
        """Get a boolean noting whether this Shape has a parent object."""
        return self._parent is not None

    @property
    def geometry(self):
        """Get a tuple of LineSegment3D objects that represent the boundary."""
        return self._geometry

    @property
    def vertices(self):
        """Get a list of vertices for the boundary."""
        return tuple(pt for geo in self._geometry for pt in geo.vertices)

    @property
    def length(self):
        """Get a number for the total length of the Boundary."""
        return sum([geo.length for geo in self._geometry])

    @property
    def min(self):
        """Get a Point3D for the minimum of the bounding box around the object."""
        return self._calculate_min(self._geometry)

    @property
    def max(self):
        """Get a Point3D for the maximum of the bounding box around the object."""
        return self._calculate_max(self._geometry)

    @property
    def center(self):
        """A Point3D for the center of the bounding box around the object."""
        mn, mx = self.min, self.max
        return Point3D((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, (mn.z + mx.z) / 2)

    def rename_by_attribute(self, format_str='{display_name} - {length}'):
        """Set the display name of this Boundary using a format string with attributes.

        Args:
            format_str: Text string for the pattern with which the Boundary will be
                renamed. Any property on this class may be used and each
                property should be put in curly brackets. Nested properties
                can be specified by using "." to denote nesting levels
                (eg. properties.energy.construction.display_name). Functions that
                return string outputs can also be passed here as long as these
                functions defaults specified for all arguments.
        """
        matches = re.findall(r'{([^}]*)}', format_str)
        attributes = [get_attr_nested(self, m, decimal_count=2) for m in matches]
        for attr_name, attr_val in zip(matches, attributes):
            format_str = format_str.replace('{{{}}}'.format(attr_name), attr_val)
        self.display_name = format_str
        return format_str

    def move(self, moving_vec):
        """Move this Boundary along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the object.
        """
        self._geometry = tuple(l_geo.move(moving_vec) for l_geo in self._geometry)
        self.properties.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate this Shape by a certain angle around an axis and origin.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        self._geometry = tuple(l_geo.rotate(axis, math.radians(angle), origin)
                               for l_geo in self._geometry)
        self.properties.rotate(axis, angle, origin)

    def rotate_xy(self, angle, origin):
        """Rotate this Boundary counterclockwise in the XY plane by a certain angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        self._geometry = tuple(l_geo.rotate_xy(math.radians(angle), origin)
                               for l_geo in self._geometry)
        self.properties.rotate_xy(angle, origin)

    def reflect(self, plane):
        """Reflect this Boundary across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will be reflected.
        """
        self._geometry = tuple(l_geo.reflect(plane.n, plane.o)
                               for l_geo in self._geometry)
        self.properties.reflect(plane)

    def scale(self, factor, origin=None):
        """Scale this Boundary by a factor from an origin point.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        self._geometry = tuple(l_geo.scale(factor, origin)
                               for l_geo in self._geometry)
        self.properties.scale(factor, origin)

    def check_planar(self, tolerance=0.01, raise_exception=True, detailed=False):
        """Check whether all of the Boundary's vertices lie within the same plane.

        Args:
            tolerance: The minimum distance between a given vertex and a the
                object's plane at which the vertex is said to lie in the plane.
                Default: 0.01, suitable for objects in millimeters.
            raise_exception: Boolean to note whether an ValueError should be
                raised if a vertex does not lie within the object's plane.
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        # collect all of the unique points
        pts = []
        for seg in self.geometry:
            for pt in seg.vertices:
                for o_pt in pts:
                    if pt.is_equivalent(o_pt, tolerance):
                        break
                else:  # the point is unique
                    pts.append(pt)
        # evaluate the points in relation to their plane
        if len(pts) > 3:
            plane = Plane.from_three_points(*pts[:3])
            for _v in pts[3:]:
                if plane.distance_to_point(_v) >= tolerance:
                    g_ms = 'Vertex {} does not lie in the same plane.\nDistance ' \
                        'to plane is {}'.format(_v, plane.distance_to_point(_v))
                    msg = 'Boundary "{}" is not planar.\n{}'.format(self.full_id, g_ms)
                    full_msg = self._validation_message(
                        msg, raise_exception, detailed, '200101',
                        error_type='Non-Planar Geometry')
                    if detailed:  # add the out-of-plane point to helper_geometry
                        full_msg[0]['helper_geometry'] = [_v.to_dict()]
                    return full_msg
        return [] if detailed else ''

    def to_dict(self, abridged=False, included_prop=None):
        """Return Boundary as a dictionary.

        Args:
            abridged: Boolean to note whether the extension properties of the
                object (ie. materials, transmittance schedule) should be included in
                detail (False) or just referenced by identifier (True). Default: False.
            included_prop: List of properties to filter keys that must be included in
                output dictionary. For example ['therm'] will include 'therm' key if
                available in properties to_dict. By default all the keys will be
                included. To exclude all the keys from extensions use an empty list.
        """
        base = {'type': 'Boundary'}
        base['identifier'] = self.identifier
        base['geometry'] = [l_geo.to_dict() for l_geo in self._geometry]
        base['properties'] = self.properties.to_dict(abridged, included_prop)
        if self._display_name is not None:
            base['display_name'] = self.display_name
        if self.user_data is not None:
            base['user_data'] = self.user_data
        return base

    @property
    def to(self):
        """Boundary writer object.

        Use this method to access Writer class to write the context in other formats.
        """
        return writer

    def __copy__(self):
        new_shd = Boundary(self._geometry, self.identifier)
        new_shd._display_name = self._display_name
        new_shd._user_data = None if self.user_data is None else self.user_data.copy()
        new_shd._properties._duplicate_extension_attr(self._properties)
        return new_shd

    def __len__(self):
        return len(self._geometry)

    def __getitem__(self, key):
        return self._geometry[key]

    def __iter__(self):
        return iter(self._geometry)

    def __repr__(self):
        return 'Boundary: %s' % self.display_name
