#!/usr/bin/env python3
"""
로또 당첨번호 심화 패턴 분석
간격의 평균, 분산, 최대/최소 등 통계적 특성을 분석합니다.
"""

import json
from collections import Counter
from typing import List
import statistics

def load_data(filepath: str) -> List[dict]:
    """JSON 데이터 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=" * 80)
    print("로또 당첨번호 심화 패턴 분석")
    print("=" * 80)

    data = load_data('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json')
    print(f"\n총 {len(data)}회차 데이터 분석\n")

    # 간격 통계
    gap_means = []
    gap_stdevs = []
    gap_max_values = []
    gap_min_values = []
    gap_ranges = []

    # 총합 통계
    total_sums = []

    # 최대/최소 번호
    max_numbers = []
    min_numbers = []

    for entry in data:
        numbers = sorted(entry['numbers'])

        # 간격 계산
        gaps = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]

        gap_means.append(statistics.mean(gaps))
        gap_stdevs.append(statistics.stdev(gaps) if len(gaps) > 1 else 0)
        gap_max_values.append(max(gaps))
        gap_min_values.append(min(gaps))
        gap_ranges.append(max(gaps) - min(gaps))

        # 총합
        total_sums.append(sum(numbers))

        # 최대/최소
        max_numbers.append(max(numbers))
        min_numbers.append(min(numbers))

    # 간격 평균의 분포
    gap_mean_counter = Counter()
    for gm in gap_means:
        gap_mean_counter[round(gm, 1)] += 1

    # 간격 최대값 분포
    gap_max_counter = Counter(gap_max_values)

    # 간격 최소값 분포
    gap_min_counter = Counter(gap_min_values)

    # 간격 범위 분포
    gap_range_counter = Counter(gap_ranges)

    # 총합 분포
    total_sum_counter = Counter(total_sums)

    # 최대 번호 분포
    max_number_counter = Counter(max_numbers)

    # 최소 번호 분포
    min_number_counter = Counter(min_numbers)

    # ========== 결과 출력 ==========

    print("=" * 80)
    print("1. 간격 평균 분포 (상위 10개)")
    print("=" * 80)
    for i, (avg, count) in enumerate(gap_mean_counter.most_common(10), 1):
        print(f"{i:2d}. 평균 간격 = {avg:4.1f} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("2. 간격 최대값 분포 (상위 15개)")
    print("=" * 80)
    for i, (max_gap, count) in enumerate(gap_max_counter.most_common(15), 1):
        print(f"{i:2d}. 최대 간격 = {max_gap:2d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("3. 간격 최소값 분포 (상위 10개)")
    print("=" * 80)
    for i, (min_gap, count) in enumerate(gap_min_counter.most_common(10), 1):
        print(f"{i:2d}. 최소 간격 = {min_gap:2d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("4. 간격 범위(최대-최소) 분포 (상위 15개)")
    print("=" * 80)
    for i, (gap_range, count) in enumerate(gap_range_counter.most_common(15), 1):
        print(f"{i:2d}. 간격 범위 = {gap_range:2d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("5. 6개 번호 총합 분포 (상위 15개)")
    print("=" * 80)
    for i, (total_sum, count) in enumerate(total_sum_counter.most_common(15), 1):
        print(f"{i:2d}. 총합 = {total_sum:3d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("6. 최대 번호 분포 (상위 10개)")
    print("=" * 80)
    for i, (max_num, count) in enumerate(max_number_counter.most_common(10), 1):
        print(f"{i:2d}. 최대 번호 = {max_num:2d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("7. 최소 번호 분포 (상위 10개)")
    print("=" * 80)
    for i, (min_num, count) in enumerate(min_number_counter.most_common(10), 1):
        print(f"{i:2d}. 최소 번호 = {min_num:2d} - {count:3d}회 출현 ({count/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("통계 요약")
    print("=" * 80)
    print(f"간격 평균의 평균: {statistics.mean(gap_means):.2f}")
    print(f"간격 평균의 표준편차: {statistics.stdev(gap_means):.2f}")
    print(f"총합의 평균: {statistics.mean(total_sums):.2f}")
    print(f"총합의 표준편차: {statistics.stdev(total_sums):.2f}")
    print(f"총합 범위: {min(total_sums)} ~ {max(total_sums)}")

    # 가장 빈번한 총합 범위 찾기
    most_common_sum = total_sum_counter.most_common(1)[0]
    print(f"\n가장 빈번한 총합: {most_common_sum[0]} ({most_common_sum[1]}회, {most_common_sum[1]/len(data)*100:.2f}%)")

    # 총합이 120-150 사이인 회차 비율
    sum_120_150 = sum(1 for s in total_sums if 120 <= s <= 150)
    print(f"총합이 120-150 사이인 회차: {sum_120_150}회 ({sum_120_150/len(data)*100:.2f}%)")

    # 총합이 130-145 사이인 회차 비율
    sum_130_145 = sum(1 for s in total_sums if 130 <= s <= 145)
    print(f"총합이 130-145 사이인 회차: {sum_130_145}회 ({sum_130_145/len(data)*100:.2f}%)")

    print("\n" + "=" * 80)
    print("분석 완료")
    print("=" * 80)

if __name__ == "__main__":
    main()
