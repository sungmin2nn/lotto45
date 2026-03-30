#!/usr/bin/env python3
"""
주간 전략 실행기
- 200개+ 전략 실행
- ROI 기준 상위 5개 선별
- 대시보드에 추천 번호 업데이트
"""
import json
import random
import hashlib
import math
import os
import sys
from datetime import datetime
from collections import Counter

# 경로 설정
BASE_DIR = '/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45'
STRATEGIES_DIR = os.path.join(BASE_DIR, 'strategies_to_test')

# 데이터 로드
with open(os.path.join(BASE_DIR, 'lotto_data.json'), 'r') as f:
    lotto_data = json.load(f)

# 상금 정보
PRIZE = {1: 2000000000, 2: 50000000, 3: 1500000, 4: 50000, 5: 5000}

#############################################
# 기존 대시보드 전략 (17개)
#############################################

def get_frequency(data, end_round, n=10):
    """최근 n회 빈도 계산"""
    freq = Counter()
    for item in data:
        if end_round - n <= item['round'] < end_round:
            freq.update(item['numbers'])
    return freq

def hot_strategy(data, round_num):
    """HOT_집중: 최근 10회 출현 빈도 상위"""
    freq = get_frequency(data, round_num, 10)
    if not freq:
        return sorted(random.sample(range(1, 46), 6))
    top = [n for n, _ in freq.most_common(15)]
    return sorted(random.sample(top, min(6, len(top))))

def cold_strategy(data, round_num):
    """COLD_역발상: 최근 10회 미출현/저빈도"""
    freq = get_frequency(data, round_num, 10)
    all_nums = set(range(1, 46))
    appeared = set(freq.keys())
    cold = list(all_nums - appeared)
    if len(cold) < 6:
        cold += [n for n, _ in freq.most_common()[-10:]]
    return sorted(random.sample(cold, 6))

def balanced_strategy(data, round_num):
    """균등_분산: 구간별 선택"""
    ranges = [(1,9), (10,19), (20,29), (30,39), (40,45)]
    selected = []
    for start, end in ranges:
        selected.append(random.randint(start, end))
    selected.append(random.randint(1, 45))
    return sorted(list(set(selected))[:6]) if len(set(selected)) >= 6 else sorted(random.sample(range(1, 46), 6))

def fibonacci_strategy(data, round_num):
    """피보나치: 피보나치 수열 기반"""
    fib = [1, 2, 3, 5, 8, 13, 21, 34]
    valid = [n for n in fib if n <= 45]
    if len(valid) < 6:
        valid += [n + 1 for n in fib if n + 1 <= 45 and n + 1 not in valid]
    return sorted(random.sample(valid, 6))

def prime_strategy(data, round_num):
    """소수_전략: 소수 중심"""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
    return sorted(random.sample(primes, 6))

def random_strategy(data, round_num):
    """완전_랜덤"""
    return sorted(random.sample(range(1, 46), 6))

def seed_strategy(data, round_num):
    """회차_시드: 회차 기반 시드"""
    random.seed(round_num)
    result = sorted(random.sample(range(1, 46), 6))
    random.seed()
    return result

def exclude_recent_strategy(data, round_num):
    """최근_제외: 최근 3회 번호 제외"""
    recent = set()
    for item in data:
        if round_num - 3 <= item['round'] < round_num:
            recent.update(item['numbers'])
    available = [n for n in range(1, 46) if n not in recent]
    if len(available) < 6:
        return sorted(random.sample(range(1, 46), 6))
    return sorted(random.sample(available, 6))

def pair_strategy(data, round_num):
    """궁합_기반: 함께 자주 출현한 조합"""
    pairs = Counter()
    for item in data:
        if item['round'] < round_num:
            nums = item['numbers']
            for i in range(len(nums)):
                for j in range(i+1, len(nums)):
                    pairs[(nums[i], nums[j])] += 1
    if not pairs:
        return sorted(random.sample(range(1, 46), 6))
    top = pairs.most_common(10)
    candidates = set()
    for (a, b), _ in top:
        candidates.add(a)
        candidates.add(b)
    if len(candidates) >= 6:
        return sorted(random.sample(list(candidates), 6))
    return sorted(random.sample(range(1, 46), 6))

