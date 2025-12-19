"""Test Model class."""
import pytest
import os
import json
import uuid

from ladybug_geometry.geometry3d import Point3D, Vector3D, LineSegment3D, Plane, Face3D

from fairyfly.model import Model
from fairyfly.shape import Shape
from fairyfly.boundary import Boundary


def test_model_init():
    """Test the initialization of the Model and basic properties."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shape = Shape(Face3D(pts))
    shape.display_name = 'TestShape'

    line_1 = LineSegment3D.from_end_points(Point3D(0, 0, 0), Point3D(0, 0, 3))
    boundary_1 = Boundary((line_1,))
    boundary_1.display_name = 'Outdoors'

    line_2 = LineSegment3D.from_end_points(Point3D(1, 0, 0), Point3D(1, 0, 3))
    boundary_2 = Boundary((line_2,))
    boundary_2.display_name = 'Indoors'

    model = Model([shape], [boundary_1, boundary_2])
    model.display_name = 'Single Material'
    str(model)  # test the string representation of the object

    assert uuid.UUID(model.identifier)
    assert model.display_name == 'Single Material'
    assert model.units == 'Millimeters'
    assert model.tolerance == 0.01
    assert model.angle_tolerance == 1.0
    assert len(model.shapes) == 1
    assert isinstance(model.shapes[0], Shape)
    assert len(model.boundaries) == 2
    assert isinstance(model.boundaries[0], Boundary)

    assert model.shape_area == pytest.approx(3, rel=1e-3)
    assert model.boundary_length == pytest.approx(6, rel=1e-3)
    assert isinstance(model.min, Point3D)
    assert isinstance(model.max, Point3D)
    assert isinstance(model.center, Point3D)


def test_model_properties_setability():
    """Test the setting of properties on the Model."""
    model = Model.from_layers([15, 5, 100, 15])
    model.display_name = 'Layered Construction'

    assert model.display_name == 'Layered Construction'
    model.units = 'Centimeters'
    assert model.units == 'Centimeters'
    model.tolerance = 0.1
    assert model.tolerance == 0.1
    model.angle_tolerance = 0.01
    assert model.angle_tolerance == 0.01
    model.tolerance = None
    assert model.tolerance == 0.001


def test_model_init_from_objects():
    """Test the initialization of the Model from_objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shape = Shape(Face3D(pts))
    shape.display_name = 'TestShape'
    line_1 = LineSegment3D.from_end_points(Point3D(0, 0, 0), Point3D(0, 0, 3))
    boundary_1 = Boundary((line_1,))
    boundary_1.display_name = 'Outdoors'
    line_2 = LineSegment3D.from_end_points(Point3D(1, 0, 0), Point3D(1, 0, 3))
    boundary_2 = Boundary((line_2,))
    boundary_2.display_name = 'Indoors'

    model = Model.from_objects([shape, boundary_1, boundary_2])
    model.display_name = 'Single Material'

    assert len(model.shapes) == 1
    assert isinstance(model.shapes[0], Shape)
    assert len(model.boundaries) == 2
    assert isinstance(model.boundaries[0], Boundary)


def test_shapes_by_identifier():
    """Test the shapes_by_identifier method."""
    pts1 = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shape1_id = uuid.uuid4()
    shape1 = Shape(Face3D(pts1), identifier=shape1_id)
    pts2 = (Point3D(1, 0, 0), Point3D(1, 0, 3), Point3D(2, 0, 3), Point3D(2, 0, 0))
    shape2_id = uuid.uuid4()
    shape2 = Shape(Face3D(pts2), identifier=shape2_id)
    model = Model(shapes=[shape1, shape2])

    assert len(model.shapes_by_identifier([shape1_id])) == 1
    with pytest.raises(ValueError):
        model.shapes_by_identifier([str(uuid.uuid4())])

    model.remove_shapes()
    with pytest.raises(ValueError):
        model.shapes_by_identifier([shape2_id])


