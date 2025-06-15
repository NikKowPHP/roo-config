import importlib

def test_packages_installed():
    required_packages = [
        'qdrant_client',
        'sentence_transformers',
        'tree_sitter'
    ]
    
    missing = []
    for pkg in required_packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    
    assert not missing, f"Missing required packages: {', '.join(missing)}"