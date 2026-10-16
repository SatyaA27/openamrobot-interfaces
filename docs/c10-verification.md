<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# C10 execution evidence — 16 October 2026

**SYNTHETIC QA PASS. REAL_EPISODE_NOT_VERIFIED. PRODUCTION ACCEPTANCE BLOCKED.**

Repository: `openAMRobot/openamrobot-interfaces`. Branch:
`c10-dataset-quality-gate`. Parent/base:
`87ab8a936c97ab55ee74b8988ca3d7659160ea6a`, freshly fetched from upstream and
confirmed unchanged after verification. The draft PR records its actual head SHA;
embedding a commit's own SHA in its tracked content is not possible.

The initial clean checkout was `c9-lerobot-dataset-contract` at
`989b963f324b2e57c644edaa59e312a786b747e4`. A fresh scoped branch was created
from upstream main. Existing files/worktrees and the inspected baseline checkout
were preserved. No C9 schema/fixture, ROS interface, frozen contract, governance,
safety-path, release pin or baseline source was changed.

Environment: macOS 26.5.1, Apple arm64; Python 3.12.13; jsonschema 4.26.0,
PyYAML 6.0.3, pyarrow 26.0.0. Dependencies were installed only in an isolated
temporary venv. No ROS/Gazebo/GPU dependencies were installed for C10.

## Commands and results

Commands below ran from the repository root. Python suite output and full JSON
report are retained locally under ignored `.verification/c10-evidence/`.

```bash
git fetch upstream main
git switch -c c10-dataset-quality-gate upstream/main
uv venv --python python3.12 /private/tmp/openamrobot-c10-venv
UV_CACHE_DIR=/private/tmp/openamrobot-c10-uv-cache uv pip install \
  --python /private/tmp/openamrobot-c10-venv/bin/python jsonschema PyYAML pyarrow

/private/tmp/openamrobot-c10-venv/bin/python tools/run_verification_tests.py tests test_c10_dataset.py
/private/tmp/openamrobot-c10-venv/bin/python tools/run_verification_tests.py tests test_c10_native.py
/private/tmp/openamrobot-c10-venv/bin/python tools/run_verification_tests.py tests test_compatibility.py
/private/tmp/openamrobot-c10-venv/bin/python -m unittest discover -s tests -p test_schema_validation.py -k SchemaTests -v
/private/tmp/openamrobot-c10-venv/bin/python tools/prove_c10_negative.py
/private/tmp/openamrobot-c10-venv/bin/python -c 'from pathlib import Path; import sys; sys.path.insert(0,"tools"); from lint_schemas import validate_schemas; print(validate_schemas(Path.cwd()))'
git diff --check
```

| Verification | Result / executed count |
| --- | --- |
| C10 core suite | PASS, 63 tests, zero skips |
| C10 native-artifact suite | PASS, 31 tests, zero skips; includes actual temporary Parquet reads/corruption and orphan rows in shared files. Video-unavailable branch explicitly exercised locally. |
| Existing compatibility suite | PASS, 14 tests |
| Existing schema-only regression class | PASS, 10 tests |
| Existing registered schema validation | PASS, 1 schema / 10 registered assets (schema plus 1 valid and 8 invalid fixtures) |
| Reverted affine rule | Current code: 1 unchanged negative test PASS. Temporary reverted rule: that same test FAILED with exactly 1 assertion failure and no errors/skips. Proof command exit 0. |
| Whitespace/scope review | PASS; canonical C9 assets untouched |

The C10 matrices contain 46 C9-valid semantic corruption cases and 21 named
wrapper corruption/missing-evidence cases across all 28 diagnostic families.
Other tests exercise clean PASS, boundaries, missing approval and environmental
evidence. Counts are unittest test methods; subcases are not inflated into
additional tests. See the [acceptance matrix](c10-check-fixture-matrix.md).

The exact reverted comparison is
`calculated == stamp.get("mapped_authoritative_ns")`. The experiment replaces
only that expression in a temporary module copy. The unchanged
`test_reject_affine_arithmetic` fails with
`Expected C10_MAPPING/REJECT` because the bad declared mapping is accepted.
An import failure, wrong test count, skip or unexpected error fails the proof.

Also executed:

```bash
/private/tmp/openamrobot-c10-venv/bin/python tools/run_verification_tests.py tests test_schema_validation.py
```

This full existing suite executed **15 tests and failed with 3 errors**, each
`ModuleNotFoundError: No module named 'catkin_pkg'` in ROS-interface verification.
It is not recorded as a pass. The schema-only class and registered C9 validation
were then verified independently as shown above. The Mac lacks
`/opt/ros/jazzy/setup.bash` and `colcon`, so `bash tools/verify.sh` was not run.
It requires the documented Ubuntu/Jazzy environment. Existing ROS stages remain
intact; hosted `quality/build` must complete them on the PR head. The added C10
workflow installs scoped Python/native inspection dependencies and ffmpeg and
runs the nonempty C10 suites. Hosted results are separate evidence.

## Synthetic native CLI report

A new temporary directory was created using `tempfile.mkdtemp`; the fixture
generator wrote only there. Reproduce the generation from the repository root:

```python
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, "tests")
from c10_fixture import fixture, write_dataset
sidecar, native, policy = fixture()
dataset = Path(tempfile.mkdtemp(prefix="c10-synthetic-native-"))
write_dataset(dataset, sidecar, native, policy)
print(dataset)
```

The actual CLI command used the printed path:

```bash
/private/tmp/openamrobot-c10-venv/bin/python tools/check_c10_dataset.py \
  --dataset-path /var/folders/6y/841vvczx5g50bx_3cgjnvtg40000gn/T/c10-synthetic-native-rcy0er3d \
  --policy /var/folders/6y/841vvczx5g50bx_3cgjnvtg40000gn/T/c10-synthetic-native-rcy0er3d/synthetic-policy.json \
  --report .verification/c10-evidence/synthetic-report.json
```

Dataset ID: `openamrobot/synthetic-c9-contract-fixture`; revision:
`synthetic-fixture-1`; episode: `synthetic-episode-000000`, index 0.
Result: exit **2**, **NOT_VERIFIED**, `training_ready: false` and
`production_acceptance: NOT_VERIFIED`. Native frame coverage: 2/2;
inter-observation skew measured from selected fixture times: 0 ns for both
frames. These values are deterministic fixture arithmetic, not recording
measurements. Full findings distinguish the completed synthetic checks from
unavailable calibration/config/profile bytes, release and real-episode evidence,
and media inspection. No real recordings were used or changed.

## Not verified

- **REAL_EPISODE_NOT_VERIFIED:** no actual native episode plus matching sidecar
  found in the bounded authorized workspace search. No dataset revision exists
  here that can be reported as real-data validation.
- Actual MP4 decoding/frozen-image analysis was not run locally: ffmpeg and
  ffprobe are absent. Mocked decoder metadata/content checks do not count as
  actual decoding. The hosted workflow supplies these tools for the real
  synthetic-media branch, pending its result.
- Runtime repository ownership/adoption, release-owner pin, timing/action/source
  profiles, calibration/configuration source bytes and physical acceptance.
- Full ROS Jazzy integration on this Mac and hosted CI on the final PR head.
- Private contributor-agreement/third-party authorization records. The draft PR
  makes no agreement-acceptance or institutional-authorization attestation.

The October 16 deliverable is prepared as a reviewable conformance implementation
with synthetic evidence. Its real-episode and production acceptance obligations
remain unsatisfied. The reviewer must confirm runtime ownership, approved
profiles/pin and the next real-recording evidence before adoption.
