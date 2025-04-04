# AI GitHub Issue Synthesis Experiment - Summary

## Problem & Motivation

A key limitation to the scale of our data pipeline is the requirement for each PR that we train on to have an associated GitHub issue. One approach to potentially overcome this hurdle is to synthesize plausible GitHub Issues for PRs that lack them.
This experiment explores the feasibility of using AI for this synthesis task. We investigated whether an AI model could generate relevant issue titles and bodies using information from a PR, primarily its code diff.

## Goal of this Document

While the ultimate measure of success for this synthetic data is improved performance on our benchmark "Verified" dataset, this document serves as an initial qualitative "vibe check". We present several examples of AI-synthesized issues alongside the code diffs that prompted them. This allows colleagues to assess the realism and relevance of the generated text. The full system prompt and example LLM prompts used are included in the appendix for context.

# Examples (Synthesized Issue -> Corresponding Diff)

Below are up to 10 examples demonstrating the AI's synthesized GitHub issue based on a code diff. Examples are selected where the input diff is no more than 10000 characters.


## Example 1 (Repo: ansible/ansible, PR #84869: [ansible-pull fix adhoc output inconsistencies on changed](https://github.com/ansible/ansible/pull/84869))

**Output (Synthesized Issue):**
> **Ansible Pull --only-if-changed Option Behaves Inconsistently**
>
> When using the `ansible-pull` command with the `--only-if-changed` option, the behavior is inconsistent. Sometimes the playbook runs even when there are no changes in the repository, and sometimes it does not run even when there are changes present.
> 
> This issue seems to be related to the way Ansible detects changes in the repository. The change detection mechanism appears to be affected by settings like the callback plugin used or the result format specified. As a result, the `--only-if-changed` option does not work reliably across different configurations and setups.
> 
> Additionally, there might be cases where the change detection mechanism fails to accurately identify changes, leading to the playbook being executed unnecessarily or skipped when it should have run.
> 
> It would be beneficial to have a consistent and reliable change detection mechanism for the `ansible-pull` command, ensuring that the `--only-if-changed` option works as expected, regardless of the callback plugins, result formats, or other configuration settings used.

**Input (Diff that generated the above issue):**
```diff
diff --git a/changelogs/fragments/pull_changed_fix.yml b/changelogs/fragments/pull_changed_fix.yml
new file mode 100644
index 00000000000000..ac6f04e77b70d0
--- /dev/null
+++ b/changelogs/fragments/pull_changed_fix.yml
@@ -0,0 +1,2 @@
+bugfixes:
+  - ansible-pull change detection will now work independant of callback or result format settings.
diff --git a/lib/ansible/cli/pull.py b/lib/ansible/cli/pull.py
index ee24c9ff9aabfb..dda02aa3f33025 100755
--- a/lib/ansible/cli/pull.py
+++ b/lib/ansible/cli/pull.py
@@ -31,6 +31,34 @@
 
 display = Display()
 
+SAFE_OUTPUT_ENV = {
+    'ANSIBLE_CALLBACK_RESULT_FORMAT': 'json',
+    'ANSIBLE_LOAD_CALLBACK_PLUGINS': '0',
+}
+
+
+def safe_output_env(f):
+
+    def wrapper(*args, **kwargs):
+
+        orig = {}
+
+        for k, v in SAFE_OUTPUT_ENV.items():
+            orig[k] = os.environ.get(k, None)
+            os.environ[k] = v
+
+        result = f(*args, **kwargs)
+
+        for key in orig.keys():
+            if orig[key] is None:
+                del os.environ[key]
+            else:
+                os.environ[key] = orig[key]
+
+        return result
+
+    return wrapper
+
 
 class PullCLI(CLI):
     """ Used to pull a remote copy of ansible on each managed node,
@@ -42,7 +70,7 @@ class PullCLI(CLI):
         you should use an external scheduler and/or locking to ensure there are no clashing operations.
 
         The setup playbook can be tuned to change the cron frequency, logging locations, and parameters to ansible-pull.
-        This is useful both for extreme scale-out as well as periodic remediation.
+        This is useful both for extreme scale-out and periodic remediation.
         Usage of the 'fetch' module to retrieve logs from ansible-pull runs would be an
         excellent way to gather and analyze remote logs from ansible-pull.
     """
@@ -76,8 +104,9 @@ def _get_inv_cli():
         return inv_opts
 
     def init_parser(self):
-        """ create an options parser for bin/ansible """
+        """ Specific args/option parser for pull """
 
+        # signature is different from parent as caller should not need to add usage/desc
         super(PullCLI, self).init_parser(
             usage='%prog -U <repository> [options] [<playbook.yml>]',
             desc="pulls playbooks from a VCS repo and executes them on target host")
@@ -106,10 +135,12 @@ def init_parser(self):
                                  help='path to the directory to which Ansible will checkout the repository.')
         self.parser.add_argument('-U', '--url', dest='url', default=None, help='URL of the playbook repository')
         self.parser.add_argument('--full', dest='fullclone', action='store_true', help='Do a full clone, instead of a shallow one.')
+        # TODO: resolve conflict with check mode, added manually below
         self.parser.add_argument('-C', '--checkout', dest='checkout',
                                  help='branch/tag/commit to checkout. Defaults to behavior of repository module.')
         self.parser.add_argument('--accept-host-key', default=False, dest='accept_host_key', action='store_true',
                                  help='adds the hostkey for the repo url if not already added')
+        # Overloaded with adhoc ... but really passthrough to adhoc
         self.parser.add_argument('-m', '--module-name', dest='module_name', default=self.DEFAULT_REPO_TYPE,
                                  help='Repository module name, which ansible will use to check out the repo. Choices are %s. Default is %s.'
                                       % (self.REPO_CHOICES, self.DEFAULT_REPO_TYPE))
@@ -121,7 +152,7 @@ def init_parser(self):
         self.parser.add_argument('--track-subs', dest='tracksubs', default=False, action='store_true',
                                  help='submodules will track the latest changes. This is equivalent to specifying the --remote flag to git submodule update')
         # add a subset of the check_opts flag group manually, as the full set's
-        # shortcodes conflict with above --checkout/-C
+        # shortcodes conflict with above --checkout/-C, see to-do above
         self.parser.add_argument("--check", default=False, dest='check', action='store_true',
                                  help="don't make any changes; instead, try to predict some of the changes that may occur")
         self.parser.add_argument("--diff", default=C.DIFF_ALWAYS, dest='diff', action='store_true',
@@ -177,7 +208,7 @@ def run(self):
             limit_opts = 'localhost,127.0.0.1'
         base_opts = '-c local '
         if context.CLIARGS['verbosity'] > 0:
-            base_opts += ' -%s' % ''.join(["v" for x in range(0, context.CLIARGS['verbosity'])])
+            base_opts += ' -%s' % ''.join(["v" for dummy in range(0, context.CLIARGS['verbosity'])])
 
         # Attempt to use the inventory passed in as an argument
         # It might not yet have been downloaded so use localhost as default
@@ -250,14 +281,15 @@ def run(self):
         # RUN the Checkout command
         display.debug("running ansible with VCS module to checkout repo")
         display.vvvv('EXEC: %s' % cmd)
-        rc, b_out, b_err = run_cmd(cmd, live=True)
+        rc, b_out, b_err = safe_output_env(run_cmd)(cmd, live=True)
 
+        print('BCS', context.CLIARGS['ifchanged'], b'"changed": true' not in b_out, b"changed: True" not in b_out)
         if rc != 0:
             if context.CLIARGS['force']:
                 display.warning("Unable to update repository. Continuing with (forced) run of playbook.")
             else:
                 return rc
-        elif context.CLIARGS['ifchanged'] and b'"changed": true' not in b_out:
+        elif context.CLIARGS['ifchanged'] and (b'"changed": true' not in b_out or b"changed: True" not in b_out):
             display.display("Repository has not changed, quitting.")
             return 0
 
@@ -347,7 +379,7 @@ def select_playbook(path):
             if 0 < len(errors):
                 display.warning("
".join(errors))
             elif len(playbooks) == len(context.CLIARGS['args']):
-                playbook = " ".join(playbooks)
+                playbook = " ".join(str(playbooks))
             return playbook
         else:
             fqdn = socket.getfqdn()
diff --git a/test/integration/targets/ansible-pull/runme.sh b/test/integration/targets/ansible-pull/runme.sh
index fd97c707f05dc7..3c171c5b1533b0 100755
--- a/test/integration/targets/ansible-pull/runme.sh
+++ b/test/integration/targets/ansible-pull/runme.sh
@@ -27,6 +27,23 @@ cd "${repo_dir}"
     git commit -m "Initial commit."
 )
 
+function change_repo {
+    cd "${repo_dir}"
+    date > forced_change
+    git add forced_change
+    git commit -m "forced changed"
+    cd -
+}
+
+function no_change_tests {
+    # test for https://github.com/ansible/ansible/issues/13688
+    if grep MAGICKEYWORD "${temp_log}"; then
+        cat "${temp_log}"
+        echo "Ran the playbook, found MAGICKEYWORD in output."
+        exit 1
+    fi
+}
+
 function pass_tests {
 	# test for https://github.com/ansible/ansible/issues/13688
 	if ! grep MAGICKEYWORD "${temp_log}"; then
@@ -66,6 +83,7 @@ function pass_tests_multi {
 
 export ANSIBLE_INVENTORY
 export ANSIBLE_HOST_PATTERN_MISMATCH
+export ANSIBLE_DEBUG=1
 
 unset ANSIBLE_INVENTORY
 unset ANSIBLE_HOST_PATTERN_MISMATCH
@@ -97,3 +115,31 @@ export ANSIBLE_CACHE_PLUGIN=jsonfile ANSIBLE_CACHE_PLUGIN_CONNECTION=./
 ansible-pull -d "${pull_dir}" -U "${repo_dir}" "$@" gather_facts.yml
 ansible-pull -d "${pull_dir}" -U "${repo_dir}" --flush-cache "$@" test_empty_facts.yml
 unset ANSIBLE_CACHE_PLUGIN ANSIBLE_CACHE_PLUGIN_CONNECTION
+
+#### CHACHCHCHANGES!
+echo 'setup for change detection'
+ORIG_CONFIG="${ANSIBLE_CONFIG}"
+unset ANSIBLE_CONFIG
+
+echo 'test no run on no changes'
+ansible-pull -d "${pull_dir}" -U "${repo_dir}" --only-if-changed "$@" | tee "${temp_log}"
+no_change_tests
+
+echo 'test run on changes'
+change_repo
+ansible-pull -d "${pull_dir}" -U "${repo_dir}" --only-if-changed "$@" | tee "${temp_log}"
+pass_tests
+
+# test changed with non yaml result format, ensures we ignore callback or format changes for adhoc/change detection
+echo 'test no run on no changes, yaml result format'
+ANSIBLE_CALLBACK_RESULT_FORMAT='yaml' ansible-pull -d "${pull_dir}" -U "${repo_dir}" --only-if-changed "$@" | tee "${temp_log}"
+no_change_tests
+
+echo 'test run on changes, yaml result format'
+change_repo
+ANSIBLE_CALLBACK_RESULT_FORMAT='yaml' ansible-pull -d "${pull_dir}" -U "${repo_dir}" --only-if-changed "$@" | tee "${temp_log}"
+pass_tests
+
+if [ "${ORIG_CONFIG}" != "" ]; then
+  export ANSIBLE_CONFIG="${ORIG_CONFIG}"
+fi

```


