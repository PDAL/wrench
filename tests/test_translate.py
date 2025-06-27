import subprocess
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_type,output,point_count",
    [
        ("main_laz", utils.test_data_filepath("translate.las"), 693895),
        ("main_laz", utils.test_data_filepath("translate.copc.laz"), 693895),
        ("main_copc", utils.test_data_filepath("translate-copc-input.laz"), 693895),
        ("vpc_file", utils.test_data_filepath("translate-vpc.copc.laz"), 338163),
        ("vpc_copc_file", utils.test_data_filepath("translate.vpc"), 338163),
    ],
)
def test_translate_laz_to_las(
    input_type: str,
    output: Path,
    point_count: int,
    main_laz_file: str,
    main_copc_file: str,
    vpc_file: str,
    vpc_copc_file: str,
):
    """Test translate las function"""

    if input_type == "main_laz":
        input = main_laz_file
    elif input_type == "main_copc":
        input = main_copc_file
    elif input_type == "vpc_file":
        input = vpc_file
    elif input_type == "vpc_copc_file":
        input = vpc_copc_file
    else:
        assert False, "Invalid input type"

    print(f"{utils.pdal_wrench_path()} translate --input={input} --output={output.as_posix()}")
    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={input}",
            f"--output={output.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output.exists()

    pipeline = pdal.Reader(filename=output.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == point_count
