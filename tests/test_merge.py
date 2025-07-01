import subprocess
import typing
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_type,output",
    [
        ("laz_files", utils.test_data_filepath("data_merged.las")),
        ("laz_files", utils.test_data_filepath("data_merged.copc.laz")),
    ],
)
def test_merge_to_file(input_type: str, output: Path, laz_files: typing.List[str]):
    """Test merge las function"""

    if input_type == "laz_files":
        input_files = laz_files
    else:
        assert False, "Invalid input type"

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "merge",
            f"--output={output.as_posix()}",
            *laz_files,
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 338163


@pytest.mark.parametrize(
    "input_type,output",
    [
        ("vpc_copc_file", utils.test_data_filepath("merged-copc-vpc.las")),
        ("vpc_copc_file", utils.test_data_filepath("merged-copc-vpc.cop.laz")),
        ("vpc_file", utils.test_data_filepath("merged-vpc.copc.laz")),
        ("vpc_file", utils.test_data_filepath("merged-vpc.las")),
    ],
)
def test_merge_vpc(
    input_type: str,
    output: Path,
    vpc_laz_file: str,
    vpc_copc_file: str,
):
    """Test merge of vpc file"""

    if input_type == "vpc_file":
        input = vpc_laz_file
    elif input_type == "vpc_copc_file":
        input = vpc_copc_file
    else:
        assert False, "Invalid input type"

    print(f" {utils.pdal_wrench_path()}" " merge" f" --output={output.as_posix()}" f" {input}")
    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "merge",
            f"--output={output.as_posix()}",
            input,
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 338163
