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


def test_translate_with_transform_laz():
    """Test translate with transformation function"""

    input_file = utils.test_data_filepath("stadium-utm.laz")
    output_file = utils.test_data_output_filepath(
        "translate-transform-point-check.laz", "translate-transform-point-check"
    )

    matrix = [
        "1 0 0 100",
        "0 1 0 200",
        "0 0 1 300",
        "0 0 0 1",
    ]
    matrix_arg = " ".join(matrix)

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={input_file.as_posix()}",
            f"--output={output_file.as_posix()}",
            f"--transform-matrix={matrix_arg}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_file.exists()

    pipeline_output = pdal.Reader(filename=output_file.as_posix()).pipeline()
    pipeline_output.execute()
    first_point_output = pipeline_output.arrays[0][0]

    assert first_point_output["X"] == 494576.35000000003
    assert first_point_output["Y"] == 4878552.03
    assert first_point_output["Z"] == 427.45
