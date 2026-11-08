"""Filter the datasets of the DB with the steps of one config.

Usage: python3 local/dataset_filtering/run.py config/multidataset_ser_01.yaml
Outputs go to output/<config name>/.
"""
import sys
from pathlib import Path

import yaml

from src.filter_pipeline import FilterPipeline

HERE = Path(__file__).resolve().parent


def main(config_path):
    config_path = Path(config_path)
    if not config_path.exists():
        config_path = HERE / config_path
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    FilterPipeline(config, db_root=HERE.parent.parent, output_dir=HERE / "output" / config_path.stem).run()
    print(f"Written to {HERE / 'output' / config_path.stem}")


if __name__ == "__main__":
    main(sys.argv[1])