## Example 2 (Repo: apache/airflow, PR #48699: [Enable task sdk for system tests](https://github.com/apache/airflow/pull/48699))

**Output (Synthesized Issue):**
> **Task SDK Not Working in System Tests**
>
> When running system tests, the Task SDK appears to be non-functional. Tasks that are intended to communicate with the Airflow API server and make use of advanced SDK features are failing to execute correctly during system test runs. This is leading to incomplete test coverage and potential regressions in the Task SDK functionality.
> 
> The symptoms observed include:
> 
> - System tests involving tasks that use the Task SDK fail with errors related to the tasks being unable to connect to the API server or access required SDK functionality.
> - Task logs show errors indicating the API server is not available or the SDK is not properly initialized.
> - Test runs complete with skipped or errored tests related to Task SDK usage.
> 
> It appears that the current system test setup is not properly configured to support Task SDK functionality. Potential causes could include:
> 
> - The API server is not being started or configured correctly for system tests.
> - The system test environment is missing required dependencies or configuration for the Task SDK.
> - There are incompatibilities or issues with the way the Task SDK interacts with the system test execution environment.
> 
> To ensure proper test coverage and stability of the Task SDK, it is important to resolve this issue and enable full Task SDK support within the system test suite.

**Input (Diff that generated the above issue):**
```diff
diff --git a/Dockerfile.ci b/Dockerfile.ci
index d238e7b01a908..304fdea38c0ba 100644
--- a/Dockerfile.ci
+++ b/Dockerfile.ci
@@ -1023,7 +1023,9 @@ function check_airflow_python_client_installation() {
 }
 
 function start_api_server_with_examples(){
-    if [[ ${START_API_SERVER_WITH_EXAMPLES=} != "true" ]]; then
+    # check if we should not start the api server with examples by checking if both
+    # START_API_SERVER_WITH_EXAMPLES is false AND the TEST_GROUP env var is not equal to "system"
+    if [[ ${START_API_SERVER_WITH_EXAMPLES=} != "true" && ${TEST_GROUP:=""} != "system" ]]; then
         return
     fi
     export AIRFLOW__CORE__LOAD_EXAMPLES=True
diff --git a/airflow-core/src/airflow/executors/workloads.py b/airflow-core/src/airflow/executors/workloads.py
index 4d9d2286141a7..83d7feed5556f 100644
--- a/airflow-core/src/airflow/executors/workloads.py
+++ b/airflow-core/src/airflow/executors/workloads.py
@@ -98,17 +98,22 @@ class ExecuteTask(BaseWorkload):
 
     @classmethod
     def make(
-        cls, ti: TIModel, dag_rel_path: Path | None = None, generator: JWTGenerator | None = None
+        cls,
+        ti: TIModel,
+        dag_rel_path: Path | None = None,
+        generator: JWTGenerator | None = None,
+        bundle_info: BundleInfo | None = None,
     ) -> ExecuteTask:
         from pathlib import Path
 
         from airflow.utils.helpers import log_filename_template_renderer
 
         ser_ti = TaskInstance.model_validate(ti, from_attributes=True)
-        bundle_info = BundleInfo(
-            name=ti.dag_model.bundle_name,
-            version=ti.dag_run.bundle_version,
-        )
+        if not bundle_info:
+            bundle_info = BundleInfo(
+                name=ti.dag_model.bundle_name,
+                version=ti.dag_run.bundle_version,
+            )
         fname = log_filename_template_renderer()(ti=ti)
         token = ""
 
diff --git a/airflow-core/src/airflow/models/dag.py b/airflow-core/src/airflow/models/dag.py
index 8ca0f3383303b..f8c5eec3c7e02 100644
--- a/airflow-core/src/airflow/models/dag.py
+++ b/airflow-core/src/airflow/models/dag.py
@@ -29,6 +29,7 @@
 from contextlib import ExitStack
 from datetime import datetime, timedelta
 from functools import cache
+from pathlib import Path
 from re import Pattern
 from typing import (
     TYPE_CHECKING,
@@ -76,6 +77,7 @@
     UnknownExecutorException,
 )
 from airflow.executors.executor_loader import ExecutorLoader
+from airflow.executors.workloads import BundleInfo
 from airflow.models.asset import (
     AssetDagRunQueue,
     AssetModel,
@@ -234,10 +236,10 @@ def get_asset_triggered_next_run_info(
     }
 
 
-def _triggerer_is_healthy():
+def _triggerer_is_healthy(session: Session):
     from airflow.jobs.triggerer_job_runner import TriggererJobRunner
 
-    job = TriggererJobRunner.most_recent_job()
+    job = TriggererJobRunner.most_recent_job(session=session)
     return job and job.is_alive()
 
 
@@ -1714,7 +1716,7 @@ def add_logger_if_needed(ti: TaskInstance):
                     self.log.warning("No tasks to run. unrunnable tasks: %s", ids_unrunnable)
                     time.sleep(1)
 
-                triggerer_running = _triggerer_is_healthy()
+                triggerer_running = _triggerer_is_healthy(session)
                 for ti in scheduled_tis:
                     ti.task = tasks[ti.task_id]
 
@@ -1727,8 +1729,26 @@ def add_logger_if_needed(ti: TaskInstance):
                     if use_executor:
                         if executor.has_task(ti):
                             continue
-                        # Send the task to the executor
-                        executor.queue_task_instance(ti, ignore_ti_state=True)
+                        # TODO: Task-SDK: This check is transitionary. Remove once all executors are ported over.
+                        from airflow.executors import workloads
+                        from airflow.executors.base_executor import BaseExecutor
+
+                        if executor.queue_workload.__func__ is not BaseExecutor.queue_workload:  # type: ignore[attr-defined]
+                            workload = workloads.ExecuteTask.make(
+                                ti,
+                                dag_rel_path=Path(self.fileloc),
+                                generator=executor.jwt_generator,
+                                # For the system test/debug purpose, we use the default bundle which uses
+                                # local file system. If it turns out to be a feature people want, we could
+                                # plumb the Bundle to use as a parameter to dag.test
+                                bundle_info=BundleInfo(name="dags-folder"),
+                            )
+                            executor.queue_workload(workload, session=session)
+                            ti.state = TaskInstanceState.QUEUED
+                            session.commit()
+                        else:
+                            # Send the task to the executor
+                            executor.queue_task_instance(ti, ignore_ti_state=True)
                     else:
                         # Run the task locally
                         try:
diff --git a/dev/breeze/src/airflow_breeze/commands/testing_commands.py b/dev/breeze/src/airflow_breeze/commands/testing_commands.py
index 0bbb342d2a8b5..1748b1eb0b8e0 100644
--- a/dev/breeze/src/airflow_breeze/commands/testing_commands.py
+++ b/dev/breeze/src/airflow_breeze/commands/testing_commands.py
@@ -1015,7 +1015,7 @@ def system_tests(
         collect_only=collect_only,
         enable_coverage=enable_coverage,
         forward_credentials=forward_credentials,
-        forward_ports=False,
+        forward_ports=True,
         github_repository=github_repository,
         integration=(),
         keep_env_variables=keep_env_variables,
diff --git a/dev/breeze/src/airflow_breeze/utils/run_tests.py b/dev/breeze/src/airflow_breeze/utils/run_tests.py
index f5412a6af3b7f..e9b442d13a47c 100644
--- a/dev/breeze/src/airflow_breeze/utils/run_tests.py
+++ b/dev/breeze/src/airflow_breeze/utils/run_tests.py
@@ -396,6 +396,9 @@ def generate_args_for_pytest(
             args.append(f"--ignore={group_folder}")
     if test_group not in IGNORE_DB_INIT_FOR_TEST_GROUPS:
         args.append("--with-db-init")
+    if test_group == GroupOfTests.SYSTEM:
+        # System tests will be inited with the api server is started
+        args.append("--without-db-init")
     if test_group == GroupOfTests.PYTHON_API_CLIENT:
         args.append("--ignore-glob=clients/python/tmp/*")
     args.extend(get_suspended_provider_args())
diff --git a/devel-common/src/tests_common/pytest_plugin.py b/devel-common/src/tests_common/pytest_plugin.py
index 222c6c23b5d32..dbe12113dfa7d 100644
--- a/devel-common/src/tests_common/pytest_plugin.py
+++ b/devel-common/src/tests_common/pytest_plugin.py
@@ -224,6 +224,12 @@ def pytest_addoption(parser: pytest.Parser):
         dest="db_init",
         help="Forces database initialization before tests",
     )
+    group.addoption(
+        "--without-db-init",
+        action="store_true",
+        dest="no_db_init",
+        help="Forces NO database initialization before tests",
+    )
     group.addoption(
         "--integration",
         action="append",
@@ -337,7 +343,7 @@ def initialize_airflow_tests(request):
 
     # Initialize Airflow db if required
     lock_file = os.path.join(airflow_home, ".airflow_db_initialised")
-    if not skip_db_tests:
+    if not skip_db_tests and not request.config.option.no_db_init:
         if request.config.option.db_init:
             from tests_common.test_utils.db import initial_db_init
 
diff --git a/scripts/docker/entrypoint_ci.sh b/scripts/docker/entrypoint_ci.sh
index a53a888a1665c..b7a6df4094668 100755
--- a/scripts/docker/entrypoint_ci.sh
+++ b/scripts/docker/entrypoint_ci.sh
@@ -349,7 +349,9 @@ function check_airflow_python_client_installation() {
 }
 
 function start_api_server_with_examples(){
-    if [[ ${START_API_SERVER_WITH_EXAMPLES=} != "true" ]]; then
+    # check if we should not start the api server with examples by checking if both
+    # START_API_SERVER_WITH_EXAMPLES is false AND the TEST_GROUP env var is not equal to "system"
+    if [[ ${START_API_SERVER_WITH_EXAMPLES=} != "true" && ${TEST_GROUP:=""} != "system" ]]; then
         return
     fi
     export AIRFLOW__CORE__LOAD_EXAMPLES=True

```


