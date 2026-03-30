"""
화학/원소 기반 전략 (20개)
"""
import json
import random
from collections import Counter

with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

# 전략 1: 원자번호 전략
def atomic_number_strategy(data, round_num):
    """원자번호 1-45 (수소~로듐)"""
    # 주요 원소: H(1), He(2), C(6), N(7), O(8), Fe(26), Au(79->34)
    important = [1, 2, 6, 7, 8, 11, 12, 13, 14, 17, 19, 20, 26, 29, 30]
    valid = [n for n in important if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 2: 비활성 기체 전략
def noble_gas_strategy(data, round_num):
    """비활성 기체 원자번호"""
    # He(2), Ne(10), Ar(18), Kr(36), Xe(54->9), Rn(86->41)
    noble = [2, 10, 18, 36, 9, 41, 4, 20, 28, 44]
    valid = [n for n in noble if 1 <= n <= 45]
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))
    return sorted(random.sample(valid, 6))

# 전략 3: 알칼리 금속 전략
def alkali_metal_strategy(data, round_num):
    """알칼리 금속 원자번호"""
    # Li(3), Na(11), K(19), Rb(37), Cs(55->10)
    alkali = [3, 11, 19, 37, 10, 5, 13, 21, 29, 45]
    valid = [n for n in alkali if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 4: 원자량 전략
def atomic_mass_strategy(data, round_num):
    """주요 원소 원자량 (정수부)"""
    # H:1, He:4, C:12, N:14, O:16, Na:23, Fe:56->11, Cu:64->19
    masses = [1, 4, 12, 14, 16, 23, 11, 19, 24, 27, 28, 32, 35, 39, 40]
    valid = [n for n in masses if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 5: 주기율표 주기 전략
def periodic_period_strategy(data, round_num):
    """주기율표 주기별 원소"""
    # 1주기: 1-2, 2주기: 3-10, 3주기: 11-18, 4주기: 19-36
    period1 = [1, 2]
    period2 = list(range(3, 11))
    period3 = list(range(11, 19))
    period4 = list(range(19, 37))

    # 각 주기에서 선택
    selected = []
    selected += random.sample(period1, 1)
    selected += random.sample(period2, 2)
    selected += random.sample(period3, 1)
    selected += random.sample([n for n in period4 if n <= 45], 2)

    return sorted(selected)

# 전략 6: 전자 껍질 전략
def electron_shell_strategy(data, round_num):
    """전자 껍질 최대 전자 수 2n²"""
    # K:2, L:8, M:18, N:32
    shells = [2, 8, 18, 32, 10, 20, 28, 36, 40, 44]
    valid = [n for n in shells if 1 <= n <= 45]
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))
    return sorted(random.sample(valid, 6))

# 전략 7: 전기음성도 전략
def electronegativity_strategy(data, round_num):
    """전기음성도 * 10"""
    # F:4.0, O:3.5, Cl:3.0, N:3.0, C:2.5, H:2.1
    electroneg = [40, 35, 30, 25, 21, 16, 12, 10, 8, 5, 20, 15, 28, 32, 38]
    valid = [n for n in electroneg if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 8: 이온화 에너지 전략
def ionization_energy_strategy(data, round_num):
    """제1 이온화 에너지 패턴"""
    # 주기율표 패턴: 같은 주기 내 증가, 새 주기 시작시 감소
    energies = [13, 24, 5, 9, 8, 11, 14, 13, 17, 21, 5, 7, 6, 8, 10, 10, 13, 16]
    valid = list(set([n for n in energies if 1 <= n <= 45]))
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))
    return sorted(random.sample(valid, 6))

