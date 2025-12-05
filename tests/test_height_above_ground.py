import itertools
import subprocess
from pathlib import Path

import pdal
import pytest
import utils

# Base test cases with input, output, and expected point count
test_cases = [
    (
        utils.test_data_filepath("stadium-utm.laz"),
        utils.test_data_output_filepath("stadium-utm.las", "height_above_ground"),
        693895,
    ),
    (
        utils.test_data_filepath("stadium-utm.laz"),
        utils.test_data_output_filepath("stadium-utm.copc.laz", "height_above_ground"),
        693895,
    ),
    (
        utils.test_data_filepath("stadium-utm.copc.laz"),
        utils.test_data_output_filepath("stadium-utm-copc-input.copc.laz", "height_above_ground"),
        693895,
    ),
    (
        utils.test_data_filepath("data.vpc"),
        utils.test_data_output_filepath("stadium-utm-vpc.copc.laz", "height_above_ground"),
        338163,
    ),
    (
        utils.test_data_filepath("data_copc.vpc"),
        utils.test_data_output_filepath("stadium-utm-vpc-copc.vpc", "height_above_ground"),
        338163,
    ),
]

# algorithms
algorithms = ["nn", "delaunay"]

# main setting of the height_above_ground
replace_z_values = [True, False]

# Create all combinations for tests
parametrize_values = []
for (input_path, output_path, point_count), algorithm, replace_z in itertools.product(
    test_cases, algorithms, replace_z_values
):
    parametrize_values.append((input_path, output_path, point_count, replace_z, algorithm))


@pytest.mark.parametrize(
    "input_path,output_path,point_count,replace_z,algorithm",
    parametrize_values,
)
def test_height_above_ground_files(
    input_path: Path, output_path: Path, point_count: int, replace_z: bool, algorithm: str
):
    """Test height_above_ground function"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "height_above_ground",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            f"--algorithm={algorithm}",
            f"--replace-z={str(replace_z).lower()}",
        ],
    )

    assert res.returncode == 0

    assert output_path.exists()

    if not output_path.name.endswith(".copc.laz") and output_path.suffix.lower() in [".laz", ".las"]:
        pipeline = pdal.Reader(filename=output_path.as_posix(), use_eb_vlr=True).pipeline()
    else:
        pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    dimensions = pipeline.arrays[0].dtype.names

    # check dimensions
    assert "HeightAboveGround" in dimensions

    # for non vpc files check values (vpc have different values)
    if input_path.suffix.lower() != ".vpc" and algorithm == "nn":
        if replace_z:
            values = pipeline.arrays[0]["Z"]
            assert min(values) == pytest.approx(-0.85, abs=0.01)
            assert max(values) == pytest.approx(43.82, abs=0.01)
        else:
            values = pipeline.arrays[0]["Z"]
            assert min(values) == pytest.approx(126.64, abs=0.01)
            assert max(values) == pytest.approx(182.32, abs=0.01)
            values = pipeline.arrays[0]["HeightAboveGround"]
            assert min(values) == pytest.approx(-0.85, abs=0.01)
            assert max(values) == pytest.approx(43.82, abs=0.01)

    assert number_of_points == point_count


def test_run_with_bad_algorithms():
    input_path = utils.test_data_filepath("stadium-utm.laz")
    output_path = utils.test_data_output_filepath("stadium-utm.las", "height_above_ground")

    # missing algorithm
    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "height_above_ground",
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
            "height_above_ground",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            f"--algorithm={unknown_algorithm}",
        ],
        text=True,
        capture_output=True,
    )

    assert res.returncode == 0
    assert f"unknown algorithm: {unknown_algorithm}" in res.stderr
