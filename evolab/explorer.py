"""
evolab/explorer.py — LLM 탐색가 (Claude Code `claude -p` 연결)

역할: 명예의 전당 상위 전략의 산술식·사유를 LLM에게 보여주고,
'더 나은 산술식 + 사유'를 가진 새 전략 코드를 생성하게 한다 (자유 탐색 + 변이).

⚠️ 보안: LLM이 생성한 코드를 실행하므로 두 단계로 막는다.
  1) 정적 검사 — import/os/eval/__ 등 위험 토큰 포함 시 거부
  2) 샌드박스 실행 — 제한된 builtins/모듈만 주입, 실제 generate()를 몇 회차 돌려
     6개 유효 번호(1~45, 중복 없음)를 내놓는지 검증. 하나라도 어기면 거부.
  (※ 완벽한 샌드박스는 아니다 — 로컬 개인용 + 신뢰 가능한 Claude 출력 전제.
     낯선 LLM/원격 실행엔 컨테이너 격리를 권장.)
"""

import json
import math
import os
import random
import re
import subprocess
from collections import Counter, defaultdict
from typing import List, Dict

from strategies import Strategy

# ------------------------------------------------------------------
# 1. 프롬프트
# ------------------------------------------------------------------
CONTRACT = '''\
너는 로또 6/45 번호 생성 '전략'을 만드는 진화 엔진의 탐색가다.
아래 규칙을 반드시 지켜 새 전략 N개를 제안하라.

[정직성 — 매우 중요]
- 6/45에서 6개를 고르면 기대 적중 개수는 어떤 전략이든 0.8개로 동일하다.
- 따라서 '당첨 확률을 올린다'는 거짓이다. 만들지 마라.
- 의미 있는 목표는 두 가지뿐:
  (a) 비인기 조합(분배 회피): 1~31 생일 범위 쏠림·연속수·구간쏠림을 피한다.
  (b) 통계 건전성: 합계 100~170, 홀짝 2:4~4:2, 번호 분산.
- 산술식(formula)과 사유(rationale)는 솔직해야 한다. 근거가 약하면 약하다고 적어라.

[코드 계약]
- 각 전략은 파이썬 함수 하나로 작성한다:
      def generate(history, round_num):
          ...
          return sorted([6개 정수])   # 1~45, 중복 없음
- history: 회차 dict 리스트. 각 dict은 {"round":int, "numbers":[6개], "bonus":int, "rank1":{"winners":int,...}, ...}
- 반드시 round_num '이전' 회차만 사용하라. 미래 참조 금지.
- 사용 가능한 전역: random, math, Counter, defaultdict, 그리고 헬퍼
      past(history, round_num, n=None)  # round_num 이전 회차를 최신순으로 n개 반환
- import 금지. open/eval/exec/os/sys 등 일절 금지. 오직 위 전역만.

[출력 형식 — 엄격]
다른 말 없이 JSON 배열만 출력하라. 각 원소:
  {"name": "짧은_한글이름", "formula": "산술식 한 줄", "rationale": "사유 1~2문장", "code": "def generate(history, round_num):\\n    ..."}
'''


def build_prompt(hall_entries: List[Dict], n: int = 2, lens: str = "") -> str:
    top = hall_entries[:5]
    inspire = "\n".join(
        f'- {e["name"]}: formula="{e["formula"]}" / fitness={e["metrics"]["fitness"]} '
        f'/ ROI={e["metrics"]["roi"]} / 비인기={e["metrics"]["unpopularity"]}'
        for e in top
    ) or "(아직 없음)"
    lens_block = f"\n[이 섬의 탐색 방향]\n{lens}\n" if lens else ""
    return (
        f"{CONTRACT}\n\n[현재 명예의 전당 상위 전략 — 참고/변이 대상(= 다른 섬이 공유한 지식)]\n"
        f"{inspire}\n{lens_block}\n"
        f"위를 참고해 서로 다른 접근의 새 전략 {n}개를 JSON 배열로 제안하라."
    )


# 섬(island): 각자 다른 탐색 관점. 모두 같은 명예의 전당을 공유(= 이주/지식 전파).
ISLANDS = [
    {"name": "분배회피", "lens": "비인기 조합(분배 회피)을 극대화하라. 32~45 고번호 활용, "
                                "생일범위(1~31) 쏠림·연속수 회피를 산술식에 직접 녹여라."},
    {"name": "통계건전성", "lens": "합계 100~170, 홀짝 2:4~4:2, 전 구간 고른 분산 같은 "
                                  "통계적 정상성을 산술식으로 강제하라."},
    {"name": "빈도주기", "lens": "출현 빈도·주기·간격 통계를 산술식의 핵심으로 삼아라. "
                                "단, 도박사의 오류 가능성을 사유에 솔직히 명시하라."},
    {"name": "외부수치시드", "lens": "당첨자수·판매액·날짜 같은 외부 수치를 결정적 시드로 쓰는 "
                                    "새로운 매핑을 설계하라. 근거가 약하면 약하다고 적어라."},
]


# ------------------------------------------------------------------
# 2. claude -p 호출
# ------------------------------------------------------------------
def call_claude(prompt: str, timeout: int = 180) -> str:
    """claude CLI를 헤드리스(-p)로 호출해 응답 텍스트를 받는다."""
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, encoding="utf-8", timeout=timeout,
        )
        return proc.stdout or ""
    except FileNotFoundError:
        print("⚠️ claude CLI 없음 — LLM 탐색 건너뜀")
        return ""
    except subprocess.TimeoutExpired:
        print("⚠️ claude 호출 타임아웃 — LLM 탐색 건너뜀")
        return ""


