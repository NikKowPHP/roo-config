### **Step 2: Configure VS Code (Critical for Roo Extension)**

After the script completes, you must tell VS Code to use the new virtual environment. This ensures the Roo extension runs with the correct tools.

*   In VS Code, open the **Command Palette** (`Ctrl+Shift+P` on Windows/Linux, `Cmd+Shift+P` on macOS).
*   Type and select **`Python: Select Interpreter`**.
*   A list of Python interpreters will appear. Choose the one that includes **`./.venv/bin/python`** in its path. It will often be marked as "Recommended".

![VSCode Select Interpreter](https://code.visualstudio.com/assets/docs/python/environments/interpreter-selection.png)

### **Step 3: Link Agent Rules to Roo**

Make the custom agent definitions in the `.roo/` directory available to the Roo extension.

```bash
# This only needs to be run once, or when agent definitions change.
./copy_script.sh
```

**That's it!** You are now ready to use the Roo VS Code extension to run the AI agents. The AI's memory is already running and has been pre-loaded with the entire codebase.

---

## 📖 How to Use the Factory

The system is controlled by giving it a task and then kicking off the `orchestrator` agent. The Orchestrator analyzes the project state and delegates work to the correct specialist agent.

**Your only action to start or resume work is always to run the `orchestrator` agent from the Roo VS Code extension UI.**

### Scenario 1: Adding a New Feature

Create a new "Work Item" ticket in the `work_items/` directory (create the directory if it doesn't exist).

**Example `work_items/item-002-add-pdf-export.md`:**
```markdown
---
status: "open"
priority: "high"
---

# Feature Request: Export blog post to PDF

## Description
In addition to HTML, users should be able to export the final blog post as a PDF file.

## Acceptance Criteria
- A new command-line flag, `--pdf <output_path>`, should be added.
- When this flag is used, the tool should convert the markdown to HTML internally, and then render that HTML into a PDF file at the specified output path.
```

**How the AI Factory Responds:**
Run the `orchestrator` agent. It will detect the new open ticket and activate the **Architect**. The Architect will use `cct query` to understand the existing code and create a specific plan (`dev_todo_item-002.md`) to implement the feature. The standard TDD cycle will then execute this plan.

### Scenario 2: Fixing a Bug

Create a "Bug Report" ticket in the `work_items/` directory.

**Example `work_items/bug-003-image-links-broken.md`:**
```markdown
---
status: "open"
priority: "critical"
---

# Bug Report: Image links are broken in HTML output

## Steps to Reproduce
1. Create a markdown file with an image link: `![An image](https://example.com/image.png)`
2. Run the tool to convert it to HTML.
3. Open the HTML file in a browser.

## Observed Behavior
The `<img>` tag in the HTML is malformed.

## Expected Behavior
The generated HTML should contain a valid image tag: `<img src="https://example.com/image.png" alt="An image">`.
```
**How the AI Factory Responds:**
The flow is identical to adding a feature. The Orchestrator assigns the bug report to the Architect for planning, and the Developer's TDD approach is perfect for bug fixing: it will first write a new test that *fails* because of the bug, and then write the code to make that test pass.

---

## 🧹 Tearing Down the Environment

When you are finished, you can run the cleanup script to stop the Docker containers, remove the database volume, and delete the local Python environment.

```bash
./delete_environment.sh
```