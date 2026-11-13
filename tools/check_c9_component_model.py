#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Explicit source-model consistency test; generated-URDF execution remains separate."""

import argparse
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--upperbody-root", type=Path, required=True)
parser.add_argument(
    "--interfaces-root", type=Path, default=Path(__file__).resolve().parents[1]
)
args = parser.parse_args()


class ModelConsistency(unittest.TestCase):
    def test_pinned_model_names_stroke_groups_and_order(self):
        root = Path(args.upperbody_root)
        import subprocess

        profile = json.loads(
            (
                args.interfaces_root / "profiles/c9/mobile-lift-qpos-v1-proposed.json"
            ).read_text()
        )
        self.assertEqual(
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip(),
            profile["model"]["commit"],
        )
        package = root / "ros2/src/openamrobot_upperbody_description"
        config = yaml.safe_load(
            (package / "config/upperbody_configuration.yaml").read_text()
        )
        self.assertEqual(
            config["column"]["dold_v4_350"]["stroke"],
            profile["model"]["lift_range_m"][1],
        )
        tree = ET.parse(package / "urdf/openamrobot_upperbody.xacro")
        joint = tree.find(".//joint[@name='lift_joint']")
        self.assertEqual(joint.get("type"), "prismatic")
        self.assertEqual(joint.find(".//limit").get("lower"), "0.0")
        self.assertEqual(joint.find(".//limit").get("upper"), "${col['stroke']}")
        controllers = yaml.safe_load(
            (
                root
                / "ros2/src/openamrobot_upperbody_control/config/arm_controllers.yaml"
            ).read_text()
        )
        for side in ("left", "right"):
            arm = controllers[f"{side}_arm_controller"]["ros__parameters"]["joints"]
            expected = [
                c["joint"]
                for c in profile["channels"]
                if c["component"] == f"{side}_arm"
            ]
            self.assertEqual(arm, expected)
            self.assertEqual(
                controllers[f"{side}_gripper_controller"]["ros__parameters"]["joint"],
                f"openarm_{side}_finger_joint1",
            )
        srdf = ET.parse(
            root / "ros2/src/openamrobot_upperbody_moveit/config/openamrobot.srdf"
        )
        self.assertEqual(
            srdf.find(".//group[@name='lift']/joint").get("name"), "lift_joint"
        )
        for name in ("left_arm", "right_arm", "both_arms"):
            self.assertFalse(
                any(
                    j.get("name") == "lift_joint"
                    for j in srdf.findall(f".//group[@name='{name}']/joint")
                )
            )


result = unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromTestCase(ModelConsistency)
)
raise SystemExit(0 if result.wasSuccessful() else 1)
