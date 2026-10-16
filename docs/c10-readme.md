<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# C10 Dataset Quality Gate reference

**Draft placement pending architecture review. SYNTHETIC QA is not REAL DATA
VALIDATION or PRODUCTION ACCEPTANCE.** Owner: SatyaA27. Reviewer:
panthera-momagdii. Target date: 16 October 2026.

This read-only Python consumer checks the accepted C9 v1 sidecar against native
LeRobot metadata and available artifacts. It creates no dataset format, writes
no recording, and requires no ROS, Gazebo, LeRobot installation or GPU. The
canonical schema and native writer remain unchanged. See the
[compatibility matrix](c10-compatibility-matrix.md) and
[Integration Gate/provenance audit](c10-provenance.md).

## Install and run on macOS

From the repository root, with Python 3.12 or later:

```bash
python3.12 -m venv /tmp/openamrobot-c10
/tmp/openamrobot-c10/bin/python -m pip install -r tools/requirements-c10.txt
/tmp/openamrobot-c10/bin/python tools/run_verification_tests.py tests test_c10_dataset.py
# Optional native Parquet inspection and integration tests:
/tmp/openamrobot-c10/bin/python -m pip install -r tools/requirements-c10-native.txt
/tmp/openamrobot-c10/bin/python tools/run_verification_tests.py tests 'test_c10*.py'
/tmp/openamrobot-c10/bin/python tools/check_c10_dataset.py \
  --dataset-path /absolute/path/to/native-dataset \
  --policy /absolute/path/to/reviewed-c10-policy.json \
  --report /tmp/c10-report.json
```

`--policy` is optional: omitting it leaves evidence-dependent decisions
`NOT_VERIFIED`. Repeat `--episode 0 --episode 7` to inspect selected episodes;
omitting selection requires a sidecar for every native episode. Report output
must be outside the dataset. No missing test dependencies are silently skipped.

Native v3 layout: `meta/info.json`, `meta/tasks.parquet`,
`meta/episodes/chunk-*/file-*.parquet`, native `data_path` and `video_path`
templates, and C9 sidecars at
`meta/openamrobot/episodes/episode-{episode_index:06d}.json` (YAML also accepted).
Legacy JSONL metadata is read when Parquet metadata is absent, without calling
that layout a verified v3 writer. Shared native video files require explicit
`videos/<feature>/{chunk_index,file_index,from_timestamp,to_timestamp}` episode
bindings; video segments use a half-open timestamp range. Native data rows use
`data/chunk_index`, `data/file_index` and their episode index, with native global
row ranges checked when present. File paths must stay inside the dataset root.

Parquet inspection requires `pyarrow`. Video frame inspection requires `ffprobe`;
exact decoded pixel hashes additionally require `ffmpeg` and a reviewed repeated
image policy. These executables can be installed through the user's normal
package manager. Absence is reported explicitly, including when the integration
test exercises the unavailable-tool branch. Frame count/dimension checks decode
frame metadata, rather than trusting a container's nominal frame-count field.

## Verdicts and report

| Exit | Verdict | Consumer behavior |
| --- | --- | --- |
| 0 | PASS | All implemented required conformance/evidence checks completed. Subject to human adoption and release acceptance. |
| 1 | REJECT | Contradictory, malformed or corrupt input. Block ingestion into training. |
| 2 | NOT_VERIFIED / BLOCKED | Required evidence or inspection capability missing. Block training. Also used for CLI usage/report-output failure. |

REJECT takes precedence over NOT_VERIFIED. Each finding has a stable check ID,
severity, status, episode/frame/stream context, observed/expected evidence,
units, threshold, policy provenance and suggested fix. Metrics are emitted only
for evidence actually inspected: native frame coverage, selected-time intervals,
source sequence gaps/reuse, stale runs, measured source FPS, inter-observation
skew and separate action latency. Nominal native output FPS and configured
camera FPS remain distinct from measured FPS. Clock decimal lexemes are retained
for exact affine arithmetic; output represents exact fractional clock values as
decimal strings. Nonfinite vector evidence is represented as strings in strict
JSON while still producing REJECT.

An abbreviated synthetic report looks like:

```json
{
  "report_version": 1,
  "status": "NOT_VERIFIED",
  "exit_code": 2,
  "training_ready": false,
  "production_acceptance": "NOT_VERIFIED",
  "findings": [{
    "check_id": "C10_REAL_EPISODE",
    "status": "NOT_VERIFIED",
    "severity": "BLOCKER",
    "episode": 0,
    "frame": null,
    "stream": null,
    "observed": "synthetic",
    "expected": "actual recording with provenance reviewed externally",
    "units": null,
    "threshold": null,
    "policy": null,
    "fix": "Provide a real recorded episode; synthetic fixtures establish QA behavior only."
  }]
}
```

The [evidence handoff](c10-evidence-handoff.md) documents a single command that
generates the complete synthetic CLI report, exact checker SHA/command and
reproduction inputs. The C10 workflow uploads these and native-suite output as
downloadable artifacts, including on failure. The report stays blocked even
when synthetic semantic checks pass. Earlier local results remain in the
[execution evidence](c10-verification.md).

