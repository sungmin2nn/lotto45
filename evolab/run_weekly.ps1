# evolab 주간 자동 실행 (Windows)
# 1) 최신 당첨번호 수집  2) 진화 사이클(섬 모델, claude -p)  3) 로그
# 추첨(매주 토요일) 다음날 일요일에 돌리는 것을 권장.
#
# [수동 실행]
#   powershell -ExecutionPolicy Bypass -File C:\Users\z3117\AI\lotto45\evolab\run_weekly.ps1
#
# [작업 스케줄러 등록] — 매주 일요일 10:00 (직접 실행해 등록; 시스템 설정 변경이라 사용자 확인 후)
#   $act = New-ScheduledTaskAction -Execute 'powershell.exe' `
#          -Argument '-ExecutionPolicy Bypass -File C:\Users\z3117\AI\lotto45\evolab\run_weekly.ps1'
#   $trg = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 10:00
#   Register-ScheduledTask -TaskName 'evolab-weekly' -Action $act -Trigger $trg -Description 'evolab 로또 전략 진화'

$ErrorActionPreference = 'Continue'
$Root = Split-Path $PSScriptRoot -Parent          # ...\lotto45
$Log  = Join-Path $PSScriptRoot 'weekly_log.txt'
$Stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

Add-Content $Log "======================================== $Stamp"

Set-Location $Root
Add-Content $Log '[1] 최신 당첨번호 수집...'
python collect_lotto.py *>> $Log

Add-Content $Log '[2] evolab 진화 사이클 (섬 모델)...'
python evolab\engine.py --islands *>> $Log

Add-Content $Log "[완료] $Stamp`n"
Write-Host "evolab 주간 실행 완료. 로그: $Log"