def odd_even_strategy(data, round_num):
    """홀짝_균형: 홀수 3 + 짝수 3"""
    odds = [n for n in range(1, 46, 2)]
    evens = [n for n in range(2, 46, 2)]
    return sorted(random.sample(odds, 3) + random.sample(evens, 3))

def high_low_strategy(data, round_num):
    """고저_균형: 저번호 3 + 고번호 3"""
    low = list(range(1, 23))
    high = list(range(23, 46))
    return sorted(random.sample(low, 3) + random.sample(high, 3))

def last_digit_strategy(data, round_num):
    """끝수_분산: 다양한 끝수"""
    by_digit = {i: [] for i in range(10)}
    for n in range(1, 46):
        by_digit[n % 10].append(n)
    selected = []
    digits = random.sample(range(10), 6)
    for d in digits:
        if by_digit[d]:
            selected.append(random.choice(by_digit[d]))
    if len(selected) < 6:
        selected += random.sample([n for n in range(1, 46) if n not in selected], 6 - len(selected))
    return sorted(selected[:6])

def sum_range_strategy(data, round_num):
    """합계_범위: 합이 100-175"""
    for _ in range(100):
        nums = sorted(random.sample(range(1, 46), 6))
        if 100 <= sum(nums) <= 175:
            return nums
    return sorted(random.sample(range(1, 46), 6))

def consecutive_strategy(data, round_num):
    """연속번호_포함: 연속 2개 포함"""
    start = random.randint(1, 44)
    consecutive = [start, start + 1]
    others = [n for n in range(1, 46) if n not in consecutive]
    return sorted(consecutive + random.sample(others, 4))

def golden_ratio_strategy(data, round_num):
    """황금비율: 황금비 간격"""
    phi = 1.618
    start = random.randint(1, 10)
    nums = [start]
    current = start
    for _ in range(10):
        current = int(current * phi) % 45 + 1
        if current not in nums and 1 <= current <= 45:
            nums.append(current)
    if len(nums) >= 6:
        return sorted(nums[:6])
    return sorted(random.sample(range(1, 46), 6))

#############################################
# 신규 전략: 종교_역사 (ROI 814.94%)
#############################################