def test_boundaries_by_identifier():
    """Test the boundaries_by_identifier method."""
    line_1 = LineSegment3D.from_end_points(Point3D(0, 0, 0), Point3D(0, 0, 3))
    bnd1_id = uuid.uuid4()
    boundary_1 = Boundary((line_1,), identifier=bnd1_id)
    boundary_1.display_name = 'Outdoors'
    line_2 = LineSegment3D.from_end_points(Point3D(1, 0, 0), Point3D(1, 0, 3))
    bnd2_id = uuid.uuid4()
    boundary_2 = Boundary((line_2,), identifier=bnd2_id)
    boundary_2.display_name = 'Indoors'
    model = Model(boundaries=[boundary_1, boundary_2])

    assert len(model.boundaries_by_identifier([bnd1_id])) == 1
    with pytest.raises(ValueError):
        model.boundaries_by_identifier([str(uuid.uuid4())])

    model.remove_boundaries()
    with pytest.raises(ValueError):
        model.boundaries_by_identifier([bnd2_id])


def test_move():
    """Test the Model move method."""
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 0))
    shape = Shape(Face3D(pts_1, plane_1))
    line_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0))
    line_2 = (Point3D(2, 2, 0), Point3D(0, 2, 0))
    boundary = Boundary.from_vertices((line_1, line_2))
    model = Model([shape], [boundary])
    model.display_name = 'Single Material'

    model = model.duplicate()
    vec_1 = Vector3D(2, 2, 2)
    model.move(vec_1)

    new_shp = model.shapes[0]
    assert new_shp.geometry[0] == Point3D(2, 2, 2)
    assert new_shp.geometry[1] == Point3D(4, 2, 2)
    assert new_shp.geometry[2] == Point3D(4, 4, 2)
    assert new_shp.geometry[3] == Point3D(2, 4, 2)
    assert new_shp.normal == shape.normal
    assert shape.area == new_shp.area
    assert shape.perimeter == new_shp.perimeter

    new_bnd = model.boundaries[0]
    assert new_bnd.geometry[0].p1 == Point3D(2, 2, 2)
    assert new_bnd.geometry[0].p2 == Point3D(4, 2, 2)
    assert new_bnd.geometry[1].p1 == Point3D(4, 4, 2)
    assert new_bnd.geometry[1].p2 == Point3D(2, 4, 2)
    assert boundary.length == new_bnd.length


def test_scale():
    """Test the Model scale method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shape = Shape(Face3D(pts, plane))
    line_1 = (Point3D(1, 1, 2), Point3D(2, 1, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(1, 2, 2))
    boundary = Boundary.from_vertices((line_1, line_2))
    model = Model([shape], [boundary])
    model.display_name = 'Single Material'

    model = model.duplicate()
    model.scale(2)

    new_shp = model.shapes[0]
    assert new_shp.geometry[0] == Point3D(2, 2, 4)
    assert new_shp.geometry[1] == Point3D(4, 2, 4)
    assert new_shp.geometry[2] == Point3D(4, 4, 4)
    assert new_shp.geometry[3] == Point3D(2, 4, 4)
    assert new_shp.area == pytest.approx(shape.area * 2 ** 2, rel=1e-3)
    assert new_shp.perimeter == shape.perimeter * 2
    assert new_shp.normal == shape.normal

    new_bnd = model.boundaries[0]
    assert new_bnd.geometry[0].p1 == Point3D(2, 2, 4)
    assert new_bnd.geometry[0].p2 == Point3D(4, 2, 4)
    assert new_bnd.geometry[1].p1 == Point3D(4, 4, 4)
    assert new_bnd.geometry[1].p2 == Point3D(2, 4, 4)
    assert new_bnd.length == boundary.length * 2


def test_convert_to_units():
    """Test the Model convert_to_units method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shape = Shape(Face3D(pts, plane))
    line_1 = (Point3D(1, 1, 2), Point3D(2, 1, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(1, 2, 2))
    boundary = Boundary.from_vertices((line_1, line_2))
    model = Model([shape], [boundary], units='Centimeters')
    model.display_name = 'Single Material'

    model = model.duplicate()
    model.convert_to_units('Millimeters')

    new_shp = model.shapes[0]
    assert new_shp.area == pytest.approx(shape.area * 100, rel=1e-3)
    assert new_shp.perimeter == shape.perimeter * 10
    assert new_shp.normal == shape.normal

    new_bnd = model.boundaries[0]
    assert new_bnd.length == boundary.length * 10

    model.convert_to_units('Inches')


def test_remove_degenerate_geometry():
    """Test the Model remove_degenerate_geometry method."""
    model = Model.from_layers([15, 5, 100, 15])
    model.display_name = 'Layered Construction'
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(0, 0, 3), Point3D(0.0001, 0, 0))
    shape = Shape(Face3D(pts))
    shape.display_name = 'Degenerate Shape'
    model.add_shape(shape)

    assert len(model.shapes) == 5
    assert len(model.boundaries) == 2
    model.remove_degenerate_geometry()
    assert len(model.shapes) == 4
    assert len(model.boundaries) == 2