## Example 3 (Repo: borgbackup/borg, PR #8714: [implement padme chunk size obfuscation (SPEC 250), fixes #8705](https://github.com/borgbackup/borg/pull/8714))

**Output (Synthesized Issue):**
> **Backup files have inconsistent compressed sizes**
>
> When creating backups with Borg, the compressed size of files often varies significantly, even for files of similar size. This makes it difficult to estimate storage requirements and can lead to inefficient use of storage space.
> 
> Compressed file sizes are influenced by factors such as the compression algorithm used, the compression level, and the content of the file itself. However, even for files with similar content, the compressed sizes can vary widely due to the way data is chunked and compressed.
> 
> For example, I have observed that two text files of approximately 1MB in size can have compressed sizes ranging from 10KB to 100KB, making it difficult to predict the required storage space for backups.
> 
> It would be helpful if Borg could provide a more consistent and predictable compressed file size, particularly for files with similar content and size. This would enable better storage planning and capacity management for backup repositories.

**Input (Diff that generated the above issue):**
```diff
diff --git a/src/borg/archiver/help_cmd.py b/src/borg/archiver/help_cmd.py
index b9f9e15214..40ce591125 100644
--- a/src/borg/archiver/help_cmd.py
+++ b/src/borg/archiver/help_cmd.py
@@ -470,6 +470,15 @@ class HelpMixIn:
               ...
               123: 8MiB (max.)
 
+            *Padmé padding* (deterministic)
+
+            ::
+
+              250: pads to sums of powers of 2, max 12% overhead
+
+            Uses the Padmé algorithm to deterministically pad the compressed size to a sum of
+            powers of 2, limiting overhead to 12%. See https://lbarman.ch/blog/padme/ for details.
+
         Examples::
 
             borg create --compression lz4 REPO::ARCHIVE data
@@ -481,7 +490,8 @@ class HelpMixIn:
             borg create --compression auto,lzma ...
             borg create --compression obfuscate,110,none ...
             borg create --compression obfuscate,3,auto,zstd,10 ...
-            borg create --compression obfuscate,2,zstd,6 ...

"""
+            borg create --compression obfuscate,2,zstd,6 ...
+            borg create --compression obfuscate,250,zstd,3 ...

"""
     )
 
     def do_help(self, parser, commands, args):
diff --git a/src/borg/compress.pyx b/src/borg/compress.pyx
index 46013274a6..404a6ac4b0 100644
--- a/src/borg/compress.pyx
+++ b/src/borg/compress.pyx
@@ -16,16 +16,18 @@ decompressor.
 """
 
 from argparse import ArgumentTypeError
+import math
 import random
 from struct import Struct
 import zlib
 
+import math
+
 try:
     import lzma
 except ImportError:
     lzma = None
 
-
 from .constants import MAX_DATA_SIZE
 from .helpers import Buffer, DecompressionError
 
@@ -556,6 +558,8 @@ class ObfuscateSize(CompressorBase):
         elif 110 <= level <= 123:
             self._obfuscate = self._random_padding_obfuscate
             self.max_padding_size = 2 ** (level - 100)  # 1kiB .. 8MiB
+        elif level == 250:  # Padmé
+            self._obfuscate = self._padme_obfuscate
 
     def _obfuscate(self, compr_size):
         # implementations need to return the size of obfuscation data,
@@ -600,6 +604,24 @@ class ObfuscateSize(CompressorBase):
             self.compressor = compressor_cls()
         return self.compressor.decompress(meta, compressed_data)  # decompress data
 
+    
+    def _padme_obfuscate(self, compr_size):
+        if compr_size < 2:
+            return 0
+
+        E = math.floor(math.log2(compr_size))  # Get exponent (power of 2)
+         
+        S = math.floor(math.log2(E)) + 1
+        lastBits = E - S
+        bitMask = (2 ** lastBits - 1)
+
+        padded_size = (compr_size + bitMask) & ~bitMask  # Apply rounding
+
+        # Ensure max 12% overhead
+        max_allowed = int(compr_size * 1.12)
+        final_size = min(padded_size, max_allowed)
+
+        return final_size - compr_size # return padding value
 
 # Maps valid compressor names to their class
 COMPRESSOR_TABLE = {
diff --git a/src/borg/testsuite/compress_test.py b/src/borg/testsuite/compress_test.py
index c294b5ff89..70bc1cec3f 100644
--- a/src/borg/testsuite/compress_test.py
+++ b/src/borg/testsuite/compress_test.py
@@ -210,3 +210,33 @@ def test_specified_compression_level(c_type, c_name, c_levels):
 def test_invalid_compression_level(invalid_spec):
     with pytest.raises(argparse.ArgumentTypeError):
         CompressionSpec(invalid_spec)
+
+
+@pytest.mark.parametrize(
+    "data_length, expected_padding",
+    [
+        (0, 0),
+        (1, 0),
+        (10, 0),
+        (100, 4),
+        (1000, 24),
+        (10000, 240),
+        (20000, 480),
+        (50000, 1200),
+        (100000, 352),
+        (1000000, 15808),
+        (5000000, 111808),
+        (10000000, 223616),
+        (20000000, 447232),
+    ],
+)
+def test_padme_obfuscation(data_length, expected_padding):
+    compressor = Compressor(name="obfuscate", level=250, compressor=Compressor("none"))
+    data = b"x" * data_length
+    meta, compressed = compressor.compress({}, data)
+
+    expected_padded_size = data_length + expected_padding
+
+    assert (
+        len(compressed) == expected_padded_size
+    ), f"For {data_length}, expected {expected_padded_size}, got {len(compressed)}"

```


