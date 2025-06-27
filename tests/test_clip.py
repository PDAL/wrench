import subprocess
from pathlib import Path

import numpy as np
import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_type,output",
    [
        ("main_laz", utils.test_data_filepath("clipped.las")),
        ("main_laz", utils.test_data_filepath("clipped.copc.laz")),
        ("main_copc", utils.test_data_filepath("clipped-copc-input.laz")),
        ("main_copc", utils.test_data_filepath("clipped-copc-input.copc.laz")),
    ],
)
def test_input_file_output_file(
    input_type: str,
    output: Path,
    main_laz_file: str,
    main_copc_file: str,
):
    """Test clip input is file output is file"""

    if input_type == "main_laz":
        input = main_laz_file
    elif input_type == "main_copc":
        input = main_copc_file
    else:
        assert False, "Invalid input type"

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "clip",
            f"--output={output.as_posix()}",
            f"--input={input}",
            f"--polygon={utils.test_data_filepath('rectangle1.gpkg')}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 66832


@pytest.mark.parametrize(
    "input_type,output",
    [
        ("vpc_file", utils.test_data_filepath("clipped-vpc.copc.laz")),
        ("vpc_copc_file", utils.test_data_filepath("clipped-vpc-copc-files.vpc")),
        ("vpc_copc_file", utils.test_data_filepath("clipped-vpc-copc-files.copc.laz")),
    ],
)
def test_clip_vpc(input_type: str, output: Path, vpc_file: str, vpc_copc_file: str):
    """Test clip vpc to different outputs function"""

    if input_type == "vpc_file":
        input = vpc_file
    elif input_type == "vpc_copc_file":
        input = vpc_copc_file
    else:
        assert False, "Invalid input type"

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "clip",
            f"--output={output.as_posix()}",
            f"--input={input}",
            f"--polygon={utils.test_data_filepath('rectangle.gpkg')}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 66911
