"""
심리학/인지과학 기반 전략 (20개)
"""
import json
import random
from collections import Counter
from datetime import datetime

# 데이터 로드
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

# 전략 1: 행운의 숫자 전략 (7, 8, 9 선호)
def lucky_numbers_strategy(data, round_num):
    """문화적으로 행운으로 여겨지는 숫자 기반"""
    # 7, 8은 동서양 모두 행운의 숫자
    lucky = [7, 8, 17, 18, 27, 28, 37, 38]
    # 9는 동양에서 완전수
    lucky += [9, 19, 29, 39]

    selected = random.sample(lucky, min(4, len(lucky)))

    # 나머지는 랜덤
    remaining = [n for n in range(1, 46) if n not in selected]
    selected += random.sample(remaining, 6 - len(selected))

    return sorted(selected)

# 전략 2: 불행의 숫자 회피 전략
def avoid_unlucky_strategy(data, round_num):
    """4, 13 등 불행의 숫자 회피"""
    unlucky = {4, 13, 14, 24, 34, 44}  # 4가 들어간 숫자
    candidates = [n for n in range(1, 46) if n not in unlucky]
    return sorted(random.sample(candidates, 6))

# 전략 3: 생일 편향 역이용 전략
def birthday_bias_inverse_strategy(data, round_num):
    """사람들이 생일(1-31)을 선호하므로 32-45 강조"""
    # 32-45에서 4개, 1-31에서 2개
    high = random.sample(range(32, 46), 4)
    low = random.sample(range(1, 32), 2)
    return sorted(high + low)

