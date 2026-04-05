"""
로또 당첨번호 자동 수집기 (완전판 - 33개 필드)
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JSON_FILE = "lotto_data.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'AJAX': 'true',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.dhlottery.co.kr/lt645/result',
}

def fetch_all_data():
    url = "https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?srchLtEpsd=all"
    
    print("📡 API 호출 중...")
    res = requests.get(url, headers=HEADERS, timeout=60, verify=False)
    
    if res.status_code != 200:
        print(f"❌ HTTP 에러: {res.status_code}")
        return None
    
    try:
        data = res.json()
    except:
        print(f"❌ JSON 파싱 실패")
        return None
    
    if 'data' not in data or 'list' not in data['data']:
        print(f"❌ 데이터 구조 오류")
        return None
    
    raw_list = data['data']['list']
    print(f"✅ {len(raw_list)}개 회차 데이터 수신")
    
    result = []
    for item in raw_list:
        result.append({
            "round": item.get("ltEpsd"),
            "date": item.get("ltRflYmd", ""),
            "numbers": [
                item.get("tm1WnNo"),
                item.get("tm2WnNo"),
                item.get("tm3WnNo"),
                item.get("tm4WnNo"),
                item.get("tm5WnNo"),
                item.get("tm6WnNo")
            ],
            "bonus": item.get("bnsWnNo"),
            "rank1": {
                "winners": item.get("rnk1WnNope", 0),
                "prize": item.get("rnk1WnAmt", 0),
                "totalPrize": item.get("rnk1SumWnAmt", 0)
            },
            "rank2": {
                "winners": item.get("rnk2WnNope", 0),
                "prize": item.get("rnk2WnAmt", 0),
                "totalPrize": item.get("rnk2SumWnAmt", 0)
            },
            "rank3": {
                "winners": item.get("rnk3WnNope", 0),
                "prize": item.get("rnk3WnAmt", 0),
                "totalPrize": item.get("rnk3SumWnAmt", 0)
            },
            "rank4": {
                "winners": item.get("rnk4WnNope", 0),
                "prize": item.get("rnk4WnAmt", 0),
                "totalPrize": item.get("rnk4SumWnAmt", 0)
            },
            "rank5": {
                "winners": item.get("rnk5WnNope", 0),
                "prize": item.get("rnk5WnAmt", 0),
                "totalPrize": item.get("rnk5SumWnAmt", 0)
            },
            "totalWinners": item.get("sumWnNope", 0),
            "totalSales": item.get("wholEpsdSumNtslAmt", 0),
            "gameNo": item.get("gmSqNo", 0),
        })
    
    result.sort(key=lambda x: x["round"])
    return result

def save_json(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 {JSON_FILE} 저장 완료")

def format_money(amount):
    if amount >= 100000000:
        return f"{amount / 100000000:.1f}억원"
    elif amount >= 10000:
        return f"{amount / 10000:.0f}만원"
    else:
        return f"{amount:,}원"

def main():
    print("🎱 로또 데이터 수집 시작")
    print("=" * 50)
    
    data = fetch_all_data()
    
    if data:
        save_json(data)
        print("=" * 50)
        print(f"✅ 완료! {len(data)}개 회차")
        print(f"📊 범위: {data[0]['round']}회 ~ {data[-1]['round']}회")
        
        latest = data[-1]
        print(f"\n📋 최신 회차 ({latest['round']}회):")
        print(f"   당첨번호: {latest['numbers']} + {latest['bonus']}")
        print(f"   1등: {format_money(latest['rank1']['prize'])} × {latest['rank1']['winners']}명")
    else:
        print("❌ 수집 실패")
        exit(1)

if __name__ == "__main__":
    main()
