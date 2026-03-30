"""
금융/경제 기반 전략 (20개)
"""
import json
import random
import math
from collections import Counter
from datetime import datetime

with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

def get_all_numbers(data, end_round):
    numbers = []
    for item in data:
        if item['round'] < end_round:
            numbers.extend(item['numbers'])
    return numbers

# 전략 1: 피보나치 되돌림 전략
def fibonacci_retracement_strategy(data, round_num):
    """피보나치 되돌림 레벨"""
    # 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%
    levels = [0, 23.6, 38.2, 50, 61.8, 78.6, 100]
    # 1-45 범위에 매핑
    nums = [int(l * 45 / 100) + 1 for l in levels]
    nums = [n for n in nums if 1 <= n <= 45]

    if len(nums) < 6:
        nums += random.sample([n for n in range(1, 46) if n not in nums], 6 - len(nums))

    return sorted(random.sample(list(set(nums)), 6))

# 전략 2: 이동평균선 전략
def moving_average_strategy(data, round_num):
    """5일, 20일, 60일, 120일 이동평균"""
    ma_periods = [5, 20, 60, 120]
    # 비율로 변환
    nums = [5, 20, 12, 6, 10, 15, 30, 40, 45, 25, 35]
    valid = [n for n in nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 3: RSI 전략
def rsi_strategy(data, round_num):
    """RSI 과매수/과매도 레벨"""
    # 30 이하: 과매도, 70 이상: 과매수
    rsi_nums = [30, 70, 50, 14, 7, 21, 28, 42, 35, 40, 45, 25, 15]
    valid = [n for n in rsi_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 4: 볼린저 밴드 전략
def bollinger_band_strategy(data, round_num):
    """볼린저 밴드 ±2 표준편차"""
    # 중심 20, 상단/하단
    center = 23  # 1-45의 중앙
    std = 7
    bands = [center - 2*std, center - std, center, center + std, center + 2*std]
    bands += [center - 3, center + 3, center - 5, center + 5]

    valid = list(set([n for n in bands if 1 <= n <= 45]))
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))

    return sorted(random.sample(valid, 6))

# 전략 5: MACD 전략
def macd_strategy(data, round_num):
    """MACD (12, 26, 9)"""
    macd_nums = [12, 26, 9, 17, 35, 21, 3, 6, 14, 28, 38, 44]
    valid = [n for n in macd_nums if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 6: 황금 비율 포트폴리오 전략
def golden_portfolio_strategy(data, round_num):
    """61.8% : 38.2% 비율"""
    golden = 0.618
    # 6개 번호를 황금비로 분배
    low_count = int(6 * golden)  # 4개는 낮은 범위
    high_count = 6 - low_count   # 2개는 높은 범위

    low = random.sample(range(1, 28), low_count)
    high = random.sample(range(28, 46), high_count)

    return sorted(low + high)

# 전략 7: 켈리 기준 전략
def kelly_criterion_strategy(data, round_num):
    """켈리 공식 기반 베팅"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    total = len(all_nums)

    # 승률(p)과 배당률(b) 시뮬레이션
    kelly_scores = {}
    for i in range(1, 46):
        p = counter.get(i, 0) / total  # 등장 확률
        b = 45 / max(counter.get(i, 1), 1)  # 희소할수록 높은 배당
        # f* = (bp - q) / b
        q = 1 - p
        if b > 0:
            kelly = (b * p - q) / b
        else:
            kelly = 0
        kelly_scores[i] = kelly

    top = sorted(kelly_scores.keys(), key=lambda x: kelly_scores[x], reverse=True)[:15]
    return sorted(random.sample(top, 6))

# 전략 8: 샤프 비율 전략
def sharpe_ratio_strategy(data, round_num):
    """위험 대비 수익률"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)

    # 각 번호의 "수익률"과 "변동성" 계산
    sharpe = {}
    for i in range(1, 46):
        returns = counter.get(i, 0)
        # 변동성: 번호값의 표준편차 영향
        volatility = abs(i - 23) / 22 + 0.1
        sharpe[i] = returns / volatility

    top = sorted(sharpe.keys(), key=lambda x: sharpe[x], reverse=True)[:15]
    return sorted(random.sample(top, 6))

# 전략 9: 달러 코스트 애버리징 전략
def dca_strategy(data, round_num):
    """정기적 분산 투자 개념"""
    # 균등 분배: 1-45를 6등분
    segments = []
    for i in range(6):
        start = i * 7 + 1
        end = min(start + 7, 46)
        segments.append(random.randint(start, end - 1))

    return sorted(segments)

# 전략 10: 옵션 스트라이크 전략
def option_strike_strategy(data, round_num):
    """옵션 행사가격 패턴"""
    # ATM (현재가), ITM, OTM
    atm = 23  # 중앙
    strikes = [atm - 10, atm - 5, atm, atm + 5, atm + 10, atm - 15, atm + 15]
    valid = [n for n in strikes if 1 <= n <= 45]

    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))

    return sorted(random.sample(valid, 6))

