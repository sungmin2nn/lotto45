#!/usr/bin/env python3
"""
로또 창의적 전략 백테스팅 (새로운 30개 전략)
- 암호학, 언어학, 게임이론, 생물학, 물리상수, 기하학 등 기반
"""

import json
import random
import math
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


class LottoStrategy:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.active = True

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        raise NotImplementedError

    def get_past_data(self, round_num: int, history: List[Dict], n: int = 10) -> List[Dict]:
        past = [h for h in history if h['round'] < round_num]
        return sorted(past, key=lambda x: x['round'], reverse=True)[:n]

    def get_date_from_round(self, round_num: int) -> datetime:
        start_date = datetime(2002, 12, 7)
        return start_date + timedelta(weeks=round_num - 1)


# ============================================================
# 암호학/해시 기반 전략
# ============================================================

class SHA256Strategy(LottoStrategy):
    """SHA256 해시 기반"""
    def __init__(self):
        super().__init__("SHA256_해시", "회차번호 SHA256 해시의 16진수 → 번호 변환")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        hash_input = f"lotto_round_{round_num}".encode()
        hash_hex = hashlib.sha256(hash_input).hexdigest()

        selected = set()
        for i in range(0, len(hash_hex), 2):
            if len(selected) >= 6:
                break
            hex_val = int(hash_hex[i:i+2], 16)
            num = (hex_val % 45) + 1
            selected.add(num)

        while len(selected) < 6:
            selected.add(random.randint(1, 45))

        return sorted(list(selected))[:6]


class MD5Strategy(LottoStrategy):
    """MD5 해시 기반"""
    def __init__(self):
        super().__init__("MD5_해시", "회차+날짜 MD5 해시 기반")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)
        hash_input = f"{round_num}_{date.strftime('%Y%m%d')}".encode()
        hash_hex = hashlib.md5(hash_input).hexdigest()

        selected = set()
        for i in range(0, min(32, len(hash_hex)), 2):
            if len(selected) >= 6:
                break
            hex_val = int(hash_hex[i:i+2], 16)
            num = (hex_val % 45) + 1
            selected.add(num)

        while len(selected) < 6:
            selected.add(random.randint(1, 45))

        return sorted(list(selected))[:6]


# ============================================================
# 언어학/한글 기반 전략
# ============================================================

class KoreanChoSungStrategy(LottoStrategy):
    """한글 초성 기반 (ㄱ=1, ㄴ=2, ...)"""
    def __init__(self):
        super().__init__("한글_초성", "회차를 한글 초성으로 변환 (ㄱ=1, ㄴ=2...)")
        # 초성 14개: ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ
        self.cho_map = {i+1: i+1 for i in range(14)}

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 회차를 14진법으로 변환
        digits = []
        n = round_num
        while n > 0:
            digits.append((n % 14) + 1)
            n //= 14

        selected = set()
        for d in digits:
            selected.add(d)
            selected.add((d * 3) % 45 + 1)  # 배수 추가

        # 14의 배수들
        for i in range(1, 4):
            selected.add(14 * i if 14 * i <= 45 else 14 * i - 45)

        while len(selected) < 6:
            selected.add(random.randint(1, 45))

        return sorted(list(selected))[:6]


class NumberPronunciationStrategy(LottoStrategy):
    """숫자 발음 기반"""
    def __init__(self):
        super().__init__("숫자_발음", "숫자 발음 글자수 기반 (1=일=1글자, 11=십일=2글자)")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 글자수별 그룹
        one_char = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # 일, 이, 삼...
        two_char = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # 십, 십일...
        three_char = list(range(20, 46))  # 이십, 이십일...

        # 회차에 따라 조합
        pattern = round_num % 4
        if pattern == 0:
            selected = random.sample(one_char, 2) + random.sample(two_char, 2) + random.sample(three_char, 2)
        elif pattern == 1:
            selected = random.sample(one_char, 3) + random.sample(three_char, 3)
        elif pattern == 2:
            selected = random.sample(two_char, 3) + random.sample(three_char, 3)
        else:
            selected = random.sample(one_char, 1) + random.sample(two_char, 2) + random.sample(three_char, 3)

        return sorted(selected[:6])


# ============================================================
# 게임이론 기반 전략
# ============================================================

