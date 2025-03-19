import shutil
from pathlib import Path


def test_data_folder() -> Path:
    """Return data folder for tests"""
    return Path(__file__).parent / "data"


def test_data_filepath(file_name: str) -> Path:
    """Return path to file in data folder"""
    return test_data_folder() / file_name


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
