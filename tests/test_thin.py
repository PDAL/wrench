import subprocess
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_path,output_path,point_count",
    [
        (utils.test_data_filepath("stadium-utm.laz"), utils.test_data_filepath("thin.las"), 138779),
        (utils.test_data_filepath("stadium-utm.laz"), utils.test_data_filepath("thin.copc.laz"), 138779),
        (utils.test_data_filepath("stadium-utm.copc.laz"), utils.test_data_filepath("thin-copc-input.laz"), 138779),
        (utils.test_data_filepath("data.vpc"), utils.test_data_filepath("thin-vpc.copc.laz"), 67634),
    ],
)
def test_thin(input_path: Path, output_path: Path, point_count: int):
    """Test thin to las function"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "thin",
            "--mode=every-nth",
            "--step-every-nth=5",
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
