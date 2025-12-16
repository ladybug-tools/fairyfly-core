"""Collection of methods for type input checking."""
import uuid
import math

try:
    INFPOS = math.inf
    INFNEG = -1 * math.inf
except AttributeError:
    # python 2
    INFPOS = float('inf')
    INFNEG = float('-inf')


def valid_uuid(value, input_name=''):
    """Check that a string is a UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.

    Note that this is slightly different than the UUIDs used in THERM, which
    have 4 fewer values for a 8-4-4-12 structure instead of a 8-4-4-4-12
    structure. The therm_id_from_uuid method can be used to convert an input here
    into a format acceptable for THERM.
    """
    try:
        value = str(value)
    except TypeError:
        raise TypeError('Input {} must be a text string. Got {}: {}.'.format(
            input_name, type(value), value))
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValueError(
            'Input {} must be formatted as a 8-4-4-4-12 UUID. '
            'Got: {}.'.format(input_name, value))


def therm_id_from_uuid(value):
    """Convert a valid_uuid into a format that THERM will accept."""
    hex_id = value.replace('-', '')
    return '{}-{}-{}-{}'.format(hex_id[:8], hex_id[8:12], hex_id[12:16], hex_id[16:28])


def _number_check(value, input_name):
    """Check if value is a number."""
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise TypeError('Input {} must be a number. Got {}: {}.'.format(
            input_name, type(value), value))
    return number


def float_in_range(value, mi=INFNEG, ma=INFPOS, input_name=''):
    """Check a float value to be between minimum and maximum."""
    number = _number_check(value, input_name)
    assert mi <= number <= ma, 'Input number {} must be between {} and {}. ' \
        'Got {}'.format(input_name, mi, ma, value)
    return number


def float_in_range_excl(value, mi=INFNEG, ma=INFPOS, input_name=''):
    """Check a float value to be greater than minimum and less than maximum."""
    number = _number_check(value, input_name)
    assert mi < number < ma, 'Input number {} must be greater than {} ' \
        'and less than {}. Got {}'.format(input_name, mi, ma, value)
    return number


def float_in_range_excl_incl(value, mi=INFNEG, ma=INFPOS, input_name=''):
    """Check a float value to be greater than minimum and less than/equal to maximum."""
    number = _number_check(value, input_name)
    assert mi < number <= ma, 'Input number {} must be greater than {} and less than ' \
        'or equal to {}. Got {}'.format(input_name, mi, ma, value)
    return number


def float_in_range_incl_excl(value, mi=INFNEG, ma=INFPOS, input_name=''):
    """Check a float value to be greater than/equal to minimum and less than maximum."""
    number = _number_check(value, input_name)
    assert mi <= number < ma, 'Input number {} must be greater than or equal to {} ' \
        'and less than {}. Got {}'.format(input_name, mi, ma, value)
    return number


def int_in_range(value, mi=INFNEG, ma=INFPOS, input_name=''):
    """Check an integer value to be between minimum and maximum."""
    try:
        number = int(value)
    except ValueError:
        # try to convert to float and then digit if possible
        try:
            number = int(float(value))
        except (ValueError, TypeError):
            raise TypeError('Input {} must be an integer. Got {}: {}.'.format(
                input_name, type(value), value))
    except (ValueError, TypeError):
        raise TypeError('Input {} must be an integer. Got {}: {}.'.format(
            input_name, type(value), value))
    assert mi <= number <= ma, 'Input integer {} must be between {} and {}. ' \
        'Got {}.'.format(input_name, mi, ma, value)
    return number


def float_positive(value, input_name=''):
    """Check a float value to be positive."""
    return float_in_range(value, 0, INFPOS, input_name)


def int_positive(value, input_name=''):
    """Check if an integer value is positive."""
    return int_in_range(value, 0, INFPOS, input_name)


def tuple_with_length(value, length=3, item_type=float, input_name=''):
    """Try to create a tuple with a certain value."""
    try:
        value = tuple(item_type(v) for v in value)
    except (ValueError, TypeError):
        raise TypeError('Input {} must be a {}.'.format(
            input_name, item_type))
    assert len(value) == length, 'Input {} length must be {} not {}'.format(
        input_name, length, len(value))
    return value


def list_with_length(value, length=3, item_type=float, input_name=''):
    """Try to create a list with a certain value."""
    try:
        value = [item_type(v) for v in value]
    except (ValueError, TypeError):
        raise TypeError('Input {} must be a {}.'.format(
            input_name, item_type))
    assert len(value) == length, 'Input {} length must be {} not {}'.format(
        input_name, length, len(value))
    return value


def invalid_dict_error(invalid_dict, error):
    """Raise a ValueError for an invalid dictionary that failed to serialize.

    This error message will include the identifier (and display_name) if they are
    present within the invalid_dict, making it easier for ens users to find the
    invalid object within large objects like Models.

    Args:
        invalid_dict: A dictionary of an invalid honeybee object that failed
            to serialize.
        error:
    """
    obj_type = invalid_dict['type'].replace('Abridged', '') \
        if 'type' in invalid_dict else 'Honeybee Object'
    obj_id = invalid_dict['identifier'] if 'identifier' in invalid_dict else ''
    full_id = '{}[{}]'.format(invalid_dict['display_name'], obj_id) \
        if 'display_name' in invalid_dict else obj_id
    raise ValueError('{} "{}" is invalid:\n{}'.format(obj_type, full_id, error))
