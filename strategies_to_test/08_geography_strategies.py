"""
지리/좌표 기반 전략 (20개)
"""
import json
import random
import math
from collections import Counter

with open('/Users/kslee/Downloads/kslee_ZIP/zip1/lotto45/lotto_data.json', 'r') as f:
    lotto_data = json.load(f)

# 전략 1: 위도 전략
def latitude_strategy(data, round_num):
    """주요 도시 위도"""
    # 서울:37, 도쿄:35, 북경:39, 뉴욕:40, 런던:51->6, 파리:48->3
    latitudes = [37, 35, 39, 40, 6, 3, 33, 34, 38, 41, 42, 43, 44, 45, 32]
    valid = [n for n in latitudes if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 2: 경도 전략
def longitude_strategy(data, round_num):
    """주요 도시 경도 (일부 변환)"""
    # 서울:127->37, 도쿄:139->4, 뉴욕:-74->29, 런던:0->45
    longitudes = [37, 4, 29, 45, 21, 12, 6, 18, 24, 30, 36, 42, 9, 15, 33]
    valid = [n for n in longitudes if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 3: 시간대 전략
def timezone_strategy(data, round_num):
    """세계 시간대 UTC-12 ~ UTC+14"""
    # 시간대 * 2로 매핑
    timezones = list(range(1, 27))
    # 주요 시간대 강조: KST(+9), JST(+9), EST(-5), PST(-8), GMT(0)
    important = [18, 18, 14, 8, 24, 20, 16, 12, 22, 26]

    all_tz = timezones + important
    valid = list(set([n for n in all_tz if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 4: 고도 전략
def altitude_strategy(data, round_num):
    """유명 산/도시 해발 고도"""
    # 에베레스트:8849m->44, 백두산:2744m->27, 서울:38m->4
    altitudes = [44, 27, 4, 38, 15, 22, 8, 12, 30, 35, 40, 19, 25, 33, 42]
    valid = [n for n in altitudes if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 5: 대륙 전략
def continent_strategy(data, round_num):
    """7대륙 관련 숫자"""
    # 아시아:44, 아프리카:30, 북미:24, 남미:18, 유럽:10, 오세아니아:9, 남극:14
    continents = [44, 30, 24, 18, 10, 9, 14, 7, 1, 2, 3, 4, 5, 6, 8]
    valid = [n for n in continents if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 6: 해양 전략
def ocean_strategy(data, round_num):
    """5대양 면적 비율"""
    # 태평양:46%, 대서양:23%, 인도양:20%, 남빙양:6%, 북빙양:4%
    oceans = [46, 23, 20, 6, 4, 1, 2, 3, 5, 10, 15, 25, 30, 35, 40, 45]
    valid = [n for n in oceans if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 7: 국가 코드 전략
def country_code_strategy(data, round_num):
    """국가 전화번호 코드"""
    # 한국:82->37, 미국:1, 일본:81->36, 중국:86->41, 영국:44
    codes = [37, 1, 36, 41, 44, 33, 39, 7, 34, 43, 45, 30, 31, 32, 38]
    valid = [n for n in codes if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 8: 인구 밀도 전략
def population_density_strategy(data, round_num):
    """인구 밀도 패턴"""
    # 인구밀도 높은/낮은 지역 대비
    high_density = [1, 2, 3, 4, 5]  # 도심
    low_density = [41, 42, 43, 44, 45]  # 오지
    medium = list(range(20, 30))  # 중간

    selected = random.sample(high_density, 2) + random.sample(low_density, 2) + random.sample(medium, 2)
    return sorted(selected)

# 전략 9: 적도/극지 전략
def equator_polar_strategy(data, round_num):
    """적도(0도)와 극지(90도) 기준"""
    # 적도 근처: 23 (북회귀선)
    # 극지 근처: 66 (북극권) -> 21
    geo_lines = [23, 21, 45, 1, 22, 24, 20, 19, 25, 26, 44, 43, 2, 3]
    valid = [n for n in geo_lines if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 10: 거리 전략
def distance_strategy(data, round_num):
    """주요 도시 간 거리"""
    # 서울-도쿄:1160km->12, 서울-북경:956km->10, 지구둘레:40075km->40
    distances = [12, 10, 40, 20, 8, 15, 25, 30, 35, 45, 5, 18, 22, 28, 33]
    valid = [n for n in distances if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 11: 지진 규모 전략
def earthquake_magnitude_strategy(data, round_num):
    """리히터 규모 패턴"""
    # 규모 * 5로 매핑
    magnitudes = [n * 5 for n in range(1, 10)]
    magnitudes += [1, 2, 3, 4, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45]

    valid = list(set([n for n in magnitudes if 1 <= n <= 45]))
    return sorted(random.sample(valid, 6))

# 전략 12: 기후대 전략
def climate_zone_strategy(data, round_num):
    """기후대별 위도"""
    # 열대:0-23, 아열대:23-35, 온대:35-55, 냉대:55-70, 극지:70-90
    tropical = list(range(1, 24))
    temperate = list(range(35, 46))

    selected = random.sample(tropical, 3) + random.sample(temperate, 3)
    return sorted(selected)

# 전략 13: 반도/섬 전략
def peninsula_island_strategy(data, round_num):
    """한반도 관련 숫자"""
    # 면적:220,000km² -> 22, 길이:1,100km -> 11
    korean = [22, 11, 38, 37, 33, 43, 45, 1, 17, 27, 34, 39, 44, 12, 21]
    valid = [n for n in korean if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 14: 산맥 전략
def mountain_range_strategy(data, round_num):
    """주요 산맥 높이/길이"""
    # 히말라야:8848m->44, 알프스:4809m->24, 백두대간:~1600km->16
    mountains = [44, 24, 16, 8, 12, 20, 28, 32, 36, 40, 4, 15, 25, 35, 45]
    valid = [n for n in mountains if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 15: 강 길이 전략
def river_length_strategy(data, round_num):
    """주요 강 길이"""
    # 나일:6650km->33, 아마존:6400km->32, 한강:514km->5
    rivers = [33, 32, 5, 10, 15, 20, 25, 30, 35, 40, 44, 4, 8, 12, 22]
    valid = [n for n in rivers if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 16: 호수 면적 전략
def lake_area_strategy(data, round_num):
    """주요 호수 면적"""
    # 카스피해:371,000km²->37, 슈피리어:82,100km²->8
    lakes = [37, 8, 31, 26, 22, 18, 12, 6, 3, 1, 42, 38, 28, 20, 15]
    valid = [n for n in lakes if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 17: 사막 전략
def desert_strategy(data, round_num):
    """사막 면적/위치"""
    # 사하라:9,000,000km²->9, 고비:1,300,000km²->13
    deserts = [9, 13, 45, 25, 30, 35, 40, 15, 20, 10, 5, 1, 22, 28, 33]
    valid = [n for n in deserts if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 18: 국경선 전략
def border_strategy(data, round_num):
    """국경선 길이 패턴"""
    # 국경 많은 나라: 중국(14개국), 러시아(14개국)
    borders = [14, 28, 42, 7, 21, 35, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]
    valid = [n for n in borders if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 19: GPS 좌표 전략
def gps_coordinate_strategy(data, round_num):
    """GPS 좌표 숫자"""
    # 서울시청: 37.5666, 126.9780
    gps = [37, 5, 6, 12, 9, 7, 8, 26, 38, 35, 40, 42, 45, 1, 3]
    valid = [n for n in gps if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))

# 전략 20: 면적 비율 전략
def area_ratio_strategy(data, round_num):
    """땅/바다 면적 비율"""
    # 육지:29%, 바다:71%
    # 한국 면적:100,210km² -> 10
    ratios = [29, 71, 10, 30, 70, 20, 40, 60, 15, 35, 25, 45, 5, 50, 80]
    valid = [n for n in ratios if 1 <= n <= 45]
    return sorted(random.sample(valid, 6))


STRATEGIES = {
    '위도': latitude_strategy,
    '경도': longitude_strategy,
    '시간대': timezone_strategy,
    '고도': altitude_strategy,
    '대륙': continent_strategy,
    '해양': ocean_strategy,
    '국가_코드': country_code_strategy,
    '인구_밀도': population_density_strategy,
    '적도_극지': equator_polar_strategy,
    '거리': distance_strategy,
    '지진_규모': earthquake_magnitude_strategy,
    '기후대': climate_zone_strategy,
    '반도_섬': peninsula_island_strategy,
    '산맥': mountain_range_strategy,
    '강_길이': river_length_strategy,
    '호수_면적': lake_area_strategy,
    '사막': desert_strategy,
    '국경선': border_strategy,
    'GPS_좌표': gps_coordinate_strategy,
    '면적_비율': area_ratio_strategy,
}

if __name__ == '__main__':
    print(f"지리 전략 {len(STRATEGIES)}개 로드됨")
