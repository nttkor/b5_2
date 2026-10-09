"""Entry point: python main.py

Mini Git CLI 메인 엔트리 포인트.
대화형 REPL 루프(mini-git> 프롬프트)를 시작합니다.
"""

from __future__ import annotations

import sys
from pathlib import Path

# 루트 디렉터리 경로 등록 및 mini_git 패키지 별칭 매핑 (호환성 보장)
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import src as mini_git  # noqa: E402
sys.modules["mini_git"] = mini_git

from src.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
