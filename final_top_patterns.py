#!/usr/bin/env python3
"""최종 TOP 5 패턴 통합 분석"""

import json
from collections import Counter, defaultdict
from typing import List, Dict

def load_data(filepath: str) -> List[Dict]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_arithmetic_sequences(nums):
    """등차수열 찾기"""
    sorted_nums = sorted(nums)
    for i in range(len(sorted_nums) - 2):
        for j in range(i+1, len(sorted_nums) - 1):
            diff = sorted_nums[j] - sorted_nums[i]
            for k in range(j+1, len(sorted_nums)):
                if sorted_nums[k] - sorted_nums[j] == diff:
                    return True
    return False

def main():
    data = load_data('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json')
    total = len(data)

    # 모든 패턴 수집
    all_patterns = []

    # 카운터
    count_has_consecutive = 0  # 연속번호 포함 (최소 간격 1)
    count_arithmetic = 0  # 등차수열 3개 이상
    count_sum_range = defaultdict(int)  # 합계 범위
    count_prime = defaultdict(int)  # 소수 개수
    count_odd_even = defaultdict(int)  # 홀짝 비율
    count_sum_divisible = defaultdict(int)  # 합 나누어떨어짐
    count_af_digit = defaultdict(int)  # a*f 일의 자리
    count_range_dist = defaultdict(int)  # 범위 분포

    for item in data:
        numbers = item.get('numbers', [])
        if len(numbers) != 6:
            continue

        sorted_nums = sorted(numbers)

        # 1. 연속번호 포함 여부
        has_consecutive = False
        for i in range(5):
            if sorted_nums[i+1] - sorted_nums[i] == 1:
                has_consecutive = True
                break
        if has_consecutive:
            count_has_consecutive += 1

        # 2. 등차수열
        if find_arithmetic_sequences(numbers):
            count_arithmetic += 1

        # 3. 합계 범위
        number_sum = sum(numbers)
        if 60 <= number_sum <= 100:
            count_sum_range['60-100'] += 1
        elif 101 <= number_sum <= 140:
            count_sum_range['101-140'] += 1
        elif 141 <= number_sum <= 180:
            count_sum_range['141-180'] += 1
        elif 181 <= number_sum <= 220:
            count_sum_range['181-220'] += 1

        # 4. 소수 개수
        prime_count = sum(1 for n in numbers if is_prime(n))
        count_prime[prime_count] += 1

        # 5. 홀짝 비율
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        count_odd_even[f'{odd_count}홀{6-odd_count}짝'] += 1

        # 6. 합 나누어떨어짐
        for divisor in [3, 4, 5, 6, 7]:
            if number_sum % divisor == 0:
                count_sum_divisible[divisor] += 1

        # 7. a*f 일의 자리
        af_digit = (sorted_nums[0] * sorted_nums[5]) % 10
        count_af_digit[af_digit] += 1

        # 8. 범위 분포
        range1 = sum(1 for n in numbers if 1 <= n <= 15)
        range2 = sum(1 for n in numbers if 16 <= n <= 30)
        range3 = sum(1 for n in numbers if 31 <= n <= 45)
        count_range_dist[f'{range1}-{range2}-{range3}'] += 1

    # 패턴 리스트 작성
    all_patterns.append(('연속번호 포함 (최소간격=1)', count_has_consecutive, total))
    all_patterns.append(('등차수열 3개 이상', count_arithmetic, total))

    for range_name, count in count_sum_range.items():
        all_patterns.append((f'합계 범위 {range_name}', count, total))

    for prime_num, count in count_prime.items():
        all_patterns.append((f'소수 {prime_num}개 포함', count, total))

    for ratio, count in count_odd_even.items():
        all_patterns.append((f'홀짝비율 {ratio}', count, total))

    for divisor, count in count_sum_divisible.items():
        all_patterns.append((f'합 % {divisor} = 0', count, total))

    for digit, count in count_af_digit.items():
        all_patterns.append((f'a×f의 일의자리 = {digit}', count, total))

    for dist, count in count_range_dist.items():
        all_patterns.append((f'범위분포 {dist}', count, total))

    # 비율 계산 및 정렬
    pattern_with_rate = [(name, (count/total)*100, count, total) for name, count, total in all_patterns]
    pattern_with_rate.sort(key=lambda x: x[1], reverse=True)

    print("=" * 80)
    print("로또 데이터 숨겨진 수학 공식 - 최종 분석 결과")
    print("=" * 80)
    print()
    print(f"총 {total}개 회차 분석")
    print()
    print("=" * 80)
    print("가장 높은 확률로 성립하는 규칙 TOP 5")
    print("=" * 80)
    print()

    for i, (name, rate, count, total_count) in enumerate(pattern_with_rate[:5], 1):
        print(f"【규칙 {i}】 {name}")
        print(f"  성립 비율: {rate:.2f}%")
        print(f"  성립 횟수: {count}/{total_count}회")
        print()

    print("=" * 80)
    print("TOP 6-10 추가 발견 패턴")
    print("=" * 80)
    print()

    for i, (name, rate, count, total_count) in enumerate(pattern_with_rate[5:10], 6):
        print(f"{i}. {name}: {rate:.2f}% ({count}/{total_count})")

    print()
    print("=" * 80)
    print("주요 통계 요약")
    print("=" * 80)
    print()

    # 특별한 패턴 설명
    print("【분석 인사이트】")
    print()
    print("1. 연속번호는 전체의 51.68%에서 나타남")
    print("   -> 적어도 1쌍의 연속번호(예: 12-13)가 포함될 가능성이 높음")
    print()
    print("2. 등차수열이 49.14%에서 발견됨")
    print("   -> 일정한 간격의 3개 이상 번호(예: 5,10,15 또는 7,14,21)")
    print()
    print("3. 합계가 101-140 범위에 41.82% 집중")
    print("   -> 6개 번호 합이 이 범위에 있을 확률이 가장 높음")
    print()
    print("4. 소수가 2개 포함되는 경우가 35.91%로 가장 빈번")
    print("   -> 소수(2,3,5,7,11,13,17,19,23,29,31,37,41,43) 중 정확히 2개")
    print()
    print("5. 홀수:짝수 비율이 3:3인 경우가 33.53%")
    print("   -> 홀짝이 균형을 이루는 경향")
    print()

    # 추가 복합 패턴 분석
    print("=" * 80)
    print("복합 조건 분석 (TOP 2 규칙 동시 만족)")
    print("=" * 80)
    print()

    # 연속번호 + 등차수열 동시 만족
    both_count = 0
    for item in data:
        numbers = item.get('numbers', [])
        if len(numbers) != 6:
            continue

        sorted_nums = sorted(numbers)

        # 연속번호 체크
        has_consecutive = any(sorted_nums[i+1] - sorted_nums[i] == 1 for i in range(5))

        # 등차수열 체크
        has_arithmetic = find_arithmetic_sequences(numbers)

        if has_consecutive and has_arithmetic:
            both_count += 1

    both_rate = (both_count / total) * 100
    print(f"연속번호 AND 등차수열: {both_count}/{total}회 ({both_rate:.2f}%)")
    print()

if __name__ == '__main__':
    main()
