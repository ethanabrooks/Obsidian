# working branch / working-data:

## Question

What gcs directory structures can I point dromeus --model at? Context: had to manually save a 70b checkpoint and the directory structure from the online RL trainer looks different from the one in, e.g., llama 70b 3.3 checkpoint.

## Answers

### Correct

````
# Dromeus Model Directory Structures

Based on the code, I can see that Dromeus supports two different model directory structures in GCS:

## 1. V2 Model Structure

This is detected by checking for the existence of an `is_v2` file in the root of the model directory:

```python
is_v2 = gcsfile.exists(gcsfile.join(self.original_model_path, 'is_v2'))
```

```

For V2 models, Dromeus only downloads specific subdirectories from the checkpoint as specified in `checkpoint_subdirs`. This means:

- The model directory should have an `is_v2` marker file
- Only specific subdirectories (defined in `checkpoint_subdirs`) are downloaded
- Each subdirectory is downloaded to the same local directory

## 2. Legacy (V1) Model Structure

If the `is_v2` file is not found, Dromeus treats it as a legacy model and downloads the entire directory structure:

```python
else:
    symlink_or_copy(self.original_model_path, dest, self._symlink_ok)
```

## Adapting Your 70B Checkpoint

If your manually saved 70B checkpoint has a different structure than expected, you have two options:

1. **Adapt to V2 format**: Create an `is_v2` marker file in your checkpoint directory and ensure your model files are organized into the expected subdirectorie
   s (whatever is listed in `checkpoint_subdirs` for your application).

2. **Use legacy format**: Ensure all required files are in the root of your checkpoint directory if you want to use the legacy approach.

If you need to know exactly what subdirectories are expected for your specific implementation, you would need to check what values are passed for `checkpoint_s
ubdirs` when creating the `DefinedLocalModel` instance in your specific application.
````

````
# Dromeus Model Directory Structures

Based on the code, I can see that Dromeus supports two different model directory structures in GCS:

## 1. V2 Model Structure

This is detected by checking for the existence of an `is_v2` file in the root of the model directory:

```python
is_v2 = gcsfile.exists(gcsfile.join(self.original_model_path, 'is_v2'))
```

For V2 models, Dromeus only downloads specific subdirectories from the checkpoint as specified in `checkpoint_subdirs`. This means:

- The model directory should have an `is_v2` marker file
- Only specific subdirectories (defined in `checkpoint_subdirs`) are downloaded
- Each subdirectory is downloaded to the same local directory

## 2. Legacy (V1) Model Structure

If the `is_v2` file is not found, Dromeus treats it as a legacy model and downloads the entire directory structure:

```python
else:
    symlink_or_copy(self.original_model_path, dest, self._symlink_ok)
```

## Adapting Your 70B Checkpoint

If your manually saved 70B checkpoint has a different structure than expected, you have two options:

1. **Adapt to V2 format**: Create an `is_v2` marker file in your checkpoint directory and ensure your model files are organized into the expected subdirectorie
s (whatever is listed in `checkpoint_subdirs` for your application).

2. **Use legacy format**: Ensure all required files are in the root of your checkpoint directory if you want to use the legacy approach.

If you need to know exactly what subdirectories are expected for your specific implementation, you would need to check what values are passed for `checkpoint_s
ubdirs` when creating the `DefinedLocalModel` instance in your specific application.
````

````
Based on the code context, Dromeus can handle various GCS (Google Cloud Storage) directory structures when specified with the `--model` flag. There are a few patterns evident in the codebase:

1. **Standard Checkpoints**: The primary pattern is a direct GCS path to a model checkpoint, like:
   ```
   gs://mathesis-training-persistent/Meta-Llama-3.3-70B-Instruct/
   ```

   This is shown in the `MODEL_CONFIGS` dictionary with entries like `llama3_70b` and others.

2. **Fine-tuned Checkpoints with Epoch/Step Information**: For fine-tuned models (like those from online RL), the path typically includes epoch and step information:
   ```
   gs://mathesis-training-persistent/cm-llama8b-best-onlinerl/04-07-2025/epoch000-step08049/
   ```

3. **V2 Checkpoint Format**: There appears to be a "v2" format detection mechanism. In the `DefinedLocalModel._download` method, it checks if a file called `is_v2` exists in the specified GCS path to determine if it's a v2 format checkpoint.

For your specific case where you manually saved a 70B checkpoint from the online RL trainer, you should be able to point Dromeus at the directory containing your checkpoint files. The key differences between the online RL checkpoint structure and standard checkpoint structure might be:

1. The presence of additional metadata files
2. Different naming conventions for weight files
3. Possibly different subdirectory organization

However, as long as the necessary model files are in the specified directory or its subdirectories, Dromeus should be able to load them. The `_download` method in `DefinedLocalModel` handles downloading from appropriate subdirectories when needed.

If you're having specific issues, you might want to:
1. Check if your checkpoint directory contains an `is_v2` file
2. Ensure the checkpoint files follow one of the expected patterns
3. Try specifying a more specific subdirectory that directly contains the model weights

Based on the `_lepton_command` function, it appears that Dromeus expects a straightforward path to the model, which it passes directly to its launcher.
````

## Question

if I run olympus/grob/launchers/manager.py -- cleanup, will it touch the stuff in the checkpoints in the lepton storage?

## Answers

### Incorrect

(Doesn't say what it does by default)

```
Based on the code provided, when you run `olympus/grob/launchers/manager.py --cleanup`, whether it will delete checkpoints in Lepton storage depends on the spe
cific arguments passed to the script.

