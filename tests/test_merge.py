import subprocess
import typing

import numpy as np
import pdal
import utils


def test_merge_las(laz_files: typing.List[str]):
    """Test merge las function"""

    merged_las_file = utils.test_data_filepath("data_merged.las")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "merge",
            f"--output={merged_las_file.as_posix()}",
            *laz_files,
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader.las(filename=merged_las_file.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 338163

    # points as numpy array
    array = pipeline.arrays[0]

    # all points
    assert isinstance(array, np.ndarray)

    # first point
    assert isinstance(array[0], np.void)
    assert len(array[0]) == 20
    assert isinstance(array[0]["X"], np.float64)
    assert isinstance(array[0]["Y"], np.float64)
    assert isinstance(array[0]["Z"], np.float64)
    assert isinstance(array[0]["Intensity"], np.uint16)


def test_merge_vpc(vpc_file: str):
    """Test merge of vpc file"""

    merged_las_file = utils.test_data_filepath("data_merged.las")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "merge",
            f"--output={merged_las_file.as_posix()}",
            vpc_file,
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader.las(filename=merged_las_file.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 338163

    # points as numpy array
    array = pipeline.arrays[0]

    # all points
    assert isinstance(array, np.ndarray)

    # first point
    assert isinstance(array[0], np.void)
    assert len(array[0]) == 20
    assert isinstance(array[0]["X"], np.float64)
    assert isinstance(array[0]["Y"], np.float64)
    assert isinstance(array[0]["Z"], np.float64)
    assert isinstance(array[0]["Intensity"], np.uint16)


def test_merge_to_copc(laz_files: typing.List[str]):
    """Test merge to copc function"""

    merged_copc_file = utils.test_data_filepath("data_merged.copc.laz")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "merge",
            f"--output={merged_copc_file.as_posix()}",
            *laz_files,
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader(filename=merged_copc_file.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 97965
