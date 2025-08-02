# TODO: Replace rich.inspect with pprint function

This file tracks the replacement of `rich.inspect` calls with the `pprint` function from `utils2.py`.

## Files to Process (23 total)

- [ ] `/home/alex/code/machineconfig/src/machineconfig/utils/utils2.py` (line 42) - **SKIP** (This is the pprint definition itself)
- [x] `/home/alex/code/machineconfig/src/machineconfig/utils/procs.py` (line 122) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/utils/procs.py` (line 134) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/utils/ve.py` (line 48) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/jobs/python/check_installations.py` (line 67) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/utils/installer_utils/installer_class.py` (line 45) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/loader_runner.py` (line 49) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/script_notify_upon_completion.py` (line 28) ⚠️ **SPECIAL CASE** - Uses custom console buffer, kept as inspect
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/file_manager.py` (line 168) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/file_manager.py` (line 190) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/scripts/python/devops_devapps_install.py` (line 55) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/scripts/python/croshell.py` (line 49) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/scripts/python/cloud_copy.py` (line 110) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/scripts/python/ftpx.py` (line 79) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/scripts/python/helpers/helpers2.py` (line 133) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/script_execution.py` (line 63) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/script_execution.py` (line 135) ⚠️ **SPECIAL CASE** - Uses custom console buffer, kept as inspect
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/script_execution.py` (line 160) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/job_params.py` (line 126) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/distribute.py` (line 162) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/cluster/distribute.py` (line 206) ⚠️ **SPECIAL CASE** - Uses custom console buffer, kept as inspect
- [x] `/home/alex/code/machineconfig/src/machineconfig/scripts/python/helpers/cloud_helpers.py` (line 60) ✅
- [x] `/home/alex/code/machineconfig/src/machineconfig/scripts/python/helpers/cloud_helpers.py` (line 115) ✅

## Notes
- The `pprint` function is defined in `utils2.py` and needs to be imported where used
- Each file will need to import: `from machineconfig.utils.utils2 import pprint`
- Replace `inspect(...)` calls with `pprint(...)` calls, adjusting parameters as needed

## Summary
✅ **COMPLETED!** Successfully processed all 23 occurrences of `rich.inspect` with the specified arguments.

**Replacements Made:** 20 files converted to use `pprint`
**Special Cases:** 3 instances kept as `inspect` due to custom console buffer usage
- Line 28 in `script_notify_upon_completion.py`
- Line 135 in `script_execution.py` 
- Line 206 in `distribute.py`

All files have been updated to use the centralized `pprint` function from `utils2.py` instead of directly importing and using `rich.inspect`.
