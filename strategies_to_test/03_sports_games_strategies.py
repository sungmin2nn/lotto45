"""
스포츠/게임 기반 전략 (20개)
"""
import json
import random
from collections import Counter
from datetime import datetime

with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

def get_all_numbers(data, end_round):
    numbers = []
    for item in data:
        if item['round'] < end_round:
            numbers.extend(item['numbers'])
    return numbers

def get_recent_numbers(data, end_round, n_rounds=10):
    numbers = []
    for item in data:
        if end_round - n_rounds <= item['round'] < end_round:
            numbers.extend(item['numbers'])
    return numbers

# 전략 1: 축구 등번호 전략
def soccer_jersey_strategy(data, round_num):
    """유명 축구선수 등번호"""
    famous = [7, 10, 9, 11, 23, 8, 6, 4, 5, 1, 21, 17, 14, 22, 30]
    return sorted(random.sample(famous, 6))

# 전략 2: 농구 등번호 전략
def basketball_jersey_strategy(data, round_num):
    """유명 농구선수 등번호"""
    famous = [23, 24, 33, 32, 11, 3, 6, 1, 13, 21, 34, 15, 7, 45, 12]
    valid = [n for n in famous if n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 3: 야구 등번호 전략
def baseball_jersey_strategy(data, round_num):
    """유명 야구선수 등번호"""
    famous = [42, 3, 4, 5, 21, 24, 31, 44, 27, 14, 17, 99, 25, 36]
    valid = [n for n in famous if n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 4: 골프 전략
def golf_strategy(data, round_num):
    """골프 점수 관련 숫자"""
    # 파(3,4,5), 홀 수(1-18), 우승 점수대(-20 ~ -10)
    golf_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    return sorted(random.sample(golf_nums, 6))

# 전략 5: 체스 전략
def chess_strategy(data, round_num):
    """체스판 좌표 기반"""
    # 8x8 = 64칸, 1-45만 사용
    chess_moves = []
    for row in range(1, 9):
        for col in range(1, 9):
            pos = (row - 1) * 8 + col
            if 1 <= pos <= 45:
                chess_moves.append(pos)
    return sorted(random.sample(chess_moves, 6))

# 전략 6: 포커 전략
def poker_strategy(data, round_num):
    """포커 카드 값 기반"""
    # A=1, 2-10, J=11, Q=12, K=13 (4벌)
    cards = list(range(1, 14)) * 3 + list(range(14, 46))
    valid = [n for n in cards if 1 <= n <= 45]
    return sorted(random.sample(list(set(valid)), 6))

# 전략 7: 주사위 전략
def dice_strategy(data, round_num):
    """주사위 합 패턴"""
    # 여러 주사위 합의 조합
    dice_sums = []
    for i in range(1, 7):
        for j in range(1, 7):
            s = i + j
            if 1 <= s <= 45:
                dice_sums.append(s)
    for i in range(1, 7):
        for j in range(1, 7):
            for k in range(1, 7):
                s = i + j + k
                if 1 <= s <= 45:
                    dice_sums.append(s)

    valid = list(set(dice_sums))
    return sorted(random.sample(valid, 6))

# 전략 8: 볼링 전략
def bowling_strategy(data, round_num):
    """볼링 점수 관련"""
    # 스트라이크=10, 스페어, 프레임 점수
    bowling_nums = [10, 20, 30, 40, 9, 18, 27, 36, 45, 8, 16, 24, 32]
    valid = [n for n in bowling_nums if 1 <= n <= 45]
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))
    return sorted(random.sample(valid, 6))

# 전략 9: 당구 전략
def billiards_strategy(data, round_num):
    """당구공 번호"""
    # 1-15번 공
    balls = list(range(1, 16))
    # 3쿠션 점수대
    balls += [21, 24, 27, 30, 33, 36]
    valid = [n for n in balls if 1 <= n <= 45]
    return sorted(random.sample(list(set(valid)), 6))

