import shutil
from pathlib import Path

import pdal


def test_data_folder() -> Path:
    """Return data folder for tests"""
    return Path(__file__).parent / "data"


def test_data_filepath(file_name: str) -> Path:
    """Return path to file in data folder"""
    return test_data_folder() / file_name


def test_data_output_filepath(file_name: str, subfolder: str) -> Path:
    """Return path to file in data folder"""
    folder = test_data_folder() / "output"
    if subfolder:
        folder = folder / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    return folder / file_name


def pdal_wrench_path() -> str:
    """Return path to pdal_wrench executable"""
    executable_name = "pdal_wrench"

    # check system executable exists
    if shutil.which(executable_name):
        return executable_name

    # try to look in build directory
    path_pdal_wrench = Path(__file__).parent.parent / "build" / executable_name

    if not path_pdal_wrench.exists():
        raise FileNotFoundError(path_pdal_wrench)

    return path_pdal_wrench.as_posix()


def run_change_dim_value_pipeline(input_file: Path, output_file: Path, dim_name: str, dim_value: float):
    """
    Run filter assign pipeline on input file and save to output file.
    """
    pipeline = pdal.Pipeline()

    # Read input file
    pipeline |= pdal.Reader(filename=input_file.as_posix())

    # Apply assign filter
    pipeline |= pdal.Filter.assign(value=[f"{dim_name} = {dim_value}"])

    # Write output with HeightAboveGround dimension
    pipeline |= pdal.Writer(filename=output_file.as_posix(), forward="all")

    # Execute the pipeline
    count = pipeline.execute()

    assert count > 0