class NashEquilibriumStrategy(LottoStrategy):
    """내쉬 균형 - 다른 사람이 안 고를 것 같은 번호"""
    def __init__(self):
        super().__init__("내쉬_균형", "대중이 선호하는 번호 회피 (7,8,13,18,21 등 회피)")
        # 대중이 선호하는 번호들
        self.popular = {7, 8, 13, 18, 21, 27, 33, 37, 43}

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 인기 번호 회피
        unpopular = [n for n in range(1, 46) if n not in self.popular]
        return sorted(random.sample(unpopular, 6))


class MinimaxStrategy(LottoStrategy):
    """미니맥스 - 최악의 경우 최소화"""
    def __init__(self):
        super().__init__("미니맥스", "최악의 결과를 최소화하는 균형 조합")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 각 구간에서 균등하게 선택 (위험 분산)
        zones = [
            list(range(1, 10)),
            list(range(10, 19)),
            list(range(19, 28)),
            list(range(28, 37)),
            list(range(37, 46))
        ]

        selected = []
        for zone in zones:
            selected.append(random.choice(zone))

        # 6번째는 가장 적게 뽑힌 구간에서
        remaining = [n for n in range(1, 46) if n not in selected]
        selected.append(random.choice(remaining))

        return sorted(selected[:6])


# ============================================================
# 물리 상수 기반 전략
# ============================================================

class PiConstantStrategy(LottoStrategy):
    """원주율 π 기반"""
    def __init__(self):
        super().__init__("원주율_파이", "π의 소수점 자릿수 활용")
        # π = 3.14159265358979...
        self.pi_digits = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        offset = round_num % len(self.pi_digits)
        selected = set()

        for i in range(10):
            idx = (offset + i) % len(self.pi_digits)
            num = self.pi_digits[idx]
            if i < 5:
                num = num + (i * 10)  # 10대, 20대 등으로 확장
            if 1 <= num <= 45:
                selected.add(num)

        while len(selected) < 6:
            selected.add(random.randint(1, 45))

        return sorted(list(selected))[:6]


class EulerConstantStrategy(LottoStrategy):
    """자연로그 e 기반"""
    def __init__(self):
        super().__init__("자연로그_e", "e=2.71828의 자릿수 활용")
        # e = 2.71828182845904...
        self.e_digits = [2, 7, 1, 8, 2, 8, 1, 8, 2, 8, 4, 5, 9, 0, 4, 5, 2, 3, 5, 3]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        offset = round_num % len(self.e_digits)
        selected = set()

        for i in range(15):
            idx = (offset + i) % len(self.e_digits)
            num = self.e_digits[idx]
            if num == 0:
                num = 10  # 0을 10으로
            # 다양한 변환
            selected.add(num)
            selected.add((num + 10) if num + 10 <= 45 else num)
            selected.add((num + 20) if num + 20 <= 45 else num)

        result = list(selected)
        if len(result) >= 6:
            return sorted(random.sample(result, 6))

        while len(result) < 6:
            result.append(random.randint(1, 45))
        return sorted(result[:6])


class GoldenRatioStrategy(LottoStrategy):
    """황금비 φ 기반"""
    def __init__(self):
        super().__init__("황금비_phi", "φ=1.618 기반 간격 선택")
        self.phi = (1 + math.sqrt(5)) / 2  # 1.618...

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 황금비 간격으로 번호 선택
        start = (round_num % 10) + 1
        selected = set()

        current = start
        for i in range(6):
            selected.add(int(current) if int(current) <= 45 else int(current) % 45 + 1)
            current = current * self.phi
            if current > 45:
                current = current % 45 + 1

        while len(selected) < 6:
            selected.add(random.randint(1, 45))

        return sorted(list(selected))[:6]


# ============================================================
# 기하학 기반 전략
# ============================================================

class HexagonStrategy(LottoStrategy):
    """육각형 패턴"""
    def __init__(self):
        super().__init__("육각형_패턴", "6각형 꼭짓점 + 중심 패턴")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 중심점
        center = 23  # 1~45의 중앙

        # 6각형 꼭짓점 (60도 간격)
        vertices = []
        radius = 10 + (round_num % 5)  # 10~14
        for i in range(6):
            angle = i * 60 + (round_num % 60)
            num = int(center + radius * math.cos(math.radians(angle)))
            num = max(1, min(45, num))
            vertices.append(num)

        selected = list(set(vertices))
        while len(selected) < 6:
            selected.append(random.randint(1, 45))

        return sorted(selected[:6])


