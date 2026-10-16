# C10 compatibility review

Status: **Draft conformance reference, pending architecture review.** This review
does not approve a runtime home, source profile, release pin or numeric threshold.
The reference tooling under `tools/` and its synthetic `tests/` exercise the
accepted C9 contract; recorder, ingestion and training implementation ownership
remains unresolved.

The C9 v1 shape was accepted in [issue #18](https://github.com/openAMRobot/openamrobot-interfaces/issues/18#issuecomment-5919324379)
and [PR #16](https://github.com/openAMRobot/openamrobot-interfaces/pull/16)
merged on 2 October 2026 as `fa7c438e33bd807c174fa0747119d7d627faa3bf`.
The older Proposed label in the C9 document does not override that decision.
Comparison baseline: [dataset tooling](https://github.com/4u-79/openamrobot-c-baseline/tree/a29ce7c89b7c42c9147ad81e6a751de9dad045c9),
commit `a29ce7c89b7c42c9147ad81e6a751de9dad045c9`.

| Area | Inspected baseline behavior | Accepted C9 v1 / reconciliation needed |
| --- | --- | --- |
| Native format | Calls its layout v3.0; expects JSONL task/episode registries and one Parquet/video file per episode. | Native LeRobot v3.0 remains primary; sidecar at `meta/openamrobot/episodes/episode-{episode_index:06d}.json`. Resolve actual native metadata/file bindings using the chosen writer; the label alone proves no loader compatibility. |
| Cameras | Wrist keys agree; requires `observation.images.camera_scene` and `observation.images.camera_base_nav` with fixed shapes. | Requires `observation.images.head` and `observation.images.base` plus wrists; additional explicitly bound cameras allowed. An approved source mapping must resolve the differing keys and physical/stereo identity; no silent aliases. |
| State/action | Exactly 19 channels; historical fixed-mast rev18.2 profile, mixed base velocity, joint radians and normalized grippers; zero-limit torso channels. Both validator constants are 19; README and validator docstring retain stale 21-channel wording. | Named ordered dimensions, units, frames and action semantics control interpretation. The supplied OpenArm development profile has 16 positions in degrees. Neither vector length nor latest URDF authorizes conversion. The historical profile must remain distinct from the current lift/arm configuration. |
| Source profiles | Enum `ROBOT`, `GAZEBO`, `ISAAC`, `CALIBRATION`, `DIAGNOSTICS`; defaults to requiring `ROBOT`. | Source-profile identity and version must describe the actual configuration, serialization, clocks and units. The enum alone establishes none of these facts. Synthetic or simulation evidence cannot establish physical acceptance. |
| Clock representation | Two frame-level float64 seconds columns: host monotonic `timestamp` and `timestamp_device`. Integrity gate assumes epoch alignment; contract validator instead removes the median host/device offset. | Recording-relative integer nanoseconds; each stream retains raw device/host receipt evidence and explicit affine mapping, unit, source domain and validity interval. A host receipt is an arrival proxy. Reconstructing absent acquisition evidence from native FPS is invalid. |
| Skew | Integrity gate: maximum absolute host/device difference. Contract validator: maximum deviation of that difference from its median. These measure different quantities. | Recompute selected time using the declared mapping and ties-to-even nanosecond rounding. Recompute per-stream absolute skew against observation reference; inter-observation skew is max minus min across cameras/state. Assess action latency separately. Missing/unmapped timing is unassessable, never zero. |
| Thresholds | Defaults: 30 ms skew, 30 frames minimum, camera container FPS at least 95% of configured FPS; frozen run at least 2 s and phase lag beyond 3 frames produce nonblocking flags. | These are baseline parameters, not accepted C9 release limits. C9 pending tolerance is null; a declared value plus evidence does not prove approval. An explicit reviewed policy must supply numeric acceptance values. Container FPS cannot establish acquisition freshness. |
| Range checks | Hard-coded 19-channel limits, 5% of span margin; zero-span channels use absolute `1e-4` tolerance. `FIX-OOB-STATS` injects NaN/Inf rather than a finite range violation. | Check finite values and profile-specific bounds separately, by dimension name/unit and immutable configuration evidence. Do not apply radians/normalized-gripper limits to the degrees profile. |
| Calibration/configuration | README describes hashes; inspected gate attaches source profile and declared length from the episode registry, without checking C9 calibration/configuration artifacts. | Each camera needs calibration ID/version and structured measured residual or explicit not-measured reason. Configuration hashes identify exact artifact bytes and serialization. Checking identifier shape/equality does not verify artifact existence, contents or physical accuracy. |
| Provenance/pins | `requirements.txt` pins `lerobot==0.4.1`; README describes a future release manifest. | Inspected upstream snapshot is v0.6.1, `7e241bd630a3719a56157a497ce5d08f244784f1`; this is not a validated release pin. Record actual recorder version/commit separately; retain unknowns and null validated pin until release-owner approval. |
| Completeness/events | Eight fault classes cover jitter, missing video frames, phase lag, repeated images, broken Parquet, vector width, nonfinite values and orphan task. Most operate on in-memory synthetic records. | Bind every native frame/task/episode and stream source sample; verify recording boundaries/completeness, independent outcome and event linkage. Synthetic fixtures do not demonstrate native dataset loading, media decoding or real capture. |

The [13 October integration decision](https://github.com/openAMRobot/openamrobot-interfaces/issues/18#issuecomment-6152412257)
requires camera mappings, configuration/action profiles, pins and timestamps to
be reconciled before a real-episode gate, training or another schema freeze.
The accepted additive schema shape remains intact. The
[organization decisions register](https://github.com/openAMRobot/.github/blob/539da1982bccf8e2315483f41ac16734e0bed328/decisions.yaml)
records the current lift/arm and configuration distinctions; it supplies no
C10 runtime-home or dataset synchronization acceptance decision.

Acceptance remains blocked on an approved runtime owner/location and policy,
an approved source profile with immutable configuration/calibration evidence,
a validated LeRobot release pin, and one actual native episode plus matching C9
sidecar and end-to-end report. A passing conformance fixture alone closes none
of those items.
