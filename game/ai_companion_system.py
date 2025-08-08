"""
AI 파티원(용병) 시스템
플레이어가 직접 조작하지 않는 AI 동료들
"""
import random
import time
from typing import List, Dict, Optional, Tuple
from enum import Enum

class AIPersonality(Enum):
    """AI 성격 타입"""
    AGGRESSIVE = "aggressive"      # 공격적 - 항상 공격 우선
    DEFENSIVE = "defensive"        # 방어적 - 방어와 회복 우선
    BALANCED = "balanced"          # 균형잡힌 - 상황에 따라 판단
    SUPPORTIVE = "supportive"      # 지원형 - 버프와 힐링 중심
    TACTICAL = "tactical"          # 전술적 - 복잡한 전략 사용

class AIRequest(Enum):
    """AI가 플레이어에게 요청하는 사항"""
    NEED_HEALING = "need_healing"           # 회복 필요
    NEED_MP_POTION = "need_mp_potion"       # MP 물약 필요
    REQUEST_COORDINATED_ATTACK = "coord_attack"  # 협동 공격 요청
    REQUEST_FORMATION_CHANGE = "formation"   # 진형 변경 요청
    REQUEST_ITEM_SHARE = "item_share"       # 아이템 공유 요청
    WARNING_DANGER = "warning"              # 위험 경고
    SUGGEST_RETREAT = "retreat"             # 후퇴 제안

