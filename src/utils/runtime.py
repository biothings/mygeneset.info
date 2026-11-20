"""Report the current process's Python runtime."""

import os
import platform
import sys
import sysconfig

import biothings


def runtime_info():
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "free_threaded": sysconfig.get_config_var("Py_GIL_DISABLED") == 1,
        "gil_enabled": sys._is_gil_enabled(),
        "biothings_version": biothings.__version__,
        "pid": os.getpid(),
    }


def require_free_threading():
    info = runtime_info()
    if not info["free_threaded"] or info["gil_enabled"]:
        raise RuntimeError("Use free-threaded Python 3.14 (python3.14t) with the GIL disabled.")
    return info
