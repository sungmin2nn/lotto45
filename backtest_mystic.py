#!/usr/bin/env python3
"""
로또 명리학/점성술/띠 기반 전략 백테스팅
- 음양오행, 천간지지, 십이지신, 사주팔자 등 15개 전략
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import math

# ============================================================
# 전략 기본 클래스
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

    def get_date_from_round(self, round_num: int) -> datetime:
        """회차 번호를 날짜로 변환 (1회: 2002-12-07)"""
        start_date = datetime(2002, 12, 7)
        return start_date + timedelta(weeks=round_num - 1)


# ============================================================
# 명리학/점성술/띠 기반 전략 15개
# ============================================================

class YinYangWuxingStrategy(LottoStrategy):
    """1. 음양오행 - 번호를 음양오행으로 분류, 균형 맞추기"""

    def __init__(self):
        super().__init__("음양오행", "번호를 음양오행(목화토금수)으로 분류하여 균형있게 선택")
        # 오행 분류: 끝수로 분류
        # 1,2:목(木), 3,4:화(火), 5,6:토(土), 7,8:금(金), 9,0:수(水)
        self.wuxing = {
            '목': [1, 2, 11, 12, 21, 22, 31, 32, 41, 42],
            '화': [3, 4, 13, 14, 23, 24, 33, 34, 43, 44],
            '토': [5, 6, 15, 16, 25, 26, 35, 36, 45],
            '금': [7, 8, 17, 18, 27, 28, 37, 38],
            '수': [9, 10, 19, 20, 29, 30, 39, 40]
        }

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 각 오행에서 최소 1개씩 선택 (5개), 나머지 1개는 랜덤
        selected = []
        elements = list(self.wuxing.keys())
        random.shuffle(elements)

        for elem in elements[:5]:
            pool = [n for n in self.wuxing[elem] if n not in selected]
            if pool:
                selected.append(random.choice(pool))

        # 6개째 추가
        all_nums = [n for n in range(1, 46) if n not in selected]
        if all_nums:
            selected.append(random.choice(all_nums))

        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.append(n)

        return sorted(selected[:6])


class CheonganJijiStrategy(LottoStrategy):
    """2. 천간지지 - 10천간 12지지 기반 번호"""

    def __init__(self):
        super().__init__("천간지지", "10천간 12지지 조합 기반 번호")
        # 천간(10): 갑을병정무기경신임계
        self.cheonggan = list(range(1, 11))
        # 지지(12): 자축인묘진사오미신유술해
        self.jiji = list(range(1, 13))

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 회차를 60갑자 순환으로 변환
        gapja_idx = (round_num - 1) % 60
        cheonggan_idx = gapja_idx % 10
        jiji_idx = gapja_idx % 12

        selected = set()

        # 천간 번호
        selected.add(self.cheonggan[cheonggan_idx])
        # 지지 번호
        selected.add(self.jiji[jiji_idx])

        # 천간+지지 조합
        combined = (cheonggan_idx + jiji_idx) % 45 + 1
        selected.add(combined)

        # 천간*지지
        multiplied = (cheonggan_idx * jiji_idx) % 45 + 1
        selected.add(multiplied)

        # 나머지는 천간, 지지에서 선택
        pool = set(self.cheonggan + self.jiji) - selected
        while len(selected) < 6 and pool:
            selected.add(pool.pop())

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class ZodiacAnimalStrategy(LottoStrategy):
    """3. 십이지신(띠) - 해당 연도 띠 번호"""

    def __init__(self):
        super().__init__("십이지신_띠", "해당 연도 띠 번호 선택 (쥐1, 소2, 범3...)")
        # 십이지: 자(쥐), 축(소), 인(범), 묘(토끼), 진(용), 사(뱀)
        #        오(말), 미(양), 신(원숭이), 유(닭), 술(개), 해(돼지)
        self.animals = ['쥐', '소', '범', '토끼', '용', '뱀',
                       '말', '양', '원숭이', '닭', '개', '돼지']

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)
        year = date.year

        # 2020년 = 쥐띠 기준
        animal_idx = (year - 2020) % 12

        # 띠 번호: 1, 13, 25, 37 (쥐띠면)
        base_num = animal_idx + 1
        animal_nums = []
        for i in range(4):
            num = base_num + i * 12
            if 1 <= num <= 45:
                animal_nums.append(num)

        # 띠 번호 중 2~3개 선택
        selected = set()
        if len(animal_nums) >= 2:
            selected.update(random.sample(animal_nums, min(3, len(animal_nums))))

        # 나머지는 행운의 수로
        lucky_nums = [year % 45 + 1, (year // 10) % 45 + 1, (year % 100) % 45 + 1]
        for num in lucky_nums:
            if num not in selected and 1 <= num <= 45:
                selected.add(num)
                if len(selected) >= 6:
                    break

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class SajuPaljaStrategy(LottoStrategy):
    """4. 사주팔자 - 생년월일시 기반 (회차를 날짜로 변환)"""

    def __init__(self):
        super().__init__("사주팔자", "추첨일 기준 사주(년월일시) 기반 번호")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)

        # 년, 월, 일, 시를 번호로 변환
        year_num = date.year % 45 + 1
        month_num = date.month
        day_num = date.day % 45 + 1
        hour_num = ((round_num * 7) % 24) % 45 + 1  # 가상의 시

        selected = set([year_num, month_num, day_num, hour_num])

        # 사주 합
        saju_sum = (date.year + date.month + date.day) % 45 + 1
        selected.add(saju_sum)

        # 사주 곱
        saju_mul = (date.year % 10) * (date.month % 10) * (date.day % 10) % 45 + 1
        selected.add(saju_mul)

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class MagicSquareStrategy(LottoStrategy):
    """5. 구성 마방진 - 3x3 마방진 숫자 활용"""

    def __init__(self):
        super().__init__("구성_마방진", "3x3 마방진(낙서) 숫자 기반")
        # 낙서(洛書) 마방진
        self.magic_square = [
            [4, 9, 2],
            [3, 5, 7],
            [8, 1, 6]
        ]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 마방진 숫자들
        base_nums = []
        for row in self.magic_square:
            base_nums.extend(row)

        # 배수로 확장
        selected = set()
        multiplier = (round_num % 5) + 1

        for num in base_nums:
            expanded = num * multiplier
            if 1 <= expanded <= 45:
                selected.add(expanded)
            if len(selected) >= 6:
                break

        # 부족하면 원본 숫자 사용
        for num in base_nums:
            if num <= 45:
                selected.add(num)
            if len(selected) >= 6:
                break

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class PalgwaeStrategy(LottoStrategy):
    """6. 팔괘 - 8괘 기반 번호 선택"""

    def __init__(self):
        super().__init__("팔괘", "8괘(건곤감리진손간태) 기반 번호")
        # 팔괘: 건(1), 태(2), 리(3), 진(4), 손(5), 감(6), 간(7), 곤(8)
        self.palgwae = {
            '건': [1, 9, 17, 25, 33, 41],
            '태': [2, 10, 18, 26, 34, 42],
            '리': [3, 11, 19, 27, 35, 43],
            '진': [4, 12, 20, 28, 36, 44],
            '손': [5, 13, 21, 29, 37, 45],
            '감': [6, 14, 22, 30, 38],
            '간': [7, 15, 23, 31, 39],
            '곤': [8, 16, 24, 32, 40]
        }

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 회차에 따라 괘 선택
        gwae_idx = round_num % 8
        gwae_names = list(self.palgwae.keys())
        primary_gwae = gwae_names[gwae_idx]
        secondary_gwae = gwae_names[(gwae_idx + 4) % 8]  # 대칭 괘

        selected = set()

        # 주 괘에서 3개
        pool1 = self.palgwae[primary_gwae]
        selected.update(random.sample(pool1, min(3, len(pool1))))

        # 부 괘에서 3개
        pool2 = [n for n in self.palgwae[secondary_gwae] if n not in selected]
        selected.update(random.sample(pool2, min(3, len(pool2))))

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class ZodiacSignStrategy(LottoStrategy):
    """7. 별자리 - 12별자리 기반"""

    def __init__(self):
        super().__init__("별자리", "12별자리 기반 번호 (양자리1, 황소2...)")
        self.zodiac_signs = ['양자리', '황소', '쌍둥이', '게', '사자', '처녀',
                            '천칭', '전갈', '사수', '염소', '물병', '물고기']

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)

        # 날짜로 별자리 판단 (간단 버전)
        month = date.month
        day = date.day

        # 별자리 인덱스 (대략)
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            sign_idx = 0  # 양자리
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            sign_idx = 1  # 황소
        elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
            sign_idx = 2  # 쌍둥이
        elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
            sign_idx = 3  # 게
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            sign_idx = 4  # 사자
        elif (month == 8 and day >= 23) or (month == 9 and day <= 23):
            sign_idx = 5  # 처녀
        elif (month == 9 and day >= 24) or (month == 10 and day <= 22):
            sign_idx = 6  # 천칭
        elif (month == 10 and day >= 23) or (month == 11 and day <= 22):
            sign_idx = 7  # 전갈
        elif (month == 11 and day >= 23) or (month == 12 and day <= 21):
            sign_idx = 8  # 사수
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            sign_idx = 9  # 염소
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            sign_idx = 10  # 물병
        else:
            sign_idx = 11  # 물고기

        # 별자리 번호
        base_num = sign_idx + 1
        sign_nums = []
        for i in range(4):
            num = base_num + i * 12
            if 1 <= num <= 45:
                sign_nums.append(num)

        selected = set()
        if sign_nums:
            selected.update(random.sample(sign_nums, min(3, len(sign_nums))))

        # 행운의 숫자 추가
        lucky = [month, day % 45 + 1, (month * day) % 45 + 1]
        for num in lucky:
            if num not in selected and 1 <= num <= 45:
                selected.add(num)
                if len(selected) >= 6:
                    break

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class PlanetStrategy(LottoStrategy):
    """8. 행성배치 - 7행성 번호 (1-7, 8-14...)"""

    def __init__(self):
        super().__init__("행성배치", "7행성(일월화수목금토) 기반 번호")
        # 7행성: 태양(일), 달(월), 화성(화), 수성(수), 목성(목), 금성(금), 토성(토)
        self.planets = {
            '일': [1, 8, 15, 22, 29, 36, 43],
            '월': [2, 9, 16, 23, 30, 37, 44],
            '화': [3, 10, 17, 24, 31, 38, 45],
            '수': [4, 11, 18, 25, 32, 39],
            '목': [5, 12, 19, 26, 33, 40],
            '금': [6, 13, 20, 27, 34, 41],
            '토': [7, 14, 21, 28, 35, 42]
        }

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)

        # 요일 계산
        weekday = date.weekday()  # 0:월, 1:화, ..., 6:일
        planet_names = ['월', '화', '수', '목', '금', '토', '일']
        today_planet = planet_names[weekday]

        selected = set()

        # 오늘의 행성에서 2개
        pool1 = self.planets[today_planet]
        selected.update(random.sample(pool1, min(2, len(pool1))))

        # 다른 행성들에서 각 1개씩
        other_planets = [p for p in planet_names if p != today_planet]
        random.shuffle(other_planets)

        for planet in other_planets:
            if len(selected) >= 6:
                break
            pool = [n for n in self.planets[planet] if n not in selected]
            if pool:
                selected.add(random.choice(pool))

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class LunarPhaseStrategy(LottoStrategy):
    """9. 달의 위상 - 추첨일 음력 날짜 기반"""

    def __init__(self):
        super().__init__("달의_위상", "음력 날짜 기반 번호 (초하루~그믐)")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)

        # 간단한 음력 근사 (실제로는 복잡하지만 간소화)
        # 달의 위상 주기: 약 29.5일
        days_since_epoch = (date - datetime(2000, 1, 1)).days
        lunar_day = (days_since_epoch % 30) + 1  # 1~30

        selected = set()

        # 음력 날짜
        selected.add(lunar_day)

        # 음력 날짜의 배수
        for i in range(1, 4):
            num = (lunar_day * i) % 45 + 1
            selected.add(num)
            if len(selected) >= 6:
                break

        # 달의 위상별 번호
        if lunar_day <= 7:  # 초승달
            phase_nums = [1, 8, 15, 22, 29, 36]
        elif lunar_day <= 15:  # 상현달
            phase_nums = [7, 14, 21, 28, 35, 42]
        elif lunar_day <= 22:  # 보름달
            phase_nums = [15, 16, 17, 18, 19, 20]
        else:  # 하현달
            phase_nums = [30, 31, 32, 33, 34, 35]

        for num in phase_nums:
            if num not in selected and 1 <= num <= 45:
                selected.add(num)
                if len(selected) >= 6:
                    break

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class SolarTermStrategy(LottoStrategy):
    """10. 절기 - 24절기 기반 번호"""

    def __init__(self):
        super().__init__("절기", "24절기 기반 번호 선택")
        # 24절기 (간소화)
        self.solar_terms = [
            '입춘', '우수', '경칩', '춘분', '청명', '곡우',
            '입하', '소만', '망종', '하지', '소서', '대서',
            '입추', '처서', '백로', '추분', '한로', '상강',
            '입동', '소설', '대설', '동지', '소한', '대한'
        ]

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)

        # 절기 인덱스 (월에 따라 대략)
        month = date.month
        day = date.day

        # 각 월마다 2개의 절기
        term_idx = ((month - 1) * 2 + (1 if day >= 15 else 0)) % 24

        # 절기 번호
        base_num = term_idx + 1
        term_nums = []
        for i in range(3):
            num = base_num + i * 24
            if 1 <= num <= 45:
                term_nums.append(num)

        selected = set()
        if term_nums:
            selected.update(term_nums)

        # 절기 순서 번호
        selected.add((term_idx % 45) + 1)

        # 계절 번호 (봄0-5, 여름6-11, 가을12-17, 겨울18-23)
        season = term_idx // 6
        season_nums = [season * 10 + i for i in range(1, 6) if 1 <= season * 10 + i <= 45]
        for num in season_nums:
            if num not in selected:
                selected.add(num)
                if len(selected) >= 6:
                    break

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class SamjaeStrategy(LottoStrategy):
    """11. 삼재 - 삼재 피하기"""

    def __init__(self):
        super().__init__("삼재", "삼재 해당 번호 피하기")
        # 삼재: 12년 주기로 들삼재, 눌삼재, 날삼재

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)
        year = date.year

        # 삼재 띠 (12년 주기)
        animal_idx = (year - 2020) % 12

        # 들삼재, 눌삼재, 날삼재 (연속된 3개 띠)
        samjae_animals = [(animal_idx + i) % 12 for i in range(3)]

        # 삼재 번호들
        samjae_nums = set()
        for idx in samjae_animals:
            base = idx + 1
            for i in range(4):
                num = base + i * 12
                if 1 <= num <= 45:
                    samjae_nums.add(num)

        # 삼재 아닌 번호들
        safe_nums = [n for n in range(1, 46) if n not in samjae_nums]

        if len(safe_nums) >= 6:
            return sorted(random.sample(safe_nums, 6))

        # 부족하면 전체에서
        return sorted(random.sample(range(1, 46), 6))


class LuckyDayStrategy(LottoStrategy):
    """12. 길일 - 음력 길일 기반"""

    def __init__(self):
        super().__init__("길일", "음력 길일(초하루, 보름, 말일) 기반")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)

        # 음력 날짜 (간소화)
        days_since_epoch = (date - datetime(2000, 1, 1)).days
        lunar_day = (days_since_epoch % 30) + 1

        # 길일 여부
        is_lucky = lunar_day in [1, 15, 30] or lunar_day % 7 == 0

        if is_lucky:
            # 길일이면 특별 번호
            lucky_nums = [1, 3, 7, 9, 15, 21, 28, 33, 37, 43]
        else:
            # 평범한 날
            lucky_nums = list(range(1, 46))

        selected = set()

        # 날짜 관련 번호
        selected.add(lunar_day)
        selected.add(date.day % 45 + 1)
        selected.add((date.month * date.day) % 45 + 1)

        # 길일 번호에서 선택
        pool = [n for n in lucky_nums if n not in selected]
        while len(selected) < 6 and pool:
            selected.add(random.choice(pool))
            pool = [n for n in pool if n not in selected]

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class AstronomyAngleStrategy(LottoStrategy):
    """13. 천문 각도 - 행성 각도 기반"""

    def __init__(self):
        super().__init__("천문_각도", "행성 각도(0-360도) 기반 번호")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        date = self.get_date_from_round(round_num)

        # 가상의 행성 각도 (일자 기반)
        days_since_epoch = (date - datetime(2000, 1, 1)).days

        # 각 행성의 공전 주기 (간소화)
        mercury_angle = (days_since_epoch * 4.15) % 360  # 수성
        venus_angle = (days_since_epoch * 1.6) % 360     # 금성
        mars_angle = (days_since_epoch * 0.53) % 360     # 화성

        selected = set()

        # 각도를 번호로 변환 (0-360 -> 1-45)
        selected.add(int(mercury_angle / 360 * 45) + 1)
        selected.add(int(venus_angle / 360 * 45) + 1)
        selected.add(int(mars_angle / 360 * 45) + 1)

        # 각도 합
        total_angle = (mercury_angle + venus_angle + mars_angle) % 360
        selected.add(int(total_angle / 360 * 45) + 1)

        # 각도 차
        angle_diff = abs(mercury_angle - venus_angle) % 180
        selected.add(int(angle_diff / 180 * 45) + 1)

        # 특수 각도 (120도, 180도)
        if abs(venus_angle - mars_angle) < 30:  # 합
            special_nums = [11, 22, 33, 44]
        elif abs(venus_angle - mars_angle) > 150:  # 충
            special_nums = [7, 14, 21, 28, 35, 42]
        else:
            special_nums = [5, 10, 15, 20, 25, 30, 35, 40, 45]

        for num in special_nums:
            if num not in selected:
                selected.add(num)
                if len(selected) >= 6:
                    break

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class TarotStrategy(LottoStrategy):
    """14. 타로 - 22장 메이저 아르카나 기반"""

    def __init__(self):
        super().__init__("타로", "22장 메이저 아르카나 기반 번호")
        # 메이저 아르카나: 0(바보) ~ 21(세계)
        self.major_arcana = list(range(22))

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 회차 기반 타로 카드 선택
        card_idx = round_num % 22

        selected = set()

        # 선택된 카드 번호
        card_num = card_idx if card_idx > 0 else 22  # 0 대신 22
        selected.add(card_num)

        # 카드의 배수
        for i in range(2, 4):
            num = (card_num * i) % 45 + 1
            selected.add(num)

        # 카드 의미별 번호
        if card_idx in [0, 1, 10, 19]:  # 시작/변화
            theme_nums = [1, 10, 19, 28, 37]
        elif card_idx in [2, 11, 20]:  # 균형
            theme_nums = [2, 11, 20, 29, 38]
        elif card_idx in [3, 12, 21]:  # 완성
            theme_nums = [3, 12, 21, 30, 39]
        else:  # 기타
            theme_nums = [7, 14, 21, 28, 35, 42]

        for num in theme_nums:
            if num not in selected and 1 <= num <= 45:
                selected.add(num)
                if len(selected) >= 6:
                    break

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


class YijingCycleStrategy(LottoStrategy):
    """15. 역학 순환 - 60갑자 순환"""

    def __init__(self):
        super().__init__("역학_순환", "60갑자 순환 기반 번호")

    def generate(self, round_num: int, history: List[Dict]) -> List[int]:
        # 60갑자 순환
        gapja_idx = (round_num - 1) % 60

        selected = set()

        # 갑자 번호
        selected.add((gapja_idx % 45) + 1)

        # 10간 번호
        gan_idx = gapja_idx % 10
        selected.add(gan_idx + 1)

        # 12지 번호
        ji_idx = gapja_idx % 12
        selected.add(ji_idx + 1)

        # 60갑자의 1/3, 2/3 지점
        selected.add((gapja_idx + 20) % 45 + 1)
        selected.add((gapja_idx + 40) % 45 + 1)

        # 순환 패턴
        cycle_nums = []
        for i in range(1, 6):
            num = ((gapja_idx * i) % 45) + 1
            cycle_nums.append(num)

        for num in cycle_nums:
            if num not in selected:
                selected.add(num)
                if len(selected) >= 6:
                    break

        # 부족하면 랜덤
        while len(selected) < 6:
            n = random.randint(1, 45)
            if n not in selected:
                selected.add(n)

        return sorted(list(selected)[:6])


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
        """전략들 초기화"""
        return [
            YinYangWuxingStrategy(),
            CheonganJijiStrategy(),
            ZodiacAnimalStrategy(),
            SajuPaljaStrategy(),
            MagicSquareStrategy(),
            PalgwaeStrategy(),
            ZodiacSignStrategy(),
            PlanetStrategy(),
            LunarPhaseStrategy(),
            SolarTermStrategy(),
            SamjaeStrategy(),
            LuckyDayStrategy(),
            AstronomyAngleStrategy(),
            TarotStrategy(),
            YijingCycleStrategy(),
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

        print(f"백테스팅 시작: {start_round}회 ~ {end_round}회")
        print(f"전략 수: {len(self.strategies)}개")
        print("-" * 60)

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
                    'actual': actual,
                    'bonus': bonus
                }

            if round_num % 100 == 0:
                print(f"  {round_num}회 완료")

        print("-" * 60)
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

            # 수익률 계산 (1게임 1000원 기준)
            cost = total * 1000
            prize = (rank_counts['1등'] * 2000000000 +  # 1등 평균 20억 (가정)
                    rank_counts['2등'] * 50000000 +     # 2등 평균 5천만
                    rank_counts['3등'] * 1500000 +      # 3등 평균 150만
                    rank_counts['4등'] * 50000 +        # 4등 평균 5만
                    rank_counts['5등'] * 5000)          # 5등 고정 5천
            roi = ((prize - cost) / cost * 100) if cost > 0 else 0

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

        print("\n" + "=" * 90)
        print("명리학/점성술/띠 기반 전략 백테스팅 결과")
        print("=" * 90)

        # 4등+ 비율로 정렬
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['4등+율'], reverse=True)

        header = f"{'순위':<4} {'전략명':<15} {'총회차':<7} {'1등':<5} {'2등':<5} {'3등':<5} {'4등':<5} {'5등':<6} {'4등+':<6} {'4등+율':<8} {'수익률':<10}"
        print(header)
        print("-" * 90)

        for i, (name, s) in enumerate(sorted_stats, 1):
            row = f"{i:<4} {name:<15} {s['total']:<7} {s['1등']:<5} {s['2등']:<5} {s['3등']:<5} {s['4등']:<5} {s['5등']:<6} {s['4등+']:<6} {s['4등+율']:<7}% {s['수익률']:<9}%"
            print(row)

        print("=" * 90)

        # 추가 분석
        print("\n주요 통계:")
        print(f"  평균 4등+ 비율: {sum(s['4등+율'] for s in stats.values()) / len(stats):.2f}%")
        print(f"  평균 수익률: {sum(s['수익률'] for s in stats.values()) / len(stats):.2f}%")
        print(f"  최고 4등+ 비율: {max(s['4등+율'] for s in stats.values()):.2f}% ({sorted_stats[0][0]})")
        print(f"  최고 수익률: {max(s['수익률'] for s in stats.values()):.2f}%")


# ============================================================
# 메인 실행
# ============================================================

def main():
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'lotto_data.json')

    engine = BacktestEngine(data_path)
    engine.run_backtest(start_round=1)
    engine.print_summary()


if __name__ == '__main__':
    main()