## Reviewed policy input

Policy JSON is a local, proposed checker configuration, not an additional native
LeRobot or C9 contract. `approved: true`, a nonempty `id` and `evidence` identify
an approval supplied by the caller; the tool cannot grant or authenticate human
approval. Release owners must review these artifacts before deployment. There
are **no built-in hardware thresholds, action bounds or universal vector widths**.

The complete executable **synthetic-only** example is
[`synthetic_policy()`](../tests/c10_fixture.py). Never promote its numbers,
hashes, profiles or approval flag into recording policy. A real reviewed policy
supplies:

- `profiles`: exact state/action feature-key mapping to versioned `profile`,
  ordered `dimensions` (name/unit/meaning) and `reference_frame`.
- `source_profile`: exact C9 provenance `id` and an `artifact` with `path` and
  `sha256`. No unit coercion or camera aliases are applied.
- `synchronization.max_skew_ns`: accepted inter-observation bound. C9 must
  declare the matching bound. Pending C9 tolerance stays NOT_VERIFIED even when
  a policy supplies a number. Action timing is excluded from observation skew.
- `action_latency`: inclusive `min_ns`/`max_ns`, exact declared `values`,
  `timestamp`, `observation_relationship` and an explicit
  `reference_frame_offset` identifying the linked observation. Missing reference
  evidence remains unverified; free-text relationships are not inferred.
- `action_bounds`: every action dimension name mapped to authoritative `min`,
  `max` and exact `unit`. Limits are inclusive.
- `stream_quality`: each stream maps to `min_fps`, `max_freshness_ns`,
  `max_sequence_gap`, `max_reuse`. Partial policy leaves the decision unverified.
  This assesses observed timing/IDs; a host-arrival timestamp remains an arrival
  proxy, never upgraded to physical exposure evidence.
- `video_content`: per-camera `max_identical_run` in decoded frames. This
  requires explicit review because a static scene can produce identical images.
- `artifacts`: records with `kind` (`robot_configuration`,
  `stream_configuration` or `calibration`), `path`, `sha256`, and `stream` except
  for the robot configuration. Calibration also supplies `id` and `version`.
  Hashes use `sha256:` followed by the digest of exact bytes; no normalization.
- `calibration`: per-camera `name`, `unit`, `statistic`, `method`, `max_value`
  for a measured residual. Matching IDs and bytes cannot prove physical accuracy.
- `release`: `pin` equal to the C9 validated release object, and `version` and
  `commit` equal to that pin and the actual `lerobot` software provenance entry.
  Inspected baselines and `unknown` versions do not qualify.
- `native_identity`: reviewed `dataset_id`, `dataset_revision`,
  `episode_ids` mapping decimal episode index strings to IDs, and `evidence`
  identifying the immutable native snapshot. This supplies bindings absent from
  standard native metadata without injecting fields into `meta/info.json`.
  Explicit native contradictions reject the data.
- `real_episode`: full `dataset_id`, `dataset_revision`, `episode_id`,
  `episode_index`, plus external recording-review `evidence`. A producer's
  `data_origin: actual` claim alone cannot qualify.

All referenced artifact paths are dataset-relative, immutable inputs. A policy
is provenance supplied to the checker, not a replacement for organization
change control. Repository and release acceptance remain human decisions.

## Recorder and C11 invocation

Finalize the recording and native metadata, retain the exact source artifacts,
and export the matching C9 sidecar. Invoke this checker with the reviewed policy
and persist the report outside the recording. A consumer may start training
only after checking **both** exit code 0 and `status == "PASS"`; exit 1 or 2
must block it. Capture reports against an immutable dataset revision and include
the checker revision and reviewed policy ID in the training job provenance.
Do not rewrite data or manufacture timing/calibration evidence to open the gate.
Safety events are recorded observations, never safety authorization.

## Acceptance and limitations

The [check-to-corruption matrix](c10-check-fixture-matrix.md) lists the named
tests for every diagnostic family. C10-only mutations are validated against the
unchanged C9 schema before checking the expected diagnostic. Native integration
tests use temporary synthetic artifacts; no real recording is corrupted.

REAL_EPISODE_NOT_VERIFIED: no real native episode with matching sidecar was
found in the authorized workspace search. The two-frame C9 example and generated
Parquet are synthetic. A claimed source/profile hash cannot establish hardware
authenticity. Exact pixel equality detects repeated images, not every frozen,
miscalibrated or semantically wrong recording. No training or policy evaluation
was executed. The checker reads the referenced episode artifacts in memory;
large-scale streaming ingestion remains runtime work. No remote dataset is
downloaded and no remote release pin is authenticated automatically.

Runtime repository ownership, release pin, timing/action/source profiles,
calibration criteria and the next real-episode evidence require reviewer/owner
confirmation. The interfaces location is a draft conformance reference under
the existing verification structure. No recorder or training implementation is
introduced. Full October 16 production acceptance is **not satisfied** by this
reference implementation. ROS Jazzy integration and hosted CI results must be
reported separately from Mac Python tests.
