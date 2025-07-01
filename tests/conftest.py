import subprocess
import typing

import pdal
import pytest
import requests
import utils


@pytest.fixture(autouse=True, scope="session")
def _prepare_data():

    test_data_folder = utils.test_data_folder()

    if not test_data_folder.exists():
        test_data_folder.mkdir(parents=True)

    base_data = utils.test_data_filepath("stadium-utm.laz")

    if not base_data.exists():
        # PDAL autzen stadium dataset
        url = "https://media.githubusercontent.com/media/PDAL/data/refs/heads/main/autzen/stadium-utm.laz"

        r = requests.get(url, timeout=10 * 60)

        with open(base_data, "wb") as f:
            f.write(r.content)
            # Run the pdal_wrench command

    laz_file = pdal.Reader(base_data.as_posix()).pipeline()
    number_points = laz_file.execute()

    assert number_points == 693895

    files_for_vpc = []
    files_for_vpc_copc = []

    for i in range(1, 5):

        clip_gpkg_file = utils.test_data_filepath(f"rectangle{i}.gpkg")
        clipped_laz_file = utils.test_data_filepath(f"data_clipped{i}.laz")
        clipped_copc_file = utils.test_data_filepath(f"data_clipped{i}.copc.laz")

        files_for_vpc.append(clipped_laz_file)
        files_for_vpc_copc.append(clipped_copc_file)

        if not clipped_laz_file.exists():

            input_file = base_data

            res = subprocess.run(
                [
                    utils.pdal_wrench_path(),
                    "clip",
                    "--polygon",
                    str(clip_gpkg_file),
                    "--output",
                    str(clipped_laz_file),
                    "--input",
                    str(input_file),
                ],
                check=True,
            )

            assert res.returncode == 0

            clipped_laz = pdal.Reader(clipped_laz_file.as_posix()).pipeline()
            number_points = clipped_laz.execute()

            assert number_points > 0

        assert clipped_laz_file.exists()

        if not clipped_copc_file.exists():

            input_file = base_data

            res = subprocess.run(
                [
                    utils.pdal_wrench_path(),
                    "clip",
                    "--polygon",
                    str(clip_gpkg_file),
                    "--output",
                    str(clipped_copc_file),
                    "--input",
                    str(input_file),
                ],
                check=True,
            )

            assert res.returncode == 0

            clipped_copc = pdal.Reader(clipped_copc_file.as_posix()).pipeline()
            number_points = clipped_copc.execute()

            assert number_points > 0

    vpc_file = utils.test_data_filepath("data.vpc")

    if not vpc_file.exists():
        res = subprocess.run(
            [
                utils.pdal_wrench_path(),
                "build_vpc",
                "--output",
                vpc_file.as_posix(),
                *[f.as_posix() for f in files_for_vpc],
            ],
            check=True,
        )

        assert res.returncode == 0

    assert vpc_file.exists()

    vpc = pdal.Reader(vpc_file.as_posix()).pipeline()
    number_points = vpc.execute()

    assert number_points == 338163

    vpc_copc_file = utils.test_data_filepath("data_copc.vpc")

    if not vpc_copc_file.exists():
        res = subprocess.run(
            [
                utils.pdal_wrench_path(),
                "build_vpc",
                "--output",
                vpc_copc_file.as_posix(),
                *[f.as_posix() for f in files_for_vpc_copc],
            ],
            check=True,
        )

        assert res.returncode == 0

    assert vpc_copc_file.exists()

    vpc_copc = pdal.Reader(vpc_copc_file.as_posix()).pipeline()
    number_points = vpc_copc.execute()

    assert number_points == 338163

    base_copc_data = utils.test_data_filepath("stadium-utm.copc.laz")

    if not base_copc_data.exists():
        res = subprocess.run(
            [
                utils.pdal_wrench_path(),
                "translate",
                f"--input={base_data.as_posix()}",
                f"--output={base_copc_data.as_posix()}",
            ],
            check=True,
        )

        assert res.returncode == 0

    assert base_copc_data.exists()

    vpc = pdal.Reader.copc(base_copc_data.as_posix()).pipeline()
    number_points = vpc.execute()

    assert number_points == 693895


@pytest.fixture
def laz_files() -> typing.List[str]:
    """Return a list of laz files"""
    files = []
    for i in range(1, 5):
        files.append(utils.test_data_filepath(f"data_clipped{i}.laz").as_posix())
    return files


@pytest.fixture
def main_laz_file() -> str:
    "Return path to the main laz file"
    return utils.test_data_filepath("stadium-utm.laz").as_posix()


@pytest.fixture
def vpc_laz_file() -> str:
    "Return path to the vpc file referencing LAZ files"
    return utils.test_data_filepath("data.vpc").as_posix()


@pytest.fixture
def vpc_copc_file() -> str:
    "Return path to the vpc file referencing COPC files"
    return utils.test_data_filepath("data_copc.vpc").as_posix()


@pytest.fixture
def main_copc_file() -> str:
    "Return path to the main copc file"
    return utils.test_data_filepath("stadium-utm.copc.laz").as_posix()
