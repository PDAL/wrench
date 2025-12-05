import subprocess
from pathlib import Path

import numpy as np
import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_path,output_path",
    [
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("filter_noise.las", "filter_noise"),
        ),
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("filter_noise.copc.laz", "filter_noise"),
        ),
        (
            utils.test_data_filepath("stadium-utm.copc.laz"),
            utils.test_data_output_filepath("filter_noise-copc-input.copc.laz", "filter_noise"),
        ),
        (
            utils.test_data_filepath("data.vpc"),
            utils.test_data_output_filepath("filter_noise-vpc.copc.laz", "filter_noise"),
        ),
        (
            utils.test_data_filepath("data_copc.vpc"),
            utils.test_data_output_filepath("filter_noise.vpc", "filter_noise"),
        ),
    ],
)
def test_filter_noise_files(input_path: Path, output_path: Path):
    """Test filter noise function"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "filter_noise",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            "--algorithm=statistical",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    pipeline.execute()

    values = pipeline.arrays[0]["Classification"]
    unique_values = np.unique(values)

    assert unique_values.size == 3
    assert unique_values.tolist() == [1, 2, 7]  # 1: non-ground, 2: ground, 7: noise


def test_filter_noise_with_bad_algorithms():
    input_path = utils.test_data_filepath("stadium-utm.laz")
    output_path = utils.test_data_output_filepath("stadium-utm.las", "filter_noise")

    # missing algorithm
    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "filter_noise",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
        ],
        text=True,
        capture_output=True,
    )
    assert res.returncode == 0
    assert "missing algorithm" in res.stderr

    # unknown algorithm
    unknown_algorithm = "invalid_algorithm"

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "filter_noise",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            f"--algorithm={unknown_algorithm}",
        ],
        text=True,
        capture_output=True,
    )

    assert res.returncode == 0
    assert f"unknown algorithm: {unknown_algorithm}" in res.stderr
