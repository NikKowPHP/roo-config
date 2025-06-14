# Vector Database Agent Tool

This tool provides a portable command-line interface for AI agents to index and query any codebase.

## Installation

From the root of this tool's directory, run the following command once to make the tools available in your environment:

`pip install .`

## Usage in another Project

1.  **Configure:** In the root of the target project you want to index, create a `vdb-config.ini` file. This is crucial for giving each project a unique database collection.

    ```ini
    [main]
    collection_name = my-project-name-v1

    [scanning]
    file_extensions = .py,.js,.md
    ignore_list = .git,.venv,node_modules
    ```

2.  **Index:** Run the indexer from the root of the target project.
    
    `vdb-index`

3.  **Query & Update:** Use the tool to interact with the project's memory.

    `vdb-tool query "your natural language query"`
    `vdb-tool update path/to/modified/file.py`