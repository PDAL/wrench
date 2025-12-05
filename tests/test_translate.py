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


@pytest.mark.parametrize(
    "input_file,output_file",
    [
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("translate-transform-point-check1.laz", "translate-transform-point-check"),
        ),
        (
            utils.test_data_filepath("data.vpc"),
            utils.test_data_output_filepath("translate-transform-point-check2.laz", "translate-transform-point-check"),
        ),
    ],
)
def test_translate_with_transform_laz(input_file: Path, output_file: Path):
    """Test translate with transformation function"""

    translate_x = 100.0
    translate_y = 200.0
    translate_z = 300.0

    output_path = output_file

    matrix = f"1 0 0 {translate_x} " f"0 1 0 {translate_y} " f"0 0 1 {translate_z} " "0 0 0 1"
    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={input_file.as_posix()}",
            f"--output={output_path.as_posix()}",
            f"--transform-matrix={matrix}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    number_of_points_to_check = 10

    pipeline_output = pdal.Reader(filename=output_path.as_posix()).pipeline()
    pipeline_output.execute()
    point_output = pipeline_output.arrays[0][:number_of_points_to_check]

    pipeline_input = pdal.Reader(filename=input_file.as_posix()).pipeline()
    pipeline_input.execute()
    point_input = pipeline_input.arrays[0][:number_of_points_to_check]

    for i in range(number_of_points_to_check):
        assert point_output[i][0] == pytest.approx(point_input[i][0] + translate_x, rel=1e-3)
        assert point_output[i][1] == pytest.approx(point_input[i][1] + translate_y, rel=1e-3)
        assert point_output[i][2] == pytest.approx(point_input[i][2] + translate_z, rel=1e-3)
