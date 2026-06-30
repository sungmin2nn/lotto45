"""
evolab/core.py — 데이터 로딩 · 채점 · 적합도 계산 (결정적, LLM 무관)

이 모듈은 "사실"만 다룬다. LLM이나 전략의 주관이 끼어들지 않는
순수 함수들 — 데이터 로딩, 당첨 채점, ROI/적합도 계산.

⚠️ 정직성 메모:
- 6/45에서 6개를 고르면 기대 적중 개수는 어떤 전략이든 동일하게 0.8개다.
  따라서 백테스트에서 어떤 전략의 ROI가 높게 나와도 그것은 대부분 '분산(운)'이다.
- 수학적으로 실재하는 유일한 엣지: 1·2·3등(분배 등수)에서 '남들이 안 고르는 조합'을
  택해 당첨 시 수령액을 키우는 것 → unpopularity_score 로 근사.
- 4·5등은 고정 상금이라 분배 회피가 안 먹힌다.
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

TICKET_COST = 1000

# 1~3등은 회차마다 분배되어 변동 → 데이터에 실제 상금이 있으면 그걸 쓰고,
# 없으면(미래 회차 예측) 아래 대표 기본값으로 대체한다.
DEFAULT_PRIZE = {1: 2_000_000_000, 2: 50_000_000, 3: 1_500_000, 4: 50_000, 5: 5_000}

NUM_MIN, NUM_MAX = 1, 45
PICK = 6


# ------------------------------------------------------------------
# 데이터
# ------------------------------------------------------------------
def load_data(path: str) -> List[Dict]:
    """lotto_data.json 로드 후 회차 오름차순 정렬."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return sorted(data, key=lambda x: x["round"])


def by_round(data: List[Dict]) -> Dict[int, Dict]:
    return {d["round"]: d for d in data}


# ------------------------------------------------------------------
# 채점
# ------------------------------------------------------------------
def grade(picked: List[int], actual_numbers: List[int], bonus: int) -> Tuple[int, int]:
    """선택 6개를 실제 당첨번호와 비교. (적중 개수, 등수) 반환. 등수 0 = 미당첨."""
    p, a = set(picked), set(actual_numbers)
    m = len(p & a)
    if m == 6:
        tier = 1
    elif m == 5 and bonus in p:
        tier = 2
    elif m == 5:
        tier = 3
    elif m == 4:
        tier = 4
    elif m == 3:
        tier = 5
    else:
        tier = 0
    return m, tier


def prize_for(tier: int, round_item: Optional[Dict] = None) -> int:
    """해당 등수의 상금. 회차 데이터에 실제 상금이 있으면 우선 사용."""
    if tier == 0:
        return 0
    if round_item is not None:
        rk = round_item.get(f"rank{tier}", {})
        p = rk.get("prize")
        if p:
            return int(p)
    return DEFAULT_PRIZE[tier]


# ------------------------------------------------------------------
# 적합도 구성요소 (모두 0..1, 높을수록 좋음)
# ------------------------------------------------------------------
def unpopularity_score(numbers: List[int]) -> float:
    """
    '남들이 잘 안 고르는 조합'일수록 높은 점수 (분배 회피용 근사).
    실제 조합별 판매 데이터가 없으므로 휴리스틱이다 — 사람이 흔히 고르는 패턴을 감점.
      · 생일 범위(1~31)에 몰릴수록 감점
      · 연속수가 많을수록 감점
      · 한쪽 구간에 쏠릴수록 감점
    """
    nums = sorted(numbers)
    score = 1.0

    # 1) 생일 편향: 32~45 번호가 적을수록 감점
    high = sum(1 for n in nums if n > 31)
    score -= (PICK - high) * 0.06          # 6개 모두 31 이하면 -0.36

    # 2) 연속수 페널티
    consec = sum(1 for i in range(len(nums) - 1) if nums[i + 1] - nums[i] == 1)
    score -= consec * 0.08

    # 3) 구간 쏠림: 1~45를 3구간으로 나눠 한 구간 독점 시 감점
    buckets = [0, 0, 0]
    for n in nums:
        buckets[min((n - 1) // 15, 2)] += 1
    score -= (max(buckets) - 2) * 0.05 if max(buckets) > 2 else 0

    return max(0.0, min(1.0, score))


def soundness_score(numbers: List[int]) -> float:
    """
    통계적으로 '정상 범위'에 가까울수록 높은 점수.
      · 합계가 역대 당첨 평균대(약 100~170) 안인가
      · 홀짝 균형 (2:4 ~ 4:2)
      · 번호 분산(너무 뭉치지 않음)
    """
    nums = sorted(numbers)
    score = 1.0

    s = sum(nums)
    if not (100 <= s <= 170):
        score -= min(0.4, abs(s - 135) / 135)

    odd = sum(1 for n in nums if n % 2 == 1)
    if odd in (0, 6):
        score -= 0.3
    elif odd in (1, 5):
        score -= 0.1

    spread = nums[-1] - nums[0]
    if spread < 20:
        score -= 0.2

    return max(0.0, min(1.0, score))


# ------------------------------------------------------------------
# 적합도 종합
# ------------------------------------------------------------------
@dataclass
class Metrics:
    """한 전략의 백테스트 성적표."""
    n_predictions: int = 0
    roi: float = 0.0                       # 티켓당 수익률 (관측치 = 분산 가능!)
    tier_hits: Dict[int, int] = field(default_factory=dict)   # {등수: 횟수}
    avg_match: float = 0.0
    unpopularity: float = 0.0
    soundness: float = 0.0
    fitness: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "n_predictions": self.n_predictions,
            "roi": round(self.roi, 4),
            "tier_hits": self.tier_hits,
            "avg_match": round(self.avg_match, 4),
            "unpopularity": round(self.unpopularity, 4),
            "soundness": round(self.soundness, 4),
            "fitness": round(self.fitness, 4),
        }


# 가중치: 진짜 신호(분배회피·건전성)에 무게를 주고, ROI는 '관측 노이즈'로 보조.
FITNESS_WEIGHTS = {"roi": 0.35, "unpopularity": 0.40, "soundness": 0.25}


def compute_fitness(m: Metrics) -> float:
    """
    적합도 = w_roi·norm(ROI) + w_unpop·비인기도 + w_sound·건전성
    norm(ROI): 로또 평균 환급률이 ~0.5라 ROI 1.0(본전)이면 0.5점, 2.0이면 만점.
    """
    roi_norm = max(0.0, min(1.0, m.roi / 2.0))
    w = FITNESS_WEIGHTS
    return w["roi"] * roi_norm + w["unpopularity"] * m.unpopularity + w["soundness"] * m.soundness
