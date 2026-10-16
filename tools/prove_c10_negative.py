#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prove a specific corruption test detects reverting affine arithmetic QA.

Only a temporary source copy is mutated. The production checkout and fixture
expectations are unchanged. Exit zero means the expected failure was observed.
"""

from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
TARGET = "test_c10_dataset.C10SemanticTests.test_reject_affine_arithmetic"
CHILD = """
import importlib.util
from pathlib import Path
import sys
import unittest
root, source, expected = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(root / 'tools'))
sys.path.insert(0, str(root / 'tests'))
spec = importlib.util.spec_from_file_location('c10_semantics', source)
module = importlib.util.module_from_spec(spec)
sys.modules['c10_semantics'] = module
spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromName(sys.argv[4])
result = unittest.TextTestRunner(verbosity=2).run(suite)
valid = (result.testsRun == 1 and not result.errors and not result.skipped
         and len(result.failures) == int(expected))
raise SystemExit(0 if valid else 1)
"""


def main():
    source = ROOT / "tools/c10_semantics.py"
    original = source.read_text()
    rule = 'calculated == stamp.get("mapped_authoritative_ns")'
    if original.count(rule) != 1:
        raise SystemExit("FAIL: arithmetic rule changed; update the precise revert experiment")
    subprocess.run([sys.executable,"-c",CHILD,str(ROOT),str(source),"0",TARGET],check=True)
    with tempfile.TemporaryDirectory(prefix="c10-reverted-rule-") as directory:
        reverted = Path(directory) / source.name
        reverted.write_text(original.replace(rule,"True  # deliberately reverted arithmetic comparison\n                                 "))
        subprocess.run([sys.executable,"-c",CHILD,str(ROOT),str(reverted),"1",TARGET],check=True)
    if source.read_text() != original:
        raise SystemExit("FAIL: source checkout changed during the experiment")
    print("PASS: unchanged negative test passed on current code and failed exactly once on the reverted arithmetic rule; checkout preserved.")


if __name__ == "__main__":
    main()
