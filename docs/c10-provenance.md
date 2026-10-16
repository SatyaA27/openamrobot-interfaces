# C10 provenance and evidence limits

Audit date: 16 October 2026. This is documentation for a draft C9 conformance
reference pending architecture review, not a claim of runtime or physical
acceptance.

| Inspected source | Revision and scope |
| --- | --- |
| [Interfaces repository](https://github.com/openAMRobot/openamrobot-interfaces/tree/87ab8a936c97ab55ee74b8988ca3d7659160ea6a) | Parent `87ab8a936c97ab55ee74b8988ca3d7659160ea6a`; README boundaries, C9 schema, contract document and synthetic fixture. |
| [Accepted C9 PR #16](https://github.com/openAMRobot/openamrobot-interfaces/pull/16) | Merged 2 October 2026 as `fa7c438e33bd807c174fa0747119d7d627faa3bf`. [Acceptance](https://github.com/openAMRobot/openamrobot-interfaces/issues/18#issuecomment-5919324379) covers the v1 sidecar shape only. |
| [Dataset QA baseline](https://github.com/4u-79/openamrobot-c-baseline/tree/a29ce7c89b7c42c9147ad81e6a751de9dad045c9) | `a29ce7c89b7c42c9147ad81e6a751de9dad045c9`; read-only inspection of `scripts/check_dataset_integrity.py`, `scripts/validate_dataset_contract.py`, `tests/test_c10_fixtures.py`, `meta/info.json`, requirements and README. No baseline test run or real-episode pass is claimed. |
| [Organization rules](https://github.com/openAMRobot/.github/blob/539da1982bccf8e2315483f41ac16734e0bed328/AGENTS.md) and [decisions](https://github.com/openAMRobot/.github/blob/539da1982bccf8e2315483f41ac16734e0bed328/decisions.yaml) | `539da1982bccf8e2315483f41ac16734e0bed328`; source documents remain provenance, approved technical values belong in the register. Historical fixed-mast and current lift profiles must remain distinct. |
| [LeRobot source snapshot](https://github.com/huggingface/lerobot/tree/7e241bd630a3719a56157a497ce5d08f244784f1) | C9's previously inspected v0.6.1 snapshot, Apache-2.0; not a newly verified runtime dependency or project release pin. |

## Reuse and licensing

The baseline provides useful fault classes and comparison points: temporal
regression, frame loss, phase lag, frozen images, corrupt storage, malformed
dimensions, nonfinite data and orphan tasks. These ideas inform independent
C9-specific checks; baseline implementation and test source are not copied or
vendored.

The positive fixture is derived at test time from the accepted C9 YAML using a
deep copy. It supplies explicitly synthetic reviewed-policy inputs and adjusts
the copied event interval to contain its linked frame's observation timestamp.
The canonical C9 example remains unchanged: structural validity alone does not
promise a positive C10 semantic verdict.

## Dependencies

| Scoped dependency | Source / licence | Change |
| --- | --- | --- |
| jsonschema `>=4.18,<5` | [PyPI](https://pypi.org/project/jsonschema/), MIT | Declares the existing schema-validator dependency for standalone C10 installs. |
| PyYAML `>=6,<7` | [PyPI](https://pypi.org/project/PyYAML/), MIT | Declares the existing strict YAML-loader dependency. |
| pyarrow `>=17,<27` | [Apache Arrow/PyPI](https://pypi.org/project/pyarrow/), Apache-2.0 | Optional native Parquet inspection/integration manifest, not a training dependency. |
| ffmpeg / ffprobe | [FFmpeg](https://ffmpeg.org/legal.html), LGPL-2.1-or-later or GPL depending on build | Optional external media inspection; hosted test job installs the distribution package. No binary vendored or runtime release pin selected. |

Only C10 install manifests and its new verification job declare dependencies.
Existing packages and training requirements are not upgraded. Standard-library
code handles reports, exact decimal mapping, SHA-256 and process invocation.
These dependency ranges are tool-install constraints, not LeRobot release-owner
approval. Exact locally tested versions are in the execution evidence.

The inspected baseline commit contains no tracked `LICENSE` or `LICENSING.md`
and its README states no source license. Its public availability therefore
does not establish permission to copy its code. The license ambiguity remains
open; no license grant or ownership assignment is inferred. This audit does
not resolve third-party rights.

Repository licensing follows [LICENSING.md](../LICENSING.md): software MIT,
documentation CC BY 4.0. The [contributor agreement process](https://github.com/openAMRobot/.github/blob/539da1982bccf8e2315483f41ac16734e0bed328/CLA.md)
requires DCO and the applicable agreement, including authorization where other
rights holders control the work. The old C9 PR reports checks for its own head;
that does not attest agreement coverage or institutional authorization for this
new contribution. Those private legal records were not available in this audit
and no attestation is made on the contributor's behalf.

## Search evidence and open ownership

Read-only GitHub API searches covered the accessible organization repository
list, `org:openAMRobot C10`, `org:openAMRobot "dataset"`, C10 references in
the organization policy repository, issue #18 and its comments, and PR #16.
The accessible repository list contains interfaces, platform, manipulation,
upperbody, documentation, manifest and release repositories, with no dedicated
AI/dataset repository. No approved C10 runtime home was found. Issue #18
explicitly leaves recorder ownership open; its
[13 October comment](https://github.com/openAMRobot/openamrobot-interfaces/issues/18#issuecomment-6152412257)
requires a compatibility matrix and one real episode report. Search absence
does not establish that private or unpublished decisions do not exist.

The local search was limited to the authorized project workspace. It used
`rg --files --hidden` with `.git`, `node_modules`, `.venv` and `.pixi`
excluded, looking for `meta/info.json`, sidecar, roster, agreement and agent-rule
filenames. It found no actual native recording metadata/sidecar pair or team
roster; the existing C9 fixture is synthetic. Ignored files and remote/private
storage were not exhaustively searched. The public organization contributor
list is not the workstream roster. No real dataset, calibration artifact or
private agreement record was supplied through these sources.

The interfaces README reserves this repository for shared contracts and puts
application implementations elsewhere. Keeping this draft under existing
`tools/` and `tests/` is a reference conformance check while the runtime-home
decision remains open; it does not approve ingestion, replay or training code
here. Runtime adoption requires the work-package owner's explicit decision
and review. No real-episode, physical calibration, training readiness or
release acceptance claim follows from the synthetic results.
