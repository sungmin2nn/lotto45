#!/usr/bin/env python3
"""
범용 백테스트 실행 스크립트
사용법: python run_backtest.py <전략파일명>
예시: python run_backtest.py 01_ai_ml_strategies.py
"""
import sys
import json
import importlib.util
from datetime import datetime

# 상위 디렉토리 경로 추가
sys.path.insert(0, '/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45')

# 데이터 로드
with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

# 상금 정보
PRIZE = {
    1: 2000000000,  # 1등: 20억
    2: 50000000,    # 2등: 5천만
    3: 1500000,     # 3등: 150만
    4: 50000,       # 4등: 5만
    5: 5000,        # 5등: 5천
}

def count_matches(prediction, actual):
    """예측 번호와 실제 당첨번호의 일치 개수"""
    return len(set(prediction) & set(actual))

def get_prize_rank(matches, bonus_match=False):
    """일치 개수에 따른 등수"""
    if matches == 6:
        return 1
    elif matches == 5 and bonus_match:
        return 2
    elif matches == 5:
        return 3
    elif matches == 4:
        return 4
    elif matches == 3:
        return 5
    return 0

def run_backtest(strategies, data, start_round=100, games_per_round=5):
    """전략별 백테스트 실행"""
    results = {}

    for name, strategy_func in strategies.items():
        stats = {
            'total_cost': 0,
            'total_prize': 0,
            'wins': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'games': 0,
            'details': []
        }

        for item in data:
            if item['round'] < start_round:
                continue

            round_num = item['round']
            actual = item['numbers']
            bonus = item.get('bonus', 0)

            for game in range(games_per_round):
                try:
                    prediction = strategy_func(data, round_num)
                    if len(prediction) != 6 or not all(1 <= n <= 45 for n in prediction):
                        continue

                    matches = count_matches(prediction, actual)
                    bonus_match = bonus in prediction and matches == 5
                    rank = get_prize_rank(matches, bonus_match)

                    stats['total_cost'] += 1000
                    stats['games'] += 1

                    if rank > 0:
                        prize = PRIZE[rank]
                        stats['total_prize'] += prize
                        stats['wins'][rank] += 1

                        if rank <= 3:
                            stats['details'].append({
                                'round': round_num,
                                'rank': rank,
                                'prediction': prediction,
                                'actual': actual,
                                'matches': matches
                            })
                except Exception as e:
                    pass

        # ROI 계산
        if stats['total_cost'] > 0:
            stats['roi'] = (stats['total_prize'] - stats['total_cost']) / stats['total_cost'] * 100
        else:
            stats['roi'] = 0

        # 4등 이상 당첨률
        wins_4plus = sum(stats['wins'][i] for i in range(1, 5))
        stats['win_rate_4plus'] = wins_4plus / max(stats['games'], 1) * 100

        results[name] = stats

    return results

def print_results(results, file_name):
    """결과 출력"""
    print("\n" + "=" * 70)
    print(f"백테스트 결과: {file_name}")
    print("=" * 70)

    # ROI 순으로 정렬
    sorted_results = sorted(results.items(), key=lambda x: x[1]['roi'], reverse=True)

    print(f"\n{'전략명':<25} {'ROI':>10} {'4등+율':>10} {'3등':>6} {'4등':>6} {'5등':>6}")
    print("-" * 70)

    for name, stats in sorted_results:
        roi = stats['roi']
        win_rate = stats['win_rate_4plus']
        w3 = stats['wins'][3]
        w4 = stats['wins'][4]
        w5 = stats['wins'][5]

        # ROI에 따른 마킹
        marker = ""
        if roi >= 50:
            marker = " ★★★ 50%+ ★★★"
        elif roi >= 30:
            marker = " ★★"
        elif roi > 0:
            marker = " ★"

        print(f"{name:<25} {roi:>9.2f}% {win_rate:>9.2f}% {w3:>6} {w4:>6} {w5:>6}{marker}")

    # 3등 이상 당첨 상세
    print("\n" + "-" * 70)
    print("3등 이상 당첨 상세:")
    for name, stats in sorted_results:
        for detail in stats['details']:
            if detail['rank'] <= 3:
                print(f"  {name}: {detail['rank']}등 (회차 {detail['round']}, {detail['matches']}개 일치)")

    # 50% 이상 달성 전략 강조
    print("\n" + "=" * 70)
    over_50 = [(name, stats) for name, stats in sorted_results if stats['roi'] >= 50]
    if over_50:
        print("🎉 50% 이상 ROI 달성 전략:")
        for name, stats in over_50:
            print(f"  ★ {name}: {stats['roi']:.2f}%")
    else:
        print("50% 이상 ROI 달성 전략 없음")
        best_name, best_stats = sorted_results[0]
        print(f"최고 성과: {best_name} ({best_stats['roi']:.2f}%)")

    print("=" * 70 + "\n")

    return sorted_results

def save_results(results, file_name):
    """결과를 JSON으로 저장"""
    output = {}
    for name, stats in results.items():
        output[name] = {
            'roi': stats['roi'],
            'win_rate_4plus': stats['win_rate_4plus'],
            'wins': stats['wins'],
            'total_cost': stats['total_cost'],
            'total_prize': stats['total_prize'],
            'games': stats['games'],
        }

    output_file = f"results_{file_name.replace('.py', '')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"결과 저장됨: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python run_backtest.py <전략파일명>")
        print("예시: python run_backtest.py 01_ai_ml_strategies.py")
        sys.exit(1)

    strategy_file = sys.argv[1]

    # 전략 파일 로드
    try:
        spec = importlib.util.spec_from_file_location("strategies", strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        strategies = module.STRATEGIES
        print(f"전략 {len(strategies)}개 로드됨: {strategy_file}")
    except Exception as e:
        print(f"전략 파일 로드 실패: {e}")
        sys.exit(1)

    # 백테스트 실행
    print("백테스트 실행 중...")
    results = run_backtest(strategies, lotto_data)

    # 결과 출력
    sorted_results = print_results(results, strategy_file)

    # 결과 저장
    save_results(results, strategy_file)

if __name__ == '__main__':
    main()
