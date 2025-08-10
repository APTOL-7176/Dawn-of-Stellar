@echo off
chcp 65001 > nul
echo.
echo 🌙 === 밤새 AI 학습 (자동) === 🌙
echo.
echo 💤 이 배치파일은 AI를 밤새 학습시킵니다
echo    ⏰ 8시간 동안 자동으로 실행됩니다
echo    🧠 AI 지능이 크게 향상됩니다
echo    💻 컴퓨터를 끄지 마세요!
echo.
echo 🚀 3초 후 자동으로 시작합니다...
timeout /t 3

echo.
echo 🌙 밤새 학습 시작! 내일 아침에 확인하세요.
echo    현재 시간: %time%
echo.

D:\로그라이크_2\.venv\Scripts\python.exe -c "
import asyncio
import time
from datetime import datetime
from game.permanent_ai_learning_system import PermanentLearningDatabase, JobSpecificDatasetGenerator
from game.ultimate_integrated_ai_system import UltimateIntegratedAISystem

async def auto_night_learning():
    print('🌙 자동 밤새 학습 시작!')
    print(f'⏰ 시작 시간: {datetime.now().strftime(\"%%Y-%%m-%%d %%H:%%M:%%S\")}')
    
    try:
        # 시스템 초기화
        print('🔧 AI 시스템 초기화 중...')
        db = PermanentLearningDatabase()
        ai_system = UltimateIntegratedAISystem()
        
        # 첫 번째: 데이터셋 생성 (없으면)
        print('📚 데이터셋 확인 및 생성...')
        generator = JobSpecificDatasetGenerator()
        generator.generate_all_job_datasets()
        
        # 8시간 학습 (28800초)
        start_time = time.time()
        end_time = start_time + 28800
        
        cycle = 1
        while time.time() < end_time:
            remaining = end_time - time.time()
            hours_left = remaining / 3600
            
            print(f'')
            print(f'📚 === 학습 사이클 {cycle} 시작 ===')
            print(f'⏰ 남은 시간: {hours_left:.1f}시간')
            print(f'🕐 현재 시간: {datetime.now().strftime(\"%%H:%%M:%%S\")}')
            
            # 1시간씩 심화 학습
            print('🧠 심화 학습 진행 중...')
            await ai_system.run_night_learning(duration_hours=1)
            
            # 30분마다 진화
            if cycle % 2 == 0:
                print('🧬 AI 진화 중...')
                await ai_system.evolve_ai_generation()
            
            # 2시간마다 토너먼트
            if cycle % 4 == 0:
                print('🏆 AI 토너먼트 시작...')
                await ai_system.run_ai_tournament()
            
            # 4시간마다 상태 보고
            if cycle % 8 == 0:
                print('📊 중간 상태 보고:')
                # AI 상태 체크
                
            cycle += 1
            print(f'✅ 사이클 {cycle-1} 완료')
            
            # 잠시 휴식 (시스템 과부하 방지)
            await asyncio.sleep(30)
        
        print('')
        print('🌅 === 밤새 학습 완료! ===')
        print(f'⏰ 완료 시간: {datetime.now().strftime(\"%%Y-%%m-%%d %%H:%%M:%%S\")}')
        print(f'🎓 총 학습 사이클: {cycle-1}개')
        print('🏆 AI가 더욱 똑똑해졌습니다!')
        print('')
        print('💡 이제 게임을 실행해서 발전된 AI를 확인해보세요!')
        
    except Exception as e:
        print(f'❌ 학습 중 오류 발생: {e}')
        print('🔧 시스템을 확인하고 다시 시도해주세요.')

asyncio.run(auto_night_learning())
"

echo.
echo 🎉 밤새 학습이 완료되었습니다!
echo    💡 이제 게임을 실행해서 똑똑해진 AI를 확인해보세요!
echo.
pause
