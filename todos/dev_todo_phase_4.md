# Phase 4 Implementation Plan: Integrate and Finalize Portable Tool

This plan will clean the repository of old state files and update all agent rules to use the new, portable `vdb-tool` commands.

## Task 1: Clean Up Contaminated State Files
- [x] **LLM Prompt:** "Delete the `FIX_PLAN.md` file from the root directory. It is a leftover artifact from a previous run and is confusing the current state."
- **Verification:** Run `test ! -f FIX_PLAN.md && echo "OK"`

## Task 2: Update Architect's Rules to Use New Tool
- **LLM Prompt:** "In the file `.roo/rules-architect-senior/rules.md`, find the 'Semantic Discovery' step. Replace the command `python vector_tool.py query "Your natural language question about the code"` with the new command `vdb-tool query "Your natural language question about the code"`."
- **Verification:** Run `grep "vdb-tool query" .roo/rules-architect-senior/rules.md && echo "OK"`

## Task 3: Update Vector Updater's Rules to Use New Tool
- **LLM Prompt:** "In `.roo/custom_modes.yaml`, find the `vector-updater` custom mode. In its `roleDefinition`, replace the command `python vector_tool.py update [file_path]` with `vdb-tool update [file_path]`."
- **Verification:** Run `grep "vdb-tool update" .roo/custom_modes.yaml && echo "OK"`

## Task 4: Implement Orchestration for Memory Synchronization
- **LLM Prompt:** "Modify the Developer and Orchestrator rules to enable memory synchronization. First, in `.roo/rules-developer/rules.md`, under the 'Handle Plan Success' section, add a step to create a signal file listing modified files. Second, in `.roo/rules-orchestrator-senior/rules.md`, add a new high-priority rule to consume this signal and trigger the `vector-updater`."
- **Sub-Task 4.1: Update Developer Rules**
  - **LLM Prompt:** "In `.roo/rules-developer/rules.md` under section `3. Handle Plan Success`, add the following action before the handoff: 'Before handing off, create a file named `MODIFIED_FILES.txt` containing a list of all unique file paths that were changed during the execution of this plan.'"
  - **Verification:** Run `grep "MODIFIED_FILES.txt" .roo/rules-developer/rules.md && echo "OK"`
- **Sub-Task 4.2: Update Orchestrator Rules**
  - **LLM Prompt:** "In `.roo/rules-orchestrator-senior/rules.md`, add a new rule at priority #4 (shifting the existing #4 and subsequent rules down). This new rule must check for `MODIFIED_FILES.txt`, switch to `vector-updater` mode with the file's contents, and then delete the file."
  - **Verification:** Run `grep "MODIFIED_FILES.txt" .roo/rules-orchestrator-senior/rules.md && echo "OK"`

## Task 5: Mark Project as Complete
- **LLM Prompt:** "All planned work is now complete. The tool is portable and fully integrated. Create the final signal file `DEVELOPMENT_COMPLETE.md` to signify the end of the project."
- **Verification:** Run `test -f DEVELOPMENT_COMPLETE.md && echo "OK"`