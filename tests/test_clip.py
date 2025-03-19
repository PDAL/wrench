import subprocess

import numpy as np
import pdal
import utils


def test_clip(main_laz_file: str):
    """Test merge las function"""

    clipped_las_file = utils.test_data_filepath("data_clipped_test.las")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "clip",
            f"--output={clipped_las_file.as_posix()}",
            f"--input={main_laz_file}",
            f"--polygon={utils.test_data_filepath('rectangle1.gpkg')}",
        ],
        check=True,
    )

    assert res.returncode == 0

    pipeline = pdal.Reader.las(filename=clipped_las_file.as_posix()).pipeline()

    number_of_points = pipeline.execute()

    assert number_of_points == 66832

    # points as numpy array
    array = pipeline.arrays[0]

    # all points
    assert isinstance(array, np.ndarray)

    # first point
    assert isinstance(array[0], np.void)
    assert len(array[0]) == 20
    assert isinstance(array[0]["X"], np.float64)
    assert isinstance(array[0]["Y"], np.float64)
    assert isinstance(array[0]["Z"], np.float64)
    assert isinstance(array[0]["Intensity"], np.uint16)
