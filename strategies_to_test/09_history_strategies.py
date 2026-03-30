"""
역사적 사건 기반 전략 (20개)
"""
import json
import random
from collections import Counter

with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

# 전략 1: 한국 역사 연도 전략
def korean_history_strategy(data, round_num):
    """한국 역사 주요 연도"""
    # 1945광복, 1950한국전쟁, 1988올림픽, 2002월드컵
    years = [45, 50, 88, 2, 19, 48, 53, 60, 79, 87, 97, 18, 3, 15, 10]
    # 45 범위로 매핑
    mapped = [y % 45 + 1 if y > 45 else y for y in years]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 2: 세계 대전 전략
def world_war_strategy(data, round_num):
    """세계대전 관련 연도/숫자"""
    # WW1:1914-1918, WW2:1939-1945
    ww = [14, 18, 39, 45, 41, 44, 17, 16, 15, 19, 38, 40, 42, 43, 1, 2]
    valid = [n for n in ww if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 3: 왕조 연대기 전략
def dynasty_strategy(data, round_num):
    """한국 왕조 기간"""
    # 고조선:2333년, 삼국시대:57년, 고려:474년, 조선:518년
    dynasties = [23, 33, 5, 7, 47, 4, 51, 18, 92, 35, 13, 9, 27, 38, 44]
    # 45 범위로
    mapped = [d % 45 + 1 if d > 45 else d for d in dynasties]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 4: 혁명/독립 전략
def revolution_strategy(data, round_num):
    """혁명/독립 연도"""
    # 미국독립:1776, 프랑스혁명:1789, 러시아혁명:1917
    revolutions = [76, 89, 17, 48, 19, 45, 63, 68, 79, 91]
    # 45 범위로
    mapped = [r % 45 + 1 if r > 45 else r for r in revolutions]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 5: 올림픽 개최 연도 전략
def olympics_strategy(data, round_num):
    """하계올림픽 개최 연도"""
    # 88서울, 96애틀랜타, 00시드니, 04아테네, 08베이징, 12런던, 16리우, 20도쿄
    olympics = [88, 96, 0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 64, 72, 76, 80, 84]
    # 45 범위로
    mapped = [o % 45 + 1 if o > 45 else max(o, 1) for o in olympics]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 6: 과학 발견 전략
def scientific_discovery_strategy(data, round_num):
    """주요 과학 발견 연도"""
    # 만유인력:1687, 상대성이론:1905, DNA:1953
    discoveries = [87, 5, 53, 69, 95, 28, 32, 11, 20, 43, 38, 42, 16, 24, 8]
    # 45 범위로
    mapped = [d % 45 + 1 if d > 45 else d for d in discoveries]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 7: 인물 탄생년 전략
def birth_year_strategy(data, round_num):
    """역사적 인물 탄생년"""
    # 세종:1397, 이순신:1545, 안중근:1879
    births = [97, 45, 79, 52, 64, 89, 56, 69, 42, 18, 9, 32, 24, 15, 6]
    # 45 범위로
    mapped = [b % 45 + 1 if b > 45 else b for b in births]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 8: 전쟁/전투 전략
def battle_strategy(data, round_num):
    """주요 전쟁/전투 연도"""
    # 임진왜란:1592, 병자호란:1636, 한국전쟁:1950
    battles = [92, 36, 50, 53, 12, 27, 15, 18, 44, 45, 39, 41, 63, 73, 79]
    # 45 범위로
    mapped = [b % 45 + 1 if b > 45 else b for b in battles]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 9: 문화유산 전략
def heritage_strategy(data, round_num):
    """문화유산 지정 번호/연도"""
    # 국보 1호, 보물 번호 등
    heritage = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 86, 95]
    # 45 범위로
    mapped = [h % 45 + 1 if h > 45 else h for h in heritage]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 10: 조약/협정 전략
def treaty_strategy(data, round_num):
    """주요 조약/협정 연도"""
    # 강화도조약:1876, 을사늑약:1905, 한일병합:1910
    treaties = [76, 5, 10, 45, 48, 53, 65, 72, 91, 19, 25, 38, 42, 33, 28]
    # 45 범위로
    mapped = [t % 45 + 1 if t > 45 else t for t in treaties]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 11: 우주 탐사 전략
def space_exploration_strategy(data, round_num):
    """우주 탐사 연도"""
    # 스푸트니크:1957, 달착륙:1969, 화성탐사:2020
    space = [57, 69, 20, 61, 62, 65, 70, 71, 72, 75, 77, 81, 86, 90, 97]
    # 45 범위로
    mapped = [s % 45 + 1 if s > 45 else s for s in space]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 12: 제국 연대 전략