# 전략 4: 인지 편향 활용 전략
def cognitive_bias_strategy(data, round_num):
    """최근 본 숫자를 선호하는 가용성 휴리스틱"""
    recent = get_recent_numbers(data, round_num, 3)
    if len(set(recent)) >= 6:
        return sorted(random.sample(list(set(recent)), 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 5: 도박사의 오류 전략
def gamblers_fallacy_strategy(data, round_num):
    """오랫동안 안나온 번호가 나올 차례라는 오류 활용"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    # 가장 적게 나온 번호들
    least_common = counter.most_common()[-15:]
    candidates = [n for n, _ in least_common]

    if len(candidates) >= 6:
        return sorted(random.sample(candidates, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 6: 핫핸드 오류 전략
def hot_hand_fallacy_strategy(data, round_num):
    """최근 자주 나온 번호가 계속 나올 것이라는 오류"""
    recent = get_recent_numbers(data, round_num, 5)
    if not recent:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(recent)
    hot = [n for n, _ in counter.most_common(10)]

    if len(hot) >= 6:
        return sorted(random.sample(hot, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 7: 프레이밍 효과 전략
def framing_effect_strategy(data, round_num):
    """번호를 그룹으로 프레이밍"""
    # 1-15를 "저", 16-30을 "중", 31-45를 "고"로 프레이밍
    # 균형잡힌 포트폴리오 구성
    low = random.sample(range(1, 16), 2)
    mid = random.sample(range(16, 31), 2)
    high = random.sample(range(31, 46), 2)
    return sorted(low + mid + high)

# 전략 8: 앵커링 효과 전략
def anchoring_strategy(data, round_num):
    """이전 당첨번호를 앵커로 사용"""
    for item in data:
        if item['round'] == round_num - 1:
            anchor = item['numbers']
            # 앵커 근처에서 선택
            candidates = set()
            for n in anchor:
                for offset in range(-3, 4):
                    num = n + offset
                    if 1 <= num <= 45:
                        candidates.add(num)
            if len(candidates) >= 6:
                return sorted(random.sample(list(candidates), 6))

    return sorted(random.sample(range(1, 46), 6))

# 전략 9: 패턴 인식 편향 전략
def pattern_seeking_strategy(data, round_num):
    """인간의 패턴 찾기 본능 활용"""
    # 등차수열 패턴
    start = random.randint(1, 10)
    diff = random.randint(5, 7)
    pattern = [start + i*diff for i in range(6)]
    pattern = [n for n in pattern if 1 <= n <= 45]

    while len(pattern) < 6:
        new = random.randint(1, 45)
        if new not in pattern:
            pattern.append(new)

    return sorted(pattern[:6])

# 전략 10: 확증 편향 전략
def confirmation_bias_strategy(data, round_num):
    """특정 가설을 확증하는 번호 선택"""
    # 가설: 짝수와 홀수가 3:3으로 나온다
    evens = random.sample([n for n in range(2, 46, 2)], 3)
    odds = random.sample([n for n in range(1, 46, 2)], 3)
    return sorted(evens + odds)

# 전략 11: 손실 회피 전략
def loss_aversion_strategy(data, round_num):
    """손실 회피 - 중간값 위주 선택"""
    # 극단적인 값(1-5, 41-45) 회피
    safe_range = list(range(6, 41))
    return sorted(random.sample(safe_range, 6))

# 전략 12: 현상 유지 편향 전략
def status_quo_strategy(data, round_num):
    """변화를 싫어하는 편향 - 자주 나오는 번호 유지"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    most_common = [n for n, _ in counter.most_common(15)]
    return sorted(random.sample(most_common, 6))

# 전략 13: 군중 심리 역이용 전략
def contrarian_crowd_strategy(data, round_num):
    """군중이 피하는 번호 선택"""
    # 사람들이 잘 안고르는 번호 (4, 13 포함, 큰 숫자)
    unpopular = [4, 13, 14, 34, 40, 41, 42, 43, 44, 45]
    selected = random.sample(unpopular, min(4, len(unpopular)))

    remaining = [n for n in range(1, 46) if n not in selected]
    selected += random.sample(remaining, 6 - len(selected))

    return sorted(selected)

# 전략 14: 초두 효과 전략
def primacy_effect_strategy(data, round_num):
    """처음 본 것을 기억하는 효과 - 낮은 번호 선호"""
    return sorted(random.sample(range(1, 25), 6))

# 전략 15: 최신 효과 전략
def recency_effect_strategy(data, round_num):
    """최근 것을 기억하는 효과 - 높은 번호 선호"""
    return sorted(random.sample(range(21, 46), 6))

# 전략 16: 선택적 기억 전략
def selective_memory_strategy(data, round_num):
    """당첨됐던 특별한 번호만 기억"""
    # 연속으로 나왔던 번호들 추적
    consecutive_appeared = set()
    prev_nums = None
    for item in data:
        if item['round'] < round_num:
            if prev_nums:
                repeated = set(prev_nums) & set(item['numbers'])
                consecutive_appeared.update(repeated)
            prev_nums = item['numbers']

    if len(consecutive_appeared) >= 6:
        return sorted(random.sample(list(consecutive_appeared), 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 17: 대표성 휴리스틱 전략
def representativeness_strategy(data, round_num):
    """'전형적인' 당첨 번호 조합 추구"""
    # 전형적: 낮은것, 중간것, 높은것 골고루
    typical = []
    typical.append(random.randint(1, 10))    # 한자리
    typical.append(random.randint(11, 20))   # 10대
    typical.append(random.randint(21, 25))   # 20대 초
    typical.append(random.randint(26, 30))   # 20대 후
    typical.append(random.randint(31, 38))   # 30대
    typical.append(random.randint(39, 45))   # 40대

    return sorted(typical)

# 전략 18: 매몰비용 전략
def sunk_cost_strategy(data, round_num):
    """이전에 선택했던 번호 유지 (매몰비용 오류)"""
    # 가장 최근 당첨번호 중 일부 유지
    for item in data:
        if item['round'] == round_num - 1:
            keep = random.sample(item['numbers'], 3)
            new = random.sample([n for n in range(1, 46) if n not in keep], 3)
            return sorted(keep + new)

    return sorted(random.sample(range(1, 46), 6))

# 전략 19: 자기과신 전략
def overconfidence_strategy(data, round_num):
    """자기만의 '시스템'에 대한 과신"""
    # 본인만의 규칙: 소수 + 7의 배수
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
    sevens = [7, 14, 21, 28, 35, 42]

    pool = list(set(primes + sevens))
    return sorted(random.sample(pool, 6))

# 전략 20: 공정성 오류 전략
def fairness_fallacy_strategy(data, round_num):
    """모든 번호가 공정하게 나와야 한다는 오류"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    avg = sum(counter.values()) / 45

    # 평균 이하로 나온 번호들 (곧 나와야 할 차례)
    below_avg = [n for n in range(1, 46) if counter.get(n, 0) < avg]

    if len(below_avg) >= 6:
        return sorted(random.sample(below_avg, 6))
    return sorted(random.sample(range(1, 46), 6))


# 전략 목록
STRATEGIES = {
    '행운의_숫자': lucky_numbers_strategy,
    '불행_회피': avoid_unlucky_strategy,
    '생일_편향_역이용': birthday_bias_inverse_strategy,
    '인지_편향': cognitive_bias_strategy,
    '도박사_오류': gamblers_fallacy_strategy,
    '핫핸드_오류': hot_hand_fallacy_strategy,
    '프레이밍_효과': framing_effect_strategy,
    '앵커링_효과': anchoring_strategy,
    '패턴_인식': pattern_seeking_strategy,
    '확증_편향': confirmation_bias_strategy,
    '손실_회피': loss_aversion_strategy,
    '현상_유지': status_quo_strategy,
    '군중_역이용': contrarian_crowd_strategy,
    '초두_효과': primacy_effect_strategy,
    '최신_효과': recency_effect_strategy,
    '선택적_기억': selective_memory_strategy,
    '대표성_휴리스틱': representativeness_strategy,
    '매몰비용': sunk_cost_strategy,
    '자기과신': overconfidence_strategy,
    '공정성_오류': fairness_fallacy_strategy,
}

if __name__ == '__main__':
    print(f"심리학 전략 {len(STRATEGIES)}개 로드됨")
    for name in STRATEGIES.keys():
        print(f"  - {name}")
