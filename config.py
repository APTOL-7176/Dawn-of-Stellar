#!/usr/bin/env python3
"""
게임 설정 관리
"""

import os

class GameConfig:
    """게임 설정 클래스"""
    
    def __init__(self):
        # 환경 변수에서 개발 모드 확인
        self.DEVELOPMENT_MODE = os.getenv('ROGUELIKE_DEV_MODE', 'false').lower() == 'true'
        
        # BGM 설정
        self.BGM_SETTINGS = {
            "character_select": "prelude",  # 캐릭터 선택창 BGM
            "main_menu": "Main theme of FFVII"  # 메인화면 BGM
        }
        
        # 직업 해금 설정
        self.UNLOCKED_CLASSES = {
            "development": [
                "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크",
                "바드", "네크로맨서", "용기사", "검성", "정령술사", "암살자",
                "기계공학자", "무당", "해적", "사무라이", "드루이드", "철학자",
                "시간술사", "연금술사", "검투사", "기사", "신관", "마검사",
                "차원술사", "광전사"
            ],
            "normal": [
                "전사", "아크메이지", "궁수", "도적"  # 기본 4개 직업만 해금
            ]
        }
        
        # 패시브 해금 설정 (개발모드에서는 모든 패시브 해금)
        self.ALL_PASSIVES_UNLOCKED = self.DEVELOPMENT_MODE
        
    def get_available_classes(self):
        """현재 모드에 따른 사용 가능한 직업 반환"""
        if self.DEVELOPMENT_MODE:
            return self.UNLOCKED_CLASSES["development"]
        else:
            return self.UNLOCKED_CLASSES["normal"]
    
    def is_class_unlocked(self, class_name: str) -> bool:
        """특정 직업이 해금되었는지 확인"""
        return class_name in self.get_available_classes()
    
    def are_all_passives_unlocked(self) -> bool:
        """모든 패시브가 해금되었는지 확인"""
        return self.ALL_PASSIVES_UNLOCKED
    
    def get_bgm_track(self, scene: str) -> str:
        """특정 장면의 BGM 트랙 반환"""
        return self.BGM_SETTINGS.get(scene, "default")
    
    def print_mode_info(self):
        """현재 모드 정보 출력"""
        mode = "개발 모드" if self.DEVELOPMENT_MODE else "일반 모드"
        print(f"🎮 {mode}로 실행 중")
        print(f"📊 해금된 직업 수: {len(self.get_available_classes())}개")
        print(f"🎯 모든 패시브 해금: {'✅ 예' if self.ALL_PASSIVES_UNLOCKED else '❌ 아니오'}")

# 전역 설정 인스턴스
game_config = GameConfig()
