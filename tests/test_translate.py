import subprocess
import typing

import pdal
import utils


def test_translate_laz_to_las(main_laz_file: str):
    """Test translate las function"""

    output = utils.test_data_filepath("translate.las")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={main_laz_file}",
            f"--output={output.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader.las(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 693895


def test_translate_laz_to_copc(main_laz_file: str):
    """Test translate las function"""

    output = utils.test_data_filepath("translate.copc.laz")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={main_laz_file}",
            f"--output={output.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader.copc(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 693895


def test_translate_vpc_to_copc(vpc_file: str):
    """Test translate vpc to copc function"""

    output = utils.test_data_filepath("translate.copc.laz")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={vpc_file}",
            f"--output={output.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader.copc(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 97965
