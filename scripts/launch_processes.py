#!/usr/bin/env python3

import os
import sys
import re
import subprocess
from typing import List, Dict, Any
import time

from multiverse_launch import MultiverseLaunch
from utils import find_files, run_subprocess

class MultiverseProcessesLaunch(MultiverseLaunch):
    def __init__(self):
        super().__init__()

    def run_processes(self) -> List[subprocess.Popen]:
        processes: List[subprocess.Popen] = []
        for process in self.processes:
            for process_name, process_args in process.items():
                if process_name.endswith(".py"):
                    process_path = find_files(self.resources_paths, process_name)
                    cmd = [f"{sys.executable}", process_path]
                elif process_name == "sleep":
                    print(f"Sleeping for {process_args} seconds")
                    time.sleep(process_args)
                    continue
                else:
                    cmd = [f"{process_name}"]
                if isinstance(process_args, dict):
                    for arg_name, arg_value in process_args.items():
                        if arg_name == "data_path":
                            arg_value = find_files(self.resources_paths, arg_value)
                        elif isinstance(arg_value, list):
                            arg_value = ",".join(arg_value)
                        if isinstance(arg_value, bool):
                            if arg_value:
                                cmd.append(f"--{arg_name}")
                        else:
                            cmd.append(f"--{arg_name}={arg_value}")
                else:
                    cmd.append(f"{process_args}")
                process = run_subprocess(cmd)
                processes.append(process)
        return processes

    @property
    def processes(self) -> Dict[str, Any]:
        return self.data.get("processes", {})


def main():
    multiverse_launch = MultiverseProcessesLaunch()
    multiverse_launch.run_processes()


if __name__ == "__main__":
    main()