class AICompanion:
    """AI 동료 클래스"""
    
    def __init__(self, character, personality: AIPersonality = AIPersonality.BALANCED):
        self.character = character
        self.personality = personality
        self.trust_level = 50  # 0-100, 협력도에 영향
        self.morale = 75       # 0-100, 전투 효율성에 영향
        self.last_request_time = 0
        self.request_cooldown = 30.0  # 30초마다 요청 가능
        
        # AI 행동 가중치 (성격에 따라 다름)
        self.action_weights = self._get_personality_weights()
        
        # 아이템 사용 AI
        self.item_usage_cooldown = 0
        self.last_item_use_time = 0
        
        # 협동 공격 데이터
        self.coordinated_attack_ready = False
        self.preferred_combo_partner = None
        
    def _get_personality_weights(self) -> Dict[str, float]:
        """성격에 따른 행동 가중치 설정"""
        if self.personality == AIPersonality.AGGRESSIVE:
            return {
                "attack": 0.7,
                "skill_attack": 0.6,
                "defend": 0.1,
                "heal": 0.2,
                "item_use": 0.3
            }
        elif self.personality == AIPersonality.DEFENSIVE:
            return {
                "attack": 0.3,
                "skill_attack": 0.2,
                "defend": 0.6,
                "heal": 0.7,
                "item_use": 0.5
            }
        elif self.personality == AIPersonality.SUPPORTIVE:
            return {
                "attack": 0.2,
                "skill_attack": 0.4,
                "defend": 0.4,
                "heal": 0.8,
                "item_use": 0.7
            }
        elif self.personality == AIPersonality.TACTICAL:
            return {
                "attack": 0.5,
                "skill_attack": 0.7,
                "defend": 0.5,
                "heal": 0.6,
                "item_use": 0.6
            }
        else:  # BALANCED
            return {
                "attack": 0.5,
                "skill_attack": 0.5,
                "defend": 0.4,
                "heal": 0.5,
                "item_use": 0.4
            }
    
    def analyze_situation(self, party: List, enemies: List) -> Dict:
        """전투 상황 분석"""
        alive_allies = [ally for ally in party if ally.is_alive]
        alive_enemies = [enemy for enemy in enemies if enemy.is_alive]
        
        # 파티 상태 분석
        party_hp_avg = sum(ally.current_hp / ally.max_hp for ally in alive_allies) / len(alive_allies)
        critical_allies = [ally for ally in alive_allies if (ally.current_hp / ally.max_hp) < 0.3]
        
        # 적 상태 분석
        enemy_threat_level = sum(enemy.physical_attack + enemy.magic_attack for enemy in alive_enemies)
        weak_enemies = [enemy for enemy in alive_enemies if (enemy.current_hp / enemy.max_hp) < 0.4]
        
        return {
            "party_hp_avg": party_hp_avg,
            "critical_allies": len(critical_allies),
            "enemy_threat": enemy_threat_level,
            "weak_enemies": len(weak_enemies),
            "my_hp_ratio": self.character.current_hp / self.character.max_hp,
            "my_mp_ratio": self.character.current_mp / self.character.max_mp if self.character.max_mp > 0 else 1.0
        }
    
    def decide_action(self, party: List, enemies: List) -> Tuple[str, Dict]:
        """AI 행동 결정 - 특성 기반 강화"""
        situation = self.analyze_situation(party, enemies)
        
        # 특성 기반 행동 조정
        character_traits = getattr(self.character, 'traits', [])
        character_class = getattr(self.character, 'character_class', '전사')
        
        # 생존 우선 체크
        if situation["my_hp_ratio"] < 0.2:
            if self._can_use_healing_item():
                return "use_item", {"item_type": "healing"}
            elif situation["critical_allies"] >= 2:
                return "request", {"type": AIRequest.NEED_HEALING}
        
        # 특성 기반 우선순위 조정
        action_weights_copy = self.action_weights.copy()
        
        for trait in character_traits:
            trait_name = getattr(trait, 'name', '')
            trait_effects = getattr(trait, 'effects', {})
            
            # 공격 강화 특성
            if '공격력' in trait_name or '피해' in trait_name:
                action_weights_copy["attack"] *= 1.2
                action_weights_copy["skill_attack"] *= 1.15
            
            # 방어 강화 특성
            if '방어' in trait_name or '보호' in trait_name:
                action_weights_copy["defend"] *= 1.3
            
            # 회복 강화 특성
            if '치유' in trait_name or '회복' in trait_name:
                action_weights_copy["heal"] *= 1.4
            
            # 특정 직업 특성 반영
            if character_class == "성기사" and '성역' in trait_name:
                if situation["critical_allies"] > 0:
                    action_weights_copy["heal"] *= 1.5
            elif character_class == "검투사" and '처치' in trait_name:
                if situation["weak_enemies"] > 0:
                    action_weights_copy["attack"] *= 1.3
            elif character_class == "암살자" and '그림자' in trait_name:
                shadow_count = getattr(self.character, 'shadow_count', 0)
                if shadow_count >= 2:
                    action_weights_copy["skill_attack"] *= 1.4
            elif character_class == "광전사" and '광기' in trait_name:
                if situation["my_hp_ratio"] < 0.5:
                    action_weights_copy["attack"] *= 1.6
            elif character_class == "아크메이지" and '원소' in trait_name:
                action_weights_copy["skill_attack"] *= 1.3
        
        # 성격과 상황에 따른 행동 선택
        actions = []
        
        # 공격 옵션
        if situation["weak_enemies"] > 0:
            actions.append(("attack", action_weights_copy["attack"] * 1.3))  # 약한 적이 있으면 공격 가중치 증가
        else:
            actions.append(("attack", action_weights_copy["attack"]))
        
        # 스킬 사용
        if situation["enemy_threat"] > 200 or situation["weak_enemies"] > 1:
            actions.append(("skill", action_weights_copy["skill_attack"] * 1.2))
        else:
            actions.append(("skill", action_weights_copy["skill_attack"]))
        
        # 방어
        if situation["my_hp_ratio"] < 0.5 or situation["enemy_threat"] > 300:
            actions.append(("defend", action_weights_copy["defend"] * 1.5))
        else:
            actions.append(("defend", action_weights_copy["defend"]))
        
        # 회복
        if situation["critical_allies"] > 0 or situation["party_hp_avg"] < 0.6:
            actions.append(("heal", action_weights_copy["heal"] * 1.4))
        else:
            actions.append(("heal", action_weights_copy["heal"]))
        
        # 아이템 사용
        if self._should_use_item(situation):
            actions.append(("item", action_weights_copy["item_use"] * 1.3))
        else:
            actions.append(("item", action_weights_copy["item_use"]))
        
        # 협동 공격 요청
        if self._can_request_coordination(situation):
            actions.append(("coordinate", 0.8))
        
        # 가중치에 따른 행동 선택
        total_weight = sum(weight for _, weight in actions)
        rand = random.uniform(0, total_weight)
        current = 0
        
        for action, weight in actions:
            current += weight
            if rand <= current:
                return self._execute_action(action, situation, party, enemies)
        
        # 기본값: 공격
        return "attack", {}
    
    def _execute_action(self, action: str, situation: Dict, party: List, enemies: List) -> Tuple[str, Dict]:
        """선택된 행동 실행"""
        if action == "attack":
            target = self._select_attack_target(enemies)
            return "attack", {"target": target}
        
        elif action == "skill":
            skill, target = self._select_skill_and_target(party, enemies, situation)
            return "skill", {"skill": skill, "target": target}
        
        elif action == "defend":
            return "defend", {}
        
        elif action == "heal":
            target = self._select_heal_target(party)
            return "heal", {"target": target}
        
        elif action == "item":
            item_type = self._select_item_to_use(situation)
            return "use_item", {"item_type": item_type}
        
        elif action == "coordinate":
            return "request", {"type": AIRequest.REQUEST_COORDINATED_ATTACK}
        
        else:
            return "attack", {}
    
    def _select_attack_target(self, enemies: List):
        """공격 대상 선택"""
        alive_enemies = [enemy for enemy in enemies if enemy.is_alive]
        if not alive_enemies:
            return None
        
        if self.personality == AIPersonality.TACTICAL:
            # 전술적: 가장 위험한 적 우선
            return max(alive_enemies, key=lambda e: e.physical_attack + e.magic_attack)
        elif self.personality == AIPersonality.AGGRESSIVE:
            # 공격적: 가장 약한 적 우선 (빠른 처치)
            return min(alive_enemies, key=lambda e: e.current_hp / e.max_hp)
        else:
            # 기본: 랜덤하되 약간 약한 적 선호
            weights = [(2.0 - (enemy.current_hp / enemy.max_hp)) for enemy in alive_enemies]
            return random.choices(alive_enemies, weights=weights)[0]
    
    def _select_skill_and_target(self, party: List, enemies: List, situation: Dict):
        """스킬과 대상 선택 - 독 시스템 통합"""
        # 간단한 스킬 선택 로직
        available_skills = getattr(self.character, 'available_skills', [])
        if not available_skills:
            return None, None
        
        character_class = getattr(self.character, 'character_class', '')
        
        # MP 상황 고려
        usable_skills = [skill for skill in available_skills 
                        if hasattr(skill, 'mp_cost') and skill.mp_cost <= self.character.current_mp]
        
        if not usable_skills:
            return None, None
        
        # 상황에 맞는 스킬 선택
        if situation["critical_allies"] > 0:
            # 힐링 스킬 우선
            heal_skills = [skill for skill in usable_skills if 'heal' in skill.name.lower() or 
                          'cure' in skill.name.lower() or '치유' in skill.name or '회복' in skill.name]
            if heal_skills:
                skill = random.choice(heal_skills)
                target = min([ally for ally in party if ally.is_alive], key=lambda a: a.current_hp / a.max_hp)
                return skill, target
        
        # 도적 전용 독 전략
        if character_class == "도적":
            return self._select_rogue_skill_strategy(usable_skills, enemies, situation)
        
        # 공격 스킬
        attack_skills = [skill for skill in usable_skills if 'attack' in skill.name.lower() or 
                        'damage' in skill.name.lower() or '공격' in skill.name or '타격' in skill.name]
        if attack_skills:
            skill = random.choice(attack_skills)
            target = self._select_attack_target(enemies)
            return skill, target
        
        # 기본값
        skill = random.choice(usable_skills)
        target = random.choice([enemy for enemy in enemies if enemy.is_alive])
        return skill, target
    
    def _select_rogue_skill_strategy(self, usable_skills: List, enemies: List, situation: Dict):
        """도적 전용 독 전략 스킬 선택"""
        alive_enemies = [enemy for enemy in enemies if enemy.is_alive]
        if not alive_enemies:
            return None, None
        
        # 베놈 파워 확인
        venom_power = getattr(self.character, 'venom_power', 0)
        
        # 독 관련 스킬들 분류
        poison_skills = []
        venom_skills = []
        attack_skills = []
        
        for skill in usable_skills:
            skill_name = skill.name.lower()
            korean_name = skill.name
            
            if ('독' in korean_name or 'poison' in skill_name or 
                '베놈' in korean_name or 'venom' in skill_name):
                if '흡수' in korean_name or 'absorption' in skill_name:
                    venom_skills.append(skill)
                else:
                    poison_skills.append(skill)
            else:
                attack_skills.append(skill)
        
        # 독이 걸리지 않은 적들 찾기
        non_poisoned_enemies = []
        poisoned_enemies = []
        
        for enemy in alive_enemies:
            enemy_status = getattr(enemy, 'status_effects', {})
            is_poisoned = any('독' in str(effect) or 'poison' in str(effect).lower() 
                             for effect in enemy_status.keys())
            
            if is_poisoned:
                poisoned_enemies.append(enemy)
            else:
                non_poisoned_enemies.append(enemy)
        
        # 전략 결정
        # 1. 독이 걸리지 않은 적이 있으면 독 스킬 우선
        if non_poisoned_enemies and poison_skills:
            skill = random.choice(poison_skills)
            target = random.choice(non_poisoned_enemies)
            return skill, target
        
        # 2. 베놈 파워가 높고 독 흡수 스킬이 있으면 사용
        if venom_power > 30 and venom_skills:
            skill = random.choice(venom_skills)
            # 독이 가장 많이 걸린 적 우선
            if poisoned_enemies:
                target = max(poisoned_enemies, key=lambda e: self._get_enemy_poison_amount(e))
            else:
                target = random.choice(alive_enemies)
            return skill, target
        
        # 3. 일반 공격 스킬
        if attack_skills:
            skill = random.choice(attack_skills)
            target = self._select_attack_target(alive_enemies)
            return skill, target
        
        # 4. 기본값
        if usable_skills:
            skill = random.choice(usable_skills)
            target = random.choice(alive_enemies)
            return skill, target
        
        return None, None
    
    def _get_enemy_poison_amount(self, enemy) -> float:
        """적의 독 누적량 확인"""
        try:
            status_effects = getattr(enemy, 'status_effects', {})
            total_poison = 0.0
            
            for effect_name, effect_data in status_effects.items():
                if '독' in effect_name or 'poison' in effect_name.lower():
                    if isinstance(effect_data, dict):
                        amount = effect_data.get('amount', 0)
                        total_poison += amount
                    elif hasattr(effect_data, 'amount'):
                        total_poison += effect_data.amount
            
            return total_poison
        except:
            return 0.0
    
    def _select_heal_target(self, party: List):
        """회복 대상 선택"""
        alive_allies = [ally for ally in party if ally.is_alive and ally.current_hp < ally.max_hp]
        if not alive_allies:
            return None
        
        # 가장 체력이 낮은 아군 선택
        return min(alive_allies, key=lambda ally: ally.current_hp / ally.max_hp)
    
    def _can_use_healing_item(self) -> bool:
        """회복 아이템 사용 가능 여부"""
        current_time = time.time()
        if current_time - self.last_item_use_time < self.item_usage_cooldown:
            return False
        
        # 인벤토리에 회복 아이템이 있는지 확인 (간단 버전)
        return hasattr(self.character, 'inventory') and self.character.inventory
    
    def _should_use_item(self, situation: Dict) -> bool:
        """아이템 사용 여부 결정"""
        if not self._can_use_healing_item():
            return False
        
        # HP가 낮거나 MP가 부족할 때
        return situation["my_hp_ratio"] < 0.5 or situation["my_mp_ratio"] < 0.3
    
    def _select_item_to_use(self, situation: Dict) -> str:
        """사용할 아이템 타입 선택"""
        if situation["my_hp_ratio"] < 0.4:
            return "healing"
        elif situation["my_mp_ratio"] < 0.3:
            return "mp_potion"
        else:
            return "healing"
    
    def _can_request_coordination(self, situation: Dict) -> bool:
        """협동 공격 요청 가능 여부"""
        current_time = time.time()
        if current_time - self.last_request_time < self.request_cooldown:
            return False
        
        # 상황이 어렵거나 좋은 기회일 때만
        return (situation["enemy_threat"] > 250 or 
                situation["weak_enemies"] > 0 and situation["party_hp_avg"] > 0.6)
    
    def make_request_to_player(self, request_type: AIRequest, context: Dict = None) -> str:
        """플레이어에게 요청/제안하기"""
        self.last_request_time = time.time()
        
        personality_messages = {
            AIPersonality.AGGRESSIVE: {
                AIRequest.REQUEST_COORDINATED_ATTACK: f"💥 {self.character.name}: 지금이야! 같이 공격하자!",
                AIRequest.NEED_HEALING: f"🩹 {self.character.name}: 치료가 필요해! 빨리!",
                AIRequest.WARNING_DANGER: f"⚠️ {self.character.name}: 위험해! 조심해!",
            },
            AIPersonality.DEFENSIVE: {
                AIRequest.REQUEST_COORDINATED_ATTACK: f"🛡️ {self.character.name}: 함께 신중하게 공격해보자.",
                AIRequest.NEED_HEALING: f"💚 {self.character.name}: 회복이 필요합니다.",
                AIRequest.SUGGEST_RETREAT: f"🚪 {self.character.name}: 후퇴를 고려해봐야 할 것 같아요.",
            },
            AIPersonality.SUPPORTIVE: {
                AIRequest.REQUEST_COORDINATED_ATTACK: f"✨ {self.character.name}: 제가 지원할게요! 공격하세요!",
                AIRequest.NEED_HEALING: f"🌿 {self.character.name}: 치료가 필요해요.",
                AIRequest.REQUEST_ITEM_SHARE: f"🎒 {self.character.name}: 아이템을 나누어 써요.",
            },
            AIPersonality.TACTICAL: {
                AIRequest.REQUEST_COORDINATED_ATTACK: f"🎯 {self.character.name}: 전략적으로 협공합시다.",
                AIRequest.REQUEST_FORMATION_CHANGE: f"📋 {self.character.name}: 진형을 바꿔보는 게 어떨까요?",
                AIRequest.WARNING_DANGER: f"📊 {self.character.name}: 분석 결과, 위험합니다.",
            }
        }
        
        # 기본 메시지
        default_messages = {
            AIRequest.REQUEST_COORDINATED_ATTACK: f"⚔️ {self.character.name}: 협동 공격하자!",
            AIRequest.NEED_HEALING: f"💔 {self.character.name}: 치료가 필요해!",
            AIRequest.NEED_MP_POTION: f"🔮 {self.character.name}: MP 물약이 필요해!",
            AIRequest.REQUEST_ITEM_SHARE: f"🤝 {self.character.name}: 아이템을 공유하자!",
            AIRequest.WARNING_DANGER: f"⚠️ {self.character.name}: 위험해!",
            AIRequest.SUGGEST_RETREAT: f"🏃 {self.character.name}: 후퇴하자!",
        }
        
        # 성격별 메시지가 있으면 사용, 없으면 기본 메시지
        personality_msgs = personality_messages.get(self.personality, {})
        message = personality_msgs.get(request_type, default_messages.get(request_type, f"{self.character.name}: 도와줘!"))
        
        return message
    
    def respond_to_player_action(self, player_action: str, success: bool):
        """플레이어 행동에 대한 반응"""
        if success:
            self.trust_level = min(100, self.trust_level + 5)
            self.morale = min(100, self.morale + 3)
            
            # 성격별 반응
            if self.personality == AIPersonality.AGGRESSIVE:
                return f"🔥 {self.character.name}: 좋아! 계속 가자!"
            elif self.personality == AIPersonality.SUPPORTIVE:
                return f"💝 {self.character.name}: 고마워요! 정말 도움이 됐어요!"
            elif self.personality == AIPersonality.TACTICAL:
                return f"👍 {self.character.name}: 훌륭한 판단이었습니다."
            else:
                return f"😊 {self.character.name}: 잘했어!"
        else:
            self.trust_level = max(0, self.trust_level - 3)
            self.morale = max(0, self.morale - 2)
            
            if self.personality == AIPersonality.DEFENSIVE:
                return f"😟 {self.character.name}: 괜찮아요, 다음엔 더 조심해요."
            else:
                return f"😕 {self.character.name}: 아쉽네... 다음 기회에!"
    
    def get_combat_effectiveness(self) -> float:
        """전투 효율성 계산 (사기와 신뢰도에 따라)"""
        base_effectiveness = 1.0
        morale_bonus = (self.morale - 50) * 0.01  # -0.5 ~ +0.5
        trust_bonus = (self.trust_level - 50) * 0.005  # -0.25 ~ +0.25
        
        return max(0.3, base_effectiveness + morale_bonus + trust_bonus)  # 최소 30% 효율

