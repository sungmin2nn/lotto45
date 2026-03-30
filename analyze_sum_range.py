#!/usr/bin/env python3
"""
로또 당첨번호 합계 및 범위 패턴 분석
"""

import json
from collections import Counter, defaultdict
import statistics

file_path = '/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json'

# 데이터 로드
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 분석용 데이터 수집
sums = []
ranges = []
low_high_ratios = []
last_digits = []
decade_distributions = []

for info in data:
    # 데이터가 딕셔너리인지 확인
    if isinstance(info, dict):
        # drwtNo1 형식인지 확인
        if 'drwtNo1' in info:
            numbers = sorted([
                info['drwtNo1'],
                info['drwtNo2'],
                info['drwtNo3'],
                info['drwtNo4'],
                info['drwtNo5'],
                info['drwtNo6']
            ])
        # numbers 형식인지 확인
        elif 'numbers' in info:
            numbers = sorted(info['numbers'])
        else:
            continue
    else:
        continue

    total_sum = sum(numbers)
    sums.append(total_sum)

    number_range = numbers[-1] - numbers[0]
    ranges.append(number_range)

    low_count = sum(1 for n in numbers if n <= 22)
    low_high_ratios.append(low_count)

    for num in numbers:
        last_digits.append(num % 10)

    decade_count = {
        '1-10': 0,
        '11-20': 0,
        '21-30': 0,
        '31-40': 0,
        '41-45': 0
    }
    for num in numbers:
        if 1 <= num <= 10:
            decade_count['1-10'] += 1
        elif 11 <= num <= 20:
            decade_count['11-20'] += 1
        elif 21 <= num <= 30:
            decade_count['21-30'] += 1
        elif 31 <= num <= 40:
            decade_count['31-40'] += 1
        elif 41 <= num <= 45:
            decade_count['41-45'] += 1
    decade_distributions.append(decade_count)

print("=" * 80)
print("로또 당첨번호 패턴 분석 보고서")
print("=" * 80)
print(f"분석 회차 수: {len(data):,}회\n")

# 1. 6개 번호 합계 분포
print("1. 6개 번호 합계 분포")
print("-" * 80)
print(f"   평균: {statistics.mean(sums):.2f}")
print(f"   중앙값: {statistics.median(sums):.2f}")
print(f"   최소: {min(sums)}")
print(f"   최대: {max(sums)}")
print(f"   표준편차: {statistics.stdev(sums):.2f}")

sum_ranges = {
    '21-90': 0,
    '91-120': 0,
    '121-150': 0,
    '151-180': 0,
    '181-210': 0,
    '211-255': 0
}
for s in sums:
    if 21 <= s <= 90:
        sum_ranges['21-90'] += 1
    elif 91 <= s <= 120:
        sum_ranges['91-120'] += 1
    elif 121 <= s <= 150:
        sum_ranges['121-150'] += 1
    elif 151 <= s <= 180:
        sum_ranges['151-180'] += 1
    elif 181 <= s <= 210:
        sum_ranges['181-210'] += 1
    elif 211 <= s <= 255:
        sum_ranges['211-255'] += 1

print("\n   합계 범위별 분포:")
max_range_count = max(sum_ranges.values())
for range_name, count in sum_ranges.items():
    percentage = (count / len(sums)) * 100
    is_max = " ★ 최다" if count == max_range_count else ""
    bar = "■" * int(percentage / 2)
    print(f"   {range_name}: {count:,}회 ({percentage:5.2f}%){is_max:8} {bar}")

# 2. 번호 간 간격 패턴
print("\n2. 번호 간 간격 패턴 (첫번째-마지막 번호 차이)")
print("-" * 80)
print(f"   평균: {statistics.mean(ranges):.2f}")
print(f"   중앙값: {statistics.median(ranges):.2f}")
print(f"   최소: {min(ranges)}")
print(f"   최대: {max(ranges)}")
print(f"   표준편차: {statistics.stdev(ranges):.2f}")

