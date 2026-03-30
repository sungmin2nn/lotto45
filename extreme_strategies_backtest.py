#!/usr/bin/env python3
"""
로또 극단적/역발상 전략 백테스팅
- 15개의 극단적 전략 구현
- 백테스팅 및 결과 표 생성
"""

import json
import random
import math
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional


class LottoStrategy:
    """번호 생성 전략 기본 클래스"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        """번호 6개 생성 (하위 클래스에서 구현)"""
        raise NotImplementedError

    def get_past_data(self, round_num: int, history: List[Dict], n: int = 10) -> List[Dict]:
        """해당 회차 이전 n개 회차 데이터 반환"""
        past = [h for h in history if h['round'] < round_num]
        return sorted(past, key=lambda x: x['round'], reverse=True)[:n]


# ============================================================
# 극단적/역발상 전략 15개
# ============================================================

class WorstAvoidStrategy(LottoStrategy):
    """1. 최악_회피: 역대 최악 패턴 피하기"""

    def __init__(self):
        super().__init__("최악_회피", "역대 가장 낮은 매칭률 패턴 피하기")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 100)
        if len(past) < 10:
            return sorted(random.sample(range(1, 46), 6))

        # 패턴별 평균 매칭 계산 (홀짝비, 고저비)
        # 최악 패턴: 홀수만, 작은 번호만 회피
        # 대신 균형잡힌 조합 생성
        odds = random.sample([n for n in range(1, 46) if n % 2 == 1], 3)
        evens = random.sample([n for n in range(1, 46) if n % 2 == 0], 3)
        return sorted(odds + evens)


class PopularOppositeStrategy(LottoStrategy):
    """2. 인기_반대: 가장 인기 있는 조합의 반대"""

    def __init__(self):
        super().__init__("인기_반대", "최빈출 번호 제외, 저빈출 번호 선택")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 50)
        if len(past) < 10:
            return sorted(random.sample(range(1, 46), 6))

        # 빈도 계산
        freq = defaultdict(int)
        for h in past:
            for n in h['numbers']:
                freq[n] += 1

        # 빈도 하위 20개 중 6개 선택
        sorted_nums = sorted(range(1, 46), key=lambda x: freq.get(x, 0))[:20]
        return sorted(random.sample(sorted_nums, 6))


class ConsecutiveMaxStrategy(LottoStrategy):
    """3. 연속_극대화: 3~4개 연속번호 포함"""

    def __init__(self):
        super().__init__("연속_극대화", "연속번호 3~4개 포함")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 연속 3개 또는 4개
        consecutive_count = random.choice([3, 4])
        start = random.randint(1, 45 - consecutive_count + 1)
        consecutive = list(range(start, start + consecutive_count))

        # 나머지 번호
        pool = [n for n in range(1, 46) if n not in consecutive]
        rest = random.sample(pool, 6 - consecutive_count)

        return sorted(consecutive + rest)


class ExtremeHighLowStrategy(LottoStrategy):
    """4. 극단_고저: 1-10 + 40-45만"""

    def __init__(self):
        super().__init__("극단_고저", "최저(1-10) + 최고(40-45) 번호만")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        low = list(range(1, 11))    # 1-10
        high = list(range(40, 46))  # 40-45

        # 각각에서 3개씩 선택
        selected = random.sample(low, 3) + random.sample(high, 3)
        return sorted(selected)


class OneSidedBiasStrategy(LottoStrategy):
    """5. 한쪽_쏠림: 홀수만 또는 짝수만 5:1"""

    def __init__(self):
        super().__init__("한쪽_쏠림", "홀수 5개 + 짝수 1개 또는 반대")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        odds = [n for n in range(1, 46) if n % 2 == 1]
        evens = [n for n in range(1, 46) if n % 2 == 0]

        if random.random() < 0.5:
            # 홀수 5개 + 짝수 1개
            selected = random.sample(odds, 5) + random.sample(evens, 1)
        else:
            # 짝수 5개 + 홀수 1개
            selected = random.sample(evens, 5) + random.sample(odds, 1)

        return sorted(selected)


class SameEndDigitStrategy(LottoStrategy):
    """6. 끝수_동일: 같은 끝수 3개 이상"""

    def __init__(self):
        super().__init__("끝수_동일", "같은 끝수 3개 이상 포함")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 끝수 선택
        end_digit = random.randint(0, 9)

        # 해당 끝수 번호들
        same_end = [n for n in range(1, 46) if n % 10 == end_digit]

        if len(same_end) >= 3:
            selected = random.sample(same_end, 3)
        else:
            selected = same_end.copy()

        # 나머지 번호
        pool = [n for n in range(1, 46) if n not in selected]
        rest = random.sample(pool, 6 - len(selected))

        return sorted(selected + rest)


class Tens10ConcentrateStrategy(LottoStrategy):
    """7. 10단위_집중: 10-19 구간 집중"""

    def __init__(self):
        super().__init__("10단위_집중", "10-19 구간에서 4개 + 나머지 2개")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        zone = list(range(10, 20))  # 10-19
        selected = random.sample(zone, 4)

        # 나머지 구간에서 2개
        pool = [n for n in range(1, 46) if n not in zone]
        rest = random.sample(pool, 2)

        return sorted(selected + rest)


class Tens20ConcentrateStrategy(LottoStrategy):
    """8. 20단위_집중: 20-29 구간 집중"""

    def __init__(self):
        super().__init__("20단위_집중", "20-29 구간에서 4개 + 나머지 2개")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        zone = list(range(20, 30))  # 20-29
        selected = random.sample(zone, 4)

        # 나머지 구간에서 2개
        pool = [n for n in range(1, 46) if n not in zone]
        rest = random.sample(pool, 2)

        return sorted(selected + rest)


class OnesDigitConsecutiveStrategy(LottoStrategy):
    """9. 1의자리_연속: 1,11,21,31,41 + 1개"""

    def __init__(self):
        super().__init__("1의자리_연속", "1의 자리가 같은 번호 5개 + 1개")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 1의 자리 선택
        ones_digit = random.randint(1, 5)

        # 해당 자리 번호들 (1,11,21,31,41 등)
        same_ones = [n for n in range(ones_digit, 46, 10)]

        if len(same_ones) >= 5:
            selected = random.sample(same_ones, 5)
        else:
            selected = same_ones.copy()

        # 나머지 1개
        pool = [n for n in range(1, 46) if n not in selected]
        rest = random.sample(pool, min(1, len(pool)))

        result = selected + rest
        while len(result) < 6:
            n = random.randint(1, 45)
            if n not in result:
                result.append(n)

        return sorted(result[:6])


class ZoneSkipStrategy(LottoStrategy):
    """10. 구간_스킵: 10-19 완전 제외"""

    def __init__(self):
        super().__init__("구간_스킵", "10-19 구간 완전 제외")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 10-19 제외
        pool = [n for n in range(1, 46) if not (10 <= n <= 19)]
        return sorted(random.sample(pool, 6))


class BonusTrackingStrategy(LottoStrategy):
    """11. 보너스_추적: 보너스 번호 패턴 추적"""

    def __init__(self):
        super().__init__("보너스_추적", "최근 보너스 번호 패턴 기반")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 20)
        if len(past) < 5:
            return sorted(random.sample(range(1, 46), 6))

        # 보너스 번호 수집
        bonus_nums = [h.get('bonus', 0) for h in past if h.get('bonus')]

        if not bonus_nums:
            return sorted(random.sample(range(1, 46), 6))

        # 보너스 번호 근처 번호들 선택
        candidates = set()
        for b in bonus_nums[-10:]:  # 최근 10개
            for offset in [-2, -1, 0, 1, 2]:
                n = b + offset
                if 1 <= n <= 45:
                    candidates.add(n)

        candidates = list(candidates)
        if len(candidates) >= 6:
            return sorted(random.sample(candidates, 6))

        # 부족하면 랜덤 추가
        while len(candidates) < 6:
            n = random.randint(1, 45)
            if n not in candidates:
                candidates.append(n)

        return sorted(candidates[:6])


class NeverWonPatternStrategy(LottoStrategy):
    """12. 낙첨_패턴: 절대 안나온 조합 유형"""

    def __init__(self):
        super().__init__("낙첨_패턴", "역대 한번도 안나온 극단 패턴")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 극단적 패턴: 모두 10 이하
        pool = list(range(1, 11))
        return sorted(random.sample(pool, 6))


class SumExtremeStrategy(LottoStrategy):
    """13. 합계_극단: 합 80이하 또는 190이상"""

    def __init__(self):
        super().__init__("합계_극단", "번호 합이 80 이하 또는 190 이상")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        if random.random() < 0.5:
            # 합 80 이하 목표
            for _ in range(100):
                nums = sorted(random.sample(range(1, 25), 6))
                if sum(nums) <= 80:
                    return nums
            # 실패시 작은 번호들
            return sorted(random.sample(range(1, 20), 6))
        else:
            # 합 190 이상 목표
            for _ in range(100):
                nums = sorted(random.sample(range(20, 46), 6))
                if sum(nums) >= 190:
                    return nums
            # 실패시 큰 번호들
            return sorted(random.sample(range(30, 46), 6))


class StdDevMaxStrategy(LottoStrategy):
    """14. 표준편차_극대: 번호 편차 최대화"""

    def __init__(self):
        super().__init__("표준편차_극대", "번호 간격 최대화 (분산 극대)")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 간격을 최대화하는 조합
        # 예: 1, 10, 20, 30, 40, 45
        selected = [1, 10, 20, 30, 40, 45]

        # 약간의 변형
        result = []
        for num in selected:
            variation = random.randint(-2, 2)
            new_num = max(1, min(45, num + variation))
            result.append(new_num)

        # 중복 제거
        result = list(set(result))
        while len(result) < 6:
            n = random.randint(1, 45)
            if n not in result:
                result.append(n)

        return sorted(result[:6])


class FixedNumbersStrategy(LottoStrategy):
    """15. 완전_고정: 특정 번호 3개 항상 포함"""

    def __init__(self):
        super().__init__("완전_고정", "특정 번호 3개 고정 (7, 17, 27) + 랜덤 3개")
        self.fixed = [7, 17, 27]  # 행운의 번호

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 나머지 3개 랜덤 선택
        pool = [n for n in range(1, 46) if n not in self.fixed]
        rest = random.sample(pool, 3)

        return sorted(self.fixed + rest)


# ============================================================
# 백테스팅 엔진
# ============================================================

class BacktestEngine:
    """백테스팅 엔진"""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.history = self.load_data()
        self.strategies = self.init_strategies()
        self.results = {}  # {round: {strategy_name: {numbers, match, rank}}}

    def load_data(self) -> List[Dict]:
        """로또 데이터 로드"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x['round'])

    def init_strategies(self) -> List[LottoStrategy]:
        """극단적 전략들 초기화"""
        return [
            WorstAvoidStrategy(),
            PopularOppositeStrategy(),
            ConsecutiveMaxStrategy(),
            ExtremeHighLowStrategy(),
            OneSidedBiasStrategy(),
            SameEndDigitStrategy(),
            Tens10ConcentrateStrategy(),
            Tens20ConcentrateStrategy(),
            OnesDigitConsecutiveStrategy(),
            ZoneSkipStrategy(),
            BonusTrackingStrategy(),
            NeverWonPatternStrategy(),
            SumExtremeStrategy(),
            StdDevMaxStrategy(),
            FixedNumbersStrategy(),
        ]

    def check_match(self, prediction: List[int], actual: List[int], bonus: int) -> Tuple[int, str]:
        """당첨 확인 (일치 개수, 등수)"""
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

        print(f"백테스팅 시작: {start_round}회 ~ {end_round}회")
        print(f"전략 수: {len(self.strategies)}개")
        print("-" * 80)

        for h in self.history:
            round_num = h['round']
            if round_num < start_round or round_num > end_round:
                continue

            actual = h['numbers']
            bonus = h.get('bonus', 0)

            self.results[round_num] = {}

            for strategy in self.strategies:
                # 번호 생성 (해당 회차 이전 데이터만 사용)
                prediction = strategy.generate(round_num, self.history)
                match_count, rank = self.check_match(prediction, actual, bonus)

                self.results[round_num][strategy.name] = {
                    'numbers': prediction,
                    'match': match_count,
                    'rank': rank,
                    'actual': actual,
                    'bonus': bonus
                }

            if round_num % 100 == 0:
                print(f"  {round_num}회 완료")

        print("-" * 80)
        print("백테스팅 완료!")

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

            # 수익률 계산 (1게임당 1000원 가정)
            cost = total * 1000  # 총 구매 비용
            revenue = 0
            revenue += rank_counts['1등'] * 2000000000  # 1등 평균 20억
            revenue += rank_counts['2등'] * 50000000     # 2등 평균 5천만
            revenue += rank_counts['3등'] * 1500000      # 3등 평균 150만
            revenue += rank_counts['4등'] * 50000        # 4등 평균 5만
            revenue += rank_counts['5등'] * 5000         # 5등 고정 5천

            profit_rate = ((revenue - cost) / cost * 100) if cost > 0 else 0

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
                '수익률': round(profit_rate, 2),
            }

        return stats

    def print_table(self):
        """결과 표 출력"""
        stats = self.get_statistics()

        print("\n" + "=" * 120)
        print("극단적/역발상 전략 백테스팅 결과")
        print("=" * 120)
        print(f"\n{'No':<4} {'전략명':<20} {'총회차':<8} {'1등':<6} {'2등':<6} {'3등':<6} {'4등':<6} {'5등':<6} {'4등+':<6} {'4등+율':<10} {'수익률':<10}")
        print("-" * 120)

        # 4등+ 율 기준 정렬
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['4등+율'], reverse=True)

        for i, (name, s) in enumerate(sorted_stats, 1):
            print(f"{i:<4} {name:<20} {s['total']:<8} {s['1등']:<6} {s['2등']:<6} {s['3등']:<6} {s['4등']:<6} {s['5등']:<6} {s['4등+']:<6} {s['4등+율']:<9.2f}% {s['수익률']:<9.2f}%")

        print("=" * 120)

        # 통계 요약
        print(f"\n[통계 요약]")
        print(f"- 평균 4등+율: {sum(s['4등+율'] for s in stats.values()) / len(stats):.2f}%")
        print(f"- 최고 4등+율: {max(s['4등+율'] for s in stats.values()):.2f}%")
        print(f"- 최저 4등+율: {min(s['4등+율'] for s in stats.values()):.2f}%")
        print(f"- 평균 수익률: {sum(s['수익률'] for s in stats.values()) / len(stats):.2f}%")


# ============================================================
# 메인 실행
# ============================================================

def main():
    import os

    # 데이터 경로
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'lotto_data.json')

    # 엔진 초기화 및 실행
    engine = BacktestEngine(data_path)
    engine.run_backtest(start_round=1)
    engine.print_table()


if __name__ == '__main__':
    main()
