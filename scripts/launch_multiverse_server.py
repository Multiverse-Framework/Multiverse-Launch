#!/usr/bin/env python3

from multiverse_launch import MultiverseLaunch
from utils import run_subprocess
import os


def main():
    multiverse_launch = MultiverseLaunch()

    server_port = multiverse_launch.multiverse_server["port"]
    multiverse_launch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    multiverse_server_path = os.path.join(multiverse_launch_path, "bin", f"multiverse_server{'.exe' if os.name == 'nt' else ''}")
    run_subprocess([multiverse_server_path, f"tcp://*:{server_port}"])


if __name__ == "__main__":
    main()