## Example 4 (Repo: bottlepy/bottle, PR #1482: [Make FileUpload.save accept Path instance for destination](https://github.com/bottlepy/bottle/pull/1482))

**Output (Synthesized Issue):**
> **Unable to save uploaded files to specific directory paths**
>
> When using the `FileUpload.save()` method to save an uploaded file, the `destination` parameter only accepts string paths, not `pathlib.Path` instances. This causes issues when working with paths constructed from `Path` objects, as they have to be converted to strings before passing them to `FileUpload.save()`.
> 
> For example, if I have a directory path constructed as a `Path` object:
> 
> ```python
> import pathlib
> 
> uploads_dir = pathlib.Path('/var/www/uploads')
> ```
> 
> And then try to save an uploaded file to a subdirectory using:
> 
> ```python
> uploaded_file = request.files.get('file_input')
> save_path = uploads_dir / 'user_uploads' / uploaded_file.filename
> uploaded_file.save(save_path)
> ```
> 
> This will raise a `TypeError` because `FileUpload.save()` expects a string for the `destination` parameter, but `save_path` is a `Path` object.
> 
> It would be helpful if `FileUpload.save()` could accept `Path` instances directly, avoiding the need to convert them to strings manually before passing them as the `destination`.

**Input (Diff that generated the above issue):**
```diff
diff --git a/bottle.py b/bottle.py
index 38a9732f..cba9f44c 100755
--- a/bottle.py
+++ b/bottle.py
@@ -76,6 +76,7 @@ def _cli_patch(cli_args):  # pragma: no coverage
 from tempfile import NamedTemporaryFile
 from traceback import format_exc, print_exc
 from unicodedata import normalize
+from pathlib import Path
 
 try:
     from ujson import dumps as json_dumps, loads as json_lds
@@ -2673,6 +2674,8 @@ def save(self, destination, overwrite=False, chunk_size=2 ** 16):
             :param overwrite: If True, replace existing files. (default: False)
             :param chunk_size: Bytes to read at a time. (default: 64kb)
         """
+        if isinstance(destination, Path):
+            destination = str(destination)
         if isinstance(destination, str):  # Except file-likes here
             if os.path.isdir(destination):
                 destination = os.path.join(destination, self.filename)

```


## Example 5 (Repo: celery/celery, PR #9655: [Fix for apply_async(ignore_result=False)](https://github.com/celery/celery/pull/9655))

**Output (Synthesized Issue):**
> **Task results not being stored when `ignore_result=False`**
>
> When using `apply_async(ignore_result=False)` to execute a Celery task, the task result is not being stored even though `ignore_result` is set to `False`. This seems to contradict the expected behavior, where setting `ignore_result=False` should ensure that the task result is persisted.
> 
> This issue appears to be related to the `task_ignore_results` setting in the Celery configuration. Even when `ignore_result=False` is passed to `apply_async`, the task result is not being stored if `task_ignore_results=True` in the Celery configuration.
> 
> This behavior makes it difficult to reliably retrieve task results when executing tasks asynchronously, as the `ignore_result` parameter does not seem to override the global `task_ignore_results` setting as expected.

**Input (Diff that generated the above issue):**
```diff
diff --git a/celery/app/trace.py b/celery/app/trace.py
index 2e8cf8a318..d2c233cba9 100644
--- a/celery/app/trace.py
+++ b/celery/app/trace.py
@@ -327,7 +327,7 @@ def build_tracer(name, task, loader=None, hostname=None, store_errors=True,
     fun = task if task_has_custom(task, '__call__') else task.run
 
     loader = loader or app.loader
-    ignore_result = task.ignore_result
+    ignore_result = task.request.ignore_result
     track_started = task.track_started
     track_started = not eager and (task.track_started and not ignore_result)
 

```


## Example 6 (Repo: certbot/certbot, PR #10258: [Add certbot-dns-cdmon to third-party plugins list](https://github.com/certbot/certbot/pull/10258))

**Output (Synthesized Issue):**
> **Add Support for DNS Authentication with cdmon**
>
> Certbot currently lacks support for automating DNS challenges when using cdmon's DNS hosting service. As a user of cdmon, I would like to be able to obtain and renew Let's Encrypt SSL/TLS certificates for my domains managed by cdmon's DNS without needing to manually create and remove DNS TXT records for each certificate issuance or renewal.
> 
> Having to manually create and remove DNS TXT records for Let's Encrypt validation is tedious and error-prone, especially when managing multiple domains and needing to renew certificates regularly. Automating this process through a cdmon DNS plugin for Certbot would greatly improve the user experience and reduce the risk of failed validation due to misconfigurations or missed cleanup of DNS records.
> 
> The existing third-party plugin options do not currently support cdmon's DNS service, so adding this new plugin would fill a gap and allow cdmon users to fully automate the certificate lifecycle management through Certbot.

