import subprocess
import typing

import pdal
import utils


def test_thin_laz_to_las(main_laz_file: str):
    """Test thin to las function"""

    output = utils.test_data_filepath("thin.las")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "thin",
            "--mode=every-nth",
            "--step-every-nth=5",
            f"--input={main_laz_file}",
            f"--output={output.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader.las(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 138779


def test_thin_laz_to_copc(main_laz_file: str):
    """Test thin to copc function"""

    output = utils.test_data_filepath("thin.copc.laz")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "thin",
            "--mode=every-nth",
            "--step-every-nth=5",
            f"--input={main_laz_file}",
            f"--output={output.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader.copc(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 138779


def test_thin_vpc_to_copc(vpc_file: str):
    """Test thin vpc to copc function"""

    output = utils.test_data_filepath("thin-vpc.copc.laz")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "thin",
            "--mode=every-nth",
            "--step-every-nth=5",
            f"--input={vpc_file}",
            f"--output={output.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader.copc(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 67634


def test_thin_copc_to_laz(main_copc_file: str):
    """Test thin copc to laz function"""

    output = utils.test_data_filepath("thin-copc-input.laz")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "thin",
            "--mode=every-nth",
            "--step-every-nth=5",
            f"--input={main_copc_file}",
            f"--output={output.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 138779
