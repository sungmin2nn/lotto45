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

def 역산_곱끝0(data, round_num):
    """역산_곱끝0: 첫번째*마지막 번호 곱의 끝자리가 0 (24.73% 적중)"""
    import random
    
    # a*f의 일의 자리가 0이 되려면:
    # a가 5의 배수이거나, f가 5의 배수이거나, 둘 다 짝수
    # 5의 배수: 5, 10, 15, 20, 25, 30, 35, 40, 45
    # 10의 배수: 10, 20, 30, 40
    
    mult_5 = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    mult_10 = [10, 20, 30, 40]
    evens = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44]
    
    max_attempts = 100
    for _ in range(max_attempts):
        # 방법 1: a를 5의 배수로 (작은 수)
        a = random.choice([5, 10, 15])
        # f를 큰 수로 (35-45)
        f = random.choice(range(35, 46))
        
        # 중간 번호 4개 선택
        middle_pool = [n for n in range(a+1, f) if n != a and n != f]
        if len(middle_pool) >= 4:
            middle = random.sample(middle_pool, 4)
            numbers = sorted([a] + middle + [f])
            
            # 검증: a*f 끝자리가 0인지
            if (numbers[0] * numbers[5]) % 10 == 0:
                return numbers
    
    # 실패시 기본 반환
    return sorted(random.sample(range(1, 46), 6))

USER_STRATEGIES['역산_곱끝0'] = 역산_곱끝0

def 역산_합7나머지(data, round_num):
    """역산_합7나머지: 6개 번호 합계 % 7 = 4 (15.53% 적중)"""
    import random
    
    # 6개 번호 합이 7로 나눈 나머지가 4가 되도록
    # 평균 합계 138 기준, 138 % 7 = 5이므로 목표 합계는 137, 130, 123... 또는 144, 151...
    # 합계 범위 120-160에서 % 7 = 4인 값: 123, 130, 137, 144, 151, 158
    
    target_sums = [123, 130, 137, 144, 151, 158]
    
    max_attempts = 200
    for _ in range(max_attempts):
        target = random.choice(target_sums)
        
        # 번호 6개 랜덤 선택
        numbers = sorted(random.sample(range(1, 46), 6))
        current_sum = sum(numbers)
        
        # 합계 조정 (번호 교체)
        diff = current_sum - target
        
        if diff == 0:
            return numbers
        
        # 간단한 조정: 합이 맞을 때까지 시도
        for adjust_try in range(50):
            idx = random.randint(0, 5)
            old_num = numbers[idx]
            
            # 새 번호 후보
            candidates = [n for n in range(1, 46) if n not in numbers]
            for new_num in candidates:
                new_sum = current_sum - old_num + new_num
                if new_sum % 7 == 4 and 100 <= new_sum <= 180:
                    numbers[idx] = new_num
                    return sorted(numbers)
    
    # 실패시 조건에 가장 가까운 결과 반환
    return sorted(random.sample(range(1, 46), 6))

USER_STRATEGIES['역산_합7나머지'] = 역산_합7나머지

def 역산_회차연계(data, round_num):
    """역산_회차연계: 회차%45 및 자릿수합 포함 (14.22% + 13.80%)"""
    import random
    
    # 회차 번호 % 45가 당첨번호에 포함 (14.22%)
    # 회차 자릿수 합도 포함 (13.80%)
    
    mod_45 = round_num % 45
    if mod_45 == 0:
        mod_45 = 45  # 0은 45로 대체
    
    # 회차 자릿수 합
    digit_sum = sum(int(d) for d in str(round_num))
    if digit_sum > 45:
        digit_sum = digit_sum % 45
    if digit_sum == 0:
        digit_sum = random.randint(1, 45)
    
    # 필수 포함 번호
    must_include = set()
    if 1 <= mod_45 <= 45:
        must_include.add(mod_45)
    if 1 <= digit_sum <= 45:
        must_include.add(digit_sum)
    
    numbers = list(must_include)
    
    # 나머지 번호 채우기 (균형있게)
    remaining_pool = [n for n in range(1, 46) if n not in numbers]
    
    while len(numbers) < 6:
        n = random.choice(remaining_pool)
        if n not in numbers:
            numbers.append(n)
            remaining_pool.remove(n)
    
    return sorted(numbers)[:6]

USER_STRATEGIES['역산_회차연계'] = 역산_회차연계

def 역산_통합(data, round_num):
    """역산_통합: 역산 규칙 3개 조합 (곱끝0 + 합%7=4 + 회차)"""
    import random
    
    # === 역산 분석 결과 규칙들 ===
    # 1. a*f의 일의 자리 = 0 (24.73%)
    # 2. 합계 % 7 = 4 (15.53%)
    # 3. 회차 % 45 포함 (14.22%)
    
    max_attempts = 500
    
    for _ in range(max_attempts):
        # 회차 기반 필수 번호
        mod_45 = round_num % 45
        if mod_45 == 0:
            mod_45 = 45
        
        # a*f 끝자리 0 조건: a는 5의 배수 소수, f는 짝수
        a_candidates = [5, 10, 15]  # 작은 5의 배수
        f_candidates = [40, 42, 44, 45, 36, 38]  # 큰 수 중 a*f 끝자리 0 만들 수 있는 것
        
        a = random.choice(a_candidates)
        f = random.choice(f_candidates)
        
        # a*f 끝자리 0 확인
        if (a * f) % 10 != 0:
            continue
        
        # 중간 번호 선택 (mod_45 포함 시도)
        middle_pool = [n for n in range(a+1, f) if n != mod_45]
        
        if mod_45 > a and mod_45 < f:
            middle = [mod_45]
            remaining = random.sample(middle_pool, min(3, len(middle_pool)))
            middle.extend(remaining)
        else:
            middle = random.sample(middle_pool, min(4, len(middle_pool)))
        
        numbers = sorted([a] + middle[:4] + [f])
        
        if len(numbers) != 6:
            continue
        
        # 합계 % 7 = 4 확인
        if sum(numbers) % 7 == 4:
            return numbers
    
    # 조건 완화: a*f 끝자리 0만 만족
    for _ in range(100):
        a = random.choice([5, 10, 15])
        f = random.choice([40, 42, 44, 45])
        if (a * f) % 10 != 0:
            continue
        
        middle_pool = [n for n in range(a+1, f)]
        middle = random.sample(middle_pool, 4)
        return sorted([a] + middle + [f])
    
    return sorted(random.sample(range(1, 46), 6))

USER_STRATEGIES['역산_통합'] = 역산_통합
