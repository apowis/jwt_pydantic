"""
Updates the version number in pyroject.toml
"""
# TODO: add support for dev releases.
import argparse
from pathlib import Path
import toml

from packaging import version
from packaging.version import Version


def major_bump(version_no: Version) -> Version:
    """
    Bump major version by one.
    """
    return version.parse(f"{version_no.major+1}.0.0")


def minor_bump(version_no: Version) -> Version:
    """
    Bump minor version by one.
    """
    return version.parse(f"{version_no.major}.{version_no.minor+1}.0")


def micro_bump(version_no: Version) -> Version:
    """
    Bump micro version by one.
    """
    return version.parse(f"{version_no.major}.{version_no.minor}.{version_no.micro+1}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bumptype",
        help="Type of version bump",
        choices=["major", "minor", "micro"],
        required=True,
    )
    parser.add_argument(
        "--pyproj_path",
        metavar="pyproject",
        help="Path to pyproject.toml",
        default="./pyproject.toml",
    )
    args = parser.parse_args()
    bump_funcs = {"major": major_bump, "minor": minor_bump, "micro": micro_bump}
    bump_func = bump_funcs[args.bumptype]

    pyproj = Path(args.pyproj_path)
    with pyproj.open("rb") as fh:
        pyproj_dict = toml.load(fh)

    old_version = version.parse(pyproj_dict["project"]["version"])
    new_version = bump_func(old_version)
    pyproj_dict["project"]["version"] = str(new_version)
    with pyproj.open("wb") as fh:  # type: ignore
        toml.dump(pyproj_dict, fh)
