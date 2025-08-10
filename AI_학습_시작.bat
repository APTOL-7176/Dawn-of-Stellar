@echo off
chcp 65001 > nul
echo.
echo 🤖 ===== Dawn of Stellar AI 학습 시스템 ===== 🤖
echo.
echo 🚀 AI 학습 모드를 선택하세요:
echo.
echo    1. 💤 밤새 자동 학습 (8시간)
echo    2. 🏃 빠른 학습 (1시간)  
echo    3. 🏆 토너먼트 학습 (AI끼리 대전)
echo    4. 📚 데이터셋 생성 (28개 직업)
echo    5. 🧠 지능 진화 테스트
echo    6. 🔥 극한 학습 모드 (24시간)
echo    7. 📊 학습 상태 확인
echo    8. 🗑️ 학습 데이터 초기화
echo    9. 🎮 AI vs 플레이어 테스트
echo.
set /p choice="선택 (1-9): "

if "%choice%"=="1" goto night_learning
if "%choice%"=="2" goto quick_learning
if "%choice%"=="3" goto tournament_learning
if "%choice%"=="4" goto dataset_generation
if "%choice%"=="5" goto evolution_test
if "%choice%"=="6" goto extreme_learning
if "%choice%"=="7" goto check_status
if "%choice%"=="8" goto reset_data
if "%choice%"=="9" goto ai_vs_player
goto invalid_choice

:night_learning
echo.
echo 💤 밤새 자동 학습을 시작합니다...
echo    ⏰ 예상 시간: 8시간
echo    🧠 학습 모드: 심화 학습 + 진화
echo    📈 목표: 지능 레벨 3단계 향상
echo.
echo 💡 컴퓨터를 끄지 마세요! 내일 아침에 확인하세요.
echo.
pause
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import asyncio
from game.permanent_ai_learning_system import PermanentLearningDatabase
from game.ultimate_integrated_ai_system import UltimateIntegratedAISystem
import time

async def night_learning():
    print('🌙 밤새 학습 시작!')
    
    # 학습 시스템 초기화
    db = PermanentLearningDatabase()
    ai_system = UltimateIntegratedAISystem()
    
    # 8시간 = 28800초
    end_time = time.time() + 28800
    
    cycle = 1
    while time.time() < end_time:
        print(f'📚 학습 사이클 {cycle} 시작...')
        
        # 1시간씩 학습
        await ai_system.run_night_learning(duration_hours=1)
        
        # 30분마다 진화 체크
        if cycle % 2 == 0:
            await ai_system.evolve_ai_generation()
        
        # 2시간마다 토너먼트
        if cycle % 4 == 0:
            await ai_system.run_ai_tournament()
        
        cycle += 1
        
        # 잠시 휴식
        await asyncio.sleep(60)
    
    print('🌅 밤새 학습 완료! 결과를 확인하세요.')

asyncio.run(night_learning())
"
goto end

:quick_learning
echo.
echo 🏃 빠른 학습을 시작합니다...
echo    ⏰ 예상 시간: 1시간
echo    🧠 학습 모드: 집중 학습
echo.
pause
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import asyncio
from game.ultimate_integrated_ai_system import UltimateIntegratedAISystem

async def quick_learning():
    print('⚡ 빠른 학습 시작!')
    ai_system = UltimateIntegratedAISystem()
    await ai_system.run_night_learning(duration_hours=1)
    print('✅ 빠른 학습 완료!')

asyncio.run(quick_learning())
"
goto end

:tournament_learning
echo.
echo 🏆 AI 토너먼트 학습을 시작합니다...
echo    🤖 27명의 AI가 서로 대전하며 학습합니다
echo.
pause
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import asyncio
from game.ultimate_integrated_ai_system import UltimateIntegratedAISystem

async def tournament_learning():
    print('🏆 AI 토너먼트 시작!')
    ai_system = UltimateIntegratedAISystem()
    
    for round in range(10):
        print(f'🥊 토너먼트 라운드 {round + 1}/10')
        await ai_system.run_ai_tournament()
        await asyncio.sleep(5)
    
    print('🏆 토너먼트 학습 완료!')

asyncio.run(tournament_learning())
"
goto end

:dataset_generation
echo.
echo 📚 28개 직업 데이터셋을 생성합니다...
echo    📊 각 직업마다 64개 스킬 + 64개 전략
echo.
pause
D:\로그라이크_2\.venv\Scripts\python.exe -c "
from game.permanent_ai_learning_system import JobSpecificDatasetGenerator

