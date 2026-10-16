<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# C10 evidence handoff

**SYNTHETIC reporting evidence only. REAL_EPISODE_NOT_VERIFIED.
PRODUCTION ACCEPTANCE BLOCKED. PR #25 stays draft.**

This addresses the scoped review of commit
`8440f4b818f4bd0e6bbbbcc1538eee0555e0012a` on
[PR #25](https://github.com/openAMRobot/openamrobot-interfaces/pull/25).
The review recommends keeping this as a conformance-reference consumer under
`tools/` and `tests/` while runtime ownership is agreed separately. It does not
approve a runtime repository, numeric policy, source profile or release pin.

## Owner decisions

The work-package owner's explicit **adopt / adapt / reject** decision has not
been recorded. Instructions to prepare this evidence are not substituted for
that decision. The following checklist remains open:

- [ ] SatyaA27 records adopt, adapt or reject in the PR thread.
- [ ] Architecture/runtime owners confirm the runtime home and adoption scope.
- [ ] Release owner supplies the validated LeRobot release/commit and evidence.
- [ ] Recording/profile owners approve timing/FPS/freshness policy and action
  dimensions, order, units, bounds and observation/timestamp relationship.
- [ ] Calibration/configuration owners provide versioned source-profile and
  calibration/configuration artifacts, exact-byte hashes and residual criteria.
- [ ] Recording owner supplies an actual native episode revision, matching C9
  sidecar and immutable artifacts for the next real-episode acceptance report.

No baseline defaults fill these decisions. Existing synthetic test-policy values
are reused only to exercise reporting and remain labelled synthetic. Contributor
agreement and other rights-holder authorization records remain unverified.

## Reproduce the synthetic CLI report

Check out the exact `checker.git_head` found in the downloaded evidence manifest,
then install the existing scoped native-test dependencies. Run from that checkout:

```bash
python3.12 -m venv /tmp/openamrobot-c10-handoff
/tmp/openamrobot-c10-handoff/bin/python -m pip install -r tools/requirements-c10-native.txt
/tmp/openamrobot-c10-handoff/bin/python tools/generate_c10_evidence.py \
  --output-dir .verification/c10-evidence/synthetic \
  --expected-checker-sha "$(git rev-parse HEAD)"
```

Use a fresh output directory for each invocation. The helper refuses to overwrite
an existing directory; it writes generated dataset/report artifacts only inside
its new bundle. It reuses
the C9-derived two-frame fixture and native Parquet writer in
`tests/c10_fixture.py`, invokes the actual checker CLI, and retains the unmodified
checker report. No real recording is discovered, downloaded or modified.

For byte comparisons with an earlier run, use the Python/package versions in
`evidence.json` under `environment`, especially its `pyarrow` version: the
dependency ranges alone are not an environment lock. Absolute command paths and
manifest creation time describe each invocation and can differ; the raw fixture
report and dataset hashes reproduce across output directories in the tested
environment. No new project release pin is created by recording test versions.

The helper records the exact subprocess argument vector, shell-readable command
and working directory. Repeating that captured command in the original checkout
re-runs the checker against the retained generated dataset. When moving an
artifact to another machine, regenerate the bundle at the recorded checker SHA
or adjust only the local paths to the downloaded dataset/policy/report. Absolute
interpreter and workspace paths in the manifest describe the original run.

`--expected-checker-sha` requires the actual checkout to match that full SHA and
the source tree to be clean. Without that flag a local dirty checkout is recorded
transparently; it is not immutable exact-SHA evidence. CI always supplies the
expected PR-head SHA. Source-file hashes further identify the checker, semantic
implementation, loader, C9 schema/example and fixture/evidence generator bytes.

The fixture identity is dataset
`openamrobot/synthetic-c9-contract-fixture`, revision `synthetic-fixture-1`,
episode `synthetic-episode-000000`, index 0. Its timing, configuration and
calibration numbers are synthetic inputs, not hardware measurements or approvals.

## Downloadable workflow evidence

Open the **C10 reference quality gate** run linked from PR #25's checks, verify
its head SHA, and download:

```text
c10-evidence-<full-PR-head-SHA>-<run-attempt>
```

GitHub retains this artifact for **30 days**; authenticated artifact-download
access may be required. The PR handoff records the exact successful run and
artifact links after CI finishes. Local ignored paths are supplemental evidence,
not the reviewer handoff. When retention expires, the command above recreates
the bundle from the recorded source revision and dependency versions.

The artifact contains:

| Path | Evidence |
| --- | --- |
| `expected-checker-sha.txt` | Requested immutable PR-head source revision. |
| `core-suite.log` | Complete core-suite output and executed test count. |
| `native-suite.log` | Complete native-suite output, including media capability/result branch. |
| `evidence-suite.log` | Evidence-helper and workflow failure-retention regression output. |
| `revert-negative.log` | Current-code positive test and intended failure with a reverted arithmetic rule. |
| `generation.log` | Evidence-generation command output, including failure diagnostics. |
| `synthetic/evidence.json` | Actual checker SHA/source state, exact CLI command, dataset revision, environment, source/dataset/report hashes, actual gate verdict and separate reporting-path result. |
| `synthetic/c10-report.json` | Original strict JSON report from the actual C10 CLI. |
| `synthetic/cli-stdout.log`, `synthetic/cli-stderr.log` | Original CLI process output. |
| `synthetic/dataset/` | Generated native Parquet metadata/data, matching C9 sidecar and explicitly synthetic policy for reproduction. |

The report is expected to have `status: NOT_VERIFIED`, `exit_code: 2`,
`training_ready: false` and `production_acceptance: NOT_VERIFIED`. Native fixture
frame coverage and selected-time skew are measured only from those synthetic
inputs. The generator exits zero only when the expected blocked reporting path
was observed and the generated dataset remained unchanged. Its success does
**not** convert the checker verdict to PASS. Unexpected PASS, REJECT, a missing
or inconsistent report, checker revision mismatch, or changed input bytes fails
the generator and retains available diagnostics.

All test/evidence steps preserve nonzero results through `tee` using `pipefail`.
They continue after an earlier check failure unless the run is cancelled. The
upload step uses `if: always()` and includes hidden `.verification` files, so
available logs, raw rejected reports and partial manifests remain downloadable
when checks fail. There is no `continue-on-error` and no blanket acceptance of
exit 2 for arbitrary checker invocations. Upload success cannot erase a failed
test or generation step. Missing evidence files are reported rather than
invented; cancellation or runner failure may prevent their creation.

## Verification and scope

```bash
/tmp/openamrobot-c10-handoff/bin/python tools/run_verification_tests.py tests 'test_c10*.py'
/tmp/openamrobot-c10-handoff/bin/python tools/run_verification_tests.py tests test_compatibility.py
/tmp/openamrobot-c10-handoff/bin/python -m unittest discover -s tests -p test_schema_validation.py -k SchemaTests -v
/tmp/openamrobot-c10-handoff/bin/python tools/prove_c10_negative.py
```

The new evidence tests preserve the existing core/native corruption suites and
exercise raw blocked reports, exact command/revision/hash binding, deterministic
report reproduction, output-directory protection, unexpected gate outcomes,
missing/malformed evidence and workflow failure/pipe behavior. Exact final counts,
commands, head/base SHAs and downloadable artifacts are recorded on PR #25 after
verification. [Earlier execution evidence](c10-verification.md) remains historical
and is not substituted for the latest exact-head CI result.

Local follow-up on macOS with the existing Python 3.12.13 environment passed
**117 C10 tests** (63 core, 31 native, 23 evidence), **14 compatibility tests**,
**10 schema-only tests**, and the unchanged registered C9 validation (1 schema,
10 assets). The arithmetic revert proof still passed: its single negative test
passes on current code and fails once under the temporary reverted rule.
The evidence guard was also reverted in a temporary module copy by replacing
`if not expected_gate_result(report, manifest["gate"]["process_exit_code"]):`
with `if False:`. Unchanged
`C10EvidenceTests.test_rejects_unexpected_gate_pass` then failed exactly once at
`assertNotEqual(helper_exit, 0)`, with no import errors or skipped tests. Neither
experiment changed tracked source or fixture expectations. Actual video decoding
and full ROS Jazzy integration remain hosted checks because this Mac lacks
ffmpeg/ffprobe and ROS Jazzy/colcon; explicit unavailable branches are not media
or ROS execution evidence.

No dependency manifest, checker verdict logic, accepted C9 schema, frozen
profile or runtime policy is changed by this follow-up. The only generated
recordings are temporary synthetic fixtures. Full real-episode and production
acceptance remain unresolved regardless of a successful evidence handoff.
