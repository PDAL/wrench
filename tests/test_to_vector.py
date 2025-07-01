import subprocess
from pathlib import Path

import pytest
import utils
from osgeo import ogr

ogr.UseExceptions()


@pytest.mark.parametrize(
    "input_path,gpkg_file,point_count",
    [
        (utils.test_data_filepath("stadium-utm.laz"), utils.test_data_filepath("points-laz.gpkg"), 693895),
        (utils.test_data_filepath("data.vpc"), utils.test_data_filepath("points-vpc.gpkg"), 338163),
    ],
)
def test_to_vector(input_path: Path, gpkg_file: Path, point_count: int):
    """Test to_vector function"""

    if gpkg_file.exists():
        gpkg_file.unlink()

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "to_vector",
            f"--output={gpkg_file.as_posix()}",
            f"--input={input_path.as_posix()}",
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
    assert layer.GetFeatureCount() == point_count