def test_check_duplicate_shape_identifiers():
    """Test the check_duplicate_shape_identifiers method."""
    pts1 = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shape1_id = uuid.uuid4()
    shape1 = Shape(Face3D(pts1), identifier=shape1_id)
    pts2 = (Point3D(1, 0, 0), Point3D(1, 0, 3), Point3D(2, 0, 3), Point3D(2, 0, 0))
    shape2 = Shape(Face3D(pts2), identifier=shape1_id)
    model_1 = Model(shapes=[shape1])
    model_2 = Model(shapes=[shape1, shape2])

    assert model_1.check_duplicate_shape_identifiers(False) == ''
    assert model_2.check_duplicate_shape_identifiers(False) != ''
    with pytest.raises(ValueError):
        model_2.check_duplicate_shape_identifiers(True)


def test_check_duplicate_boundary_identifiers():
    """Test the check_duplicate_boundary_identifiers method."""
    line_1 = LineSegment3D.from_end_points(Point3D(0, 0, 0), Point3D(0, 0, 3))
    bnd1_id = uuid.uuid4()
    boundary_1 = Boundary((line_1,), identifier=bnd1_id)
    boundary_1.display_name = 'Outdoors'
    line_2 = LineSegment3D.from_end_points(Point3D(1, 0, 0), Point3D(1, 0, 3))
    boundary_2 = Boundary((line_2,), identifier=bnd1_id)
    boundary_2.display_name = 'Indoors'
    model_1 = Model(boundaries=[boundary_1])
    model_2 = Model(boundaries=[boundary_1, boundary_2])

    assert model_1.check_duplicate_boundary_identifiers(False) == ''
    assert model_2.check_duplicate_boundary_identifiers(False) != ''
    with pytest.raises(ValueError):
        model_2.check_duplicate_boundary_identifiers(True)


def test_check_planar():
    """Test the check_planar method."""
    pts_1 = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    pts_2 = (Point3D(0, 0, 0), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shape_1 = Shape(Face3D(pts_1, plane_1))
    shape_2 = Shape(Face3D(pts_2, plane_1))
    line_1 = (Point3D(0, 0, 2), Point3D(2, 0, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(0, 2, 2))
    boundary_1 = Boundary.from_vertices((line_1, line_2))
    line_1 = (Point3D(0, 0, 0), Point3D(2, 0, 2))
    line_2 = (Point3D(2, 2, 2), Point3D(0, 2, 2))
    boundary_2 = Boundary.from_vertices((line_1, line_2))

    model_1 = Model([shape_1], [boundary_1])
    model_2 = Model([shape_2], [boundary_2])
    assert model_1.check_planar(0.01, False) == ''
    assert model_2.check_planar(0.01, False) != ''
    with pytest.raises(ValueError):
        model_2.check_planar(0.01, True)


def test_check_self_intersecting():
    """Test the check_self_intersecting method."""
    plane_1 = Plane(Vector3D(0, 0, 1))
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2), Point3D(0, 2))
    pts_2 = (Point3D(0, 0), Point3D(0, 2), Point3D(2, 0), Point3D(2, 2))
    shape_1 = Shape(Face3D(pts_1, plane_1))
    shape_2 = Shape(Face3D(pts_2, plane_1))

    model_1 = Model([shape_1])
    model_2 = Model([shape_2])
    assert model_1.check_self_intersecting(0.01, False) == ''
    assert model_2.check_self_intersecting(0.01, False) != ''
    with pytest.raises(ValueError):
        model_2.check_self_intersecting(0.01, True)