def extract_json(text: str):
    """응답에서 JSON 배열만 추출 (```json 펜스/잡설 제거)."""
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    raw = m.group(1) if m else None
    if raw is None:
        s, e = text.find("["), text.rfind("]")
        raw = text[s:e + 1] if (s != -1 and e > s) else None
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


# ------------------------------------------------------------------
# 3. 안전 검사 + 샌드박스
# ------------------------------------------------------------------
FORBIDDEN = re.compile(
    r"\b(import|exec|eval|open|compile|globals|locals|getattr|setattr|"
    r"delattr|os|sys|subprocess|socket|input|__\w+__|file)\b"
)

SAFE_BUILTINS = {
    "range": range, "len": len, "min": min, "max": max, "sum": sum, "abs": abs,
    "sorted": sorted, "set": set, "list": list, "dict": dict, "tuple": tuple,
    "round": round, "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
    "int": int, "float": float, "bool": bool, "any": any, "all": all, "reversed": reversed,
}


def _past(history, round_num, n=None):
    prev = sorted([h for h in history if h["round"] < round_num],
                  key=lambda x: x["round"], reverse=True)
    return prev[:n] if n else prev


def compile_generate(code: str):
    """코드 문자열 → generate 콜러블. 위험하면 ValueError."""
    if FORBIDDEN.search(code):
        raise ValueError("금지 토큰 포함")
    sandbox = {
        "__builtins__": SAFE_BUILTINS,
        "random": random, "math": math,
        "Counter": Counter, "defaultdict": defaultdict, "past": _past,
    }
    exec(code, sandbox)                       # 제한된 네임스페이스에서만 실행
    fn = sandbox.get("generate")
    if not callable(fn):
        raise ValueError("generate 함수 없음")
    return fn


def validate(fn, data: List[Dict]) -> bool:
    """샘플 회차로 실제 실행 → 6개 유효 번호 내놓는지 검증."""
    sample_rounds = [d["round"] for d in data[-5:]]
    for rn in sample_rounds:
        try:
            out = fn(data, rn)
        except Exception:
            return False
        if not isinstance(out, (list, tuple)) or len(out) != 6:
            return False
        if len(set(out)) != 6:
            return False
        if not all(isinstance(x, int) and 1 <= x <= 45 for x in out):
            return False
    return True


# ------------------------------------------------------------------
# 4. 동적 전략
# ------------------------------------------------------------------
class DynamicStrategy(Strategy):
    def __init__(self, name, formula, rationale, code, generation=1, parents=None):
        super().__init__(generation, parents or [])
        self.name = name
        self.formula = formula
        self.rationale = rationale
        self.code = code
        self._fn = compile_generate(code)

    def generate(self, history, round_num):
        out = self._fn(history, round_num)
        return sorted(int(x) for x in out)

    def meta(self):
        d = super().meta()
        d["code"] = self.code
        return d


def build_from_spec(spec: Dict, data: List[Dict], generation: int) -> "DynamicStrategy":
    """LLM 스펙 → 검증된 DynamicStrategy. 실패 시 None."""
    for key in ("name", "formula", "rationale", "code"):
        if key not in spec:
            return None
    try:
        st = DynamicStrategy(spec["name"], spec["formula"], spec["rationale"],
                             spec["code"], generation=generation)
    except (ValueError, SyntaxError):
        return None
    if not validate(st._fn, data):
        return None
    return st


# ------------------------------------------------------------------
# 5. 진입점
# ------------------------------------------------------------------
def _accept(specs, data, gen, origin=None):
    accepted, rejected = [], 0
    for spec in specs:
        st = build_from_spec(spec, data, gen)
        if st:
            if origin:
                st.parents = [f"island:{origin}"]
            accepted.append(st)
        else:
            rejected += 1
    return accepted, rejected


def propose(hall_entries: List[Dict], data: List[Dict], n: int = 2) -> List["DynamicStrategy"]:
    """단일 탐색가: LLM에게 새 전략 n개를 받아 검증 통과분만 반환."""
    text = call_claude(build_prompt(hall_entries, n))
    specs = extract_json(text)
    if not specs:
        print("⚠️ LLM 제안 파싱 실패 또는 빈 응답")
        return []
    gen = 1 + max((e.get("generation", 0) for e in hall_entries), default=0)
    accepted, rejected = _accept(specs, data, gen)
    print(f"🧪 LLM 제안 {len(specs)}개 → 검증통과 {len(accepted)}개 / 거부 {rejected}개")
    return accepted


def propose_islands(hall_entries: List[Dict], data: List[Dict],
                    n_per: int = 1, parallel: bool = True) -> List["DynamicStrategy"]:
    """
    섬 모델: 각 섬이 서로 다른 관점으로 동시에 LLM 탐색 → 전부 모아 검증 → 이름 dedup.
    모든 섬이 같은 명예의 전당을 프롬프트에 받으므로 좋은 전략이 자연히 전파(이주)된다.
    """
    gen = 1 + max((e.get("generation", 0) for e in hall_entries), default=0)

    def run(island):
        text = call_claude(build_prompt(hall_entries, n_per, lens=island["lens"]))
        specs = extract_json(text)
        accepted, rejected = _accept(specs, data, gen, origin=island["name"])
        print(f"🏝️ [{island['name']}] 제안 {len(specs)} → 통과 {len(accepted)} / 거부 {rejected}")
        return accepted

    results: List = []
    if parallel:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(ISLANDS)) as ex:
            for acc in ex.map(run, ISLANDS):
                results.extend(acc)
    else:
        for island in ISLANDS:
            results.extend(run(island))

    seen, out = set(), []
    for s in results:
        if s.name not in seen:
            seen.add(s.name)
            out.append(s)
    print(f"🌊 섬 {len(ISLANDS)}개 → 총 통과(중복제거) {len(out)}개")
    return out
