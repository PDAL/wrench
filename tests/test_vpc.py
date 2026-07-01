import json
import subprocess
import tempfile
from pathlib import Path

import pytest
import utils


def test_build_vpc_absolute_paths(laz_files):
    """Paths stored in VPC use absolute paths when --use-absolute-paths is passed."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_vpc = Path(tmp_dir) / "out.vpc"

        res = subprocess.run(
            [
                utils.pdal_wrench_path(),
                "build_vpc",
                "--use-absolute-paths",
                f"--output={output_vpc.as_posix()}",
                *laz_files,
            ],
            check=True,
        )

        assert res.returncode == 0
        assert output_vpc.exists()

        data = json.loads(output_vpc.read_text())
        assert data["type"] == "FeatureCollection"

        for feature in data["features"]:
            for asset in feature["assets"].values():
                href = asset["href"]
                assert Path(href).is_absolute(), f"Expected absolute path, got: {href}"


def test_build_vpc_relative_paths_default(laz_files):
    """Paths stored in VPC are relative by default (no --absolute-paths)."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_vpc = Path(tmp_dir) / "out.vpc"

        res = subprocess.run(
            [
                utils.pdal_wrench_path(),
                "build_vpc",
                f"--output={output_vpc.as_posix()}",
                *laz_files,
            ],
            check=True,
        )

        assert res.returncode == 0
        assert output_vpc.exists()

        data = json.loads(output_vpc.read_text())
        assert data["type"] == "FeatureCollection"

        for feature in data["features"]:
            data_href = feature["assets"]["data"]["href"]
            assert data_href.startswith("./"), f"Expected relative path starting with ./, got: {data_href}"
