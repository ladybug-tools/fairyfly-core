"""Test the Shape class."""
import pytest
import uuid
from ladybug_geometry.geometry3d import Point3D, Vector3D, Plane, Face3D
from fairyfly.shape import Shape


def test_shape_init():
    """Test the initialization of Shape objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shape = Shape(Face3D(pts))
    shape.display_name = 'TestShape'
    str(shape)  # test the string representation

    assert uuid.UUID(shape.identifier)
    assert shape.display_name == 'TestShape'
    assert isinstance(shape.geometry, Face3D)
    assert len(shape.vertices) == 4
    assert shape.normal == Vector3D(0, 1, 0)
    assert shape.center == Point3D(0.5, 0, 1.5)
    assert shape.area == 3
    assert shape.perimeter == 8
    assert round(shape.altitude, 3) == 0
    assert round(shape.azimuth, 3) == 0
    assert isinstance(shape.min, Point3D)
    assert isinstance(shape.max, Point3D)
    assert not shape.has_parent


def test_shape_from_vertices():
    """Test the initialization of shape objects from vertices."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shape = Shape.from_vertices(pts)
    shape.display_name = 'TestShape'

    assert uuid.UUID(shape.identifier)
    assert shape.display_name == 'TestShape'
    assert isinstance(shape.geometry, Face3D)
    assert len(shape.vertices) == 4
    assert shape.normal == Vector3D(0, 1, 0)
    assert shape.center == Point3D(0.5, 0, 1.5)
    assert shape.area == 3
    assert shape.perimeter == 8
    assert not shape.has_parent


def test_shape_duplicate():
    """Test the duplication of shape objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shp_1 = Shape(Face3D(pts))
    shp_1.display_name = 'TestShape'
    shp_2 = shp_1.duplicate()

    assert shp_1 is not shp_2
    for i, pt in enumerate(shp_1.vertices):
        assert pt == shp_2.vertices[i]
    assert shp_1.identifier == shp_2.identifier

    shp_2.move(Vector3D(0, 1, 0))
    for i, pt in enumerate(shp_1.vertices):
        assert pt != shp_2.vertices[i]


def test_move():
    """Test the shape move method."""
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 0))
    shape = Shape(Face3D(pts_1, plane_1))

    vec_1 = Vector3D(2, 2, 2)
    new_shp = shape.duplicate()
    new_shp.move(vec_1)
    assert new_shp.geometry[0] == Point3D(2, 2, 2)
    assert new_shp.geometry[1] == Point3D(4, 2, 2)
    assert new_shp.geometry[2] == Point3D(4, 4, 2)
    assert new_shp.geometry[3] == Point3D(2, 4, 2)
    assert new_shp.normal == shape.normal
    assert shape.area == new_shp.area
    assert shape.perimeter == new_shp.perimeter


def test_scale():
    """Test the shape scale method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shape = Shape(Face3D(pts, plane))

    new_shp = shape.duplicate()
    new_shp.scale(2)
    assert new_shp.geometry[0] == Point3D(2, 2, 4)
    assert new_shp.geometry[1] == Point3D(4, 2, 4)
    assert new_shp.geometry[2] == Point3D(4, 4, 4)
    assert new_shp.geometry[3] == Point3D(2, 4, 4)
    assert new_shp.area == shape.area * 2 ** 2
    assert new_shp.perimeter == shape.perimeter * 2
    assert new_shp.normal == shape.normal


def test_rotate():
    """Test the shape rotate method."""
    pts = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shape = Shape(Face3D(pts, plane))
    origin = Point3D(0, 0, 0)
    axis = Vector3D(1, 0, 0)

    test_1 = shape.duplicate()
    test_1.rotate(axis, 180, origin)
    assert test_1.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(-2, rel=1e-3)
    assert shape.area == test_1.area
    assert len(shape.vertices) == len(test_1.vertices)

    test_2 = shape.duplicate()
    test_2.rotate(axis, 90, origin)
    assert test_2.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[0].y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[0].z == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[2].z == pytest.approx(2, rel=1e-3)
    assert shape.area == test_2.area
    assert len(shape.vertices) == len(test_2.vertices)


