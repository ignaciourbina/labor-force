import json
from pathlib import Path

def test_unique_labels_match_codes():
    data = json.loads(Path('API_database_laborforce/data_occup_foreign_extended.json').read_text())
    codes = {row['soc'] for row in data}
    labels = {row['occ_label'] for row in data}
    assert len(codes) == len(labels)
