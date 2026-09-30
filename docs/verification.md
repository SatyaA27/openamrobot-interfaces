# ROS 2 Jazzy verification

From a checkout on Ubuntu 24.04 with ROS 2 Jazzy installed, run:

```bash
bash tools/verify.sh
```

The command works from any directory, returns nonzero on any failed stage,
and is the same command used by the `quality/build` job in the `ROS 2 Jazzy`
workflow. It requires no robot and never actuates hardware. Message tests publish
only on a unique verification topic with discovery restricted to localhost.

## Prerequisites

Install ROS 2 Jazzy using the [official Ubuntu installation instructions](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).
Install verification tools and manifest dependencies once, from the checkout:

```bash
sudo apt-get update
sudo apt-get install -y python3-colcon-common-extensions python3-rosdep python3-jsonschema python3-yaml \
  ros-jazzy-rmw-fastrtps-cpp ros-jazzy-rmw-cyclonedds-cpp
# Only on machines where rosdep has not been initialized:
sudo rosdep init
rosdep update --rosdistro jazzy
rosdep install --from-paths ros2 --ignore-src --rosdistro jazzy -y
```

Verification runs `rosdep check` and fails if dependencies are missing; it does
not silently install software or require sudo. CI provisions dependencies first
in the official `ros:jazzy-ros-base` container. These prerequisites are separate
from the checks, which always run through `tools/verify.sh`.

## What is checked

1. Check dependencies in a fresh shell that does not inherit the developer's
   ROS overlays, Python paths, CMake prefixes, or shell startup files.
2. Run [lint/schema validation](schema-validation.md): package metadata,
   CMake lint, ROS definition parsing and registered JSON/YAML schema fixtures.
   Run all 15 schema-validator regression tests and the registered C9
   LeRobotDataset valid/invalid manifests. Schema validation establishes
   structural conformance only; it does not validate capture hardware,
   calibration, synchronization measurements, or release readiness.
3. Copy all interface packages under `ros2/` into a new workspace and build with
   colcon, using only `/opt/ros/jazzy` as the underlay. No cached build or symlink
   install is used.
4. Copy the installed packages to a new prefix and rename the original producer
   workspace. Its recorded source, build, and install paths no longer exist.
5. Source ROS Jazzy and the relocated install's `local_setup.bash`. Check every
   source `.msg`, `.srv`, and `.action` definition through `ros2 interface show`,
   Python class loading, and generated native Python type-support loading.
   Discovering no interfaces fails.
6. Run [compatibility/version validation](compatibility.md): match generated
   RIHS01 type hashes, constants and package versions against the committed
   snapshot, then enforce version and reason-code rules against the Git base.
   Run all 14 compatibility regression tests. CI supplies the PR base or
   push-before SHA with full Git history; local runs use `VERIFY_BASE_REF`
   (default `HEAD^`). Set it explicitly for a multi-commit branch.
7. Build the standalone `tests/install_consumer` package in another new
   workspace and clean shell. It finds both `openamr_nav_msgs` and
   `openamr_ui_msgs` through their installed CMake exports, compiles representative
   navigation/message/action headers, links generated C++ type support, and runs
   the resulting executable to check runtime loading.
8. For each of Fast DDS (`rmw_fastrtps_cpp`) and Cyclone DDS
   (`rmw_cyclonedds_cpp`), start a fake publisher in a separate process, publish one navigation status,
   and then start a late consumer. Require reliable, transient-local, depth-1
   delivery and check the header, contract version, profile/threshold IDs,
   health/readiness, reason arrays, and nested sensor values against explicit
   expected values. Startup and receipt each have a 10-second deadline; the
   whole test has an outer 45-second timeout and cleans up its publisher.
9. Remove `NavigationStatus.thresholds_id` from a temporary copy of the source
   and build that package in a separate workspace. Run the unchanged consumer
   against only that install and ROS Jazzy. Require exit 42 and the exact
   missing-field diagnostic. Success, timeouts, import errors, and failed builds
   are failures of this verification stage, not acceptable negative results.

Both regression suites use the single `tools/run_verification_tests.py` runner;
empty suites, skipped tests, errors and failures return nonzero.

