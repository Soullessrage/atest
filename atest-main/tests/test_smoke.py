from pathlib import Path


def test_app_entrypoint_exists():
    assert Path("app/ui/main.py").exists()
