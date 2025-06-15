import os

def test_requirements_file_does_not_contain_tree_sitter_languages():
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    assert 'tree-sitter-languages' not in requirements, \
        "'tree-sitter-languages' should not be in requirements.txt"