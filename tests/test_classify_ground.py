import subprocess

import numpy as np
import pdal
import pytest
import utils


@pytest.mark.parametrize("algorithm", ["pmf", "smrf"])
def test_classify_ground(algorithm: str, main_copc_file_without_classification: str):

    output_path = utils.test_data_output_filepath(
        f"stadium-utm-classified-ground-{algorithm}.copc.laz", "classify_ground"
    )

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "classify_ground",
            f"--input={main_copc_file_without_classification}",
            f"--output={output_path.as_posix()}",
            f"--algorithm={algorithm}",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()
    number_of_points = pipeline.execute()

    assert number_of_points == 693895

    values = pipeline.arrays[0]["Classification"]
    unique_values = np.unique(values)

    assert unique_values.size == 3
    assert unique_values.tolist() == [0, 1, 2]  # 1: non-ground, 2: ground, 0: never classified


def test_run_with_bad_algorithms():
    input_path = utils.test_data_filepath("stadium-utm.laz")
    output_path = utils.test_data_output_filepath("stadium-utm.las", "classify_ground")

    # missing algorithm
    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "classify_ground",
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
            "classify_ground",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            f"--algorithm={unknown_algorithm}",
        ],
        text=True,
        capture_output=True,
    )

    assert res.returncode == 0
    assert f"unknown algorithm: {unknown_algorithm}" in res.stderr