**Input (Diff that generated the above issue):**
```diff
diff --git a/certbot/docs/using.rst b/certbot/docs/using.rst
index b3ab3cd954..b288692d04 100644
--- a/certbot/docs/using.rst
+++ b/certbot/docs/using.rst
@@ -330,6 +330,7 @@ dns-stackit_       Y    N    DNS Authentication using STACKIT DNS
 dns-ionos_         Y    N    DNS Authentication using IONOS Cloud DNS
 dns-mijn-host_     Y    N    DNS Authentication using mijn.host DNS
 nginx-unit_        Y    Y    Automates obtaining and installing a certificate with Nginx Unit
+dns-cdmon_         Y    N    DNS Authentication using cdmon's API
 ================== ==== ==== =================================================================
 
 .. _haproxy: https://github.com/greenhost/certbot-haproxy
@@ -361,6 +362,7 @@ nginx-unit_        Y    Y    Automates obtaining and installing a certificate wi
 .. _dns-ionos: https://github.com/ionos-cloud/certbot-dns-ionos-cloud
 .. _dns-mijn-host: https://github.com/mijnhost/certbot-dns-mijn-host
 .. _nginx-unit: https://github.com/kea/certbot-nginx-unit
+.. _dns-cdmon: https://github.com/rascazzione/certbot-dns-cdmon
 
 If you're interested, you can also :ref:`write your own plugin <dev-plugin>`.
 

```


## Example 7 (Repo: cherrypy/cherrypy, PR #2022: [[pre-commit.ci] pre-commit autoupdate](https://github.com/cherrypy/cherrypy/pull/2022))

**Output (Synthesized Issue):**
> **Pre-commit hooks are not working correctly**
>
> There seems to be an issue with the pre-commit hooks not working as expected in this repository. I've noticed that some static analysis tools like flake8, pydocstyle, and yamllint are not catching certain code style violations or formatting issues. Additionally, the pre-commit hooks for checking trailing whitespace and removing tabs don't seem to be functioning properly. This is leading to commits with style inconsistencies being merged into the codebase, which can make it harder to maintain code quality over time.

**Input (Diff that generated the above issue):**
```diff
diff --git a/.github/ISSUE_TEMPLATE.md b/.github/ISSUE_TEMPLATE.md
index af86b79f9..dbf77f798 100644
--- a/.github/ISSUE_TEMPLATE.md
+++ b/.github/ISSUE_TEMPLATE.md
@@ -1,12 +1,12 @@
 <!--
-**** DELETE THIS BLOCK ****  
+**** DELETE THIS BLOCK ****
 
 Thanks for filing an issue!  Please keep issues limited to bug reports,
 feature requests, and other general issues. For support questions, please feel
 free to reach out on stackoverflow:
 https://stackoverflow.com/questions/tagged/cherrypy
 
-**** /DELETE THIS BLOCK ****  
+**** /DELETE THIS BLOCK ****
 -->
 
 **I'm submitting a ...**
diff --git a/.pre-commit-config.yaml b/.pre-commit-config.yaml
index 623ad9872..29eee6851 100644
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@ -9,7 +9,7 @@ repos:
 #     - --in-place
 
 - repo: https://github.com/pre-commit/pre-commit-hooks.git
-  rev: v1.1.1
+  rev: v5.0.0
   hooks:
   - id: trailing-whitespace
     exclude: cherrypy/test/static/index.html
@@ -40,7 +40,7 @@ repos:
   - id: pydocstyle
 
 - repo: https://github.com/PyCQA/flake8.git
-  rev: 7.1.0
+  rev: 7.2.0
   hooks:
   - id: flake8
     additional_dependencies:
@@ -50,7 +50,7 @@ repos:
     # - flake8-pytest-style ~= 1.7.2
 
 - repo: https://github.com/Lucas-C/pre-commit-hooks.git
-  rev: v1.5.4
+  rev: v1.5.5
   hooks:
   - id: remove-tabs
 
@@ -60,7 +60,7 @@ repos:
   - id: forbid-html-img-without-alt-text
 
 - repo: https://github.com/adrienverge/yamllint.git
-  rev: v1.34.0
+  rev: v1.37.0
   hooks:
   - id: yamllint
     files: \.(yaml|yml)$

```


---

# Appendix: Prompts Used

## System Prompt

The overall instruction given to the model:

```yaml
You are an AI assistant helping a software development team. Your task is to analyze the provided text from a *merged* GitHub Pull Request (including description, comments, commits, and diff) and potentially related open issues from the same repository. Based *only* on this information, generate the text (title and body) for a *new*, plausible GitHub issue that this Pull Request *appears* to resolve. Crucially, the generated issue should describe the **problem or symptoms** from the perspective of someone encountering the issue *before* the fix was made. Avoid detailing the specific solution implemented in the PR. Focus on creating a realistic-sounding issue (like a bug report or feature request) that logically connects to the changes shown in the PR, but sounds like it was written without knowledge of the final fix. Do not invent external context. Output *only* the issue title and body in markdown format, starting with the title.
Example Output Format:
# Issue Title

This is the issue body...

```

## LLM Prompt Examples

These are examples of the specific, detailed prompts provided to the model for individual tasks, typically including the code diff and context.

