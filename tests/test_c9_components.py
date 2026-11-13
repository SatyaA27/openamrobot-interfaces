# SPDX-License-Identifier: MIT
"""Additive profile conformance and preserved accepted C9 v1 bytes."""

import hashlib
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class ComponentContractTests(unittest.TestCase):
    def test_registered_schema_fixtures(self):
        import sys

        sys.path.insert(0, str(ROOT / "tools"))
        from lint_schemas import validate_schemas

        self.assertEqual(validate_schemas(ROOT)["status"], "PASS")

    def test_v1_bytes_unchanged(self):
        expected = {
            "schemas/json/c9-lerobot-dataset.schema.json": "692e04693bc738033af1da10f98e029f342497ddaeae4792945f829335f1938e",
            "schemas/yaml/c9-lerobot-dataset-valid.yaml": "e21218b4cd4ce09969ca589cc83e72d46bfa99eee9e197195a56ec1ad22a3e28",
        }
        for path, digest in expected.items():
            self.assertEqual(
                hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest
            )

    def test_proposed_profile_and_explicit_channel_order(self):
        schema = json.loads(
            (ROOT / "schemas/json/c9-component-profile.schema.json").read_text()
        )
        profile = json.loads(
            (ROOT / "profiles/c9/mobile-lift-qpos-v1-proposed.json").read_text()
        )
        Draft202012Validator(schema).validate(profile)
        self.assertEqual(profile["status"], "proposed")
        self.assertEqual(
            profile,
            json.loads(
                (ROOT / "schemas/json/c9-component-profile-valid.json").read_text()
            ),
        )
        self.assertEqual([c["index"] for c in profile["channels"]], list(range(19)))
        self.assertEqual(len({c["name"] for c in profile["channels"]}), 19)
        self.assertEqual(
            set(profile["components"]), {c["component"] for c in profile["channels"]}
        )
        self.assertTrue(all(c["action_source"] is None for c in profile["channels"]))


if __name__ == "__main__":
    unittest.main()
