@echo off
chcp 65001 > nul
echo.
echo ⚡ === AI 빠른 학습 테스트 === ⚡
echo.
echo 🏃 5분만에 AI 학습을 테스트해볼 수 있습니다!
echo    📚 데이터셋 생성
echo    🧠 기본 학습
echo    🏆 미니 토너먼트
echo    🧬 진화 테스트
echo.
pause

echo 🚀 빠른 학습 테스트 시작!

D:\로그라이크_2\.venv\Scripts\python.exe -c "
import asyncio
from game.permanent_ai_learning_system import PermanentLearningDatabase, JobSpecificDatasetGenerator
from game.ultimate_integrated_ai_system import UltimateIntegratedAISystem

async def quick_test():
    print('⚡ AI 빠른 학습 테스트 시작!')
    
    try:
        # 1. 데이터셋 생성 테스트
        print('📚 1단계: 데이터셋 생성 테스트...')
        generator = JobSpecificDatasetGenerator()
        
        # 몇 개 직업만 테스트
        test_jobs = ['전사', '아크메이지', '궁수']
        for job in test_jobs:
            generator.generate_job_dataset(job)
            print(f'   ✅ {job} 데이터셋 생성 완료')
        
        # 2. AI 시스템 초기화
        print('🤖 2단계: AI 시스템 초기화...')
        ai_system = UltimateIntegratedAISystem()
        
        # 3. 빠른 학습 (5분)
        print('🧠 3단계: 빠른 학습 (5분)...')
        await ai_system.run_night_learning(duration_hours=0.083)  # 5분 = 0.083시간
        
        # 4. 미니 토너먼트
        print('🏆 4단계: 미니 토너먼트...')
        await ai_system.run_ai_tournament()
        
        # 5. 진화 테스트
        print('🧬 5단계: 진화 테스트...')
        await ai_system.evolve_ai_generation()
        
        print('')
        print('🎉 빠른 학습 테스트 완료!')
        print('✅ 모든 AI 시스템이 정상 작동합니다!')
        print('💡 이제 \"밤새_AI_학습.bat\"로 본격적인 학습을 시작하세요!')
        
    except Exception as e:
        print(f'❌ 테스트 중 오류: {e}')
        print('🔧 시스템을 확인해주세요.')

asyncio.run(quick_test())
"

echo.
echo 🎉 빠른 테스트가 완료되었습니다!
echo.
pause
