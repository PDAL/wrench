import subprocess
from pathlib import Path

import numpy as np
import pdal
import pytest
import utils


def test_filter_noise_radius():
    """Test filter noise function with radius on vpc"""

    input_path = utils.test_data_filepath("data_copc.vpc")
    output_path = utils.test_data_output_filepath("filter_noise.vpc", "filter_noise")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "filter_noise",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            "--algorithm=radius",
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

    nonground_point = pipeline.arrays[0][
        (pipeline.arrays[0]["X"] == 494423.10000000003) & (pipeline.arrays[0]["Y"] == 4878521.0200000005)
    ]
    assert nonground_point["Classification"] == 1  # non-ground
    assert nonground_point["Z"] == 128.81

    ground_point = pipeline.arrays[0][
        (pipeline.arrays[0]["X"] == 494367.93000000005) & (pipeline.arrays[0]["Y"] == 4878517.25)
    ]
    assert ground_point["Classification"] == 2  # ground
    assert ground_point["Z"] == 128.63

    noise_point = pipeline.arrays[0][(pipeline.arrays[0]["X"] == 494414.28) & (pipeline.arrays[0]["Y"] == 4878485.96)]
    assert noise_point["Classification"] == 7  # noise
    assert noise_point["Z"] == 129.32


def test_filter_noise_statistical():
    """Test filter noise function with statistical on laz"""

    input_path = utils.test_data_filepath("stadium-utm.laz")
    output_path = utils.test_data_output_filepath("filter_noise.copc.laz", "filter_noise")

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

    nonground_point = pipeline.arrays[0][
        (pipeline.arrays[0]["X"] == 494629.19000000006) & (pipeline.arrays[0]["Y"] == 4878441.75)
    ]
    assert nonground_point["Classification"] == 1  # non-ground
    assert nonground_point["Z"] == 129.14

    ground_point = pipeline.arrays[0][(pipeline.arrays[0]["X"] == 494657.37) & (pipeline.arrays[0]["Y"] == 4878358.05)]
    assert ground_point["Classification"] == 2  # ground
    assert ground_point["Z"] == 130.15999999999997

    noise_point = pipeline.arrays[0][(pipeline.arrays[0]["X"] == 494650.53) & (pipeline.arrays[0]["Y"] == 4878439.98)]
    assert noise_point["Classification"] == 7  # noise
    assert noise_point["Z"] == 140.09999999999997


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


def test_filter_noise_statistical_remove_noise_points():
    """Test filter noise function with statistical on laz and removal of noise points"""

    input_path = utils.test_data_filepath("stadium-utm.laz")
    output_path = utils.test_data_output_filepath("filter_noise_remove_points.laz", "filter_noise")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "filter_noise",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            "--algorithm=statistical",
            "--remove-noise-points=true",
        ],
        check=True,
    )

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    pipeline.execute()

    values = pipeline.arrays[0]["Classification"]
    unique_values = np.unique(values)

    assert unique_values.size == 2
    assert unique_values.tolist() == [1, 2]  # 1: non-ground, 2: ground

    nonground_point = pipeline.arrays[0][
        (pipeline.arrays[0]["X"] == 494629.19000000006) & (pipeline.arrays[0]["Y"] == 4878441.75)
    ]
    assert nonground_point["Classification"] == 1  # non-ground
    assert nonground_point["Z"] == 129.14

    ground_point = pipeline.arrays[0][(pipeline.arrays[0]["X"] == 494657.37) & (pipeline.arrays[0]["Y"] == 4878358.05)]
    assert ground_point["Classification"] == 2  # ground
    assert ground_point["Z"] == 130.15999999999997

    noise_point = pipeline.arrays[0][(pipeline.arrays[0]["X"] == 494650.53) & (pipeline.arrays[0]["Y"] == 4878439.98)]
    assert noise_point.size == 0
