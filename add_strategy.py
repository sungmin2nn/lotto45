#!/usr/bin/env python3
"""
새로운 전략 추가 및 검증 시스템
- 새 전략을 백테스팅하고 결과 저장
- 대시보드에 자동 추가
"""

import json
import os
import random
from datetime import datetime

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOTTO_DATA_FILE = os.path.join(BASE_DIR, 'lotto_data.json')
BACKTEST_RESULTS_FILE = os.path.join(BASE_DIR, 'backtest_results.json')
BACKTEST_DETAIL_FILE = os.path.join(BASE_DIR, 'backtest_results_detail.json')
STRATEGY_DESC_FILE = os.path.join(BASE_DIR, 'strategy_descriptions.json')
USER_STRATEGIES_FILE = os.path.join(BASE_DIR, 'user_strategies.py')

# 상금 테이블
PRIZE = {
    1: 2000000000,  # 1등: 20억
    2: 50000000,    # 2등: 5천만
    3: 1500000,     # 3등: 150만
    4: 50000,       # 4등: 5만
    5: 5000         # 5등: 5천
}

def load_lotto_data():
    """로또 데이터 로드"""
    with open(LOTTO_DATA_FILE, 'r') as f:
        data = json.load(f)
    return sorted(data, key=lambda x: x['round'])

def check_match(predicted, actual, bonus):
    """당첨 확인"""
    matches = len(set(predicted) & set(actual))
    has_bonus = bonus in predicted

    if matches == 6:
        return 1, matches
    elif matches == 5 and has_bonus:
        return 2, matches
    elif matches == 5:
        return 3, matches
    elif matches == 4:
        return 4, matches
    elif matches == 3:
        return 5, matches
    return 0, matches

def backtest_strategy(strategy_func, lotto_data, strategy_name):
    """전략 백테스팅 실행"""
    results = {
        'wins': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        'total': 0,
        'total_prize': 0,
        'total_cost': 0,
        'details': []
    }

    for i, draw in enumerate(lotto_data):
        round_num = draw['round']
        actual = draw['numbers']
        bonus = draw['bonus']

        # 이전 데이터로 예측 (최소 10회차 이후부터)
        if i < 10:
            continue

        past_data = lotto_data[:i]

        try:
            predicted = strategy_func(past_data, round_num)
            if not predicted or len(predicted) != 6:
                continue
            predicted = sorted(predicted)
        except Exception as e:
            continue

        rank, matches = check_match(predicted, actual, bonus)
        results['total'] += 1
        results['total_cost'] += 1000

        if rank > 0:
            results['wins'][rank] += 1
            results['total_prize'] += PRIZE[rank]

            if rank <= 4:  # 4등 이상만 상세 기록
                results['details'].append({
                    'round': round_num,
                    'rank': rank,
                    'matches': matches,
                    'predicted': predicted,
                    'actual': actual,
                    'bonus': bonus
                })

    # ROI 계산
    if results['total_cost'] > 0:
        results['roi'] = ((results['total_prize'] - results['total_cost']) / results['total_cost']) * 100
    else:
        results['roi'] = 0

    # 4등+ 달성률
    wins_4plus = results['wins'][2] + results['wins'][3] + results['wins'][4]
    results['rate_4plus'] = (wins_4plus / results['total'] * 100) if results['total'] > 0 else 0

    return results

def save_strategy_to_file(name, code, category, description, formula, example):
    """전략 코드를 파일에 저장"""
    # user_strategies.py 업데이트
    if os.path.exists(USER_STRATEGIES_FILE):
        with open(USER_STRATEGIES_FILE, 'r') as f:
            content = f.read()
    else:
        content = '''#!/usr/bin/env python3
"""사용자 정의 전략 모음"""
import random

USER_STRATEGIES = {}

'''

    # 전략 함수 추가 (숫자로 시작하면 strategy_ 접두사 추가)
    func_name = name.replace(' ', '_').replace('-', '_')
    if func_name[0].isdigit():
        func_name = 'strategy_' + func_name
    new_code = f'''
def {func_name}(data, round_num):
    """{name}: {description}"""
{code}

USER_STRATEGIES['{name}'] = {func_name}
'''

    # 기존에 같은 이름의 전략이 있으면 교체
    if f"USER_STRATEGIES['{name}']" in content:
        # 기존 전략 삭제 (간단한 방법)
        lines = content.split('\n')
        new_lines = []
        skip = False
        for line in lines:
            if f'def {func_name}(' in line:
                skip = True
            if skip and line.startswith('USER_STRATEGIES['):
                skip = False
                if f"USER_STRATEGIES['{name}']" not in line:
                    new_lines.append(line)
                continue
            if not skip:
                new_lines.append(line)
        content = '\n'.join(new_lines)

    content += new_code

    with open(USER_STRATEGIES_FILE, 'w') as f:
        f.write(content)

