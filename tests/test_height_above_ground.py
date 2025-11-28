import subprocess
from pathlib import Path

import pdal
import pytest
import utils


@pytest.mark.parametrize(
    "input_path,output_path,point_count,replace_z",
    [
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("stadium-utm.las", "height_above_ground"),
            693895,
            True,
        ),
        (
            utils.test_data_filepath("stadium-utm.laz"),
            utils.test_data_output_filepath("stadium-utm.copc.laz", "height_above_ground"),
            693895,
            False,
        ),
        (
            utils.test_data_filepath("stadium-utm.copc.laz"),
            utils.test_data_output_filepath("stadium-utm-copc-input.copc.laz", "height_above_ground"),
            693895,
            False,
        ),
        # (
        #     utils.test_data_filepath("data.vpc"),
        #     utils.test_data_output_filepath("stadium-utm-vpc.copc.laz", "height_above_ground"),
        #     338163,
        #     False,
        # ),
        (
            utils.test_data_filepath("data_copc.vpc"),
            utils.test_data_output_filepath("stadium-utm-vpc-copc.vpc", "height_above_ground"),
            338163,
            False,
        ),
    ],
)
def test_height_above_ground_files(input_path: Path, output_path: Path, point_count: int, replace_z: bool):
    """Test height_above_ground function"""

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "height_above_ground",
            f"--input={input_path.as_posix()}",
            f"--output={output_path.as_posix()}",
            f"--replace-z={str(replace_z).lower()}",
        ],
        check=True,
    )
    print(res.stdout)

    assert res.returncode == 0

    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()
    number_of_points = pipeline.execute()

    dimensions = pipeline.arrays[0].dtype.names

    # check dimensions
    if replace_z:
        assert "HeightAboveGround" not in dimensions
    else:
        assert "HeightAboveGround" in dimensions

    # for non vpc files check values (vpc have different values)
    if input_path.suffix.lower() != ".vpc":
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
