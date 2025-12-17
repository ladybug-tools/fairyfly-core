# coding: utf-8
"""Honeybee Shape."""
from __future__ import division
import math
import re

from ladybug_geometry.geometry3d import Point3D, Face3D

from ._base import _Base
from .search import get_attr_nested
from .properties import ShapeProperties
import fairyfly.writer.shape as writer


class Shape(_Base):
    """A single planar shape.

    Args:
        geometry: A ladybug-geometry Face3D.
        identifier: Text string for a unique Shape ID. Must be a UUID in the
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
        * normal
        * center
        * area
        * perimeter
        * min
        * max
        * tilt
        * altitude
        * azimuth
        * user_data
    """
    __slots__ = ('_geometry', '_parent')

    def __init__(self, geometry, identifier=None):
        """A single planar shape."""
        _Base.__init__(self, identifier)  # process the identifier

        # process the geometry and basic properties
        assert isinstance(geometry, Face3D), \
            'Expected ladybug_geometry Face3D. Got {}'.format(type(geometry))
        self._geometry = geometry
        self._parent = None  # _parent will be set when the Shape is added to an object

        # initialize properties for extensions
        self._properties = ShapeProperties(self)

    @classmethod
    def from_dict(cls, data):
        """Initialize an Shape from a dictionary.

        Args:
            data: A dictionary representation of an Shape object.
        """
        try:
            # check the type of dictionary
            assert data['type'] == 'Shape', 'Expected Shape dictionary. ' \
                'Got {}.'.format(data['type'])
            # serialize the dictionary to an object
            shape = cls(Face3D.from_dict(data['geometry']), data['identifier'])
            if 'display_name' in data and data['display_name'] is not None:
                shape.display_name = data['display_name']
            if 'user_data' in data and data['user_data'] is not None:
                shape.user_data = data['user_data']
            # serialize the properties
            if data['properties']['type'] == 'ShapeProperties':
                shape.properties._load_extension_attr_from_dict(data['properties'])
            return shape
        except Exception as e:
            cls._from_dict_error_message(data, e)

    @classmethod
    def from_vertices(cls, vertices, identifier=None):
        """Create a Shape from vertices with each vertex as an iterable of 3 floats.

        Note that this method is not recommended for a shape with one or more holes
        since the distinction between hole vertices and boundary vertices cannot
        be derived from a single list of vertices.

        Args:
            vertices: A flattened list of 3 or more vertices as (x, y, z).
            identifier: Text string for a unique Shape ID. Must be a UUID in the
                format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx. If None, a UUID will
                automatically be generated. (Default: None).
        """
        geometry = Face3D(tuple(Point3D(*v) for v in vertices))
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
        """Get a ladybug_geometry Face3D object representing the Shape."""
        return self._geometry

    @property
    def vertices(self):
        """Get a list of vertices for the shape (in counter-clockwise order)."""
        return self._geometry.vertices

    @property
    def normal(self):
        """Get a ladybug_geometry Vector3D for the direction the shape is pointing.
        """
        return self._geometry.normal

    @property
    def center(self):
        """Get a ladybug_geometry Point3D for the center of the shape.

        Note that this is the center of the bounding rectangle around this geometry
        and not the area centroid.
        """
        return self._geometry.center

    @property
    def area(self):
        """Get the area of the shape."""
        return self._geometry.area

    @property
    def perimeter(self):
        """Get the perimeter of the shape."""
        return self._geometry.perimeter

    @property
    def min(self):
        """Get a Point3D for the minimum of the bounding box around the object."""
        return self._geometry.min

    @property
    def max(self):
        """Get a Point3D for the maximum of the bounding box around the object."""
        return self._geometry.max

    @property
    def tilt(self):
        """Get the tilt of the geometry between 0 (up) and 180 (down)."""
        return math.degrees(self._geometry.tilt)

    @property
    def altitude(self):
        """Get the altitude of the geometry between +90 (up) and -90 (down)."""
        return math.degrees(self._geometry.altitude)

    @property
    def azimuth(self):
        """Get the azimuth of the geometry, between 0 and 360.

        Given Y-axis as North, 0 = North, 90 = East, 180 = South, 270 = West
        This will be zero if the Face3D is perfectly horizontal.
        """
        return math.degrees(self._geometry.azimuth)

    def rename_by_attribute(self, format_str='{display_name} - {area}'):
        """Set the display name of this Shape using a format string with attributes.

        Args:
            format_str: Text string for the pattern with which the Shape will be
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
        """Move this Shape along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the face.
        """
        self._geometry = self.geometry.move(moving_vec)
        self.properties.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate this Shape by a certain angle around an axis and origin.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        self._geometry = self.geometry.rotate(axis, math.radians(angle), origin)
        self.properties.rotate(axis, angle, origin)

    def rotate_xy(self, angle, origin):
        """Rotate this Shape counterclockwise in the world XY plane by a certain angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        self._geometry = self.geometry.rotate_xy(math.radians(angle), origin)
        self.properties.rotate_xy(angle, origin)

    def reflect(self, plane):
        """Reflect this Shape across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will be reflected.
        """
        self._geometry = self.geometry.reflect(plane.n, plane.o)
        self.properties.reflect(plane)

    def scale(self, factor, origin=None):
        """Scale this Shape by a factor from an origin point.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        self._geometry = self.geometry.scale(factor, origin)
        self.properties.scale(factor, origin)

    def remove_colinear_vertices(self, tolerance=0.01):
        """Remove all colinear and duplicate vertices from this object's geometry.

        Args:
            tolerance: The minimum distance between a vertex and the boundary segments
                at which point the vertex is considered colinear. Default: 0.01,
                suitable for objects in meters.
        """
        try:
            self._geometry = self.geometry.remove_colinear_vertices(tolerance)
        except AssertionError as e:  # usually a sliver face of some kind
            raise ValueError(
                'Shape "{}" is invalid with dimensions less than the '
                'tolerance.\n{}'.format(self.full_id, e))

    def is_geo_equivalent(self, shape, tolerance=0.01):
        """Get a boolean for whether this object is geometrically equivalent to another.

        The total number of vertices and the ordering of these vertices can be
        different but the geometries must share the same center point and be
        next to one another to within the tolerance.

        Args:
            shape: Another Shape for which geometric equivalency will be tested.
            tolerance: The minimum difference between the coordinate values of two
                vertices at which they can be considered geometrically equivalent.

        Returns:
            True if geometrically equivalent. False if not geometrically equivalent.
        """
        if self.display_name != shape.display_name:
            return False
        if abs(self.area - shape.area) > tolerance * self.area:
            return False
        return self.geometry.is_centered_adjacent(shape.geometry, tolerance)

    def check_planar(self, tolerance=0.01, raise_exception=True, detailed=False):
        """Check whether all of the Shape's vertices lie within the same plane.

        Args:
            tolerance: The minimum distance between a given vertex and a the
                object's plane at which the vertex is said to lie in the plane.
                Default: 0.01, suitable for objects in meters.
            raise_exception: Boolean to note whether an ValueError should be
                raised if a vertex does not lie within the object's plane.
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        try:
            self.geometry.check_planar(tolerance, raise_exception=True)
        except ValueError as e:
            msg = 'Shape "{}" is not planar.\n{}'.format(self.full_id, e)
            full_msg = self._validation_message(
                msg, raise_exception, detailed, '200101',
                error_type='Non-Planar Geometry')
            if detailed:  # add the out-of-plane points to helper_geometry
                help_pts = [
                    p.to_dict() for p in self.geometry.non_planar_vertices(tolerance)
                ]
                full_msg[0]['helper_geometry'] = help_pts
            return full_msg
        return [] if detailed else ''

    def check_self_intersecting(self, tolerance=0.01, raise_exception=True,
                                detailed=False):
        """Check whether the edges of the Shape intersect one another (like a bowtie).

        Args:
            tolerance: The minimum difference between the coordinate values of two
                vertices at which they can be considered equivalent. Default: 0.01,
                suitable for objects in meters.
            raise_exception: If True, a ValueError will be raised if the object
                intersects with itself. Default: True.
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        if self.geometry.is_self_intersecting:
            msg = 'Shape "{}" has self-intersecting edges.'.format(self.full_id)
            try:  # see if it is self-intersecting because of a duplicate vertex
                new_geo = self.geometry.remove_duplicate_vertices(tolerance)
                if not new_geo.is_self_intersecting:
                    return [] if detailed else ''  # valid with removed dup vertex
            except AssertionError:
                return [] if detailed else ''  # degenerate geometry
            full_msg = self._validation_message(
                msg, raise_exception, detailed, '200102',
                error_type='Self-Intersecting Geometry')
            if detailed:  # add the self-intersection points to helper_geometry
                help_pts = [p.to_dict() for p in self.geometry.self_intersection_points]
                full_msg[0]['helper_geometry'] = help_pts
            return full_msg
        return [] if detailed else ''

    def to_dict(self, abridged=False, included_prop=None, include_plane=True):
        """Return Shape as a dictionary.

        Args:
            abridged: Boolean to note whether the extension properties of the
                object (ie. THERM materials) should be included in detail (False)
                or just referenced by identifier (True). (Default: False).
            included_prop: List of properties to filter keys that must be included in
                output dictionary. For example ['therm'] will include 'therm' key if
                available in properties to_dict. By default all the keys will be
                included. To exclude all the keys from extensions use an empty list.
            include_plane: Boolean to note wether the plane of the Face3D should be
                included in the output. This can preserve the orientation of the
                X/Y axes of the plane but is not required and can be removed to
                keep the dictionary smaller. (Default: True).
        """
        base = {'type': 'Shape'}
        base['identifier'] = self.identifier
        base['geometry'] = self._geometry.to_dict(include_plane)
        base['properties'] = self.properties.to_dict(abridged, included_prop)
        if self._display_name is not None:
            base['display_name'] = self.display_name
        if self.user_data is not None:
            base['user_data'] = self.user_data
        return base

    @property
    def to(self):
        """Shape writer object.

        Use this method to access Writer class to write the shape in different formats.

        Usage:

        .. code-block:: python

            shape.to.therm(shape) -> therm XML element
        """
        return writer

    def __copy__(self):
        new_shape = Shape(self.geometry, self.identifier)
        new_shape._display_name = self._display_name
        new_shape._user_data = None if self.user_data is None else self.user_data.copy()
        new_shape._properties._duplicate_extension_attr(self._properties)
        return new_shape

    def __repr__(self):
        return 'Shape: %s' % self.display_name
