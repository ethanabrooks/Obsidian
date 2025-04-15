# Chronicle of a Failed Ascent: Adding Dependencies in Olympus

This document outlines the recent experience attempting to add the `pydantic-ai` dependency to a new project (`experimental/agentless-localization/`) within the Olympus monorepo. The goal is to highlight the challenges encountered and discuss potential improvements.

## Timeline of Events & Challenges

1.  **Initial Development:** Started developing a new project under `experimental/`, which has relaxed CI/CD and review requirements (though still requires a rubber stamp for merging).
2.  **Isolated Workspace:** To improve focus and tool performance (file search, AI context), a separate Cursor workspace was created at the root of `experimental/agentless-localization/`. This worked well initially but caused IDE type errors for internal Olympus imports (e.g., `Stub file not found for "experimental.agentless_localization.edit_locator"`), as the workspace lacked the broader monorepo context.
3.  **First Dependency Attempt:** Needed to add `pydantic-ai`. Attempted adding it to the central `third-party/BUILD` file.
4.  **Build Interruption:** Ran `pants generate-lockfiles`. After ~8 minutes, realized a concurrent terminal session on a different branch (within the same workspace) had interfered, effectively restarting the process without the new dependency.
5.  **Dependency Conflict:** Switched back to the correct branch and reran `pants generate-lockfiles`. After ~7.5 minutes, the process failed due to a version conflict: `pydantic-ai` required `mistralai>=1.0.0`, while Olympus used `mistralai==0.42`.
6.  **Addressing Conflict (MistralAI Upgrade/Removal):** Attempting to upgrade `mistralai` proved complex due to breaking API changes in v1.0.0. Following Arnaud's suggestion, opted to remove the `mistralai` dependency entirely, as the corresponding endpoint wasn't in use.
7.  **Lockfile Regeneration (Success):** Regenerating lockfiles after removing `mistralai` took ~6 minutes.
8.  **CI/CD Bottleneck (MistralAI Removal PR):** Pushing the PR to remove `mistralai` triggered _all_ tests across Olympus. This took ~35 minutes, ultimately failing due to a timeout and unrelated flaky tests in `mathesis`.
9.  **CI/CD Rerun:** Rerunning the failed `mathesis` tests took an additional ~13.5 minutes.
10. **PR Merged:** The `mathesis` tests passed on the second attempt, and the PR removing `mistralai` was merged.
11. **Second Dependency Attempt (pydantic-ai):** Pulled `main` and tried adding `pydantic-ai` to `third-party/BUILD` again.
12. **New Build Failure:** Ran `pants generate-lockfiles`. After ~4.5 minutes (270 seconds), it failed with a complex error during the metadata preparation phase for `pandas` (specifically, a compilation error related to `PyArray_Descr` missing `c_metadata`, likely due to a numpy version incompatibility surfaced by the dependency changes).

```
# ... (trimmed error log) ...
stderr:
pid 3518652 -> .../python /home/ethan/.cache/pants/named_caches/pex_root/.../pex ... download ... pydantic-ai>=0.0.52 ... --index-url https://pypi.org/simple/ --extra-index-url https://flashinfer.ai/whl/cu124/torch2.4/ --retries 5 --timeout 15 exited with 1 and STDERR:
pip: Ignoring the following environment variables in Pex venv mode: ...
pip:   error: subprocess-exited-with-error
pip:   × Preparing metadata (pyproject.toml) did not run successfully.
pip:   │ exit code: 1
# ... (meson/ninja build logs showing pandas compilation error) ...
pip:    ../../pandas/_libs/src/vendored/numpy/datetime/np_datetime.c: In function ‘get_datetime_metadata_from_dtype’:
pip:    ../../pandas/_libs/src/vendored/numpy/datetime/np_datetime.c:946:52: error: ‘PyArray_Descr’ {aka ‘struct _PyArray_Descr’} has no member named ‘c_metadata’
pip:      946 |     return (((PyArray_DatetimeDTypeMetaData *)dtype->c_metadata)->meta);
pip:          |                                                    ^~
# ... (further build errors) ...
pip:    ERROR: Preparing metadata (pyproject.toml) exited with 1

ProcessExecutionFailure: Process 'Generate lockfile for base' failed with exit code 1.
```

## Key Issues & Observations

- **Dependency Management Time:** Adding or modifying dependencies triggers lengthy `generate-lockfiles` processes (6-8+ minutes per attempt, even before build failures).
- **Dependency Conflicts:** The shared dependency environment makes conflicts likely when adding new packages with specific version requirements. Resolving these can involve significant effort (e.g., upgrading/removing other dependencies).
- **CI/CD Inefficiency:** The current CI/CD setup appears to run _all_ tests even for seemingly isolated dependency changes. This results in extremely long test times (30-50+ minutes) and vulnerability to unrelated flaky tests, significantly slowing down the development cycle for dependency updates. The lack of pinned dependencies might exacerbate this, causing widespread changes even with minor additions.
- **Monorepo vs. Isolated Development:** Working within the monorepo provides integration benefits but introduces friction (dependency conflicts, slow builds, complex tooling, CI bottlenecks). Working in an isolated environment speeds up initial development but creates integration challenges later and IDE issues with internal imports.

## Potential Solutions & Discussion Points (from colleagues)

- **Managed CI/CD:** (Francis) Explore third-party CI/CD management services if engineers within the company don't have the bandwidth to optimize the current setup.
- **Dependency Pinning:** (Francis) Pinning dependencies could prevent unexpected updates during `generate-lockfiles`, potentially reducing the scope of CI runs and preventing subtle bugs caused by shifting dependencies.
- **Independent Pants Resolves:** (David) Create separate dependency resolves within Pants for specific projects.
  - _Pros:_ Faster dependency management within the resolve, hooks into existing CI/CD checks (if configured).
  - _Cons:_ Makes code sharing/importing across resolves difficult or impossible, potentially fragmenting the codebase.
- **PEX Binary Export:** (Richie) Develop in a separate resolve and export the functionality as a PEX binary.
  - _Pros:_ Encapsulates dependencies.
  - _Cons:_ Adds complexity (PEX internals), hinders library-style code sharing (requires subprocess interaction).
- **CI/CD Configuration Review:** (Ethan) Investigate why the CI/CD runs all tests on dependency changes. Optimizing this seems crucial, regardless of other approaches. Is Pants' dependency analysis being fully utilized to determine affected targets?

## Current Recommendation

Given the significant time investment required solely for dependency management and CI/CD within the main Olympus structure (estimated ~half a day just to integrate a stable project), the current pragmatic approach for _brand new, initially independent_ projects might be:

1.  Develop the core logic and tests in a completely separate repository using a faster dependency manager (e.g., `uv`).
2.  Once the project stabilizes and proves its value, allocate dedicated time for the integration process into Olympus, accepting the associated friction as a known cost.

This chronicle highlights a need to improve the developer experience around dependency management and CI/CD efficiency within Olympus to reduce friction and accelerate development, especially for projects requiring new external libraries.
