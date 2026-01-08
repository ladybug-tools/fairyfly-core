# coding=utf-8
"""Utilities to convert any dictionary to Python objects.

Note that importing this module will import almost all modules within the
library in order to be able to re-serialize almost any dictionary produced
from the library.
"""
from fairyfly.model import Model
from fairyfly.shape import Shape
from fairyfly.boundary import Boundary


def dict_to_object(fairyfly_dict, raise_exception=True):
    """Re-serialize a dictionary of almost any object within fairyfly.

    This includes any Model, Shape or Boundary object.

    Args:
        fairyfly_dict: A dictionary of any Fairyfly object. Note
            that this should be a non-abridged dictionary to be valid.
        raise_exception: Boolean to note whether an exception should be raised
            if the object is not identified as a part of fairyfly.
            Default: True.

    Returns:
        A Python object derived from the input fairyfly_dict.
    """
    try:  # get the type key from the dictionary
        obj_type = fairyfly_dict['type']
    except KeyError:
        raise ValueError('Fairyfly dictionary lacks required "type" key.')

    if obj_type == 'Model':
        return Model.from_dict(fairyfly_dict)
    elif obj_type == 'Shape':
        return Shape.from_dict(fairyfly_dict)
    elif obj_type == 'Boundary':
        return Boundary.from_dict(fairyfly_dict)
    elif raise_exception:
        raise ValueError('{} is not a recognized fairyfly object'.format(obj_type))
