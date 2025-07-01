import subprocess
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_path,output_path,point_count",
    [
        (utils.test_data_filepath("stadium-utm.laz"), utils.test_data_filepath("translate.las"), 693895),
        (utils.test_data_filepath("stadium-utm.laz"), utils.test_data_filepath("translate.copc.laz"), 693895),
        (
            utils.test_data_filepath("stadium-utm.copc.laz"),
            utils.test_data_filepath("translate-copc-input.copc.laz"),
            693895,
        ),
        (utils.test_data_filepath("data.vpc"), utils.test_data_filepath("translate-vpc.copc.laz"), 338163),
        (utils.test_data_filepath("data_copc.vpc"), utils.test_data_filepath("translate.vpc"), 338163),
    ],
)
def test_translate_files(input_path: Path, output_path: Path, point_count: int):
    """Test translate function"""

    print(f"{utils.pdal_wrench_path()} translate --input={input_path} --output={output_path.as_posix()}")
    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "translate",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == point_count