def religion_history_strategy(data, round_num):
    """종교_역사: 종교 창시/전파 연도 기반"""
    religions = [63, 1, 22, 6, 4, 7, 10, 13, 16, 30, 33, 38, 40, 44, 45]
    valid = [n for n in religions if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

#############################################
# 신규 전략: 카오스_이론 (ROI 58.01%)
#############################################

def chaos_theory_strategy(data, round_num):
    """카오스_이론: 로지스틱 맵 기반"""
    x = 0.1 + (round_num % 100) / 1000
    r = 3.9
    numbers = set()
    for _ in range(100):
        x = r * x * (1 - x)
        num = int(x * 45) + 1
        if 1 <= num <= 45:
            numbers.add(num)
        if len(numbers) >= 6:
            break
    while len(numbers) < 6:
        numbers.add(random.randint(1, 45))
    return sorted(list(numbers))[:6]

#############################################
# 기존 대시보드 전략 목록
#############################################

DASHBOARD_STRATEGIES = {
    'HOT_집중': hot_strategy,
    'COLD_역발상': cold_strategy,
    '균등_분산': balanced_strategy,
    '피보나치': fibonacci_strategy,
    '소수_전략': prime_strategy,
    '완전_랜덤': random_strategy,
    '회차_시드': seed_strategy,
    '최근_제외': exclude_recent_strategy,
    '궁합_기반': pair_strategy,
    '홀짝_균형': odd_even_strategy,
    '고저_균형': high_low_strategy,
    '끝수_분산': last_digit_strategy,
    '합계_범위': sum_range_strategy,
    '연속번호_포함': consecutive_strategy,
    '황금비율': golden_ratio_strategy,
    '종교_역사': religion_history_strategy,
    '카오스_이론': chaos_theory_strategy,
}

#############################################
# 외부 전략 파일 로드
#############################################

def load_external_strategies():
    """strategies_to_test 폴더의 전략들 로드"""
    all_strategies = {}

    if not os.path.exists(STRATEGIES_DIR):
        return all_strategies

    for filename in os.listdir(STRATEGIES_DIR):
        if filename.endswith('_strategies.py') and not filename.startswith('run_'):
            filepath = os.path.join(STRATEGIES_DIR, filename)
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("strategies", filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'STRATEGIES'):
                    category = filename.replace('.py', '').replace('_strategies', '')
                    for name, func in module.STRATEGIES.items():
                        full_name = f"{name}"
                        if full_name not in all_strategies:
                            all_strategies[full_name] = func
            except Exception as e:
                print(f"  경고: {filename} 로드 실패 - {e}")

    return all_strategies

#############################################
# 백테스트 실행
#############################################

def run_backtest(strategies, data, start_round=100, games_per_round=5):
    """전략별 백테스트"""
    results = {}

    for name, func in strategies.items():
        stats = {'total_cost': 0, 'total_prize': 0, 'wins': {1:0, 2:0, 3:0, 4:0, 5:0}, 'games': 0}

        for item in data:
            if item['round'] < start_round:
                continue

            round_num = item['round']
            actual = item['numbers']
            bonus = item.get('bonus', 0)

            for _ in range(games_per_round):
                try:
                    prediction = func(data, round_num)
                    if len(prediction) != 6:
                        continue

                    matches = len(set(prediction) & set(actual))
                    bonus_match = bonus in prediction and matches == 5

                    rank = 0
                    if matches == 6:
                        rank = 1
                    elif matches == 5 and bonus_match:
                        rank = 2
                    elif matches == 5:
                        rank = 3
                    elif matches == 4:
                        rank = 4
                    elif matches == 3:
                        rank = 5

                    stats['total_cost'] += 1000
                    stats['games'] += 1

                    if rank > 0:
                        stats['total_prize'] += PRIZE[rank]
                        stats['wins'][rank] += 1

                except Exception:
                    pass

        if stats['total_cost'] > 0:
            stats['roi'] = (stats['total_prize'] - stats['total_cost']) / stats['total_cost'] * 100
        else:
            stats['roi'] = -100

        results[name] = stats

    return results

#############################################
# 메인 실행
#############################################

def load_saved_results():
    """저장된 백테스트 결과 로드"""
    saved_results = {}

    # strategies_to_test 폴더의 결과 파일들
    for filename in os.listdir(STRATEGIES_DIR):
        if filename.startswith('results_') and filename.endswith('.json'):
            filepath = os.path.join(STRATEGIES_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for name, stats in data.items():
                        saved_results[name] = {
                            'roi': stats.get('roi', -100),
                            'wins': {
                                1: stats['wins'].get('1', stats['wins'].get(1, 0)),
                                2: stats['wins'].get('2', stats['wins'].get(2, 0)),
                                3: stats['wins'].get('3', stats['wins'].get(3, 0)),
                                4: stats['wins'].get('4', stats['wins'].get(4, 0)),
                                5: stats['wins'].get('5', stats['wins'].get(5, 0)),
                            },
                            'total_cost': stats.get('total_cost', 0),
                            'total_prize': stats.get('total_prize', 0),
                            'games': stats.get('games', 0),
                        }
            except Exception as e:
                print(f"  경고: {filename} 로드 실패 - {e}")

    # physics_math_backtest_results.json 로드 (BASE_DIR에 있음)
    physics_file = os.path.join(BASE_DIR, 'physics_math_backtest_results.json')
    if os.path.exists(physics_file):
        try:
            with open(physics_file, 'r') as f:
                data = json.load(f)
                for item in data:  # 리스트 형태
                    name = item.get('strategy', '').replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').replace('6.', '').replace('7.', '').replace('8.', '').replace('9.', '')
                    if name:
                        saved_results[name] = {
                            'roi': item.get('roi', -100),
                            'wins': {
                                1: item.get('rank1', 0),
                                2: item.get('rank2', 0),
                                3: item.get('rank3', 0),
                                4: item.get('rank4', 0),
                                5: item.get('rank5', 0),
                            },
                            'total_cost': item.get('cost', 0),
                            'total_prize': item.get('revenue', 0),
                            'games': item.get('total', 0),
                        }
        except Exception as e:
            print(f"  경고: physics_math 결과 로드 실패 - {e}")

    return saved_results

def main():
    print("=" * 60)
    print("  주간 전략 실행기")
    print("=" * 60)
    print(f"  실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 다음 회차 계산
    latest_round = max(item['round'] for item in lotto_data)
    next_round = latest_round + 1
    print(f"  다음 회차: {next_round}회")

    # 모든 전략 수집
    print("\n[1] 전략 로드 중...")
    all_strategies = dict(DASHBOARD_STRATEGIES)
    external = load_external_strategies()
    all_strategies.update(external)
    print(f"  총 {len(all_strategies)}개 전략 로드됨")
    print(f"    - 대시보드: {len(DASHBOARD_STRATEGIES)}개")
    print(f"    - 외부 전략: {len(external)}개")

    # 저장된 결과 로드 (기존 백테스트 결과 사용)
    print("\n[2] 저장된 백테스트 결과 로드 중...")
    saved_results = load_saved_results()
    print(f"  {len(saved_results)}개 전략 결과 로드됨")

    # 대시보드 전략 결과 추가 (기존 backtest_results.json에서)
    backtest_file = os.path.join(BASE_DIR, 'backtest_results.json')
    if os.path.exists(backtest_file):
        with open(backtest_file, 'r') as f:
            dashboard_data = json.load(f)
            stats_data = dashboard_data.get('statistics', {})
            for name, s in stats_data.items():
                if name not in saved_results:
                    total = s.get('total', 1217)
                    cost = total * 1000
                    prize = (s.get('1등', 0) * PRIZE[1] + s.get('2등', 0) * PRIZE[2] +
                             s.get('3등', 0) * PRIZE[3] + s.get('4등', 0) * PRIZE[4] +
                             s.get('5등', 0) * PRIZE[5])
                    roi = s.get('roi', (prize - cost) / cost * 100 if cost > 0 else -100)
                    saved_results[name] = {
                        'roi': roi,
                        'wins': {1: s.get('1등', 0), 2: s.get('2등', 0), 3: s.get('3등', 0),
                                 4: s.get('4등', 0), 5: s.get('5등', 0)},
                        'total_cost': cost,
                        'total_prize': prize,
                        'games': total,
                    }

    # ROI 순 정렬
    sorted_results = sorted(saved_results.items(), key=lambda x: x[1]['roi'], reverse=True)

    # 상위 5개 선별
    top5 = sorted_results[:5]

    print("\n[3] 상위 5개 전략:")
    print("-" * 60)
    for i, (name, stats) in enumerate(top5, 1):
        roi = stats['roi']
        wins = stats.get('wins', {})
        w2 = wins.get(2, wins.get('2', 0))
        w3 = wins.get(3, wins.get('3', 0))
        w4 = wins.get(4, wins.get('4', 0))
        print(f"  {i}. {name}: ROI {roi:.2f}% (2등:{w2}, 3등:{w3}, 4등:{w4})")

    # 상위 5개 전략으로 다음 회차 예측
    print("\n[4] 다음 회차 예측 번호 생성...")
    predictions = []
    for name, stats in top5:
        func = all_strategies.get(name)
        if func:
            try:
                numbers = func(lotto_data, next_round)
                # 4등 이상 달성률 계산
                total_rounds = stats.get('total', len(lotto_data))
                wins_4plus = stats['wins'].get(2,0) + stats['wins'].get(3,0) + stats['wins'].get(4,0)
                rate_4plus = round((wins_4plus / total_rounds) * 100, 1) if total_rounds > 0 else 0
                predictions.append({
                    'strategy': name,
                    'numbers': numbers,
                    'roi': round(stats['roi'], 2),
                    'rate_4plus': rate_4plus,
                    'description': f"ROI {stats['roi']:.1f}% (2등:{stats['wins'].get(2,0)}, 3등:{stats['wins'].get(3,0)}, 4등:{stats['wins'].get(4,0)})"
                })
                print(f"  {name}: {numbers}")
            except Exception as e:
                print(f"  {name}: 예측 실패 - {e}")

    # 대시보드 업데이트
    print("\n[5] 대시보드 업데이트 중...")
    backtest_file = os.path.join(BASE_DIR, 'backtest_results.json')

    with open(backtest_file, 'r') as f:
        dashboard_data = json.load(f)

    # statistics 업데이트
    for name, stats in sorted_results:
        dashboard_data['statistics'][name] = {
            'total': stats.get('games', 1000) // 5 if stats.get('games', 0) > 0 else 1000,
            'avg_match': 0.8,
            '1등': stats['wins'].get(1, 0),
            '2등': stats['wins'].get(2, 0),
            '3등': stats['wins'].get(3, 0),
            '4등': stats['wins'].get(4, 0),
            '5등': stats['wins'].get(5, 0),
            '4등이상': sum(stats['wins'].get(i, 0) for i in range(1, 5)),
            '4등이상율': round(sum(stats['wins'].get(i, 0) for i in range(1, 5)) / max(stats.get('games', 1), 1) * 100, 2),
            '5등이상': sum(stats['wins'].values()),
            '5등이상율': round(sum(stats['wins'].values()) / max(stats.get('games', 1), 1) * 100, 2),
            'roi': round(stats['roi'], 2)
        }

    # strategies 배열 업데이트 (전체 전략 목록)
    strategy_descriptions = {
        '종교_역사': '종교 창시/전파 연도 기반 (ROI 814.94%)',
        '카오스_이론': '카오스 이론 초기조건 민감성',
        '메타러닝': 'AI 메타러닝 기반',
        '황금비율': '황금비(1.618) 기반 번호 간격',
        '해양': '5대양 면적 비율 기반',
    }
    dashboard_data['strategies'] = []
    for name, stats in sorted_results:
        desc = strategy_descriptions.get(name, f'ROI {stats["roi"]:.1f}%')
        dashboard_data['strategies'].append({
            'name': name,
            'description': desc
        })

    # predictions 업데이트
    dashboard_data['predictions'] = predictions
    dashboard_data['generated_at'] = datetime.now().isoformat()
    dashboard_data['next_round'] = next_round

    with open(backtest_file, 'w') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

    print(f"  저장 완료: {backtest_file}")

    # 결과 요약
    print("\n" + "=" * 60)
    print("  실행 완료!")
    print("=" * 60)
    print(f"  총 전략: {len(all_strategies)}개")
    print(f"  50%+ ROI: {len([r for r in sorted_results if r[1]['roi'] >= 50])}개")
    print(f"  양수 ROI: {len([r for r in sorted_results if r[1]['roi'] > 0])}개")
    print("\n  추천 번호 (상위 5개 전략):")
    for pred in predictions:
        print(f"    {pred['strategy']}: {pred['numbers']}")
    print("=" * 60)

    return predictions

if __name__ == '__main__':
    main()
