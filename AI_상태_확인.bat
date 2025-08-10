@echo off
chcp 65001 > nul
echo.
echo 📊 === AI 학습 상태 확인 === 📊
echo.

D:\로그라이크_2\.venv\Scripts\python.exe -c "
import os
import sqlite3
from datetime import datetime
from game.permanent_ai_learning_system import PermanentLearningDatabase

def check_ai_status():
    print('📊 === AI 학습 상태 상세 보고서 ===')
    print(f'🕐 확인 시간: {datetime.now().strftime(\"%%Y-%%m-%%d %%H:%%M:%%S\")}')
    print()
    
    # 1. 데이터베이스 파일 확인
    db_path = 'ai_permanent_learning.db'
    if os.path.exists(db_path):
        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / (1024 * 1024)
        size_kb = size_bytes / 1024
        
        print(f'💾 학습 데이터베이스:')
        print(f'   📁 파일 크기: {size_mb:.2f} MB ({size_kb:.1f} KB)')
        print(f'   📅 수정 시간: {datetime.fromtimestamp(os.path.getmtime(db_path)).strftime(\"%%Y-%%m-%%d %%H:%%M:%%S\")}')
        print()
        
        # 데이터베이스 내용 확인
        try:
            db = PermanentLearningDatabase()
            
            # 전체 직업 목록
            all_jobs = [
                '전사', '아크메이지', '궁수', '도적', '성기사', '암흑기사', '몽크', '바드',
                '네크로맨서', '용기사', '검성', '정령술사', '시간술사', '연금술사', 
                '차원술사', '마검사', '기계공학자', '무당', '암살자', '해적', 
                '사무라이', '드루이드', '철학자', '검투사', '기사', '신관', '광전사'
            ]
            
            print('🎯 직업별 학습 데이터:')
            total_skills = 0
            total_strategies = 0
            learned_jobs = 0
            
            for job in all_jobs:
                try:
                    skills = db.get_job_skills(job)
                    strategies = db.get_job_strategies(job)
                    
                    if skills or strategies:
                        skill_count = len(skills) if skills else 0
                        strategy_count = len(strategies) if strategies else 0
                        
                        print(f'   🏆 {job}: 스킬 {skill_count}개, 전략 {strategy_count}개')
                        
                        total_skills += skill_count
                        total_strategies += strategy_count
                        learned_jobs += 1
                    else:
                        print(f'   ⚪ {job}: 학습 전')
                except:
                    print(f'   ❌ {job}: 데이터 오류')
            
            print()
            print(f'📈 학습 통계:')
            print(f'   🎓 학습 완료 직업: {learned_jobs}/{len(all_jobs)}')
            print(f'   ⚔️ 총 스킬 수: {total_skills}개')
            print(f'   🧠 총 전략 수: {total_strategies}개')
            print(f'   📊 완료율: {(learned_jobs/len(all_jobs)*100):.1f}%%')
            
            # AI 지능 레벨 추정
            if learned_jobs == 0:
                ai_level = '🥚 초보 (미학습)'
            elif learned_jobs < 5:
                ai_level = '🐣 기초 (부분 학습)'
            elif learned_jobs < 10:
                ai_level = '🐥 중급 (기본 학습)'
            elif learned_jobs < 20:
                ai_level = '🐤 고급 (심화 학습)'
            elif learned_jobs < 27:
                ai_level = '🦅 전문가 (고도 학습)'
            else:
                ai_level = '🧠 천재 (완전 학습)'
            
            print()
            print(f'🧬 추정 AI 지능 레벨: {ai_level}')
            
        except Exception as e:
            print(f'❌ 데이터베이스 읽기 오류: {e}')
    
    else:
        print('💾 학습 데이터베이스: 없음')
        print('   💡 \"AI_빠른_테스트.bat\"를 먼저 실행해보세요!')
    
    print()
    
    # 2. 기타 AI 파일들 확인
    ai_files = [
        'game/permanent_ai_learning_system.py',
        'game/ultimate_integrated_ai_system.py', 
        'game/human_ai_hybrid_multiplayer.py',
        'game/ultimate_ai_learning_system.py'
    ]
    
    print('🔧 AI 시스템 파일:')
    for file_path in ai_files:
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f'   ✅ {file_path} ({size_kb:.1f} KB)')
        else:
            print(f'   ❌ {file_path} (없음)')
    
    print()
    print('📋 추천 행동:')
    
    if not os.path.exists(db_path):
        print('   1. \"AI_빠른_테스트.bat\" 실행으로 시스템 테스트')
        print('   2. \"밤새_AI_학습.bat\" 실행으로 본격 학습')
    elif learned_jobs < 10:
        print('   1. \"밤새_AI_학습.bat\" 실행으로 더 많은 직업 학습')
        print('   2. \"AI_학습_시작.bat\" 실행으로 집중 학습')
    else:
        print('   1. 게임 실행해서 똑똑해진 AI 확인')
        print('   2. \"AI_학습_시작.bat\"의 토너먼트 모드로 AI 대전')
    
    print()
    print('✅ AI 상태 확인 완료!')

check_ai_status()
"

echo.
echo 📊 상태 확인이 완료되었습니다!
pause
