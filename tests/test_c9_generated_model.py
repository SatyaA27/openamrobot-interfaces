# SPDX-License-Identifier: MIT
"""Unit regressions for generated-model checks; actual expansion has a separate CI job."""

import copy
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verify_c9_generated_model import check_urdf


class GeneratedModelChecks(unittest.TestCase):
    def setUp(self):
        self.profile = json.loads(
            (ROOT / "profiles/c9/mobile-lift-qpos-v1-proposed.json").read_text()
        )
        self.root = ET.Element("robot")
        for c in self.profile["channels"]:
            if c["component"] == "base":
                continue
            kind = "prismatic" if c["component"] == "lift" else "revolute"
            joint = ET.SubElement(self.root, "joint", name=c["joint"], type=kind)
            ET.SubElement(
                joint,
                "limit",
                lower=str(c["range"][0]),
                upper=str(c["range"][1]),
                effort="0",
                velocity="0",
            )

    def test_real_observation_does_not_imply_command_authority(self):
        check_urdf(self.root, self.profile, "real")

    def test_changed_lift_range_fails(self):
        self.root.find("./joint[@name='lift_joint']/limit").set("upper", "0.351")
        with self.assertRaisesRegex(ValueError, "range differs.*lift_joint"):
            check_urdf(self.root, self.profile, "real")

    def test_changed_gripper_range_fails(self):
        self.root.find("./joint[@name='openarm_right_finger_joint1']/limit").set(
            "lower", "0"
        )
        with self.assertRaisesRegex(ValueError, "range differs.*right_finger"):
            check_urdf(self.root, self.profile, "real")

    def test_lift_units_must_be_metres(self):
        profile = copy.deepcopy(self.profile)
        next(c for c in profile["channels"] if c["component"] == "lift")["unit"] = "mm"
        with self.assertRaisesRegex(ValueError, "type/unit differs.*lift_joint"):
            check_urdf(self.root, profile, "real")

    def test_real_ros_lift_command_is_rejected(self):
        control = ET.SubElement(self.root, "ros2_control")
        joint = ET.SubElement(control, "joint", name="lift_joint")
        ET.SubElement(joint, "command_interface", name="position")
        with self.assertRaisesRegex(ValueError, "Real profile unexpectedly authorizes"):
            check_urdf(self.root, self.profile, "real")
        check_urdf(self.root, self.profile, "mock")
        check_urdf(self.root, self.profile, "gazebo")


if __name__ == "__main__":
    unittest.main()