def update_backtest_results(name, results):
    """백테스트 결과 파일 업데이트 (가벼운 통계는 backtest_results.json,
    회차별 상세는 backtest_results_detail.json — 모바일에서 홈 화면마다
    수 MB 상세 데이터까지 받지 않도록 분리되어 있다)"""
    if os.path.exists(BACKTEST_RESULTS_FILE):
        with open(BACKTEST_RESULTS_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {'statistics': {}, 'predictions': [], 'strategies': []}

    if os.path.exists(BACKTEST_DETAIL_FILE):
        with open(BACKTEST_DETAIL_FILE, 'r') as f:
            detail = json.load(f)
    else:
        detail = {'results': {}}
    detail.setdefault('results', {})

    # 통계 업데이트
    data['statistics'][name] = {
        'total': results['total'],
        'roi': results['roi'],
        '1등': results['wins'][1],
        '2등': results['wins'][2],
        '3등': results['wins'][3],
        '4등': results['wins'][4],
        '5등': results['wins'][5]
    }

    # 회차별 결과 업데이트 (상세 파일)
    for item in results['details']:
        round_str = str(item['round'])
        if round_str not in detail['results']:
            detail['results'][round_str] = {}

        rank_str = f"{item['rank']}등"
        detail['results'][round_str][name] = {
            'numbers': item['predicted'],
            'actual': item['actual'],
            'match': item['matches'],
            'rank': rank_str,
            'bonus': item.get('bonus')
        }

    # strategies 배열 업데이트
    existing = next((s for s in data.get('strategies', []) if s['name'] == name), None)
    if existing:
        existing['roi'] = results['roi']
        existing['wins'] = results['wins']
    else:
        data.setdefault('strategies', []).append({
            'name': name,
            'roi': results['roi'],
            'wins': results['wins']
        })

    data['generated_at'] = datetime.now().isoformat()
    detail['generated_at'] = data['generated_at']

    with open(BACKTEST_RESULTS_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(BACKTEST_DETAIL_FILE, 'w') as f:
        json.dump(detail, f, ensure_ascii=False, indent=2)

def update_strategy_descriptions(name, category, description, formula, example, results):
    """전략 설명 파일 업데이트"""
    if os.path.exists(STRATEGY_DESC_FILE):
        with open(STRATEGY_DESC_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    # 당첨 이력 생성
    win_history = []
    for detail in results['details']:
        if detail['rank'] <= 4:  # 4등 이상
            win_history.append({
                'round': detail['round'],
                'rank': detail['rank'],
                'numbers': detail['predicted'],
                'actual': detail['actual'],
                'matches': detail['matches'],
                'bonus': detail['rank'] == 2
            })

    data[name] = {
        'name': name,
        'category': category,
        'description': description,
        'formula': formula,
        'example': example,
        'win_history': win_history[:10]  # 최대 10개
    }

    with open(STRATEGY_DESC_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_new_strategy(name, code, category='사용자', description='', formula='', example=''):
    """
    새로운 전략 추가 메인 함수

    Parameters:
    - name: 전략 이름
    - code: 전략 코드 (들여쓰기 4칸, data와 round_num 사용 가능)
    - category: 카테고리 (수학, AI/ML, 역사 등)
    - description: 간단한 설명
    - formula: 상세 공식/규칙
    - example: 예시 번호

    Returns:
    - dict: 백테스트 결과
    """
    print(f"\n{'='*60}")
    print(f"  새 전략 추가: {name}")
    print(f"{'='*60}")

    # 1. 전략 함수 생성
    print("\n[1] 전략 함수 생성 중...")
    func_code = f'''
def temp_strategy(data, round_num):
{code}
'''

    # 실행 환경 설정
    exec_globals = {'random': random}
    try:
        exec(func_code, exec_globals)
        strategy_func = exec_globals['temp_strategy']
        print("  ✅ 함수 생성 성공")
    except Exception as e:
        print(f"  ❌ 함수 생성 실패: {e}")
        return None

    # 2. 테스트 실행
    print("\n[2] 테스트 실행 (10회)...")
    lotto_data = load_lotto_data()
    for i in range(3):
        try:
            test_nums = strategy_func(lotto_data[-100:], lotto_data[-1]['round'] + 1)
            if test_nums and len(test_nums) == 6 and all(1 <= n <= 45 for n in test_nums):
                print(f"  테스트 {i+1}: {sorted(test_nums)} ✅")
            else:
                print(f"  ❌ 잘못된 결과: {test_nums}")
                return None
        except Exception as e:
            print(f"  ❌ 테스트 실패: {e}")
            return None

    # 3. 백테스팅
    print("\n[3] 백테스팅 실행 중...")
    results = backtest_strategy(strategy_func, lotto_data, name)

    print(f"\n  📊 백테스트 결과:")
    print(f"  {'─'*40}")
    print(f"  총 테스트: {results['total']}회")
    print(f"  ROI: {results['roi']:.2f}%")
    print(f"  2등: {results['wins'][2]}회")
    print(f"  3등: {results['wins'][3]}회")
    print(f"  4등: {results['wins'][4]}회")
    print(f"  5등: {results['wins'][5]}회")
    print(f"  4등+ 달성률: {results['rate_4plus']:.2f}%")

    # 4. 파일 저장
    print("\n[4] 결과 저장 중...")

    # 전략 코드 저장
    save_strategy_to_file(name, code, category, description, formula, example)
    print(f"  ✅ 전략 코드 저장: user_strategies.py")

    # 백테스트 결과 저장
    update_backtest_results(name, results)
    print(f"  ✅ 백테스트 결과 저장: backtest_results.json")

    # 전략 설명 저장
    if not example:
        example = str(sorted(strategy_func(lotto_data[-100:], lotto_data[-1]['round'] + 1)))
    update_strategy_descriptions(name, category, description, formula, example, results)
    print(f"  ✅ 전략 설명 저장: strategy_descriptions.json")

    # 5. 결과 요약
    print(f"\n{'='*60}")
    print(f"  완료!")
    print(f"{'='*60}")

    roi_status = "🔥 우수" if results['roi'] >= 50 else "✅ 양호" if results['roi'] > 0 else "⚠️ 손실"
    print(f"  전략: {name}")
    print(f"  ROI: {results['roi']:.2f}% {roi_status}")
    print(f"  4등 이상: {results['wins'][2] + results['wins'][3] + results['wins'][4]}회")

    if results['details']:
        print(f"\n  최근 당첨 기록:")
        for d in results['details'][-3:]:
            print(f"    {d['round']}회 {d['rank']}등 - 예측:{d['predicted']}")

    print(f"\n  💡 대시보드에서 확인: https://sungmin2nn.github.io/lotto45/")
    print(f"{'='*60}\n")

    return results


# 사용 예시
if __name__ == '__main__':
    # 예시: 3의 배수 전략
    result = add_new_strategy(
        name="3의_배수",
        code='''    # 3의 배수 번호 중심 선택
    multiples_of_3 = [n for n in range(3, 46, 3)]  # [3,6,9,...,45]
    others = [n for n in range(1, 46) if n % 3 != 0]

    # 3의 배수 4개 + 나머지 2개
    selected = random.sample(multiples_of_3, 4)
    selected += random.sample(others, 2)
    return sorted(selected)''',
        category="수학",
        description="3의 배수 번호 중심 선택 전략",
        formula="3의 배수: [3,6,9,12,15,18,21,24,27,30,33,36,39,42,45]\\n3의 배수 4개 + 나머지 2개 선택",
        example="[3, 9, 18, 27, 36, 44]"
    )
