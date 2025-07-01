import subprocess
import typing
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "output_path",
    [
        (utils.test_data_filepath("data_merged.las")),
        (utils.test_data_filepath("data_merged.copc.laz")),
    ],
)
def test_merge_to_file(output_path: Path, laz_files: typing.List[str]):
    """Test merge las function"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "merge",
            f"--output={output_path.as_posix()}",
            *laz_files,
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 338163


@pytest.mark.parametrize(
    "input_path,output_path",
    [
        (utils.test_data_filepath("data_copc.vpc"), utils.test_data_filepath("merged-copc-vpc.las")),
        (utils.test_data_filepath("data_copc.vpc"), utils.test_data_filepath("merged-copc-vpc.cop.laz")),
        (utils.test_data_filepath("data.vpc"), utils.test_data_filepath("merged-vpc.copc.laz")),
        (utils.test_data_filepath("data.vpc"), utils.test_data_filepath("merged-vpc.las")),
    ],
)
def test_merge_vpc(
    input_path: Path,
    output_path: Path,
):
    """Test merge of vpc file"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "merge",
            f"--output={output_path.as_posix()}",
            input_path.as_posix(),
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 338163
