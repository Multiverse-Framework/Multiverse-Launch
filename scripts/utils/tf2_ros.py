#!/usr/bin/env python3

import subprocess

from .utils import run_subprocess

def run_tf2_ros(node_name, node_params) -> subprocess.Popen:
    cmd = [
        "ros2",
        "run",
        "tf2_ros",
        node_name,
        *node_params,
    ]
    cmd = [str(arg) for arg in cmd]
    return run_subprocess(cmd)
