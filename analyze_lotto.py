import json
from collections import Counter, defaultdict

# JSON 파일 읽기
with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r', encoding='utf-8') as f:
    lotto_data = json.load(f)

# 데이터 구조 확인
print("=" * 80)
print("데이터 구조 확인")
print("=" * 80)
print(f"전체 회차 수: {len(lotto_data)}")
if lotto_data:
    print(f"첫 번째 회차 샘플: {lotto_data[0]}")
    print()

# 1. 각 번호(1-45)의 출현 빈도
number_freq = Counter()
all_numbers = []

for draw in lotto_data:
    # 당첨번호 추출 (보너스 제외)
    if 'numbers' in draw:
        numbers = draw['numbers']
    elif 'drwtNo1' in draw:
        numbers = [draw.get(f'drwtNo{i}') for i in range(1, 7)]
        numbers = [n for n in numbers if n is not None]
    else:
        continue

    all_numbers.extend(numbers)
    number_freq.update(numbers)

print("=" * 80)
print("1. 각 번호(1-45)의 출현 빈도")
print("=" * 80)
for num in range(1, 46):
    freq = number_freq.get(num, 0)
    print(f"번호 {num:2d}: {freq:4d}회")
print()

# 2. 가장 많이 나온 번호 TOP 10
print("=" * 80)
print("2. 가장 많이 나온 번호 TOP 10")
print("=" * 80)
most_common = number_freq.most_common(10)
for rank, (num, freq) in enumerate(most_common, 1):
    print(f"{rank:2d}. 번호 {num:2d}: {freq:4d}회")
print()

# 3. 가장 적게 나온 번호 TOP 10
print("=" * 80)
print("3. 가장 적게 나온 번호 TOP 10")
print("=" * 80)
least_common = sorted(number_freq.items(), key=lambda x: x[1])[:10]
for rank, (num, freq) in enumerate(least_common, 1):
    print(f"{rank:2d}. 번호 {num:2d}: {freq:4d}회")
print()

# 4. 연속 번호 출현 패턴
print("=" * 80)
print("4. 연속 번호 출현 패턴 (n, n+1)")
print("=" * 80)
consecutive_pairs = Counter()

for draw in lotto_data:
    if 'numbers' in draw:
        numbers = sorted(draw['numbers'])
    elif 'drwtNo1' in draw:
        numbers = sorted([draw.get(f'drwtNo{i}') for i in range(1, 7) if draw.get(f'drwtNo{i}') is not None])
    else:
        continue

    # 연속 번호 찾기
    for i in range(len(numbers) - 1):
        if numbers[i+1] - numbers[i] == 1:
            consecutive_pairs[(numbers[i], numbers[i+1])] += 1

# 연속 번호 쌍을 빈도순으로 정렬
sorted_pairs = sorted(consecutive_pairs.items(), key=lambda x: x[1], reverse=True)
print(f"총 연속 번호 쌍 종류: {len(sorted_pairs)}개")
print(f"\n가장 많이 나온 연속 번호 쌍 TOP 20:")
for rank, (pair, freq) in enumerate(sorted_pairs[:20], 1):
    print(f"{rank:2d}. {pair[0]:2d},{pair[1]:2d}: {freq:3d}회")

# 회차당 연속 번호 쌍 개수 분포
consecutive_count_dist = Counter()
for draw in lotto_data:
    if 'numbers' in draw:
        numbers = sorted(draw['numbers'])
    elif 'drwtNo1' in draw:
        numbers = sorted([draw.get(f'drwtNo{i}') for i in range(1, 7) if draw.get(f'drwtNo{i}') is not None])
    else:
        continue

    count = 0
    for i in range(len(numbers) - 1):
        if numbers[i+1] - numbers[i] == 1:
            count += 1
    consecutive_count_dist[count] += 1

print(f"\n회차당 연속 번호 쌍 개수 분포:")
for count in sorted(consecutive_count_dist.keys()):
    freq = consecutive_count_dist[count]
    pct = freq / len(lotto_data) * 100
    print(f"연속 쌍 {count}개: {freq:4d}회 ({pct:5.2f}%)")
print()

# 5. 홀짝 비율 패턴
print("=" * 80)
print("5. 홀짝 비율 패턴")
print("=" * 80)
odd_even_pattern = Counter()

for draw in lotto_data:
    if 'numbers' in draw:
        numbers = draw['numbers']
    elif 'drwtNo1' in draw:
        numbers = [draw.get(f'drwtNo{i}') for i in range(1, 7) if draw.get(f'drwtNo{i}') is not None]
    else:
        continue

    odd_count = sum(1 for n in numbers if n % 2 == 1)
    even_count = len(numbers) - odd_count
    odd_even_pattern[(odd_count, even_count)] += 1

print("홀짝 비율 분포:")
for pattern in sorted(odd_even_pattern.keys()):
    freq = odd_even_pattern[pattern]
    pct = freq / len(lotto_data) * 100
    print(f"홀{pattern[0]}짝{pattern[1]}: {freq:4d}회 ({pct:5.2f}%)")
print()

# 추가 통계
print("=" * 80)
print("추가 통계")
print("=" * 80)
print(f"전체 분석 회차: {len(lotto_data)}회")
print(f"전체 추출된 번호 개수: {len(all_numbers)}개")
print(f"번호당 평균 출현 횟수: {len(all_numbers) / 45:.2f}회")
print(f"최다 출현 번호: {most_common[0][0]}번 ({most_common[0][1]}회)")
print(f"최소 출현 번호: {least_common[0][0]}번 ({least_common[0][1]}회)")
print(f"출현 횟수 편차: {most_common[0][1] - least_common[0][1]}회")