class SpiralStrategy(LottoStrategy):
    """나선형 패턴"""
    def __init__(self):
        super().__init__("나선형_패턴", "아르키메데스 나선 기반")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        selected = set()
        a = 1 + (round_num % 3)  # 나선 시작점
        b = 2 + (round_num % 3)  # 나선 간격

        theta = 0
        while len(selected) < 6:
            r = a + b * theta
            num = int(r) % 45 + 1
            selected.add(num)
            theta += 0.5
            if theta > 10:
                break

        while len(selected) < 6:
            selected.add(random.randint(1, 45))

        return sorted(list(selected))[:6]


# ============================================================
# 생물학/진화 기반 전략
# ============================================================

class DNAPatternStrategy(LottoStrategy):
    """DNA 염기서열 패턴"""
    def __init__(self):
        super().__init__("DNA_패턴", "ACGT 염기를 번호로 매핑")
        # A=1-11, C=12-22, G=23-33, T=34-45
        self.bases = {
            'A': list(range(1, 12)),
            'C': list(range(12, 23)),
            'G': list(range(23, 34)),
            'T': list(range(34, 46))
        }

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 회차를 DNA 코돈으로 변환
        patterns = ['AACGT', 'ACGTA', 'CGTAA', 'GTAAC', 'TAACG']
        pattern = patterns[round_num % len(patterns)]

        selected = []
        for base in pattern[:6]:
            pool = self.bases.get(base, list(range(1, 46)))
            num = random.choice([n for n in pool if n not in selected])
            selected.append(num)

        while len(selected) < 6:
            selected.append(random.randint(1, 45))

        return sorted(selected[:6])


class EvolutionStrategy(LottoStrategy):
    """진화 알고리즘 - 최근 당첨번호 변이"""
    def __init__(self):
        super().__init__("진화_알고리즘", "최근 당첨번호에 작은 변이 적용")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 3)
        if len(past) < 1:
            return sorted(random.sample(range(1, 46), 6))

        # 최근 번호를 부모로
        parent = past[0]['numbers'].copy()

        # 변이 적용
        child = []
        for num in parent:
            mutation = random.choice([-2, -1, 0, 1, 2])
            new_num = num + mutation
            new_num = max(1, min(45, new_num))
            child.append(new_num)

        # 중복 제거
        child = list(set(child))
        while len(child) < 6:
            child.append(random.randint(1, 45))

        return sorted(child[:6])


# ============================================================
# 음악/리듬 기반 전략
# ============================================================

class MusicalScaleStrategy(LottoStrategy):
    """음계 기반 (도레미파솔라시 = 7음계)"""
    def __init__(self):
        super().__init__("음계_패턴", "7음계를 45개 번호로 매핑")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 7음계 (도=1, 레=2, ...) → 45까지 반복
        scale = [1, 3, 5, 6, 8, 10, 12]  # 반음 포함 간격

        selected = set()
        key = round_num % 7  # 조(Key) 변경

        for note in scale:
            num = (note + key * 6) % 45 + 1
            selected.add(num)

        while len(selected) < 6:
            selected.add(random.randint(1, 45))

        return sorted(list(selected))[:6]


class RhythmStrategy(LottoStrategy):
    """리듬 패턴 (4/4박자 등)"""
    def __init__(self):
        super().__init__("리듬_패턴", "4/4박자 강약 패턴")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 4/4 박자: 강-약-중강-약
        # 강=높은번호, 약=낮은번호
        strong = list(range(30, 46))  # 강
        medium = list(range(15, 30))  # 중
        weak = list(range(1, 15))     # 약

        pattern = round_num % 3
        if pattern == 0:
            selected = random.sample(strong, 2) + random.sample(medium, 2) + random.sample(weak, 2)
        elif pattern == 1:
            selected = random.sample(strong, 3) + random.sample(weak, 3)
        else:
            selected = random.sample(medium, 4) + random.sample(strong, 1) + random.sample(weak, 1)

        return sorted(selected[:6])


# ============================================================
# 역사/기념일 기반 전략
# ============================================================

class HistoricalDateStrategy(LottoStrategy):
    """역사적 날짜 기반"""
    def __init__(self):
        super().__init__("역사적_날짜", "유명한 날짜들을 번호로 (8.15, 6.25 등)")
        # 월+일을 번호로
        self.dates = [
            (8, 15),  # 광복절
            (6, 25),  # 한국전쟁
            (3, 1),   # 삼일절
            (10, 9),  # 한글날
            (5, 18),  # 5.18
            (4, 19),  # 4.19
            (12, 25), # 크리스마스
            (1, 1),   # 새해
        ]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        selected = set()

        for month, day in self.dates:
            selected.add(month)
            selected.add(day)
            combined = (month + day) % 45 + 1
            selected.add(combined)

        result = list(selected)
        if len(result) >= 6:
            return sorted(random.sample(result, 6))

        while len(result) < 6:
            result.append(random.randint(1, 45))
        return sorted(result[:6])


