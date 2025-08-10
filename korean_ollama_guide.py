"""
🇰🇷 Dawn of Stellar - 한글 AI 모델 설정 가이드
Ollama에서 한국어 특화 모델 사용하기

2025년 8월 10일 - 한글 로바트 최적화!
"""

def setup_korean_ollama_guide():
    print("🇰🇷 === 한글 AI 모델 설정 가이드 ===")
    print()
    
    print("📋 추천 한글 모델 순위:")
    print("═══════════════════════════════════════")
    
    models = [
        {
            "rank": "🏆 1위",
            "name": "EXAONE 3.5 (엑사원)",
            "command": "ollama pull exaone3.5:7.8b",
            "size": "4.7GB",
            "pros": ["LG AI 공식 모델", "한영 이중언어", "안정적 성능", "확실히 다운로드 가능", "빠른 속도"],
            "cons": ["대화가 다소 격식적"],
            "best_for": "로바트 대화, 기술 질문, 안정적 사용"
        },
        {
            "rank": "🥈 2위",
            "name": "EEVE-Korean (이브)",
            "command": "ollama pull bnksys/yanolja-eeve-korean-instruct-10.8b",
            "size": "6.2GB",
            "pros": ["가장 자연스러운 한국어", "한국 문화 이해도 높음", "창작 능력 뛰어남"],
            "cons": ["용량이 큼", "다소 느림", "가끔 다운로드 실패"],
            "best_for": "창작, 스토리텔링 (다운로드 가능할 때)"
        },
        {
            "rank": "🥉 3위",
            "name": "Korean Llama 3.2", 
            "command": "ollama pull timHan/llama3.2korean3B4QKM",
            "size": "2.0GB",
            "pros": ["빠른 속도", "적은 메모리", "Meta 기반", "한국어 파인튜닝"],
            "cons": ["성능 제한적", "짧은 응답"],
            "best_for": "저사양 PC, 빠른 응답"
        },
        {
            "rank": "⚡ 경량",
            "name": "DNA Korean 8B",
            "command": "ollama pull dnotitia/dna:8b", 
            "size": "4.7GB",
            "pros": ["한국어 특화", "SOTA 성능", "빠른 속도", "한영 이중언어"],
            "cons": ["상대적으로 새로운 모델"],
            "best_for": "일반 대화, 한국어 작업"
        }
    ]
    
    for model in models:
        print(f"\n{model['rank']} {model['name']}")
        print(f"📦 설치: {model['command']}")
        print(f"💾 용량: {model['size']}")
        print(f"✅ 장점: {', '.join(model['pros'])}")
        print(f"⚠️ 단점: {', '.join(model['cons'])}")
        print(f"🎯 추천 용도: {model['best_for']}")
        print("-" * 50)
    
    print("\n🎮 === Dawn of Stellar 로바트용 설정 ===")
    print("1. 위 모델 중 하나 설치")
    print("2. ollama serve 실행")
    print("3. 런처선택_GPT5.bat → [5] AI API 키 설정")
    print("4. Ollama 선택")
    print("5. 모델명 입력 (예: exaone3.5:7.8b)")
    
    print("\n💡 === 시스템별 추천 ===")
    system_recommendations = {
        "고성능 PC (RAM 16GB+)": "EXAONE 3.5 7.8B",
        "중간 성능 PC (RAM 8-16GB)": "EXAONE 3.5 7.8B",
        "저성능 PC (RAM 8GB 이하)": "설치 불가 (클라우드 API 사용 권장)",
        "게임용 최적화": "EXAONE 3.5 7.8B (빠른 응답)",
        "자연스러운 대화": "EXAONE 3.5 7.8B (안정적)",
        "기술적 질문": "EXAONE 3.5 7.8B (최고)"
    }
    
    for system, recommendation in system_recommendations.items():
        print(f"• {system}: {recommendation}")
    
    print("\n🚀 === 빠른 설치 스크립트 ===")
    print("# 1. Ollama 설치 확인")
    print("ollama --version")
    print()
    print("# 2. 추천 모델 설치 (택 1)")
    print("ollama pull exaone3.5:7.8b  # LG AI 공식, 최고 안정성")
    print("ollama pull bnksys/yanolja-eeve-korean-instruct-10.8b  # 자연스러운 대화 (불안정)")
    print("ollama pull dnotitia/dna:8b  # 한국어 SOTA")
    print("ollama pull timHan/llama3.2korean3B4QKM  # 경량화")
    print("ollama pull solar-ko:7b                              # 빠른 속도")
    print()
    print("# 3. 서버 실행")
    print("ollama serve")
    print()
    print("# 4. 테스트")
    print('ollama run exaone3.5:7.8b "안녕하세요!"')
    print('ollama run bnksys/yanolja-eeve-korean-instruct-10.8b "안녕하세요!"')
    print('ollama run dnotitia/dna:8b "안녕하세요!"')

