# AI GitHub Issue Synthesis Experiment

## Goal

To evaluate the ability of an AI model to synthesize relevant GitHub issue titles and bodies based on code diffs and contextual information.

## Methodology

An AI model was provided with a system prompt and a series of specific prompts (`llm_prompt`) containing code diffs and other context. The model's output (`synthesized_issue`) was recorded. This document summarizes the setup and shows representative examples.

## System Prompt

```yaml
You are an AI assistant helping a software development team. Your task is to analyze the provided text from a *merged* GitHub Pull Request (including description, comments, commits, and diff) and potentially related open issues from the same repository. Based *only* on this information, generate the text (title and body) for a *new*, plausible GitHub issue that this Pull Request *appears* to resolve. Crucially, the generated issue should describe the **problem or symptoms** from the perspective of someone encountering the issue *before* the fix was made. Avoid detailing the specific solution implemented in the PR. Focus on creating a realistic-sounding issue (like a bug report or feature request) that logically connects to the changes shown in the PR, but sounds like it was written without knowledge of the final fix. Do not invent external context. Output *only* the issue title and body in markdown format, starting with the title.
Example Output Format:
# Issue Title

This is the issue body...

```

## LLM Prompt Structure

The prompt provided to the LLM typically included the code diff, repository/PR context, and specific instructions.

<details>
<summary>Click to view full LLM Prompt Example (from first result)</summary>