# ============================================================
# 색채학 기반 전략
# ============================================================

class ColorCodeStrategy(LottoStrategy):
    """색상 코드 기반"""
    def __init__(self):
        super().__init__("색상_코드", "로또볼 색상 기반 균형 선택")
        # 로또 공 색상: 1-10노랑, 11-20파랑, 21-30빨강, 31-40회색, 41-45초록
        self.colors = {
            'yellow': list(range(1, 11)),
            'blue': list(range(11, 21)),
            'red': list(range(21, 31)),
            'gray': list(range(31, 41)),
            'green': list(range(41, 46))
        }

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 색상별 균등 선택
        selected = []
        for color, nums in self.colors.items():
            count = 2 if color in ['yellow', 'blue'] else 1
            selected.extend(random.sample(nums, min(count, len(nums))))

        while len(selected) < 6:
            selected.append(random.randint(1, 45))

        return sorted(selected[:6])


# ============================================================
# 확률/통계 심화 전략
# ============================================================

class BinomialStrategy(LottoStrategy):
    """이항분포 기반"""
    def __init__(self):
        super().__init__("이항분포", "이항분포 확률 기반 번호 선택")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 50)
        if len(past) < 10:
            return sorted(random.sample(range(1, 46), 6))

        # 각 번호 출현율
        freq = defaultdict(int)
        for h in past:
            for n in h['numbers']:
                freq[n] += 1

        total = len(past) * 6
        probabilities = {}
        for n in range(1, 46):
            p = freq[n] / total
            # 이항분포: 출현율이 평균에 가까운 번호 선호
            avg_p = 6 / 45
            distance = abs(p - avg_p)
            probabilities[n] = 1 / (distance + 0.01)

        # 확률 가중 샘플링
        nums = list(probabilities.keys())
        weights = list(probabilities.values())

        selected = []
        while len(selected) < 6:
            num = random.choices(nums, weights=weights, k=1)[0]
            if num not in selected:
                selected.append(num)

        return sorted(selected)


class ZipfLawStrategy(LottoStrategy):
    """지프의 법칙 기반"""
    def __init__(self):
        super().__init__("지프_법칙", "지프 분포 기반 역순위 가중치")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 30)
        if len(past) < 10:
            return sorted(random.sample(range(1, 46), 6))

        # 빈도 순위
        freq = defaultdict(int)
        for h in past:
            for n in h['numbers']:
                freq[n] += 1

        sorted_nums = sorted(range(1, 46), key=lambda x: freq[x], reverse=True)

        # 지프 법칙: 순위의 역수에 비례하는 확률
        weights = [1 / (i + 1) for i in range(45)]

        selected = []
        available = sorted_nums.copy()
        available_weights = weights.copy()

        while len(selected) < 6:
            num = random.choices(available, weights=available_weights, k=1)[0]
            selected.append(num)
            idx = available.index(num)
            available.pop(idx)
            available_weights.pop(idx)

        return sorted(selected)


# ============================================================
# 시간 기반 전략
# ============================================================

class CircadianStrategy(LottoStrategy):
    """생체리듬 기반"""
    def __init__(self):
        super().__init__("생체_리듬", "24시간 생체리듬 기반 (추첨시간 20:45)")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 추첨시간 20:45 기준
        hour = 20
        minute = 45

        selected = set()
        selected.add(hour)  # 20
        selected.add(minute)  # 45
        selected.add(hour + minute % 45)  # 합
        selected.add(abs(hour - minute) % 45 + 1)  # 차

        # 24시간 주기 번호
        for h in range(0, 24, 4):
            num = (h + round_num) % 45 + 1
            selected.add(num)

        result = list(selected)
        if len(result) >= 6:
            return sorted(random.sample(result, 6))

        while len(result) < 6:
            result.append(random.randint(1, 45))
        return sorted(result[:6])


