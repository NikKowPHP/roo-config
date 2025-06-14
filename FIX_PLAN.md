# Fix Plan: Enable Vector Updater Mode

## Diagnosis
The Orchestrator AI is unable to switch to the `vector-updater` mode, even though it is defined in `custom_modes.yaml`. The previous fix failed because the virtual environment was not activated when running the `src/vdb/tool.py` script.

## Task 1: Modify copy_script.sh to activate virtual environment [x]
- **LLM Prompt:** "Modify the `copy_script.sh` script to activate the virtual environment before copying the `custom_modes.yaml` file. The script should now contain `#!/bin/bash\n\nsource venv/bin/activate && cp .roo/custom_modes.yaml ~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.yaml`"
- **Verification:** Read the contents of `copy_script.sh` and confirm that it contains the correct activation command.

## Task 2: Make src/vdb/tool.py executable
- **LLM Prompt:** "Make the `src/vdb/tool.py` script executable using the command `chmod +x src/vdb/tool.py`"
- **Verification:** Check the output of the command to confirm it executed successfully.

## Task 3: Reload Custom Modes Configuration
- **LLM Prompt:** "Execute the `copy_script.sh` script to reload the custom modes configuration."
- **Verification:** Check the output of the script to confirm it executed successfully.

## Task 4: Attempt Mode Switch Again
- **LLM Prompt:** "Switch to `vector-updater` mode with the contents of `MODIFIED_FILES.txt` as the reason."
- **Verification:** Confirm that the mode switch is successful.

## Task 5: Update Vector Database
- **LLM Prompt:** "Run the `src/vdb/tool.py update todos/dev_todo_phase_5.md` script using the command `venv/bin/python src/vdb/tool.py update todos/dev_todo_phase_5.md`"
- **Verification:** Check the output of the script to confirm it executed successfully.

## Task 6: Clean up and reset for autonomous handoff
- **LLM Prompt:** "Delete the file `NEEDS_ARCHITECTURAL_REVIEW.md` from the root directory."
- **Verification:** The file `NEEDS_ARCHITECTURAL_REVIEW.md` no longer exists.