# 전략 11: 헤지 전략
def hedge_strategy(data, round_num):
    """헤지: 상반된 포지션"""
    # 낮은 번호와 높은 번호의 페어링
    pairs = []
    for i in range(1, 23):
        pair_num = 46 - i  # 대칭
        if pair_num <= 45:
            pairs.append((i, pair_num))

    selected_pairs = random.sample(pairs, 3)
    result = []
    for a, b in selected_pairs:
        result.extend([a, b])

    return sorted(result)

# 전략 12: 스프레드 전략
def spread_strategy(data, round_num):
    """가격 스프레드 개념"""
    # 연속된 번호들의 스프레드
    start = random.randint(5, 35)
    spread = [start + i for i in range(-2, 4) if 1 <= start + i <= 45]

    while len(spread) < 6:
        new = random.randint(1, 45)
        if new not in spread:
            spread.append(new)

    return sorted(spread[:6])

# 전략 13: 변동성 전략
def volatility_strategy(data, round_num):
    """고변동성 시기 패턴"""
    # 최근 변동이 큰 번호 선택
    recent = []
    for item in data:
        if round_num - 10 <= item['round'] < round_num:
            recent.append(set(item['numbers']))

    if len(recent) < 2:
        return sorted(random.sample(range(1, 46), 6))

    # 번호별 등장/미등장 변동성
    volatility = {}
    for i in range(1, 46):
        appearances = sum(1 for r in recent if i in r)
        volatility[i] = abs(appearances - len(recent) / 2)

    # 변동성 높은 번호 선택
    high_vol = sorted(volatility.keys(), key=lambda x: volatility[x], reverse=True)[:15]
    return sorted(random.sample(high_vol, 6))

# 전략 14: 모멘텀 전략
def momentum_strategy(data, round_num):
    """상승 모멘텀 번호"""
    early = []
    late = []

    for item in data:
        if round_num - 20 <= item['round'] < round_num - 10:
            early.extend(item['numbers'])
        elif round_num - 10 <= item['round'] < round_num:
            late.extend(item['numbers'])

    if not early or not late:
        return sorted(random.sample(range(1, 46), 6))

    early_counter = Counter(early)
    late_counter = Counter(late)

    # 모멘텀: 최근 증가한 번호
    momentum = {}
    for i in range(1, 46):
        early_rate = early_counter.get(i, 0) / max(len(early), 1)
        late_rate = late_counter.get(i, 0) / max(len(late), 1)
        momentum[i] = late_rate - early_rate

    top = sorted(momentum.keys(), key=lambda x: momentum[x], reverse=True)[:15]
    return sorted(random.sample(top, 6))