# 전략 9: 산화 상태 전략
def oxidation_state_strategy(data, round_num):
    """일반적인 산화 상태"""
    # -3 ~ +7 -> 1~11로 매핑
    states = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    # 금속의 일반적 산화수
    metal_states = [1, 2, 3, 12, 13, 22, 23, 32, 33, 42, 43]

    valid = list(set([n for n in states + metal_states if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 10: 화학 반응식 전략
def chemical_equation_strategy(data, round_num):
    """화학 반응식 계수"""
    # 2H2 + O2 -> 2H2O, 4Fe + 3O2 -> 2Fe2O3
    coefficients = [1, 2, 3, 4, 5, 6, 12, 13, 23, 24, 34, 35, 45]
    valid = [n for n in coefficients if 1 <= n <= 45]
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))
    return sorted(random.sample(valid, 6))

# 전략 11: 아보가드로 수 전략
def avogadro_strategy(data, round_num):
    """아보가드로 수 6.022 × 10²³"""
    avogadro = [6, 22, 23, 10, 2, 60, 62, 26, 3, 12, 18, 24, 30, 36, 42]
    valid = [n for n in avogadro if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 12: pH 스케일 전략
def ph_scale_strategy(data, round_num):
    """pH 0-14 스케일"""
    # pH * 3으로 매핑
    ph_values = [n * 3 for n in range(0, 15)]
    ph_values += [1, 2, 4, 5, 7, 8, 10, 11, 13, 14]

    valid = list(set([n for n in ph_values if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 13: 결합 에너지 전략
def bond_energy_strategy(data, round_num):
    """결합 에너지 (kJ/mol 스케일)"""
    # C-C:348, C=C:614, C≡C:839, C-H:413 -> /20으로 매핑
    energies = [17, 31, 42, 21, 10, 15, 25, 35, 40, 45, 5, 8, 12, 28, 33]
    valid = [n for n in energies if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 14: 동위원소 전략
def isotope_strategy(data, round_num):
    """주요 동위원소 질량수"""
    # C-12, C-14, U-235->10, U-238->13, O-16, O-18
    isotopes = [12, 14, 10, 13, 16, 18, 1, 2, 3, 4, 6, 8, 35, 37, 40]
    valid = [n for n in isotopes if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 15: 녹는점 전략
def melting_point_strategy(data, round_num):
    """원소 녹는점 패턴"""
    # 저온(-39 수은) ~ 고온(3422 텅스텐)
    # 특징적 값들을 45 범위로
    melting = [1, 4, 10, 14, 23, 29, 34, 39, 44, 7, 12, 17, 22, 27, 32, 37, 42]
    valid = [n for n in melting if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 16: 밀도 전략
def density_strategy(data, round_num):
    """원소 밀도 패턴"""
    # Os(22.6), Ir(22.4), Pt(21.5), Au(19.3), W(19.3)
    # 값들을 1-45로 매핑
    densities = [23, 22, 21, 19, 11, 9, 7, 5, 3, 1, 14, 16, 18, 25, 27]
    valid = [n for n in densities if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 17: 오비탈 전략
def orbital_strategy(data, round_num):
    """전자 오비탈 (s, p, d, f)"""
    # s:2개, p:6개, d:10개, f:14개
    orbitals = [2, 6, 10, 14, 8, 18, 32, 4, 12, 16, 20, 24, 28, 36, 40]
    valid = [n for n in orbitals if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 18: 합금 비율 전략
def alloy_ratio_strategy(data, round_num):
    """합금 조성 비율"""
    # 스테인리스 스틸: Fe 74%, Cr 18%, Ni 8%
    # 청동: Cu 88%, Sn 12%
    ratios = [74, 18, 8, 88, 12, 60, 40, 70, 30, 75, 25, 90, 10, 95, 5]
    # 45 범위로
    mapped = [r % 45 + 1 if r > 45 else r for r in ratios]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 19: 반응 속도 전략
def reaction_rate_strategy(data, round_num):
    """반응 속도 상수 패턴"""
    # 아레니우스 식 관련 숫자
    rates = [1, 2, 3, 5, 8, 13, 10, 20, 30, 40, 15, 25, 35, 45, 12, 24, 36]
    valid = [n for n in rates if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 20: 몰 농도 전략
def molarity_strategy(data, round_num):
    """몰 농도 관련 숫자"""
    # 0.1M, 0.5M, 1M, 2M, 5M, 10M 등
    molarities = [1, 2, 5, 10, 15, 20, 25, 50, 100, 150, 200]
    # 45 범위로
    mapped = [m % 45 + 1 if m > 45 else m for m in molarities]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    if len(valid) < 6:
        valid += random.sample([n for n in range(1, 46) if n not in valid], 6 - len(valid))
    return sorted(random.sample(valid, 6))


STRATEGIES = {
    '원자번호': atomic_number_strategy,
    '비활성_기체': noble_gas_strategy,
    '알칼리_금속': alkali_metal_strategy,
    '원자량': atomic_mass_strategy,
    '주기율표_주기': periodic_period_strategy,
    '전자_껍질': electron_shell_strategy,
    '전기음성도': electronegativity_strategy,
    '이온화_에너지': ionization_energy_strategy,
    '산화_상태': oxidation_state_strategy,
    '화학_반응식': chemical_equation_strategy,
    '아보가드로': avogadro_strategy,
    'pH_스케일': ph_scale_strategy,
    '결합_에너지': bond_energy_strategy,
    '동위원소': isotope_strategy,
    '녹는점': melting_point_strategy,
    '밀도': density_strategy,
    '오비탈': orbital_strategy,
    '합금_비율': alloy_ratio_strategy,
    '반응_속도': reaction_rate_strategy,
    '몰_농도': molarity_strategy,
}

if __name__ == '__main__':
    print(f"화학 전략 {len(STRATEGIES)}개 로드됨")