def korean_model_comparison():
    print("\n📊 === 한글 모델 상세 비교 ===")
    
    comparison = {
        "자연스러운 한국어": {
            "EXAONE 3.5": "⭐⭐⭐⭐⭐",
            "EEVE-Korean": "⭐⭐⭐⭐⭐",
            "Solar-Ko": "⭐⭐⭐⭐",
            "KoVicuna": "⭐⭐⭐",
            "KoAlpaca": "⭐⭐⭐"
        },
        "응답 속도": {
            "EXAONE 3.5": "⭐⭐⭐⭐⭐",
            "EEVE-Korean": "⭐⭐⭐",
            "Solar-Ko": "⭐⭐⭐⭐⭐",
            "KoVicuna": "⭐⭐",
            "KoAlpaca": "⭐⭐⭐"
        },
        "창작 능력": {
            "EXAONE 3.5": "⭐⭐⭐⭐",
            "EEVE-Korean": "⭐⭐⭐⭐⭐",
            "Solar-Ko": "⭐⭐⭐",
            "KoVicuna": "⭐⭐⭐⭐",
            "KoAlpaca": "⭐⭐⭐"
        },
        "기술적 질문": {
            "EXAONE 3.5": "⭐⭐⭐⭐⭐",
            "EEVE-Korean": "⭐⭐⭐",
            "Solar-Ko": "⭐⭐⭐⭐⭐",
            "KoVicuna": "⭐⭐⭐⭐",
            "KoAlpaca": "⭐⭐⭐"
        },
        "메모리 효율성": {
            "EXAONE 3.5": "⭐⭐⭐⭐",
            "EEVE-Korean": "⭐⭐⭐",
            "Solar-Ko": "⭐⭐⭐⭐",
            "KoVicuna": "⭐⭐",
            "KoAlpaca": "⭐⭐⭐"
        }
    }
    
    for category, scores in comparison.items():
        print(f"\n📈 {category}:")
        for model, score in scores.items():
            print(f"  {model:15} {score}")

if __name__ == "__main__":
    setup_korean_ollama_guide()
    korean_model_comparison()
    
    print("\n🎯 === 로바트별 추천 모델 ===")
    robat_recommendations = {
        "전사": "EXAONE 3.5 (빠른 반응 + 안정성)",
        "아크메이지": "EXAONE 3.5 (지적인 대화 + 기술력)",
        "해적": "EEVE-Korean (자유분방한 표현)",
        "철학자": "EXAONE 3.5 (논리적 사고)",
        "기계공학자": "EXAONE 3.5 (기술적 정확성)",
        "바드": "EEVE-Korean (창작 능력)",
        "네크로맨서": "EEVE-Korean (신비로운 표현)"
    }
    
    for robat, model in robat_recommendations.items():
        print(f"• {robat} 로바트: {model}")
    
    print("\n🌟 결론: 로바트 대화용으로는 EXAONE 3.5가 가장 안정적!")
    print("💡 창작 능력이 필요하면 EEVE-Korean 추천! (다운로드 가능한 경우)")
    print("🏆 종합 추천: EXAONE 3.5 (LG AI 공식 지원, 안정성 1위)")
    print("\n⚠️ 중요: EEVE 계열은 다운로드 오류가 자주 발생하므로 EXAONE 우선 권장!")
