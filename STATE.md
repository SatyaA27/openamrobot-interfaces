# STATE

Read this file before any work in this repository and update it in the same PR as the work.
The PR evidence check fails when STATE.md exists and a PR neither updates it nor says
"no change" with a reason. Keep it under 60 lines; facts only, each with a date or SHA.

## Repository

- Type and lifecycle: interface, active
- Readiness: R1 (evidence: ROS 2 Jazzy workflow running `tools/verify.sh` on main, run 37936438992)
- Owner role: software-lead
- Verification: `bash tools/verify.sh`; last PASS on main at 87ab8a9 (2026-10-09), run 37936438992

## Current work

| Work package | Branch or PR | Status | Next step |
|---|---|---|---|
| C10 dataset quality gate | PR #25 | draft / synthetic evidence only | Work-package owner reviews placement and supplies real-episode evidence |
| Shared rules v2 (rollout step a, pilot) | PR #26 | in review | merge, then step (b) pin the harness |

## Decisions this repository implements

- CHARGING, DOCK-NO-CONTACTS, DOCKING-NOT-CHARGING (register scope includes this repository;
  `DockingStatus.msg` carries no charging or contact state). Watchdog decisions check: 0
  findings at e63311d (2026-10-17).

## Known gaps

- Harness rollout steps (b) to (e) not done as of main 87ab8a9: `repository-quality` calls the
  reusable workflow at `@main`; Watchdog reports 3 unpinned actions (2026-10-17).
- C10 real-episode and production-acceptance evidence is not verified; see PR #25.
- No runtime ownership or approved release pin is claimed for the proposed C10 reference checker.

## Not verified

- This step-(a) PR changes repository guidance only; it does not run ROS, DDS, hardware or production acceptance tests.
- No physical robot, safety-chain, released binary or cross-version deployment evidence is claimed.

## 12 November 2026 — proposed C9 component adjunct

- Branch `satya/c9-components-proposed`, base 14912e1: preserves accepted C9 v1 bytes;
  adds a proposed versioned mapping adjunct for upperbody#35/#36 and a source-model check.
- Local schema/profile tests: 3 PASS; explicit pinned-model source check: 1 PASS.
  Full ROS/DDS `tools/verify.sh` BLOCKED at absent Jazzy prerequisites on macOS.
- New full-body action/capture mappings, stowed pose and release pin need owner review;
  no actual recording or physical acceptance is verified.

- 12 November continuation: generated mock/Gazebo/real URDFs pass check_urdf and
  proposed C9 joint/type/range/interface checks in ROS Jazzy. Model arm/gripper
  bounds populated; real lift retains no ROS command interface. Dedicated CI
  retains generated evidence. Model checks do not grant motion/profile acceptance.
