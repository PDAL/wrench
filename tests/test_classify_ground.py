import subprocess

import numpy as np
import pdal
import pytest
import utils


def test_classify_ground(main_copc_file_without_classification: str):

    output_path = utils.test_data_output_filepath(f"stadium-utm-classified-ground.copc.laz", "classify_ground")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "classify_ground",
            f"--input={main_copc_file_without_classification}",
            f"--output={output_path.as_posix()}",
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
