#!/usr/bin/env python3
"""
자연현상/패턴 기반 로또 전략 15개
1. 달_주기: 29.5일 주기 활용
2. 계절_패턴: 봄여름가을겨울 번호대
3. 요일_특성: 토요일 추첨 요일 패턴
4. 소수_쌍둥이: 쌍둥이 소수 (11,13), (17,19)
5. 완전수: 6, 28 등 완전수 포함
6. 삼각수: 1,3,6,10,15,21,28,36,45
7. 사각수: 1,4,9,16,25,36
8. 회문수: 11,22,33,44
9. 배수_패턴: 특정 수의 배수들
10. 모듈러: mod 연산 기반
11. 비트_패턴: 이진수 패턴
12. 디지털_루트: 각 자리수 합의 반복
13. 번호_밀도: 구간별 밀도 분석
14. 반복_주기: n회 주기 반복 패턴
15. 대칭_번호: 합이 46이 되는 쌍
"""

import json
import random
import math
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional


# ============================================================
# 자연현상/패턴 기반 전략 클래스들
# ============================================================

class LottoStrategy:
    """번호 생성 전략 기본 클래스"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.introduced_round = 1
        self.active = True

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        """번호 6개 생성 (하위 클래스에서 구현)"""
        raise NotImplementedError

    def get_past_data(self, round_num: int, history: List[Dict], n: int = 10) -> List[Dict]:
        """해당 회차 이전 n개 회차 데이터 반환"""
        past = [h for h in history if h['round'] < round_num]
        return sorted(past, key=lambda x: x['round'], reverse=True)[:n]


class MoonCycleStrategy(LottoStrategy):
    """달 주기 전략 - 29.5일 주기 활용"""

    def __init__(self):
        super().__init__("달_주기", "29.5일 달 주기를 번호에 반영 (29, 30 중심)")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 달 주기 관련 번호: 29, 30 및 그 배수, 약수
        moon_related = [1, 2, 3, 5, 6, 10, 15, 29, 30]

        # 회차를 29.5로 나눈 나머지로 추가 번호 선택
        phase = int((round_num % 29.5) * 1.5)
        if 1 <= phase <= 45:
            moon_related.append(phase)

        # 중복 제거
        moon_related = list(set([n for n in moon_related if 1 <= n <= 45]))

        # 6개 선택 (부족하면 랜덤 추가)
        if len(moon_related) >= 6:
            return sorted(random.sample(moon_related, 6))
        else:
            extra = random.sample([n for n in range(1, 46) if n not in moon_related], 6 - len(moon_related))
            return sorted(moon_related + extra)


class SeasonalStrategy(LottoStrategy):
    """계절 패턴 전략 - 봄여름가을겨울 번호대"""

    def __init__(self):
        super().__init__("계절_패턴", "4계절을 번호대로 분할 (1-11봄, 12-22여름, 23-33가을, 34-45겨울)")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 4계절 구간
        spring = list(range(1, 12))    # 1-11
        summer = list(range(12, 23))   # 12-22
        autumn = list(range(23, 34))   # 23-33
        winter = list(range(34, 46))   # 34-45

        # 각 계절에서 균등하게 선택 (1~2개씩)
        selected = []
        selected.append(random.choice(spring))
        selected.append(random.choice(summer))
        selected.append(random.choice(autumn))
        selected.append(random.choice(winter))

        # 나머지 2개는 랜덤 계절에서
        seasons = [spring, summer, autumn, winter]
        for _ in range(2):
            season = random.choice(seasons)
            num = random.choice(season)
            while num in selected:
                season = random.choice(seasons)
                num = random.choice(season)
            selected.append(num)

        return sorted(selected[:6])


class WeekdayStrategy(LottoStrategy):
    """요일 특성 전략 - 토요일 추첨일 패턴"""

    def __init__(self):
        super().__init__("요일_특성", "토요일(6일) 관련 번호: 6, 7 및 6의 배수")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 토요일 관련: 6, 7 및 6의 배수
        saturday_nums = [6, 7, 12, 18, 24, 30, 36, 42]

        # 회차 % 7로 요일 시뮬레이션
        weekday_num = (round_num % 7) + 1
        if 1 <= weekday_num <= 45:
            saturday_nums.append(weekday_num)

        saturday_nums = list(set([n for n in saturday_nums if 1 <= n <= 45]))

        if len(saturday_nums) >= 6:
            return sorted(random.sample(saturday_nums, 6))
        else:
            extra = random.sample([n for n in range(1, 46) if n not in saturday_nums], 6 - len(saturday_nums))
            return sorted(saturday_nums + extra)


class TwinPrimeStrategy(LottoStrategy):
    """쌍둥이 소수 전략 - (11,13), (17,19), (29,31), (41,43)"""

    def __init__(self):
        super().__init__("소수_쌍둥이", "쌍둥이 소수 쌍 활용: (11,13), (17,19), (29,31), (41,43)")
        self.twin_primes = [(11, 13), (17, 19), (29, 31), (41, 43)]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        selected = []

        # 쌍둥이 소수 쌍 중 1~2쌍 선택
        num_pairs = random.randint(1, 2)
        for pair in random.sample(self.twin_primes, num_pairs):
            selected.extend(pair)

        # 나머지는 일반 소수에서
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
        while len(selected) < 6:
            num = random.choice(primes)
            if num not in selected:
                selected.append(num)

        return sorted(selected[:6])


class PerfectNumberStrategy(LottoStrategy):
    """완전수 전략 - 6, 28 등 완전수 포함"""

    def __init__(self):
        super().__init__("완전수", "완전수 6, 28과 그 약수들 활용")
        # 6의 약수: 1, 2, 3, 6
        # 28의 약수: 1, 2, 4, 7, 14, 28
        self.perfect_related = [1, 2, 3, 4, 6, 7, 14, 28]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 완전수 관련 번호
        candidates = self.perfect_related.copy()

        # 부족하면 합성수 추가
        composites = [n for n in range(4, 46) if n not in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]]

        while len(candidates) < 15:
            num = random.choice(composites)
            if num not in candidates:
                candidates.append(num)

        return sorted(random.sample(candidates, 6))


class TriangularNumberStrategy(LottoStrategy):
    """삼각수 전략 - 1,3,6,10,15,21,28,36,45"""

    def __init__(self):
        super().__init__("삼각수", "삼각수 1,3,6,10,15,21,28,36,45 중심 선택")
        self.triangular = [1, 3, 6, 10, 15, 21, 28, 36, 45]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 삼각수에서 3~4개 선택
        num_tri = random.randint(3, 4)
        selected = random.sample(self.triangular, num_tri)

        # 나머지는 삼각수 ±1
        tri_neighbors = []
        for t in self.triangular:
            if t > 1:
                tri_neighbors.append(t - 1)
            if t < 45:
                tri_neighbors.append(t + 1)

        tri_neighbors = [n for n in tri_neighbors if 1 <= n <= 45 and n not in selected]

        while len(selected) < 6 and tri_neighbors:
            num = random.choice(tri_neighbors)
            if num not in selected:
                selected.append(num)
                tri_neighbors.remove(num)

        # 여전히 부족하면 랜덤
        while len(selected) < 6:
            num = random.randint(1, 45)
            if num not in selected:
                selected.append(num)

        return sorted(selected[:6])


class SquareNumberStrategy(LottoStrategy):
    """사각수 전략 - 1,4,9,16,25,36"""

    def __init__(self):
        super().__init__("사각수", "완전제곱수 1,4,9,16,25,36 중심")
        self.squares = [1, 4, 9, 16, 25, 36]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 사각수에서 3~4개
        num_sq = random.randint(3, 4)
        selected = random.sample(self.squares, num_sq)

        # 나머지는 사각수 ±1, ±2
        sq_neighbors = []
        for s in self.squares:
            for delta in [-2, -1, 1, 2]:
                neighbor = s + delta
                if 1 <= neighbor <= 45:
                    sq_neighbors.append(neighbor)

        sq_neighbors = list(set([n for n in sq_neighbors if n not in selected]))

        while len(selected) < 6 and sq_neighbors:
            num = random.choice(sq_neighbors)
            if num not in selected:
                selected.append(num)
                if num in sq_neighbors:
                    sq_neighbors.remove(num)

        while len(selected) < 6:
            num = random.randint(1, 45)
            if num not in selected:
                selected.append(num)

        return sorted(selected[:6])


class PalindromeStrategy(LottoStrategy):
    """회문수 전략 - 11,22,33,44"""

    def __init__(self):
        super().__init__("회문수", "회문수 11,22,33,44 포함")
        self.palindromes = [11, 22, 33, 44]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 회문수 2~3개 선택
        num_pal = random.randint(2, 3)
        selected = random.sample(self.palindromes, num_pal)

        # 나머지는 같은 끝수 번호
        # 예: 11 -> 1, 21, 31, 41
        for pal in selected[:]:
            last_digit = pal % 10
            same_end = [n for n in range(1, 46) if n % 10 == last_digit and n not in selected]
            if same_end and len(selected) < 6:
                selected.append(random.choice(same_end))

        # 부족하면 랜덤
        while len(selected) < 6:
            num = random.randint(1, 45)
            if num not in selected:
                selected.append(num)

        return sorted(selected[:6])


class MultiplePatternStrategy(LottoStrategy):
    """배수 패턴 전략 - 특정 수의 배수들"""

    def __init__(self):
        super().__init__("배수_패턴", "3, 5, 7의 배수 조합")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 회차에 따라 다른 배수 선택
        base = [3, 5, 7][round_num % 3]

        multiples = [n for n in range(base, 46, base)]

        # 배수에서 4개 선택
        num_mult = min(4, len(multiples))
        selected = random.sample(multiples, num_mult)

        # 나머지는 배수 ±1
        neighbors = []
        for m in multiples:
            if m > 1:
                neighbors.append(m - 1)
            if m < 45:
                neighbors.append(m + 1)

        neighbors = [n for n in neighbors if 1 <= n <= 45 and n not in selected]

        while len(selected) < 6 and neighbors:
            num = random.choice(neighbors)
            if num not in selected:
                selected.append(num)
                if num in neighbors:
                    neighbors.remove(num)

        while len(selected) < 6:
            num = random.randint(1, 45)
            if num not in selected:
                selected.append(num)

        return sorted(selected[:6])


class ModularStrategy(LottoStrategy):
    """모듈러 전략 - mod 연산 기반"""

    def __init__(self):
        super().__init__("모듈러", "mod 7, mod 9 패턴 활용")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # mod 값별로 그룹화
        mod_base = [7, 9][round_num % 2]

        # 각 mod 값에서 1개씩 선택
        selected = []
        for remainder in range(min(6, mod_base)):
            candidates = [n for n in range(1, 46) if n % mod_base == remainder]
            if candidates:
                selected.append(random.choice(candidates))

        # 부족하면 랜덤 추가
        while len(selected) < 6:
            num = random.randint(1, 45)
            if num not in selected:
                selected.append(num)

        return sorted(selected[:6])


class BitPatternStrategy(LottoStrategy):
    """비트 패턴 전략 - 이진수 패턴"""

    def __init__(self):
        super().__init__("비트_패턴", "이진수에서 1의 개수가 특정 값인 번호")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 이진수에서 1의 개수가 2~4개인 번호 선호
        target_bits = random.randint(2, 4)

        candidates = []
        for n in range(1, 46):
            if bin(n).count('1') == target_bits:
                candidates.append(n)

        if len(candidates) >= 6:
            return sorted(random.sample(candidates, 6))
        else:
            # 부족하면 ±1 비트 개수도 포함
            for n in range(1, 46):
                bits = bin(n).count('1')
                if abs(bits - target_bits) == 1 and n not in candidates:
                    candidates.append(n)

            if len(candidates) >= 6:
                return sorted(random.sample(candidates, 6))
            else:
                extra = random.sample([n for n in range(1, 46) if n not in candidates], 6 - len(candidates))
                return sorted(candidates + extra)


class DigitalRootStrategy(LottoStrategy):
    """디지털 루트 전략 - 각 자리수 합의 반복"""

    def __init__(self):
        super().__init__("디지털_루트", "디지털 루트(각 자리수 합을 1자리까지 반복)가 다양하게")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        def digital_root(n):
            while n >= 10:
                n = sum(int(d) for d in str(n))
            return n

        # 각 디지털 루트(1~9)에서 번호 그룹화
        by_root = defaultdict(list)
        for n in range(1, 46):
            root = digital_root(n)
            by_root[root].append(n)

        # 6개의 서로 다른 루트에서 1개씩
        roots = random.sample(list(by_root.keys()), 6)
        selected = []
        for root in roots:
            selected.append(random.choice(by_root[root]))

        return sorted(selected[:6])


class DensityStrategy(LottoStrategy):
    """번호 밀도 전략 - 구간별 밀도 분석"""

    def __init__(self):
        super().__init__("번호_밀도", "과거 데이터 구간별 출현 밀도 기반 선택")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 20)

        if len(past) < 5:
            return sorted(random.sample(range(1, 46), 6))

        # 구간별(1-15, 16-30, 31-45) 출현 빈도
        zone_freq = defaultdict(int)
        for h in past:
            for n in h['numbers']:
                if 1 <= n <= 15:
                    zone = 0
                elif 16 <= n <= 30:
                    zone = 1
                else:
                    zone = 2
                zone_freq[zone] += 1

        # 밀도 높은 구간에서 더 많이 선택
        zones = [
            list(range(1, 16)),
            list(range(16, 31)),
            list(range(31, 46))
        ]

        # 밀도 순으로 정렬
        sorted_zones = sorted(zone_freq.items(), key=lambda x: x[1], reverse=True)

        selected = []
        picks = [3, 2, 1]  # 밀도 순으로 개수 배분

        for i, (zone_idx, _) in enumerate(sorted_zones):
            if i < 3:
                zone = zones[zone_idx]
                num_pick = min(picks[i], len(zone))
                selected.extend(random.sample(zone, num_pick))

        # 부족하면 랜덤
        while len(selected) < 6:
            num = random.randint(1, 45)
            if num not in selected:
                selected.append(num)

        return sorted(selected[:6])


class CyclicPatternStrategy(LottoStrategy):
    """반복 주기 전략 - n회 주기 반복 패턴"""

    def __init__(self):
        super().__init__("반복_주기", "7회 또는 13회 주기로 반복되는 번호 패턴")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 7회 또는 13회 전 당첨번호 참고
        cycle = [7, 13][round_num % 2]

        target_round = round_num - cycle
        past_rounds = [h for h in history if h['round'] == target_round]

        if past_rounds:
            # 해당 회차 번호 기반으로 변형
            base_nums = past_rounds[0]['numbers']
            selected = []

            for n in base_nums:
                # ±1~3 범위 내에서 변형
                delta = random.randint(-3, 3)
                new_num = n + delta
                new_num = max(1, min(45, new_num))
                if new_num not in selected:
                    selected.append(new_num)

            # 부족하면 랜덤
            while len(selected) < 6:
                num = random.randint(1, 45)
                if num not in selected:
                    selected.append(num)

            return sorted(selected[:6])
        else:
            return sorted(random.sample(range(1, 46), 6))


class SymmetricStrategy(LottoStrategy):
    """대칭 번호 전략 - 합이 46이 되는 쌍"""

    def __init__(self):
        super().__init__("대칭_번호", "합이 46이 되는 대칭 쌍 활용 (1+45, 2+44, ...)")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 대칭 쌍: (1,45), (2,44), (3,43), ... (22,24), (23,23)
        pairs = [(i, 46 - i) for i in range(1, 24)]

        # 2~3쌍 선택
        num_pairs = random.randint(2, 3)
        selected = []

        for pair in random.sample(pairs, num_pairs):
            selected.extend(pair)

        # 부족하면 중앙값(23) 근처에서
        center_nums = list(range(20, 27))
        while len(selected) < 6:
            num = random.choice(center_nums)
            if num not in selected:
                selected.append(num)

        return sorted(selected[:6])


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
        """자연현상/패턴 기반 전략 15개 초기화"""
        return [
            MoonCycleStrategy(),
            SeasonalStrategy(),
            WeekdayStrategy(),
            TwinPrimeStrategy(),
            PerfectNumberStrategy(),
            TriangularNumberStrategy(),
            SquareNumberStrategy(),
            PalindromeStrategy(),
            MultiplePatternStrategy(),
            ModularStrategy(),
            BitPatternStrategy(),
            DigitalRootStrategy(),
            DensityStrategy(),
            CyclicPatternStrategy(),
            SymmetricStrategy(),
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

    def calculate_roi(self, rank_counts: Dict, total_games: int) -> float:
        """수익률 계산 (단순화: 평균 상금 기준)"""
        # 평균 상금 (단순 추정)
        avg_prizes = {
            '1등': 2000000000,
            '2등': 50000000,
            '3등': 1500000,
            '4등': 50000,
            '5등': 5000
        }

        total_prize = 0
        for rank, count in rank_counts.items():
            if rank in avg_prizes:
                total_prize += avg_prizes[rank] * count

        total_cost = total_games * 1000  # 게임당 1000원

        if total_cost == 0:
            return 0.0

        roi = ((total_prize - total_cost) / total_cost) * 100
        return round(roi, 2)

    def run_backtest(self, start_round: int = 1, end_round: Optional[int] = None):
        """백테스팅 실행"""
        if end_round is None:
            end_round = max(h['round'] for h in self.history)

        print(f"백테스팅 시작: {start_round}회 ~ {end_round}회")
        print(f"전략 수: {len(self.strategies)}개\n")

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
                    'rank': rank
                }

        print("백테스팅 완료!\n")

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

            for r in results:
                rank_counts[r['rank']] += 1

            # 4등 이상율
            rank_4_plus = rank_counts['1등'] + rank_counts['2등'] + rank_counts['3등'] + rank_counts['4등']
            rate_4_plus = round(rank_4_plus / total * 100, 2)

            # 수익률 계산
            roi = self.calculate_roi(rank_counts, total)

            stats[name] = {
                'total': total,
                '1등': rank_counts['1등'],
                '2등': rank_counts['2등'],
                '3등': rank_counts['3등'],
                '4등': rank_counts['4등'],
                '5등': rank_counts['5등'],
                '4등+': rank_4_plus,
                '4등+율': rate_4_plus,
                '수익률': roi
            }

        return stats

    def print_summary_table(self):
        """결과를 표 형식으로 출력"""
        stats = self.get_statistics()

        print("=" * 120)
        print("자연현상/패턴 기반 전략 백테스팅 결과")
        print("=" * 120)
        print(f"{'순위':<4} {'전략명':<15} {'총회차':<8} {'1등':<6} {'2등':<6} {'3등':<6} {'4등':<6} {'5등':<6} {'4등+':<8} {'4등+율':<10} {'수익률(%)':<12}")
        print("-" * 120)

        # 4등+율 기준 정렬
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['4등+율'], reverse=True)

        for i, (name, s) in enumerate(sorted_stats, 1):
            print(f"{i:<4} {name:<15} {s['total']:<8} {s['1등']:<6} {s['2등']:<6} {s['3등']:<6} {s['4등']:<6} {s['5등']:<6} {s['4등+']:<8} {s['4등+율']:<10.2f}% {s['수익률']:<12.2f}")

        print("=" * 120)


# ============================================================
# 메인 실행
# ============================================================

def main():
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'lotto_data.json')

    # 엔진 초기화 및 실행
    engine = BacktestEngine(data_path)
    engine.run_backtest(start_round=1)
    engine.print_summary_table()


if __name__ == '__main__':
    main()
