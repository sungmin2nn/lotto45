#!/usr/bin/env python3
"""
로또 당첨번호 수학적 패턴 역산 분석
각 당첨번호 세트의 내부 수학적 규칙을 분석합니다.
"""

import json
from collections import Counter
from typing import List, Tuple
import math

def load_data(filepath: str) -> List[dict]:
    """JSON 데이터 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_gaps(numbers: List[int]) -> Tuple[int, ...]:
    """번호 간격 패턴 분석 (첫번째-두번째 차이, 두번째-세번째 차이 등)"""
    return tuple(numbers[i+1] - numbers[i] for i in range(len(numbers)-1))

def analyze_multiples(numbers: List[int]) -> dict:
    """배수 관계 분석 (3의 배수 개수, 5의 배수 개수 등)"""
    return {
        'mult_3': sum(1 for n in numbers if n % 3 == 0),
        'mult_5': sum(1 for n in numbers if n % 5 == 0),
        'mult_7': sum(1 for n in numbers if n % 7 == 0),
        'even': sum(1 for n in numbers if n % 2 == 0),
        'odd': sum(1 for n in numbers if n % 2 == 1),
    }

def analyze_digit_patterns(numbers: List[int]) -> dict:
    """자릿수 패턴 분석 (1의 자리 합, 10의 자리 합)"""
    ones = [n % 10 for n in numbers]
    tens = [n // 10 for n in numbers]
    return {
        'ones_sum': sum(ones),
        'tens_sum': sum(tens),
        'ones_pattern': tuple(ones),
        'tens_pattern': tuple(tens)
    }

def analyze_consecutive(numbers: List[int]) -> int:
    """연속성 패턴 (연속된 숫자 쌍이 있는 경우)"""
    count = 0
    for i in range(len(numbers)-1):
        if numbers[i+1] - numbers[i] == 1:
            count += 1
    return count

def analyze_symmetry(numbers: List[int]) -> dict:
    """대칭성 (작은 번호 3개 합 vs 큰 번호 3개 합 비율)"""
    lower_sum = sum(numbers[:3])
    upper_sum = sum(numbers[3:])
    total = sum(numbers)
    return {
        'lower_sum': lower_sum,
        'upper_sum': upper_sum,
        'ratio': round(lower_sum / upper_sum, 3) if upper_sum > 0 else 0,
        'diff': upper_sum - lower_sum
    }

def is_arithmetic_sequence(numbers: List[int]) -> bool:
    """등차수열 여부 확인"""
    gaps = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
    return len(set(gaps)) == 1

def is_prime(n: int) -> bool:
    """소수 판별"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def analyze_primes(numbers: List[int]) -> int:
    """소수 개수"""
    return sum(1 for n in numbers if is_prime(n))

def is_fibonacci_like(numbers: List[int]) -> bool:
    """피보나치 유사 수열 확인 (연속 3개 이상이 n[i] + n[i+1] = n[i+2])"""
    for i in range(len(numbers) - 2):
        if numbers[i] + numbers[i+1] == numbers[i+2]:
            return True
    return False

def analyze_range_distribution(numbers: List[int]) -> dict:
    """번호 범위 분포 (1-15, 16-30, 31-45)"""
    return {
        'range_1_15': sum(1 for n in numbers if 1 <= n <= 15),
        'range_16_30': sum(1 for n in numbers if 16 <= n <= 30),
        'range_31_45': sum(1 for n in numbers if 31 <= n <= 45),
    }

