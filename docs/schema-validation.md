# Interface lint and schema validation

The local/CI command `bash tools/verify.sh` always runs these checks before build:

- Parse and validate every `package.xml` with ROS `catkin_pkg`, treating metadata
  warnings as failures; reject duplicate package names and empty interface sets.
- Run `ament_lint_cmake` on each interface package's CMakeLists.txt.
- Parse every `.msg`, `.srv` and `.action` with the ROS `rosidl_adapter` parser,
  which checks ROS syntax, names, types and constants. Reject tabs/trailing
  whitespace. Generation/build subsequently checks resolvable dependencies.
- Validate the schema registry, all declared JSON/YAML schemas and fixtures,
  and run nonempty validator regression tests, including rejection cases.

Tools come from the documented apt prerequisites and rosdep's manifest
dependencies. A missing tool/dependency fails; no stage is skipped.

## JSON/YAML coverage

The C9 LeRobotDataset contract is registered in
`schemas/json/c9-lerobot-dataset.schema.json`, with a valid YAML manifest and
parseable invalid JSON manifests. It is a proposed contract, so schema success
does not validate camera calibration, timing, hardware, or release readiness.
Validator regression tests still run in addition to the registered fixtures.

When adding a domain schema, register it in `schemas/validation.json`:

```json
{
  "format_version": 1,
  "entries": [{
    "schema": "schemas/json/example.schema.json",
    "valid": ["schemas/yaml/example-valid.yaml"],
    "invalid": ["schemas/json/example-invalid.json"]
  }]
}
```

Each schema must declare JSON Schema Draft 2020-12 and have at least one valid
and one invalid instance. JSON and YAML inputs must represent JSON-compatible
data. Duplicate keys, malformed documents, non-finite numbers, unknown registry
keys, missing files, unregistered assets and invalid schemas fail verification.
Invalid fixtures must parse successfully and fail schema validation; parser or
reference errors do not count as successful rejection.

Only in-document `$ref`/`$dynamicRef` references are supported; network retrieval
is forbidden. Use `$defs` for shared definitions within a schema. Every file in
`schemas/json/` and `schemas/yaml/` must be covered, except Markdown documentation
and `.gitkeep` files. Paths cannot escape the schemas directory.

Evidence is saved in `lint-schema.json` and `lint-schema.log` within the normal
`ros2-jazzy-evidence` artifact. The JSON report distinguishes interface validation
from domain-schema applicability. Overall build success is not release readiness
or a compatibility guarantee.
