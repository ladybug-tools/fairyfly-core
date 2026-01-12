# coding=utf-8
"""Module for coloring geometry with attributes."""
from __future__ import division

from .shape import Shape
from .boundary import Boundary
from .search import get_attr_nested

from ladybug.graphic import GraphicContainer
from ladybug.legend import LegendParameters, LegendParametersCategorized
from ladybug_geometry.geometry3d.pointvector import Point3D


class _ColorObject(object):
    """Base class for visualization objects.

    Properties:
        * legend_parameters
        * attr_name
        * attr_name_end
        * attributes
        * attributes_unique
        * attributes_original
        * min_point
        * max_point
        * graphic_container
    """
    __slots__ = ('_attr_name', '_legend_parameters', '_attr_name_end',
                 '_attributes', '_attributes_unique', '_attributes_original',
                 '_min_point', '_max_point')

    def __init__(self, legend_parameters=None):
        """Initialize ColorObject."""
        # assign the legend parameters of this object
        self.legend_parameters = legend_parameters

        self._attr_name = None
        self._attr_name_end = None
        self._attributes = None
        self._attributes_unique = None
        self._attributes_original = None
        self._min_point = None
        self._max_point = None

    @property
    def legend_parameters(self):
        """Get or set the legend parameters."""
        return self._legend_parameters

    @legend_parameters.setter
    def legend_parameters(self, value):
        if value is not None:
            assert isinstance(value, LegendParameters) and not \
                isinstance(value, LegendParametersCategorized), \
                'Expected LegendParameters. Got {}.'.format(type(value))
            self._legend_parameters = value
        else:
            self._legend_parameters = LegendParameters()

    @property
    def attr_name(self):
        """Get a text string of an attribute that the input objects should have."""
        return self._attr_name

    @property
    def attr_name_end(self):
        """Get text for the last attribute in the attr_name.

        Useful when attr_name is nested.
        """
        return self._attr_name_end

    @property
    def attributes(self):
        """Get a tuple of text for the attributes assigned to the objects.

        If the input attr_name is a valid attribute for the object but None is
        assigned, the output will be 'None'. If the input attr_name is not valid
        for the input object, 'N/A' will be returned.
        """
        return self._attributes

    @property
    def attributes_unique(self):
        """Get a tuple of text for the unique attributes assigned to the objects."""
        return self._attributes_unique

    @property
    def attributes_original(self):
        """Get a tuple of objects for the attributes assigned to the objects.

        These will follow the original object typing of the attribute and won't
        be strings like the attributes.
        """
        return self._attributes_original

    @property
    def min_point(self):
        """Get a Point3D for the minimum of the box around the objects."""
        return self._min_point

    @property
    def max_point(self):
        """Get a Point3D for the maximum of the box around the objects."""
        return self._max_point

    @property
    def graphic_container(self):
        """Get a ladybug GraphicContainer that relates to this object.

        The GraphicContainer possesses almost all things needed to visualize the
        ColorShapes object including the legend, value_colors, etc.
        """
        # produce a range of values from the collected attributes
        attr_dict = {i: val for i, val in enumerate(self.attributes_unique)}
        attr_dict_rev = {val: i for i, val in attr_dict.items()}
        try:
            values = tuple(attr_dict_rev[r_attr] for r_attr in self.attributes)
        except KeyError:  # possibly caused by float cast to -0.0
            values = []
            for r_attr in self.attributes:
                if r_attr == '-0.0':
                    values.append(attr_dict_rev['0.0'])
                else:
                    values.append(attr_dict_rev[r_attr])

        # produce legend parameters with an ordinal dict for the attributes
        l_par = self.legend_parameters.duplicate()
        if l_par.is_segment_count_default:
            l_par.segment_count = len(self.attributes_unique)
        l_par.ordinal_dictionary = attr_dict
        if l_par.is_title_default:
            l_par.title = self.attr_name_end.replace('_', ' ').title()

        return GraphicContainer(values, self.min_point, self.max_point, l_par)

    def _process_attribute_name(self, attr_name):
        """Process the attribute name and assign it to this object."""
        self._attr_name = str(attr_name)
        at_split = self._attr_name.split('.')
        if len(at_split) == 1:
            self._attr_name_end = at_split[-1]
        elif at_split[-1] == 'display_name':
            self._attr_name_end = at_split[-2]
        elif at_split[-1] == '__name__' and at_split[-2] == '__class__':
            self._attr_name_end = at_split[-3]
        else:
            self._attr_name_end = at_split[-1]

    def _process_attributes(self, hb_objs):
        """Process the attributes of fairyfly objects."""
        nd = self.legend_parameters.decimal_count
        attributes = [get_attr_nested(obj, self._attr_name, nd) for obj in hb_objs]
        attributes_unique = set(attributes)
        float_attr = [atr for atr in attributes_unique if isinstance(atr, float)]
        str_attr = [atr for atr in attributes_unique if isinstance(atr, str)]
        float_attr.sort()
        str_attr.sort()
        self._attributes = tuple(str(val) for val in attributes)
        self._attributes_unique = tuple(str_attr) + tuple(str(val) for val in float_attr)
        self._attributes_original = \
            tuple(get_attr_nested(obj, self._attr_name, cast_to_str=False)
                  for obj in hb_objs)

    def _calculate_min_max(self, hb_objs):
        """Calculate maximum and minimum Point3D for a set of shapes."""
        st_rm_min, st_rm_max = hb_objs[0].geometry.min, hb_objs[0].geometry.max
        min_pt = [st_rm_min.x, st_rm_min.y, st_rm_min.z]
        max_pt = [st_rm_max.x, st_rm_max.y, st_rm_max.z]

        for shape in hb_objs[1:]:
            rm_min, rm_max = shape.geometry.min, shape.geometry.max
            if rm_min.x < min_pt[0]:
                min_pt[0] = rm_min.x
            if rm_min.y < min_pt[1]:
                min_pt[1] = rm_min.y
            if rm_min.z < min_pt[2]:
                min_pt[2] = rm_min.z
            if rm_max.x > max_pt[0]:
                max_pt[0] = rm_max.x
            if rm_max.y > max_pt[1]:
                max_pt[1] = rm_max.y
            if rm_max.z > max_pt[2]:
                max_pt[2] = rm_max.z

        self._min_point = Point3D(min_pt[0], min_pt[1], min_pt[2])
        self._max_point = Point3D(max_pt[0], max_pt[1], max_pt[2])

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()


