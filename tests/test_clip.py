import subprocess
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_path,output_path",
    [
        (utils.test_data_filepath("stadium-utm.laz"), utils.test_data_filepath("clipped.las")),
        (utils.test_data_filepath("stadium-utm.laz"), utils.test_data_filepath("clipped.copc.laz")),
        (utils.test_data_filepath("stadium-utm.copc.laz"), utils.test_data_filepath("clipped-copc-input.laz")),
        (utils.test_data_filepath("stadium-utm.copc.laz"), utils.test_data_filepath("clipped-copc-input.copc.laz")),
    ],
)
def test_input_file_output_file(
    input_path: Path,
    output_path: Path,
):
    """Test clip input is file output is file"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "clip",
            f"--output={output_path.as_posix()}",
            f"--input={input_path.as_posix()}",
            f"--polygon={utils.test_data_filepath('rectangle1.gpkg')}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 66832


@pytest.mark.parametrize(
    "input_path,output_path",
    [
        (utils.test_data_filepath("data.vpc"), utils.test_data_filepath("clipped-vpc.copc.laz")),
        (utils.test_data_filepath("data_copc.vpc"), utils.test_data_filepath("clipped-vpc-copc-files.vpc")),
        (utils.test_data_filepath("data_copc.vpc"), utils.test_data_filepath("clipped-vpc-copc-files.copc.laz")),
    ],
)
def test_clip_vpc(
    input_path: Path,
    output_path: Path,
):
    """Test clip vpc to different outputs function"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "clip",
            f"--output={output_path.as_posix()}",
            f"--input={input_path.as_posix()}",
            f"--polygon={utils.test_data_filepath('rectangle.gpkg')}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 66911
