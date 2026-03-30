#!/usr/bin/env python3
"""
물리/수학/통계 기반 로또 전략 백테스팅
15개 전략: 엔트로피, 표준편차, 중심극한, 베이지안, 카오스, 웨이브, 황금나선, 프랙탈, 확률밀도, 마르코프, 푸아송, 기하분포, 조화평균, 최소자승, 몬테카를로
"""

import json
import math
import random
from typing import List, Tuple, Dict
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
from datetime import datetime


def load_lotto_data(filepath: str) -> List[Dict]:
    """로또 데이터 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_rank(predicted: List[int], actual: List[int], bonus: int) -> Tuple[int, int]:
    """등수 계산 (실제 로또 규칙)"""
    match_count = len(set(predicted) & set(actual))
    has_bonus = bonus in predicted

    if match_count == 6:
        return 1, 1  # 1등
    elif match_count == 5 and has_bonus:
        return 2, 1  # 2등
    elif match_count == 5:
        return 3, 1  # 3등
    elif match_count == 4:
        return 4, 1  # 4등
    elif match_count == 3:
        return 5, 1  # 5등
    else:
        return 0, 0  # 낙첨


def calculate_entropy(numbers: List[int], bins: int = 9) -> float:
    """엔트로피 계산 (45개를 bins개 구간으로 분할)"""
    hist = [0] * bins
    bin_size = 45 / bins
    for num in numbers:
        bin_idx = min(int((num - 1) / bin_size), bins - 1)
        hist[bin_idx] += 1

    total = len(numbers)
    entropy = 0
    for count in hist:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


# ============================================================
# 전략 1: 엔트로피 최대화
# ============================================================
def strategy_entropy_maximization(history: List[Dict], current_round: int) -> List[int]:
    """번호 분포의 엔트로피가 최대가 되도록 번호 선택"""
    best_combo = None
    max_entropy = -1

    # 랜덤 샘플링으로 최적 조합 탐색
    for _ in range(5000):
        combo = sorted(random.sample(range(1, 46), 6))
        entropy = calculate_entropy(combo, bins=6)
        if entropy > max_entropy:
            max_entropy = entropy
            best_combo = combo

    return best_combo


# ============================================================
# 전략 2: 표준편차 최적화
# ============================================================
def strategy_std_optimization(history: List[Dict], current_round: int) -> List[int]:
    """번호들의 표준편차가 역대 평균과 일치하도록"""
    if len(history) < 10:
        return sorted(random.sample(range(1, 46), 6))

    # 역대 표준편차 평균 계산
    std_list = [np.std(draw['numbers']) for draw in history[-100:]]
    target_std = np.mean(std_list)

    best_combo = None
    min_diff = float('inf')

    for _ in range(5000):
        combo = sorted(random.sample(range(1, 46), 6))
        combo_std = np.std(combo)
        diff = abs(combo_std - target_std)
        if diff < min_diff:
            min_diff = diff
            best_combo = combo

    return best_combo


# ============================================================
# 전략 3: 중심극한정리
# ============================================================
def strategy_central_limit(history: List[Dict], current_round: int) -> List[int]:
    """많은 샘플의 평균 근처 번호 선택"""
    if len(history) < 10:
        return sorted(random.sample(range(1, 46), 6))

    # 역대 번호들의 평균 계산
    all_numbers = []
    for draw in history[-50:]:
        all_numbers.extend(draw['numbers'])

    mean = np.mean(all_numbers)
    std = np.std(all_numbers)

    # 정규분포에서 샘플링
    selected = set()
    while len(selected) < 6:
        num = int(np.random.normal(mean, std))
        if 1 <= num <= 45:
            selected.add(num)

    return sorted(list(selected))


# ============================================================
# 전략 4: 베이지안 추론
# ============================================================
def strategy_bayesian(history: List[Dict], current_round: int) -> List[int]:
    """이전 데이터로 사후확률 계산"""
    if len(history) < 10:
        return sorted(random.sample(range(1, 46), 6))

    # 최근 데이터로 각 번호의 출현 확률 계산
    recent_numbers = []
    for draw in history[-30:]:
        recent_numbers.extend(draw['numbers'])

    counter = Counter(recent_numbers)
    total = sum(counter.values())

    # 사전확률(uniform) + 우도(출현빈도) = 사후확률
    prior = 1 / 45
    posterior = {}
    for num in range(1, 46):
        likelihood = counter.get(num, 0) / total if total > 0 else 0
        # 베이지안 업데이트 (간단한 형태)
        posterior[num] = (likelihood * 0.7 + prior * 0.3)

    # 확률에 따라 가중 샘플링
    numbers = list(posterior.keys())
    weights = list(posterior.values())
    selected = []

    while len(selected) < 6:
        num = random.choices(numbers, weights=weights, k=1)[0]
        if num not in selected:
            selected.append(num)

    return sorted(selected)


# ============================================================
# 전략 5: 카오스 이론
# ============================================================
def strategy_chaos(history: List[Dict], current_round: int) -> List[int]:
    """초기값 민감성 활용 (회차+날짜 기반 로지스틱 맵)"""
    # 로지스틱 맵: x_{n+1} = r * x_n * (1 - x_n)
    r = 3.9  # 카오스 영역
    x = (current_round % 1000) / 1000.0  # 초기값

    selected = set()
    iterations = 0
    max_iterations = 1000

    while len(selected) < 6 and iterations < max_iterations:
        x = r * x * (1 - x)
        num = int(x * 45) + 1
        if 1 <= num <= 45:
            selected.add(num)
        iterations += 1

    # 부족하면 랜덤으로 채우기
    while len(selected) < 6:
        selected.add(random.randint(1, 45))

    return sorted(list(selected))


# ============================================================
# 전략 6: 웨이브 패턴 (사인파)
# ============================================================
def strategy_wave(history: List[Dict], current_round: int) -> List[int]:
    """사인파 기반 번호 선택"""
    selected = set()

    for i in range(6):
        # 서로 다른 주파수의 사인파
        phase = (current_round + i * 10) * 0.1
        value = math.sin(phase) * 22.5 + 22.5  # 0~45 범위로 스케일
        num = int(value) + 1
        num = max(1, min(45, num))
        selected.add(num)

    # 중복 제거 후 부족하면 채우기
    while len(selected) < 6:
        selected.add(random.randint(1, 45))

    return sorted(list(selected))


# ============================================================
# 전략 7: 황금나선 (피보나치)
# ============================================================
def strategy_golden_spiral(history: List[Dict], current_round: int) -> List[int]:
    """피보나치 나선 기반"""
    phi = (1 + math.sqrt(5)) / 2  # 황금비

    selected = set()
    for i in range(20):
        # 황금각을 이용한 나선
        angle = i * 2 * math.pi / phi
        radius = math.sqrt(i)

        # 극좌표를 1~45 범위로 변환
        num = int((math.sin(angle) * radius) % 45) + 1
        num = max(1, min(45, num))
        selected.add(num)

        if len(selected) >= 6:
            break

    while len(selected) < 6:
        selected.add(random.randint(1, 45))

    return sorted(list(selected))[:6]


# ============================================================
# 전략 8: 프랙탈 (자기유사성)
# ============================================================
def strategy_fractal(history: List[Dict], current_round: int) -> List[int]:
    """자기유사성 패턴"""
    if len(history) < 10:
        return sorted(random.sample(range(1, 46), 6))

    # 최근 패턴의 스케일 변환
    recent = history[-3:]
    pattern = []
    for draw in recent:
        pattern.extend(draw['numbers'])

    # 패턴을 축소/확대하여 새로운 번호 생성
    selected = set()
    scale_factor = 0.8 + (current_round % 10) * 0.04  # 0.8 ~ 1.2

    for num in pattern:
        scaled = int(num * scale_factor)
        scaled = max(1, min(45, scaled))
        selected.add(scaled)
        if len(selected) >= 6:
            break

    while len(selected) < 6:
        selected.add(random.randint(1, 45))

    return sorted(list(selected))[:6]


# ============================================================
# 전략 9: 확률밀도 (정규분포)
# ============================================================
def strategy_probability_density(history: List[Dict], current_round: int) -> List[int]:
    """정규분포 기반 번호 선택"""
    # 1~45의 중심값 23을 평균으로
    mean = 23
    std = 10

    selected = set()
    while len(selected) < 6:
        num = int(np.random.normal(mean, std))
        if 1 <= num <= 45:
            selected.add(num)

    return sorted(list(selected))


# ============================================================
# 전략 10: 마르코프 체인
# ============================================================
def strategy_markov(history: List[Dict], current_round: int) -> List[int]:
    """이전 상태 기반 전이확률"""
    if len(history) < 5:
        return sorted(random.sample(range(1, 46), 6))

    # 전이 확률 행렬 구축
    transition = defaultdict(lambda: defaultdict(int))

    for i in range(len(history) - 1):
        current_nums = history[i]['numbers']
        next_nums = history[i + 1]['numbers']

        for curr in current_nums:
            for nxt in next_nums:
                transition[curr][nxt] += 1

    # 마지막 회차 번호에서 시작
    last_numbers = history[-1]['numbers']
    selected = set()

    for start_num in last_numbers:
        if start_num in transition and transition[start_num]:
            next_candidates = list(transition[start_num].keys())
            weights = list(transition[start_num].values())
            next_num = random.choices(next_candidates, weights=weights, k=1)[0]
            selected.add(next_num)

        if len(selected) >= 6:
            break

    while len(selected) < 6:
        selected.add(random.randint(1, 45))

    return sorted(list(selected))[:6]


# ============================================================
# 전략 11: 푸아송 분포
# ============================================================
def strategy_poisson(history: List[Dict], current_round: int) -> List[int]:
    """희귀 이벤트 확률 (푸아송 분포)"""
    if len(history) < 10:
        return sorted(random.sample(range(1, 46), 6))

    # 각 번호의 평균 출현율 계산
    counter = Counter()
    for draw in history[-50:]:
        counter.update(draw['numbers'])

    lambda_param = 50 * 6 / 45  # 평균 출현 횟수

    selected = set()
    attempts = 0
    while len(selected) < 6 and attempts < 1000:
        for num in range(1, 46):
            observed = counter.get(num, 0)
            # 푸아송 확률
            prob = stats.poisson.pmf(observed, lambda_param)
            if random.random() < prob * 10:  # 스케일 조정
                selected.add(num)
                if len(selected) >= 6:
                    break
        attempts += 1

    while len(selected) < 6:
        selected.add(random.randint(1, 45))

    return sorted(list(selected))[:6]


# ============================================================
# 전략 12: 기하분포
# ============================================================
def strategy_geometric(history: List[Dict], current_round: int) -> List[int]:
    """첫 성공까지의 시행 (기하분포)"""
    # 각 번호가 마지막으로 나온 이후 몇 회차 지났는지 계산
    last_seen = {}

    for i, draw in enumerate(history):
        for num in draw['numbers']:
            last_seen[num] = i

    current_idx = len(history) - 1

    # 기하분포: 오래 안 나온 번호에 높은 가중치
    weights = {}
    p = 6 / 45  # 성공 확률

    for num in range(1, 46):
        if num in last_seen:
            gap = current_idx - last_seen[num]
        else:
            gap = current_idx

        # 기하분포 확률: (1-p)^(k-1) * p
        weights[num] = ((1 - p) ** gap) * p if gap > 0 else p

    # 가중치 기반 샘플링
    numbers = list(weights.keys())
    weight_values = list(weights.values())

    selected = []
    while len(selected) < 6:
        num = random.choices(numbers, weights=weight_values, k=1)[0]
        if num not in selected:
            selected.append(num)

    return sorted(selected)


# ============================================================
# 전략 13: 조화평균
# ============================================================
def strategy_harmonic_mean(history: List[Dict], current_round: int) -> List[int]:
    """번호들의 조화평균 기반"""
    if len(history) < 10:
        return sorted(random.sample(range(1, 46), 6))

    # 역대 당첨 번호들의 조화평균 계산
    recent_draws = history[-20:]
    harmonic_means = []

    for draw in recent_draws:
        nums = draw['numbers']
        # 조화평균 = n / (1/x1 + 1/x2 + ... + 1/xn)
        h_mean = len(nums) / sum(1/n for n in nums)
        harmonic_means.append(h_mean)

    target = np.mean(harmonic_means)

    # 조화평균이 target에 가까운 조합 찾기
    best_combo = None
    min_diff = float('inf')

    for _ in range(5000):
        combo = sorted(random.sample(range(1, 46), 6))
        h_mean = 6 / sum(1/n for n in combo)
        diff = abs(h_mean - target)
        if diff < min_diff:
            min_diff = diff
            best_combo = combo

    return best_combo


# ============================================================
# 전략 14: 최소자승법 (트렌드 피팅)
# ============================================================
def strategy_least_squares(history: List[Dict], current_round: int) -> List[int]:
    """트렌드 라인 피팅"""
    if len(history) < 20:
        return sorted(random.sample(range(1, 46), 6))

    # 각 번호의 출현 트렌드 분석
    trends = {}
    recent = history[-30:]

    for num in range(1, 46):
        occurrences = []
        for i, draw in enumerate(recent):
            if num in draw['numbers']:
                occurrences.append(i)

        if len(occurrences) >= 2:
            # 선형 회귀로 트렌드 계산
            x = np.array(occurrences)
            y = np.arange(len(occurrences))
            slope, intercept = np.polyfit(x, y, 1)
            trends[num] = slope
        else:
            trends[num] = 0

    # 트렌드가 양수인(상승 중인) 번호 선택
    sorted_nums = sorted(trends.items(), key=lambda x: x[1], reverse=True)
    selected = [num for num, _ in sorted_nums[:6]]

    return sorted(selected)


# ============================================================
# 전략 15: 몬테카를로 시뮬레이션
# ============================================================
def strategy_monte_carlo(history: List[Dict], current_round: int) -> List[int]:
    """시뮬레이션 기반 최적화"""
    if len(history) < 10:
        return sorted(random.sample(range(1, 46), 6))

    # 역대 데이터 분석
    all_numbers = []
    for draw in history[-50:]:
        all_numbers.extend(draw['numbers'])

    counter = Counter(all_numbers)

    # 몬테카를로: 여러 번 시뮬레이션하여 최적 조합 찾기
    best_score = -1
    best_combo = None

    for _ in range(3000):
        combo = sorted(random.sample(range(1, 46), 6))

        # 점수: 역대 출현 빈도의 분산이 낮을수록 좋음
        freqs = [counter.get(num, 0) for num in combo]
        score = -np.var(freqs)  # 분산이 낮을수록 높은 점수

        if score > best_score:
            best_score = score
            best_combo = combo

    return best_combo


# ============================================================
# 백테스팅 엔진
# ============================================================
def backtest_strategy(data: List[Dict], strategy_func, strategy_name: str,
                     start_round: int = 100) -> Dict:
    """전략 백테스팅"""
    results = {
        'strategy': strategy_name,
        'rank1': 0, 'rank2': 0, 'rank3': 0, 'rank4': 0, 'rank5': 0,
        'total': 0,
        'revenue': 0,
        'cost': 0
    }

    TICKET_PRICE = 1000
    PRIZES = {
        1: 2000000000,  # 평균 1등 상금
        2: 50000000,    # 평균 2등 상금
        3: 1500000,     # 평균 3등 상금
        4: 50000,       # 4등 고정
        5: 5000         # 5등 고정
    }

    for i in range(start_round, len(data)):
        history = data[:i]
        current = data[i]

        # 전략으로 번호 예측
        try:
            predicted = strategy_func(history, current['round'])
            if not predicted or len(predicted) != 6:
                continue
        except Exception as e:
            # 에러 발생 시 스킵
            continue

        # 등수 계산
        rank, count = calculate_rank(predicted, current['numbers'], current['bonus'])

        results['total'] += 1
        results['cost'] += TICKET_PRICE

        if rank > 0:
            results[f'rank{rank}'] += count
            results['revenue'] += PRIZES[rank]

    # 수익률 계산
    if results['cost'] > 0:
        results['roi'] = ((results['revenue'] - results['cost']) / results['cost']) * 100
    else:
        results['roi'] = 0

    # 4등 이상 비율
    if results['total'] > 0:
        results['rank4_plus_rate'] = ((results['rank1'] + results['rank2'] +
                                       results['rank3'] + results['rank4']) / results['total']) * 100
    else:
        results['rank4_plus_rate'] = 0

    return results


def main():
    """메인 실행"""
    print("=" * 80)
    print("물리/수학/통계 기반 로또 전략 백테스팅")
    print("=" * 80)
    print()

    # 데이터 로드
    data_path = '/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json'
    print(f"데이터 로딩 중: {data_path}")
    data = load_lotto_data(data_path)
    print(f"총 {len(data)}회차 데이터 로드 완료")
    print()

    # 15개 전략 정의
    strategies = [
        (strategy_entropy_maximization, "1.엔트로피_최대화"),
        (strategy_std_optimization, "2.표준편차_최적화"),
        (strategy_central_limit, "3.중심극한정리"),
        (strategy_bayesian, "4.베이지안_추론"),
        (strategy_chaos, "5.카오스_이론"),
        (strategy_wave, "6.웨이브_패턴"),
        (strategy_golden_spiral, "7.황금나선"),
        (strategy_fractal, "8.프랙탈"),
        (strategy_probability_density, "9.확률밀도"),
        (strategy_markov, "10.마르코프_체인"),
        (strategy_poisson, "11.푸아송_분포"),
        (strategy_geometric, "12.기하분포"),
        (strategy_harmonic_mean, "13.조화평균"),
        (strategy_least_squares, "14.최소자승법"),
        (strategy_monte_carlo, "15.몬테카를로"),
    ]

    # 백테스팅 실행
    all_results = []

    for strategy_func, strategy_name in strategies:
        print(f"백테스팅 중: {strategy_name}...")
        result = backtest_strategy(data, strategy_func, strategy_name, start_round=100)
        all_results.append(result)
        print(f"  완료 - 총 {result['total']}회 테스트")

    print()
    print("=" * 80)
    print("백테스팅 결과")
    print("=" * 80)
    print()

    # 테이블 헤더
    header = f"{'전략':<20} {'1등':>6} {'2등':>6} {'3등':>6} {'4등':>6} {'5등':>6} {'4등+율':>8} {'수익률':>10}"
    print(header)
    print("-" * 80)

    # 결과 출력
    for result in all_results:
        row = (f"{result['strategy']:<20} "
               f"{result['rank1']:>6} "
               f"{result['rank2']:>6} "
               f"{result['rank3']:>6} "
               f"{result['rank4']:>6} "
               f"{result['rank5']:>6} "
               f"{result['rank4_plus_rate']:>7.2f}% "
               f"{result['roi']:>9.1f}%")
        print(row)

    print("-" * 80)
    print()

    # 상세 통계
    print("=" * 80)
    print("상세 통계")
    print("=" * 80)
    print()

    for result in all_results:
        print(f"[{result['strategy']}]")
        print(f"  총 테스트: {result['total']:,}회")
        print(f"  총 비용: {result['cost']:,}원")
        print(f"  총 수익: {result['revenue']:,}원")
        print(f"  순손익: {result['revenue'] - result['cost']:,}원")
        print(f"  수익률: {result['roi']:.2f}%")
        print(f"  4등 이상 확률: {result['rank4_plus_rate']:.2f}%")
        print()

    # 결과를 JSON으로 저장
    output_path = '/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/physics_math_backtest_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"결과가 저장되었습니다: {output_path}")
    print()

    # 최고 성능 전략
    best_roi = max(all_results, key=lambda x: x['roi'])
    best_rank4_plus = max(all_results, key=lambda x: x['rank4_plus_rate'])

    print("=" * 80)
    print("최고 성능 전략")
    print("=" * 80)
    print(f"최고 수익률: {best_roi['strategy']} ({best_roi['roi']:.2f}%)")
    print(f"최고 4등+ 확률: {best_rank4_plus['strategy']} ({best_rank4_plus['rank4_plus_rate']:.2f}%)")
    print()


if __name__ == '__main__':
    main()
