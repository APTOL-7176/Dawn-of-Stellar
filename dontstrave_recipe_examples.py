#!/usr/bin/env python3
"""더 많은 돈스타브 스타일 요리 추가"""

from game.cooking_system import CookingSystem

def add_dontstrave_style_recipes():
    """돈스타브 스타일 제약 조건을 가진 새로운 요리들 추가 예시"""
    print("=== 돈스타브 스타일 새로운 요리 예시 ===")
    
    # 이런 식으로 더 복잡한 제약 조건을 가진 요리들을 추가할 수 있습니다:
    
    examples = [
        {
            "name": "바베큐 플래터",
            "forbidden": ["채소류", "과일류"],  # 순수 고기 요리
            "required": ["고기류", "향신료"],
            "max_amounts": {"고기류": 3.0, "향신료": 1.0},
            "cooking_method": "굽기",
            "description": "고기만으로 만든 바베큐 - 채소나 과일 금지"
        },
        {
            "name": "비건 파스타",
            "forbidden": ["고기류", "해산물", "달걀"],  # 완전 채식
            "required": ["곡물류", "채소류"],
            "max_amounts": {"곡물류": 2.0},
            "cooking_method": "끓이기",
            "description": "완전 채식 파스타 - 동물성 재료 일체 금지"
        },
        {
            "name": "해산물 리조또",
            "forbidden": ["고기류"],  # 해산물 전용
            "required": ["해산물", "곡물류", "액체류"],
            "max_amounts": {"해산물": 2.5, "곡물류": 1.5},
            "cooking_method": "끓이기",
            "description": "해산물만 사용 - 고기 사용 금지"
        },
        {
            "name": "디톡스 스무디",
            "forbidden": ["고기류", "해산물", "곡물류", "향신료"],  # 순수 자연재료만
            "required": ["과일류", "채소류"],
            "max_amounts": {"과일류": 3.0, "채소류": 2.0},
            "cooking_method": "갈기",
            "description": "독소 제거 스무디 - 가공식품 일체 금지"
        },
        {
            "name": "전사의 스테이크",
            "forbidden": ["과일류", "액체류"],  # 건조한 고기 요리
            "required": ["고기류"],
            "max_amounts": {"고기류": 4.0, "향신료": 2.0},
            "cooking_method": "굽기",
            "description": "전사를 위한 단단한 스테이크 - 부드러운 재료 금지"
        },
        {
            "name": "마법사의 포션",
            "forbidden": ["고기류", "해산물"],  # 신비로운 재료만
            "required": ["특수재료", "약초류", "액체류"],
            "max_amounts": {"특수재료": 5.0},
            "cooking_method": "연금술",
            "description": "마법사의 신비한 물약 - 속세의 재료 금지"
        }
    ]
    
    print("추가 가능한 돈스타브 스타일 요리들:")
    for recipe in examples:
        print(f"\n• {recipe['name']}")
        print(f"  금지 재료: {recipe['forbidden']}")
        print(f"  필수 재료: {recipe['required']}")
        print(f"  최대량 제한: {recipe['max_amounts']}")
        print(f"  조리법: {recipe['cooking_method']}")
        print(f"  설명: {recipe['description']}")

if __name__ == "__main__":
    add_dontstrave_style_recipes()
