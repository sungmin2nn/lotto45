#!/usr/bin/env python3
"""백테스팅 결과를 보기 좋게 출력"""

import json


def main():
    with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/physics_math_backtest_results.json', 'r') as f:
        results = json.load(f)

    print("=" * 95)
    print("물리/수학/통계 기반 로또 전략 백테스팅 결과")
    print("=" * 95)
    print()
    print(f"총 테스트 회차: {results[0]['total']:,}회 (100회차 ~ 1217회차)")
    print(f"1게임당 비용: 1,000원")
    print()

    # 테이블 헤더
    print("=" * 95)
    header = f"{'전략':<20} {'1등':>5} {'2등':>5} {'3등':>5} {'4등':>5} {'5등':>5} {'4등+율':>8} {'수익률':>10}"
    print(header)
    print("-" * 95)

    # 결과 출력
    for result in results:
        row = (f"{result['strategy']:<20} "
               f"{result['rank1']:>5} "
               f"{result['rank2']:>5} "
               f"{result['rank3']:>5} "
               f"{result['rank4']:>5} "
               f"{result['rank5']:>5} "
               f"{result['rank4_plus_rate']:>7.2f}% "
               f"{result['roi']:>9.1f}%")
        print(row)

    print("=" * 95)
    print()

    # 최고 성능 전략
    best_roi = max(results, key=lambda x: x['roi'])
    best_rank4_plus = max(results, key=lambda x: x['rank4_plus_rate'])
    most_wins = max(results, key=lambda x: x['rank1'] + x['rank2'] + x['rank3'] + x['rank4'] + x['rank5'])

    print("최고 성능 전략")
    print("-" * 95)
    print(f"최고 수익률: {best_roi['strategy']:<30} {best_roi['roi']:>10.2f}%")
    print(f"최고 4등 이상 비율: {best_rank4_plus['strategy']:<30} {best_rank4_plus['rank4_plus_rate']:>10.2f}%")
    print(f"최다 당첨: {most_wins['strategy']:<30} {most_wins['rank1'] + most_wins['rank2'] + most_wins['rank3'] + most_wins['rank4'] + most_wins['rank5']:>10}회")
    print()

    # 상세 통계
    print("=" * 95)
    print("상세 통계 (TOP 5)")
    print("=" * 95)
    print()

    # 수익률 기준 정렬
    sorted_by_roi = sorted(results, key=lambda x: x['roi'], reverse=True)[:5]

    for i, result in enumerate(sorted_by_roi, 1):
        print(f"[{i}] {result['strategy']}")
        print(f"    총 비용: {result['cost']:>15,}원")
        print(f"    총 수익: {result['revenue']:>15,}원")
        print(f"    순손익: {result['revenue'] - result['cost']:>15,}원")
        print(f"    수익률: {result['roi']:>15.2f}%")
        print(f"    당첨: 1등 {result['rank1']}회, 2등 {result['rank2']}회, 3등 {result['rank3']}회, 4등 {result['rank4']}회, 5등 {result['rank5']}회")
        print(f"    4등 이상 비율: {result['rank4_plus_rate']:>10.2f}%")
        print()

    # 등수별 통계
    print("=" * 95)
    print("등수별 종합 통계")
    print("=" * 95)
    total_rank1 = sum(r['rank1'] for r in results)
    total_rank2 = sum(r['rank2'] for r in results)
    total_rank3 = sum(r['rank3'] for r in results)
    total_rank4 = sum(r['rank4'] for r in results)
    total_rank5 = sum(r['rank5'] for r in results)
    total_tests = results[0]['total'] * len(results)

    print(f"전체 테스트: {total_tests:,}회 (15개 전략 × {results[0]['total']:,}회)")
    print(f"1등: {total_rank1:>5}회 ({total_rank1/total_tests*100:.4f}%)")
    print(f"2등: {total_rank2:>5}회 ({total_rank2/total_tests*100:.4f}%)")
    print(f"3등: {total_rank3:>5}회 ({total_rank3/total_tests*100:.4f}%)")
    print(f"4등: {total_rank4:>5}회 ({total_rank4/total_tests*100:.4f}%)")
    print(f"5등: {total_rank5:>5}회 ({total_rank5/total_tests*100:.4f}%)")
    print(f"총 당첨: {total_rank1 + total_rank2 + total_rank3 + total_rank4 + total_rank5:>5}회 ({(total_rank1 + total_rank2 + total_rank3 + total_rank4 + total_rank5)/total_tests*100:.2f}%)")
    print()


if __name__ == '__main__':
    main()