def empire_strategy(data, round_num):
    """대제국 존속 기간"""
    # 로마제국:1000년, 몽골제국:200년, 오스만:600년
    empires = [10, 20, 60, 25, 30, 40, 50, 15, 35, 45, 5, 8, 12, 18, 28]
    valid = [n for n in empires if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 13: 산업혁명 전략
def industrial_revolution_strategy(data, round_num):
    """산업혁명 관련 연도"""
    # 1차:1760, 2차:1870, 3차:1970, 4차:2010
    industrial = [60, 70, 10, 65, 75, 80, 85, 90, 95, 0, 5, 15, 20, 25, 30]
    # 45 범위로
    mapped = [i % 45 + 1 if i > 45 else max(i, 1) for i in industrial]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 14: 종교 역사 전략
def religion_history_strategy(data, round_num):
    """종교 창시/전파 연도"""
    # 불교:BC563, 기독교:AD1, 이슬람:AD622
    religions = [63, 1, 22, 6, 4, 7, 10, 13, 16, 30, 33, 38, 40, 44, 45]
    valid = [n for n in religions if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 15: 발명 특허 전략
def invention_strategy(data, round_num):
    """주요 발명 연도"""
    # 전화:1876, 전구:1879, 비행기:1903, 컴퓨터:1946
    inventions = [76, 79, 3, 46, 37, 44, 85, 89, 95, 7, 13, 21, 28, 35, 40]
    # 45 범위로
    mapped = [i % 45 + 1 if i > 45 else i for i in inventions]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 16: 경제 위기 전략
def economic_crisis_strategy(data, round_num):
    """경제 위기 연도"""
    # 대공황:1929, IMF:1997, 금융위기:2008
    crises = [29, 97, 8, 73, 87, 90, 94, 1, 7, 11, 15, 20, 37, 38, 45]
    # 45 범위로
    mapped = [c % 45 + 1 if c > 45 else c for c in crises]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 17: 헌법/법률 전략
def constitution_strategy(data, round_num):
    """헌법 제정/개정 연도"""
    # 대한민국헌법:1948, 개정:1952,1960,1962,1969,1972,1980,1987
    constitution = [48, 52, 60, 62, 69, 72, 80, 87, 3, 5, 7, 15, 25, 35, 45]
    # 45 범위로
    mapped = [c % 45 + 1 if c > 45 else c for c in constitution]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 18: 예술 사조 전략
def art_movement_strategy(data, round_num):
    """예술 사조 연도"""
    # 르네상스:1400, 바로크:1600, 인상파:1870, 현대미술:1900
    art = [40, 60, 70, 0, 10, 20, 30, 50, 80, 90, 5, 15, 25, 35, 45]
    # 45 범위로
    mapped = [a % 45 + 1 if a > 45 else max(a, 1) for a in art]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 19: 철학자 생몰년 전략
def philosopher_strategy(data, round_num):
    """철학자 생몰년"""
    # 공자:BC551-479, 소크라테스:BC470-399, 칸트:1724-1804
    philosophers = [51, 79, 70, 99, 24, 4, 96, 83, 44, 18, 56, 31, 89, 16, 5]
    # 45 범위로
    mapped = [p % 45 + 1 if p > 45 else p for p in philosophers]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 20: 왕/황제 재위 전략
def monarch_reign_strategy(data, round_num):
    """왕/황제 재위 기간"""
    # 세종:32년, 영조:52년, 고종:44년
    reigns = [32, 52, 44, 46, 25, 15, 10, 7, 5, 3, 20, 27, 35, 40, 45]
    # 45 범위로
    mapped = [r % 45 + 1 if r > 45 else r for r in reigns]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))


STRATEGIES = {
    '한국_역사': korean_history_strategy,
    '세계_대전': world_war_strategy,
    '왕조_연대기': dynasty_strategy,
    '혁명_독립': revolution_strategy,
    '올림픽': olympics_strategy,
    '과학_발견': scientific_discovery_strategy,
    '인물_탄생년': birth_year_strategy,
    '전쟁_전투': battle_strategy,
    '문화유산': heritage_strategy,
    '조약_협정': treaty_strategy,
    '우주_탐사': space_exploration_strategy,
    '제국_연대': empire_strategy,
    '산업혁명': industrial_revolution_strategy,
    '종교_역사': religion_history_strategy,
    '발명_특허': invention_strategy,
    '경제_위기': economic_crisis_strategy,
    '헌법_법률': constitution_strategy,
    '예술_사조': art_movement_strategy,
    '철학자': philosopher_strategy,
    '왕_황제_재위': monarch_reign_strategy,
}

if __name__ == '__main__':
    print(f"역사 전략 {len(STRATEGIES)}개 로드됨")