range_groups = {
    '0-10': 0,
    '11-20': 0,
    '21-30': 0,
    '31-40': 0,
    '41-44': 0
}
for r in ranges:
    if 0 <= r <= 10:
        range_groups['0-10'] += 1
    elif 11 <= r <= 20:
        range_groups['11-20'] += 1
    elif 21 <= r <= 30:
        range_groups['21-30'] += 1
    elif 31 <= r <= 40:
        range_groups['31-40'] += 1
    elif 41 <= r <= 44:
        range_groups['41-44'] += 1

print("\n   간격 범위별 분포:")
for range_name, count in range_groups.items():
    percentage = (count / len(ranges)) * 100
    bar = "■" * int(percentage / 2)
    print(f"   {range_name}: {count:,}회 ({percentage:5.2f}%) {bar}")

# 3. 저번호 vs 고번호 비율
print("\n3. 저번호(1-22) vs 고번호(23-45) 비율")
print("-" * 80)
low_high_counter = Counter(low_high_ratios)
print("   6개 중 저번호 개수 분포:")
max_count = max(low_high_counter.values())
for i in range(7):
    count = low_high_counter.get(i, 0)
    percentage = (count / len(low_high_ratios)) * 100
    high_count = 6 - i
    is_max = " ★ 최다" if count == max_count else ""
    bar = "■" * int(percentage / 2)
    print(f"   저번호 {i}개 / 고번호 {high_count}개: {count:,}회 ({percentage:5.2f}%){is_max:8} {bar}")

avg_low = statistics.mean(low_high_ratios)
print(f"\n   평균 저번호 개수: {avg_low:.2f}개")
print(f"   평균 고번호 개수: {6-avg_low:.2f}개")

# 4. 끝자리 분포
print("\n4. 끝자리(1의 자리) 분포")
print("-" * 80)
last_digit_counter = Counter(last_digits)
total_numbers = len(last_digits)
print(f"   총 번호 개수: {total_numbers:,}개 (회차당 6개)")
print("\n   끝자리별 출현 빈도:")

for digit in range(10):
    count = last_digit_counter.get(digit, 0)
    percentage = (count / total_numbers) * 100
    bar = "■" * int(percentage / 0.5)
    print(f"   {digit}: {count:,}회 ({percentage:5.2f}%) {bar}")

# 5. 10단위별 분포
print("\n5. 10단위별 분포")
print("-" * 80)

decade_totals = defaultdict(int)
for dist in decade_distributions:
    for decade, count in dist.items():
        decade_totals[decade] += count

total_numbers_all = sum(decade_totals.values())
print(f"   총 번호 개수: {total_numbers_all:,}개")
print("\n   구간별 출현 빈도:")

for decade in ['1-10', '11-20', '21-30', '31-40', '41-45']:
    count = decade_totals[decade]
    percentage = (count / total_numbers_all) * 100
    bar = "■" * int(percentage / 0.5)

    if decade == '41-45':
        theoretical_prob = (5 / 45) * 100
    else:
        theoretical_prob = (10 / 45) * 100

    diff = percentage - theoretical_prob
    print(f"   {decade}: {count:,}회 ({percentage:5.2f}%) | 이론값: {theoretical_prob:.2f}% | 차이: {diff:+.2f}% {bar}")

print("\n   회차당 평균 개수:")
for decade in ['1-10', '11-20', '21-30', '31-40', '41-45']:
    avg_count = decade_totals[decade] / len(decade_distributions)
    print(f"   {decade}: {avg_count:.2f}개")

print("\n   가장 많이 나온 10단위 조합 패턴 (상위 10개):")
decade_patterns = []
for dist in decade_distributions:
    pattern = tuple(dist[d] for d in ['1-10', '11-20', '21-30', '31-40', '41-45'])
    decade_patterns.append(pattern)

pattern_counter = Counter(decade_patterns)
for idx, (pattern, count) in enumerate(pattern_counter.most_common(10), 1):
    pattern_str = f"({pattern[0]}, {pattern[1]}, {pattern[2]}, {pattern[3]}, {pattern[4]})"
    percentage = (count / len(decade_patterns)) * 100
    print(f"   {idx}. {pattern_str}: {count:,}회 ({percentage:.2f}%)")

print("\n" + "=" * 80)
print("분석 완료")
print("=" * 80)
