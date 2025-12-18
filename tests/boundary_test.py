"""Test the Boundary class."""
import pytest
import uuid
from ladybug_geometry.geometry3d import Vector3D, Point3D, Plane, LineSegment3D
from fairyfly.boundary import Boundary


def test_boundary_init():
    """Test the initialization of Boundary objects."""
    line_1 = LineSegment3D.from_end_points(Point3D(0, 0, 0), Point3D(0, 0, 3))
    line_2 = LineSegment3D.from_end_points(Point3D(1, 0, 0), Point3D(1, 0, 3))
    boundary = Boundary((line_1, line_2))
    boundary.display_name = 'TestBoundary'
    str(boundary)  # test the string representation

    assert uuid.UUID(boundary.identifier)
    assert boundary.display_name == 'TestBoundary'
    assert isinstance(boundary.geometry, tuple)
    assert len(boundary.geometry) == 2
    for geo in boundary.geometry:
        assert isinstance(geo, LineSegment3D)
    assert boundary.center == Point3D(0.5, 0, 1.5)
    assert boundary.length == 6
    assert isinstance(boundary.min, Point3D)
    assert isinstance(boundary.max, Point3D)
    assert not boundary.has_parent


def test_boundary_from_vertices():
    """Test the initialization of boundary objects from vertices."""
    line_1 = ((0, 0, 0), (0, 0, 3))
    line_2 = ((1, 0, 0), (1, 0, 3))
    boundary = Boundary.from_vertices((line_1, line_2))
    boundary.display_name = 'TestBoundary'

    assert uuid.UUID(boundary.identifier)
    assert isinstance(boundary.geometry, tuple)
    assert len(boundary.geometry) == 2
    for geo in boundary.geometry:
        assert isinstance(geo, LineSegment3D)
    assert boundary.center == Point3D(0.5, 0, 1.5)
    assert boundary.length == 6
    assert isinstance(boundary.min, Point3D)
    assert isinstance(boundary.max, Point3D)
    assert not boundary.has_parent


def test_boundary_duplicate():
    """Test the duplication of boundary objects."""
    line_1 = LineSegment3D.from_end_points(Point3D(0, 0, 0), Point3D(0, 0, 3))
    line_2 = LineSegment3D.from_end_points(Point3D(1, 0, 0), Point3D(1, 0, 3))
    bnd_1 = Boundary((line_1, line_2))
    bnd_1.display_name = 'TestBoundary'
    bnd_2 = bnd_1.duplicate()

    assert bnd_1 is not bnd_2
    for i, pt in enumerate(bnd_1.vertices):
        assert pt == bnd_2.vertices[i]
    assert bnd_1.identifier == bnd_2.identifier

    bnd_2.move(Vector3D(0, 1, 0))
    for i, pt in enumerate(bnd_1.vertices):
        assert pt != bnd_2.vertices[i]


def test_move():
    """Test the boundary move method."""
    line_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0))
    line_2 = (Point3D(2, 2, 0), Point3D(0, 2, 0))
    boundary = Boundary.from_vertices((line_1, line_2))

    vec_1 = Vector3D(2, 2, 2)
    new_bnd = boundary.duplicate()
    new_bnd.move(vec_1)
    assert new_bnd.geometry[0].p1 == Point3D(2, 2, 2)
    assert new_bnd.geometry[0].p2 == Point3D(4, 2, 2)
    assert new_bnd.geometry[1].p1 == Point3D(4, 4, 2)
    assert new_bnd.geometry[1].p2 == Point3D(2, 4, 2)
    assert boundary.length == new_bnd.length


def test_scale():
    """Test the boundary scale method."""
    line_1 = (Point3D(1, 1, 2), Point3D(2, 1, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(1, 2, 2))
    boundary = Boundary.from_vertices((line_1, line_2))

    new_bnd = boundary.duplicate()
    new_bnd.scale(2)
    assert new_bnd.geometry[0].p1 == Point3D(2, 2, 4)
    assert new_bnd.geometry[0].p2 == Point3D(4, 2, 4)
    assert new_bnd.geometry[1].p1 == Point3D(4, 4, 4)
    assert new_bnd.geometry[1].p2 == Point3D(2, 4, 4)
    assert new_bnd.length == boundary.length * 2


def test_rotate():
    """Test the boundary rotate method."""
    line_1 = (Point3D(0, 0, 2), Point3D(2, 0, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(0, 2, 2))
    boundary = Boundary.from_vertices((line_1, line_2))
    origin = Point3D(0, 0, 0)
    axis = Vector3D(1, 0, 0)

    test_1 = boundary.duplicate()
    test_1.rotate(axis, 180, origin)
    assert test_1.geometry[0].p1.x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].p1.y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].p1.z == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].p1.x == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].p1.y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].p1.z == pytest.approx(-2, rel=1e-3)
    assert len(boundary.vertices) == len(test_1.vertices)

    test_2 = boundary.duplicate()
    test_2.rotate(axis, 90, origin)
    assert test_2.geometry[0].p1.x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[0].p1.y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[0].p1.z == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[1].p1.x == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[1].p1.y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[1].p1.z == pytest.approx(2, rel=1e-3)
    assert len(boundary.vertices) == len(test_2.vertices)