# 전략 15: 평균 회귀 전략
def mean_reversion_strategy(data, round_num):
    """평균으로 회귀 예측"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    avg = sum(counter.values()) / 45

    # 평균 이하인 번호들 (회귀 대상)
    below = [n for n in range(1, 46) if counter.get(n, 0) < avg * 0.8]

    if len(below) >= 6:
        return sorted(random.sample(below, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 16: 베타 전략
def beta_strategy(data, round_num):
    """시장 베타 개념"""
    # 베타 = 공분산 / 분산
    # 베타 > 1: 공격적, 베타 < 1: 방어적

    recent = []
    for item in data:
        if round_num - 20 <= item['round'] < round_num:
            recent.append(item['numbers'])

    if len(recent) < 5:
        return sorted(random.sample(range(1, 46), 6))

    # 각 번호의 "베타" 계산 (함께 등장하는 패턴)
    beta = {i: 0 for i in range(1, 46)}
    for nums in recent:
        for n in nums:
            beta[n] += 1

    # 중간 베타 번호 선택 (너무 높지도 낮지도 않은)
    sorted_beta = sorted(beta.keys(), key=lambda x: beta[x])
    mid_beta = sorted_beta[10:35]

    return sorted(random.sample(mid_beta, 6))

# 전략 17: 알파 전략
def alpha_strategy(data, round_num):
    """초과 수익 알파 추구"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    avg = sum(counter.values()) / 45

    # 알파: 평균 대비 초과 성과
    alpha = {}
    for i in range(1, 46):
        alpha[i] = counter.get(i, 0) - avg

    # 양의 알파 번호
    positive_alpha = [n for n in range(1, 46) if alpha[n] > 0]

    if len(positive_alpha) >= 6:
        return sorted(random.sample(positive_alpha, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 18: 배당 전략
def dividend_strategy(data, round_num):
    """배당 수익률 패턴"""
    # 안정적이고 꾸준한 번호
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    # 최근 20회차에서 안정적으로 등장
    stable = []
    for item in data:
        if round_num - 20 <= item['round'] < round_num:
            stable.extend(item['numbers'])

    counter = Counter(stable)
    # 일정 횟수 이상 등장한 번호
    regular = [n for n, c in counter.items() if c >= 3]

    if len(regular) >= 6:
        return sorted(random.sample(regular, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 19: 성장주 전략
def growth_stock_strategy(data, round_num):
    """성장세 높은 번호"""
    # 시간에 따른 등장 빈도 증가
    periods = [[], [], [], []]  # 4개 기간으로 분할

    for item in data:
        r = item['round']
        if r < round_num - 60:
            continue
        idx = (round_num - r - 1) // 15
        if 0 <= idx < 4:
            periods[idx].extend(item['numbers'])

    if all(len(p) > 0 for p in periods):
        growth = {}
        for i in range(1, 46):
            counts = [p.count(i) for p in periods]
            # 최근일수록 높은 가중치
            growth[i] = sum(c * (idx + 1) for idx, c in enumerate(counts))

        top = sorted(growth.keys(), key=lambda x: growth[x], reverse=True)[:15]
        return sorted(random.sample(top, 6))

    return sorted(random.sample(range(1, 46), 6))

# 전략 20: 가치주 전략
def value_stock_strategy(data, round_num):
    """저평가된 번호 (잘 안나왔지만 가치 있는)"""
    all_nums = get_all_numbers(data, round_num)
    if not all_nums:
        return sorted(random.sample(range(1, 46), 6))

    counter = Counter(all_nums)
    avg = sum(counter.values()) / 45

    # 평균 근처지만 약간 아래인 번호 (저평가)
    value = [n for n in range(1, 46) if 0.7 * avg <= counter.get(n, 0) < avg]

    if len(value) >= 6:
        return sorted(random.sample(value, 6))
    return sorted(random.sample(range(1, 46), 6))


# 전략 목록
STRATEGIES = {
    '피보나치_되돌림': fibonacci_retracement_strategy,
    '이동평균선': moving_average_strategy,
    'RSI': rsi_strategy,
    '볼린저_밴드': bollinger_band_strategy,
    'MACD': macd_strategy,
    '황금_포트폴리오': golden_portfolio_strategy,
    '켈리_기준': kelly_criterion_strategy,
    '샤프_비율': sharpe_ratio_strategy,
    'DCA': dca_strategy,
    '옵션_스트라이크': option_strike_strategy,
    '헤지': hedge_strategy,
    '스프레드': spread_strategy,
    '변동성': volatility_strategy,
    '모멘텀': momentum_strategy,
    '평균_회귀': mean_reversion_strategy,
    '베타': beta_strategy,
    '알파': alpha_strategy,
    '배당': dividend_strategy,
    '성장주': growth_stock_strategy,
    '가치주': value_stock_strategy,
}

if __name__ == '__main__':
    print(f"금융 전략 {len(STRATEGIES)}개 로드됨")
    for name in STRATEGIES.keys():
        print(f"  - {name}")
