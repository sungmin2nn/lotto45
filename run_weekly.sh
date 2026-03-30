#!/bin/bash
# 로또 주간 자동 실행 스크립트

cd /Users/kslee/Downloads/kslee_ZIP/zip1/lotto45

LOG_FILE="weekly_log.txt"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "========================================" >> $LOG_FILE
echo "실행 시간: $DATE" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# 1. 최신 당첨번호 수집
echo "[1] 당첨번호 수집 중..." >> $LOG_FILE
python3 collect_lotto.py >> $LOG_FILE 2>&1

# 2. 전략 실행 + 번호 생성
echo "[2] 전략 실행 중..." >> $LOG_FILE
python3 weekly_runner.py >> $LOG_FILE 2>&1

echo "완료!" >> $LOG_FILE
echo "" >> $LOG_FILE
