#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로또 번호 조합 패턴 분석 스크립트
"""

import json
from collections import Counter, defaultdict
from itertools import combinations
import sys

def load_lotto_data(filepath):
    """로또 데이터 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_2_number_combinations(data):
    """2개 번호 조합 분석"""
    combo_counter = Counter()

    for draw in data:
        numbers = draw['numbers']
        for combo in combinations(numbers, 2):
            combo_counter[combo] += 1

    return combo_counter.most_common(20)

def analyze_3_number_combinations(data):
    """3개 번호 조합 분석"""
    combo_counter = Counter()

    for draw in data:
        numbers = draw['numbers']
        for combo in combinations(numbers, 3):
            combo_counter[combo] += 1

    return combo_counter.most_common(10)

def analyze_conditional_probability(data, top_n=10):
    """조건부 확률 분석: 특정 번호가 나왔을 때 함께 나오는 번호"""
    # 각 번호별로 함께 나온 번호 카운트
    co_occurrence = defaultdict(Counter)
    number_count = Counter()

    for draw in data:
        numbers = draw['numbers']
        for num in numbers:
            number_count[num] += 1
            for other_num in numbers:
                if num != other_num:
                    co_occurrence[num][other_num] += 1

    # 가장 많이 나온 번호들에 대해 조건부 확률 계산
    most_common_numbers = [num for num, _ in number_count.most_common(top_n)]

    results = {}
    for num in most_common_numbers:
        # 조건부 확률: P(B|A) = P(A,B) / P(A)
        conditional_probs = {}
        for other_num, count in co_occurrence[num].most_common(10):
            probability = count / number_count[num]
            conditional_probs[other_num] = {
                'count': count,
                'probability': probability
            }
        results[num] = {
            'total_appearances': number_count[num],
            'top_companions': conditional_probs
        }

    return results

def analyze_bonus_patterns(data):
    """보너스 번호 패턴 분석"""
    bonus_counter = Counter()

    for draw in data:
        if 'bonus' in draw and draw['bonus'] is not None:
            bonus_counter[draw['bonus']] += 1

    return bonus_counter.most_common()

def analyze_consecutive_repeats(data):
    """연속 회차 반복 번호 패턴 분석"""
    repeat_counter = Counter()
    repeat_counts = []

    for i in range(1, len(data)):
        prev_numbers = set(data[i-1]['numbers'])
        curr_numbers = set(data[i]['numbers'])

        # 연속 회차에서 반복된 번호
        repeated = prev_numbers & curr_numbers
        repeat_count = len(repeated)
        repeat_counts.append(repeat_count)

        for num in repeated:
            repeat_counter[num] += 1

    avg_repeat = sum(repeat_counts) / len(repeat_counts) if repeat_counts else 0

    return {
        'most_repeated_numbers': repeat_counter.most_common(20),
        'average_repeats_per_draw': avg_repeat,
        'max_repeats': max(repeat_counts) if repeat_counts else 0,
        'min_repeats': min(repeat_counts) if repeat_counts else 0,
        'repeat_distribution': Counter(repeat_counts)
    }

def main():
    filepath = '/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json'

    print("=" * 80)
    print("로또 번호 조합 패턴 분석 보고서")
    print("=" * 80)
    print()

    # 데이터 로드
    print("데이터 로딩 중...")
    data = load_lotto_data(filepath)
    print(f"총 {len(data)}회 데이터 분석")
    print()

    # 1. 2개 번호 조합 TOP 20
    print("=" * 80)
    print("1. 가장 많이 함께 나온 2개 번호 조합 TOP 20")
    print("=" * 80)
    two_combos = analyze_2_number_combinations(data)
    for i, (combo, count) in enumerate(two_combos, 1):
        percentage = (count / len(data)) * 100
        print(f"{i:2d}. {combo[0]:2d}-{combo[1]:2d} : {count:3d}회 ({percentage:5.2f}%)")
    print()

    # 2. 3개 번호 조합 TOP 10
    print("=" * 80)
    print("2. 가장 많이 함께 나온 3개 번호 조합 TOP 10")
    print("=" * 80)
    three_combos = analyze_3_number_combinations(data)
    for i, (combo, count) in enumerate(three_combos, 1):
        percentage = (count / len(data)) * 100
        print(f"{i:2d}. {combo[0]:2d}-{combo[1]:2d}-{combo[2]:2d} : {count:3d}회 ({percentage:5.2f}%)")
    print()

    # 3. 조건부 확률 분석
    print("=" * 80)
    print("3. 특정 번호가 나왔을 때 함께 자주 나오는 번호 (조건부 확률)")
    print("=" * 80)
    conditional_probs = analyze_conditional_probability(data)
    for num, info in sorted(conditional_probs.items()):
        print(f"\n번호 {num:2d} (총 {info['total_appearances']}회 출현)이 나왔을 때:")
        for i, (companion, stats) in enumerate(info['top_companions'].items(), 1):
            print(f"  {i:2d}. 번호 {companion:2d} : {stats['count']:3d}회 함께 출현 "
                  f"(확률: {stats['probability']*100:5.2f}%)")
    print()

    # 4. 보너스 번호 패턴
    print("=" * 80)
    print("4. 보너스 번호 패턴")
    print("=" * 80)
    bonus_patterns = analyze_bonus_patterns(data)
    total_bonus = sum(count for _, count in bonus_patterns)
    print(f"총 보너스 번호 데이터: {total_bonus}회\n")
    for i, (num, count) in enumerate(bonus_patterns, 1):
        percentage = (count / total_bonus) * 100
        print(f"{i:2d}. 번호 {num:2d} : {count:3d}회 ({percentage:5.2f}%)")
    print()

    # 5. 연속 회차 반복 패턴
    print("=" * 80)
    print("5. 연속 회차에서 반복되는 번호 패턴")
    print("=" * 80)
    repeat_analysis = analyze_consecutive_repeats(data)

    print(f"평균 연속 반복 번호 개수: {repeat_analysis['average_repeats_per_draw']:.2f}개")
    print(f"최대 연속 반복 번호 개수: {repeat_analysis['max_repeats']}개")
    print(f"최소 연속 반복 번호 개수: {repeat_analysis['min_repeats']}개")
    print()

    print("반복 번호 개수 분포:")
    for repeat_count, frequency in sorted(repeat_analysis['repeat_distribution'].items()):
        percentage = (frequency / (len(data) - 1)) * 100
        print(f"  {repeat_count}개 반복: {frequency:3d}회 ({percentage:5.2f}%)")
    print()

    print("연속 회차에서 가장 많이 반복된 번호 TOP 20:")
    for i, (num, count) in enumerate(repeat_analysis['most_repeated_numbers'], 1):
        percentage = (count / (len(data) - 1)) * 100
        print(f"{i:2d}. 번호 {num:2d} : {count:3d}회 ({percentage:5.2f}%)")
    print()

    print("=" * 80)
    print("분석 완료")
    print("=" * 80)

if __name__ == '__main__':
    main()
