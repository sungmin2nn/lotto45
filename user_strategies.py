#!/usr/bin/env python3
"""사용자 정의 전략 모음"""
import random

USER_STRATEGIES = {}


def strategy_3의_배수(data, round_num):
    """3의_배수: 3의 배수 번호 중심 선택 전략"""
    # 3의 배수 번호 중심 선택
    multiples_of_3 = [n for n in range(3, 46, 3)]  # [3,6,9,...,45]
    others = [n for n in range(1, 46) if n % 3 != 0]

    # 3의 배수 4개 + 나머지 2개
    selected = random.sample(multiples_of_3, 4)
    selected += random.sample(others, 2)
    return sorted(selected)

USER_STRATEGIES['3의_배수'] = strategy_3의_배수

def 궁합_조합(data, round_num):
    """궁합_조합: 1217회차 분석 결과 강력한 궁합 조합 기반"""
    # 분석 결과 강력한 궁합 조합들
    strong_pairs = [
        (11, 21),  # 34회 (2.79%)
        (33, 40),  # 33회 (2.71%)
        (6, 38),   # 31회 (2.55%)
        (10, 31),  # 30회 (2.47%)
        (12, 24),  # 30회 (2.47%)
        (37, 40),  # 29회 (2.38%)
        (14, 15),  # 29회 (2.38%)
        (19, 21),  # 29회 (2.38%)
        (3, 13),   # 29회 (2.38%)
        (1, 28),   # 29회 (2.38%)
    ]
    
    # 랜덤하게 2-3개의 궁합 조합 선택
    import random
    selected_pairs = random.sample(strong_pairs, random.choice([2, 3]))
    
    # 선택된 조합에서 번호 추출
    numbers = set()
    for pair in selected_pairs:
        numbers.add(pair[0])
        numbers.add(pair[1])
    
    # 6개가 될 때까지 나머지 번호 추가 (고빈도 번호 중심)
    hot_numbers = [34, 27, 12, 13, 33, 40, 45, 18, 37, 14]
    for n in hot_numbers:
        if len(numbers) >= 6:
            break
        if n not in numbers:
            numbers.add(n)
    
    # 6개가 안되면 랜덤 추가
    while len(numbers) < 6:
        numbers.add(random.randint(1, 45))
    
    return sorted(list(numbers))[:6]

USER_STRATEGIES['궁합_조합'] = 궁합_조합

def 균형_분포(data, round_num):
    """균형_분포: 합계/홀짝/10단위 균형 분포 기반"""
    import random
    
    # 분석 결과 기반 최적 조건
    # 1. 합계: 121-180 (63.57% 출현)
    # 2. 홀짝: 3:3 (33.53%) 또는 4:2/2:4 (48.9%)
    # 3. 10단위: 각 구간에서 1-2개
    
    max_attempts = 100
    
    for _ in range(max_attempts):
        # 각 10단위 구간에서 선택
        decade_1_10 = random.sample(range(1, 11), random.choice([1, 2]))    # 1-10
        decade_11_20 = random.sample(range(11, 21), random.choice([1, 2]))  # 11-20  
        decade_21_30 = random.sample(range(21, 31), random.choice([1, 2]))  # 21-30
        decade_31_40 = random.sample(range(31, 41), random.choice([1, 1, 2]))  # 31-40
        decade_41_45 = random.sample(range(41, 46), random.choice([0, 1]))  # 41-45
        
        # 번호 합치기
        all_nums = decade_1_10 + decade_11_20 + decade_21_30 + decade_31_40 + decade_41_45
        
        # 6개 선택
        if len(all_nums) >= 6:
            numbers = sorted(random.sample(all_nums, 6))
        else:
            # 부족하면 추가
            remaining = list(set(range(1, 46)) - set(all_nums))
            numbers = sorted(all_nums + random.sample(remaining, 6 - len(all_nums)))
        
        # 조건 검증
        total_sum = sum(numbers)
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        
        # 합계 121-180, 홀짝 2-4개
        if 121 <= total_sum <= 180 and 2 <= odd_count <= 4:
            return numbers
    
    # 조건 만족 못하면 마지막 결과 반환
    return numbers

USER_STRATEGIES['균형_분포'] = 균형_분포