class AIMercenaryManager:
    """AI 용병 관리자"""
    
    def __init__(self):
        self.available_mercenaries = []  # 고용 가능한 용병들
        self.active_companions = []      # 현재 활성화된 AI 동료들
        self.pending_requests = []       # 대기 중인 요청들
        self.coordination_combo_ready = False
        
    def generate_random_mercenary(self, level_range: Tuple[int, int] = (1, 10)):
        """랜덤 용병 생성"""
        from game.character_database import CharacterDatabase
        
        char_db = CharacterDatabase()
        all_characters = char_db.get_all_characters()
        
        # 랜덤 캐릭터 선택
        char_data = random.choice(all_characters)
        character = char_db.create_character(char_data['class'])
        
        # 레벨 설정
        target_level = random.randint(*level_range)
        while character.level < target_level:
            character.gain_experience(character.experience_to_next)
        
        # 랜덤 성격 할당
        personality = random.choice(list(AIPersonality))
        
        # 용병 이름 수정 (AI 표시)
        character.name = f"{character.name} (AI)"
        
        return AIMercenaryEncounter(character, personality)
    
    def add_companion(self, companion: AICompanion):
        """AI 동료 추가"""
        self.active_companions.append(companion)
        print(f"✅ {companion.character.name}이(가) 파티에 합류했습니다!")
        print(f"   성격: {companion.personality.value}")
        print(f"   신뢰도: {companion.trust_level}/100")
    
    def process_ai_turn(self, companion: AICompanion, party: List, enemies: List):
        """AI 턴 처리"""
        action_type, action_data = companion.decide_action(party, enemies)
        
        if action_type == "request":
            request_type = action_data["type"]
            message = companion.make_request_to_player(request_type)
            self.pending_requests.append({
                "companion": companion,
                "type": request_type,
                "message": message,
                "timestamp": time.time()
            })
            return "request", action_data
        
        return action_type, action_data
    
    def get_pending_requests(self) -> List[Dict]:
        """대기 중인 요청 목록"""
        current_time = time.time()
        # 30초 지난 요청은 제거
        self.pending_requests = [req for req in self.pending_requests 
                               if current_time - req["timestamp"] < 30.0]
        return self.pending_requests
    
    def respond_to_request(self, request_index: int, response: bool):
        """요청에 대한 응답 처리"""
        if 0 <= request_index < len(self.pending_requests):
            request = self.pending_requests.pop(request_index)
            companion = request["companion"]
            response_msg = companion.respond_to_player_action("help", response)
            return response_msg
        return None