Looking at the `do_cleanup` function, there is a parameter `delete_lepton_checkpoints` which controls whether checkpoints are deleted. When this parameter is s
et to `True`, the function calls `cleanup_lib.cleanup_checkpoints` to delete the checkpoint directories specified in the launch configuration.

From the test code (`test_cleanup_checkpoints`), I can see that the `cleanup_checkpoints` function will delete directories that begin with `lepton://`, which a
re Lepton storage paths.

In the `test_cleanup_realigns_first` test, we can see a call to `do_cleanup` with `delete_lepton_checkpoints=False`, which would preserve the checkpoints.

So to answer your question directly:
- If you run `manager.py --cleanup` without any additional flags that would set `delete_lepton_checkpoints=True`, the checkpoints in Lepton storage should be p
reserved
- However, if you run it with flags that set `delete_lepton_checkpoints=True`, then yes, it will delete checkpoints in Lepton storage

Without seeing the command-line argument parsing logic for the script, I cannot definitively say what the default behavior is, but based on the test case where
 `delete_lepton_checkpoints=False`, it's likely that you need to explicitly request checkpoint deletion.
```

```
Based on the code you provided, running `olympus/grob/launchers/manager.py --cleanup` will only delete checkpoints in the lepton storage if the `delete_lepton_
checkpoints` flag is enabled.

Looking at the `do_cleanup` function, it has a parameter `delete_lepton_checkpoints: bool` which controls whether checkpoints should be deleted. When this para
meter is `True`, the function calls `cleanup_lib.cleanup_checkpoints(lepton_service, launch_config.checkpoint_directories)` which would delete the checkpoints
stored in the locations specified in `launch_config.checkpoint_directories`.

From the launch code, we can see that `checkpoint_directories` includes three paths:
1. `'lepton_nfs'`: A local path in the GCS mirror mount directory
2. `'lepton_remote'`: A path in the Lepton storage system
3. `'gcs'`: A Google Cloud Storage path

So if you run the script with the `--cleanup` flag and the `delete_lepton_checkpoints` option is enabled, it will indeed delete checkpoints in the lepton stora
ge. However, if the `delete_lepton_checkpoints` option is not enabled, the checkpoints will be preserved.

Without seeing the argument parsing code that handles the `--cleanup` flag, I can't determine the default value for `delete_lepton_checkpoints`, but it appears
 to be a separate option that you would need to explicitly enable.
```

### Correct

````
Based on the code you provided, if you run `olympus/grob/launchers/manager.py --cleanup`, it will by default delete the checkpoints stored in lepton storage.

Looking at the `cleanup()` function, it has a parameter `delete_lepton_checkpoints` which defaults to `True`. This parameter controls whether checkpoints in Lepton storage are deleted during cleanup:

```python
async def cleanup(
  launch_name: str,
  delete_environments: bool = True,
  stop_lepton: bool = True,
  delete_lepton_checkpoints: bool = True,  # This parameter defaults to True
  mark_finished: bool = True,
  grob_config_file: str = config_lib.DEFAULT_PATH,
):
```

When you run the script with `--cleanup`, it will call this function with the default value of `delete_lepton_checkpoints=True`, meaning it will delete the checkpoints stored in Lepton.

If you want to keep the checkpoints in Lepton storage when running cleanup, you would need to specifically pass a flag to set `delete_lepton_checkpoints=False`. The exact flag syntax isn't shown in the provided code, but it would be something like `--no-delete-lepton-checkpoints` or similar, depending on how the argument parser is configured.
````

# Question

Do we know the underlying cause for sequences that don’t have a sequence file? Is this just something that happens when the original data-generation jobs time out?

## Answers

### Correct

```
Based on the code, the underlying cause for sequences that don't have a sequence file appears to be multi-faceted rather than limited to job timeouts. Here are
 the key insights:

