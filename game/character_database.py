"""
Dawn Of Stellar - 캐릭터 데이터베이스
27개의 개성 있는 직업들과 그들의 특성
"""

from typing import Dict, List


class CharacterDatabase:
    """캐릭터 데이터베이스 클래스"""
    
    @staticmethod
    def get_all_characters() -> List[Dict]:
        """28개 직업에 맞는 기본 캐릭터 반환"""
        try:
            # auto_party_builder에서 실제 캐릭터 데이터 가져오기
            from game.auto_party_builder import AutoPartyBuilder
            
            builder = AutoPartyBuilder()
            
            # 직업별 설명 정의
            class_descriptions = {
                "전사": "강력한 물리 공격과 높은 방어력을 지닌 근접 전투의 전문가",
                "아크메이지": "강력한 마법 공격과 다양한 주문을 구사하는 마법의 대가",
                "궁수": "정확한 원거리 공격과 빠른 속도로 적을 제압하는 사격의 달인",
                "도적": "독과 은밀함을 이용한 지속 피해의 전문가. 적을 서서히 독살한다.",
                "성기사": "신성한 힘으로 적을 정화하고 동료를 치유하는 성기사",
                "암흑기사": "어둠의 힘을 다루며 생명력을 흡수하는 타락한 기사",
                "몽크": "내면의 기를 다스려 강력한 육체 능력을 발휘하는 수도자",
                "바드": "음악으로 동료를 돕고 적을 현혹하는 음유시인",
                "네크로맨서": "죽음을 조작하고 언데드를 부리는 어둠의 술사",
                "용기사": "용의 힘을 빌려 강력한 공격력을 발휘하는 드래곤의 기사",
                "검성": "검술의 달인으로 무한한 검기를 발휘하는 검의 성인",
                "정령술사": "정령의 힘을 빌려 자연의 마법을 사용하는 원소술사",
                "암살자": "그림자에 숨어 치명적인 일격을 가하는 냉혹한 살인자",
                "기계공학자": "기계 장치로 전략적인 우위를 만드는 발명가",
                "무당": "영적인 힘으로 악령을 퇴치하고 자연을 치유하는 주술사",
                "해적": "바다를 누비며 자유로운 전투를 펼치는 바다의 무법자",
                "사무라이": "카타나와 명예의 길을 걷는 동양의 무사",
                "드루이드": "자연과 하나되어 야생의 힘을 사용하는 자연술사",
                "철학자": "깊은 사고와 지혜로 적을 압도하는 현자",
                "시간술사": "시간과 공간을 조작하는 신비로운 마법사",
                "연금술사": "물질 변환과 포션 제작의 대가",
                "검투사": "투기장에서 단련된 강인한 전투 기술을 보유한 전사",
                "기사": "기사도 정신으로 무장한 중무장 기마 전사",
                "신관": "신성한 치유와 축복으로 동료를 돕는 성직자",
                "마검사": "마법과 검술을 조화롭게 사용하는 이중 특화 전사",
                "차원술사": "차원을 넘나들며 공간을 조작하는 궁극의 마법사",
                "광전사": "광기에 사로잡혀 압도적인 공격력을 발휘하는 전사"
            }
            
            # 역할별 특성 정의 (auto_party_builder와 동일하게 5개씩)
            role_traits = {
                "전사": ["적응형 무술", "전장의 지배자", "불굴의 의지", "전투 본능", "균형감각"],
                "아크메이지": ["마력 집중", "마나 순환", "원소 지배", "마법 폭주", "마법 연구자"],
                "궁수": ["정밀 사격", "민첩한 몸놀림", "원거리 숙련", "바람의 가호", "사냥꾼의 직감"],
                "도적": ["독술 마스터", "베놈 흡수", "맹독 면역", "독성 강화", "독의 지배자"],
                "성기사": ["치유의 빛", "신성한 가호", "축복받은 무기", "수호의 맹세", "정의의 분노"],
                "암흑기사": ["생명 흡수", "어둠의 계약", "불사의 의지", "어둠 조작", "공포 오라"],
                "몽크": ["내공 순환", "연타 숙련", "정신 수양", "참선의 깨달음", "기절 공격"],
                "바드": ["영감 부여", "다중 주문", "재생의 노래", "마법 저항", "카리스마"],
                "네크로맨서": ["언데드 소환", "영혼 조작", "생명력 흡수", "어둠 친화", "공포 유발"],
                "용기사": ["용의 분노", "비늘 방어", "생명력 흡수", "용의 숨결", "고대의 지혜"],
                "검성": ["무한 검기", "카타나 숙련", "검기 방출", "검의 춤", "무사도"],
                "정령술사": ["정령 소환", "원소 지배", "자연과의 대화", "정령 친화", "마나 효율"],
                "암살자": ["그림자 이동", "독 마스터", "일격필살", "은신 숙련", "치명타 특화"],
                "기계공학자": ["기계 소환", "발명가", "기계 친화", "수리 기술", "창의성"],
                "무당": ["영적 보호", "자연 치유", "영혼 시야", "악령 퇴치", "신령 소통"],
                "해적": ["해적 코드", "선상 전투", "보물 탐지", "해상 경험", "운명의 바람"],
                "사무라이": ["카타나 숙련", "명예의 길", "집중력", "일격필살", "무사도"],
                "드루이드": ["자연의 가호", "야생 동조", "자연 치유", "동물 친화", "식물 성장"],
                "철학자": ["깊은 사고", "지혜의 힘", "논리적 분석", "정신 집중", "학자의 직감"],
                "시간술사": ["시간 조작", "인과 조작", "시간 정지", "예지력", "시공간 이해"],
                "연금술사": ["물질 변환", "연금술 숙련", "포션 제작", "원소 이해", "실험 정신"],
                "검투사": ["검투 기술", "관중 어필", "전투 본능", "생존 의지", "명성"],
                "기사": ["기사도", "충성심", "중무장", "기마술", "귀족의 품격"],
                "신관": ["신성한 힘", "축복", "치유 마법", "정화", "신앙"],
                "마검사": ["마검 조화", "이중 숙련", "마법 검술", "원소 부여", "균형 감각"],
                "차원술사": ["차원 이동", "공간 왜곡", "차원 균열", "시공간 이해", "무한 지식"],
                "광전사": ["광기 상태", "분노", "무모한 돌진", "고통 무시", "전투 흥분"]
            }
            
            characters = []
            for class_name in builder.ALL_CLASSES:
                # auto_party_builder에서 스탯 가져오기
                stats = builder._get_class_base_stats(class_name)
                description = class_descriptions.get(class_name, "신비로운 능력을 지닌 전사")
                
                # 개발모드 여부에 따라 특성 설정
                try:
                    from config import game_config
                    if game_config.are_all_passives_unlocked():
                        # 개발모드: 모든 특성 표시
                        traits = role_traits.get(class_name, ["특수능력", "전투기술", "생존본능", "전술지식", "특별훈련"])
                    else:
                        # 일반모드: 특성 해금 안됨
                        traits = []
                except ImportError:
                    # config를 불러올 수 없으면 일반모드로 간주
                    traits = []
                
                characters.append({
                    "name": class_name,
                    "class": class_name,
                    "description": description,
                    "hp": stats["hp"],
                    "p_atk": stats["physical_attack"],
                    "m_atk": stats["magic_attack"],
                    "p_def": stats["physical_defense"],
                    "m_def": stats["magic_defense"],
                    "speed": stats["speed"],
                    "traits": traits
                })
            
            return characters
            
        except ImportError:
            # 폴백: 기본 4명 캐릭터 (일반모드에서는 특성 해금 안됨)
            # auto_party_builder의 스탯과 동일하게 설정
            return [
                {
                    "name": "전사", 
                    "class": "전사",
                    "description": "강력한 물리 공격과 높은 방어력을 지닌 근접 전투의 전문가",
                    "hp": 216, "p_atk": 75, "m_atk": 43, "p_def": 63, "m_def": 48, "speed": 56,
                    "traits": []  # 일반모드에서는 특성 해금 안됨
                },
                {
                    "name": "아크메이지", 
                    "class": "아크메이지",
                    "description": "강력한 마법 공격과 다양한 주문을 구사하는 마법의 대가",
                    "hp": 121, "p_atk": 43, "m_atk": 78, "p_def": 33, "m_def": 67, "speed": 58,
                    "traits": []  # 일반모드에서는 특성 해금 안됨
                },
                {
                    "name": "궁수", 
                    "class": "궁수",
                    "description": "정확한 원거리 공격과 빠른 속도로 적을 제압하는 사격의 달인",
                    "hp": 164, "p_atk": 74, "m_atk": 33, "p_def": 44, "m_def": 43, "speed": 68,
                    "traits": []  # 일반모드에서는 특성 해금 안됨
                },
                {
                    "name": "도적", 
                    "class": "도적",
                    "description": "빠른 속도와 치명타로 적의 약점을 노리는 그림자의 전사",
                    "hp": 150, "p_atk": 64, "m_atk": 38, "p_def": 43, "m_def": 49, "speed": 83,
                    "traits": []  # 일반모드에서는 특성 해금 안됨
                }
            ]
    
    @staticmethod
    def get_default_party() -> List[str]:
        """기본 파티 반환"""
        return ["전사", "아크메이지", "궁수", "도적"]
    
    @staticmethod
    def get_character_by_name(name: str) -> Dict:
        """이름으로 캐릭터 검색"""
        characters = CharacterDatabase.get_all_characters()
        for char in characters:
            if char["name"] == name:
                return char
        return None
    
    @staticmethod 
    def get_balanced_party_from_list(unlocked_names: List[str]) -> List[str]:
        """해금된 캐릭터 목록에서 균형잡힌 파티 구성"""
        try:
            from game.auto_party_builder import AutoPartyBuilder
            builder = AutoPartyBuilder()
            return builder.get_balanced_party_from_list(unlocked_names)
        except Exception as e:
            print(f"균형잡힌 파티 생성 실패: {e}")
            # 기본적으로 처음 4명 반환
            return unlocked_names[:4] if len(unlocked_names) >= 4 else unlocked_names
    
    @staticmethod
    def create_character_from_data(char_data: Dict):
        """캐릭터 데이터에서 Character 객체 생성"""
        # Character 클래스 동적 임포트로 순환참조 방지
        try:
            from game.character import Character
            return Character(
                name=char_data["name"],
                character_class=char_data["class"],
                max_hp=char_data.get("hp", 150),
                physical_attack=char_data.get("p_atk", 50),
                magic_attack=char_data.get("m_atk", 50),
                physical_defense=char_data.get("p_def", 50),
                magic_defense=char_data.get("m_def", 50),
                speed=char_data.get("speed", 50)
            )
        except ImportError:
            # Character 클래스를 찾을 수 없는 경우 딕셔너리 반환
            return char_data


def get_character_database():
    """전역 캐릭터 데이터베이스 반환"""
    return CharacterDatabase()