class ColorShape(_ColorObject):
    """Object for visualizing shape attributes.

    Args:
        shapes: An array of fairyfly Shapes, which will be colored with the attribute.
        attr_name: A text string of an attribute that the input shapes should have.
            This can have '.' that separate the nested attributes from one another.
            For example, 'properties.therm.materials'.
        legend_parameters: An optional LegendParameter object to change the display
            of the ColorShape (Default: None).

    Properties:
        * shapes
        * attr_name
        * legend_parameters
        * attr_name_end
        * attributes
        * attributes_unique
        * attributes_original
        * geometry
        * graphic_container
        * min_point
        * max_point
    """
    __slots__ = ('_shapes',)

    def __init__(self, shapes, attr_name, legend_parameters=None):
        """Initialize ColorShape."""
        try:  # check the input shapes
            shapes = tuple(shapes)
        except TypeError:
            raise TypeError('Input shapes must be an array. Got {}.'.format(type(shapes)))
        assert len(shapes) > 0, 'ColorShapes must have at least one shape.'
        for shape in shapes:
            assert isinstance(shape, Shape), 'Expected fairyfly Shape for ' \
                'ColorShape shapes. Got {}.'.format(type(shape))
        self._shapes = shapes
        self._calculate_min_max(shapes)

        # assign the legend parameters of this object
        self.legend_parameters = legend_parameters

        # get the attributes of the input shapes
        self._process_attribute_name(attr_name)
        self._process_attributes(shapes)

    @property
    def shapes(self):
        """Get a tuple of fairyfly Shapes assigned to this object."""
        return self._shapes

    @property
    def geometry(self):
        """Get a nested array with each sub-array having the Face3D of each shape."""
        return [s.geometry for s in self.shapes]

    def __repr__(self):
        """Color Shape representation."""
        return 'Color Shape:\n{} Shapes\n{}'.format(len(self.shapes), self.attr_name_end)


class ColorBoundary(_ColorObject):
    """Object for visualizing boundary attributes.

    Args:
        boundaries: An array of fairyfly Boundaries which will be colored with
            their attributes.
        attr_name: A text string of an attribute that the input faces should have.
            This can have '.' that separate the nested attributes from one another.
            For example, 'properties.therm.condition.temperature'.
        legend_parameters: An optional LegendParameter object to change the display
            of the ColorBoundary (Default: None).

    Properties:
        * boundaries
        * attr_name
        * legend_parameters
        * attr_name_end
        * attributes_unique
        * attributes
        * attributes_original
        * flat_geometry
        * graphic_container
        * min_point
        * max_point
    """
    __slots__ = ('_boundaries',)

    def __init__(self, boundaries, attr_name, legend_parameters=None):
        """Initialize ColorBoundary."""
        try:  # check the input boundaries
            boundaries = tuple(boundaries)
        except TypeError:
            raise TypeError(
                'Input boundaries must be an array. Got {}.'.format(type(boundaries)))
        assert len(boundaries) > 0, 'ColorBoundary must have at least one boundary.'
        for bound in boundaries:
            assert isinstance(bound, Boundary), 'Expected fairyfly Boundary for ' \
                'ColorBoundary. Got {}.'.format(type(bound))
        self._boundaries = boundaries
        self._calculate_min_max(boundaries)

        # assign the legend parameters of this object
        self.legend_parameters = legend_parameters

        # get the attributes of the input faces
        self._process_attribute_name(attr_name)
        self._process_attributes(boundaries)

    @property
    def boundaries(self):
        """Get the fairyfly Boundaries assigned to this object.
        """
        return self._boundaries

    @property
    def attributes(self):
        """Get a tuple of text for the attributes assigned to the objects.

        If the input attr_name is a valid attribute for the object but None is
        assigned, the output will be 'None'. If the input attr_name is not valid
        for the input object, 'N/A' will be returned.
        """
        flat_attr = []
        for bnd, attrib in zip(self._boundaries, self._attributes):
            flat_attr.extend([attrib] * len(bnd))
        return flat_attr

    @property
    def attributes_original(self):
        """Get a tuple of objects for the attributes assigned to the objects.

        These will follow the original object typing of the attribute and won't
        be strings like the attributes.
        """
        flat_attr = []
        for bnd, attrib in zip(self._boundaries, self._attributes_original):
            flat_attr.extend([attrib] * len(bnd))
        return flat_attr

    @property
    def flat_geometry(self):
        """Get an array of LineSegment3D on this object.

        The geometries here align with the attributes and graphic_container colors.
        """
        return [lin for bound in self._boundaries for lin in bound]

    def __repr__(self):
        """Color Shape representation."""
        return 'Color Boundary:\n{} Boundary\n{}'.format(
            len(self.boundaries), self.attr_name_end)
