#!/usr/bin/env python3
"""Antigravity CLI (agy) 실시간 사고(Thinking) 및 행동(Actions) 라이브 모니터링 툴.

백그라운드 또는 다른 터미널에서 실행 중인 agy 세션의 트랜스크립트 로그를 실시간 추적하여,
에이전트의 내부 추론(Thinking / CoT), 도구 호출(Tool Calls), 사용자 입력, 최종 응답을
ANSI 컬러와 함께 스트리밍 출력합니다.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
from pathlib import Path

# ANSI 컬러 코드
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RED = "\033[31m"
BG_BLUE = "\033[44m"
BG_YELLOW = "\033[43m"
BG_CYAN = "\033[46m"


def get_default_brain_dir() -> Path:
    """agy 기본 브레인 저장소 디렉터리 경로를 반환합니다.

    Returns:
        Path: brain 디렉터리 경로 (~/.gemini/antigravity-cli/brain)
    """
    home = Path.home()
    return home / ".gemini" / "antigravity-cli" / "brain"


def find_latest_session(brain_dir: Path, exclude_id: str = None) -> tuple[str, Path] | None:
    """가장 최근에 수정된 agy 세션 디렉터리와 트랜스크립트 파일 경로를 탐색합니다.

    Args:
        brain_dir (Path): brain 상위 디렉터리
        exclude_id (str, optional): 제외할 세션 ID (현재 세션 제외용)

    Returns:
        tuple[str, Path] | None: (세션 ID, transcript.jsonl 경로) 또는 None
    """
    if not brain_dir.exists():
        return None

    # 디렉터리별 수정 시각 기준 정렬
    candidates = []
    for item in brain_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            if exclude_id and item.name == exclude_id:
                continue
            transcript = item / ".system_generated" / "logs" / "transcript.jsonl"
            if transcript.exists():
                candidates.append((transcript.stat().st_mtime, item.name, transcript))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    latest_time, session_id, transcript_path = candidates[0]
    return session_id, transcript_path


def format_step(step_data: dict, show_thinking: bool = True) -> str:
    """트랜스크립트 한 스텝 데이터를 가독성 높은 컬러 텍스트로 포맷팅합니다.

    Args:
        step_data (dict): JSON 한 줄 파싱 딕셔너리
        show_thinking (bool): Thinking 출력 여부

    Returns:
        str: 포맷팅된 문자열 (내용이 없으면 빈 문자열)
    """
    step_idx = step_data.get("step_index", "?")
    step_type = step_data.get("type", "UNKNOWN")
    lines = []

    # 1. 사용자 입력
    if step_type == "USER_INPUT":
        content = step_data.get("content", "").strip()
        # <USER_REQUEST> 태그 추출 또는 원본 출력
        match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, re.DOTALL)
        clean_content = match.group(1).strip() if match else content
        lines.append(f"\n{BOLD}{GREEN}📥 [STEP {step_idx} | USER INPUT]{RESET}")
        lines.append(f"{GREEN}{clean_content}{RESET}\n")
        return "\n".join(lines)

    # 2. 에이전트 사고(Thinking / Chain-of-Thought)
    thinking = step_data.get("thinking")
    if thinking and show_thinking:
        lines.append(f"\n{BOLD}{CYAN}🧠 [STEP {step_idx} | THINKING (내부 사고/계획)]{RESET}")
        # 줄바꿈 들여쓰기 처리
        for line in thinking.strip().splitlines():
            lines.append(f"{CYAN}  │ {line}{RESET}")
        lines.append(f"{CYAN}  └───{RESET}")

    # 3. 도구 호출(Tool Calls)
    tool_calls = step_data.get("tool_calls", [])
    if tool_calls:
        for idx, tc in enumerate(tool_calls, 1):
            tool_name = tc.get("name", "tool")
            args = tc.get("args", {})
            summary = args.get("toolSummary", "")
            action = args.get("toolAction", "")
            target = (
                args.get("CommandLine")
                or args.get("TargetFile")
                or args.get("AbsolutePath")
                or args.get("Url")
                or args.get("query")
                or ""
            )

            lines.append(f"{BOLD}{YELLOW}🛠️  [STEP {step_idx} | ACTION {idx}] {tool_name}{RESET}")
            if summary or action:
                lines.append(f"{YELLOW}   Summary: {summary} ({action}){RESET}")
            if target:
                lines.append(f"{YELLOW}   Target : {BOLD}{target}{RESET}")

    # 4. 모델 텍스트 응답(Content)
    content = step_data.get("content")
    if content and step_type == "PLANNER_RESPONSE" and not tool_calls:
        lines.append(f"\n{BOLD}{MAGENTA}💬 [STEP {step_idx} | ASSISTANT RESPONSE]{RESET}")
        lines.append(f"{MAGENTA}{content.strip()}{RESET}\n")

    return "\n".join(lines) if lines else ""


def stream_transcript(transcript_path: Path, session_id: str, history_lines: int = 5):
    """지정된 transcript.jsonl 파일을 tail -f 방식으로 실시간 스트리밍합니다.

    Args:
        transcript_path (Path): transcript.jsonl 경로
        session_id (str): 세션 ID
        history_lines (int): 초기에 출력할 과거 스텝 수
    """
    print(f"{BOLD}{GREEN}==================================================================={RESET}")
    print(f"{BOLD}📡 agy 실시간 사고 & 행동 모니터링 시작 (Live Stream){RESET}")
    print(f"📌 세션 ID : {BOLD}{session_id}{RESET}")
    print(f"📂 로그 경로: {transcript_path}")
    print(f"🛑 종료 방법: Ctrl+C")
    print(f"{BOLD}{GREEN}==================================================================={RESET}\n")

    if not transcript_path.exists():
        print(f"{RED}로그 파일이 존재하지 않습니다: {transcript_path}{RESET}")
        return

    # 초기 기록 읽기
    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        existing_lines = f.readlines()

    # 과거 history_lines개 스텝 출력
    if existing_lines:
        start_idx = max(0, len(existing_lines) - history_lines)
        for line in existing_lines[start_idx:]:
            try:
                data = json.loads(line)
                out = format_step(data)
                if out:
                    print(out)
            except json.JSONDecodeError:
                pass

    print(f"\n{DIM}--- [현재 시점부터 실시간 스트리밍 대기 중...] ---{RESET}\n")

    # tail -f 루프
    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                try:
                    data = json.loads(line)
                    out = format_step(data)
                    if out:
                        print(out)
                        sys.stdout.flush()
                except json.JSONDecodeError:
                    pass
            else:
                time.sleep(0.3)


def main():
    """CLI 진입점 함수."""
    parser = argparse.ArgumentParser(
        description="Antigravity CLI (agy) 실시간 사고 및 행동(Thinking/Tool) 라이브 모니터"
    )
    parser.add_argument(
        "--session",
        type=str,
        default=None,
        help="모니터링할 특정 agy 세션 ID (기본값: 가장 최근 수정된 세션 자동 감지)",
    )
    parser.add_argument(
        "--history",
        type=int,
        default=5,
        help="초기 시작 시 출력할 이전 스텝 수 (기본값: 5)",
    )
    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="사고(Thinking) 필터링하고 도구 호출 및 답변만 표시",
    )

    args = parser.parse_args()
    brain_dir = get_default_brain_dir()

    if args.session:
        session_id = args.session
        transcript_path = brain_dir / session_id / ".system_generated" / "logs" / "transcript.jsonl"
    else:
        # 현재 실행 중인 자기 자신 세션(bf07f24c...)을 제외하고 가장 최근 세션 탐색
        current_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "bf07f24c-aa8d-4e68-9087-fab2a03c2dcd")
        found = find_latest_session(brain_dir, exclude_id=current_id)
        if not found:
            # 제외 없이 최신 검색
            found = find_latest_session(brain_dir)
        if not found:
            print(f"{RED}감지된 agy 세션이 없습니다.{RESET}")
            sys.exit(1)
        session_id, transcript_path = found

    try:
        stream_transcript(transcript_path, session_id, history_lines=args.history)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}모니터링을 종료합니다.{RESET}")


if __name__ == "__main__":
    main()
