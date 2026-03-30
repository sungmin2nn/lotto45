"""
AI/Machine Learning 기반 전략 (20개)
"""
import json
import random
import hashlib
from collections import Counter
from datetime import datetime

# 데이터 로드
with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

def get_all_numbers(data, end_round):
    """end_round 이전까지의 모든 번호"""
    numbers = []
    for item in data:
        if item['round'] < end_round:
            numbers.extend(item['numbers'])
    return numbers

def get_recent_numbers(data, end_round, n_rounds=10):
    """최근 n_rounds 회차의 번호"""
    numbers = []
    for item in data:
        if end_round - n_rounds <= item['round'] < end_round:
            numbers.extend(item['numbers'])
    return numbers

# 전략 1: 클러스터링 중심점 전략
def clustering_center_strategy(data, round_num):
    """K-means 클러스터링 중심점 기반 선택"""
    recent = get_recent_numbers(data, round_num, 20)
    if len(recent) < 30:
        return sorted(random.sample(range(1, 46), 6))

    # 간단한 3개 클러스터 중심 계산
    low = [n for n in recent if n <= 15]
    mid = [n for n in recent if 16 <= n <= 30]
    high = [n for n in recent if n > 30]

    centers = []
    if low: centers.append(sum(low) // len(low))
    if mid: centers.append(sum(mid) // len(mid))
    if high: centers.append(sum(high) // len(high))

    # 중심점 근처 번호 선택
    candidates = set()
    for c in centers:
        for offset in range(-3, 4):
            num = c + offset
            if 1 <= num <= 45:
                candidates.add(num)

    if len(candidates) >= 6:
        return sorted(random.sample(list(candidates), 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 2: 이상치 탐지 전략
def outlier_detection_strategy(data, round_num):
    """이상치(잘 안나온 번호) 기반 선택"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    avg = sum(counter.values()) / 45
    std = (sum((counter.get(i, 0) - avg)**2 for i in range(1, 46)) / 45) ** 0.5

    # 평균 - 1 표준편차 이하인 번호 (이상치)
    outliers = [i for i in range(1, 46) if counter.get(i, 0) < avg - std]

    if len(outliers) >= 6:
        return sorted(random.sample(outliers, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 3: 시계열 예측 전략
def time_series_strategy(data, round_num):
    """이동평균 기반 시계열 예측"""
    recent = get_recent_numbers(data, round_num, 5)
    if not recent:
        return sorted(random.sample(range(1, 46), 6))

    # 최근 5회차 평균
    avg = sum(recent) / len(recent)

    # 평균 근처 번호 + 변동성 반영
    candidates = []
    for i in range(1, 46):
        # 평균에서 멀수록 가중치 낮음
        distance = abs(i - avg)
        if distance < 15:
            candidates.extend([i] * (15 - int(distance)))

    if len(set(candidates)) >= 6:
        selected = set()
        while len(selected) < 6:
            selected.add(random.choice(candidates))
        return sorted(list(selected))
    return sorted(random.sample(range(1, 46), 6))

# 전략 4: 연관규칙 마이닝 전략
def association_rule_strategy(data, round_num):
    """함께 자주 등장하는 번호 쌍 기반"""
    pairs = Counter()
    for item in data:
        if item['round'] < round_num:
            nums = item['numbers']
            for i in range(len(nums)):
                for j in range(i+1, len(nums)):
                    pairs[(nums[i], nums[j])] += 1

    if not pairs:
        return sorted(random.sample(range(1, 46), 6))

    # 가장 자주 등장하는 쌍에서 번호 추출
    top_pairs = pairs.most_common(10)
    candidates = set()
    for (a, b), _ in top_pairs:
        candidates.add(a)
        candidates.add(b)

    if len(candidates) >= 6:
        return sorted(random.sample(list(candidates), 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 5: 앙상블 투표 전략
def ensemble_voting_strategy(data, round_num):
    """여러 전략의 투표 결과"""
    votes = Counter()

    # 여러 간단한 전략에서 투표
    strategies = [
        clustering_center_strategy,
        outlier_detection_strategy,
        time_series_strategy,
    ]

    for strat in strategies:
        try:
            nums = strat(data, round_num)
            for n in nums:
                votes[n] += 1
        except:
            pass

    if votes:
        top = [n for n, _ in votes.most_common(10)]
        if len(top) >= 6:
            return sorted(random.sample(top, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 6: 그래디언트 부스팅 모사 전략
def gradient_boost_strategy(data, round_num):
    """그래디언트 부스팅 개념 적용"""
    all_nums = get_all_numbers(data, round_num)
    recent = get_recent_numbers(data, round_num, 10)

    if not all_nums or not recent:
        return sorted(random.sample(range(1, 46), 6))

    all_counter = Counter(all_nums)
    recent_counter = Counter(recent)

    # 전체 대비 최근 변화율로 가중치 계산
    scores = {}
    for i in range(1, 46):
        all_rate = all_counter.get(i, 0) / max(len(all_nums), 1)
        recent_rate = recent_counter.get(i, 0) / max(len(recent), 1)
        # 최근 상승 추세인 번호에 가중치
        scores[i] = recent_rate - all_rate + 0.5

    # 상위 15개에서 선택
    top = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:15]
    return sorted(random.sample(top, 6))

# 전략 7: 신경망 시뮬레이션 전략
def neural_net_simulation_strategy(data, round_num):
    """간단한 신경망 개념 시뮬레이션"""
    recent = get_recent_numbers(data, round_num, 20)
    if not recent:
        return sorted(random.sample(range(1, 46), 6))

    # 입력층: 최근 빈도
    input_layer = [recent.count(i) for i in range(1, 46)]

    # 은닉층: 비선형 변환 (ReLU 유사)
    hidden = [max(0, x - sum(input_layer)/45) for x in input_layer]

    # 출력층: softmax 유사 정규화
    total = sum(hidden) + 0.001
    output = [h / total for h in hidden]

    # 확률적 선택
    candidates = list(range(1, 46))
    selected = set()
    while len(selected) < 6:
        r = random.random()
        cumsum = 0
        for i, p in enumerate(output):
            cumsum += p
            if r <= cumsum:
                selected.add(candidates[i])
                break
        else:
            selected.add(random.choice(candidates))

    return sorted(list(selected))

# 전략 8: Q-러닝 시뮬레이션 전략
def q_learning_strategy(data, round_num):
    """Q-러닝 개념 적용"""
    # Q-table 초기화 (번호별 보상)
    q_table = {i: 0.5 for i in range(1, 46)}

    # 과거 데이터로 Q-table 업데이트
    learning_rate = 0.1
    for item in data:
        if item['round'] < round_num:
            for n in item['numbers']:
                # 당첨 번호는 보상 증가
                q_table[n] += learning_rate * (1 - q_table[n])
            for n in range(1, 46):
                if n not in item['numbers']:
                    # 미당첨 번호는 약간 감소
                    q_table[n] -= learning_rate * 0.1 * q_table[n]

    # Q값 상위 15개에서 선택
    top = sorted(q_table.keys(), key=lambda x: q_table[x], reverse=True)[:15]
    return sorted(random.sample(top, 6))

# 전략 9: 유전 알고리즘 전략
def genetic_algorithm_strategy(data, round_num):
    """유전 알고리즘 기반 선택"""
    recent = get_recent_numbers(data, round_num, 30)
    if not recent:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(recent)

    # 초기 개체군 생성
    population = [sorted(random.sample(range(1, 46), 6)) for _ in range(20)]

    # 적합도 평가 함수
    def fitness(chromosome):
        return sum(counter.get(n, 0) for n in chromosome)

    # 3세대 진화
    for _ in range(3):
        # 적합도 순 정렬
        population.sort(key=fitness, reverse=True)

        # 상위 절반 선택
        survivors = population[:10]

        # 교차 및 돌연변이
        new_pop = survivors[:]
        for i in range(10):
            p1, p2 = random.sample(survivors, 2)
            # 교차
            child = sorted(set(p1[:3] + p2[3:]))
            while len(child) < 6:
                child.append(random.randint(1, 45))
            child = sorted(set(child))[:6]
            if len(child) == 6:
                new_pop.append(child)

        population = new_pop[:20]

    return sorted(population[0]) if population else sorted(random.sample(range(1, 46), 6))

# 전략 10: 랜덤 포레스트 투표 전략
def random_forest_strategy(data, round_num):
    """랜덤 포레스트 개념 적용"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)

    # 여러 "트리" 생성 (다른 랜덤 시드)
    votes = Counter()
    for tree_id in range(10):
        random.seed(round_num + tree_id)
        # 부트스트랩 샘플링
        sample = random.choices(all_nums, k=len(all_nums)//2)
        sample_counter = Counter(sample)
        top = sample_counter.most_common(10)
        for n, _ in top:
            votes[n] += 1

    random.seed()  # 시드 리셋
    top_votes = [n for n, _ in votes.most_common(15)]
    if len(top_votes) >= 6:
        return sorted(random.sample(top_votes, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 11: SVM 경계 전략
def svm_boundary_strategy(data, round_num):
    """SVM 결정 경계 개념"""
    recent = get_recent_numbers(data, round_num, 20)
    if not recent:
        return sorted(random.sample(range(1, 46), 6))

    # 최근 나온 번호와 안나온 번호의 "경계" 찾기
    appeared = set(recent)
    not_appeared = set(range(1, 46)) - appeared

    # 경계 근처 번호 (나온 번호 ±1)
    boundary = set()
    for n in appeared:
        for offset in [-1, 0, 1]:
            num = n + offset
            if 1 <= num <= 45:
                boundary.add(num)

    if len(boundary) >= 6:
        return sorted(random.sample(list(boundary), 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 12: 오토인코더 재구성 전략
def autoencoder_strategy(data, round_num):
    """오토인코더 개념 - 압축 후 복원"""
    recent = get_recent_numbers(data, round_num, 30)
    if not recent:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(recent)

    # 인코딩: 상위 10개로 압축
    encoded = [n for n, _ in counter.most_common(10)]

    # 디코딩: 압축된 정보에서 확장
    decoded = set(encoded)
    for n in encoded:
        for offset in [-2, -1, 1, 2]:
            num = n + offset
            if 1 <= num <= 45:
                decoded.add(num)

    if len(decoded) >= 6:
        return sorted(random.sample(list(decoded), 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 13: RNN 시퀀스 전략
def rnn_sequence_strategy(data, round_num):
    """RNN 시퀀스 학습 개념"""
    # 최근 5회차의 번호 시퀀스 분석
    sequences = []
    for item in data:
        if round_num - 5 <= item['round'] < round_num:
            sequences.append(sorted(item['numbers']))

    if len(sequences) < 3:
        return sorted(random.sample(range(1, 46), 6))

    # 시퀀스 패턴: 각 위치별 평균
    position_avgs = []
    for pos in range(6):
        vals = [seq[pos] for seq in sequences if len(seq) > pos]
        if vals:
            position_avgs.append(int(sum(vals) / len(vals)))

    # 평균 근처에서 선택
    candidates = set()
    for avg in position_avgs:
        for offset in range(-3, 4):
            num = avg + offset
            if 1 <= num <= 45:
                candidates.add(num)

    if len(candidates) >= 6:
        return sorted(random.sample(list(candidates), 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 14: GAN 생성 전략
def gan_generation_strategy(data, round_num):
    """GAN 개념 - 생성자/판별자 시뮬레이션"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)

    # 판별자: 실제 분포 학습
    real_dist = {i: counter.get(i, 0) for i in range(1, 46)}

    # 생성자: 실제 분포에 가까운 번호 생성 시도
    generated = []
    for _ in range(100):
        fake = sorted(random.sample(range(1, 46), 6))
        # 판별자 점수
        score = sum(real_dist[n] for n in fake)
        generated.append((score, fake))

    # 가장 높은 점수의 생성 결과
    generated.sort(reverse=True)
    return generated[0][1]

# 전략 15: 변분 오토인코더 전략
def vae_strategy(data, round_num):
    """VAE 개념 - 잠재 공간 샘플링"""
    recent = get_recent_numbers(data, round_num, 50)
    if not recent:
        return sorted(random.sample(range(1, 46), 6))

    # 잠재 공간: 평균과 분산
    mean = sum(recent) / len(recent)
    variance = sum((n - mean)**2 for n in recent) / len(recent)
    std = variance ** 0.5

    # 잠재 공간에서 샘플링
    samples = []
    for _ in range(20):
        z = random.gauss(mean, std)
        num = int(round(z))
        if 1 <= num <= 45:
            samples.append(num)

    if len(set(samples)) >= 6:
        return sorted(random.sample(list(set(samples)), 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 16: 어텐션 메커니즘 전략
def attention_strategy(data, round_num):
    """Attention 메커니즘 개념"""
    recent_rounds = []
    for item in data:
        if round_num - 10 <= item['round'] < round_num:
            recent_rounds.append(item)

    if len(recent_rounds) < 3:
        return sorted(random.sample(range(1, 46), 6))

    # 각 회차에 어텐션 가중치 (최근일수록 높음)
    attention_weights = []
    for i, item in enumerate(recent_rounds):
        weight = (i + 1) / len(recent_rounds)  # 최근일수록 높음
        attention_weights.append(weight)

    # 가중치 적용하여 번호 집계
    weighted_votes = Counter()
    for item, weight in zip(recent_rounds, attention_weights):
        for n in item['numbers']:
            weighted_votes[n] += weight

    top = [n for n, _ in weighted_votes.most_common(15)]
    if len(top) >= 6:
        return sorted(random.sample(top, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 17: 트랜스포머 위치 인코딩 전략
def transformer_position_strategy(data, round_num):
    """트랜스포머 위치 인코딩 개념"""
    import math

    # 번호별 위치 인코딩
    position_encoding = {}
    for i in range(1, 46):
        # sin/cos 인코딩
        pe = math.sin(i / 10) + math.cos(i / 10)
        position_encoding[i] = pe

    recent = get_recent_numbers(data, round_num, 20)
    if not recent:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(recent)

    # 빈도 + 위치 인코딩 결합
    scores = {}
    for i in range(1, 46):
        freq = counter.get(i, 0)
        scores[i] = freq + position_encoding[i] * 2

    top = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:15]
    return sorted(random.sample(top, 6))

# 전략 18: 메타러닝 전략
def meta_learning_strategy(data, round_num):
    """메타러닝 개념 - 전략의 전략"""
    # 여러 전략 결과 수집
    all_strategies = [
        clustering_center_strategy,
        time_series_strategy,
        genetic_algorithm_strategy,
        attention_strategy,
    ]

    all_results = []
    for strat in all_strategies:
        try:
            result = strat(data, round_num)
            all_results.extend(result)
        except:
            pass

    if all_results:
        counter = Counter(all_results)
        top = [n for n, _ in counter.most_common(10)]
        if len(top) >= 6:
            return sorted(random.sample(top, 6))

    return sorted(random.sample(range(1, 46), 6))

# 전략 19: 베이지안 신경망 전략
def bayesian_neural_strategy(data, round_num):
    """베이지안 신경망 개념 - 불확실성 모델링"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    total = len(all_nums)

    # 사전 확률 (균등)
    prior = 1/45

    # 사후 확률 계산
    posterior = {}
    for i in range(1, 46):
        likelihood = counter.get(i, 0) / total
        posterior[i] = likelihood * prior

    # 불확실성이 높은 번호 (중간 확률)
    sorted_nums = sorted(posterior.keys(), key=lambda x: abs(posterior[x] - 1/45))

    return sorted(random.sample(sorted_nums[:20], 6))

# 전략 20: 강화학습 보상 전략
def reinforcement_reward_strategy(data, round_num):
    """강화학습 보상 기반 선택"""
    # 각 번호의 누적 보상
    rewards = {i: 0 for i in range(1, 46)}

    for item in data:
        if item['round'] < round_num:
            # 당첨 번호는 +1 보상
            for n in item['numbers']:
                rewards[n] += 1
            # 연속 당첨은 추가 보상
            for i in range(len(item['numbers']) - 1):
                if item['numbers'][i+1] - item['numbers'][i] == 1:
                    rewards[item['numbers'][i]] += 0.5
                    rewards[item['numbers'][i+1]] += 0.5

    # 보상 상위에서 선택
    top = sorted(rewards.keys(), key=lambda x: rewards[x], reverse=True)[:15]
    return sorted(random.sample(top, 6))


# 전략 목록
STRATEGIES = {
    '클러스터링_중심': clustering_center_strategy,
    '이상치_탐지': outlier_detection_strategy,
    '시계열_예측': time_series_strategy,
    '연관규칙_마이닝': association_rule_strategy,
    '앙상블_투표': ensemble_voting_strategy,
    '그래디언트_부스트': gradient_boost_strategy,
    '신경망_시뮬레이션': neural_net_simulation_strategy,
    'Q러닝': q_learning_strategy,
    '유전_알고리즘': genetic_algorithm_strategy,
    '랜덤_포레스트': random_forest_strategy,
    'SVM_경계': svm_boundary_strategy,
    '오토인코더': autoencoder_strategy,
    'RNN_시퀀스': rnn_sequence_strategy,
    'GAN_생성': gan_generation_strategy,
    'VAE_샘플링': vae_strategy,
    '어텐션_메커니즘': attention_strategy,
    '트랜스포머_위치': transformer_position_strategy,
    '메타러닝': meta_learning_strategy,
    '베이지안_신경망': bayesian_neural_strategy,
    '강화학습_보상': reinforcement_reward_strategy,
}

if __name__ == '__main__':
    print(f"AI/ML 전략 {len(STRATEGIES)}개 로드됨")
    for name in STRATEGIES.keys():
        print(f"  - {name}")
