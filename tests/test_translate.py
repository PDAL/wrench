import subprocess
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_path,output_path,point_count",
    [
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("translate.las", "translate"),
            693895,
        ),
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("translate.copc.laz", "translate"),
            693895,
        ),
        (
            utils.test_data_filepath("stadium-utm.copc.laz"),
            utils.test_data_output_filepath("translate-copc-input.copc.laz", "translate"),
            693895,
        ),
        (
            utils.test_data_filepath("data.vpc"),
            utils.test_data_output_filepath("translate-vpc.copc.laz", "translate"),
            338163,
        ),
        (
            utils.test_data_filepath("data_copc.vpc"),
            utils.test_data_output_filepath("translate.vpc", "translate"),
            338163,
        ),
    ],
)
def test_translate_files(input_path: Path, output_path: Path, point_count: int):
    """Test translate function"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == point_count


@pytest.mark.parametrize(
    "input_path,output_path,point_count",
    [
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("translate-transform.las", "translate-transform"),
            693895,
        ),
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("translate-transform.copc.laz", "translate-transform"),
            693895,
        ),
        (
            utils.test_data_filepath("stadium-utm.copc.laz"),
            utils.test_data_output_filepath("translate-transform-copc-input.copc.laz", "translate-transform"),
            693895,
        ),
        (
            utils.test_data_filepath("data.vpc"),
            utils.test_data_output_filepath("translate-transform-vpc.copc.laz", "translate-transform"),
            338163,
        ),
        (
            utils.test_data_filepath("data_copc.vpc"),
            utils.test_data_output_filepath("translate-transform.vpc", "translate-transform"),
            338163,
        ),
    ],
)
def test_translate_with_transform_files(input_path: Path, output_path: Path, point_count: int):
    """Test translate with transformation function"""

    matrix = "1 0 0 100 " "0 1 0 200 " "0 0 1 300 " "0 0 0 1"

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            f"--transform-matrix={matrix}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == point_count
