"""
evolab/engine.py — 백테스트 · 명예의 전당 · 진화 루프

구조 (Hall of Fame + 섬 모델의 뼈대):
  1. backtest()      : 전략을 과거 회차에 굴려 ROI/적합도 측정 (미래참조 없음)
  2. HallOfFame      : 성과 좋은 전략을 공유 풀에 승격/저장 (= 전략 '공유')
  3. Ledger          : 회차×전략별 (사유·번호·결과) 누적 원장
  4. run_cycle()     : 채점 → 평가 → 선발 → 예측 → 영속화 (한 사이클)
  5. propose_via_llm(): LLM 탐색가 훅 (지금은 스텁 — 나중에 Claude/Gemini 연결)
"""

import json
import os
import sys
import random
from collections import Counter
from datetime import date
from typing import List, Dict, Optional

# Windows 콘솔(cp949)에서도 이모지/한글 출력이 깨지지 않도록 UTF-8 고정
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core import (
    load_data, grade, prize_for, TICKET_COST,
    unpopularity_score, soundness_score, Metrics, compute_fitness,
)
from strategies import Strategy, seed_strategies
import explorer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(os.path.dirname(BASE_DIR), "lotto_data.json")
HOF_FILE = os.path.join(BASE_DIR, "hall_of_fame.json")
LEDGER_FILE = os.path.join(BASE_DIR, "ledger.jsonl")
DASHBOARD_FILE = os.path.join(BASE_DIR, "dashboard_data.json")
EVOLVED_FILE = os.path.join(BASE_DIR, "evolved_strategies.json")
PICKS_FILE = os.path.join(BASE_DIR, "picks.json")

TIER_NAMES = {1: "1등", 2: "2등", 3: "3등", 4: "4등", 5: "5등"}


# ======================================================================
# 1. 백테스트
# ======================================================================
def backtest(strategy: Strategy, data: List[Dict],
             window: int = 100, trials: int = 20, rng_seed: int = 0) -> Metrics:
    """
    최근 `window` 회차에 대해, 각 회차마다 strategy 로 `trials` 번 번호를 생성하고
    그 회차 실제 결과로 채점 → ROI·적중분포·적합도 집계.
    전략이 확률적(random)이므로 trials 평균으로 분산을 줄인다.
    """
    rng = random.Random(rng_seed)
    rounds = sorted(data, key=lambda x: x["round"])[-window:]
    tier_hits, matches, payout_sum, n = Counter(), [], 0, 0
    unpop_sum = sound_sum = 0.0

    for item in rounds:
        rnum, actual, bonus = item["round"], item["numbers"], item["bonus"]
        for _ in range(trials):
            # 전략 내부 random 을 재현 가능하게: 전역 seed 고정
            random.seed(rng.randint(0, 2**31))
            nums = strategy.generate(data, rnum)
            m, tier = grade(nums, actual, bonus)
            tier_hits[tier] += 1
            matches.append(m)
            payout_sum += prize_for(tier, item)
            unpop_sum += unpopularity_score(nums)
            sound_sum += soundness_score(nums)
            n += 1

    met = Metrics(
        n_predictions=n,
        roi=(payout_sum / (TICKET_COST * n)) if n else 0.0,
        tier_hits={t: c for t, c in sorted(tier_hits.items()) if t != 0},
        avg_match=(sum(matches) / n) if n else 0.0,
        unpopularity=(unpop_sum / n) if n else 0.0,
        soundness=(sound_sum / n) if n else 0.0,
    )
    met.fitness = compute_fitness(met)
    return met


