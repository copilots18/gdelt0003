import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_discover_mode_is_safe_without_authorization():
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / 'create_short.py'), '--data', str(ROOT / 'data' / 'highlights.json'), '--count', '3'],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload['status'] == 'discover'
    assert payload['authorized'] is False
    assert payload['batch_count'] == 3


def test_authorized_mode_allows_creation():
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / 'create_short.py'), '--data', str(ROOT / 'data' / 'highlights.json'), '--count', '3', '--authorize'],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload['status'] == 'create'
    assert payload['authorized'] is True
    assert len(payload['batch']) >= 1
