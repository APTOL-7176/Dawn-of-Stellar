"""
🗺️ Dawn of Stellar - 맵 스캐닝 및 전술 제안 시스템
아군이 주변 맵을 감지하고 전술적 제안을 하는 시스템

2025년 8월 11일 구현
"""

import random
from typing import List, Tuple, Dict, Optional, Set
from enum import Enum
from dataclasses import dataclass

# 게임 모듈들
try:
    from .world import TileType, World
    from .error_logger import log_system
except ImportError:
    # 로깅이 없으면 더미 함수 사용
    def log_system(category, message, details=None):
        print(f"[MAP_SCANNER] {category}: {message}")
        if details:
            print(f"[MAP_SCANNER] Details: {details}")
    
    # 기본 TileType 정의
    class TileType(Enum):
        FLOOR = '.'
        WALL = '#'
        ENEMY = 'E'
        PLAYER = '@'
        TREASURE = '$'
        TRAP = '^'
        DOOR = '='
        STAIRS_UP = '<'
        STAIRS_DOWN = '>'
    from .character import Character
    from .ai_chat_system import AICharacterProfile
    from .error_logger import log_system, log_debug
except ImportError:
    # 개발 환경에서의 임포트
    TileType = None
    World = None
    Character = None
    AICharacterProfile = None

class ScanRange(Enum):
    """스캔 범위"""
    CLOSE = 3      # 근거리 (3x3)
    MEDIUM = 5     # 중거리 (5x5)
    FAR = 7        # 원거리 (7x7)
    FULL_ROOM = 15 # 방 전체 (15x15)

class ThreatLevel(Enum):
    """위험도"""
    SAFE = "안전"
    LOW = "낮음"
    MEDIUM = "보통"
    HIGH = "높음"
    CRITICAL = "위험"

class ActionPriority(Enum):
    """행동 우선순위"""
    IMMEDIATE = "즉시"
    HIGH = "높음"  
    MEDIUM = "보통"
    LOW = "낮음"
    OPTIONAL = "선택"

@dataclass
class MapObject:
    """맵 객체 정보"""
    tile_type: any  # TileType
    position: Tuple[int, int]
    distance: int
    description: str
    interaction_required: str = None  # 필요한 스킬/직업
    threat_level: ThreatLevel = ThreatLevel.SAFE
    potential_reward: str = None

@dataclass
class TacticalSuggestion:
    """전술적 제안"""
    title: str
    description: str
    priority: ActionPriority
    suggested_character: str = None  # 제안하는 캐릭터 이름
    required_skills: List[str] = None
    benefits: List[str] = None
    risks: List[str] = None
    alternative_options: List[str] = None