class WeekPatternStrategy(LottoStrategy):
    """요일 + 주차 패턴"""
    def __init__(self):
        super().__init__("주간_패턴", "요일(토요일)+주차 기반")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)

        weekday = date.weekday()  # 0=월~6=일
        week_of_year = date.isocalendar()[1]  # 연중 주차
        day_of_month = date.day
        month = date.month

        selected = set()
        selected.add(weekday + 1)
        selected.add(week_of_year % 45 + 1)
        selected.add(day_of_month)
        selected.add(month)
        selected.add((weekday + week_of_year) % 45 + 1)
        selected.add((day_of_month + month) % 45 + 1)

        result = list(selected)
        while len(result) < 6:
            result.append(random.randint(1, 45))

        return sorted(result[:6])


# ============================================================
# 특수 수학 기반 전략
# ============================================================

class CatalanNumberStrategy(LottoStrategy):
    """카탈란 수 기반"""
    def __init__(self):
        super().__init__("카탈란_수", "카탈란 수열 활용 (1,1,2,5,14,42)")
        self.catalan = [1, 1, 2, 5, 14, 42]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        selected = set()

        for c in self.catalan:
            if 1 <= c <= 45:
                selected.add(c)
            # 배수/조합
            num = (c + round_num) % 45 + 1
            selected.add(num)

        result = list(selected)
        if len(result) >= 6:
            return sorted(random.sample(result, 6))

        while len(result) < 6:
            result.append(random.randint(1, 45))
        return sorted(result[:6])


class LucasNumberStrategy(LottoStrategy):
    """뤼카 수 기반"""
    def __init__(self):
        super().__init__("뤼카_수", "뤼카 수열 (2,1,3,4,7,11,18,29)")
        self.lucas = [2, 1, 3, 4, 7, 11, 18, 29]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        selected = set()

        for l in self.lucas:
            if 1 <= l <= 45:
                selected.add(l)

        # 뤼카 수 조합
        for i in range(len(self.lucas) - 1):
            num = (self.lucas[i] + self.lucas[i+1]) % 45 + 1
            selected.add(num)

        result = list(selected)
        if len(result) >= 6:
            return sorted(random.sample(result, 6))

        while len(result) < 6:
            result.append(random.randint(1, 45))
        return sorted(result[:6])


class PellNumberStrategy(LottoStrategy):
    """펠 수 기반"""
    def __init__(self):
        super().__init__("펠_수", "펠 수열 (0,1,2,5,12,29)")
        self.pell = [1, 2, 5, 12, 29]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        selected = set()

        for p in self.pell:
            if 1 <= p <= 45:
                selected.add(p)
            # 변형
            selected.add((p + 10) if p + 10 <= 45 else p)
            selected.add((p + 20) if p + 20 <= 45 else p)

        result = list(selected)
        if len(result) >= 6:
            return sorted(random.sample(result, 6))

        while len(result) < 6:
            result.append(random.randint(1, 45))
        return sorted(result[:6])


# ============================================================
# 조합론 기반 전략
# ============================================================

class DerangementStrategy(LottoStrategy):
    """완전순열(교란) 기반"""
    def __init__(self):
        super().__init__("완전순열", "자기 자리에 없는 번호 패턴")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        past = self.get_past_data(round_num, history, 1)
        if len(past) < 1:
            return sorted(random.sample(range(1, 46), 6))

        # 직전 당첨번호의 위치 기억
        last_nums = past[0]['numbers']

        # 각 위치에서 다른 번호 선택 (완전순열)
        selected = []
        for i, num in enumerate(last_nums):
            # 해당 구간의 다른 번호
            zone_start = (i * 8) + 1
            zone_end = min(zone_start + 7, 45)
            zone = [n for n in range(zone_start, zone_end + 1) if n != num and n not in selected]

            if zone:
                selected.append(random.choice(zone))
            else:
                candidates = [n for n in range(1, 46) if n not in selected and n != num]
                if candidates:
                    selected.append(random.choice(candidates))

        while len(selected) < 6:
            candidates = [n for n in range(1, 46) if n not in selected]
            selected.append(random.choice(candidates))

        return sorted(selected[:6])


class PartitionStrategy(LottoStrategy):
    """분할수 기반"""
    def __init__(self):
        super().__init__("분할수", "합이 특정 값이 되는 분할 패턴")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 목표 합: 138 (평균)
        target_sum = 138 + (round_num % 20 - 10)  # 128~148

        for _ in range(200):
            nums = sorted(random.sample(range(1, 46), 6))
            if abs(sum(nums) - target_sum) <= 5:
                return nums

        return sorted(random.sample(range(1, 46), 6))


# ============================================================
# 백테스팅 엔진
# ============================================================