# ======================================================================
# 2. 명예의 전당 (공유 풀)
# ======================================================================
class HallOfFame:
    def __init__(self, path: str = HOF_FILE, capacity: int = 20):
        self.path = path
        self.capacity = capacity
        self.entries: List[Dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as f:
                self.entries = json.load(f)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    def submit(self, strategy: Strategy, metrics: Metrics):
        """전략을 공유 풀에 제출. 같은 id면 갱신. 상위 capacity개만 유지."""
        entry = {
            **strategy.meta(),
            "metrics": metrics.to_dict(),
            "note": "관측 ROI는 분산(운)일 수 있음. 실재 엣지는 unpopularity 기반 분배회피뿐.",
        }
        self.entries = [e for e in self.entries if e["id"] != strategy.id]
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e["metrics"]["fitness"], reverse=True)
        self.entries = self.entries[: self.capacity]

    def top(self, n: int = 5) -> List[Dict]:
        return self.entries[:n]


# ======================================================================
# 3. 예측 원장 (누적)
# ======================================================================
def append_ledger(records: List[Dict], path: str = LEDGER_FILE):
    with open(path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_ledger(path: str = LEDGER_FILE) -> List[Dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def grade_pending(data: List[Dict], path: str = LEDGER_FILE):
    """추첨 완료된 회차에 대해 원장의 pending 예측을 채점해 다시 쓴다."""
    rows = read_ledger(path)
    if not rows:
        return 0
    rmap = {d["round"]: d for d in data}
    graded = 0
    for r in rows:
        if r.get("status") == "pending" and r["round"] in rmap:
            item = rmap[r["round"]]
            m, tier = grade(r["numbers"], item["numbers"], item["bonus"])
            r.update(status="graded", actual=item["numbers"], match=m,
                     tier=tier, payout=prize_for(tier, item))
            graded += 1
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return graded


# ======================================================================
# 3.5 공식 픽 (주간 2세트 + 온디맨드 추가 세트)
# ======================================================================
def load_picks(path: str = PICKS_FILE) -> List[Dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_picks(picks: List[Dict], path: str = PICKS_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(picks, f, ensure_ascii=False, indent=2)


def _feedback_text(results: List[Dict]) -> str:
    hits = [r for r in results if r["tier"]]
    if hits:
        parts = ", ".join(f"세트{r['id']} {TIER_NAMES[r['tier']]}({r['count']}개 일치)" for r in hits)
        return (f"당첨 발생 — {parts}. (동반 당첨자 수는 별도 발표 전까지 확인 불가. "
                f"분배회피 전략이었다면 그 수가 적을수록 본래 목적에 부합)")
    best = max(r["count"] for r in results) if results else 0
    return (f"전 세트 미당첨(최고 {best}개 일치). 어떤 조합이든 기대 적중은 0.8개라 "
            f"이 결과는 전략 우열과 무관한 정상 분산 범위입니다.")


def build_pick_sets(scored: List[tuple], data: List[Dict], next_round: int,
                     n: int, exclude_strategy_ids: Optional[set] = None) -> List[Dict]:
    """적합도순 scored[(strategy, metrics), ...]에서 아직 안 쓴 전략 상위 n개로 세트 구성."""
    exclude_strategy_ids = exclude_strategy_ids or set()
    chosen = [(st, met) for st, met in scored if st.id not in exclude_strategy_ids][:n]
    sets = []
    for i, (st, met) in enumerate(chosen, 1):
        nums = st.generate(data, next_round)
        sets.append({
            "id": i, "strategy_id": st.id, "strategy": st.name,
            "numbers": sorted(nums), "rationale": st.rationale,
            "formula": st.formula, "fitness": round(met.fitness, 4),
        })
    return sets


def grade_picks(picks: List[Dict], data: List[Dict]) -> int:
    """결과가 나온 회차의 픽을 채점하고 사유+피드백을 채운다."""
    rmap = {d["round"]: d for d in data}
    graded = 0
    for p in picks:
        if p.get("result") is not None:
            continue
        item = rmap.get(p["round"])
        if not item:
            continue
        winning, bonus = item["numbers"], item["bonus"]
        wset = set(winning)
        results = []
        for s in p["sets"]:
            matched = sorted(set(s["numbers"]) & wset)
            _, tier = grade(s["numbers"], winning, bonus)
            results.append({
                "id": s["id"], "matched": matched, "count": len(matched),
                "tier": tier, "rank": TIER_NAMES.get(tier, "낙첨"),
            })
        p["result"] = {"winning": winning, "bonus": bonus, "sets": results}
        p["feedback"] = _feedback_text(results)
        graded += 1
    return graded


def record_weekly_picks(picks: List[Dict], scored: List[tuple], data: List[Dict],
                         next_round: int, n: int = 2) -> Optional[Dict]:
    """회차당 1번, 명예의 전당 적합도 상위 n개 전략으로 '주간 공식 픽'을 기록 (중복 실행 안전)."""
    if any(p["round"] == next_round and p["type"] == "weekly" for p in picks):
        return None
    sets = build_pick_sets(scored, data, next_round, n)
    entry = {
        "round": next_round, "type": "weekly",
        "generated_at": date.today().isoformat(),
        "basis": (f"명예의 전당 적합도 상위 {n}개 전략 — 최근 출현빈도·주기성·구간분산 등 "
                  f"내부 과거 당첨 데이터 기반 산식 + 분배회피(비인기도)·통계건전성 결합. "
                  f"※ 타인의 실제 구매 패턴(외부 데이터)은 두뇌에 없음(gap) — 휴리스틱으로만 근사."),
        "sets": sets, "result": None, "feedback": None,
    }
    picks.append(entry)
    return entry


def generate_extra_picks(n: int = 3) -> Dict:
    """온디맨드 추가 픽 — 주간 자동 사이클과 별개로, 요청 시점에 즉시 생성."""
    data = load_data(DATA_FILE)
    next_round = data[-1]["round"] + 1
    evolved = load_evolved(data)
    population = seed_strategies() + evolved
    scored = sorted(((st, backtest(st, data)) for st in population),
                     key=lambda x: x[1].fitness, reverse=True)

    picks = load_picks()
    grade_picks(picks, data)
    used_ids = {s["strategy_id"] for p in picks if p["round"] == next_round for s in p["sets"]}
    sets = build_pick_sets(scored, data, next_round, n, used_ids)
    entry = {
        "round": next_round, "type": "extra",
        "generated_at": date.today().isoformat(),
        "basis": f"요청에 의한 추가 픽 {n}세트 — 명예의 전당 적합도 순위 기반(이번 회차 기사용 전략 제외).",
        "sets": sets, "result": None, "feedback": None,
    }
    picks.append(entry)
    save_picks(picks)
    update_dashboard_picks(picks)
    return entry


def update_dashboard_picks(picks: List[Dict], path: str = DASHBOARD_FILE):
    """picks.json 변경분만 dashboard_data.json에 반영 (predictions 등 다른 필드는 보존)."""
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            out = json.load(f)
    out["weekly_picks"] = [p for p in picks if p["type"] == "weekly"][-8:]
    out["extra_picks"] = [p for p in picks if p["type"] == "extra"][-8:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


# ======================================================================
# 4. LLM 탐색가 + 진화 전략 영속화
# ======================================================================
def load_evolved(data: List[Dict]) -> List[Strategy]:
    """저장된 LLM 진화 전략을 재구성. 재검증 실패분은 자동 폐기."""
    if not os.path.exists(EVOLVED_FILE):
        return []
    with open(EVOLVED_FILE, encoding="utf-8") as f:
        specs = json.load(f)
    out = []
    for s in specs:
        st = explorer.build_from_spec(s, data, s.get("generation", 1))
        if st:
            st.parents = s.get("parents", [])
            out.append(st)
    return out


def save_evolved(strategies: List[Strategy]):
    """진화 전략을 이름 기준 dedup 하여 저장 (코드 포함)."""
    seen, specs = set(), []
    for st in strategies:
        if st.name in seen:
            continue
        seen.add(st.name)
        specs.append(st.meta())
    with open(EVOLVED_FILE, "w", encoding="utf-8") as f:
        json.dump(specs, f, ensure_ascii=False, indent=2)


def propose_via_llm(hall: HallOfFame, data: List[Dict], n: int = 2) -> List[Strategy]:
    """명예의 전당을 참고해 LLM(claude -p)이 새 전략을 제안 → 검증 통과분 반환."""
    return explorer.propose(hall.entries, data, n=n)


def propose_islands(hall: HallOfFame, data: List[Dict], n_per: int = 1) -> List[Strategy]:
    """섬 모델: 여러 탐색가가 서로 다른 관점으로 동시 탐색 → 명예의 전당으로 공유."""
    return explorer.propose_islands(hall.entries, data, n_per=n_per)


# ======================================================================
# 4.5 대시보드용 JSON 내보내기 (index.html 이 fetch 함)
# ======================================================================
def export_dashboard(hall: HallOfFame, predictions: List[Dict],
                     next_round: int, path: str = DASHBOARD_FILE):
    """
    명예의 전당 + 예측 원장 → index.html 의 새 카드가 읽을 단일 JSON.
    회차별 누적 적중(ledger)도 요약해 담는다 = '매 회차 누적 반영' 시각화용.
    """
    rows = read_ledger()
    graded = [r for r in rows if r.get("status") == "graded"]

    # 회차별 누적: 그 회차 예측들 중 최고 적중 개수 + 등수별 히트
    by_round = {}
    for r in graded:
        b = by_round.setdefault(r["round"], {"round": r["round"], "best_match": 0, "tier_hits": {}})
        b["best_match"] = max(b["best_match"], r.get("match") or 0)
        t = r.get("tier") or 0
        if t:
            b["tier_hits"][t] = b["tier_hits"].get(t, 0) + 1

    tier_total = {}
    for r in graded:
        t = r.get("tier") or 0
        if t:
            tier_total[t] = tier_total.get(t, 0) + 1

    # 전략별 당첨 이력(win_history) — 대시보드 모달이 이미 지원하는 형식
    win_hist = {}
    for r in graded:
        if (r.get("tier") or 0) in (1, 2, 3, 4):   # 4등 이상만 '당첨'으로 표기
            win_hist.setdefault(r["strategy_id"], []).append({
                "round": r["round"], "rank": r["tier"],
                "numbers": r["numbers"], "actual": r.get("actual") or [],
            })

    out = {
        "next_round": next_round,
        "strategies": [
            {
                "name": e["name"], "formula": e["formula"], "rationale": e["rationale"],
                "generation": e["generation"], "metrics": e["metrics"],
            }
            for e in hall.entries
        ],
        "predictions": [
            {"strategy": p["strategy_id"], "numbers": p["numbers"], "rationale": p["rationale"]}
            for p in predictions
        ],
        "ledger_summary": {
            "graded_rounds": len(by_round),
            "tier_total": tier_total,
            "rounds": [by_round[k] for k in sorted(by_round)],
            "win_history": win_hist,
        },
        "honesty_note": "ROI는 분산(운)일 수 있음. 기대 적중 개수는 모든 전략이 0.8개로 동일. "
                        "실재 엣지는 분배회피(비인기도)뿐.",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


# ======================================================================
# 5. 한 사이클
# ======================================================================
def run_cycle(verbose: bool = True, use_llm: bool = False,
              islands: bool = False, n_propose: int = 2) -> Dict:
    data = load_data(DATA_FILE)
    latest = data[-1]["round"]
    next_round = latest + 1

    # (a) 지난 예측 채점
    n_graded = grade_pending(data)
    picks = load_picks()
    n_picks_graded = grade_picks(picks, data)

    # (b) 전략 모집단 = 시드 + 저장된 진화전략 + (옵션) LLM 신규 제안
    hall = HallOfFame()
    evolved = load_evolved(data)
    if islands:
        proposed = propose_islands(hall, data, n_per=n_propose)
    elif use_llm:
        proposed = propose_via_llm(hall, data, n=n_propose)
    else:
        proposed = []
    if proposed:                                   # 새로 통과한 전략을 누적 저장
        save_evolved(evolved + proposed)
    population: List[Strategy] = seed_strategies() + evolved + proposed

    # (c) 백테스트 → 명예의 전당 갱신
    scored = []
    for st in population:
        met = backtest(st, data)
        hall.submit(st, met)
        scored.append((st, met))
    hall.save()

    # (d) 상위 전략으로 다음 회차 예측 → 원장에 pending 기록
    scored.sort(key=lambda x: x[1].fitness, reverse=True)
    # 이미 이번 회차 예측이 원장에 있으면 중복 기록 방지 (재실행 안전)
    existing = {(r["round"], r["strategy_id"]) for r in read_ledger()}
    predictions = []
    for st, met in scored[:5]:
        nums = st.generate(data, next_round)
        predictions.append({
            "round": next_round, "strategy_id": st.id,
            "numbers": nums, "rationale": st.rationale,
            "formula": st.formula, "status": "pending",
            "actual": None, "match": None, "tier": None, "payout": None,
        })
    new_rows = [p for p in predictions if (p["round"], p["strategy_id"]) not in existing]
    append_ledger(new_rows)

    # (d.5) 주간 공식 픽 2세트 자동 기록 (회차당 1번, 중복 실행 안전)
    weekly_entry = record_weekly_picks(picks, scored, data, next_round, n=2)
    save_picks(picks)

    # (e) 대시보드용 JSON 내보내기
    export_dashboard(hall, predictions, next_round)
    update_dashboard_picks(picks)

    if verbose:
        print(f"📊 사이클 완료 — 데이터 최신 {latest}회, 다음 예측 {next_round}회")
        print(f"   채점된 지난 예측: {n_graded}건 / 채점된 픽: {n_picks_graded}건")
        print(f"\n🏆 명예의 전당 TOP 5 (적합도순):")
        for e in hall.top(5):
            mt = e["metrics"]
            print(f"   {e['name']:14s} fit={mt['fitness']:.3f} "
                  f"ROI={mt['roi']:.3f} 비인기={mt['unpopularity']:.2f} "
                  f"건전성={mt['soundness']:.2f} 적중분포={mt['tier_hits']}")
        print(f"\n🔮 {next_round}회 추천 (상위 전략별):")
        for p in predictions:
            print(f"   [{p['strategy_id']}] {p['numbers']}  ← {p['rationale'][:40]}…")
        if weekly_entry:
            print(f"\n🎯 주간 공식 픽 {next_round}회 (2세트):")
            for s in weekly_entry["sets"]:
                print(f"   세트{s['id']} [{s['strategy']}] {s['numbers']}")
        print(f"\n⚠️  ROI는 분산(운)일 수 있음. 실재 엣지는 분배회피(unpopularity)뿐.")

    return {"next_round": next_round, "graded": n_graded,
            "picks_graded": n_picks_graded, "weekly_entry": weekly_entry,
            "hall_top": hall.top(5), "predictions": predictions}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="evolab 진화 사이클")
    ap.add_argument("--llm", action="store_true", help="단일 LLM(claude -p) 탐색가로 새 전략 생성")
    ap.add_argument("--islands", action="store_true", help="섬 모델: 여러 탐색가 동시 탐색")
    ap.add_argument("-n", type=int, default=2, help="제안 전략 수 (섬 모드면 섬당 개수)")
    ap.add_argument("--extra", type=int, default=0, metavar="N",
                     help="주간 자동 사이클과 별개로, 다음 회차 추가 픽 N세트를 온디맨드 생성")
    args = ap.parse_args()
    if args.extra:
        entry = generate_extra_picks(args.extra)
        print(f"➕ 추가 픽 {args.extra}세트 생성 — {entry['round']}회 ({entry['generated_at']})")
        for s in entry["sets"]:
            print(f"   세트{s['id']} [{s['strategy']}] {s['numbers']}")
    else:
        run_cycle(use_llm=args.llm, islands=args.islands,
                  n_propose=(1 if args.islands and args.n == 2 else args.n))
