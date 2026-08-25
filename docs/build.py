#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent

# 生成脚本会输出中文，强制用 UTF-8 交换数据，避免受系统区域编码影响。
env = os.environ | {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

for script in sorted((here / "scripts").glob("*.py")):
    print(f"Generating output for {script.name}...")
    out = subprocess.check_output(
        [sys.executable, script.absolute()],
        cwd=here,
        text=True,
        encoding="utf8",
        env=env,
    )
    if out:
        (here / "src" / "generated" / f"{script.stem}.html").write_text(
            out, encoding="utf8"
        )

if (here / "public").exists():
    shutil.rmtree(here / "public")
subprocess.run(["hugo"], cwd=here / "src", check=True)