def main():
    print("=" * 80)
    print("로또 당첨번호 수학적 패턴 역산 분석")
    print("=" * 80)

    # 데이터 로드
    data = load_data('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json')
    print(f"\n총 {len(data)}회차 데이터 분석 시작...\n")

    # 패턴 수집용 카운터
    gap_patterns = Counter()
    multiple_patterns = Counter()
    consecutive_counts = Counter()
    symmetry_ratios = Counter()
    symmetry_diffs = Counter()
    ones_sums = Counter()
    tens_sums = Counter()
    arithmetic_sequences = 0
    fibonacci_sequences = 0
    prime_counts = Counter()
    range_distributions = Counter()
    even_odd_patterns = Counter()

    # 각 회차별 분석
    for entry in data:
        numbers = sorted(entry['numbers'])  # 정렬된 상태로 분석

        # 1. 간격 패턴
        gaps = analyze_gaps(numbers)
        gap_patterns[gaps] += 1

        # 2. 배수 관계
        multiples = analyze_multiples(numbers)
        mult_key = (multiples['mult_3'], multiples['mult_5'], multiples['mult_7'])
        multiple_patterns[mult_key] += 1
        even_odd_patterns[(multiples['even'], multiples['odd'])] += 1

        # 3. 자릿수 패턴
        digit_info = analyze_digit_patterns(numbers)
        ones_sums[digit_info['ones_sum']] += 1
        tens_sums[digit_info['tens_sum']] += 1

        # 4. 연속성 패턴
        consec = analyze_consecutive(numbers)
        consecutive_counts[consec] += 1

        # 5. 대칭성
        sym = analyze_symmetry(numbers)
        symmetry_ratios[sym['ratio']] += 1
        symmetry_diffs[sym['diff']] += 1

        # 6. 등차수열 확인
        if is_arithmetic_sequence(numbers):
            arithmetic_sequences += 1

        # 7. 피보나치 유사 확인
        if is_fibonacci_like(numbers):
            fibonacci_sequences += 1

        # 8. 소수 개수
        prime_count = analyze_primes(numbers)
        prime_counts[prime_count] += 1

        # 9. 범위 분포
        range_dist = analyze_range_distribution(numbers)
        range_key = (range_dist['range_1_15'], range_dist['range_16_30'], range_dist['range_31_45'])
        range_distributions[range_key] += 1

    # ========== 결과 출력 ==========

    print("\n" + "=" * 80)
    print("1. 간격 패턴 분석 (번호 사이의 차이)")
    print("=" * 80)
    print("가장 많이 나타난 상위 10개 간격 패턴:\n")
    for i, (pattern, count) in enumerate(gap_patterns.most_common(10), 1):
        print(f"{i:2d}. 간격 {str(list(pattern)):30s} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("2. 배수 관계 분석")
    print("=" * 80)
    print("(3의배수, 5의배수, 7의배수) 개수 패턴:\n")
    for i, (pattern, count) in enumerate(multiple_patterns.most_common(10), 1):
        print(f"{i:2d}. 배수패턴 (3:{pattern[0]}개, 5:{pattern[1]}개, 7:{pattern[2]}개) - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n짝수/홀수 조합 패턴:\n")
    for i, (pattern, count) in enumerate(even_odd_patterns.most_common(5), 1):
        print(f"{i:2d}. 짝수:{pattern[0]}개, 홀수:{pattern[1]}개 - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("3. 자릿수 패턴 분석")
    print("=" * 80)
    print("1의 자리 합계 분포 (상위 10개):\n")
    for i, (sum_val, count) in enumerate(ones_sums.most_common(10), 1):
        print(f"{i:2d}. 1의 자리 합 = {sum_val:2d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n10의 자리 합계 분포 (상위 10개):\n")
    for i, (sum_val, count) in enumerate(tens_sums.most_common(10), 1):
        print(f"{i:2d}. 10의 자리 합 = {sum_val:2d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("4. 연속성 패턴 분석")
    print("=" * 80)
    print("연속된 숫자 쌍의 개수 분포:\n")
    for i, (consec, count) in enumerate(sorted(consecutive_counts.items()), 1):
        print(f"{i}. 연속 쌍 {consec}개 - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("5. 대칭성 분석 (작은 3개 합 vs 큰 3개 합)")
    print("=" * 80)
    print("합의 차이 분포 (상위 10개):\n")
    for i, (diff, count) in enumerate(symmetry_diffs.most_common(10), 1):
        print(f"{i:2d}. 차이 = {diff:2d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n비율 분포 (상위 10개):\n")
    for i, (ratio, count) in enumerate(symmetry_ratios.most_common(10), 1):
        print(f"{i:2d}. 비율 = {ratio:.3f} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("6. 수학적 관계 (등차수열, 피보나치, 소수 비율 등)")
    print("=" * 80)
    print(f"\n등차수열: {arithmetic_sequences}회 출현 ({arithmetic_sequences/len(data)*100:.2f}%)")
    print(f"피보나치 유사: {fibonacci_sequences}회 출현 ({fibonacci_sequences/len(data)*100:.2f}%)")

    print("\n소수 개수 분포:\n")
    for i, (prime_count, count) in enumerate(sorted(prime_counts.items()), 1):
        print(f"{i}. 소수 {prime_count}개 - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("7. 범위 분포 분석 (1-15, 16-30, 31-45)")
    print("=" * 80)
    print("가장 많이 나타난 상위 10개 범위 분포:\n")
    for i, (pattern, count) in enumerate(range_distributions.most_common(10), 1):
        print(f"{i:2d}. (1-15:{pattern[0]}개, 16-30:{pattern[1]}개, 31-45:{pattern[2]}개) - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    # ========== 최종 결론: 가장 강력한 3개 규칙 ==========

    print("\n\n" + "=" * 80)
    print("최종 결론: 가장 강력한 3개 규칙")
    print("=" * 80)

    # 규칙 1: 가장 많이 나타난 짝수/홀수 비율
    top_even_odd = even_odd_patterns.most_common(1)[0]
    rule1_strength = top_even_odd[1] / len(data) * 100

    # 규칙 2: 가장 많이 나타난 범위 분포
    top_range = range_distributions.most_common(1)[0]
    rule2_strength = top_range[1] / len(data) * 100

    # 규칙 3: 연속 쌍 개수
    top_consec = consecutive_counts.most_common(1)[0]
    rule3_strength = top_consec[1] / len(data) * 100

    print(f"\n규칙 1. 짝수/홀수 균형 법칙 (강도: {rule1_strength:.2f}%)")
    print(f"   - 짝수 {top_even_odd[0][0]}개 + 홀수 {top_even_odd[0][1]}개 조합이 {top_even_odd[1]}회 출현")
    print(f"   - 이는 전체의 {rule1_strength:.2f}%에 해당하며, 가장 빈번한 패턴")

    print(f"\n규칙 2. 범위 분산 법칙 (강도: {rule2_strength:.2f}%)")
    print(f"   - 1-15구간: {top_range[0][0]}개, 16-30구간: {top_range[0][1]}개, 31-45구간: {top_range[0][2]}개")
    print(f"   - 이 분포가 {top_range[1]}회 출현하여 가장 안정적인 범위 조합")

    print(f"\n규칙 3. 연속성 제한 법칙 (강도: {rule3_strength:.2f}%)")
    print(f"   - 연속된 숫자 쌍이 {top_consec[0]}개인 경우가 {top_consec[1]}회로 가장 많음")
    print(f"   - 연속된 숫자가 너무 많거나 적지 않은 균형적 패턴")

    # 추가 인사이트
    print("\n" + "=" * 80)
    print("추가 인사이트")
    print("=" * 80)

    # 가장 흔한 간격 패턴
    top_gap = gap_patterns.most_common(1)[0]
    print(f"\n- 가장 빈번한 간격 패턴: {list(top_gap[0])} ({top_gap[1]}회, {top_gap[1]/len(data)*100:.2f}%)")

    # 가장 흔한 1의 자리 합
    top_ones = ones_sums.most_common(1)[0]
    print(f"- 가장 빈번한 1의 자리 합: {top_ones[0]} ({top_ones[1]}회, {top_ones[1]/len(data)*100:.2f}%)")

    # 가장 흔한 대칭 차이
    top_diff = symmetry_diffs.most_common(1)[0]
    print(f"- 가장 빈번한 앞3개-뒤3개 차이: {top_diff[0]} ({top_diff[1]}회, {top_diff[1]/len(data)*100:.2f}%)")

    # 가장 흔한 배수 패턴
    top_mult = multiple_patterns.most_common(1)[0]
    print(f"- 가장 빈번한 배수 패턴: 3의배수 {top_mult[0][0]}개, 5의배수 {top_mult[0][1]}개, 7의배수 {top_mult[0][2]}개 ({top_mult[1]}회, {top_mult[1]/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("분석 완료")
    print("=" * 80)

if __name__ == "__main__":
    main()