class MapScanner:
    """맵 스캐닝 및 분석 시스템"""
    
    def __init__(self, world, party_members: List):
        self.world = world
        self.party_members = party_members
        self.last_scan_position = None
        self.scan_history = []
        self.discovered_objects = []
        self.tactical_memory = []
        
        # 직업별 전문 분야
        self.job_expertise = {
            "도적": ["자물쇠해제", "함정감지", "은신", "정찰"],
            "기계공학자": ["기계조작", "기술분석", "장비수리", "구조분석"],
            "정령술사": ["마법감지", "원소분석", "에너지감지", "마법구조물"],
            "아크메이지": ["마법지식", "고대문자", "마법분석", "지식탐구"],
            "성기사": ["신성마법", "악마감지", "정화", "신성구조물"],
            "신관": ["치유마법", "축복", "정화", "신성감지"],
            "드루이드": ["자연친화", "동물소통", "식물감지", "자연구조물"],
            "철학자": ["지식탐구", "고대문자", "논리분석", "연구"],
            "궁수": ["원거리정찰", "적감지", "지형분석", "고지점확보"],
            "전사": ["전술분석", "방어전략", "위험평가", "근접전투"],
            "몽크": ["기감지", "위험직감", "내면감지", "정신집중"],
            "바드": ["정보수집", "사기진작", "소리분석", "사회성"],
            "암살자": ["은신정찰", "적약점파악", "그림자이동", "암살기회"],
            "네크로맨서": ["언데드감지", "죽음의기운", "영혼감지", "어둠마법"],
            "용기사": ["용의힘", "화염감지", "고온내성", "용족감지"],
            "검성": ["검의도", "기감지", "전투직감", "무기분석"],
            "시간술사": ["시간감지", "미래예지", "시간분석", "차원감지"],
            "연금술사": ["화학분석", "재료감지", "독성분석", "폭발물"],
            "차원술사": ["차원감지", "공간분석", "차원균열", "텔레포트"],
            "마검사": ["마검술", "마법검술", "이중감지", "마법전투"],
            "무당": ["영혼감지", "저주감지", "악령퇴치", "정신보호"],
            "암흑기사": ["어둠마법", "흡혈감지", "어둠의힘", "악마친화"],
            "해적": ["항해술", "보물감지", "교활함", "모험정신"],
            "사무라이": ["무사도", "명예감지", "검술분석", "일격필살"],
            "검투사": ["투기감각", "전투분석", "관중의식", "생존본능"],
            "기사": ["기사도", "정의감", "방어전술", "대의명분"],
            "광전사": ["광폭화", "전투광기", "위험무시", "파괴충동"]
        }
    
    def scan_area(self, center_pos: Tuple[int, int], scan_range: ScanRange = ScanRange.MEDIUM, 
                  vision_range: int = None) -> Dict:
        """지정된 범위 내 맵 스캔 (시야 시스템 기반)"""
        if not self.world or not self.world.current_map:
            return {"error": "맵 정보를 찾을 수 없습니다"}
        
        # 실제 시야 범위 확인
        if vision_range is None:
            if hasattr(self.world, 'party_manager') and self.world.party_manager:
                vision_range = self.world.party_manager.get_total_vision_range()
            else:
                vision_range = 3  # 기본 시야 범위
        
        x, y = center_pos
        # 스캔 범위를 시야 범위로 제한
        radius = min(scan_range.value, vision_range)
        
        scan_results = {
            "scan_center": center_pos,
            "scan_range": scan_range.name,
            "vision_range": vision_range,
            "effective_range": radius,
            "objects_found": [],
            "enemies_detected": [],
            "interactive_objects": [],
            "hazards": [],
            "opportunities": [],
            "tactical_suggestions": []
        }
        
        log_system("맵스캔", f"위치 {center_pos}에서 시야 {vision_range}, 스캔 {radius} 범위 스캔 시작")
        
        # 스캔 범위 내 모든 타일 조사 (시야 범위 내에서만)
        for scan_x in range(x - radius, x + radius + 1):
            for scan_y in range(y - radius, y + radius + 1):
                if self._is_valid_position(scan_x, scan_y):
                    # 유클리드 거리로 원형 시야 구현
                    dx, dy = scan_x - x, scan_y - y
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    # 시야 범위를 벗어나면 스킵
                    if distance > vision_range:
                        continue
                    
                    # 타일이 실제로 보이는지 확인
                    if hasattr(self.world, 'tiles') and self.world.tiles:
                        try:
                            if not self.world.tiles[scan_y][scan_x].visible:
                                continue  # 보이지 않는 타일은 스캔하지 않음
                        except (IndexError, AttributeError):
                            pass  # 시야 시스템이 없으면 계속 진행
                    
                    tile_info = self._analyze_tile(scan_x, scan_y, int(distance))
                    
                    if tile_info:
                        scan_results["objects_found"].append(tile_info)
                        
                        # 카테고리별 분류
                        if tile_info.tile_type in [TileType.ENEMY, TileType.BOSS]:
                            scan_results["enemies_detected"].append(tile_info)
                        elif tile_info.interaction_required:
                            scan_results["interactive_objects"].append(tile_info)
                        elif tile_info.threat_level != ThreatLevel.SAFE:
                            scan_results["hazards"].append(tile_info)
                        elif tile_info.potential_reward:
                            scan_results["opportunities"].append(tile_info)
        
        # 전술적 제안 생성
        scan_results["tactical_suggestions"] = self._generate_tactical_suggestions(scan_results)
        
        # 스캔 결과 저장
        self.last_scan_position = center_pos
        self.scan_history.append(scan_results)
        
        log_system("맵스캔", f"스캔 완료: 객체 {len(scan_results['objects_found'])}개, 적 {len(scan_results['enemies_detected'])}개, 상호작용 객체 {len(scan_results['interactive_objects'])}개 발견")
        
        return scan_results
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """유효한 위치인지 확인"""
        if not self.world or not self.world.current_map:
            return False
        return 0 <= x < len(self.world.current_map) and 0 <= y < len(self.world.current_map[0])
    
    def _analyze_tile(self, x: int, y: int, distance: int) -> Optional[MapObject]:
        """특정 타일 분석"""
        if not self._is_valid_position(x, y):
            return None
        
        tile_char = self.world.current_map[x][y]
        
        # 타일 타입 결정 (문자 -> TileType 매핑)
        tile_type_map = {
            "#": "WALL", ".": "FLOOR", "+": "DOOR", "&": "LOCKED_DOOR",
            "?": "SECRET_DOOR", "<": "STAIRS_UP", ">": "STAIRS_DOWN",
            "@": "PLAYER", "E": "ENEMY", "♔": "BOSS", "!": "ITEM",
            "$": "TREASURE", "=": "CHEST", "^": "TRAP", "/": "LEVER",
            "T": "ALTAR", "~": "FOUNTAIN", "B": "BOOKSHELF", "F": "FORGE",
            "G": "GARDEN", "*": "CRYSTAL", "X": "CURSED_ALTAR", "P": "POISON_CLOUD",
            "O": "DARK_PORTAL", "C": "CURSED_CHEST", "U": "UNSTABLE_FLOOR"
        }
        
        tile_type_str = tile_type_map.get(tile_char)
        if not tile_type_str or tile_type_str in ["WALL", "FLOOR"]:
            return None  # 일반 벽이나 바닥은 무시
        
        # 타일 정보 생성
        description, interaction, threat, reward = self._get_tile_info(tile_type_str)
        
        return MapObject(
            tile_type=tile_type_str,
            position=(x, y),
            distance=distance,
            description=description,
            interaction_required=interaction,
            threat_level=threat,
            potential_reward=reward
        )
    
    def _get_tile_info(self, tile_type: str) -> Tuple[str, str, ThreatLevel, str]:
        """타일 타입별 정보 반환"""
        tile_info = {
            "DOOR": ("문", None, ThreatLevel.SAFE, None),
            "LOCKED_DOOR": ("잠긴 문", "자물쇠해제", ThreatLevel.LOW, "통로 개방"),
            "SECRET_DOOR": ("비밀 문", "탐지 스킬", ThreatLevel.SAFE, "숨겨진 통로"),
            "STAIRS_UP": ("위층 계단", None, ThreatLevel.SAFE, "상층 이동"),
            "STAIRS_DOWN": ("아래층 계단", None, ThreatLevel.SAFE, "하층 이동"),
            "ENEMY": ("적", None, ThreatLevel.HIGH, "경험치/아이템"),
            "BOSS": ("보스", None, ThreatLevel.CRITICAL, "희귀 아이템"),
            "ITEM": ("아이템", None, ThreatLevel.SAFE, "장비/소모품"),
            "TREASURE": ("보물", None, ThreatLevel.SAFE, "귀중품"),
            "CHEST": ("보물상자", "자물쇠해제", ThreatLevel.SAFE, "다량의 아이템"),
            "TRAP": ("함정", "함정감지", ThreatLevel.MEDIUM, "함정 해제 후 보상"),
            "LEVER": ("레버", "기계조작", ThreatLevel.SAFE, "숨겨진 통로/보물"),
            "ALTAR": ("신성한 제단", "신성마법", ThreatLevel.SAFE, "축복 효과"),
            "FOUNTAIN": ("치유의 샘", None, ThreatLevel.SAFE, "체력/마나 회복"),
            "BOOKSHELF": ("고대 서적", "지식탐구", ThreatLevel.SAFE, "새로운 지식"),
            "FORGE": ("마법 대장간", "기계조작", ThreatLevel.SAFE, "장비 강화"),
            "GARDEN": ("신비한 정원", "자연친화", ThreatLevel.SAFE, "특수 재료"),
            "CRYSTAL": ("마법 수정", "정령술", ThreatLevel.SAFE, "마나 충전"),
            "CURSED_ALTAR": ("저주받은 제단", "신성마법", ThreatLevel.HIGH, "정화 후 강력한 축복"),
            "POISON_CLOUD": ("독성 구름", "자연친화", ThreatLevel.MEDIUM, "중화 후 안전 통로"),
            "DARK_PORTAL": ("어둠의 포털", "정령술", ThreatLevel.HIGH, "차단 후 마법 에너지"),
            "CURSED_CHEST": ("저주받은 상자", "신성마법", ThreatLevel.MEDIUM, "정화 후 희귀 아이템"),
            "UNSTABLE_FLOOR": ("불안정한 바닥", "기계조작", ThreatLevel.MEDIUM, "보강 후 안전 통로")
        }
        
        info = tile_info.get(tile_type, ("알 수 없는 객체", None, ThreatLevel.SAFE, None))
        return info[0], info[1], info[2], info[3]
    
    def _generate_tactical_suggestions(self, scan_results: Dict) -> List[TacticalSuggestion]:
        """스캔 결과를 바탕으로 전술적 제안 생성"""
        suggestions = []
        
        # 적 감지 시 제안
        if scan_results["enemies_detected"]:
            enemy_count = len(scan_results["enemies_detected"])
            boss_count = len([e for e in scan_results["enemies_detected"] if e.tile_type == "BOSS"])
            
            if boss_count > 0:
                suggestions.append(TacticalSuggestion(
                    title="⚔️ 보스 전투 대비 필요",
                    description=f"보스 {boss_count}마리가 감지되었습니다. 충분한 준비 후 도전하세요.",
                    priority=ActionPriority.HIGH,
                    suggested_character=self._get_best_character_for_skill("전술분석"),
                    benefits=["희귀 아이템 획득", "대량 경험치"],
                    risks=["높은 피해 위험", "파티 전멸 가능성"],
                    alternative_options=["우회 경로 탐색", "준비 완료 후 재도전"]
                ))
            
            if enemy_count > 2:
                suggestions.append(TacticalSuggestion(
                    title="🎯 다수 적 대응 전략",
                    description=f"적 {enemy_count}마리가 근처에 있습니다. 전술적 접근이 필요합니다.",
                    priority=ActionPriority.MEDIUM,
                    suggested_character=self._get_best_character_for_skill("전술분석"),
                    benefits=["안전한 전투", "효율적 처치"],
                    risks=["다수 포위 위험"],
                    alternative_options=["개별 격파", "함정 활용", "우회 경로"]
                ))
        
        # 상호작용 객체별 제안
        for obj in scan_results["interactive_objects"]:
            expert = self._get_best_character_for_skill(obj.interaction_required)
            if expert:
                suggestions.append(TacticalSuggestion(
                    title=f"🔧 {obj.description} 상호작용 가능",
                    description=f"{expert}가 {obj.interaction_required} 스킬로 {obj.description}와 상호작용할 수 있습니다.",
                    priority=ActionPriority.MEDIUM if obj.potential_reward else ActionPriority.LOW,
                    suggested_character=expert,
                    required_skills=[obj.interaction_required],
                    benefits=[obj.potential_reward] if obj.potential_reward else ["탐험 진행"],
                    risks=self._get_interaction_risks(obj.tile_type)
                ))
        
        # 위험 요소 경고
        for hazard in scan_results["hazards"]:
            if hazard.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                counter_skill = self._get_counter_skill(hazard.tile_type)
                expert = self._get_best_character_for_skill(counter_skill) if counter_skill else None
                
                suggestions.append(TacticalSuggestion(
                    title=f"⚠️ {hazard.description} 위험 감지",
                    description=f"거리 {hazard.distance}에서 위험한 {hazard.description}가 감지되었습니다.",
                    priority=ActionPriority.HIGH,
                    suggested_character=expert,
                    required_skills=[counter_skill] if counter_skill else [],
                    benefits=["안전 확보"] + ([hazard.potential_reward] if hazard.potential_reward else []),
                    risks=["접근 시 피해", "파티 위험"],
                    alternative_options=["우회", "원거리 공격", "준비 후 접근"]
                ))
        
        # 기회 요소 제안
        if scan_results["opportunities"]:
            closest_opportunity = min(scan_results["opportunities"], key=lambda x: x.distance)
            suggestions.append(TacticalSuggestion(
                title=f"💎 기회 발견: {closest_opportunity.description}",
                description=f"거리 {closest_opportunity.distance}에 {closest_opportunity.potential_reward} 기회가 있습니다.",
                priority=ActionPriority.MEDIUM,
                benefits=[closest_opportunity.potential_reward],
                risks=["시간 소모"]
            ))
        
        return suggestions
    
    def _get_best_character_for_skill(self, skill: str) -> Optional[str]:
        """특정 스킬에 가장 적합한 캐릭터 찾기"""
        if not skill or not self.party_members:
            return None
        
        for member in self.party_members:
            job_class = getattr(member, 'job_class', None) or getattr(member, 'character_class', '알 수 없음')
            if skill in self.job_expertise.get(job_class, []):
                return getattr(member, 'name', f"{job_class} 동료")
        
        return None
    
    def _get_counter_skill(self, tile_type: str) -> Optional[str]:
        """위험 요소에 대한 대응 스킬"""
        counter_skills = {
            "CURSED_ALTAR": "신성마법",
            "POISON_CLOUD": "자연친화", 
            "DARK_PORTAL": "정령술",
            "CURSED_CHEST": "신성마법",
            "UNSTABLE_FLOOR": "기계조작",
            "TRAP": "함정감지"
        }
        return counter_skills.get(tile_type)
    
    def _get_interaction_risks(self, tile_type: str) -> List[str]:
        """상호작용 시 위험 요소"""
        risks = {
            "CURSED_ALTAR": ["저주 효과", "마나 소모"],
            "CURSED_CHEST": ["저주 아이템", "함정 가능성"],
            "TRAP": ["피해 위험", "함정 발동"],
            "DARK_PORTAL": ["적 소환", "어둠 에너지"],
            "POISON_CLOUD": ["독 피해", "시야 제한"]
        }
        return risks.get(tile_type, ["미지의 위험"])
    
    def get_area_summary(self, position: Tuple[int, int]) -> str:
        """지역 요약 정보"""
        scan_results = self.scan_area(position, ScanRange.MEDIUM)
        
        summary_parts = []
        
        # 적 상황
        enemy_count = len(scan_results["enemies_detected"])
        if enemy_count > 0:
            boss_count = len([e for e in scan_results["enemies_detected"] if e.tile_type == "BOSS"])
            if boss_count > 0:
                summary_parts.append(f"⚔️ 보스 {boss_count}마리 포함 총 {enemy_count}마리 적 감지")
            else:
                summary_parts.append(f"⚔️ 적 {enemy_count}마리 감지")
        else:
            summary_parts.append("✅ 주변 안전")
        
        # 상호작용 객체
        interactive_count = len(scan_results["interactive_objects"])
        if interactive_count > 0:
            summary_parts.append(f"🔧 상호작용 가능한 객체 {interactive_count}개")
        
        # 기회 요소
        opportunity_count = len(scan_results["opportunities"])
        if opportunity_count > 0:
            summary_parts.append(f"💎 탐험 기회 {opportunity_count}개")
        
        # 위험 요소
        hazard_count = len(scan_results["hazards"])
        if hazard_count > 0:
            summary_parts.append(f"⚠️ 위험 요소 {hazard_count}개")
        
        return " | ".join(summary_parts) if summary_parts else "🗺️ 평범한 지역"
    
    def get_top_suggestions(self, position: Tuple[int, int], limit: int = 3) -> List[TacticalSuggestion]:
        """상위 전술 제안 반환"""
        scan_results = self.scan_area(position, ScanRange.MEDIUM)
        suggestions = scan_results["tactical_suggestions"]
        
        # 우선순위별 정렬
        priority_order = {
            ActionPriority.IMMEDIATE: 0,
            ActionPriority.HIGH: 1,
            ActionPriority.MEDIUM: 2,
            ActionPriority.LOW: 3,
            ActionPriority.OPTIONAL: 4
        }
        
        suggestions.sort(key=lambda x: priority_order.get(x.priority, 5))
        return suggestions[:limit]

def get_map_scanner() -> Optional[MapScanner]:
    """맵 스캐너 인스턴스 반환"""
    # 게임 인스턴스에서 월드와 파티 정보 가져오기
    try:
        # 이 부분은 실제 게임 구조에 맞게 수정 필요
        from main import game_instance
        if hasattr(game_instance, 'world') and hasattr(game_instance, 'party_members'):
            return MapScanner(game_instance.world, game_instance.party_members)
    except:
        pass
    
    return None