def test_rotate_xy():
    """Test the Shape rotate_xy method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shape = Shape(Face3D(pts, plane))
    origin_1 = Point3D(1, 1, 0)

    test_1 = shape.duplicate()
    test_1.rotate_xy(180, origin_1)
    assert test_1.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[2].y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(2, rel=1e-3)

    test_2 = shape.duplicate()
    test_2.rotate_xy(90, origin_1)
    assert test_2.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert test_2.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[2].y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(2, rel=1e-3)


def test_reflect():
    """Test the Shape reflect method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shape = Shape(Face3D(pts, plane))

    origin_1 = Point3D(1, 0, 2)
    origin_2 = Point3D(0, 0, 2)
    normal_1 = Vector3D(1, 0, 0)
    normal_2 = Vector3D(-1, -1, 0).normalize()
    plane_1 = Plane(normal_1, origin_1)
    plane_2 = Plane(normal_2, origin_2)
    plane_3 = Plane(normal_2, origin_1)

    test_1 = shape.duplicate()
    test_1.reflect(plane_1)
    assert test_1.geometry[-1].x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[-1].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[1].y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].z == pytest.approx(2, rel=1e-3)

    test_1 = shape.duplicate()
    test_1.reflect(plane_2)
    assert test_1.geometry[-1].x == pytest.approx(-1, rel=1e-3)
    assert test_1.geometry[-1].y == pytest.approx(-1, rel=1e-3)
    assert test_1.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].x == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].z == pytest.approx(2, rel=1e-3)

    test_2 = shape.duplicate()
    test_2.reflect(plane_3)
    assert test_2.geometry[-1].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[-1].y == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[1].x == pytest.approx(-1, rel=1e-3)
    assert test_2.geometry[1].y == pytest.approx(-1, rel=1e-3)
    assert test_2.geometry[1].z == pytest.approx(2, rel=1e-3)


def test_remove_colinear_vertices():
    """Test the remove_colinear_vertices method."""
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2), Point3D(0, 2))
    pts_2 = (Point3D(0, 0), Point3D(1, 0), Point3D(2, 0), Point3D(2, 2),
             Point3D(0, 2))
    shape_1 = Shape(Face3D(pts_1))
    shape_2 = Shape(Face3D(pts_2))

    assert len(shape_1.geometry.vertices) == 4
    assert len(shape_2.geometry.vertices) == 5
    shape_1.remove_colinear_vertices(0.0001)
    shape_2.remove_colinear_vertices(0.0001)
    assert len(shape_1.geometry.vertices) == 4
    assert len(shape_2.geometry.vertices) == 4


def test_check_planar():
    """Test the check_planar method."""
    pts_1 = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    pts_2 = (Point3D(0, 0, 0), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    pts_3 = (Point3D(0, 0, 2.0001), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shape_1 = Shape(Face3D(pts_1, plane_1))
    shape_2 = Shape(Face3D(pts_2, plane_1))
    shape_3 = Shape(Face3D(pts_3, plane_1))

    assert shape_1.check_planar(0.001) == ''
    assert shape_2.check_planar(0.001, False) != ''
    with pytest.raises(Exception):
        shape_2.check_planar(0.0001)
    assert shape_3.check_planar(0.001) == ''
    assert shape_3.check_planar(0.000001, False) != ''
    with pytest.raises(Exception):
        shape_3.check_planar(0.000001)


def test_check_self_intersecting():
    """Test the check_self_intersecting method."""
    plane_1 = Plane(Vector3D(0, 0, 1))
    plane_2 = Plane(Vector3D(0, 0, -1))
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2), Point3D(0, 2))
    pts_2 = (Point3D(0, 0), Point3D(0, 2), Point3D(2, 0), Point3D(2, 2))
    shape_1 = Shape(Face3D(pts_1, plane_1))
    shape_2 = Shape(Face3D(pts_2, plane_1))
    shape_3 = Shape(Face3D(pts_1, plane_2))
    shape_4 = Shape(Face3D(pts_2, plane_2))

    assert shape_1.check_self_intersecting(0.01, False) == ''
    assert shape_2.check_self_intersecting(0.01, False) != ''
    with pytest.raises(Exception):
        assert shape_2.check_self_intersecting(0.01, True)
    assert shape_3.check_self_intersecting(0.01, False) == ''
    assert shape_4.check_self_intersecting(0.01, False) != ''
    with pytest.raises(Exception):
        assert shape_4.check_self_intersecting(0.01, True)


def test_to_dict():
    """Test the shape to_dict method."""
    vertices = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    shp = Shape.from_vertices(vertices)
    shp.display_name = 'RectangleShape'

    shp = shp.to_dict()
    assert shp['type'] == 'Shape'
    assert uuid.UUID(shp['identifier'])
    assert shp['display_name'] == 'RectangleShape'
    assert 'geometry' in shp
    assert len(shp['geometry']['boundary']) == len(vertices)
    assert 'properties' in shp
    assert shp['properties']['type'] == 'ShapeProperties'


def test_to_from_dict():
    """Test the to/from dict of Shape objects."""
    vertices = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    shp = Shape.from_vertices(vertices)
    shp.display_name = 'RectangleShape'

    shp_dict = shp.to_dict()
    new_shp = Shape.from_dict(shp_dict)
    assert isinstance(new_shp, Shape)
    assert new_shp.to_dict() == shp_dict


def test_writer():
    """Test the Shape writer object."""
    vertices = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    shp = Shape.from_vertices(vertices)

    writers = [mod for mod in dir(shp.to) if not mod.startswith('_')]
    for writer in writers:
        assert callable(getattr(shp.to, writer))