The message test uses `rclpy` with both mandatory Jazzy middleware packages.
The shared command passes each RMW into the isolated shell explicitly; caller
RMW settings cannot override or skip either run. Missing middleware, timeouts
and exchange failures fail the gate. This tests each middleware separately,
not cross-middleware interoperability, a complete docking sequencer, or a
physical robot.
It checks that package discovery resolves the intended install. The negative
fixture simulates reverting a required field, not a historical Git commit or a
general compatibility/version policy. It does not modify tracked message files.
The consumer rejects the reverted definition in its contract preflight before
starting message exchange. The positive run must complete real DDS exchange;
neither missing dependencies nor test timeouts are skipped.
Fixture values and consumer checks use the generated message constants. This
tests message exchange, not independent constant-value/version enforcement.
The preflight rejection does not establish old-producer/new-consumer compatibility.

The consumer has no source/build include paths to the interface packages. The
retired producer files are retained for diagnosis; this is environment and path
isolation, not an OS filesystem security boundary. This verifies a freshly built,
relocated install, not a released binary artifact or a pinned release manifest.
It does not prove general ROS install relocatability.

## Evidence and CI

Each invocation creates a new ignored `.verification/run.*` directory containing:

- `verification.log`: full command output, including the consumer execution;
- `result.txt`: overall PASS or the failing stage and exit code;
- `lint-schema.json` and `lint-schema.log`: lint/schema results, applicability
  and regression-test output;
- `interface-snapshot.json`: generated interface snapshot;
- `compatibility.json` and `compatibility.log`: baseline comparison, version
  validation and regression-test output;
- `generated-interfaces.log`: generated-interface output, when reached;
- `navigation-exchange-rmw_fastrtps_cpp.log`: Fast DDS exchange and loaded RMW;
- `navigation-exchange-rmw_cyclonedds_cpp.log`: Cyclone DDS exchange and loaded RMW;
- `reverted-consumer.log`: expected missing-field failure (exit 42);
- `reverted-interface.patch`: exact temporary field-removal change;
- `producer-retired/log/` (or `producer/log/` on an earlier failure): colcon build logs;
- `consumer/log/`: downstream build logs, when reached.
- `reverted/log/`: build logs for the temporary reverted interface.

CI uploads these files as `ros2-jazzy-evidence`, including available partial
evidence on failure. The build and install trees remain local and are not uploaded.
An artifact alone does not mean verification passed: require a successful
`quality/build` job and a PASS in `result.txt`. Remove old `.verification/run.*`
directories manually when their diagnostic workspaces are no longer needed.

The workflow runs on pull requests and pushes to `main`. Fork pull requests use
the ordinary `pull_request` event with read-only permissions and no secrets;
maintainer approval may be required by GitHub's Actions policy.

## Troubleshooting

- **Prerequisites fail:** ensure `/opt/ros/jazzy/setup.bash` exists, initialize and
  update rosdep, and install the dependencies listed by `rosdep check`.
- **A developer overlay used to make the build pass:** verification deliberately
  ignores it. Declare and install the missing dependency instead.
- **Generated interfaces or consumer fail:** inspect the failing stage in
  `verification.log` and the corresponding colcon logs. Check exported runtime
  dependencies and installed headers/libraries; do not add producer source or
  build paths to the consumer.

## Checking failure detection

In a disposable checkout, change only the publisher fixture assignment of
`message.thresholds_id` in `tests/navigation_exchange.py` to a different string,
leaving the consumer expectation unchanged. Run `bash tools/verify.sh`: it must
exit nonzero with `FAIL: unexpected thresholds_id` in the exchange log and a
failed middleware stage in `result.txt`. Restore the fixture before normal
verification. This is a deliberately broken exchange, separate from the exact
exit-42 reverted-field preflight test.

## Issue #6 and release scope

The shared command combines build, generated-interface, lint/schema,
compatibility/version, installed-consumer, message-exchange and reverted-field
checks. Keep [Issue #6](https://github.com/openAMRobot/openamrobot-interfaces/issues/6)
open until passing combined main-branch evidence is attached after merge.
This does not establish release readiness or close runtime integration work.
