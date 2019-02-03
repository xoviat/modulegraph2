"""
Support code for running inside a virtualenv.

The graph generated by modulegraph2 contains nodes
as if the stdlib is loaded from the original location,
regardless of the tweaks virtualenv performs to
create a working environment
"""
import os
import sys

if hasattr(sys, "real_prefix"):
    virtual_lib = os.path.join(
        os.path.normpath(sys.prefix),
        "lib",
        f"python{sys.version_info[0]}.{sys.version_info[1]}",
    )
    site_packages = os.path.join(virtual_lib, "site-packages")

    def same_contents(path1: str, path2: str) -> bool:
        with open(path1, "rb") as fp:
            contents1 = fp.read()

        with open(path2, "rb") as fp:
            contents2 = fp.read()

        return contents1 == contents2

    # Running inside of a virtualenv environment
    def adjust_path(path: str) -> str:
        # Type annotation and comment are needed because Mypy
        # doesn't understand the additional attributes
        # introduced by virtualenv.
        real_prefix: str = sys.real_prefix  # type: ignore
        norm_prefix = os.path.normpath(sys.prefix)
        norm_path = os.path.normpath(path)

        if not norm_path.startswith(virtual_lib):
            return path

        if norm_path.startswith(site_packages):
            return path

        relpath = os.path.relpath(norm_path, norm_prefix)
        real_path = os.path.join(real_prefix, relpath)

        if os.path.islink(norm_path):
            return os.readlink(norm_path)

        elif os.path.islink(os.path.dirname(norm_path)):
            base = os.path.basename(norm_path)
            dirn = os.path.dirname(norm_path)
            dirn = os.readlink(dirn)
            return os.path.join(dirn, base)

        elif (
            os.path.isfile(norm_path)
            and os.path.isfile(real_path)
            and same_contents(norm_path, real_path)
        ):
            # On Windows virtualenv does not use symlinks, but
            # copies part of the stdlib into the virtual environment.
            return real_path

        elif norm_path == os.path.join(virtual_lib, "site.py"):
            return os.path.join(
                real_prefix,
                "lib",
                f"python{sys.version_info[0]}.{sys.version_info[1]}",
                "site.py",
            )

        elif norm_path == os.path.join(virtual_lib, "distutils"):
            return os.path.join(
                real_prefix,
                "lib",
                f"python{sys.version_info[0]}.{sys.version_info[1]}",
                "distutils",
            )

        elif norm_path == os.path.join(virtual_lib, "distutils", "__init__.py"):
            return os.path.join(
                real_prefix,
                "lib",
                f"python{sys.version_info[0]}.{sys.version_info[1]}",
                "distutils",
                "__init__.py",
            )

        else:
            return path


else:  # pragma: nocover (tests run in virtualenv)

    # Running outside of a virtualenv environment
    def adjust_path(path: str) -> str:
        return path
