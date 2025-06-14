# Phase 5 Implementation Plan: System Correction and Finalization

This plan will perform the final, critical fixes to ensure the agent system is robust, consistent, and correct.

## Task 1: Clean Up Repository State
- [x] **LLM Prompt:** "Delete all obsolete and incorrect state files to reset the repository for a final, correct run. Delete the following files: `PROJECT_VERIFIED_AND_COMPLETE.md`, `MODIFIED_FILES.txt`, `todos/dev_todo_phase_1.md`, and `todos/dev_todo_phase_2.md`."
- **Verification:**
  - Run `test ! -f PROJECT_VERIFIED_AND_COMPLETE.md && echo "OK"`
  - Run `test ! -f MODIFIED_FILES.txt && echo "OK"`
  - Run `test ! -f todos/dev_todo_phase_1.md && echo "OK"`
  - Run `test ! -f todos/dev_todo_phase_2.md && echo "OK"`

## Task 2: Correct Orchestrator Priority Logic
- [x] **LLM Prompt:** "Modify `.roo/rules-orchestrator-senior/rules.md`. The rule for `MODIFIED_FILES.txt` must have a higher priority than the rule for `DEVELOPMENT_COMPLETE.md`. Re-order the decision tree so that the `MODIFIED_FILES.txt` check happens *before* the `DEVELOPMENT_COMPLETE.md` check."
- **Verification:** Open `.roo/rules-orchestrator-senior/rules.md` and confirm that the `MODIFIED_FILES.txt` condition is evaluated before the `DEVELOPMENT_COMPLETE.md` condition.

## Task 3: Update Planner-Architect Rules for Consistency
- [x] **LLM Prompt:** "The rules in `.roo/rules-planner-architect/rules.md` are outdated. Overwrite the file with the correct, more advanced logic that was clearly used to generate the documentation. This logic includes manifest creation and self-verification."
- **Verification:** Run `grep "Blueprint Self-Verification" .roo/rules-planner-architect/rules.md && echo "OK"`

## Task 4: Delete Obsolete Planner-Orchestrator
- [x] **LLM Prompt:** "The `planner-orchestrator` role is now fully superseded by the more robust `orchestrator-senior` and the new `planner-architect` workflow. Delete the file `.roo/rules-planner-orchestrator/rules.md` to remove the obsolete agent."
- **Verification:** Run `test ! -f .roo/rules-planner-orchestrator/rules.md && echo "OK"`

## Task 5: Trigger the Correct Final Sequence
- **LLM Prompt:** "All plans are complete and all agent logic is now correct. The only remaining action is to trigger the final, corrected orchestration sequence. Create an empty file named `DEVELOPMENT_COMPLETE.md`."
- **Verification:** Run `test -f DEVELOPMENT_COMPLETE.md && echo "OK"`