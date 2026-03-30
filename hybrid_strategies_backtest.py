#!/usr/bin/env python3
"""
로또 복합/하이브리드 전략 백테스팅
15개의 복합 전략 구현 및 평가
"""

import json
import random
import math
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional

# ============================================================
# 기본 유틸리티 클래스
# ============================================================

class LottoStrategy:
    """번호 생성 전략 기본 클래스"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.introduced_round = 1
        self.active = True

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        """번호 6개 생성"""
        raise NotImplementedError

    def get_past_data(self, round_num: int, history: List[Dict], n: int = 10) -> List[Dict]:
        """해당 회차 이전 n개 회차 데이터 반환"""
        past = [h for h in history if h['round'] < round_num]
        return sorted(past, key=lambda x: x['round'], reverse=True)[:n]


# ============================================================
# 복합/하이브리드 전략 15개
# ============================================================

class HotPlusCarryoverStrategy(LottoStrategy):
    """1. HOT+이월: 최근 핫번호 + 이월 예측 조합"""

    def __init__(self):
        super().__init__("HOT+이월", "최근 10회 핫번호 상위 + 직전회차 이월번호(미출현) 조합")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 10)
        if len(past) < 2:
            return sorted(random.sample(range(1, 46), 6))

        # HOT 번호 (최근 10회)
        freq = defaultdict(int)
        for h in past:
            for n in h['numbers']:
                freq[n] += 1
        hot_nums = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)[:10]

        # 이월 번호 (직전 회차에 없었던 번호)
        last_nums = set(past[0]['numbers'])
        carryover = [n for n in range(1, 46) if n not in last_nums]

        # 교집합 우선, 그 다음 합집합
        candidates = list(set(hot_nums) & set(carryover))
        if len(candidates) < 6:
            candidates.extend([n for n in hot_nums if n not in candidates])
        if len(candidates) < 6:
            candidates.extend([n for n in carryover if n not in candidates])

        if len(candidates) >= 6:
            return sorted(random.sample(candidates, 6))
        return sorted(random.sample(range(1, 46), 6))


class ColdPlusDistributionStrategy(LottoStrategy):
    """2. COLD+분산: 콜드번호 + 균등분산 조합"""

    def __init__(self):
        super().__init__("COLD+분산", "최근 10회 미출현 콜드번호 + 각 구간별 균등분산")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 10)
        if len(past) < 3:
            return sorted(random.sample(range(1, 46), 6))

        # COLD 번호
        appeared = set()
        for h in past:
            appeared.update(h['numbers'])
        cold = [n for n in range(1, 46) if n not in appeared]

        # 구간별 분산
        zones = [
            list(range(1, 10)),
            list(range(10, 20)),
            list(range(20, 30)),
            list(range(30, 40)),
            list(range(40, 46))
        ]

        selected = []
        # 각 구간에서 COLD 번호 우선
        for zone in zones:
            zone_cold = [n for n in zone if n in cold]
            if zone_cold and len(selected) < 6:
                selected.append(random.choice(zone_cold))

        # 부족하면 일반 COLD 추가
        while len(selected) < 6 and cold:
            n = random.choice(cold)
            if n not in selected:
                selected.append(n)

        # 여전히 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.append(n)

        return sorted(selected[:6])


class SumOddEvenHighLowStrategy(LottoStrategy):
    """3. 합계+홀짝+고저: 3가지 조건 동시 만족"""

    def __init__(self):
        super().__init__("합계+홀짝+고저", "합 100~175 + 홀짝 3:3 + 고저 3:3")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        for _ in range(200):
            # 홀수/짝수 각 3개
            odds = random.sample([n for n in range(1, 46) if n % 2 == 1], 3)
            evens = random.sample([n for n in range(1, 46) if n % 2 == 0], 3)

            # 고저 분리
            low_odds = [n for n in odds if n < 23]
            high_odds = [n for n in odds if n >= 23]
            low_evens = [n for n in evens if n < 23]
            high_evens = [n for n in evens if n >= 23]

            # 고저 균형 조정
            total_low = len(low_odds) + len(low_evens)
            if total_low == 3:  # 이미 균형
                nums = sorted(odds + evens)
                if 100 <= sum(nums) <= 175:
                    return nums

        # 실패시 기본 로직
        return sorted(random.sample(range(1, 46), 6))


class PairPlusMomentumStrategy(LottoStrategy):
    """4. 궁합+모멘텀: 궁합 좋은 쌍 + 상승추세"""

    def __init__(self):
        super().__init__("궁합+모멘텀", "과거 궁합 좋은 번호쌍 + 최근 출현빈도 상승 번호")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 50)
        if len(past) < 20:
            return sorted(random.sample(range(1, 46), 6))

        # 궁합 쌍
        pair_freq = defaultdict(int)
        for h in past[:30]:
            nums = h['numbers']
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    pair = tuple(sorted([nums[i], nums[j]]))
                    pair_freq[pair] += 1

        top_pairs = sorted(pair_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        pair_nums = set()
        for pair, _ in top_pairs:
            pair_nums.update(pair)

        # 모멘텀 (최근 10회 vs 그 이전 10회)
        recent_freq = defaultdict(int)
        old_freq = defaultdict(int)
        for h in past[:10]:
            for n in h['numbers']:
                recent_freq[n] += 1
        for h in past[10:20]:
            for n in h['numbers']:
                old_freq[n] += 1

        momentum = []
        for n in range(1, 46):
            if recent_freq[n] > old_freq[n]:
                momentum.append(n)

        # 조합
        candidates = list(pair_nums & set(momentum))
        if len(candidates) < 6:
            candidates.extend([n for n in pair_nums if n not in candidates])
        if len(candidates) < 6:
            candidates.extend([n for n in momentum if n not in candidates])

        if len(candidates) >= 6:
            return sorted(random.sample(candidates, 6))
        return sorted(random.sample(range(1, 46), 6))


class FibonacciPlusPrimeStrategy(LottoStrategy):
    """5. 피보나치+소수: 피보나치 + 소수 교집합"""

    def __init__(self):
        super().__init__("피보나치+소수", "피보나치 수 + 소수 교집합 우선")
        self.fib = [1, 2, 3, 5, 8, 13, 21, 34]
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 교집합
        intersection = list(set(self.fib) & set(self.primes))

        # 피보나치 확장
        fib_extended = set(self.fib)
        for f in self.fib:
            if f > 1:
                fib_extended.add(f - 1)
            if f < 45:
                fib_extended.add(f + 1)

        # 조합
        candidates = intersection.copy()
        if len(candidates) < 6:
            candidates.extend([n for n in self.primes if n not in candidates])
        if len(candidates) < 6:
            candidates.extend([n for n in fib_extended if n not in candidates and 1 <= n <= 45])

        if len(candidates) >= 6:
            return sorted(random.sample(candidates, 6))

        while len(candidates) < 6:
            n = random.randint(1, 45)
            if n not in candidates:
                candidates.append(n)
        return sorted(candidates[:6])


class ConsecutivePlusScatteredStrategy(LottoStrategy):
    """6. 연속+비연속: 연속2개 + 분산4개"""

    def __init__(self):
        super().__init__("연속+비연속", "연속번호 2개 + 나머지는 10이상 간격 분산")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 연속 2개
        start = random.randint(1, 44)
        consecutive = [start, start + 1]

        # 분산 4개 (10 이상 간격)
        pool = [n for n in range(1, 46) if n not in consecutive]
        scattered = []

        for _ in range(100):
            attempt = sorted(random.sample(pool, 4))
            # 간격 체크
            valid = True
            all_nums = sorted(consecutive + attempt)
            for i in range(len(all_nums) - 1):
                if i == 0 or i == len(all_nums) - 2:  # 연속 쌍은 제외
                    continue
                if all_nums[i+1] - all_nums[i] < 5:
                    valid = False
                    break
            if valid:
                scattered = attempt
                break

        if not scattered:
            scattered = random.sample(pool, 4)

        return sorted(consecutive + scattered)


class MirrorPlusCarryoverStrategy(LottoStrategy):
    """7. 거울+이월: 거울번호 + 이월번호"""

    def __init__(self):
        super().__init__("거울+이월", "거울번호(46-n) + 직전회차 미출현")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 1)
        if len(past) < 1:
            return sorted(random.sample(range(1, 46), 6))

        # 직전 회차 번호의 거울
        last_nums = past[0]['numbers']
        mirrors = [46 - n for n in last_nums if 1 <= 46 - n <= 45]

        # 이월 (직전 미출현)
        carryover = [n for n in range(1, 46) if n not in last_nums]

        # 조합
        candidates = list(set(mirrors) & set(carryover))
        if len(candidates) < 6:
            candidates.extend([n for n in mirrors if n not in candidates])
        if len(candidates) < 6:
            candidates.extend([n for n in carryover if n not in candidates])

        if len(candidates) >= 6:
            return sorted(random.sample(candidates, 6))
        return sorted(random.sample(range(1, 46), 6))


class EntropyPlusSumStrategy(LottoStrategy):
    """8. 엔트로피+합계: 엔트로피 최대 + 합계범위"""

    def __init__(self):
        super().__init__("엔트로피+합계", "끝수/구간 엔트로피 최대 + 합 100~175")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        for _ in range(200):
            nums = sorted(random.sample(range(1, 46), 6))

            # 합계 조건
            if not (100 <= sum(nums) <= 175):
                continue

            # 끝수 다양성
            ends = [n % 10 for n in nums]
            if len(set(ends)) < 5:
                continue

            # 구간 다양성 (1-15, 16-30, 31-45)
            zones = [0, 0, 0]
            for n in nums:
                if n <= 15:
                    zones[0] += 1
                elif n <= 30:
                    zones[1] += 1
                else:
                    zones[2] += 1

            # 최소 1개씩
            if min(zones) >= 1:
                return nums

        return sorted(random.sample(range(1, 46), 6))


class ClusterPlusGapStrategy(LottoStrategy):
    """9. 클러스터+갭: 클러스터 + 갭패턴"""

    def __init__(self):
        super().__init__("클러스터+갭", "3개 클러스터(연속/인접) + 3개 갭(10+간격)")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 클러스터 3개 (5칸 이내)
        cluster_start = random.randint(1, 40)
        cluster_pool = list(range(cluster_start, min(cluster_start + 5, 46)))
        cluster = sorted(random.sample(cluster_pool, min(3, len(cluster_pool))))

        while len(cluster) < 3:
            cluster.append(random.randint(1, 45))
        cluster = sorted(list(set(cluster)))[:3]

        # 갭 3개
        gap_pool = [n for n in range(1, 46) if n not in cluster]
        gaps = []

        for _ in range(100):
            attempt = sorted(random.sample(gap_pool, 3))
            # 간격 10 이상
            valid = True
            for i in range(len(attempt) - 1):
                if attempt[i+1] - attempt[i] < 10:
                    valid = False
                    break
            if valid:
                gaps = attempt
                break

        if not gaps:
            gaps = random.sample(gap_pool, 3)

        return sorted(cluster + gaps)


class YinYangPlusSumStrategy(LottoStrategy):
    """10. 음양+합계: 음양균형 + 합계최적화"""

    def __init__(self):
        super().__init__("음양+합계", "음(짝수) 양(홀수) 균형 + 합계 최적")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 홀짝 균형 (3:3 or 4:2)
        patterns = [
            (3, 3),  # 홀3 짝3
            (4, 2),  # 홀4 짝2
            (2, 4),  # 홀2 짝4
        ]

        for _ in range(100):
            odd_count, even_count = random.choice(patterns)
            odds = random.sample([n for n in range(1, 46) if n % 2 == 1], odd_count)
            evens = random.sample([n for n in range(1, 46) if n % 2 == 0], even_count)
            nums = sorted(odds + evens)

            if 100 <= sum(nums) <= 175:
                return nums

        return sorted(random.sample(range(1, 46), 6))


class MoonPlusZodiacStrategy(LottoStrategy):
    """11. 달+띠: 달의위상 + 띠 조합"""

    def __init__(self):
        super().__init__("달+띠", "회차를 달의위상(28일주기), 띠(12간지) 매핑")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 달의 위상 (28일 주기)
        moon_phase = round_num % 28
        moon_nums = [(moon_phase * i) % 45 + 1 for i in range(1, 4)]

        # 띠 (12간지)
        zodiac = round_num % 12
        zodiac_nums = [(zodiac * i + round_num) % 45 + 1 for i in range(1, 4)]

        candidates = list(set(moon_nums + zodiac_nums))

        while len(candidates) < 6:
            n = random.randint(1, 45)
            if n not in candidates:
                candidates.append(n)

        return sorted(random.sample(candidates, min(6, len(candidates))) if len(candidates) >= 6 else candidates[:6])


class StatsPlusNumerologyStrategy(LottoStrategy):
    """12. 통계+점술: 빈도분석 + 수비학"""

    def __init__(self):
        super().__init__("통계+점술", "HOT번호 + 생명수(각 자릿수 합) 조합")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 20)
        if len(past) < 5:
            return sorted(random.sample(range(1, 46), 6))

        # 통계 (HOT)
        freq = defaultdict(int)
        for h in past:
            for n in h['numbers']:
                freq[n] += 1
        hot = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)[:10]

        # 수비학 (생명수: 각 자릿수 합)
        life_nums = []
        for n in range(1, 46):
            digit_sum = sum(int(d) for d in str(n))
            if digit_sum % 3 == round_num % 3:  # 회차 모듈로 매칭
                life_nums.append(n)

        candidates = list(set(hot) & set(life_nums))
        if len(candidates) < 6:
            candidates.extend([n for n in hot if n not in candidates])
        if len(candidates) < 6:
            candidates.extend([n for n in life_nums if n not in candidates])

        if len(candidates) >= 6:
            return sorted(random.sample(candidates, 6))
        return sorted(random.sample(range(1, 46), 6))


class HistoricalBestStrategy(LottoStrategy):
    """13. 역대최고: 역대 최다 당첨 조합 패턴"""

    def __init__(self):
        super().__init__("역대최고", "역대 최다출현 번호 + 최다출현 패턴")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 100)
        if len(past) < 10:
            return sorted(random.sample(range(1, 46), 6))

        # 전체 빈도
        freq = defaultdict(int)
        for h in past:
            for n in h['numbers']:
                freq[n] += 1

        # 상위 12개
        top_nums = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)[:12]

        # 패턴: 연속 있는지 체크
        has_consecutive = False
        for h in past[:20]:
            nums = sorted(h['numbers'])
            for i in range(len(nums) - 1):
                if nums[i+1] - nums[i] == 1:
                    has_consecutive = True
                    break

        # 조합
        if has_consecutive:
            # 연속 1쌍 포함
            selected = []
            for i in range(len(top_nums) - 1):
                if top_nums[i+1] - top_nums[i] == 1:
                    selected = [top_nums[i], top_nums[i+1]]
                    break

            if not selected:
                selected = [top_nums[0], top_nums[0] + 1] if top_nums[0] < 45 else [top_nums[0], top_nums[1]]

            rest = [n for n in top_nums if n not in selected]
            selected.extend(random.sample(rest, min(4, len(rest))))
        else:
            selected = random.sample(top_nums, 6)

        return sorted(selected[:6])


class EnsembleStrategy(LottoStrategy):
    """14. 앙상블: 상위5개 전략 투표"""

    def __init__(self):
        super().__init__("앙상블", "여러 전략 결과 투표로 최다 선택 번호")
        self.sub_strategies = [
            HotPlusCarryoverStrategy(),
            PairPlusMomentumStrategy(),
            SumOddEvenHighLowStrategy(),
            FibonacciPlusPrimeStrategy(),
            EntropyPlusSumStrategy(),
        ]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        votes = defaultdict(int)

        for strategy in self.sub_strategies:
            nums = strategy.generate(round_num, history)
            for n in nums:
                votes[n] += 1

        # 투표수 상위
        sorted_nums = sorted(votes.keys(), key=lambda x: votes[x], reverse=True)

        if len(sorted_nums) >= 6:
            return sorted(sorted_nums[:6])

        # 부족하면 랜덤 추가
        while len(sorted_nums) < 6:
            n = random.randint(1, 45)
            if n not in sorted_nums:
                sorted_nums.append(n)

        return sorted(sorted_nums[:6])


class MetaLearningStrategy(LottoStrategy):
    """15. 메타_학습: 최근 성과 좋은 전략 가중치"""

    def __init__(self):
        super().__init__("메타_학습", "최근 10회 성과 분석해 좋은 전략 가중")
        self.sub_strategies = [
            HotPlusCarryoverStrategy(),
            ColdPlusDistributionStrategy(),
            SumOddEvenHighLowStrategy(),
            PairPlusMomentumStrategy(),
            ConsecutivePlusScatteredStrategy(),
        ]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 10)
        if len(past) < 5:
            return sorted(random.sample(range(1, 46), 6))

        # 각 전략 평가
        scores = defaultdict(float)
        for strategy in self.sub_strategies:
            total_match = 0
            for h in past:
                pred = strategy.generate(h['round'], history)
                match = len(set(pred) & set(h['numbers']))
                total_match += match
            scores[strategy.name] = total_match

        # 최고 전략 2개 선택
        best_strategies = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]

        candidates = []
        for name, score in best_strategies:
            for strategy in self.sub_strategies:
                if strategy.name == name:
                    nums = strategy.generate(round_num, history)
                    candidates.extend(nums)

        candidates = list(set(candidates))

        if len(candidates) >= 6:
            return sorted(random.sample(candidates, 6))

        while len(candidates) < 6:
            n = random.randint(1, 45)
            if n not in candidates:
                candidates.append(n)

        return sorted(candidates[:6])


# ============================================================
# 백테스팅 엔진
# ============================================================

class BacktestEngine:
    """백테스팅 엔진"""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.history = self.load_data()
        self.strategies = self.init_strategies()
        self.results = {}

    def load_data(self) -> List[Dict]:
        """로또 데이터 로드"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x['round'])

    def init_strategies(self) -> List[LottoStrategy]:
        """복합 전략들 초기화"""
        return [
            HotPlusCarryoverStrategy(),
            ColdPlusDistributionStrategy(),
            SumOddEvenHighLowStrategy(),
            PairPlusMomentumStrategy(),
            FibonacciPlusPrimeStrategy(),
            ConsecutivePlusScatteredStrategy(),
            MirrorPlusCarryoverStrategy(),
            EntropyPlusSumStrategy(),
            ClusterPlusGapStrategy(),
            YinYangPlusSumStrategy(),
            MoonPlusZodiacStrategy(),
            StatsPlusNumerologyStrategy(),
            HistoricalBestStrategy(),
            EnsembleStrategy(),
            MetaLearningStrategy(),
        ]

    def check_match(self, prediction: List[int], actual: List[int], bonus: int) -> Tuple[int, str]:
        """당첨 확인"""
        match_count = len(set(prediction) & set(actual))
        bonus_match = bonus in prediction

        if match_count == 6:
            return match_count, "1등"
        elif match_count == 5 and bonus_match:
            return match_count, "2등"
        elif match_count == 5:
            return match_count, "3등"
        elif match_count == 4:
            return match_count, "4등"
        elif match_count == 3:
            return match_count, "5등"
        else:
            return match_count, "낙첨"

    def run_backtest(self, start_round: int = 1, end_round: Optional[int] = None):
        """백테스팅 실행"""
        if end_round is None:
            end_round = max(h['round'] for h in self.history)

        print(f"\n{'='*70}")
        print(f"복합/하이브리드 전략 백테스팅 시작")
        print(f"{'='*70}")
        print(f"회차 범위: {start_round}회 ~ {end_round}회")
        print(f"전략 수: {len(self.strategies)}개")
        print(f"{'='*70}\n")

        for h in self.history:
            round_num = h['round']
            if round_num < start_round or round_num > end_round:
                continue

            actual = h['numbers']
            bonus = h.get('bonus', 0)

            self.results[round_num] = {}

            for strategy in self.strategies:
                if not strategy.active:
                    continue

                prediction = strategy.generate(round_num, self.history)
                match_count, rank = self.check_match(prediction, actual, bonus)

                self.results[round_num][strategy.name] = {
                    'numbers': prediction,
                    'match': match_count,
                    'rank': rank,
                }

            if round_num % 100 == 0:
                print(f"진행중: {round_num}회 완료...")

        print(f"\n{'='*70}")
        print("백테스팅 완료!")
        print(f"{'='*70}\n")

    def get_statistics(self) -> Dict:
        """전체 통계 계산"""
        stats = {}

        for strategy in self.strategies:
            name = strategy.name
            results = []

            for round_num, round_results in self.results.items():
                if name in round_results:
                    results.append(round_results[name])

            if not results:
                continue

            total = len(results)
            rank_counts = defaultdict(int)
            match_sum = 0

            for r in results:
                rank_counts[r['rank']] += 1
                match_sum += r['match']

            # 수익률 계산 (1게임 1,000원 기준)
            cost = total * 1000
            # 평균 상금 (간단 추정)
            revenue = (
                rank_counts['1등'] * 2000000000 +
                rank_counts['2등'] * 50000000 +
                rank_counts['3등'] * 1500000 +
                rank_counts['4등'] * 50000 +
                rank_counts['5등'] * 5000
            )
            roi = ((revenue - cost) / cost * 100) if cost > 0 else 0

            stats[name] = {
                'total': total,
                'avg_match': round(match_sum / total, 2),
                '1등': rank_counts['1등'],
                '2등': rank_counts['2등'],
                '3등': rank_counts['3등'],
                '4등': rank_counts['4등'],
                '5등': rank_counts['5등'],
                '4등+': rank_counts['1등'] + rank_counts['2등'] + rank_counts['3등'] + rank_counts['4등'],
                '4등+율': round((rank_counts['1등'] + rank_counts['2등'] + rank_counts['3등'] + rank_counts['4등']) / total * 100, 2),
                '수익률': round(roi, 2),
            }

        return stats

    def print_summary(self):
        """결과 요약 출력"""
        stats = self.get_statistics()

        print("\n" + "=" * 120)
        print("복합/하이브리드 전략 백테스팅 결과")
        print("=" * 120)

        # 4등+ 비율로 정렬
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['4등+율'], reverse=True)

        print(f"\n{'순위':<4} {'전략명':<20} {'총회차':<8} {'1등':<6} {'2등':<6} {'3등':<6} {'4등':<6} {'5등':<6} {'4등+':<8} {'4등+율':<10} {'수익률%':<10}")
        print("-" * 120)

        for i, (name, s) in enumerate(sorted_stats, 1):
            print(f"{i:<4} {name:<20} {s['total']:<8} {s['1등']:<6} {s['2등']:<6} {s['3등']:<6} {s['4등']:<6} {s['5등']:<6} {s['4등+']:<8} {s['4등+율']:<10.2f}% {s['수익률']:<10.2f}%")

        print("=" * 120)
        print(f"\n{'='*120}")
        print("주요 통계")
        print(f"{'='*120}")

        # 평균
        avg_4plus = sum(s['4등+율'] for s in stats.values()) / len(stats)
        avg_roi = sum(s['수익률'] for s in stats.values()) / len(stats)

        print(f"평균 4등+ 비율: {avg_4plus:.2f}%")
        print(f"평균 수익률: {avg_roi:.2f}%")

        # 최고 성과
        best_4plus = sorted_stats[0]
        print(f"\n최고 4등+ 전략: {best_4plus[0]} ({best_4plus[1]['4등+율']:.2f}%)")

        best_roi = max(stats.items(), key=lambda x: x[1]['수익률'])
        print(f"최고 수익률 전략: {best_roi[0]} ({best_roi[1]['수익률']:.2f}%)")

        print(f"{'='*120}\n")


# ============================================================
# 메인 실행
# ============================================================

def main():
    import os
    import sys

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'lotto_data.json')

    if not os.path.exists(data_path):
        print(f"오류: {data_path} 파일을 찾을 수 없습니다.")
        sys.exit(1)

    engine = BacktestEngine(data_path)
    engine.run_backtest(start_round=1)
    engine.print_summary()


if __name__ == '__main__':
    main()
