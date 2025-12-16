"""Test the typing functions."""
import uuid

from fairyfly.typing import valid_uuid, therm_id_from_uuid, \
    float_in_range, int_in_range, float_positive, int_positive, \
    tuple_with_length, list_with_length, \
    float_in_range_excl, float_in_range_excl_incl, float_in_range_incl_excl, \
    invalid_dict_error

import pytest


def test_valid_uuid():
    """Test the valid_uuid method."""
    correct_str = 'c7f4015a-1e4e-4e1c-8b82-3f6bf4eabed4'
    incorrect_str = 'not-a-valid-uuid'

    assert valid_uuid(correct_str) == correct_str
    with pytest.raises(ValueError):
        valid_uuid(incorrect_str)

    assert therm_id_from_uuid(correct_str) == 'c7f4015a-1e4e-4e1c-8b823f6bf4ea'

    correct_uuid = str(uuid.uuid4())
    assert valid_uuid(correct_uuid) == correct_uuid


def test_float_in_range():
    """Test the float_in_range method."""
    assert isinstance(float_in_range(2.0, 0, 10, 'test number'), float)
    assert isinstance(float_in_range(2, 0, 10, 'test number'), float)
    assert isinstance(float_in_range('2', 0, 10, 'test number'), float)

    with pytest.raises(AssertionError):
        assert isinstance(float_in_range(2, 0, 1, 'test number'), float)
    with pytest.raises(TypeError):
        assert isinstance(float_in_range('two', 0, 10, 'test number'), float)
    with pytest.raises(TypeError):
        assert isinstance(float_in_range([2], 0, 10, 'test number'), float)

    try:
        float_in_range(2, 0, 1, 'test number')
    except AssertionError as e:
        assert 'test number' in str(e)


def test_float_in_range_excl():
    """Test the float_in_range_excl method."""
    assert isinstance(float_in_range_excl(1.0, 0, 10, 'test number'), float)
    assert isinstance(float_in_range_excl('1', 0, 10, 'test number'), float)

    with pytest.raises(AssertionError):
        assert isinstance(float_in_range_excl(0, 0, 10, 'test number'), float)
    with pytest.raises(AssertionError):
        assert isinstance(float_in_range_excl(10, 0, 10, 'test number'), float)

    try:
        float_in_range_excl(2, 0, 1, 'test number')
    except AssertionError as e:
        assert 'test number' in str(e)


def test_float_in_range_excl_incl():
    """Test the float_in_range_excl_incl method."""
    assert isinstance(float_in_range_excl_incl(1, 0, 10, 'test number'), float)
    assert isinstance(float_in_range_excl_incl(10, 0, 10, 'test number'), float)
    assert isinstance(float_in_range_excl_incl('1', 0, 10, 'test number'), float)

    with pytest.raises(AssertionError):
        assert isinstance(float_in_range_excl_incl(0, 0, 10, 'test number'), float)

    try:
        float_in_range_excl_incl(2, 0, 1, 'test number')
    except AssertionError as e:
        assert 'test number' in str(e)


def test_float_in_range_incl_excl():
    """Test the float_in_range_incl_excl method."""
    assert isinstance(float_in_range_incl_excl(1, 0, 10, 'test number'), float)
    assert isinstance(float_in_range_incl_excl(0, 0, 10, 'test number'), float)
    assert isinstance(float_in_range_incl_excl('1', 0, 10, 'test number'), float)

    with pytest.raises(AssertionError):
        assert isinstance(float_in_range_incl_excl(10, 0, 10, 'test number'), float)

    try:
        float_in_range_incl_excl(2, 0, 1, 'test number')
    except AssertionError as e:
        assert 'test number' in str(e)


