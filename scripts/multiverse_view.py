#!/usr/bin/env python3

import argparse
import os
from typing import Tuple
from enum import Enum
import time

ROS_DISTRO = os.environ.get("ROS_DISTRO")
USING_ROS1 = ROS_DISTRO in {"noetic", "melodic", "kinetic"}
USING_ROS2 = ROS_DISTRO in {"foxy", "galactic", "iron", "humble", "jazzy"}
if not USING_ROS1 and not USING_ROS2:
    raise ImportError(f"ROS_DISTRO {ROS_DISTRO} unknown.")


class Interface(Enum):
    ROS1 = "ROS1"
    ROS2 = "ROS2"


if USING_ROS1:
    INTERFACE = Interface.ROS1
elif USING_ROS2:
    INTERFACE = Interface.ROS2
else:
    raise ValueError(f"Invalid interface")


def get_scene_file() -> Tuple[str, str]:
    parser = argparse.ArgumentParser(
        prog="multiverse_view", description="View the scene in the multiverse framework"
    )
    parser.add_argument(
        "--scene_file",
        type=str,
        required=True,
        help="Path to scene file",
    )
    parser.add_argument(
        "--resource_path",
        type=str,
        required=False,
        help="Path to resource folder",
    )
    args = parser.parse_args()
    if args.resource_path is None:
        args.resource_path = os.path.dirname(args.scene_file)
    return args.scene_file, args.resource_path


class MultiverseView:
    scene_file: str
    data: str

    def __init__(self):
        self._scene_file, self._resource_path = get_scene_file()
        self._data = self.read_scene_file()
        self.processes = []

    def read_scene_file(self) -> str:
        with open(self.scene_file) as f:
            data = f.read()
        return data

    def view(self):
        file_extension = os.path.splitext(self.scene_file)[1]
        if file_extension == ".urdf":
            self.view_urdf()
        elif file_extension == ".xml":
            self.view_mjcf()
        elif file_extension in [".usda", "usd", "usdc"]:
            self.view_usd()
        else:
            raise NotImplementedError(f"Cannot view {file_extension} files yet")
        try:
            while True:
                for proc in self.processes:
                    if proc.poll() is not None:  # This one has finished
                        print(f"Process {proc.pid} has exited.")
                        
                        # Kill all other processes
                        for other in self.processes:
                            if other != proc and other.poll() is None:
                                print(f"Killing process {other.pid}")
                                other.terminate()
                                other.kill()

                        # Optional: break outer loop if only one exit triggers cleanup
                        raise SystemExit()

                time.sleep(0.5)

        except KeyboardInterrupt:
            for proc in self.processes:
                if proc.poll() is None:
                    proc.terminate()

    def view_urdf(self):
        import xml.etree.ElementTree as ET

        tree = ET.ElementTree(ET.fromstring(self.data))
        root = tree.getroot()

        transmission_tags = root.findall(".//transmission")
        for tag in transmission_tags:
            root.remove(tag)

        self._data = ET.tostring(root, encoding="unicode")

        from urdf_parser_py import urdf

        fix_frame = urdf.URDF.from_xml_string(self.data).get_root()
        if INTERFACE == Interface.ROS1:
            import rospy
            import rospkg
            from utils import (
                run_rviz,
                run_joint_state_publisher_gui,
                run_robot_state_publisher,
                is_roscore_running,
                run_subprocess,
            )

            if not is_roscore_running():
                process = run_subprocess(["roscore"])
                self.processes.append(process)

            rospy.init_node(name="multiverse_view")

            process = run_joint_state_publisher_gui()
            self.processes.append(process)

            process = run_robot_state_publisher()
            self.processes.append(process)

            ros_package = rospkg.RosPack()
            rviz_pkg_path = ros_package.get_path("rviz")
            rviz_dict = {
                "robot_descriptions": {"robot_description": self.scene_file},
                "fix_frame": fix_frame,
            }
            mesh_abspath_prefix = os.path.relpath("/", rviz_pkg_path)
            mesh_abspath_prefix = os.path.join(
                "package://rviz", mesh_abspath_prefix
            )
            process = run_rviz(
                rviz_dict=rviz_dict,
                resources_paths=[self.resource_path],
                mesh_abspath_prefix=mesh_abspath_prefix,
                rviz_pkg_path=rviz_pkg_path,
            )
            self.processes.append(process)

        elif INTERFACE == Interface.ROS2:
            from utils import (
                run_rviz2,
                run_joint_state_publisher_gui2,
                run_robot_state_publisher2,
            )

            process = run_joint_state_publisher_gui2(robot_file_path=self.scene_file)
            self.processes.append(process)

            process = run_robot_state_publisher2(robot_file_string=self.data)
            self.processes.append(process)

            rviz2_dict = {
                "robot_descriptions": {"robot_description": self.scene_file},
                "fix_frame": fix_frame,
            }
            process = run_rviz2(
                rviz2_dict=rviz2_dict, resources_paths=[self.resource_path]
            )
            self.processes.append(process)

    def view_mjcf(self):
        from utils import run_subprocess

        process = run_subprocess(["simulate", self.scene_file])
        self.processes.append(process)

    def view_usd(self):
        from utils import run_subprocess

        process = run_subprocess(["usdview", self.scene_file])
        self.processes.append(process)

    @property
    def scene_file(self) -> str:
        return self._scene_file

    @property
    def resource_path(self) -> str:
        return self._resource_path

    @property
    def data(self) -> str:
        return self._data


if __name__ == "__main__":
    multiverse_view = MultiverseView()
    multiverse_view.view()
