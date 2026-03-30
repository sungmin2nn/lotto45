"""
음악/소리 기반 전략 (20개)
"""
import json
import random
import math
from collections import Counter

with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

# 전략 1: 음계 주파수 전략
def musical_scale_strategy(data, round_num):
    """도레미파솔라시 주파수 비율"""
    # C4=261.63Hz 기준 비율을 1-45로 매핑
    # 도:1, 레:9/8, 미:5/4, 파:4/3, 솔:3/2, 라:5/3, 시:15/8
    ratios = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8, 2]
    notes = [int(r * 20) for r in ratios]
    notes = [n for n in notes if 1 <= n <= 45]

    # 추가 옥타브
    for r in ratios:
        n = int(r * 10)
        if 1 <= n <= 45:
            notes.append(n)

    valid = list(set(notes))
    if len(valid) >= 6:
        return sorted(random.sample(valid, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 2: 피아노 건반 전략
def piano_key_strategy(data, round_num):
    """피아노 88건반 중 45개 매핑"""
    # 흰 건반과 검은 건반 패턴
    white_keys = [1, 3, 5, 6, 8, 10, 12, 13, 15, 17, 18, 20, 22, 24, 25, 27, 29, 30, 32, 34, 36, 37, 39, 41, 42, 44]
    black_keys = [2, 4, 7, 9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 45]

    valid = [n for n in white_keys + black_keys if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 3: 비트 패턴 전략
def beat_pattern_strategy(data, round_num):
    """4/4박자 비트 패턴"""
    # 강-약-중강-약 패턴
    beats = []
    for measure in range(1, 12):
        beats.append(measure * 4)      # 강박
        beats.append(measure * 4 - 2)  # 중강박

    valid = [n for n in beats if 1 <= n <= 45]
    if len(valid) >= 6:
        return sorted(random.sample(valid, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 4: 화음 전략
def chord_strategy(data, round_num):
    """메이저/마이너 코드 구성음"""
    # 도미솔(C), 레파라(Dm), 미솔시(Em) 등
    chords = {
        'C': [1, 5, 8],
        'Dm': [2, 5, 9],
        'Em': [3, 7, 10],
        'F': [4, 8, 11],
        'G': [5, 9, 12],
        'Am': [6, 9, 13],
        'Bdim': [7, 10, 13]
    }

    all_notes = []
    for notes in chords.values():
        all_notes.extend(notes)
        # 한 옥타브 위
        all_notes.extend([n + 12 for n in notes])
        all_notes.extend([n + 24 for n in notes])

    valid = list(set([n for n in all_notes if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 5: 템포 BPM 전략
def tempo_bpm_strategy(data, round_num):
    """음악 템포 BPM 기반"""
    # Largo:40-60, Adagio:66-76, Andante:76-108, Moderato:108-120, Allegro:120-168
    tempos = [40, 60, 66, 76, 88, 100, 108, 120, 132, 144, 156, 168]
    # 45 이하로 매핑
    mapped = [t % 45 + 1 if t > 45 else t for t in tempos]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    if len(valid) >= 6:
        return sorted(random.sample(valid, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 6: 하모닉스 전략
def harmonics_strategy(data, round_num):
    """배음 시리즈"""
    # 기본음의 배수: f, 2f, 3f, 4f...
    base = random.randint(1, 7)
    harmonics = [base * i for i in range(1, 15)]

    valid = [n for n in harmonics if 1 <= n <= 45]
    if len(valid) >= 6:
        return sorted(random.sample(valid, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 7: 12음 기법 전략
def twelve_tone_strategy(data, round_num):
    """쇤베르크 12음 기법"""
    # 12개 음을 모두 사용하는 음렬
    tone_row = list(range(1, 13))
    random.shuffle(tone_row)

    # 역행, 전위 등 변형
    retrograde = tone_row[::-1]
    transposed = [(n + 12) for n in tone_row]

    all_tones = tone_row + retrograde + transposed
    valid = list(set([n for n in all_tones if 1 <= n <= 45]))

    return sorted(random.sample(valid, 6))

# 전략 8: 펜타토닉 전략
def pentatonic_strategy(data, round_num):
    """5음 음계"""
    # 도레미솔라 (반음 없는 음계)
    penta = [1, 3, 5, 8, 10]  # C D E G A

    all_notes = []
    for octave in range(5):
        for note in penta:
            n = note + octave * 12
            if 1 <= n <= 45:
                all_notes.append(n)

    valid = list(set(all_notes))
    return sorted(random.sample(valid, 6))

# 전략 9: 블루스 스케일 전략
def blues_scale_strategy(data, round_num):
    """블루스 음계"""
    # 1, b3, 4, b5, 5, b7
    blues = [1, 4, 6, 7, 8, 11]

    all_notes = []
    for octave in range(4):
        for note in blues:
            n = note + octave * 12
            if 1 <= n <= 45:
                all_notes.append(n)

    valid = list(set(all_notes))
    return sorted(random.sample(valid, 6))

# 전략 10: 주파수 대역 전략
def frequency_band_strategy(data, round_num):
    """저음/중음/고음 대역"""
    low = list(range(1, 16))    # 저음역
    mid = list(range(16, 31))   # 중음역
    high = list(range(31, 46))  # 고음역

    # 각 대역에서 2개씩
    selected = random.sample(low, 2) + random.sample(mid, 2) + random.sample(high, 2)
    return sorted(selected)

# 전략 11: 리듬 패턴 전략
def rhythm_pattern_strategy(data, round_num):
    """리듬 패턴 (셋잇단음표, 부점 등)"""
    # 3연음: 3, 6, 9, 12...
    triplets = [i * 3 for i in range(1, 16)]
    # 부점: 3/2 배
    dotted = [int(i * 1.5) for i in range(2, 30)]

    all_rhythms = triplets + dotted
    valid = list(set([n for n in all_rhythms if 1 <= n <= 45]))

    return sorted(random.sample(valid, 6))

# 전략 12: 음정 인터벌 전략
def interval_strategy(data, round_num):
    """음정 간격"""
    # 완전5도=7반음, 완전4도=5반음, 장3도=4반음
    intervals = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12]

    start = random.randint(1, 20)
    notes = [start]
    for interval in random.sample(intervals, 5):
        next_note = notes[-1] + interval
        if 1 <= next_note <= 45:
            notes.append(next_note)

    while len(notes) < 6:
        notes.append(random.randint(1, 45))

    return sorted(list(set(notes))[:6])

# 전략 13: 데시벨 전략
def decibel_strategy(data, round_num):
    """데시벨 레벨"""
    # 10dB(속삭임), 30dB(조용한 방), 60dB(대화), 90dB(공장), 120dB(콘서트)
    db_levels = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    # 45 범위로 매핑
    mapped = [d % 45 + 1 if d > 45 else d for d in db_levels]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    if len(valid) >= 6:
        return sorted(random.sample(valid, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 14: 기타 프렛 전략
def guitar_fret_strategy(data, round_num):
    """기타 프렛 위치"""
    # 6현 x 최대 24프렛
    frets = []
    for string in range(1, 7):
        for fret in range(0, 25):
            note = string * 5 + fret
            if 1 <= note <= 45:
                frets.append(note)

    valid = list(set(frets))
    return sorted(random.sample(valid, 6))

# 전략 15: 샘플링 레이트 전략
def sampling_rate_strategy(data, round_num):
    """오디오 샘플링 레이트"""
    # 8000, 11025, 22050, 44100, 48000, 96000 Hz
    rates = [8, 11, 22, 44, 48, 96, 192]
    # 추가 관련 숫자
    rates += [16, 24, 32, 88, 176]

    valid = [n for n in rates if 1 <= n <= 45]
    if len(valid) >= 6:
        return sorted(random.sample(valid, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 16: 음파 파형 전략
def waveform_strategy(data, round_num):
    """사인파, 사각파, 삼각파 등"""
    # 사인파 샘플 (0~360도를 1~45로)
    sine_samples = []
    for deg in range(0, 360, 30):
        val = int((math.sin(math.radians(deg)) + 1) * 22) + 1
        if 1 <= val <= 45:
            sine_samples.append(val)

    # 사각파 (0 또는 최대)
    square = [1, 23, 45]

    # 삼각파 (선형 증가/감소)
    triangle = list(range(1, 46, 4)) + list(range(45, 0, -4))

    all_waves = sine_samples + square + triangle
    valid = list(set([n for n in all_waves if 1 <= n <= 45]))

    return sorted(random.sample(valid, 6))

# 전략 17: DJ 믹싱 전략
def dj_mixing_strategy(data, round_num):
    """DJ BPM 매칭"""
    # 하우스: 120-130, 테크노: 130-150, 드럼앤베이스: 160-180
    bpms = [120, 125, 128, 130, 135, 140, 145, 150, 160, 170, 175, 180]
    # 45로 나눈 나머지
    mapped = [(b % 45) + 1 for b in bpms]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    if len(valid) >= 6:
        return sorted(random.sample(valid, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 18: 오케스트라 섹션 전략
def orchestra_section_strategy(data, round_num):
    """오케스트라 악기 배치"""
    # 현악기(1-15), 목관(16-25), 금관(26-35), 타악기(36-45)
    strings = random.sample(range(1, 16), 2)
    woodwinds = random.sample(range(16, 26), 1)
    brass = random.sample(range(26, 36), 2)
    percussion = random.sample(range(36, 46), 1)

    return sorted(strings + woodwinds + brass + percussion)

# 전략 19: 음악 시대 전략
def music_era_strategy(data, round_num):
    """음악 시대별 연도"""
    # 바로크:1600-1750, 고전:1750-1820, 낭만:1820-1910, 현대:1910-
    eras = [16, 17, 18, 19, 20, 21, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    valid = [n for n in eras if 1 <= n <= 45]

    if len(valid) >= 6:
        return sorted(random.sample(valid, 6))
    return sorted(random.sample(range(1, 46), 6))

# 전략 20: MIDI 노트 전략
def midi_note_strategy(data, round_num):
    """MIDI 노트 번호 (0-127)"""
    # 중앙 C = 60, 옥타브 = 12
    midi_notes = list(range(36, 84))  # 일반적 피아노 범위
    # 45로 매핑
    mapped = [(n % 45) + 1 for n in midi_notes]

    valid = list(set([n for n in mapped if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))


STRATEGIES = {
    '음계_주파수': musical_scale_strategy,
    '피아노_건반': piano_key_strategy,
    '비트_패턴': beat_pattern_strategy,
    '화음': chord_strategy,
    '템포_BPM': tempo_bpm_strategy,
    '하모닉스': harmonics_strategy,
    '12음_기법': twelve_tone_strategy,
    '펜타토닉': pentatonic_strategy,
    '블루스_스케일': blues_scale_strategy,
    '주파수_대역': frequency_band_strategy,
    '리듬_패턴': rhythm_pattern_strategy,
    '음정_인터벌': interval_strategy,
    '데시벨': decibel_strategy,
    '기타_프렛': guitar_fret_strategy,
    '샘플링_레이트': sampling_rate_strategy,
    '음파_파형': waveform_strategy,
    'DJ_믹싱': dj_mixing_strategy,
    '오케스트라_섹션': orchestra_section_strategy,
    '음악_시대': music_era_strategy,
    'MIDI_노트': midi_note_strategy,
}

if __name__ == '__main__':
    print(f"음악/소리 전략 {len(STRATEGIES)}개 로드됨")
