import subprocess

import utils


def test_boundary_laz(main_laz_file: str):
    """Test boundary on las function"""

    output = utils.test_data_filepath("boundary-laz.gpkg")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "boundary",
            f"--output={output.as_posix()}",
            f"--input={main_laz_file}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()


def test_boundary_copc(main_copc_file: str):
    """Test boundary on copc function"""

    output = utils.test_data_filepath("boundary_copc.gpkg")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "boundary",
            f"--output={output.as_posix()}",
            f"--input={main_copc_file}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()


def test_boundary_on_vpc(vpc_laz_file: str):
    """Test boundary on vpc function"""

    output = utils.test_data_filepath("boundary-vpc.gpkg")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "boundary",
            f"--output={output.as_posix()}",
            f"--input={vpc_laz_file}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()