def HOT_연속회피(data, round_num):
    """HOT_연속회피: 최근 고빈도 번호 + 직전회차 회피 조합"""
    import random
    from collections import Counter
    
    # 최근 10회차에서 가장 많이 나온 번호 (HOT)
    recent = data[-10:] if len(data) >= 10 else data
    freq = Counter()
    for d in recent:
        freq.update(d['numbers'])
    
    hot_nums = [n for n, _ in freq.most_common(15)]
    
    # 직전 회차 번호 (회피 대상 - 평균 0.83개만 반복되므로)
    last_nums = set(data[-1]['numbers']) if data else set()
    
    # HOT 번호 중 직전 회차에 없는 것들 선호
    preferred = [n for n in hot_nums if n not in last_nums]
    avoided = [n for n in hot_nums if n in last_nums]
    
    # 4-5개는 preferred에서, 1-2개는 avoided에서
    numbers = set()
    
    # preferred에서 4-5개
    take_from_preferred = min(len(preferred), random.choice([4, 5]))
    numbers.update(random.sample(preferred, take_from_preferred))
    
    # 나머지는 avoided 또는 전체 번호에서
    remaining_pool = list(set(range(1, 46)) - numbers)
    while len(numbers) < 6:
        if avoided and random.random() < 0.3:  # 30% 확률로 직전 번호 포함
            n = random.choice(avoided)
            if n not in numbers:
                numbers.add(n)
        else:
            n = random.choice(remaining_pool)
            if n not in numbers:
                numbers.add(n)
    
    return sorted(list(numbers))[:6]

USER_STRATEGIES['HOT_연속회피'] = HOT_연속회피

def 통합_분석(data, round_num):
    """통합_분석: 궁합+고빈도+조건부확률+합계범위 통합"""
    import random
    from collections import Counter
    
    # === 핵심 패턴 데이터 ===
    # 1. 강력한 궁합 조합 (상위 5개)
    strong_pairs = [(11,21), (33,40), (6,38), (10,31), (12,24)]
    
    # 2. 고빈도 번호 TOP 10
    hot_numbers = [34, 27, 12, 13, 33, 40, 45, 18, 37, 14]
    
    # 3. 연속 회피 (직전 회차)
    last_nums = set(data[-1]['numbers']) if data else set()
    
    # 4. 조건부 확률 높은 조합
    conditional_pairs = {
        33: [40],  # 33이 나오면 40이 19% 확률
        40: [33, 37],
        14: [15],  # 17% 확률
        12: [24],  # 17% 확률
    }
    
    numbers = set()
    
    # Step 1: 강력한 궁합 조합 1개 선택 (40%)
    if random.random() < 0.4:
        pair = random.choice(strong_pairs)
        numbers.add(pair[0])
        numbers.add(pair[1])
    
    # Step 2: 고빈도 번호 중 직전 회차에 없는 것 2-3개 추가
    available_hot = [n for n in hot_numbers if n not in last_nums and n not in numbers]
    take = min(len(available_hot), random.choice([2, 3]))
    numbers.update(random.sample(available_hot, take) if available_hot else [])
    
    # Step 3: 조건부 확률 활용 (이미 선택된 번호의 궁합 추가)
    for num in list(numbers):
        if num in conditional_pairs and len(numbers) < 6:
            companion = random.choice(conditional_pairs[num])
            if companion not in numbers:
                numbers.add(companion)
    
    # Step 4: 나머지는 전체 번호에서 균형있게 선택 (합계 121-180)
    all_nums = list(range(1, 46))
    max_attempts = 50
    for _ in range(max_attempts):
        if len(numbers) >= 6:
            break
        remaining = [n for n in all_nums if n not in numbers]
        candidate = random.choice(remaining)
        test_nums = sorted(list(numbers) + [candidate])
        if len(test_nums) <= 6:
            test_sum = sum(test_nums)
            # 합계가 너무 크거나 작으면 패스
            expected_sum = 138  # 평균
            if len(test_nums) < 6 or 100 <= test_sum <= 200:
                numbers.add(candidate)
    
    # 6개 미만이면 랜덤 추가
    while len(numbers) < 6:
        n = random.randint(1, 45)
        if n not in numbers:
            numbers.add(n)
    
    return sorted(list(numbers))[:6]

USER_STRATEGIES['통합_분석'] = 통합_분석