print('📚 데이터셋 생성 시작!')
generator = JobSpecificDatasetGenerator()
generator.generate_all_job_datasets()
print('✅ 모든 직업 데이터셋 생성 완료!')
"
goto end

:evolution_test
echo.
echo 🧠 AI 지능 진화 테스트를 시작합니다...
echo    🔬 Generation 1 → Generation 5까지 진화
echo.
pause
D:\로그라이크_2\.venv\Scripts\python.exe -c "
import asyncio
from game.ultimate_integrated_ai_system import UltimateIntegratedAISystem

async def evolution_test():
    print('🧠 AI 진화 테스트 시작!')
    ai_system = UltimateIntegratedAISystem()
    
    for gen in range(5):
        print(f'🔬 Generation {gen + 1} 진화 중...')
        await ai_system.evolve_ai_generation()
        await asyncio.sleep(3)
    
    print('🧬 AI 진화 테스트 완료!')

asyncio.run(evolution_test())
"
goto end

:extreme_learning
echo.
echo 🔥 극한 학습 모드 (24시간)
echo    ⚠️ 경고: 매우 오랜 시간이 걸립니다!
echo    💻 컴퓨터 성능을 최대한 활용합니다
echo.
set /p confirm="정말 시작하시겠습니까? (y/n): "
if /i not "%confirm%"=="y" goto menu

D:\로그라이크_2\.venv\Scripts\python.exe -c "
import asyncio
from game.ultimate_integrated_ai_system import UltimateIntegratedAISystem
import time

async def extreme_learning():
    print('🔥 극한 학습 모드 시작!')
    ai_system = UltimateIntegratedAISystem()
    
    # 24시간
    end_time = time.time() + 86400
    
    while time.time() < end_time:
        await ai_system.run_night_learning(duration_hours=2)
        await ai_system.evolve_ai_generation()
        await ai_system.run_ai_tournament()
        print('🔥 극한 학습 계속 진행 중...')
    
    print('🏆 극한 학습 완료! AI가 신급 지능에 도달했습니다!')

asyncio.run(extreme_learning())
"
goto end

:check_status
echo.
echo 📊 AI 학습 상태를 확인합니다...
echo.
D:\로그라이크_2\.venv\Scripts\python.exe -c "
from game.permanent_ai_learning_system import PermanentLearningDatabase
import os

print('📊 === AI 학습 상태 보고서 ===')
print()

# 데이터베이스 크기 확인
db_path = 'ai_permanent_learning.db'
if os.path.exists(db_path):
    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f'💾 학습 데이터 크기: {size_mb:.2f} MB')
else:
    print('💾 학습 데이터: 아직 없음')

# 학습 데이터 확인
try:
    db = PermanentLearningDatabase()
    
    # 각 직업별 학습 데이터 확인
    jobs = ['전사', '아크메이지', '궁수', '도적', '성기사', '암흑기사', '몽크', '바드']
    
    for job in jobs:
        skills = db.get_job_skills(job)
        strategies = db.get_job_strategies(job)
        print(f'🎯 {job}: 스킬 {len(skills)}개, 전략 {len(strategies)}개')
    
    print()
    print('✅ AI 학습 상태 확인 완료!')
    
except Exception as e:
    print(f'❌ 상태 확인 실패: {e}')
"
pause
goto menu

:reset_data
echo.
echo 🗑️ 학습 데이터 초기화
echo    ⚠️ 경고: 모든 AI 학습 데이터가 삭제됩니다!
echo.
set /p confirm="정말 초기화하시겠습니까? (y/n): "
if /i not "%confirm%"=="y" goto menu

echo 🗑️ 학습 데이터를 초기화합니다...
if exist ai_permanent_learning.db del ai_permanent_learning.db
echo ✅ 초기화 완료!
pause
goto menu

:ai_vs_player
echo.
echo 🎮 AI vs 플레이어 테스트
echo    🤖 학습된 AI와 실제 대전해보세요!
echo.
pause
D:\로그라이크_2\.venv\Scripts\python.exe main.py
goto end

:invalid_choice
echo.
echo ❌ 잘못된 선택입니다. 1-9 중에서 선택해주세요.
pause
goto menu

:menu
goto start

:end
echo.
echo 🎉 작업이 완료되었습니다!
echo 💡 다른 학습을 원하시면 다시 실행하세요.
echo.
pause
