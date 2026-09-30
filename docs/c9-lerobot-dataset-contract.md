# C9 whole-body capture / LeRobotDataset contract

Status: **Proposed** — [contract change request #18](https://github.com/openAMRobot/openamrobot-interfaces/issues/18), pending software-lead acceptance.

`schemas/json/c9-lerobot-dataset.schema.json` is the proposed version 1
episode-manifest contract for Workstream C9. It describes a recording and its
metadata; it does not implement a recorder, camera driver, ROS node, dataset
writer, replay system, training pipeline, policy, or safety controller.

The root object requires `contract_version: 1`, `native_lerobot`, and
`openamrobot`. Proposal status is deliberately not recorded in each episode.
Acceptance changes the document and change-request status, not the version-1
recording shape, so it does not invalidate version-1 recordings. Version 1 is
the first schema version; incompatible future changes require a new version while
closed-object fields also require a version change because older validators
reject unknown fields. Additional camera entries are already permitted in
version 1. The valid fixture is synthetic schema evidence, not a calibrated
capture or physical acceptance.

## Native LeRobot binding

`native_lerobot` is a sidecar binding descriptor for the LeRobot Dataset v3.0
layout. It identifies the dataset and episode (`dataset_id`, `episode_id`,
`episode_index`) and supplies binding descriptors interpreted against native
LeRobot `meta/info` features; those descriptors are not fields injected into
LeRobot's `info.json`. The native writer receives a `task` string and stores
the task-index mapping in `meta/tasks`/Parquet; the sidecar's `task` records
that `task_index` and the episode-level `instruction`. A changed instruction
requires a new episode rather than silently changing a task mid-episode.

The required native feature keys are:

- `observation.images.camera_wrist_left`
- `observation.images.camera_wrist_right`
- `observation.images.head`
- `observation.images.base`
- `observation.state`
- `action`

Each image binding descriptor records `[height, width, 3]`, `fps`, and
`encoding`, complementing LeRobot's native video feature and dataset FPS
metadata. `head` is the configured upstream-compatible scene/top observation
key for the ZED head camera, while `base` is the separate navigation-camera
key for the Orbbec Gemini 336L. The contract does not assume ZED left/right
eye channels, a stereo layout, or a particular driver topic; those belong to a
source profile and stream metadata.

`observation.state` and `action` bind to native `float32` vectors. Native
metadata represents vector names as strings and shape as `[N]`; the sidecar's
ordered `dimensions` adds each dimension's `unit` and `meaning`. A consumer
must not infer ordering from the vector length. This lets a policy use normal
LeRobot state/action features without a conversion format while keeping
OpenAMRobot-only recording evidence additive under `openamrobot`.

For the current OpenArm/LeRobot adapter profile, the direct dataset
representation uses 16 position values in **degrees**, ordered
`left_joint_1.pos` through `left_joint_7.pos`, `left_gripper.pos`, then
`right_joint_1.pos` through `right_joint_7.pos`, `right_gripper.pos`. The
corresponding ROS profile is separate and uses radians. This profile comes from
the pinned upstream adapter, not an accepted universal
whole-body action shape: base, tool, or future device dimensions
must be stated by name in their own profile. In the supplied profile, `action` records
the requested/pre-clip command associated with that sample's authoritative
timeline position; it is not proof of measured execution or of an action sent
after device-side clipping. `openamrobot.action_semantics` makes the distinction
explicit with `values` (`requested_pre_clip`, `sent_post_clip`, or
`execution_estimate`), `timestamp` (`command_issued`, `command_dispatched`, or
`execution_estimate`), `observation_relationship`, and
`capture_provenance`. The dimensions' `meaning` distinguishes commands from
measured state.
The supplied profile uses command-issue time, not measured execution completion time. Other profiles MUST declare their timestamp semantics.

The upstream snapshot referenced by this proposal is LeRobot `v0.6.1`, commit
`7e241bd630a3719a56157a497ce5d08f244784f1`, whose dataset format is v3.0.
OpenAMRobot has no validated LeRobot release/commit pin in its manifest or
release repository yet. A recording therefore records the snapshot as
provenance, and release approval/pinning remains a follow-up rather than a
claim made by this contract.

## Time, streams, and synchronization

`openamrobot.timebase` defines the authoritative monotonic recording timeline.
Native LeRobot frame index and FPS form a sampling grid; they are not a claim
about physical capture time. Each of the four cameras, state, and action has a
named `openamrobot.streams` entry and sample linkage. Stream metadata records
source identity, timestamp source, clock domain, timestamp unit, and the
validity of its affine device-to-recording clock mapping.

Each `openamrobot.samples` record retains available raw device times and host receipt times,
the mapped authoritative timestamp, source sequence linkage, stream health,
and measured skew. Timestamps use an explicitly declared unit (nanoseconds in
the C9 profile). A valid affine mapping expresses recording time as
`recording_ns = authoritative_origin_ns +
scale_ns_per_source_unit * (raw_source_value - source_origin)`; mapping validity is
recorded so a pending or unavailable mapping cannot be treated as synchronized data. That
permits C10 to detect stale observations, dropped or
missing frames, camera FPS/freshness failures, and state/action association
without rewriting C9 data. Wall-clock values may be retained for audit and
debugging, but neither ordering nor synchronization relies on wall-clock time.

`openamrobot.synchronization` records the declared tolerance and the measured
skew representation. The schema intentionally does not prescribe a numeric
acceptance threshold: no validated recording/calibration value exists in the
project. A pending or unvalidated threshold must remain visibly so; C10 can
apply a future approved threshold to the stored skew values.

## Calibration, configuration, and provenance

Every camera stream carries its physical/logical identity, capture descriptor,
calibration identifier, configuration hash, clock information, and source
provenance. Calibration residuals are structured metrics with an explicit
unit and statistic. The contract deliberately does not assert a universal
residual value, unit, or statistic: the calibration producer must state what
was measured. This supports the calibration and recording work package without
moving calibration implementation into this repository.

`openamrobot.provenance` records the source profile, robot configuration hash,
known software/library commits. Contract version is at the root; dataset revision is in `native_lerobot.dataset_revision`.
Calibration references remain associated with their streams. A residual is
either a measured value with name/unit/statistic/method, or
`not_measured` with a reason. Timestamp mappings use explicit `valid`,
`pending`, or `unavailable` states. These states make missing evidence visible
rather than fabricated. The schema's fixture marks its values as synthetic and
does not validate a camera, calibration, device clock, or robot configuration.
Software repository references are required nonempty text strings; the schema
does not claim to validate URI syntax.

## Episode result and events

`openamrobot.outcome` records success or failure and a termination reason.
`openamrobot.events` records timestamp-linked human interventions,
corrections, recoveries, safety-related events, and aborts. Failure and a
safety event are independent observations: neither field commands recovery or
safety behavior. These records give the C10 dataset-quality gate and the
capture/replay/evaluation work package the evidence needed to check
completeness and event linkage while leaving runtime ownership unresolved.

## Boundaries and follow-ups

This contract is an additive sidecar profile for native LeRobot v3.0 data. The
proposed sidecar discovery location is `meta/openamrobot/episodes/episode-{episode_index:06d}.json` next
to the native dataset metadata. It does not replace LeRobot `meta/info`, native
`frame_index`/FPS, Parquet/video storage, or the upstream writer. The LeRobot
v3.0 writer's `frame_index` and FPS remain native sampling fields. The schema
has no network `$ref` and does not add LeRobot as a dependency.

Schema validation proves only object shape, required fields, enumerations, and
the valid/invalid fixtures. C10 owns substantive freshness/FPS, skew, missing
frame, stale-observation, range, calibration-ID, configuration-hash, and
episode-completeness checks with deliberately corrupted fixtures. Neither C9
schema validation nor a synthetic fixture is operational or physical evidence.

Open decisions that must be backed by subsequent evidence are: the validated
LeRobot release pin in the release manifest, the numerical synchronization
threshold, physical source-profile details and camera eye/layout, the
calibration residual convention, runtime recorder ownership, and any accepted
whole-body action profile beyond the named OpenArm development profile.

Primary sources: [LeRobot v0.6.1](https://github.com/huggingface/lerobot/tree/7e241bd630a3719a56157a497ce5d08f244784f1)
(Apache-2.0), [OpenArm Dataset](https://github.com/enactic/openarm_dataset/tree/1add81f9390afbbe1c1ebdf6bac0b22d687c56b4)
(Apache-2.0), [OpenArm fake-hardware baseline PR](https://github.com/openAMRobot/openamrobot-manipulation/pull/9),
and [OpenArm description](https://github.com/enactic/openarm_description/tree/14ff67b638ff1c738a1b9a6be8aaa5ce5ed2c831).
The action distinction follows [LeRobot's v0.6.1 recorder](https://github.com/huggingface/lerobot/blob/7e241bd630a3719a56157a497ce5d08f244784f1/src/lerobot/scripts/lerobot_record.py#L328-L338).

## Normative binding and QA boundary

A sidecar MUST accompany each recorded episode at the proposed discovery path
above. It does not contain media or vector values: these remain in native
LeRobot Parquet/video files. `dataset_revision` identifies the exact dataset
revision, `length` equals the native episode length, and `fps` equals the native
dataset sampling rate. Feature shapes and names MUST match `meta/info.json`;
`dimensions` length MUST equal the vector shape and names MUST be unique.
The camera descriptor FPS describes the native output sampling rate; stream
`frame.fps` is the configured source rate. Neither proves measured FPS.

Required cameras may be augmented with `observation.images.<identifier>`
features and matching camera stream/sample entries (for example `head_right`).
Each extra stream MUST name its native feature and physical camera identity;
stereo views share an identity where they come from one physical device.
The head `stereo_view` MUST state mono/left/right/packed_stereo truthfully.
Packed layouts and any rectification MUST be described by the source profile.
The fixture's 64×48, 30 FPS and packed image are synthetic choices, not device
specifications. Wrist keys are OpenAMRobot choices configured as top-level
LeRobot cameras, avoiding the per-arm automatic prefixes.

`recording` gives monotonic start/end boundaries and complete/interrupted
status, independently of task success. Exactly one timing sample per native
frame is required, with matching episode and task indices. `frame_index` starts
at zero, is contiguous, and indexes the native frame; it is not a camera's raw
frame sequence. Each stream's `sequence_id` and `source_frame_id` identify the
source sample selected for that frame. Reuse preserves the original IDs and
timestamps rather than fabricating a fresh frame. Sequence counters MUST be
scoped to the stream and episode, with resets requiring a new episode/profile.

All authoritative timestamps are integer nanoseconds since recording start.
The affine equation uses raw values in the stream's declared `raw_unit`, with
scale in nanoseconds per raw unit; source origins and validity bounds use that
same raw unit. Round the result to nearest integer nanosecond, ties to even.
A mapping is usable only within its inclusive source validity interval. A
clock reset or mapping change requires a new episode in version 1. These are
proposed representation rules, not measured clock-calibration claims.

A valid sample's selected time MUST equal the mapped time from its declared
selection source. Host receipt time is an arrival-time proxy, not exposure
time; producers MUST not relabel it as physical acquisition time. Pending
device mappings MUST retain their raw values and a reason, and use
`health: unmapped`, null selected time and null skew. Missing/dropped slots
retain null source IDs, selected time and skew, plus unavailable timestamp
reasons; their host-receipt timestamp status is `unavailable`, so raw and
mapped receipt fields are absent. Available source samples MUST retain host
receipt information; device timestamps may explicitly be unavailable.
`fresh`/`stale` are producer reports, not QA verdicts.

`measured_skew_ns` is the absolute difference between a stream's selected time
and the sample's `authoritative_timestamp_ns` (the observation reference).
C10 MUST recompute it. Inter-observation skew is max minus min of selected
camera and robot-state times; command latency is assessed separately using
action time and the declared observation relationship. The declared tolerance
applies to inter-observation skew. An unmapped/missing stream makes synchronization
unassessable; null never means zero or pass. With `pending_evidence`, tolerance
MUST be null; `declared` requires a value and evidence basis but is not itself
proof that maintainers approved that value.

Calibration IDs/versions and configuration hashes identify immutable source
artifacts. Hashes are SHA-256 of the producer's exact configuration artifact
bytes; the source profile MUST identify the artifact and serialization.
Software provenance MUST identify the recording LeRobot version/commit when
known, separately from this proposal's inspected baseline. Unknown commits use
null; unknown versions use the explicit string `unknown`, with the reason in
the source profile. Fixture zeros and synthetic IDs MUST NOT be copied into
actual recordings. `validated_release_pin: null` means no validated pin.
For joint-space dimensions, a null reference frame requires the provided
reason; for a non-null reference frame, that reason is optional. Cartesian profiles MUST
specify frames and per-dimension units/semantics.

| C9 structural validation | Deferred C10 evidence checks |
| --- | --- |
| Required task/version/timebase/provenance | Native task/index and dataset-revision consistency |
| Camera shape, positive FPS, calibration identifiers | Actual FPS/freshness, source drops, calibration artifact existence |
| Clock source, mapping representation, sample states | Mapping arithmetic/validity, monotonicity, measured skew |
| Ordered vector descriptors and configuration hashes | Names/shape equality, ranges, actual configuration identity |
| Outcome, recording boundaries and event structure | Frame coverage, event bounds, episode completeness |

JSON Schema does not prove the cross-field or temporal requirements in the
right column. A structurally valid document can fail C10. The eight registered
negative fixtures remove a required field, set head width to zero, or exercise
one of the three conditional requirements: a pending synchronization threshold
must be null; a missing sample's selected timestamp must be null; and a missing
sample must use an unavailable host-receipt timestamp status with no receipt
raw or mapped time. None relies on malformed JSON/YAML. The existing validator
is reused unchanged.

Camera conventions are evidenced by the [OpenArm camera examples](https://github.com/enactic/openarm_dataset/blob/1add81f9390afbbe1c1ebdf6bac0b22d687c56b4/README.md#L91-L112)
and [LeRobot bimanual camera handling](https://github.com/huggingface/lerobot/blob/7e241bd630a3719a56157a497ce5d08f244784f1/src/lerobot/robots/bi_openarm_follower/bi_openarm_follower.py).
Degrees are established by the [Damiao adapter](https://github.com/huggingface/lerobot/blob/7e241bd630a3719a56157a497ce5d08f244784f1/src/lerobot/motors/damiao/damiao.py).
Native sampling-grid timestamps are defined by the [writer](https://github.com/huggingface/lerobot/blob/7e241bd630a3719a56157a497ce5d08f244784f1/src/lerobot/datasets/dataset_writer.py#L202-L227).
