import subprocess
import typing
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "output_path",
    [
        (utils.test_data_output_filepath("data_merged.las", "merge")),
        (utils.test_data_output_filepath("data_merged.copc.laz", "merge")),
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
        (utils.test_data_filepath("data_copc.vpc"), utils.test_data_output_filepath("merged-copc-vpc.las", "merge")),
        (
            utils.test_data_filepath("data_copc.vpc"),
            utils.test_data_output_filepath("merged-copc-vpc.cop.laz", "merge"),
        ),
        (utils.test_data_filepath("data.vpc"), utils.test_data_output_filepath("merged-vpc.copc.laz", "merge")),
        (utils.test_data_filepath("data.vpc"), utils.test_data_output_filepath("merged-vpc.las", "merge")),
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


def test_merge_with_extra_attribute():
    """Test merge las function with extra dimension HeightAboveGround"""

    files = [
        utils.test_data_filepath("data_hag_clipped1.las"),
        utils.test_data_filepath("data_hag_clipped2.las"),
        utils.test_data_filepath("data_hag_clipped3.las"),
        utils.test_data_filepath("data_hag_clipped4.las"),
    ]

    output_path = utils.test_data_output_filepath("data_merged_hag.las", "merge")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "merge",
            f"--output={output_path.as_posix()}",
            *[f.as_posix() for f in files],
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 338163

    dimensions = pipeline.arrays[0].dtype.names

    assert "HeightAboveGround" in dimensions