```yaml
Repository: ansible/ansible


--- Context: Existing Open Issues ---
Issue 1 (Number: 84928):
  Title: Playbook for Windows failed when delegate_to localhost
  Body: [Omitted due to length (5816 > 2000 chars)]
----------
Issue 2 (Number: 84923):
  Title: Handle None return in _get_collection_name_from_path() to prevent TypeError
  Body (Preview):
##### SUMMARY

Fixes the issue  where `_get_collection_name_from_path()` can return `None`, causing errors like `TypeError: sequence item 0: expected str instance, NoneType found`. This change adds proper handling for the `None` return value, preventing crashes when working with nested `ansible_collections` trees.

- Added check for `None` return from `_get_collection_name_from_path()` in `ansible.utils.collection_loader`.
- Prevented `None` from being used as a key in dictionaries, which p...
----------
Issue 3 (Number: 84911):
  Title: Fix AnsibleModule.tmpdir base dir race condition
  Body (Preview):
##### SUMMARY

If the base directory of the temporary directory is created between [checking if it doesn't exist](https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/basic.py#L474) and [trying to create it](https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/basic.py#L476), dir=None is passed to [tempfile.mkdtemp](https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/basic.py#L490).

Now the race condition behaves the same as if [checkin...
----------
Issue 4 (Number: 84897):
  Title: Allow user to silent the warning when reserved name variable is used
  Body: [Omitted due to length (2774 > 2000 chars)]
----------
Issue 5 (Number: 84926):
  Title: Disconnect `ssh` connection plugin verbosity from Ansible verbosity
  Body (Preview):
SSH connection plugin verbosity is hardcoded to match Ansible's verbosity (e.g., running Ansible with `-vvv` applies `-vvv` to all `ssh` invocations as well). This causes a ridiculous amount of unnecessary logging/storage overhead (especially for AAP jobs that nearly always run with increased verbosity), pollutes `raw` outputs, interpreter discovery diagnostics, and more. It also complicates attaining 100% code coverage in some interpreter discovery cases, since `stderr` always contains junk.

A...
----------
(2 issue bodies omitted due to length limit of 2000 chars.)

--- Pull Request #84869 Details ---
PR Title: ansible-pull fix adhoc output inconsistencies on changed

PR Body:
Remove changes to adhoc output that could throw off change detection on ansible pull

fixes #84863

##### ISSUE TYPE

- Bugfix Pull Request



--- Review Comments ---

suggestion
    cd "${repo_dir}"
    date > forced_change
    git add forced_change
    git commit -m "forced changed"
    cd -


suggestion
    # test for https://github.com/ansible/ansible/issues/13688
    if grep MAGICKEYWORD "${temp_log}"; then
        cat "${temp_log}"
        echo "Ran the playbook, found MAGICKEYWORD in output."
        exit 1
    fi


the change from `" ".join(playbooks)` to `" ".join(str(playbooks))` in the `select_playbook` method looks like it might be incorrect. `str(playbooks)` would stringify the list itself, rather than joining the path strings within it. Was this intended? It seems like it should revert to `" ".join(playbooks)`.


--- Issue Comments ---

[eoli3n](https://github.com/eoli3n) can you confirm this fixes your issue (sans workaround)?


--- Commit Messages ---

ansible-pull, fix change detection

Two fixes for single bug:
  - ignore callback changes for adhoc
  - allow 'yaml' change matching

Add 'on change' tests

why?t

linter cleanups

commenetary

clog

linter conflict

Apply suggestions from code review

Co-authored-by: Abhijeet Kasurde <akasurde@redhat.com>

document on output also
clean/reset env vars

need debug


--- Diff ---

diff --git a/changelogs/fragments/pull_changed_fix.yml b/changelogs/fragments/pull_changed_fix.yml
new file mode 100644
index 00000000000000..ac6f04e77b70d0
--- /dev/null
+++ b/changelogs/fragments/pull_changed_fix.yml
@@ -0,0 +1,2 @@
+bugfixes:
+  - ansible-pull change detection will now work independant of callback or result format settings.
diff --git a/lib/ansible/cli/pull.py b/lib/ansible/cli/pull.py
index ee24c9ff9aabfb..dda02aa3f33025 100755
--- a/lib/ansible/cli/pull.py
+++ b/lib/ansible/cli/pull.py
@@ -31,6 +31,34 @@
 
 display = Display()
 
+SAFE_OUTPUT_ENV = {
+    'ANSIBLE_CALLBACK_RESULT_FORMAT': 'json',
+    'ANSIBLE_LOAD_CALLBACK_PLUGINS': '0',
+}
+
+
+def safe_output_env(f):
+
+    def wrapper(*args, **kwargs):
+
+        orig = {}
+
+        for k, v in SAFE_OUTPUT_ENV.items():
+            orig[k] = os.environ.get(k, None)
+            os.environ[k] = v
+
+        result = f(*args, **kwargs)
+
+        for key in orig.keys():
+            if orig[key] is None:
+                del os.environ[key]
+            else:
+                os.environ[key] = orig[key]
+
+        return result
+
+    return wrapper
+
 
 class PullCLI(CLI):
     """ Used to pull a remote copy of ansible on each managed node,
@@ -42,7 +70,7 @@ class PullCLI(CLI):
         you should use an external scheduler and/or locking to ensure there are no clashing operations.
 
         The setup playbook can be tuned to change the cron frequency, logging locations, and parameters to ansible-pull.
-        This is useful both for extreme scale-out as well as periodic remediation.
+        This is useful both for extreme scale-out and periodic remediation.
         Usage of the 'fetch' module to retrieve logs from ansible-pull runs would be an
         excellent way to gather and analyze remote logs from ansible-pull.
     """
@@ -76,8 +104,9 @@ def _get_inv_cli():
         return inv_opts
 
     def init_parser(self):
-        """ create an options parser for bin/ansible """
+        """ Specific args/option parser for pull """
 
+        # signature is different from parent as caller should not need to add usage/desc
         super(PullCLI, self).init_parser(
             usage='%prog -U <repository> [options] [<playbook.yml>]',
             desc="pulls playbooks from a VCS repo and executes them on target host")
@@ -106,10 +135,12 @@ def init_parser(self):
                                  help='path to the directory to which Ansible will checkout the repository.')
         self.parser.add_argument('-U', '--url', dest='url', default=None, help='URL of the playbook repository')
         self.parser.add_argument('--full', dest='fullclone', action='store_true', help='Do a full clone, instead of a shallow one.')
+        # TODO: resolve conflict with check mode, added manually below
         self.parser.add_argument('-C', '--checkout', dest='checkout',
                                  help='branch/tag/commit to checkout. Defaults to behavior of repository module.')
         self.parser.add_argument('--accept-host-key', default=False, dest='accept_host_key', action='store_true',
                                  help='adds the hostkey for the repo url if not already added')
+        # Overloaded with adhoc ... but really passthrough to adhoc
         self.parser.add_argument('-m', '--module-name', dest='module_name', default=self.DEFAULT_REPO_TYPE,
                                  help='Repository module name, which ansible will use to check out the repo. Choices are %s. Default is %s.'
                                       % (self.REPO_CHOICES, self.DEFAULT_REPO_TYPE))
@@ -121,7 +152,7 @@ def init_parser(self):
         self.parser.add_argument('--track-subs', dest='tracksubs', default=False, action='store_true',
                                  help='submodules will track the latest changes. This is equivalent to specifying the --remote flag to git submodule update')
         # add a subset of the check_opts flag group manually, as the full set's
-        # shortcodes conflict with above --checkout/-C
+        # shortcodes conflict with above --checkout/-C, see to-do above
         self.parser.add_argument("--check", default=False, dest='check', action='store_true',
                                  help="don't make any changes; instead, try to predict some of the changes that may occur")
         self.parser.add_argument("--diff", default=C.DIFF_ALWAYS, dest='diff', action='store_true',
@@ -177,7 +208,7 @@ def run(self):
             limit_opts = 'localhost,127.0.0.1'
         base_opts = '-c local '
         if context.CLIARGS['verbosity'] > 0:
-            base_opts += ' -%s' % ''.join(["v" for x in range(0, context.CLIARGS['verbosity'])])
+            base_opts += ' -%s' % ''.join(["v" for dummy in range(0, context.CLIARGS['verbosity'])])
 
         # Attempt to use the inventory passed in as an argument
         # It might not yet have been downloaded so use localhost as default
@@ -250,14 +281,15 @@ def run(self):
         # RUN the Checkout command
         display.debug("running ansible with VCS module to checkout repo")
         display.vvvv('EXEC: %s' % cmd)
-        rc, b_out, b_err = run_cmd(cmd, live=True)
+        rc, b_out, b_err = safe_output_env(run_cmd)(cmd, live=True)
 
+        print('BCS', context.CLIARGS['ifchanged'], b'"changed": true' not in b_out, b"changed: True" not in b_out)
         if rc != 0:
             if context.CLIARGS['force']:
                 display.warning("Unable to update repository. Continuing with (forced) run of playbook.")
             else:
                 return rc
-        elif context.CLIARGS['ifchanged'] and b'"changed": true' not in b_out:
+        elif context.CLIARGS['ifchanged'] and (b'"changed": true' not in b_out or b"changed: True" not in b_out):
             display.display("Repository has not changed, quitting.")
             return 0
 
@@ -347,7 +379,7 @@ def select_playbook(path):
             if 0 < len(errors):
                 display.warning("
".join(errors))
             elif len(playbooks) == len(context.CLIARGS['args']):
-                playbook = " ".join(playbooks)
+                playbook = " ".join(str(playbooks))
             return playbook
         else:
             fqdn = socket.getfqdn()
diff --git a/test/integration/targets/ansible-pull/runme.sh b/test/integration/targets/ansible-pull/runme.sh
index fd97c707f05dc7..3c171c5b1533b0 100755
--- a/test/integration/targets/ansible-pull/runme.sh
+++ b/test/integration/targets/ansible-pull/runme.sh
@@ -27,6 +27,23 @@ cd "${repo_dir}"
     git commit -m "Initial commit."
 )
 
+function change_repo {
+    cd "${repo_dir}"
+    date > forced_change
+    git add forced_change
+    git commit -m "forced changed"
+    cd -
+}
+
+function no_change_tests {
+    # test for https://github.com/ansible/ansible/issues/13688
+    if grep MAGICKEYWORD "${temp_log}"; then
+        cat "${temp_log}"
+        echo "Ran the playbook, found MAGICKEYWORD in output."
+        exit 1
+    fi
+}
+
 function pass_tests {
 	# test for https://github.com/ansible/ansible/issues/13688
 	if ! grep MAGICKEYWORD "${temp_log}"; then
@@ -66,6 +83,7 @@ function pass_tests_multi {
 
 export ANSIBLE_INVENTORY
 export ANSIBLE_HOST_PATTERN_MISMATCH
+export ANSIBLE_DEBUG=1
 
 unset ANSIBLE_INVENTORY
 unset ANSIBLE_HOST_PATTERN_MISMATCH
@@ -97,3 +115,31 @@ export ANSIBLE_CACHE_PLUGIN=jsonfile ANSIBLE_CACHE_PLUGIN_CONNECTION=./
 ansible-pull -d "${pull_dir}" -U "${repo_dir}" "$@" gather_facts.yml
 ansible-pull -d "${pull_dir}" -U "${repo_dir}" --flush-cache "$@" test_empty_facts.yml
 unset ANSIBLE_CACHE_PLUGIN ANSIBLE_CACHE_PLUGIN_CONNECTION
+
+#### CHACHCHCHANGES!
+echo 'setup for change detection'
+ORIG_CONFIG="${ANSIBLE_CONFIG}"
+unset ANSIBLE_CONFIG
+
+echo 'test no run on no changes'
+ansible-pull -d "${pull_dir}" -U "${repo_dir}" --only-if-changed "$@" | tee "${temp_log}"
+no_change_tests
+
+echo 'test run on changes'
+change_repo
+ansible-pull -d "${pull_dir}" -U "${repo_dir}" --only-if-changed "$@" | tee "${temp_log}"
+pass_tests
+
+# test changed with non yaml result format, ensures we ignore callback or format changes for adhoc/change detection
+echo 'test no run on no changes, yaml result format'
+ANSIBLE_CALLBACK_RESULT_FORMAT='yaml' ansible-pull -d "${pull_dir}" -U "${repo_dir}" --only-if-changed "$@" | tee "${temp_log}"
+no_change_tests
+
+echo 'test run on changes, yaml result format'
+change_repo
+ANSIBLE_CALLBACK_RESULT_FORMAT='yaml' ansible-pull -d "${pull_dir}" -U "${repo_dir}" --only-if-changed "$@" | tee "${temp_log}"
+pass_tests
+
+if [ "${ORIG_CONFIG}" != "" ]; then
+  export ANSIBLE_CONFIG="${ORIG_CONFIG}"
+fi


--- Task ---
Based on the PR details and the context from existing issues provided above, please generate the text (title and body) for a new, plausible GitHub issue that the pull request #84869 appears to resolve. Output only the issue title and body in markdown format.

```