# 전략 10: 마라톤 전략
def marathon_strategy(data, round_num):
    """마라톤 기록 관련 숫자"""
    # 42.195km, 하프 21.1km, 구간 시간
    marathon = [42, 21, 10, 5, 2, 1, 35, 30, 25, 15, 40, 45, 20, 3]
    valid = [n for n in marathon if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 11: 수영 전략
def swimming_strategy(data, round_num):
    """수영 레인 및 거리"""
    # 레인 1-8, 거리 50/100/200/400/800/1500
    swim = [1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20, 25, 40, 44, 50]
    valid = [n for n in swim if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 12: 테니스 전략
def tennis_strategy(data, round_num):
    """테니스 점수 체계"""
    # 0, 15, 30, 40, 게임/세트
    tennis = [0, 15, 30, 40, 1, 2, 3, 4, 5, 6, 7, 10, 12, 13]
    valid = [n for n in tennis if 1 <= n <= 45]
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))
    return sorted(random.sample(valid, 6))

# 전략 13: 배구 전략
def volleyball_strategy(data, round_num):
    """배구 점수"""
    # 세트당 25점, 5세트 15점, 포지션
    volley = [25, 15, 21, 1, 2, 3, 4, 5, 6, 10, 11, 12, 20, 30]
    valid = [n for n in volley if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 14: 럭비 전략
def rugby_strategy(data, round_num):
    """럭비 점수 체계"""
    # 트라이 5점, 컨버전 2점, 페널티 3점
    rugby = [5, 7, 10, 12, 14, 15, 17, 19, 21, 24, 26, 28, 31, 33, 35, 38, 40, 42, 45]
    valid = [n for n in rugby if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 15: 복싱 전략
def boxing_strategy(data, round_num):
    """복싱 라운드 및 체급"""
    # 12라운드, 체급 무게
    boxing = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 45, 40, 35, 30, 25, 20]
    valid = [n for n in boxing if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 16: 탁구 전략
def pingpong_strategy(data, round_num):
    """탁구 점수"""
    # 11점제, 게임수
    pingpong = [11, 1, 2, 3, 4, 5, 6, 7, 9, 10, 21, 22, 33, 44]
    valid = [n for n in pingpong if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 17: 바둑 전략
def baduk_strategy(data, round_num):
    """바둑판 좌표"""
    # 19x19, 화점 위치
    baduk = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43]
    valid = [n for n in baduk if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 18: F1 전략
def f1_strategy(data, round_num):
    """F1 레이싱 번호"""
    # 유명 드라이버 번호
    f1 = [1, 3, 4, 5, 7, 10, 11, 14, 16, 18, 22, 23, 27, 33, 44, 55, 63, 77, 81]
    valid = [n for n in f1 if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 19: 스케이트보드 전략
def skateboard_strategy(data, round_num):
    """스케이트보드 트릭 각도"""
    # 180, 360, 540, 720 -> 18, 36, 54, 72 % 45
    angles = [18, 36, 9, 27, 45, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40]
    valid = [n for n in angles if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 20: e스포츠 전략
def esports_strategy(data, round_num):
    """e스포츠 관련 숫자"""
    # 팀원 5명, 맵, 라운드
    esports = [5, 10, 15, 16, 20, 25, 30, 1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 24, 32]
    valid = [n for n in esports if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))


# 전략 목록
STRATEGIES = {
    '축구_등번호': soccer_jersey_strategy,
    '농구_등번호': basketball_jersey_strategy,
    '야구_등번호': baseball_jersey_strategy,
    '골프': golf_strategy,
    '체스': chess_strategy,
    '포커': poker_strategy,
    '주사위': dice_strategy,
    '볼링': bowling_strategy,
    '당구': billiards_strategy,
    '마라톤': marathon_strategy,
    '수영': swimming_strategy,
    '테니스': tennis_strategy,
    '배구': volleyball_strategy,
    '럭비': rugby_strategy,
    '복싱': boxing_strategy,
    '탁구': pingpong_strategy,
    '바둑': baduk_strategy,
    'F1_레이싱': f1_strategy,
    '스케이트보드': skateboard_strategy,
    'e스포츠': esports_strategy,
}

if __name__ == '__main__':
    print(f"스포츠/게임 전략 {len(STRATEGIES)}개 로드됨")
    for name in STRATEGIES.keys():
        print(f"  - {name}")
