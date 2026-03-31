#!/usr/bin/env python3
"""로또 데이터에서 수학적 패턴 분석"""

import json
from collections import defaultdict, Counter
from typing import List, Tuple, Dict

def load_data(filepath: str) -> List[Dict]:
    """로또 데이터 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_symmetric_sum(numbers: List[int]) -> bool:
    """대칭 합: a + f = b + e"""
    sorted_nums = sorted(numbers)
    return sorted_nums[0] + sorted_nums[5] == sorted_nums[1] + sorted_nums[4]

def analyze_middle_sum(numbers: List[int]) -> int:
    """중앙값 합: c + d"""
    sorted_nums = sorted(numbers)
    return sorted_nums[2] + sorted_nums[3]

def analyze_edge_interval(numbers: List[int]) -> bool:
    """양끝 간격 동일: (b-a) = (f-e)"""
    sorted_nums = sorted(numbers)
    return (sorted_nums[1] - sorted_nums[0]) == (sorted_nums[5] - sorted_nums[4])

def analyze_product_ones_digit(numbers: List[int]) -> int:
    """a*f의 일의 자리"""
    sorted_nums = sorted(numbers)
    return (sorted_nums[0] * sorted_nums[5]) % 10

def analyze_half_sum_ratio(numbers: List[int]) -> Tuple[int, int]:
    """전반부/후반부 합 비교"""
    sorted_nums = sorted(numbers)
    first_half = sum(sorted_nums[:3])
    second_half = sum(sorted_nums[3:])
    return first_half, second_half

def analyze_sum_modulo(numbers: List[int], mod: int) -> int:
    """번호 합계 % mod"""
    return sum(numbers) % mod

def analyze_draw_relation(draw_num: int, numbers: List[int]) -> Dict:
    """회차 번호와 당첨번호의 관계"""
    mod_45 = draw_num % 45
    digit_sum = sum(int(d) for d in str(draw_num))

    return {
        'mod_45_in_numbers': mod_45 in numbers or mod_45 == 0,
        'digit_sum_in_numbers': digit_sum in numbers,
        'mod_45': mod_45,
        'digit_sum': digit_sum
    }

def analyze_previous_relation(current_nums: List[int], prev_nums: List[int]) -> Dict:
    """이전 회차와의 관계"""
    if not prev_nums:
        return {}

    # 겹치는 번호 개수
    overlap = len(set(current_nums) & set(prev_nums))

    # 이전 회차 합/차
    prev_sum = sum(prev_nums)
    curr_sum = sum(current_nums)

    # 이전 회차 번호들의 차이가 현재에 나오는지
    prev_sorted = sorted(prev_nums)
    differences = []
    for i in range(len(prev_sorted) - 1):
        diff = prev_sorted[i+1] - prev_sorted[i]
        if diff <= 45:
            differences.append(diff)

    diff_in_current = sum(1 for d in differences if d in current_nums)

    return {
        'overlap_count': overlap,
        'sum_diff': curr_sum - prev_sum,
        'diff_in_current': diff_in_current,
        'total_diffs': len(differences)
    }

def main():
    print("로또 데이터 분석 시작...\n")

    # 데이터 로드
    data = load_data('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json')
    total_draws = len(data)
    print(f"총 {total_draws}개 회차 데이터 분석\n")

    # 결과 저장
    results = {
        'symmetric_sum': 0,
        'middle_sum_values': Counter(),
        'edge_interval': 0,
        'product_ones_digit': Counter(),
        'half_sum_equal': 0,
        'half_sum_diff': [],
        'sum_mod_7': Counter(),
        'sum_mod_9': Counter(),
        'sum_mod_10': Counter(),
        'mod_45_in_numbers': 0,
        'digit_sum_in_numbers': 0,
        'overlap_counts': Counter(),
        'diff_in_current': 0,
        'total_diffs': 0
    }

    # 각 회차 분석
    prev_numbers = None
    for item in data:
        draw_num = item.get('round', 0)
        numbers = item.get('numbers', [])

        if len(numbers) != 6:
            continue

        sorted_nums = sorted(numbers)

        # 1. 대칭 합
        if analyze_symmetric_sum(numbers):
            results['symmetric_sum'] += 1

        # 2. 중앙값 합
        middle_sum = analyze_middle_sum(numbers)
        results['middle_sum_values'][middle_sum] += 1

        # 3. 양끝 간격
        if analyze_edge_interval(numbers):
            results['edge_interval'] += 1

        # 4. a*f 일의 자리
        ones_digit = analyze_product_ones_digit(numbers)
        results['product_ones_digit'][ones_digit] += 1

        # 5. 전반부/후반부 합
        first_half, second_half = analyze_half_sum_ratio(numbers)
        if first_half == second_half:
            results['half_sum_equal'] += 1
        results['half_sum_diff'].append(abs(first_half - second_half))

        # 6. 합계 나머지
        results['sum_mod_7'][analyze_sum_modulo(numbers, 7)] += 1
        results['sum_mod_9'][analyze_sum_modulo(numbers, 9)] += 1
        results['sum_mod_10'][analyze_sum_modulo(numbers, 10)] += 1

        # 7. 회차 관계
        draw_rel = analyze_draw_relation(draw_num, numbers)
        if draw_rel['mod_45_in_numbers']:
            results['mod_45_in_numbers'] += 1
        if draw_rel['digit_sum_in_numbers']:
            results['digit_sum_in_numbers'] += 1

        # 8. 이전 회차 관계
        if prev_numbers:
            prev_rel = analyze_previous_relation(numbers, prev_numbers)
            results['overlap_counts'][prev_rel['overlap_count']] += 1
            if prev_rel['total_diffs'] > 0:
                results['diff_in_current'] += prev_rel['diff_in_current']
                results['total_diffs'] += prev_rel['total_diffs']

        prev_numbers = numbers

    # 결과 분석 및 출력
    print("=" * 80)
    print("수학적 패턴 분석 결과")
    print("=" * 80)
    print()

    patterns = []

    # 1. 대칭 합 (a + f = b + e)
    symmetric_rate = (results['symmetric_sum'] / total_draws) * 100
    patterns.append(('대칭 합 (a+f = b+e)', symmetric_rate, results['symmetric_sum'], total_draws))
    print(f"1. 대칭 합 (a+f = b+e): {results['symmetric_sum']}/{total_draws} ({symmetric_rate:.2f}%)")
    print()

    # 2. 중앙값 합
    most_common_middle = results['middle_sum_values'].most_common(5)
    print("2. 중앙값 합 (c+d) 분포:")
    for value, count in most_common_middle:
        rate = (count / total_draws) * 100
        print(f"   c+d = {value}: {count}회 ({rate:.2f}%)")
        if count == most_common_middle[0][1]:
            patterns.append((f'중앙값 합 (c+d = {value})', rate, count, total_draws))
    print()

    # 3. 양끝 간격
    edge_rate = (results['edge_interval'] / total_draws) * 100
    patterns.append(('양끝 간격 동일 (b-a = f-e)', edge_rate, results['edge_interval'], total_draws))
    print(f"3. 양끝 간격 동일 (b-a = f-e): {results['edge_interval']}/{total_draws} ({edge_rate:.2f}%)")
    print()

    # 4. a*f 일의 자리
    print("4. a*f의 일의 자리 분포:")
    for digit in sorted(results['product_ones_digit'].keys()):
        count = results['product_ones_digit'][digit]
        rate = (count / total_draws) * 100
        print(f"   일의 자리 {digit}: {count}회 ({rate:.2f}%)")
    most_common_digit = results['product_ones_digit'].most_common(1)[0]
    patterns.append((f'a*f의 일의 자리 = {most_common_digit[0]}', (most_common_digit[1]/total_draws)*100,
                    most_common_digit[1], total_draws))
    print()

    # 5. 전반부/후반부 합
    equal_rate = (results['half_sum_equal'] / total_draws) * 100
    avg_diff = sum(results['half_sum_diff']) / len(results['half_sum_diff'])
    patterns.append(('전반부/후반부 합 동일', equal_rate, results['half_sum_equal'], total_draws))
    print(f"5. 전반부(a+b+c) vs 후반부(d+e+f):")
    print(f"   합이 같은 경우: {results['half_sum_equal']}/{total_draws} ({equal_rate:.2f}%)")
    print(f"   평균 차이: {avg_diff:.2f}")
    print()

    # 6. 합계 나머지
    print("6. 번호 합계의 나머지 분포:")
    print("   mod 7:")
    for mod in sorted(results['sum_mod_7'].keys()):
        count = results['sum_mod_7'][mod]
        rate = (count / total_draws) * 100
        print(f"      {mod}: {count}회 ({rate:.2f}%)")
    print("   mod 9:")
    for mod in sorted(results['sum_mod_9'].keys()):
        count = results['sum_mod_9'][mod]
        rate = (count / total_draws) * 100
        print(f"      {mod}: {count}회 ({rate:.2f}%)")
    print("   mod 10:")
    for mod in sorted(results['sum_mod_10'].keys()):
        count = results['sum_mod_10'][mod]
        rate = (count / total_draws) * 100
        print(f"      {mod}: {count}회 ({rate:.2f}%)")

    # 가장 편향된 나머지 찾기
    max_mod7 = results['sum_mod_7'].most_common(1)[0]
    patterns.append((f'합계 % 7 = {max_mod7[0]}', (max_mod7[1]/total_draws)*100, max_mod7[1], total_draws))
    print()

    # 7. 회차 관계
    mod45_rate = (results['mod_45_in_numbers'] / total_draws) * 100
    digit_rate = (results['digit_sum_in_numbers'] / total_draws) * 100
    patterns.append(('회차 % 45가 당첨번호에 포함', mod45_rate, results['mod_45_in_numbers'], total_draws))
    patterns.append(('회차 자릿수 합이 당첨번호에 포함', digit_rate, results['digit_sum_in_numbers'], total_draws))
    print(f"7. 회차 번호와의 관계:")
    print(f"   회차 % 45가 당첨번호에 포함: {results['mod_45_in_numbers']}/{total_draws} ({mod45_rate:.2f}%)")
    print(f"   회차 자릿수 합이 당첨번호에 포함: {results['digit_sum_in_numbers']}/{total_draws} ({digit_rate:.2f}%)")
    print()

    # 8. 이전 회차 관계
    print("8. 이전 회차와의 관계:")
    print("   겹치는 번호 개수 분포:")
    for overlap in sorted(results['overlap_counts'].keys()):
        count = results['overlap_counts'][overlap]
        rate = (count / (total_draws - 1)) * 100
        print(f"      {overlap}개 겹침: {count}회 ({rate:.2f}%)")

    if results['total_diffs'] > 0:
        diff_rate = (results['diff_in_current'] / results['total_diffs']) * 100
        patterns.append(('이전 회차 간격이 다음 회차에 포함', diff_rate,
                        results['diff_in_current'], results['total_diffs']))
        print(f"   이전 회차 번호 간격이 다음 회차에 포함: {results['diff_in_current']}/{results['total_diffs']} ({diff_rate:.2f}%)")
    print()

    # TOP 5 패턴
    patterns.sort(key=lambda x: x[1], reverse=True)

    print("=" * 80)
    print("가장 높은 확률로 성립하는 규칙 TOP 5")
    print("=" * 80)
    print()

    for i, (name, rate, count, total) in enumerate(patterns[:5], 1):
        print(f"{i}. {name}")
        print(f"   성립 비율: {rate:.2f}% ({count}/{total})")
        print()

    # 추가 통계
    print("=" * 80)
    print("추가 발견 사항")
    print("=" * 80)
    print()

    # 중앙값 합의 범위
    min_middle = min(results['middle_sum_values'].keys())
    max_middle = max(results['middle_sum_values'].keys())
    print(f"중앙값 합(c+d)의 범위: {min_middle} ~ {max_middle}")
    print()

    # 전반부/후반부 차이의 범위
    min_diff = min(results['half_sum_diff'])
    max_diff = max(results['half_sum_diff'])
    print(f"전반부/후반부 합 차이의 범위: {min_diff} ~ {max_diff}")
    print()

if __name__ == '__main__':
    main()