```yaml
Repository: ansible/ansible


--- Context: Existing Open Issues ---
Issue 1 (Number: 84923):
  Title: Handle None return in _get_collection_name_from_path() to prevent TypeError
  Body (Preview):
##### SUMMARY

Fixes the issue  where `_get_collection_name_from_path()` can return `None`, causing errors like `TypeError: sequence item 0: expected str instance, NoneType found`. This change adds proper handling for the `None` return value, preventing crashes when working with nested `ansible_collections` trees.

- Added check for `None` return from `_get_collection_name_from_path()` in `ansible.utils.collection_loader`.
- Prevented `None` from being used as a key in dictionaries, which p...
----------
Issue 2 (Number: 84922):
  Title: Callbacks do not resolve temlpating for delegate_to
  Body: [Omitted due to length (3938 > 2000 chars)]
----------
Issue 3 (Number: 84859):
  Title: [stable 2.18] needed intesect, not difference (#84839)
  Body (Preview):
fixes #84750

Added tests to verify output when using smart + others

(cherry picked from commit 0d4f00f5c89901e53c2f9c32fa87acac3fed8118)


##### ISSUE TYPE

- Bugfix Pull Request
----------
Issue 4 (Number: 84902):
  Title: [stable-2.17] import_role docs: fix markup for config variable reference
  Body (Preview):
##### SUMMARY
Backport of #84901 to stable-2.17.

##### ISSUE TYPE
- Docs Pull Request
----------
Issue 5 (Number: 84860):
  Title: [stable 2.17] needed intesect, not difference (#84839)
  Body (Preview):
fixes #84750

Added tests to verify output when using smart + others

(cherry picked from commit 0d4f00f5c89901e53c2f9c32fa87acac3fed8118)

##### ISSUE TYPE

- Bugfix Pull Request
----------
(1 issue bodies omitted due to length limit of 2000 chars.)

--- Pull Request #84925 Details ---
PR Title: Update variable names in C.INTERNAL_STATIC_VARS

PR Body:
##### SUMMARY

Related #84914

* Added ansible_check_mode, ansible_play_name, environment, vars, ansible_loop, ansible_loop_var, ansible_index_var, item, and ansible_search_path

* Removed ansible_async_path and duplicate roles_path entry

Am I missing any? https://gist.github.com/s-hertel/ce46f33e666de8045b063a083cd32ba0

Missing:
- https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html#extended-loop-variables
-

##### ISSUE TYPE

- Bugfix Pull Request



--- Issue Comments ---

@s-hertel @bcoca Do we not have tests to cover any of the functionality affected by this change?

this is just increasing the keywords, the actual tests are in  #84914 for the warn_if_reserved

I'll check if we had tests for the purging from inventory, if not, i'll add in the same PR

This could also be consolidated with #84914, or I could add tests for these variables after #84914 is merged.

either way works4me


--- Commit Messages ---

Update variable names in C.INTERNAL_STATIC_VARS

Add ansible_check_mode, ansible_play_name, environment, vars,
ansible_loop, ansible_loop_var, ansible_index_var, item, and
ansible_search_path

Remove ansible_async_path and duplicate roles_path entry


--- Diff ---

diff --git a/lib/ansible/constants.py b/lib/ansible/constants.py
index af60053a3dd445..d8c7089bcb9856 100644
--- a/lib/ansible/constants.py
+++ b/lib/ansible/constants.py
@@ -139,7 +139,7 @@ def __getitem__(self, y):
 INTERNAL_RESULT_KEYS = ('add_host', 'add_group')
 INTERNAL_STATIC_VARS = frozenset(
     [
-        "ansible_async_path",
+        "ansible_check_mode",
         "ansible_collection_name",
         "ansible_config_file",
         "ansible_dependent_role_names",
@@ -147,34 +147,42 @@ def __getitem__(self, y):
         "ansible_config_file",
         "ansible_facts",
         "ansible_forks",
+        "ansible_index_var",
         "ansible_inventory_sources",
         "ansible_limit",
+        "ansible_local",
+        "ansible_loop",
+        "ansible_loop_var",
         "ansible_play_batch",
         "ansible_play_hosts",
         "ansible_play_hosts_all",
+        "ansible_play_name",
         "ansible_play_role_names",
         "ansible_playbook_python",
         "ansible_role_name",
         "ansible_role_names",
         "ansible_run_tags",
+        "ansible_search_path",
         "ansible_skip_tags",
         "ansible_verbosity",
         "ansible_version",
+        "environment",
+        "hostvars",
         "inventory_dir",
         "inventory_file",
         "inventory_hostname",
         "inventory_hostname_short",
+        "item",
         "groups",
         "group_names",
         "omit",
-        "hostvars",
         "playbook_dir",
         "play_hosts",
         "role_name",
         "role_names",
         "role_path",
         "role_uuid",
-        "role_names",
+        "vars",
     ]
 )
 LOCALHOST = ('127.0.0.1', 'localhost', '::1')


--- Task ---
Based on the PR details and the context from existing issues provided above, please generate the text (title and body) for a new, plausible GitHub issue that the pull request #84925 appears to resolve. Output only the issue title and body in markdown format.

```

</details>

## Examples (Input Diff -> Output Issue)

Showing up to 3 examples where the input diff length is no more than 2000 characters.

### Example 1 (Repo: ansible/ansible, PR: {'number': 84925, 'title': 'Update variable names in C.INTERNAL_STATIC_VARS', 'url': 'https://github.com/ansible/ansible/pull/84925'})

**Input (Diff):**

```diff
diff --git a/lib/ansible/constants.py b/lib/ansible/constants.py
index af60053a3dd445..d8c7089bcb9856 100644
--- a/lib/ansible/constants.py
+++ b/lib/ansible/constants.py
@@ -139,7 +139,7 @@ def __getitem__(self, y):
 INTERNAL_RESULT_KEYS = ('add_host', 'add_group')
 INTERNAL_STATIC_VARS = frozenset(
     [
-        "ansible_async_path",
+        "ansible_check_mode",
         "ansible_collection_name",
         "ansible_config_file",
         "ansible_dependent_role_names",
@@ -147,34 +147,42 @@ def __getitem__(self, y):
         "ansible_config_file",
         "ansible_facts",
         "ansible_forks",
+        "ansible_index_var",
         "ansible_inventory_sources",
         "ansible_limit",
+        "ansible_local",
+        "ansible_loop",
+        "ansible_loop_var",
         "ansible_play_batch",
         "ansible_play_hosts",
         "ansible_play_hosts_all",
+        "ansible_play_name",
         "ansible_play_role_names",
         "ansible_playbook_python",
         "ansible_role_name",
         "ansible_role_names",
         "ansible_run_tags",
+        "ansible_search_path",
         "ansible_skip_tags",
         "ansible_verbosity",
         "ansible_version",
+        "environment",
+        "hostvars",
         "inventory_dir",
         "inventory_file",
         "inventory_hostname",
         "inventory_hostname_short",
+        "item",
         "groups",
         "group_names",
         "omit",
-        "hostvars",
         "playbook_dir",
         "play_hosts",
         "role_name",
         "role_names",
         "role_path",
         "role_uuid",
-        "role_names",
+        "vars",
     ]
 )
 LOCALHOST = ('127.0.0.1', 'localhost', '::1')

```

