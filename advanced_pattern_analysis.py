#!/usr/bin/env python3
"""로또 데이터에서 고급 수학적 패턴 분석"""

import json
from collections import Counter
from typing import List, Dict, Tuple

def load_data(filepath: str) -> List[Dict]:
    """로또 데이터 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_advanced_patterns(data: List[Dict]) -> Dict:
    """고급 패턴 분석"""

    total = len(data)
    patterns = []

    # 패턴별 카운터
    counters = {
        'consecutive_count': Counter(),  # 연속 번호 개수
        'prime_count': Counter(),  # 소수 개수
        'odd_even_ratio': Counter(),  # 홀짝 비율
        'range_distribution': Counter(),  # 범위별 분포 (1-15, 16-30, 31-45)
        'digit_sum_mod': Counter(),  # 각 번호 자릿수 합의 합
        'number_sum_range': [],  # 번호 합계
        'max_gap': [],  # 최대 간격
        'min_gap': [],  # 최소 간격
        'avg_gap': [],  # 평균 간격
        'sum_divisible_by': defaultdict(int),  # 합이 특정 수로 나누어떨어짐
        'all_different_tens': 0,  # 모든 번호의 십의 자리가 다름
        'arithmetic_sequence': 0,  # 등차수열 3개 이상
        'geometric_pattern': 0,  # 배수 관계
    }

    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    def find_consecutive(nums):
        """연속 번호 개수 찾기"""
        count = 0
        sorted_nums = sorted(nums)
        for i in range(len(sorted_nums) - 1):
            if sorted_nums[i+1] - sorted_nums[i] == 1:
                count += 1
        return count

    def find_arithmetic_sequences(nums):
        """등차수열 찾기 (3개 이상)"""
        sorted_nums = sorted(nums)
        for i in range(len(sorted_nums) - 2):
            for j in range(i+1, len(sorted_nums) - 1):
                diff = sorted_nums[j] - sorted_nums[i]
                for k in range(j+1, len(sorted_nums)):
                    if sorted_nums[k] - sorted_nums[j] == diff:
                        return True
        return False

    prev_numbers = None

    for item in data:
        numbers = item.get('numbers', [])
        if len(numbers) != 6:
            continue

        sorted_nums = sorted(numbers)

        # 1. 연속 번호
        consecutive = find_consecutive(numbers)
        counters['consecutive_count'][consecutive] += 1

        # 2. 소수 개수
        prime_count = sum(1 for n in numbers if is_prime(n))
        counters['prime_count'][prime_count] += 1

        # 3. 홀짝 비율
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        counters['odd_even_ratio'][f'{odd_count}홀{6-odd_count}짝'] += 1

        # 4. 범위별 분포
        range1 = sum(1 for n in numbers if 1 <= n <= 15)
        range2 = sum(1 for n in numbers if 16 <= n <= 30)
        range3 = sum(1 for n in numbers if 31 <= n <= 45)
        counters['range_distribution'][f'{range1}-{range2}-{range3}'] += 1

        # 5. 각 번호 자릿수 합의 합
        digit_sum = sum(sum(int(d) for d in str(n)) for n in numbers)
        counters['digit_sum_mod'][digit_sum % 9] += 1

        # 6. 번호 합계 범위
        number_sum = sum(numbers)
        counters['number_sum_range'].append(number_sum)

        # 7. 간격 분석
        gaps = [sorted_nums[i+1] - sorted_nums[i] for i in range(5)]
        counters['max_gap'].append(max(gaps))
        counters['min_gap'].append(min(gaps))
        counters['avg_gap'].append(sum(gaps) / len(gaps))

        # 8. 합이 특정 수로 나누어떨어짐
        for divisor in [3, 5, 6, 7, 8, 9, 11, 13]:
            if number_sum % divisor == 0:
                counters['sum_divisible_by'][divisor] += 1

        # 9. 모든 번호의 십의 자리가 다름
        tens_digits = [n // 10 for n in numbers]
        if len(set(tens_digits)) == 6:
            counters['all_different_tens'] += 1

        # 10. 등차수열
        if find_arithmetic_sequences(numbers):
            counters['arithmetic_sequence'] += 1

    return counters, total

def main():
    print("고급 패턴 분석 시작...\n")

    data = load_data('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json')
    counters, total = analyze_advanced_patterns(data)

    patterns = []

    print("=" * 80)
    print("고급 수학적 패턴 분석 결과")
    print("=" * 80)
    print()

    # 1. 연속 번호
    print("1. 연속 번호 개수:")
    for count in sorted(counters['consecutive_count'].keys()):
        freq = counters['consecutive_count'][count]
        rate = (freq / total) * 100
        print(f"   {count}개 연속: {freq}회 ({rate:.2f}%)")
        if count >= 2:
            patterns.append((f'연속 번호 {count}개 이상', rate, freq, total))
    print()

    # 2. 소수 개수
    print("2. 소수 개수:")
    for count in sorted(counters['prime_count'].keys()):
        freq = counters['prime_count'][count]
        rate = (freq / total) * 100
        print(f"   소수 {count}개: {freq}회 ({rate:.2f}%)")
        if count == max(counters['prime_count'].items(), key=lambda x: x[1])[0]:
            patterns.append((f'소수 {count}개 포함', rate, freq, total))
    print()

    # 3. 홀짝 비율
    print("3. 홀짝 비율:")
    for ratio in sorted(counters['odd_even_ratio'].keys(),
                       key=lambda x: counters['odd_even_ratio'][x], reverse=True)[:5]:
        freq = counters['odd_even_ratio'][ratio]
        rate = (freq / total) * 100
        print(f"   {ratio}: {freq}회 ({rate:.2f}%)")
        if freq == max(counters['odd_even_ratio'].values()):
            patterns.append((f'홀짝 비율 {ratio}', rate, freq, total))
    print()

    # 4. 범위별 분포
    print("4. 범위별 분포 (1-15, 16-30, 31-45):")
    for dist in sorted(counters['range_distribution'].keys(),
                      key=lambda x: counters['range_distribution'][x], reverse=True)[:5]:
        freq = counters['range_distribution'][dist]
        rate = (freq / total) * 100
        print(f"   {dist}: {freq}회 ({rate:.2f}%)")
        if freq == max(counters['range_distribution'].values()):
            patterns.append((f'범위 분포 {dist}', rate, freq, total))
    print()

    # 5. 자릿수 합의 합 mod 9
    print("5. 각 번호 자릿수 합의 총합 % 9:")
    for mod in sorted(counters['digit_sum_mod'].keys()):
        freq = counters['digit_sum_mod'][mod]
        rate = (freq / total) * 100
        print(f"   나머지 {mod}: {freq}회 ({rate:.2f}%)")
    max_digit_mod = max(counters['digit_sum_mod'].items(), key=lambda x: x[1])
    patterns.append((f'자릿수 합 % 9 = {max_digit_mod[0]}', (max_digit_mod[1]/total)*100,
                    max_digit_mod[1], total))
    print()

    # 6. 번호 합계 범위
    sum_range = counters['number_sum_range']
    print("6. 번호 합계 통계:")
    print(f"   최소: {min(sum_range)}")
    print(f"   최대: {max(sum_range)}")
    print(f"   평균: {sum(sum_range)/len(sum_range):.2f}")
    # 합계 범위별 분포
    sum_ranges = {
        '60-100': sum(1 for s in sum_range if 60 <= s <= 100),
        '101-140': sum(1 for s in sum_range if 101 <= s <= 140),
        '141-180': sum(1 for s in sum_range if 141 <= s <= 180),
        '181-220': sum(1 for s in sum_range if 181 <= s <= 220),
    }
    print("   범위별 분포:")
    for range_name, count in sorted(sum_ranges.items(), key=lambda x: x[1], reverse=True):
        rate = (count / total) * 100
        print(f"      {range_name}: {count}회 ({rate:.2f}%)")
        if count == max(sum_ranges.values()):
            patterns.append((f'합계 범위 {range_name}', rate, count, total))
    print()

    # 7. 간격 분석
    print("7. 번호 간격 분석:")
    print(f"   최대 간격 평균: {sum(counters['max_gap'])/len(counters['max_gap']):.2f}")
    print(f"   최소 간격 평균: {sum(counters['min_gap'])/len(counters['min_gap']):.2f}")
    print(f"   평균 간격 평균: {sum(counters['avg_gap'])/len(counters['avg_gap']):.2f}")
    # 최소 간격이 1인 경우 (연속 번호)
    min_gap_1 = sum(1 for g in counters['min_gap'] if g == 1)
    rate = (min_gap_1 / total) * 100
    patterns.append((f'최소 간격 1 (연속번호 포함)', rate, min_gap_1, total))
    print(f"   최소 간격이 1인 경우: {min_gap_1}회 ({rate:.2f}%)")
    print()

    # 8. 합이 특정 수로 나누어떨어짐
    print("8. 합이 특정 수로 나누어떨어지는 경우:")
    from collections import defaultdict
    for divisor in sorted(counters['sum_divisible_by'].keys()):
        freq = counters['sum_divisible_by'][divisor]
        rate = (freq / total) * 100
        print(f"   합 % {divisor} = 0: {freq}회 ({rate:.2f}%)")
        patterns.append((f'합 % {divisor} = 0', rate, freq, total))
    print()

    # 9. 십의 자리 모두 다름
    rate = (counters['all_different_tens'] / total) * 100
    patterns.append((f'십의 자리 모두 다름', rate, counters['all_different_tens'], total))
    print(f"9. 십의 자리 모두 다른 경우: {counters['all_different_tens']}회 ({rate:.2f}%)")
    print()

    # 10. 등차수열
    rate = (counters['arithmetic_sequence'] / total) * 100
    patterns.append((f'등차수열 3개 이상', rate, counters['arithmetic_sequence'], total))
    print(f"10. 등차수열 3개 이상 포함: {counters['arithmetic_sequence']}회 ({rate:.2f}%)")
    print()

    # TOP 패턴 정렬
    patterns.sort(key=lambda x: x[1], reverse=True)

    print("=" * 80)
    print("추가 발견: 높은 확률 패턴 TOP 10")
    print("=" * 80)
    print()

    for i, (name, rate, count, total_count) in enumerate(patterns[:10], 1):
        print(f"{i}. {name}")
        print(f"   성립 비율: {rate:.2f}% ({count}/{total_count})")
        print()

if __name__ == '__main__':
    from collections import defaultdict
    main()
