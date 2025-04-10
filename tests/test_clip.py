import subprocess

import numpy as np
import pdal
import utils


def test_clip_laz_to_las(main_laz_file: str):
    """Test clip las function"""

    clipped_las_file = utils.test_data_filepath("clipped.las")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "clip",
            f"--output={clipped_las_file.as_posix()}",
            f"--input={main_laz_file}",
            f"--polygon={utils.test_data_filepath('rectangle1.gpkg')}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert clipped_las_file.exists()

    pipeline = pdal.Reader.las(filename=clipped_las_file.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 66832

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


def test_clip_laz_to_copc(main_laz_file: str):
    """Test clip las function"""

    clipped_las_file = utils.test_data_filepath("clipped.copc.laz")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "clip",
            f"--output={clipped_las_file.as_posix()}",
            f"--input={main_laz_file}",
            f"--polygon={utils.test_data_filepath('rectangle1.gpkg')}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert clipped_las_file.exists()

    pipeline = pdal.Reader.las(filename=clipped_las_file.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 66832


def test_clip_vpc_to_copc(vpc_file: str):
    """Test clip vpc to copc function"""

    clipped_file = utils.test_data_filepath("clipped-vpc.copc.laz")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "clip",
            f"--output={clipped_file.as_posix()}",
            f"--input={vpc_file}",
            f"--polygon={utils.test_data_filepath('rectangle.gpkg')}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert clipped_file.exists()

    pipeline = pdal.Reader.copc(filename=clipped_file.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 19983