def test_to_dict():
    """Test the Model to_dict method."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shape = Shape(Face3D(pts))
    shape.display_name = 'TestShape'
    line_1 = LineSegment3D.from_end_points(Point3D(0, 0, 0), Point3D(0, 0, 3))
    boundary_1 = Boundary((line_1,))
    boundary_1.display_name = 'Outdoors'
    line_2 = LineSegment3D.from_end_points(Point3D(1, 0, 0), Point3D(1, 0, 3))
    boundary_2 = Boundary((line_2,))
    boundary_2.display_name = 'Indoors'
    model = Model([shape], [boundary_1, boundary_2])
    model.display_name = 'Single Material'

    model_dict = model.to_dict()
    assert model_dict['type'] == 'Model'
    assert uuid.UUID(model_dict['identifier'])
    assert model_dict['display_name'] == 'Single Material'
    assert 'shapes' in model_dict
    assert len(model_dict['shapes']) == 1
    assert 'boundaries' in model_dict
    assert len(model_dict['boundaries']) == 2
    assert 'properties' in model_dict
    assert model_dict['properties']['type'] == 'ModelProperties'


def test_to_from_dict_methods():
    """Test the to/from dict methods."""
    model = Model.from_layers([15, 5, 100, 15])
    model.display_name = 'Layered Construction'

    model_dict = model.to_dict()
    new_model = Model.from_dict(model_dict)
    assert model_dict == new_model.to_dict()

    assert new_model.identifier == model.identifier
    assert new_model.display_name == 'Layered Construction'
    assert len(new_model.shapes) == 4
    assert isinstance(new_model.shapes[0], Shape)
    assert len(new_model.boundaries) == 2
    assert isinstance(new_model.boundaries[0], Boundary)


def test_to_ffjson():
    """Test the Model to_ffjson method."""
    model = Model.from_layers([15, 5, 100, 15])
    model.display_name = 'Layered Construction'

    path = './tests/json'
    model_ffjson = model.to_ffjson("test", path)
    assert os.path.isfile(model_ffjson)
    with open(model_ffjson) as f:
        model_dict = json.load(f)
    assert model_dict['type'] == 'Model'
    assert uuid.UUID(model_dict['identifier'])
    assert model_dict['display_name'] == 'Layered Construction'
    assert 'shapes' in model_dict
    assert len(model_dict['shapes']) == 4
    assert 'boundaries' in model_dict
    assert len(model_dict['boundaries']) == 2
    assert 'properties' in model_dict
    assert model_dict['properties']['type'] == 'ModelProperties'

    new_model = Model.from_ffjson(model_ffjson)
    assert isinstance(new_model, Model)
    os.remove(model_ffjson)


def test_to_ffpkl():
    """Test the Model to_ffpkl method."""
    model = Model.from_layers([15, 5, 100, 15])
    model.display_name = 'Layered Construction'

    path = './tests/json'
    model_ffpkl = model.to_ffpkl('test', path)
    assert os.path.isfile(model_ffpkl)
    new_model = Model.from_ffpkl(model_ffpkl)
    assert isinstance(new_model, Model)
    os.remove(model_ffpkl)


def test_writer():
    """Test the Model writer object."""
    model = Model.from_layers([15, 5, 100, 15])
    model.display_name = 'Layered Construction'

    writers = [mod for mod in dir(model.to) if not mod.startswith('_')]
    for writer in writers:
        assert callable(getattr(model.to, writer))
