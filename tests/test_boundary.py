import subprocess
from pathlib import Path

import pytest
import utils


@pytest.mark.parametrize(
    "input_path,output_path",
    [
        (utils.test_data_filepath("stadium-utm.laz"), utils.test_data_filepath("boundary-laz.gpkg")),
        (utils.test_data_filepath("stadium-utm.copc.laz"), utils.test_data_filepath("boundary_copc.gpkg")),
        (utils.test_data_filepath("data.vpc"), utils.test_data_filepath("boundary-vpc.gpkg")),
    ],
)
def test_boundary(input_path: Path, output_path: Path):
    """Test boundary on las function"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "boundary",
            f"--output={output_path.as_posix()}",
            f"--input={input_path.as_posix()}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()