class BacktestEngine:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.history = self.load_data()
        self.strategies = self.init_strategies()
        self.results = {}

    def load_data(self) -> List[Dict]:
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return sorted(json.load(f), key=lambda x: x['round'])

    def init_strategies(self) -> List[LottoStrategy]:
        return [
            SHA256Strategy(),
            MD5Strategy(),
            KoreanChoSungStrategy(),
            NumberPronunciationStrategy(),
            NashEquilibriumStrategy(),
            MinimaxStrategy(),
            PiConstantStrategy(),
            EulerConstantStrategy(),
            GoldenRatioStrategy(),
            HexagonStrategy(),
            SpiralStrategy(),
            DNAPatternStrategy(),
            EvolutionStrategy(),
            MusicalScaleStrategy(),
            RhythmStrategy(),
            HistoricalDateStrategy(),
            ColorCodeStrategy(),
            BinomialStrategy(),
            ZipfLawStrategy(),
            CircadianStrategy(),
            WeekPatternStrategy(),
            CatalanNumberStrategy(),
            LucasNumberStrategy(),
            PellNumberStrategy(),
            DerangementStrategy(),
            PartitionStrategy(),
        ]

    def check_match(self, prediction: List[int], actual: List[int], bonus: int) -> Tuple[int, str]:
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
        if end_round is None:
            end_round = max(h['round'] for h in self.history)

        print(f"\n{'='*80}")
        print(f"창의적 전략 백테스팅: {start_round}회 ~ {end_round}회")
        print(f"전략 수: {len(self.strategies)}개")
        print(f"{'='*80}\n")

        for h in self.history:
            round_num = h['round']
            if round_num < start_round or round_num > end_round:
                continue

            actual = h['numbers']
            bonus = h.get('bonus', 0)

            self.results[round_num] = {}

            for strategy in self.strategies:
                try:
                    prediction = strategy.generate(round_num, self.history)
                    match_count, rank = self.check_match(prediction, actual, bonus)

                    self.results[round_num][strategy.name] = {
                        'numbers': prediction,
                        'match': match_count,
                        'rank': rank,
                    }
                except Exception as e:
                    pass

            if round_num % 200 == 0:
                print(f"  진행: {round_num}회 완료")

        print("백테스팅 완료!\n")

    def get_statistics(self) -> Dict:
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

            cost = total * 1000
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
                '1등': rank_counts['1등'],
                '2등': rank_counts['2등'],
                '3등': rank_counts['3등'],
                '4등': rank_counts['4등'],
                '5등': rank_counts['5등'],
                '4등+': sum(rank_counts[r] for r in ['1등', '2등', '3등', '4등']),
                '4등+율': round(sum(rank_counts[r] for r in ['1등', '2등', '3등', '4등']) / total * 100, 2),
                '수익률': round(roi, 2),
            }

        return stats

    def print_summary(self):
        stats = self.get_statistics()

        print("=" * 120)
        print("창의적 전략 백테스팅 결과")
        print("=" * 120)

        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['4등+율'], reverse=True)

        print(f"\n{'순위':<4} {'전략명':<18} {'총회차':<8} {'1등':<5} {'2등':<5} {'3등':<5} {'4등':<5} {'5등':<5} {'4등+':<6} {'4등+율':<9} {'수익률':<10}")
        print("-" * 120)

        for i, (name, s) in enumerate(sorted_stats, 1):
            print(f"{i:<4} {name:<18} {s['total']:<8} {s['1등']:<5} {s['2등']:<5} {s['3등']:<5} {s['4등']:<5} {s['5등']:<5} {s['4등+']:<6} {s['4등+율']:<8.2f}% {s['수익률']:<9.2f}%")

        print("=" * 120)

        # 통계
        avg_roi = sum(s['수익률'] for s in stats.values()) / len(stats)
        best_roi = max(stats.items(), key=lambda x: x[1]['수익률'])
        best_4plus = max(stats.items(), key=lambda x: x[1]['4등+율'])

        print(f"\n평균 수익률: {avg_roi:.2f}%")
        print(f"최고 수익률: {best_roi[0]} ({best_roi[1]['수익률']:.2f}%)")
        print(f"최고 4등+율: {best_4plus[0]} ({best_4plus[1]['4등+율']:.2f}%)")


def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'lotto_data.json')

    engine = BacktestEngine(data_path)
    engine.run_backtest(start_round=1)
    engine.print_summary()


if __name__ == '__main__':
    main()
