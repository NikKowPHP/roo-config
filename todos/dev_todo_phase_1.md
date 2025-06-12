# Phase 1 Implementation Plan: Vector Database System

## Task 1: Create requirements.txt
- [x] **LLM Prompt:** "Create requirements.txt with Qdrant and sentence-transformers dependencies"
- **Verification:** File exists with correct content:
  ```text
  qdrant-client
  sentence-transformers
  tree-sitter
  tree-sitter-languages
  ```

## Task 2: Implement indexer.py
- [ ] **LLM Prompt:** "Create indexer.py with codebase scanning and Qdrant upload functionality"
- **Verification:** File exists and can be run with `python indexer.py`
- **Code Requirements:** Must include:
  - Qdrant client configuration
  - File walking with ignore patterns
  - Code chunking logic
  - Vector upsert to Qdrant

## Task 3: Create vector_tool.py
- [ ] **LLM Prompt:** "Implement vector_tool.py with update and query commands"
- **Verification:** Supports both `update` and `query` subcommands
- **Code Requirements:** Must include:
  - File update functionality that replaces old vectors
  - Natural language query interface
  - JSON output format for queries

## Task 4: Update Mode Rules
- [ ] **LLM Prompt:** "Add vector query instructions to architect-senior rules"
- **Verification:** architect-senior rules include vector query step

## Task 5: Add Vector-Updater Mode
- [ ] **LLM Prompt:** "Add vector-updater mode to custom_modes.yaml"
- **Verification:** New mode exists with correct workflow