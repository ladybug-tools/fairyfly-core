# coding: utf-8
"""Fairyfly Model."""
from __future__ import division
import os
import io
import json
try:  # check if we are in IronPython
    import cPickle as pickle
except ImportError:  # wea are in cPython
    import pickle

from ladybug_geometry.geometry3d import Vector3D, Point3D, LineSegment3D, Plane, Face3D

from ._base import _Base
from .units import conversion_factor_to_meters, UNITS, UNITS_TOLERANCES
from .checkdup import check_duplicate_identifiers, check_duplicate_identifiers_parent
from .properties import ModelProperties
from .shape import Shape
from .boundary import Boundary
from .typing import clean_string, float_positive, invalid_dict_error
from .config import folders
import fairyfly.writer.model as writer


class Model(_Base):
    """A collection of Shapes and Boundaries representing a model.

    Args:
        shapes: A list of Shape objects in the model.
        boundaries: A list of the Boundary objects in the model.
        units: Text for the units system in which the model geometry
            exists. Default: 'Millimeters'. Choose from the following:

            * Millimeters
            * Inches
            * Centimeters
            * Meters
            * Feet

        tolerance: The maximum difference between x, y, and z values at which
            vertices are considered equivalent. Zero indicates that no tolerance
            checks should be performed. None indicates that the tolerance will be
            set based on the units above, with the tolerance consistently being
            between 0.01 mm and 0.001 mm (roughly the tolerance implicit in
            THERM). (Default: None).
        angle_tolerance: The max angle difference in degrees that vertices are allowed
            to differ from one another in order to consider them colinear. Zero indicates
            that no angle tolerance checks should be performed. (Default: 1.0).

    Properties:
        * identifier
        * display_name
        * units
        * tolerance
        * angle_tolerance
        * shapes
        * boundaries
        * shape_area
        * boundary_length
        * min
        * max
        * center
        * user_data
    """
    __slots__ = (
        '_shapes', '_boundaries', '_units', '_tolerance', '_angle_tolerance'
    )

    # dictionary mapping validation error codes to a corresponding check function
    ERROR_MAP = {
        '200001': 'check_duplicate_identifiers',
        '200101': 'check_planar',
        '200102': 'check_self_intersecting',
        '200103': 'check_degenerate_shapes',
        '200201': 'check_all_in_same_plane'
    }
    UNITS = UNITS
    UNITS_TOLERANCES = UNITS_TOLERANCES

    def __init__(self, shapes=None, boundaries=None,
                 units='Millimeters', tolerance=None, angle_tolerance=1.0):
        """A collection of Shapes and Boundaries for an entire model."""
        _Base.__init__(self, None)  # process the identifier
        self.units = units
        self.tolerance = tolerance
        self.angle_tolerance = angle_tolerance

        self.shapes = shapes
        self.boundaries = boundaries
        self._properties = ModelProperties(self)

    @classmethod
    def from_dict(cls, data):
        """Initialize a Model from a dictionary.

        Args:
            data: A dictionary representation of a Model object.
        """
        # check the type of dictionary
        assert data['type'] == 'Model', 'Expected Model dictionary. ' \
            'Got {}.'.format(data['type'])

        # import the units and tolerance values
        units = 'Millimeters' if 'units' not in data or data['units'] is None \
            else data['units']
        tol = cls.UNITS_TOLERANCES[units] if 'tolerance' not in data or \
            data['tolerance'] is None else data['tolerance']
        angle_tol = 1.0 if 'angle_tolerance' not in data or \
            data['angle_tolerance'] is None else data['angle_tolerance']

        # import all of the geometry
        shapes = None  # import shapes
        if 'shapes' in data and data['shapes'] is not None:
            shapes = []
            for s in data['shapes']:
                try:
                    shapes.append(Shape.from_dict(s))
                except Exception as e:
                    invalid_dict_error(s, e)
        boundaries = None  # import boundaries
        if 'boundaries' in data and data['boundaries'] is not None:
            boundaries = []
            for b in data['boundaries']:
                try:
                    boundaries.append(Boundary.from_dict(b))
                except Exception as e:
                    invalid_dict_error(b, e)

        # build the model object
        model = Model(shapes, boundaries, units, tol, angle_tol)
        model.identifier = data['identifier']
        if 'display_name' in data and data['display_name'] is not None:
            model.display_name = data['display_name']
        if 'user_data' in data and data['user_data'] is not None:
            model.user_data = data['user_data']

        # assign extension properties to the model
        model.properties.apply_properties_from_dict(data)
        return model

    @classmethod
    def from_file(cls, hb_file):
        """Initialize a Model from a FFJSON or FFpkl file, auto-sensing the type.

        Args:
            hb_file: Path to either a FFJSON or FFpkl file.
        """
        # sense the file type from the first character to avoid maxing memory with JSON
        with io.open(hb_file, encoding='utf-8') as inf:
            first_char = inf.read(1)
            second_char = inf.read(1)
        is_json = True if first_char == '{' or second_char == '{' else False
        # load the file using either FFJSON pathway or FFpkl
        if is_json:
            return cls.from_ffjson(hb_file)
        return cls.from_ffpkl(hb_file)

    @classmethod
    def from_ffjson(cls, ffjson_file):
        """Initialize a Model from a FFJSON file.

        Args:
            ffjson_file: Path to FFJSON file.
        """
        assert os.path.isfile(ffjson_file), 'Failed to find %s' % ffjson_file
        with io.open(ffjson_file, encoding='utf-8') as inf:
            inf.read(1)
            second_char = inf.read(1)
        with io.open(ffjson_file, encoding='utf-8') as inf:
            if second_char == '{':
                inf.read(1)
            data = json.load(inf)
        return cls.from_dict(data)

    @classmethod
    def from_ffpkl(cls, ffpkl_file):
        """Initialize a Model from a FFpkl file.

        Args:
            ffpkl_file: Path to FFpkl file.
        """
        assert os.path.isfile(ffpkl_file), 'Failed to find %s' % ffpkl_file
        with open(ffpkl_file, 'rb') as inf:
            data = pickle.load(inf)
        return cls.from_dict(data)

    @classmethod
    def from_objects(cls, objects, units='Millimeters',
                     tolerance=None, angle_tolerance=1.0):
        """Initialize a Model from a list of any type of fairyfly-core geometry objects.

        Args:
            objects: A list of fairyfly Shapes and Boundaries.
            units: Text for the units system in which the model geometry
                exists. Default: 'Millimeters'. Choose from the following:

                * Millimeters
                * Inches
                * Centimeters
                * Meters
                * Feet

            tolerance: The maximum difference between x, y, and z values at which
                vertices are considered equivalent. Zero indicates that no tolerance
                checks should be performed. None indicates that the tolerance will be
                set based on the units above, with the tolerance consistently being
                between 0.01 mm and 0.001 mm (roughly the tolerance implicit in
                THERM). (Default: None).
            angle_tolerance: The max angle difference in degrees that vertices
                are allowed to differ from one another in order to consider them
                colinear. Zero indicates that no angle tolerance checks should be
                performed. (Default: 1.0).
        """
        shapes = []
        boundaries = []
        for obj in objects:
            if isinstance(obj, Shape):
                shapes.append(obj)
            elif isinstance(obj, Boundary):
                boundaries.append(obj)
            else:
                raise TypeError(
                    'Expected Shape or Boundary for Model. Got {}'.format(type(obj)))
        return cls(shapes, boundaries, units, tolerance, angle_tolerance)

    @classmethod
    def from_layers(cls, thicknesses, height=200, base_plane=None,
                    units='Millimeters', tolerance=None, angle_tolerance=1.0):
        """Initialize a Model from a list of any type of fairyfly-core geometry objects.

        Args:
            thicknesses: A list of numbers for the thicknesses of each layer in
                the construction. The first thickness is the outer-most layer
                and the second thickness is the inner-most layer.
            height: A number for the height of the construction in the Y dimension.
            base_plane: An optional Plane object to set the origin of the model.
                If None, the world XY plane will be used. (Default: None).
            units: Text for the units system in which the model geometry
                exists. Default: 'Millimeters'. Choose from the following:

                * Millimeters
                * Inches
                * Centimeters
                * Meters
                * Feet

            tolerance: The maximum difference between x, y, and z values at which
                vertices are considered equivalent. Zero indicates that no tolerance
                checks should be performed. None indicates that the tolerance will be
                set based on the units above, with the tolerance consistently being
                between 0.01 mm and 0.001 mm (roughly the tolerance implicit in
                THERM). (Default: None).
            angle_tolerance: The max angle difference in degrees that vertices
                are allowed to differ from one another in order to consider them
                colinear. Zero indicates that no angle tolerance checks should be
                performed. (Default: 1.0).
        """
        # get the base plane
        if base_plane is not None:
            assert isinstance(base_plane, Plane), \
                'base_plane must be Plane. Got {}.'.format(type(base_plane))
        else:
            base_plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 0))
        # create the shape and boundary objects
        outside = LineSegment3D(base_plane.o, base_plane.y * height)
        outside.display_name = 'Outdoors'
        shapes, boundaries = [], [outside]
        for i, base in enumerate(thicknesses):
            shp_geo = Face3D.from_rectangle(base, height, base_plane)
            base_plane = base_plane.move(base_plane.x * base)
            shape = Shape(shp_geo)
            shape.display_name = 'Layer {}'.format(i + 1)
        inside = LineSegment3D(base_plane.o, base_plane.y * height)
        inside.display_name = 'Indoors'
        # create the model object
        model = cls(shapes, boundaries, units=units, tolerance=tolerance,
                    angle_tolerance=angle_tolerance)
        model.display_name = 'Layered Construction'
        return model

    @property
    def units(self):
        """Get or set Text for the units system in which the model geometry exists."""
        return self._units

    @units.setter
    def units(self, value):
        value = value.title()
        assert value in UNITS, '{} is not supported as a units system. ' \
            'Choose from the following: {}'.format(value, UNITS)
        self._units = value

    @property
    def tolerance(self):
        """Get or set a number for the max meaningful difference between x, y, z values.

        This value should be in the Model's units. Zero indicates cases
        where no tolerance checks should be performed.
        """
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value):
        self._tolerance = float_positive(value, 'model tolerance') if value is not None \
            else UNITS_TOLERANCES[self.units]

    @property
    def angle_tolerance(self):
        """Get or set a number for the max meaningful angle difference in degrees.

        Face3D normal vectors differing by this amount are not considered parallel
        and Face3D segments that differ from 180 by this amount are not considered
        colinear. Zero indicates cases where no angle_tolerance checks should be
        performed.
        """
        return self._angle_tolerance

    @angle_tolerance.setter
    def angle_tolerance(self, value):
        self._angle_tolerance = float_positive(value, 'model angle_tolerance')

    @property
    def shapes(self):
        """Get a tuple of all Shape objects in the model."""
        return tuple(self._shapes)

    @shapes.setter
    def shapes(self, value):
        self._shapes = []
        if value is not None:
            for shape in value:
                self.add_shape(shape)

    @property
    def boundaries(self):
        """Get a tuple of all Boundary objects in the model."""
        return tuple(self._shapes)

    @boundaries.setter
    def boundaries(self, value):
        self._boundaries = []
        if value is not None:
            for bound in value:
                self.add_boundary(bound)

    @property
    def min(self):
        """Get a Point3D for the min bounding box vertex in the world XY plane."""
        return self._calculate_min(self._all_objects())

    @property
    def max(self):
        """Get a Point3D for the max bounding box vertex in the world XY plane."""
        return self._calculate_max(self._all_objects())

    def add_model(self, other_model):
        """Add another Model object to this model."""
        assert isinstance(other_model, Model), \
            'Expected Model. Got {}.'.format(type(other_model))
        if self.units != other_model.units:
            other_model.convert_to_units(self.units)
        for shape in other_model._shapes:
            self._shapes.append(shape)
        for boundary in other_model._boundaries:
            self._boundaries.append(boundary)

    def add_shape(self, obj):
        """Add a Shape object to the model."""
        assert isinstance(obj, Shape), 'Expected Shape. Got {}.'.format(type(obj))
        assert not obj.has_parent, 'Shape "{}"" has a parent GlazingSystem. Add the ' \
            'GlazingSystem to the model instead of the Shape.'.format(obj.display_name)
        self._shapes.append(obj)

    def add_shapes(self, objs):
        """Add a list of Shape objects to the model."""
        for obj in objs:
            self.add_shape(obj)

    def add_boundary(self, obj):
        """Add a Boundary object to the model."""
        assert isinstance(obj, Boundary), 'Expected Boundary. Got {}.'.format(type(obj))
        assert not obj.has_parent, 'Boundary "{}"" has a parent GlazingSystem. Add the ' \
            'GlazingSystem to the model instead of the Boundary.'.format(obj.display_name)
        self._boundaries.append(obj)

    def add_boundaries(self, objs):
        """Add a list of Boundary objects to the model."""
        for obj in objs:
            self.add_boundary(obj)

    def remove_shapes(self, shape_ids=None):
        """Remove Shapes from the model.

        Args:
            shape_ids: An optional list of Shape identifiers to only remove
                certain shapes from the model. If None, all Shapes will be
                removed. (Default: None).
        """
        self._shapes = self._remove_by_ids(self.shapes, shape_ids)

    def remove_boundaries(self, boundary_ids=None):
        """Remove Boundaries from the model.

        Args:
            boundary_ids: An optional list of Boundary identifiers to only remove
                certain boundaries from the model. If None, all Boundaries will be
                removed. (Default: None).
        """
        self._boundaries = self._remove_by_ids(self.boundaries, boundary_ids)

    def shapes_by_identifier(self, identifiers):
        """Get a list of Shape objects in the model given the Shape identifiers."""
        shapes, missing_ids = [], []
        model_shapes = self._shapes
        for obj_id in identifiers:
            for shape in model_shapes:
                if shape.identifier == obj_id:
                    shapes.append(shape)
                    break
            else:
                missing_ids.append(obj_id)
        if len(missing_ids) != 0:
            all_objs = ' '.join(['"' + rid + '"' for rid in missing_ids])
            raise ValueError(
                'The following Shapes were not found in the model: {}'.format(all_objs)
            )
        return shapes

    def boundaries_by_identifier(self, identifiers):
        """Get a list of Face objects in the model given the Face identifiers."""
        boundaries, missing_ids = [], []
        model_boundaries = self.boundaries
        for obj_id in identifiers:
            for face in model_boundaries:
                if face.identifier == obj_id:
                    boundaries.append(face)
                    break
            else:
                missing_ids.append(obj_id)
        if len(missing_ids) != 0:
            all_objs = ' '.join(['"' + rid + '"' for rid in missing_ids])
            raise ValueError(
                'The following Boundaries were not found in the model: {}'.format(all_objs)
            )
        return boundaries

    def move(self, moving_vec):
        """Move this Model along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the Model.
        """
        for shape in self._shapes:
            shape.move(moving_vec)
        for boundary in self._boundaries:
            boundary.move(moving_vec)
        self.properties.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate this Model by a certain angle around an axis and origin.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for shape in self._shapes:
            shape.rotate(axis, angle, origin)
        for boundary in self._boundaries:
            boundary.rotate(axis, angle, origin)
        self.properties.rotate(axis, angle, origin)

    def rotate_xy(self, angle, origin):
        """Rotate this Model counterclockwise in the world XY plane by a certain angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for shape in self._shapes:
            shape.rotate_xy(angle, origin)
        for boundary in self._boundaries:
            boundary.rotate_xy(angle, origin)
        self.properties.rotate_xy(angle, origin)

    def reflect(self, plane):
        """Reflect this Model across a plane with the input normal vector and origin.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        for shape in self._shapes:
            shape.reflect(plane)
        for boundary in self._boundaries:
            boundary.reflect(plane)
        self.properties.reflect(plane)

    def scale(self, factor, origin=None):
        """Scale this Model by a factor from an origin point.

        Note that using this method does NOT scale the model tolerance and, if
        it is desired that this tolerance be scaled with the model geometry,
        it must be scaled separately.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        for shape in self._shapes:
            shape.scale(factor, origin)
        for boundary in self._boundaries:
            boundary.scale(factor, origin)
        self.properties.scale(factor, origin)

    def convert_to_units(self, units='Millimeters'):
        """Convert all of the geometry in this model to certain units.

        This involves scaling the geometry, scaling the Model tolerance, and
        changing the Model's units property.

        Args:
            units: Text for the units to which the Model geometry should be
                converted. Default: Millimeters. Choose from the following:

                * Millimeters
                * Inches
                * Centimeters
                * Meters
                * Feet
        """
        if self.units != units:
            scale_fac1 = conversion_factor_to_meters(self.units)
            scale_fac2 = conversion_factor_to_meters(units)
            scale_fac = scale_fac1 / scale_fac2
            self.scale(scale_fac)
            self.tolerance = self.tolerance * scale_fac
            self.units = units

    def reset_coordinate_system(self, new_origin=None):
        """Set the origin of the coordinate system in which the model exists.

        This is useful for resolving cases where the model geometry lies so
        far from the origin in its current coordinate system that it creates
        problems. For example, the float values of the coordinates are so
        high that floating point tolerance interferes with the proper
        representation of the model's details.

        Args:
            new_origin: A Point3D in the model's current coordinate system that
                will become the origin of the new coordinate system. If unspecified,
                the minimum of the bounding box around the model geometry will
                be used. (Default: None).
        """
        if new_origin is None:
            min_pt, max_pt = self.min, self.max
            new_origin = Point3D(min_pt.x, max_pt.y, max_pt.z)
        # move the geometry using a vector that is the inverse of the origin
        ref_vec = Vector3D(-new_origin.x, -new_origin.y, -new_origin.z)
        self.move(ref_vec)

    def remove_degenerate_geometry(self, tolerance=None):
        """Remove any degenerate geometry from the model.

        Degenerate geometry refers to any objects that evaluate to less than 3 vertices
        when duplicate and colinear vertices are removed at the tolerance.

        Args:
            tolerance: The minimum distance between a vertex and the boundary segments
                at which point the vertex is considered distinct. If None, the
                Model's tolerance will be used. (Default: None).
        """
        tolerance = self.tolerance if tolerance is None else tolerance
        i_to_remove = []
        for i, shape in enumerate(self._shapes):
            try:
                shape.remove_colinear_vertices(tolerance)
            except ValueError:  # degenerate shape found!
                i_to_remove.append(i)
        for i in reversed(i_to_remove):
            self._shapes.pop(i)

    def check_all(self, raise_exception=True, detailed=False, all_ext_checks=False):
        """Check all of the aspects of the Model for validation errors.

        This includes basic geometry checks. Furthermore, all extension attributes
        will be checked assuming the extension Model properties have a
        check_all function.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if any Model errors are found. If False, this method will simply
                return a text string with all errors that were found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).
            all_ext_checks: Boolean to note whether every single check that is
                available for all installed extensions should be run (True) or only
                generic checks that cover all except the most limiting of
                cases should be run (False). Examples of checks that are skipped
                include DOE2's lack of support for courtyards and floor plates
                with holes. (Default: False).

        Returns:
            A text string with all errors that were found or a list if detailed is True.
            This string (or list) will be empty if no errors were found.
        """
        # set up defaults to ensure the method runs correctly
        detailed = False if raise_exception else detailed
        msgs = []
        # check that a tolerance has been specified in the model
        assert self.tolerance != 0, \
            'Model must have a non-zero tolerance in order to perform geometry checks.'
        assert self.angle_tolerance != 0, \
            'Model must have a non-zero angle_tolerance to perform geometry checks.'
        tol = self.tolerance

        # perform checks for duplicate identifiers, which might mess with other checks
        msgs.append(self.check_all_duplicate_identifiers(False, detailed))

        # perform several checks for the fairyfly schema geometry rules
        msgs.append(self.check_planar(tol, False, detailed))
        msgs.append(self.check_self_intersecting(tol, False, detailed))

        # check the extension attributes
        ext_msgs = self._properties._check_all_extension_attr(detailed, all_ext_checks)
        if detailed:
            ext_msgs = [m for m in ext_msgs if isinstance(m, list)]
        msgs.extend(ext_msgs)

        # output a final report of errors or raise an exception
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_all_duplicate_identifiers(self, raise_exception=True, detailed=False):
        """Check that there are no duplicate identifiers for any geometry objects.

        This includes Shapes and Boundaries.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if any Model errors are found. If False, this method will simply
                return a text string with all errors that were found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A text string with all errors that were found or a list if detailed is True.
            This string (or list) will be empty if no errors were found.
        """
        # set up defaults to ensure the method runs correctly
        detailed = False if raise_exception else detailed
        msgs = []
        # perform checks for duplicate identifiers
        msgs.append(self.check_duplicate_shape_identifiers(False, detailed))
        msgs.append(self.check_duplicate_boundary_identifiers(False, detailed))
        # output a final report of errors or raise an exception
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_duplicate_shape_identifiers(self, raise_exception=True, detailed=False):
        """Check that there are no duplicate Shape identifiers in the model.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if duplicate identifiers are found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        return check_duplicate_identifiers(
            self._shapes, raise_exception, 'Shape', detailed, '200001', 'Core',
            'Duplicate Shape Identifier')

    def check_duplicate_boundary_identifiers(self, raise_exception=True, detailed=False):
        """Check that there are no duplicate Boundary identifiers in the model.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if duplicate identifiers are found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        return check_duplicate_identifiers_parent(
            self.boundaries, raise_exception, 'Boundary', detailed, '200002', 'Core',
            'Duplicate Boundary Identifier')

    def check_planar(self, tolerance=None, raise_exception=True, detailed=False):
        """Check that all of the Model's geometry components are planar.

        This includes all of the Model's Shapes and Boundaries.

        Args:
            tolerance: The minimum distance between a given vertex and a the
                object's plane at which the vertex is said to lie in the plane.
                If None, the Model tolerance will be used. (Default: None).
            raise_exception: Boolean to note whether an ValueError should be
                raised if a vertex does not lie within the object's plane.
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        tolerance = self.tolerance if tolerance is None else tolerance
        detailed = False if raise_exception else detailed
        msgs = []
        for shape in self.shapes:
            msgs.append(shape.check_planar(tolerance, False, detailed))
        for boundary in self.boundaries:
            msgs.append(boundary.check_planar(tolerance, False, detailed))
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_self_intersecting(self, tolerance=None, raise_exception=True,
                                detailed=False):
        """Check that no edges of the Model's geometry components self-intersect.

        This includes all of the Model's Shapes.

        Args:
            tolerance: The minimum difference between the coordinate values of two
                vertices at which they can be considered equivalent. If None, the
                Model tolerance will be used. (Default: None).
            raise_exception: If True, a ValueError will be raised if an object
                intersects with itself (like a bowtie). (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        tolerance = self.tolerance if tolerance is None else tolerance
        detailed = False if raise_exception else detailed
        msgs = []
        for bound in self.boundaries:
            msgs.append(bound.check_self_intersecting(tolerance, False, detailed))
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    @property
    def to(self):
        """Model writer object.

        Use this method to access Writer class to write the model in other formats.

        Usage:

        .. code-block:: python

            model.to.therm(model) -> Therm XML element.
            model.to.thmz(model) -> thmz file.
        """
        return writer

    def to_dict(self, included_prop=None, include_plane=True):
        """Return Model as a dictionary.

        Args:
            included_prop: List of properties to filter keys that must be included in
                output dictionary. For example ['therm'] will include 'therm' key if
                available in properties to_dict. By default all the keys will be
                included. To exclude all the keys from extensions use an empty list.
            include_plane: Boolean to note wether the planes of the Face3Ds should be
                included in the output. This can preserve the orientation of the
                X/Y axes of the planes but is not required and can be removed to
                keep the dictionary smaller. (Default: True).
        """
        # write all of the geometry objects and their properties
        base = {'type': 'Model'}
        base['identifier'] = self.identifier
        if self._display_name is not None:
            base['display_name'] = self.display_name
        base['units'] = self.units
        base['properties'] = self.properties.to_dict(included_prop)
        if self._shapes != []:
            base['shapes'] = [s.to_dict(True, included_prop, include_plane)
                              for s in self._shapes]
        if self._boundaries != []:
            base['boundaries'] = [b.to_dict(True, included_prop)
                                  for b in self._boundaries]
        if self.tolerance != 0:
            base['tolerance'] = self.tolerance
        if self.angle_tolerance != 0:
            base['angle_tolerance'] = self.angle_tolerance
        # write in the optional keys if they are not None
        if self.user_data is not None:
            base['user_data'] = self.user_data
        return base

    def to_ffjson(self, name=None, folder=None, indent=None, included_prop=None):
        """Write Fairyfly model to FFJSON.

        Args:
            name: A text string for the name of the FFJSON file. If None, the model
                identifier wil be used. (Default: None).
            folder: A text string for the directory where the FFJSON will be written.
                If unspecified, the default simulation folder will be used. This
                is usually at "C:\\Users\\USERNAME\\simulation."
            indent: A positive integer to set the indentation used in the resulting
                FFJSON file. (Default: None).
            included_prop: List of properties to filter keys that must be included in
                output dictionary. For example ['therm'] will include 'therm' key if
                available in properties to_dict. By default all the keys will be
                included. To exclude all the keys from extensions use an empty list.
        """
        # create dictionary from the Fairyfly Model
        hb_dict = self.to_dict(included_prop=included_prop)
        # set up a name and folder for the FFJSON
        if name is None:
            name = clean_string(self.display_name)
        file_name = name if name.lower().endswith('.ffjson') or \
            name.lower().endswith('.json') else '{}.ffjson'.format(name)
        folder = folder if folder is not None else folders.default_simulation_folder
        hb_file = os.path.join(folder, file_name)
        # write FFJSON
        with open(hb_file, 'w') as fp:
            json.dump(hb_dict, fp, indent=indent)
        return hb_file

    def to_ffpkl(self, name=None, folder=None, included_prop=None,
                 triangulate_sub_faces=False):
        """Write Fairyfly model to compressed pickle file (FFpkl).

        Args:
            name: A text string for the name of the pickle file. If None, the model
                identifier wil be used. (Default: None).
            folder: A text string for the directory where the pickle file will be
                written. If unspecified, the default simulation folder will be used.
                This is usually at "C:\\Users\\USERNAME\\simulation."
            included_prop: List of properties to filter keys that must be included in
                output dictionary. For example ['therm'] will include 'therm' key if
                available in properties to_dict. By default all the keys will be
                included. To exclude all the keys from extensions use an empty list.
        """
        # create dictionary from the Fairyfly Model
        hb_dict = self.to_dict(included_prop=included_prop)
        # set up a name and folder for the FFpkl
        if name is None:
            name = clean_string(self.display_name)
        file_name = name if name.lower().endswith('.ffpkl') or \
            name.lower().endswith('.pkl') else '{}.ffpkl'.format(name)
        folder = folder if folder is not None else folders.default_simulation_folder
        hb_file = os.path.join(folder, file_name)
        # write the Model dictionary into a file
        with open(hb_file, 'wb') as fp:
            pickle.dump(hb_dict, fp)
        return hb_file

    @staticmethod
    def validate(model, check_function='check_all', check_args=None, json_output=False):
        """Get a string of a validation report given a specific check_function.

        Args:
            model: A Fairyfly Model object for which validation will be performed.
                This can also be the file path to a FFJSON or a JSON string
                representation of a Fairyfly Model. These latter two options may
                be useful if the type of validation issue with the Model is
                one that prevents serialization.
            check_function: Text for the name of a check function on this Model
                that will be used to generate the validation report. For example,
                check_all or check_planar. (Default: check_all),
            check_args: An optional list of arguments to be passed to the
                check_function. If None, all default values for the arguments
                will be used. (Default: None).
            json_output: Boolean to note whether the output validation report
                should be formatted as a JSON object instead of plain text.
        """
        # process the input model if it's not already serialized
        report = ''
        if isinstance(model, str):
            try:
                if model.startswith('{'):
                    model = Model.from_dict(json.loads(model))
                elif os.path.isfile(model):
                    model = Model.from_file(model)
                else:
                    report = 'Input Model for validation is not a Model object, ' \
                        'file path to a Model or a Model FFJSON string.'
            except Exception as e:
                report = str(e)
        elif not isinstance(model, Model):
            report = 'Input Model for validation is not a Model object, ' \
                'file path to a Model or a Model FFJSON string.'

        if report == '':  # get the function to call to do checks
            if '.' in check_function:  # nested attribute
                attributes = check_function.split('.')  # get all the sub-attributes
                check_func = model
                for attribute in attributes:
                    if check_func is None:
                        continue
                    check_func = getattr(check_func, attribute, None)
            else:
                check_func = getattr(model, check_function, None)
            assert check_func is not None, \
                'Fairyfly Model class has no method {}'.format(check_function)
            # process the arguments and options
            args = [] if check_args is None else [] + list(check_args)
            kwargs = {'raise_exception': False}

        # create the report
        if not json_output:  # create a plain text report
            # add the versions of things into the validation message
            c_ver = folders.fairyfly_core_version_str
            ver_msg = 'Validating Model using fairyfly-core=={}'.format(c_ver)
            # run the check function
            if report == '':
                kwargs['detailed'] = False
                report = check_func(*args, **kwargs)
            # format the results of the check
            if report == '':
                full_msg = ver_msg + '\nCongratulations! Your Model is valid!'
            else:
                full_msg = ver_msg + \
                    '\nYour Model is invalid for the following reasons:\n' + report
            return full_msg
        else:
            # add the versions of things into the validation message
            out_dict = {
                'type': 'ValidationReport',
                'app_name': 'Fairyfly',
                'app_version': folders.fairyfly_core_version_str,
                'fatal_error': report
            }
            if report == '':
                kwargs['detailed'] = True
                errors = check_func(*args, **kwargs)
                out_dict['errors'] = errors
                out_dict['valid'] = True if len(out_dict['errors']) == 0 else False
            else:
                out_dict['errors'] = []
                out_dict['valid'] = False
            return json.dumps(out_dict, indent=4)

    @staticmethod
    def _remove_by_ids(objs, obj_ids):
        """Remove items from a list using a list of object IDs."""
        if obj_ids == []:
            return objs
        new_objs = []
        if obj_ids is not None:
            obj_id_set = set(obj_ids)
            for obj in objs:
                if obj.identifier not in obj_id_set:
                    new_objs.append(obj)
        return new_objs

    def __add__(self, other):
        new_model = self.duplicate()
        new_model.add_model(other)
        return new_model

    def __iadd__(self, other):
        self.add_model(other)
        return self

    def __copy__(self):
        new_model = Model(
            [shape.duplicate() for shape in self._shapes],
            [bound.duplicate() for bound in self._boundaries],
            self.units, self.tolerance, self.angle_tolerance)
        new_model._identifier = self._identifier
        new_model._display_name = self._display_name
        new_model._user_data = None if self.user_data is None else self.user_data.copy()
        new_model._properties._duplicate_extension_attr(self._properties)
        return new_model

    def __repr__(self):
        return 'Model: %s' % self.display_name
