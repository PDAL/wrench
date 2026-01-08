import subprocess
from pathlib import Path

import numpy as np
import pdal
import pytest
import utils


# test that has input file with all points set to never classified (0)
# this checks even that the pipeline classifies points correctly
def test_classify_ground_no_classification(main_copc_file_without_classification: str):

    output_path = utils.test_data_output_filepath(f"stadium-utm-classified-ground.las", "classify_ground")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "classify_ground",
            f"--input={main_copc_file_without_classification}",
            f"--output={output_path.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()
    number_of_points = pipeline.execute()

    assert number_of_points == 693895

    values = pipeline.arrays[0]["Classification"]
    unique_values = np.unique(values)

    assert unique_values.size == 3
    assert unique_values.tolist() == [0, 1, 2]  # 1: non-ground, 2: ground, 0: never classified

    # test ground point
    ground_point_output = pipeline.arrays[0][
        (pipeline.arrays[0]["X"] == 494657.37) & (pipeline.arrays[0]["Y"] == 4878358.05)
    ]
    assert ground_point_output["Classification"] == 2  # ground
    assert ground_point_output["Z"] == 130.15999999999997

    # test nonground point
    nonground_point_output = pipeline.arrays[0][
        (pipeline.arrays[0]["X"] == 494650.04000000004) & (pipeline.arrays[0]["Y"] == 4878440.17)
    ]
    assert nonground_point_output["Classification"] == 1  # non-ground
    assert nonground_point_output["Z"] == 140.09999999999997


# these tests use various input files to test classify_ground
@pytest.mark.parametrize(
    "input_path,output_path,point_count",
    [
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("classify-ground.las", "classify_ground"),
            693895,
        ),
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("classify-ground.copc.laz", "classify_ground"),
            693895,
        ),
        (
            utils.test_data_filepath("stadium-utm.copc.laz"),
            utils.test_data_output_filepath("classify-ground.copc.laz", "classify_ground"),
            693895,
        ),
        (
            utils.test_data_filepath("data.vpc"),
            utils.test_data_output_filepath("classify-ground-vpc.copc.laz", "classify_ground"),
            338163,
        ),
        (
            utils.test_data_filepath("data_copc.vpc"),
            utils.test_data_output_filepath("classify-ground-vpc.copc.laz", "classify_ground"),
            338163,
        ),
    ],
)
def test_classify_ground(input_path: Path, output_path: Path, point_count: int):

    output_path = utils.test_data_output_filepath(f"stadium-utm-classified-ground.copc.laz", "classify_ground")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "classify_ground",
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


def test_classify_ground_vpc_with_las_output_format():
    input_path = utils.test_data_filepath("data.vpc")

    vpc_las_output_path = utils.test_data_output_filepath("classify-ground-las.vpc", "classify_ground")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "classify_ground",
            f"--input={input_path.as_posix()}",
            f"--output={vpc_las_output_path.as_posix()}",
            "--vpc-output-format=las",
        ],
        check=True,
    )

    assert res.returncode == 0

    output_subfolder = vpc_las_output_path.parent / vpc_las_output_path.stem

    assert output_subfolder.exists()
    assert all([x.suffix == ".las" for x in output_subfolder.iterdir()])


def test_classify_ground_vpc_with_default_output_format():

    input_path = utils.test_data_filepath("data.vpc")

    vpc_copc_laz_output_path = utils.test_data_output_filepath("classify-ground-copc-laz.vpc", "classify_ground")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "classify_ground",
            f"--input={input_path.as_posix()}",
            f"--output={vpc_copc_laz_output_path.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    output_subfolder = vpc_copc_laz_output_path.parent / vpc_copc_laz_output_path.stem

    assert output_subfolder.exists()
    assert all([x.suffixes == [".copc", ".laz"] for x in output_subfolder.iterdir()])
