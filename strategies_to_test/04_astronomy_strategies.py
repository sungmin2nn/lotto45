"""
천문학/우주 기반 전략 (20개)
"""
import json
import random
import math
from collections import Counter
from datetime import datetime

with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

# 전략 1: 행성 거리 전략
def planet_distance_strategy(data, round_num):
    """태양계 행성 거리 비율"""
    # 수성:금성:지구:화성:목성:토성 = 0.4:0.7:1:1.5:5.2:9.5 AU
    distances = [4, 7, 10, 15, 5, 9, 19, 30, 39, 45]  # 비율 기반
    return sorted(random.sample(distances, 6))

# 전략 2: 달의 위상 전략
def moon_phase_strategy(data, round_num):
    """달의 위상 주기 (29.5일)"""
    # round_num을 달 위상과 연결
    phase = (round_num * 7) % 30  # 주 1회 추첨 가정

    # 위상에 따른 번호 선택
    base = phase + 1
    numbers = []
    for i in range(10):
        num = (base + i * 4) % 45 + 1
        numbers.append(num)

    return sorted(random.sample(list(set(numbers)), 6))

# 전략 3: 별자리 전략
def constellation_strategy(data, round_num):
    """12별자리 관련 숫자"""
    # 각 별자리의 대표 숫자
    constellations = {
        '양자리': [1, 9, 19],
        '황소자리': [2, 6, 12],
        '쌍둥이자리': [3, 15, 27],
        '게자리': [4, 7, 21],
        '사자자리': [5, 14, 23],
        '처녀자리': [6, 18, 27],
        '천칭자리': [7, 11, 22],
        '전갈자리': [8, 17, 26],
        '사수자리': [9, 16, 25],
        '염소자리': [10, 19, 28],
        '물병자리': [11, 20, 29],
        '물고기자리': [12, 21, 30]
    }
    all_nums = []
    for nums in constellations.values():
        all_nums.extend(nums)

    valid = list(set([n for n in all_nums if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 4: 태양 활동 주기 전략
def solar_cycle_strategy(data, round_num):
    """태양 활동 11년 주기"""
    cycle = 11 * 52  # 주 단위
    position = round_num % cycle

    # 주기 위치에 따른 번호
    base = (position % 45) + 1
    numbers = [base]
    for i in range(1, 10):
        num = (base + i * 11) % 45 + 1
        numbers.append(num)

    return sorted(random.sample(list(set(numbers)), 6))

# 전략 5: 황도대 전략
def zodiac_belt_strategy(data, round_num):
    """황도 12궁 각도"""
    # 각 궁은 30도, 360도를 45로 매핑
    angles = []
    for i in range(12):
        angle = i * 30
        num = int(angle / 360 * 45) + 1
        angles.append(num)

    # 추가 번호
    for i in range(12):
        num = (i * 4) % 45 + 1
        angles.append(num)

    valid = list(set([n for n in angles if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 6: 케플러 법칙 전략
def kepler_law_strategy(data, round_num):
    """케플러 행성 운동 법칙"""
    # T² ∝ a³ (주기의 제곱 = 궤도 장반경의 세제곱)
    # 1, 4, 9, 16, 25, 36... (제곱수)
    squares = [i*i for i in range(1, 10) if i*i <= 45]
    # 1, 8, 27... (세제곱수)
    cubes = [i*i*i for i in range(1, 5) if i*i*i <= 45]

    pool = list(set(squares + cubes))
    if len(pool) < 6:
        pool += random.sample([n for n in range(1, 46) if n not in pool], 6 - len(pool))

    return sorted(random.sample(pool, 6))

# 전략 7: 빛의 속도 전략
def light_speed_strategy(data, round_num):
    """빛의 속도 관련 숫자 (299,792 km/s)"""
    # 숫자들: 2, 9, 7
    light_nums = [2, 9, 7, 29, 27, 19, 17, 22, 12, 39, 37, 30]
    valid = [n for n in light_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 8: 중력 상수 전략
def gravity_constant_strategy(data, round_num):
    """중력 상수 G = 6.674 × 10^-11"""
    gravity_nums = [6, 7, 4, 11, 67, 66, 10, 1]
    valid = [n for n in gravity_nums if 1 <= n <= 45]
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))
    return sorted(random.sample(valid, 6))

# 전략 9: 허블 상수 전략
def hubble_constant_strategy(data, round_num):
    """허블 상수 ~70 km/s/Mpc"""
    hubble_nums = [7, 70, 14, 21, 28, 35, 42, 17, 27, 37]
    valid = [n for n in hubble_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 10: 천문 단위 전략
def astronomical_unit_strategy(data, round_num):
    """1 AU = 약 1.5억 km"""
    au_nums = [1, 5, 15, 10, 30, 45, 3, 6, 9, 12, 18, 21, 24, 27, 33, 36, 39, 42]
    valid = [n for n in au_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 11: 적색편이 전략
def redshift_strategy(data, round_num):
    """우주 팽창 - 적색편이"""
    # z 값들을 번호로 매핑
    z_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    expanded = []
    for z in z_values:
        expanded.append(z)
        expanded.append(z * 3)
        expanded.append(z * 4)

    valid = list(set([n for n in expanded if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 12: 블랙홀 전략
def black_hole_strategy(data, round_num):
    """블랙홀 관련 숫자 (슈바르츠실트 반경)"""
    # 사건의 지평선 근처 효과
    # 강한 숫자와 약한 숫자의 대비
    strong = [1, 2, 3, 4, 5]  # 사건의 지평선 안
    weak = [41, 42, 43, 44, 45]  # 멀리
    medium = random.sample(range(15, 35), 5)

    pool = strong + weak + medium
    return sorted(random.sample(pool, 6))

# 전략 13: 우주 배경 복사 전략
def cmb_strategy(data, round_num):
    """우주 배경 복사 2.725 K"""
    cmb_nums = [2, 7, 25, 27, 3, 5, 10, 15, 20, 30, 35, 40, 45]
    valid = [n for n in cmb_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 14: 안드로메다 전략
def andromeda_strategy(data, round_num):
    """안드로메다 은하까지 250만 광년"""
    andro_nums = [2, 5, 25, 50, 10, 20, 15, 30, 40, 45, 1, 4]
    valid = [n for n in andro_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 15: 오리온 전략
def orion_strategy(data, round_num):
    """오리온 자리 별들"""
    # 베텔게우스, 리겔 등 주요 별의 등급/거리
    orion_nums = [1, 2, 3, 7, 8, 9, 17, 18, 19, 27, 28, 29, 37, 38, 39]
    valid = [n for n in orion_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 16: 북두칠성 전략
def big_dipper_strategy(data, round_num):
    """북두칠성 7개 별"""
    # 7과 관련된 숫자들
    seven_related = [7, 14, 21, 28, 35, 42, 1, 2, 3, 4, 5, 6, 8, 17, 27, 37]
    valid = [n for n in seven_related if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 17: 혜성 주기 전략
def comet_cycle_strategy(data, round_num):
    """핼리 혜성 76년 주기"""
    # 76, 38, 19... 관련 숫자
    comet_nums = [19, 38, 7, 6, 13, 26, 39, 14, 28, 42, 5, 10, 15, 20]
    valid = [n for n in comet_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 18: 금성 주기 전략
def venus_cycle_strategy(data, round_num):
    """금성 회합 주기 584일"""
    # 5, 8, 4 관련
    venus_nums = [5, 8, 4, 58, 45, 40, 13, 21, 26, 34, 18, 27, 36]
    valid = [n for n in venus_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 19: 토성 고리 전략
def saturn_ring_strategy(data, round_num):
    """토성 고리 구조"""
    # 동심원 패턴: A, B, C 고리
    rings = []
    centers = [10, 20, 30]
    for c in centers:
        rings.extend([c-2, c-1, c, c+1, c+2])

    valid = list(set([n for n in rings if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 20: 초신성 전략
def supernova_strategy(data, round_num):
    """초신성 폭발 - 극단적 값"""
    # 최소와 최대의 대비
    extreme = [1, 2, 3, 43, 44, 45, 22, 23, 21, 24, 20, 25]
    valid = [n for n in extreme if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))


# 전략 목록
STRATEGIES = {
    '행성_거리': planet_distance_strategy,
    '달의_위상': moon_phase_strategy,
    '별자리': constellation_strategy,
    '태양_활동': solar_cycle_strategy,
    '황도대': zodiac_belt_strategy,
    '케플러_법칙': kepler_law_strategy,
    '빛의_속도': light_speed_strategy,
    '중력_상수': gravity_constant_strategy,
    '허블_상수': hubble_constant_strategy,
    '천문_단위': astronomical_unit_strategy,
    '적색편이': redshift_strategy,
    '블랙홀': black_hole_strategy,
    '우주_배경_복사': cmb_strategy,
    '안드로메다': andromeda_strategy,
    '오리온': orion_strategy,
    '북두칠성': big_dipper_strategy,
    '혜성_주기': comet_cycle_strategy,
    '금성_주기': venus_cycle_strategy,
    '토성_고리': saturn_ring_strategy,
    '초신성': supernova_strategy,
}

if __name__ == '__main__':
    print(f"천문학 전략 {len(STRATEGIES)}개 로드됨")
    for name in STRATEGIES.keys():
        print(f"  - {name}")
