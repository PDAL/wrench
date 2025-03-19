import subprocess
import typing

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

    files_for_vpc = []
    for i in range(1, 5):

        clip_gpkg_file = utils.test_data_filepath(f"rectangle{i}.gpkg")
        clipped_las_file = utils.test_data_filepath(f"data_clipped{i}.las")

        files_for_vpc.append(clipped_las_file)

        if not clipped_las_file.exists():

            input_file = base_data

            res = subprocess.run(
                [
                    utils.pdal_wrench_path(),
                    "clip",
                    "--polygon",
                    str(clip_gpkg_file),
                    "--output",
                    str(clipped_las_file),
                    "--input",
                    str(input_file),
                ],
                check=True,
            )

            assert res.returncode == 0

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


@pytest.fixture
def las_files() -> typing.List[str]:
    """Return a list of las files"""
    files = []
    for i in range(1, 5):
        files.append(utils.test_data_filepath(f"data_clipped{i}.las").as_posix())
    return files
