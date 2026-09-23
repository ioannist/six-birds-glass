import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow


def test_build_gt2_kovacs_loop_artifact_refuses_uncertified_real_loop(tmp_path: Path) -> None:
    output_path = tmp_path / "kovacs_loop.json"
    main = load_main()

    with pytest.raises(RuntimeError, match="finite loop-action closure"):
        main(output_path=output_path)

    assert not output_path.exists()


def load_main():
    script_path = Path(__file__).resolve().parents[1] / "experiments" / "build_gt2_kovacs_loop.py"
    spec = importlib.util.spec_from_file_location("build_gt2_kovacs_loop", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main
