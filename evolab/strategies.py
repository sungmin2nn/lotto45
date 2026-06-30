"""
evolab/strategies.py — 번호 생성 전략

모든 전략은 반드시 다음을 갖는다 (헌법):
  · name      : 식별용 이름
  · formula   : 산술식 (어떻게 번호를 뽑는지의 계산 규칙, 문자열)
  · rationale : 사유 (왜 이 방식이 의미 있다고 보는지)
  · generate(): 과거 데이터만 보고 6개 번호를 반환 (미래 참조 금지!)

formula/rationale 가 문자열로 강제되는 이유:
  나중에 LLM(탐색가)이 이 필드들을 '읽고' 변이시켜 새 전략을 만들기 때문이다.
  사람이 사유를 댈 수 있어야 하고, 기계도 그 사유를 다룰 수 있어야 한다.
"""

import random
from collections import Counter
from typing import List, Dict


class Strategy:
    """전략 기본 클래스."""

    name: str = "base"
    formula: str = ""
    rationale: str = ""

    def __init__(self, generation: int = 0, parents: List[str] = None):
        self.generation = generation
        self.parents = parents or []

    @property
    def id(self) -> str:
        return f"{self.name}"

    def past(self, history: List[Dict], round_num: int, n: int = None) -> List[Dict]:
        """round_num '이전' 회차만 (미래 참조 차단). n개로 제한 가능."""
        prev = [h for h in history if h["round"] < round_num]
        prev.sort(key=lambda x: x["round"], reverse=True)
        return prev[:n] if n else prev

    def generate(self, history: List[Dict], round_num: int) -> List[int]:
        raise NotImplementedError

    def meta(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "formula": self.formula,
            "rationale": self.rationale,
            "generation": self.generation,
            "parents": self.parents,
        }

    @staticmethod
    def _fill(nums: List[int], pool: List[int] = None) -> List[int]:
        """6개가 안 되면 채우고, 넘치면 자른다."""
        nums = list(dict.fromkeys(nums))          # 중복 제거(순서 유지)
        if pool is None:
            pool = list(range(1, 46))
        while len(nums) < 6:
            c = random.choice(pool)
            if c not in nums:
                nums.append(c)
        return sorted(nums[:6])


# ======================================================================
# 샘플 전략 3종 (산술식 + 사유 포함)
# ======================================================================
class MostFrequent(Strategy):
    name = "최다출현_상위"
    formula = "freq[n] = Σ_(최근 50회) count(n);  상위 12개 중 6개 무작위"
    rationale = (
        "장기적으로 자주 나온 번호일수록 추첨 기계/공의 미세한 편향이 있다면 더 나올 "
        "여지가 있다고 가정. (※ 실증적 근거는 약하며 분산일 가능성 큼)"
    )

    def generate(self, history, round_num):
        past = self.past(history, round_num, 50)
        if len(past) < 5:
            return sorted(random.sample(range(1, 46), 6))
        freq = Counter()
        for h in past:
            freq.update(h["numbers"])
        top = [n for n, _ in freq.most_common(12)]
        return self._fill(random.sample(top, min(6, len(top))), top)


class WinnerCountSeed(Strategy):
    name = "당첨자수_시드"
    formula = (
        "seed = clip(직전회차_1등_당첨자수, 1, 45);  "
        "기준점 seed 에서 ±한 칸씩 퍼지며 미당첨 위주 6개 선택"
    )
    rationale = (
        "나루님 아이디어: '최근 당첨자 수'라는 외부 수치를 시드로 삼아 번호를 결정. "
        "확률적 근거는 없지만 산술식이 명확하고 재현 가능한 탐색 축이라 테스트 대상으로 둔다."
    )

    def generate(self, history, round_num):
        past = self.past(history, round_num, 1)
        if not past:
            return sorted(random.sample(range(1, 46), 6))
        seed = past[0].get("rank1", {}).get("winners", 1) or 1
        center = max(1, min(45, seed % 45 or 45))
        # center 주변으로 대칭 확장
        picks, step = [center], 1
        while len(picks) < 6 and step < 45:
            for cand in (center - step, center + step):
                if 1 <= cand <= 45 and cand not in picks and len(picks) < 6:
                    picks.append(cand)
            step += 1
        return self._fill(picks)


class CycleDue(Strategy):
    name = "주기성_나올때됨"
    formula = (
        "gap[n] = 현재회차 - n의_마지막출현회차;  "
        "interval[n] = n의_평균출현간격;  "
        "score[n] = gap[n] / interval[n];  상위(만기 임박) 12개 중 6개"
    )
    rationale = (
        "각 번호의 평균 출현 주기 대비 '쉰 기간'이 길면 나올 때가 됐다고 보는 주기성 가설. "
        "(※ 도박사의 오류일 수 있음 — 독립 추첨에선 과거가 미래를 강제하지 않는다. 그래도 측정해본다)"
    )

    def generate(self, history, round_num):
        past = self.past(history, round_num)
        if len(past) < 20:
            return sorted(random.sample(range(1, 46), 6))
        last_seen, counts = {}, Counter()
        for h in sorted(past, key=lambda x: x["round"]):
            for n in h["numbers"]:
                last_seen[n] = h["round"]
                counts[n] += 1
        total = len(past)
        scores = {}
        for n in range(1, 46):
            interval = total / counts[n] if counts[n] else total
            gap = round_num - last_seen.get(n, 0)
            scores[n] = gap / interval if interval else 0
        top = [n for n, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:12]]
        return self._fill(random.sample(top, min(6, len(top))), top)


def seed_strategies() -> List[Strategy]:
    """0세대 시드 전략들."""
    return [MostFrequent(), WinnerCountSeed(), CycleDue()]
