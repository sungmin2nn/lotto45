#!/usr/bin/env python3
"""TOP 5 패턴의 실제 예시 출력"""

import json
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
    sorted_nums = sorted(nums)
    sequences = []
    for i in range(len(sorted_nums) - 2):
        for j in range(i+1, len(sorted_nums) - 1):
            diff = sorted_nums[j] - sorted_nums[i]
            for k in range(j+1, len(sorted_nums)):
                if sorted_nums[k] - sorted_nums[j] == diff:
                    sequences.append((sorted_nums[i], sorted_nums[j], sorted_nums[k], diff))
    return sequences

def main():
    data = load_data('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json')

    print("=" * 80)
    print("TOP 5 패턴의 실제 당첨 사례")
    print("=" * 80)
    print()

    # 규칙 1: 연속번호
    print("【규칙 1】 연속번호 포함 (성립률 51.68%)")
    print("-" * 80)
    consecutive_examples = []
    for item in data[:100]:  # 최근 100개만 검사
        numbers = item.get('numbers', [])
        round_num = item.get('round', 0)
        if len(numbers) != 6:
            continue

        sorted_nums = sorted(numbers)
        consecutive_pairs = []
        for i in range(5):
            if sorted_nums[i+1] - sorted_nums[i] == 1:
                consecutive_pairs.append((sorted_nums[i], sorted_nums[i+1]))

        if consecutive_pairs and len(consecutive_examples) < 5:
            consecutive_examples.append((round_num, sorted_nums, consecutive_pairs))

    for round_num, nums, pairs in consecutive_examples:
        print(f"  {round_num}회: {nums}")
        print(f"    -> 연속쌍: {pairs}")
    print()

    # 규칙 2: 등차수열
    print("【규칙 2】 등차수열 3개 이상 (성립률 49.14%)")
    print("-" * 80)
    arithmetic_examples = []
    for item in data[:200]:
        numbers = item.get('numbers', [])
        round_num = item.get('round', 0)
        if len(numbers) != 6:
            continue

        sequences = find_arithmetic_sequences(numbers)
        if sequences and len(arithmetic_examples) < 5:
            arithmetic_examples.append((round_num, sorted(numbers), sequences))

    for round_num, nums, seqs in arithmetic_examples:
        print(f"  {round_num}회: {nums}")
        for seq in seqs[:2]:  # 최대 2개만 표시
            print(f"    -> 등차수열: {seq[0]}, {seq[1]}, {seq[2]} (공차={seq[3]})")
    print()

    # 규칙 3: 합계 범위 101-140
    print("【규칙 3】 합계 범위 101-140 (성립률 41.82%)")
    print("-" * 80)
    sum_range_examples = []
    for item in data[:100]:
        numbers = item.get('numbers', [])
        round_num = item.get('round', 0)
        if len(numbers) != 6:
            continue

        number_sum = sum(numbers)
        if 101 <= number_sum <= 140 and len(sum_range_examples) < 5:
            sum_range_examples.append((round_num, sorted(numbers), number_sum))

    for round_num, nums, total in sum_range_examples:
        print(f"  {round_num}회: {nums}")
        print(f"    -> 합계: {total}")
    print()

    # 규칙 4: 합계 범위 141-180
    print("【규칙 4】 합계 범위 141-180 (성립률 37.72%)")
    print("-" * 80)
    sum_range2_examples = []
    for item in data[:100]:
        numbers = item.get('numbers', [])
        round_num = item.get('round', 0)
        if len(numbers) != 6:
            continue

        number_sum = sum(numbers)
        if 141 <= number_sum <= 180 and len(sum_range2_examples) < 5:
            sum_range2_examples.append((round_num, sorted(numbers), number_sum))

    for round_num, nums, total in sum_range2_examples:
        print(f"  {round_num}회: {nums}")
        print(f"    -> 합계: {total}")
    print()

    # 규칙 5: 소수 2개
    print("【규칙 5】 소수 2개 포함 (성립률 35.91%)")
    print("-" * 80)
    prime_examples = []
    for item in data[:100]:
        numbers = item.get('numbers', [])
        round_num = item.get('round', 0)
        if len(numbers) != 6:
            continue

        primes = [n for n in numbers if is_prime(n)]
        if len(primes) == 2 and len(prime_examples) < 5:
            prime_examples.append((round_num, sorted(numbers), primes))

    for round_num, nums, primes in prime_examples:
        print(f"  {round_num}회: {nums}")
        print(f"    -> 소수: {sorted(primes)}")
    print()

    print("=" * 80)
    print("복합 패턴 사례 (여러 규칙 동시 만족)")
    print("=" * 80)
    print()

    # 3개 이상 규칙 동시 만족
    multi_pattern_examples = []
    for item in data[:200]:
        numbers = item.get('numbers', [])
        round_num = item.get('round', 0)
        if len(numbers) != 6:
            continue

        sorted_nums = sorted(numbers)
        matched_rules = []

        # 연속번호
        has_consecutive = any(sorted_nums[i+1] - sorted_nums[i] == 1 for i in range(5))
        if has_consecutive:
            matched_rules.append("연속번호")

        # 등차수열
        if find_arithmetic_sequences(numbers):
            matched_rules.append("등차수열")

        # 합계 범위
        number_sum = sum(numbers)
        if 101 <= number_sum <= 140:
            matched_rules.append("합계101-140")
        elif 141 <= number_sum <= 180:
            matched_rules.append("합계141-180")

        # 소수 2개
        primes = [n for n in numbers if is_prime(n)]
        if len(primes) == 2:
            matched_rules.append("소수2개")

        # 홀짝 3:3
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        if odd_count == 3:
            matched_rules.append("홀짝3:3")

        if len(matched_rules) >= 3 and len(multi_pattern_examples) < 5:
            multi_pattern_examples.append((round_num, sorted_nums, matched_rules))

    for round_num, nums, rules in multi_pattern_examples:
        print(f"{round_num}회: {nums}")
        print(f"  만족 규칙 ({len(rules)}개): {', '.join(rules)}")
        print()

if __name__ == '__main__':
    main()
