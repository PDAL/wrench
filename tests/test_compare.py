import subprocess

import pdal
import pytest
import utils


@pytest.mark.skipif(pdal.info.major <= 2 and pdal.info.minor < 10, reason="Requires PDAL version 2.10 or higher")
def test_compare(autzen_2010_file: str, autzen_2023_file: str):
    """Test compare function"""

    output_path = utils.test_data_output_filepath(f"autzen-compare.copc.laz", "compare")

    res = subprocess.run(
        [
            utils.pdal_wrench_path(),
            "compare",
            f"--input={autzen_2010_file}",
            f"--input-compare={autzen_2023_file}",
            f"--output={output_path.as_posix()}",
            "--subsampling-cell-size=2",
        ],
        check=True,
    )

    assert res.returncode == 0
    assert output_path.exists()

    pipeline = pdal.Reader(filename=output_path.as_posix()).pipeline()
    pipeline.execute()

    dimensions = pipeline.arrays[0].dtype.names

    assert "m3c2_distance" in dimensions
    assert "m3c2_uncertainty" in dimensions
    assert "m3c2_significant" in dimensions
    assert "m3c2_std_dev1" in dimensions
    assert "m3c2_std_dev2" in dimensions
    assert "m3c2_count1" in dimensions
    assert "m3c2_count2" in dimensions

    values = pipeline.arrays[0]["m3c2_distance"]
    assert values.min() == pytest.approx(-3.227012699417537, abs=1e-15)
    assert values.max() == pytest.approx(4.87166403256035, abs=1e-15)