```yaml
Repository: apache/airflow


--- Context: Existing Open Issues ---
Issue 1 (Number: 48765):
  Title: Configuring SequentialExecutor results in very non-obvious error
  Body (Preview):
### Body

If sequential executor is configured, an unhelpful error is emitted

It should make it clear that SequentialExecutor is disabled.

Maybe it should even "upgrade" to local executor?


[2025-04-03T12:43:19.920-0700] {cli_parser.py:68} ERROR - Failed to load CLI commands from executor: ::SequentialExecutor
Traceback (most recent call last):
  File "/Users/dstandish/code/airflow/airflow-core/src/airflow/utils/module_loading.py", line 35, in import_string
    module_path, class_name = do...
----------
Issue 2 (Number: 48781):
  Title: misc: fix spelling in md,py,rst,yaml files
  Body: [Omitted due to length (2082 > 2000 chars)]
----------
Issue 3 (Number: 48795):
  Title: fix(serialized_dag): skip asset dag dep when the asset ref cannot be resolved into a valid asset
  Body: [Omitted due to length (2417 > 2000 chars)]
----------
Issue 4 (Number: 48770):
  Title: Dev: Auto-update Airflow core version in release mgmt command
  Body: [Omitted due to length (2117 > 2000 chars)]
----------
Issue 5 (Number: 48786):
  Title: Grid view stops loading when there is a pending task to be expanded
  Body: [Omitted due to length (9863 > 2000 chars)]
----------
(4 issue bodies omitted due to length limit of 2000 chars.)

--- Pull Request #48699 Details ---
PR Title: Enable task sdk for system tests

PR Body:
The two main components are:

1) Start an api server within breeze for system-tests test group. That
   gives any tasks started with the sdk a server to communicate with.
2) Update dag.test to support task sdk interaction with the executor.

### Testing
Tested end to end with the ECS executor converted to support task sdk

<!--
 Licensed to the Apache Software Foundation (ASF) under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  The ASF licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing,
 software distributed under the License is distributed on an
 "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 KIND, either express or implied.  See the License for the
 specific language governing permissions and limitations
 under the License.
 -->

<!--
Thank you for contributing! Please make sure that your code changes
are covered with tests. And in case of new features or big changes
remember to adjust the documentation.

Feel free to ping committers for the review!

In case of an existing issue, reference it using one of the following:

closes: #ISSUE
related: #ISSUE

How to write a good git commit message:
http://chris.beams.io/posts/git-commit/
-->



<!-- Please keep an empty line above the dashes. -->
---
**^ Add meaningful description above**
Read the **[Pull Request Guidelines](https://github.com/apache/airflow/blob/main/contributing-docs/05_pull_requests.rst#pull-request-guidelines)** for more information.
In case of fundamental code changes, an Airflow Improvement Proposal ([AIP](https://cwiki.apache.org/confluence/display/AIRFLOW/Airflow+Improvement+Proposals)) is needed.
In case of a new dependency, check compliance with the [ASF 3rd Party License Policy](https://www.apache.org/legal/resolved.html#category-x).
In case of backwards incompatible changes please leave a note in a newsfragment file, named `{pr_number}.significant.rst` or `{issue_number}.significant.rst`, in [airflow-core/newsfragments](https://github.com/apache/airflow/tree/main/airflow-core/newsfragments).



--- Review Comments ---

@jedcunningham The relevant piece you and I were chatting about the other day

This piece is lifted from the scheduler (as much of dag.test code is).

suggestion
        # System tests will be inited with the api server started


This feels redundant with `--with-db-init`. If `--with-db-init` is not set then no DB initialization should happen. Why do we need this flag?

Chatted with Jed offline, he's OOTO for the next little while, but he did say this looked sufficient for the testing use-case.

Good catch, the "with" should probably also be "when" too. I'll make the change :)

Yeah, there is a very confusing venn diagram here of possible paths. Really with should be called "force-db-init" since it only forces it to happen, it can happen when that thing is set to false (which you would think means force do not, but no, it's only force in the true case). And so mine is the opposite, covering that case. It forces no db-init in the pytest plugin (not even evaluating other paths that could lead to inits).

I know it's confusing, hopefully that makes sense!

I see, that makes sense :) Could you please update the `help` of both commands to basically explain what you just explained, it could very helpful for others (or even us in some time xD). Could you also mention they are mutually exclusive (might be obvious but ...)


--- Commit Messages ---

Enable task sdk for system testing

The two main components are:

1) Start an api server within breeze for system-tests test group. That
   gives any tasks started with the sdk a server to communicate with.
2) Update dag.test to support task sdk interaction with the executor.

Reduce scope of without-db-init usage


--- Diff ---

diff --git a/Dockerfile.ci b/Dockerfile.ci
index d238e7b01a908..304fdea38c0ba 100644
--- a/Dockerfile.ci
+++ b/Dockerfile.ci
@@ -1023,7 +1023,9 @@ function check_airflow_python_client_installation() {
 }
 
 function start_api_server_with_examples(){
-    if [[ ${START_API_SERVER_WITH_EXAMPLES=} != "true" ]]; then
+    # check if we should not start the api server with examples by checking if both
+    # START_API_SERVER_WITH_EXAMPLES is false AND the TEST_GROUP env var is not equal to "system"
+    if [[ ${START_API_SERVER_WITH_EXAMPLES=} != "true" && ${TEST_GROUP:=""} != "system" ]]; then
         return
     fi
     export AIRFLOW__CORE__LOAD_EXAMPLES=True
diff --git a/airflow-core/src/airflow/executors/workloads.py b/airflow-core/src/airflow/executors/workloads.py
index 4d9d2286141a7..83d7feed5556f 100644
--- a/airflow-core/src/airflow/executors/workloads.py
+++ b/airflow-core/src/airflow/executors/workloads.py
@@ -98,17 +98,22 @@ class ExecuteTask(BaseWorkload):
 
     @classmethod
     def make(
-        cls, ti: TIModel, dag_rel_path: Path | None = None, generator: JWTGenerator | None = None
+        cls,
+        ti: TIModel,
+        dag_rel_path: Path | None = None,
+        generator: JWTGenerator | None = None,
+        bundle_info: BundleInfo | None = None,
     ) -> ExecuteTask:
         from pathlib import Path
 
         from airflow.utils.helpers import log_filename_template_renderer
 
         ser_ti = TaskInstance.model_validate(ti, from_attributes=True)
-        bundle_info = BundleInfo(
-            name=ti.dag_model.bundle_name,
-            version=ti.dag_run.bundle_version,
-        )
+        if not bundle_info:
+            bundle_info = BundleInfo(
+                name=ti.dag_model.bundle_name,
+                version=ti.dag_run.bundle_version,
+            )
         fname = log_filename_template_renderer()(ti=ti)
         token = ""
 
diff --git a/airflow-core/src/airflow/models/dag.py b/airflow-core/src/airflow/models/dag.py
index 8ca0f3383303b..f8c5eec3c7e02 100644
--- a/airflow-core/src/airflow/models/dag.py
+++ b/airflow-core/src/airflow/models/dag.py
@@ -29,6 +29,7 @@
 from contextlib import ExitStack
 from datetime import datetime, timedelta
 from functools import cache
+from pathlib import Path
 from re import Pattern
 from typing import (
     TYPE_CHECKING,
@@ -76,6 +77,7 @@
     UnknownExecutorException,
 )
 from airflow.executors.executor_loader import ExecutorLoader
+from airflow.executors.workloads import BundleInfo
 from airflow.models.asset import (
     AssetDagRunQueue,
     AssetModel,
@@ -234,10 +236,10 @@ def get_asset_triggered_next_run_info(
     }
 
 
-def _triggerer_is_healthy():
+def _triggerer_is_healthy(session: Session):
     from airflow.jobs.triggerer_job_runner import TriggererJobRunner
 
-    job = TriggererJobRunner.most_recent_job()
+    job = TriggererJobRunner.most_recent_job(session=session)
     return job and job.is_alive()
 
 
@@ -1714,7 +1716,7 @@ def add_logger_if_needed(ti: TaskInstance):
                     self.log.warning("No tasks to run. unrunnable tasks: %s", ids_unrunnable)
                     time.sleep(1)
 
-                triggerer_running = _triggerer_is_healthy()
+                triggerer_running = _triggerer_is_healthy(session)
                 for ti in scheduled_tis:
                     ti.task = tasks[ti.task_id]
 
@@ -1727,8 +1729,26 @@ def add_logger_if_needed(ti: TaskInstance):
                     if use_executor:
                         if executor.has_task(ti):
                             continue
-                        # Send the task to the executor
-                        executor.queue_task_instance(ti, ignore_ti_state=True)
+                        # TODO: Task-SDK: This check is transitionary. Remove once all executors are ported over.
+                        from airflow.executors import workloads
+                        from airflow.executors.base_executor import BaseExecutor
+
+                        if executor.queue_workload.__func__ is not BaseExecutor.queue_workload:  # type: ignore[attr-defined]
+                            workload = workloads.ExecuteTask.make(
+                                ti,
+                                dag_rel_path=Path(self.fileloc),
+                                generator=executor.jwt_generator,
+                                # For the system test/debug purpose, we use the default bundle which uses
+                                # local file system. If it turns out to be a feature people want, we could
+                                # plumb the Bundle to use as a parameter to dag.test
+                                bundle_info=BundleInfo(name="dags-folder"),
+                            )
+                            executor.queue_workload(workload, session=session)
+                            ti.state = TaskInstanceState.QUEUED
+                            session.commit()
+                        else:
+                            # Send the task to the executor
+                            executor.queue_task_instance(ti, ignore_ti_state=True)
                     else:
                         # Run the task locally
                         try:
diff --git a/dev/breeze/src/airflow_breeze/commands/testing_commands.py b/dev/breeze/src/airflow_breeze/commands/testing_commands.py
index 0bbb342d2a8b5..1748b1eb0b8e0 100644
--- a/dev/breeze/src/airflow_breeze/commands/testing_commands.py
+++ b/dev/breeze/src/airflow_breeze/commands/testing_commands.py
@@ -1015,7 +1015,7 @@ def system_tests(
         collect_only=collect_only,
         enable_coverage=enable_coverage,
         forward_credentials=forward_credentials,
-        forward_ports=False,
+        forward_ports=True,
         github_repository=github_repository,
         integration=(),
         keep_env_variables=keep_env_variables,
diff --git a/dev/breeze/src/airflow_breeze/utils/run_tests.py b/dev/breeze/src/airflow_breeze/utils/run_tests.py
index f5412a6af3b7f..e9b442d13a47c 100644
--- a/dev/breeze/src/airflow_breeze/utils/run_tests.py
+++ b/dev/breeze/src/airflow_breeze/utils/run_tests.py
@@ -396,6 +396,9 @@ def generate_args_for_pytest(
             args.append(f"--ignore={group_folder}")
     if test_group not in IGNORE_DB_INIT_FOR_TEST_GROUPS:
         args.append("--with-db-init")
+    if test_group == GroupOfTests.SYSTEM:
+        # System tests will be inited with the api server is started
+        args.append("--without-db-init")
     if test_group == GroupOfTests.PYTHON_API_CLIENT:
         args.append("--ignore-glob=clients/python/tmp/*")
     args.extend(get_suspended_provider_args())
diff --git a/devel-common/src/tests_common/pytest_plugin.py b/devel-common/src/tests_common/pytest_plugin.py
index 222c6c23b5d32..dbe12113dfa7d 100644
--- a/devel-common/src/tests_common/pytest_plugin.py
+++ b/devel-common/src/tests_common/pytest_plugin.py
@@ -224,6 +224,12 @@ def pytest_addoption(parser: pytest.Parser):
         dest="db_init",
         help="Forces database initialization before tests",
     )
+    group.addoption(
+        "--without-db-init",
+        action="store_true",
+        dest="no_db_init",
+        help="Forces NO database initialization before tests",
+    )
     group.addoption(
         "--integration",
         action="append",
@@ -337,7 +343,7 @@ def initialize_airflow_tests(request):
 
     # Initialize Airflow db if required
     lock_file = os.path.join(airflow_home, ".airflow_db_initialised")
-    if not skip_db_tests:
+    if not skip_db_tests and not request.config.option.no_db_init:
         if request.config.option.db_init:
             from tests_common.test_utils.db import initial_db_init
 
diff --git a/scripts/docker/entrypoint_ci.sh b/scripts/docker/entrypoint_ci.sh
index a53a888a1665c..b7a6df4094668 100755
--- a/scripts/docker/entrypoint_ci.sh
+++ b/scripts/docker/entrypoint_ci.sh
@@ -349,7 +349,9 @@ function check_airflow_python_client_installation() {
 }
 
 function start_api_server_with_examples(){
-    if [[ ${START_API_SERVER_WITH_EXAMPLES=} != "true" ]]; then
+    # check if we should not start the api server with examples by checking if both
+    # START_API_SERVER_WITH_EXAMPLES is false AND the TEST_GROUP env var is not equal to "system"
+    if [[ ${START_API_SERVER_WITH_EXAMPLES=} != "true" && ${TEST_GROUP:=""} != "system" ]]; then
         return
     fi
     export AIRFLOW__CORE__LOAD_EXAMPLES=True


--- Task ---
Based on the PR details and the context from existing issues provided above, please generate the text (title and body) for a new, plausible GitHub issue that the pull request #48699 appears to resolve. Output only the issue title and body in markdown format.

```