def test_int_in_range():
    """Test the float_in_range method."""
    assert isinstance(int_in_range(2.0, 0, 10), int)
    assert isinstance(int_in_range(2, 0, 10), int)
    assert isinstance(int_in_range('2', 0, 10), int)

    with pytest.raises(AssertionError):
        assert isinstance(int_in_range(2, 0, 1), float)
    with pytest.raises(TypeError):
        assert isinstance(int_in_range('two', 0, 10), float)
    with pytest.raises(TypeError):
        assert isinstance(int_in_range([2], 0, 10), float)

    try:
        int_in_range(2, 0, 1, 'test number')
    except AssertionError as e:
        assert 'test number' in str(e)


def test_float_positive():
    """Test the float_positive method."""
    assert isinstance(float_positive(2.0), float)
    assert isinstance(float_positive(2), float)
    assert isinstance(float_positive('2'), float)

    with pytest.raises(AssertionError):
        assert isinstance(float_positive(-2), float)
    with pytest.raises(TypeError):
        assert isinstance(float_positive('two'), float)
    with pytest.raises(TypeError):
        assert isinstance(float_positive([2]), float)

    try:
        float_positive(-2, 'test number')
    except AssertionError as e:
        assert 'test number' in str(e)


def test_int_positive():
    """Test the int_positive method."""
    assert isinstance(int_positive(2.0), int)
    assert isinstance(int_positive(2), int)
    assert isinstance(int_positive('2'), int)

    with pytest.raises(AssertionError):
        assert isinstance(int_positive(-2), float)
    with pytest.raises(TypeError):
        assert isinstance(int_positive('two'), float)
    with pytest.raises(TypeError):
        assert isinstance(int_positive([2]), float)

    try:
        int_positive(-2, 'test number')
    except AssertionError as e:
        assert 'test number' in str(e)


def test_tuple_with_length():
    """Test the tuple_with_length method."""
    assert isinstance(tuple_with_length((1, 2, 3), 3, float, 'test tuple'), tuple)
    assert isinstance(tuple_with_length([1, 2, 3], 3, float, 'test tuple'), tuple)
    assert isinstance(tuple_with_length(range(3), 3, float, 'test tuple'), tuple)
    assert isinstance(tuple_with_length((1.0, 2.0, 3.0), 3, float, 'test tuple'), tuple)
    assert isinstance(tuple_with_length(('1', '2', '3'), 3, float, 'test tuple'), tuple)

    with pytest.raises(AssertionError):
        tuple_with_length((1, 2, 3), 4, float, 'test tuple')
    with pytest.raises(TypeError):
        tuple_with_length(('one', 'two', 'three'), 3, float, 'test tuple')

    try:
        tuple_with_length((1, 2, 3), 4, float, 'test tuple')
    except AssertionError as e:
        assert 'test tuple' in str(e)


def test_list_with_length():
    """Test the list_with_length method."""
    assert isinstance(list_with_length((1, 2, 3), 3, float, 'test list'), list)
    assert isinstance(list_with_length([1, 2, 3], 3, float, 'test list'), list)
    assert isinstance(list_with_length(range(3), 3, float, 'test list'), list)
    assert isinstance(list_with_length((1.0, 2.0, 3.0), 3, float, 'test list'), list)
    assert isinstance(list_with_length(('1', '2', '3'), 3, float, 'test list'), list)

    with pytest.raises(AssertionError):
        list_with_length((1, 2, 3), 4, float, 'test list')
    with pytest.raises(TypeError):
        list_with_length(('one', 'two', 'three'), 3, float, 'test list')

    try:
        list_with_length((1, 2, 3), 4, float, 'test list')
    except AssertionError as e:
        assert 'test list' in str(e)


def test_invalid_dict_error():
    """Test the invalid_dict_error method."""
    inv_dict = {
        'type': 'Construction',
        'identifier': 'no_heat_capacity_construction',
        'display_name': 'User-Created Construction'
    }
    error_msg = 'Construction does not contain sufficient heat capacity.'

    with pytest.raises(ValueError):
        invalid_dict_error(inv_dict, error_msg)