**Output (Synthesized Issue):**

> # Some Ansible variables are missing from INTERNAL_STATIC_VARS
>
> Ansible has a set of internal variables that are reserved and cannot be overridden by users. However, it seems that some important variables are missing from this set, leading to potential naming conflicts or unexpected behavior.
>
> For example, variables like `ansible_check_mode`, `ansible_play_name`, `environment`, `vars`, `ansible_loop`, `ansible_loop_var`, `ansible_index_var`, `item`, and `ansible_search_path` are used internally by Ansible but are not part of the `INTERNAL_STATIC_VARS` set. If a user tries to define a variable with the same name, it could lead to unintended consequences or errors.
>
> It would be beneficial to update the `INTERNAL_STATIC_VARS` set to include all the internal variables used by Ansible, ensuring that they are properly reserved and protected from accidental overrides or naming conflicts.

### Example 2 (Repo: bottlepy/bottle, PR: {'number': 1482, 'title': 'Make FileUpload.save accept Path instance for destination', 'url': 'https://github.com/bottlepy/bottle/pull/1482'})

**Input (Diff):**

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

**Output (Synthesized Issue):**

> # Unable to save FileUpload to Path instances
>
> When attempting to save a `FileUpload` instance to a `Path` object (e.g. from the `pathlib` module), the following error is raised:
>
> ```python
> TypeError: save() argument 1 must be str, not Path
> ```
>
> The `FileUpload.save()` method currently only accepts string paths or file-like objects as the destination parameter. However, it would be more convenient and idiomatic to allow `Path` instances as well, since they provide a modern object-oriented way of handling file paths in Python.
>
> It would be great if the `FileUpload.save()` method could handle `Path` instances seamlessly, either by converting them to strings internally or by accepting `Path` objects directly. This would improve the user experience and make the API more flexible and future-proof.

### Example 3 (Repo: celery/celery, PR: {'number': 9655, 'title': 'Fix for apply_async(ignore_result=False)', 'url': 'https://github.com/celery/celery/pull/9655'})

**Input (Diff):**

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

**Output (Synthesized Issue):**

> # Celery Tasks Not Storing Results Despite `ignore_result=False`
>
> When executing a Celery task with `apply_async(ignore_result=False)`, the task result is not being stored even though `ignore_result` is set to `False`. This issue occurs when the Celery app configuration has `task_ignore_results=True` set globally.
>
> The expected behavior is that setting `ignore_result=False` when calling `apply_async` should override the global `task_ignore_results` setting and force the task result to be stored. However, currently, the task result is not being stored, leading to potential issues when needing to retrieve the result later.
>
> Steps to Reproduce:
>
> 1. Configure Celery app with `task_ignore_results=True` in the config file.
> 2. Define a Celery task.
> 3. Call `apply_async` on the task with `ignore_result=False`.
> 4. Attempt to retrieve the task result.
>
> The task result should be available, but it is not being stored due to the global `task_ignore_results` setting taking precedence over the `ignore_result` argument passed to `apply_async`.
>
> This issue causes inconsistent behavior and can lead to unexpected errors or failures when relying on task results in certain situations.