class AIMercenaryEncounter:
    """용병 조우 이벤트"""
    
    def __init__(self, character, personality: AIPersonality):
        self.character = character
        self.personality = personality
        self.hire_cost = character.level * 100 + random.randint(50, 200)
        self.hire_duration = random.randint(10, 20)  # 10-20층 동안 동행
        
    def get_hire_info(self) -> str:
        """고용 정보 반환"""
        personality_desc = {
            AIPersonality.AGGRESSIVE: "공격적이고 적극적인 전투 스타일",
            AIPersonality.DEFENSIVE: "신중하고 방어적인 전투 스타일", 
            AIPersonality.BALANCED: "균형잡힌 만능 전투 스타일",
            AIPersonality.SUPPORTIVE: "지원과 회복에 특화된 스타일",
            AIPersonality.TACTICAL: "전략적이고 계산적인 전투 스타일"
        }
        
        return f"""
🤝 용병 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 이름: {self.character.name}
⚔️ 클래스: {self.character.character_class}
⭐ 레벨: {self.character.level}
💫 성격: {personality_desc[self.personality]}
💰 고용비: {self.hire_cost} 골드
⏰ 동행 기간: {self.hire_duration}층
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 AI 동료는 자동으로 전투에 참여하며, 가끔 플레이어에게 조언이나 도움을 요청합니다.
   적절히 협력하면 신뢰도가 상승하여 더 효과적인 전투가 가능합니다!
        """

# 전역 AI 매니저 인스턴스
ai_mercenary_manager = AIMercenaryManager()

def create_mercenary_encounter(player_level: int) -> AIMercenaryEncounter:
    """플레이어 레벨에 맞는 용병 조우 생성"""
    level_range = (max(1, player_level - 2), player_level + 3)
    return ai_mercenary_manager.generate_random_mercenary(level_range)

def process_coordination_request(companion: AICompanion, party: List, enemies: List) -> bool:
    """협동 공격 요청 처리"""
    # 플레이어가 수락하면 다음 턴에 협동 공격 보너스 적용
    companion.coordinated_attack_ready = True
    return True
