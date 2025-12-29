# coding: utf-8
"""A series of utility functions that are useful across several fairyfly extensions."""
from __future__ import division


def model_extension_dicts(data, extension_key, shape_ext_dicts, boundary_ext_dicts):
    """Get all Model property dictionaries of an extension organized by geometry type.

    Note that the order in which dictionaries appear in the output lists is the
    same order as the geometry objects appear when requested from the model.
    For example, the shape_ext_dicts align with the model.shapes.

    Args:
        data: A dictionary representation of an entire fairyfly-core Model.
        extension_key: Text for the key of the extension (eg. "therm").

    Returns:
        A tuple with two elements

        -   shape_ext_dicts: A list of Shape extension property dictionaries that
            align with the serialized model.shapes.

        -   boundary_ext_dicts: A list of Boundary extension property dictionaries that
            align with the serialized model.boundaries.
    """
    assert data['type'] == 'Model', \
        'Expected Model dictionary. Got {}.'.format(data['type'])
    # loop through the model dictionary using the same logic that the
    # model does when you request shapes and boundaries.
    if 'shapes' in data:
        shape_extension_dicts(data['shapes'], extension_key, shape_ext_dicts)
    if 'boundaries' in data:
        boundary_extension_dicts(data['boundaries'], extension_key, boundary_ext_dicts)
    return shape_ext_dicts, boundary_ext_dicts


def shape_extension_dicts(shape_list, extension_key, shape_ext_dicts):
    """Get all Shape property dictionaries of an extension.

    Args:
        shape_list: A list of Shape dictionaries.
        extension_key: Text for the key of the extension (eg. "therm").

    Returns:
        shape_ext_dicts -- A list with Shape extension property dictionaries.
    """
    for shp_dict in shape_list:
        try:
            shape_ext_dicts.append(shp_dict['properties'][extension_key])
        except KeyError:
            shape_ext_dicts.append(None)
    return shape_ext_dicts


def boundary_extension_dicts(boundary_list, extension_key, boundary_ext_dicts):
    """Get all Boundary property dictionaries of an extension.

    Args:
        shape_list: A list of Boundary dictionaries.
        extension_key: Text for the key of the extension (eg. "therm").

    Returns:
        boundary_ext_dicts -- A list with Boundary extension property dictionaries.
    """
    for bnd_dict in boundary_list:
        try:
            boundary_ext_dicts.append(bnd_dict['properties'][extension_key])
        except KeyError:
            boundary_ext_dicts.append(None)
    return boundary_ext_dicts
