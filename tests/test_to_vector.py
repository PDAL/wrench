import subprocess

import utils
from osgeo import ogr

ogr.UseExceptions()


def test_to_vector_las_file(main_laz_file: str):
    """Test to_vector las function"""

    gpkg_file = utils.test_data_filepath("points.gpkg")
    if gpkg_file.exists():
        gpkg_file.unlink()

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "to_vector",
            f"--output={gpkg_file.as_posix()}",
            f"--input={main_laz_file}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert gpkg_file.exists()

    ds: ogr.DataSource = ogr.Open(gpkg_file.as_posix())

    assert ds
    assert ds.GetLayerCount() == 1

    layer: ogr.Layer = ds.GetLayer(0)

    assert layer
    assert layer.GetName() == "points"
    assert layer.GetFeatureCount() == 693895


def test_to_vector_vpc_file(vpc_file: str):
    """Test to_vector las function"""

    gpkg_file = utils.test_data_filepath("points.gpkg")
    if gpkg_file.exists():
        gpkg_file.unlink()

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "to_vector",
            f"--output={gpkg_file.as_posix()}",
            f"--input={vpc_file}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert gpkg_file.exists()

    temp_folder = gpkg_file.parent / gpkg_file.stem

    assert not temp_folder.exists()

    ds: ogr.DataSource = ogr.Open(gpkg_file.as_posix())

    assert ds
    assert ds.GetLayerCount() == 1

    layer: ogr.Layer = ds.GetLayer(0)

    assert layer
    assert layer.GetName() == "points"
    assert layer.GetFeatureCount() == 338163
