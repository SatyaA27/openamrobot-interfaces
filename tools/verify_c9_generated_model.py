#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Expand the pinned combined model and verify Proposed C9 mappings (no ROS graph)."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


def git(root, *args):
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={root}", *args], cwd=root, text=True
    ).strip()


def check_urdf(root, profile, hardware_profile):
    """Compare generated limits/types/interfaces; data validation grants no motion."""
    by_name = {j.get("name"): j for j in root.findall("./joint")}
    for channel in profile["channels"]:
        if channel["component"] == "base":
            continue
        name = channel["joint"]
        joint = by_name.get(name)
        if joint is None:
            raise ValueError(f"C9 joint missing from generated model: {name}")
        expected_type = "prismatic" if channel["component"] == "lift" else "revolute"
        expected_unit = "m" if expected_type == "prismatic" else "rad"
        if joint.get("type") != expected_type or channel["unit"] != expected_unit:
            raise ValueError(f"C9 joint type/unit differs from generated model: {name}")
        limit = joint.find("limit")
        if limit is None or channel["range"] != [
            float(limit.get("lower")),
            float(limit.get("upper")),
        ]:
            raise ValueError(f"C9 range differs from generated model: {name}")
    lift = by_name["lift_joint"]
    if [float(lift.find("limit").get(k)) for k in ("lower", "upper")] != profile[
        "model"
    ]["lift_range_m"]:
        raise ValueError("C9 lift model range differs from generated URDF")
    commands = root.findall(
        "./ros2_control/joint[@name='lift_joint']/command_interface"
    )
    if hardware_profile == "real":
        if (
            commands
            or float(lift.find("limit").get("effort"))
            or float(lift.find("limit").get("velocity"))
        ):
            raise ValueError("Real profile unexpectedly authorizes a ROS lift command")
    elif len(commands) != 1 or commands[0].get("name") != "position":
        raise ValueError(
            "Mock/Gazebo profile lacks the separate lift position interface"
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("upperbody", "platform", "openarm"):
        parser.add_argument(f"--{key}-root", type=Path, required=True)
    parser.add_argument(
        "--interfaces-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    profile = json.loads(
        (
            args.interfaces_root / "profiles/c9/mobile-lift-qpos-v1-proposed.json"
        ).read_text()
    )
    upperbody = args.upperbody_root.resolve()
    pins = yaml.safe_load(
        (
            upperbody
            / "ros2/src/openamrobot_upperbody_description/config/upstream_pins.yaml"
        ).read_text()
    )["pins"]
    roots = {
        "upperbody": upperbody,
        "platform": args.platform_root.resolve(),
        "openarm": args.openarm_root.resolve(),
    }
    expected = {
        "upperbody": profile["model"]["commit"],
        "platform": pins["openamr_platform_sw"],
        "openarm": pins["openarm_description"],
    }
    for name, root in roots.items():
        if git(root, "rev-parse", "HEAD") != expected[name] or git(
            root, "status", "--porcelain"
        ):
            raise ValueError(
                f"Generated-model verification requires clean pinned {name} source"
            )
    if not shutil.which("xacro") or not shutil.which("check_urdf"):
        raise RuntimeError("Source ROS Jazzy and install xacro/liburdfdom-tools")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="oa-c9-model-prefix-") as temporary:
        prefix = Path(temporary)
        index = prefix / "share/ament_index/resource_index/packages"
        index.mkdir(parents=True)
        packages = {
            "openamrobot_upperbody_description": upperbody
            / "ros2/src/openamrobot_upperbody_description",
            "openamrobot_description": roots["platform"]
            / "ros2/src/openamrobot_description",
            "openarm_description": roots["openarm"],
        }
        for name, package in packages.items():
            (index / name).touch()
            (prefix / "share" / name).symlink_to(package)
        env = {
            **os.environ,
            "AMENT_PREFIX_PATH": str(prefix)
            + os.pathsep
            + os.environ.get("AMENT_PREFIX_PATH", ""),
        }
        for hardware in ("mock", "gazebo", "real"):
            path = output / f"combined-{hardware}.urdf"
            command = [
                "xacro",
                str(
                    packages["openamrobot_upperbody_description"]
                    / "urdf/combined_robot.xacro"
                ),
                f"hardware_profile:={hardware}",
            ]
            generated = subprocess.run(
                command, env=env, capture_output=True, text=True, timeout=60, check=True
            )
            path.write_text(generated.stdout)
            (output / f"xacro-{hardware}.log").write_text(generated.stderr)
            checked = subprocess.run(
                ["check_urdf", str(path)],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            (output / f"check-urdf-{hardware}.log").write_text(
                checked.stdout + checked.stderr
            )
            check_urdf(ET.fromstring(generated.stdout), profile, hardware)
    report = {
        "status": "PASS",
        "purpose": "Generated model/C9 consistency only; no live simulation or hardware",
        "source_commits": expected,
        "profiles_checked": ["mock", "gazebo", "real"],
        "profile_sha256": hashlib.sha256(
            (
                args.interfaces_root / "profiles/c9/mobile-lift-qpos-v1-proposed.json"
            ).read_bytes()
        ).hexdigest(),
        "urdf_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.glob("*.urdf")
        },
        "physical_acceptance": "NOT_VERIFIED",
    }
    (output / "generated-model-manifest.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(
        "PASS: mock/Gazebo/real generated models match Proposed C9 names/types/ranges; real lift has no command interface"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