def test_rotate_xy():
    """Test the Boundary rotate_xy method."""
    line_1 = (Point3D(1, 1, 2), Point3D(2, 1, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(1, 2, 2))
    boundary = Boundary.from_vertices((line_1, line_2))
    origin_1 = Point3D(1, 1, 0)

    test_1 = boundary.duplicate()
    test_1.rotate_xy(180, origin_1)
    assert test_1.geometry[0].p1.x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].p1.y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].p1.z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].p1.x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[1].p1.y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[1].p1.z == pytest.approx(2, rel=1e-3)

    test_2 = boundary.duplicate()
    test_2.rotate_xy(90, origin_1)
    assert test_2.geometry[0].p1.x == pytest.approx(1, rel=1e-3)
    assert test_2.geometry[0].p1.y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].p1.z == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[1].p1.x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[1].p1.y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].p1.z == pytest.approx(2, rel=1e-3)


def test_reflect():
    """Test the Boundary reflect method."""
    line_1 = (Point3D(1, 1, 2), Point3D(2, 1, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(1, 2, 2))
    boundary = Boundary.from_vertices((line_1, line_2))

    origin_1 = Point3D(1, 0, 2)
    normal_1 = Vector3D(1, 0, 0)
    plane_1 = Plane(normal_1, origin_1)

    test_1 = boundary.duplicate()
    test_1.reflect(plane_1)
    assert test_1.geometry[0].p1.x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].p1.y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].p1.z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].p1.x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[1].p1.y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].p1.z == pytest.approx(2, rel=1e-3)


def test_check_planar():
    """Test the check_planar method."""
    line_1 = (Point3D(0, 0, 2), Point3D(2, 0, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(0, 2, 2))
    boundary_1 = Boundary.from_vertices((line_1, line_2))

    line_1 = (Point3D(0, 0, 0), Point3D(2, 0, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(0, 2, 2))
    boundary_2 = Boundary.from_vertices((line_1, line_2))

    line_1 = (Point3D(0, 0, 2.0001), Point3D(2, 0, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(0, 2, 2))
    boundary_3 = Boundary.from_vertices((line_1, line_2))

    assert boundary_1.check_planar(0.001) == ''
    assert boundary_2.check_planar(0.001, False) != ''
    with pytest.raises(Exception):
        boundary_2.check_planar(0.0001)
    assert boundary_3.check_planar(0.001) == ''
    assert boundary_3.check_planar(0.000001, False) != ''
    with pytest.raises(Exception):
        boundary_3.check_planar(0.000001)


def test_to_dict():
    """Test the boundary to_dict method."""
    vertices = [[(0, 0, 0), (0, 10, 0)], [(0, 10, 3), (0, 0, 3)]]
    bnd = Boundary.from_vertices(vertices)
    bnd.display_name = 'RectangleBoundary'

    bnd = bnd.to_dict()
    assert bnd['type'] == 'Boundary'
    assert uuid.UUID(bnd['identifier'])
    assert bnd['display_name'] == 'RectangleBoundary'
    assert 'geometry' in bnd
    assert bnd['geometry'][0]['p'] == vertices[0][0]
    assert bnd['geometry'][1]['p'] == vertices[1][0]
    assert 'properties' in bnd
    assert bnd['properties']['type'] == 'BoundaryProperties'


def test_to_from_dict():
    """Test the to/from dict of Boundary objects."""
    vertices = [[(0, 0, 0), (0, 10, 0)], [(0, 10, 3), (0, 0, 3)]]
    bnd = Boundary.from_vertices(vertices)
    bnd.display_name = 'RectangleBoundary'

    bnd_dict = bnd.to_dict()
    new_bnd = Boundary.from_dict(bnd_dict)
    assert isinstance(new_bnd, Boundary)
    assert new_bnd.to_dict() == bnd_dict


def test_writer():
    """Test the Boundary writer object."""
    vertices = [[(0, 0, 0), (0, 10, 0)], [(0, 10, 3), (0, 0, 3)]]
    bnd = Boundary.from_vertices(vertices)

    writers = [mod for mod in dir(bnd.to) if not mod.startswith('_')]
    for writer in writers:
        assert callable(getattr(bnd.to, writer))