1. **Explicit Error Handling**: The `SequenceFileExistsFilter` class is specifically designed to filter out sequences without sequence files. It catches severa
l types of errors:
   - `common.SequenceFileNotFound`: The primary error indicating a missing sequence file
   - `google.api_core.exceptions.GoogleAPIError`: API-related errors when trying to access files
   - `google.auth.exceptions.GoogleAuthError`: Authentication errors when accessing storage

2. **Storage and Database Separation**: The system appears to use a dual-storage approach:
   - Database records for sequence metadata
   - External file storage (likely GCS based on imports) for the actual sequence content

3. **Potential Causes**:
   - **Write Failures**: The code shows that sequences are created in a two-step process - first metadata in the database, then the sequence file. If the secon
d step fails, you'd have a database record but no file.
   - **GCS Issues**: Several error handlers suggest GCS access problems could be responsible
   - **TTL Expiration**: There's code related to TTL (time-to-live) for sequence files, suggesting some files may expire intentionally (`ttl='short', 'medium',
 'long'` options)
   - **Manual Deletion**: Evidence of testing functions that specifically unlink sequence files: `os.unlink(os.path.join(gcs_tmpdir, f'my/test/collection/{id}.
sequence'))`

4. **Filter Implementation**: The system is designed to gracefully handle these missing files by filtering them out rather than failing, suggesting this is a k
nown and expected condition.

5. **Testing for This Case**: There's a test (`test_online_bon_dataset_filtering`) that explicitly tests what happens when a sequence file is missing, indicati
ng this is a known operational pattern.

Rather than just timeouts, the evidence suggests multiple failure modes (authentication errors, API errors, TTL expiration, incomplete writes) can cause the si
tuation where a sequence exists in the database but its corresponding file is missing.
```

### Incorrect

```
Based on the code provided, I can identify potential causes for sequences that don't have corresponding sequence files:

1. **Intentional Deletion**: In `test_missing_sequence`, there's an explicit test case where a sequence file is deliberately removed using `os.unlink(out)`, de
monstrating that the system should handle missing sequence files gracefully. This suggests that files can be intentionally deleted after creation.

2. **Failed Write Operations**: The sequence data has a two-part storage mechanism:
   - Database records in the `sequences` table
   - Corresponding files in Google Cloud Storage

   If the sequence metadata is successfully written to the database but the file creation fails or is interrupted, you'd have a database entry without a corres
ponding file.

3. **Timeout Issues**: While not explicitly mentioned in the code, your speculation about timeout issues in data-generation jobs is plausible. The code shows t
hat sequence writing is part of a multi-step process, and if a job times out after database insertion but before file completion, it would result in this state
.

4. **Error Handling**: The implementation of `SequenceFileExistsFilter` class specifically filters out sequences without corresponding files, indicating this i
s an expected condition that needs handling in the system.

5. **Code Design**: The system appears designed to handle this scenario, as evidenced by the `common.SequenceFileNotFound` exception that's raised when attempt
ing to access a sequence without a file.

The code includes explicit filtering logic (`SequenceFileExistsFilter`) to check for file existence and filter out sequences without files, suggesting this is
a known occurrence that the system is designed to handle gracefully rather than prevent entirely.

Based on the implementation details, I would conclude that missing sequence files are a recognized condition in this system that can arise from various operati
onal scenarios, including but not limited to job timeouts, as you suggested.
```

```
Based on the code provided, I can determine that sequences without corresponding sequence files can occur for several reasons, not just job timeouts:

1. **Explicit Deletion**: The code in `test_missing_sequence` shows that sequence files can be explicitly deleted while leaving the database entry intact. This is done with `os.unlink(out)`.

2. **Error Handling Pattern**: The code demonstrates a common pattern where sequence file absence is expected to raise `common.SequenceFileNotFound` exceptions, which clients are expected to handle. This suggests it's a recognized potential state of the system.

3. **Filtering Mechanism**: The `SequenceFileExistsFilter` class is specifically designed to filter out sequences that don't have associated sequence files, indicating this is a common enough occurrence to need systematic handling.

4. **Testing for Missing Files**: The `test_online_bon_dataset_filtering` test explicitly creates a sequence, deletes its file, and ensures it's properly filtered out, showing this is expected behavior.

5. **Two-Part Storage System**: The architecture involves:
   - Database entries in PostgreSQL that store metadata about sequences
   - Actual sequence data files stored in GCS (Google Cloud Storage)

This separation means the two systems can become out of sync if:
- A job creates a database entry but fails before writing the file
- A file is deleted without updating the database
- GCS storage operations fail after database records are created

While job timeouts could certainly be one cause, the code suggests this is a recognized aspect of the system's architecture that's explicitly handled rather than just an error condition from timeouts.
```
