"""
전투 로깅 시스템 - 모든 데미지와 중요한 이벤트를 기록
"""

import json
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class CombatLogger:
    """전투 로그 시스템"""
    
    def __init__(self):
        self.log_file = Path("combat_detailed_log.json")
        self.session_logs = []
        self.current_battle = None
        self.turn_counter = 0
        
    def start_battle(self, party: List, enemies: List, location: str = "Unknown"):
        """전투 시작 로그"""
        self.current_battle = {
            "battle_id": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.datetime.now().isoformat(),
            "location": location,
            "party_info": [],
            "enemy_info": [],
            "turns": [],
            "damage_summary": {
                "total_player_damage": 0,
                "total_enemy_damage": 0,
                "total_brv_damage": 0,
                "total_hp_damage": 0
            }
        }
        
        # 파티 정보 기록
        for char in party:
            if hasattr(char, 'is_alive') and char.is_alive:
                char_info = {
                    "name": getattr(char, 'name', 'Unknown'),
                    "class": getattr(char, 'character_class', 'Unknown'),
                    "level": getattr(char, 'level', 1),
                    "max_hp": getattr(char, 'max_hp', 0),
                    "current_hp": getattr(char, 'current_hp', 0),
                    "physical_attack": getattr(char, 'physical_attack', 0),
                    "physical_defense": getattr(char, 'physical_defense', 0),
                    "magic_attack": getattr(char, 'magic_attack', 0),
                    "magic_defense": getattr(char, 'magic_defense', 0),
                    "speed": getattr(char, 'speed', 0),
                    "brave_points": getattr(char, 'brave_points', 0),
                    "max_brv": getattr(char, 'max_brv', 0)
                }
                self.current_battle["party_info"].append(char_info)
        
        # 적 정보 기록
        for enemy in enemies:
            if hasattr(enemy, 'is_alive') and enemy.is_alive:
                enemy_info = {
                    "name": getattr(enemy, 'name', 'Unknown'),
                    "level": getattr(enemy, 'level', 1),
                    "max_hp": getattr(enemy, 'max_hp', 0),
                    "current_hp": getattr(enemy, 'current_hp', 0),
                    "physical_attack": getattr(enemy, 'physical_attack', 0),
                    "physical_defense": getattr(enemy, 'physical_defense', 0),
                    "speed": getattr(enemy, 'speed', 0),
                    "brave_points": getattr(enemy, 'brave_points', 0)
                }
                self.current_battle["enemy_info"].append(enemy_info)
        
        self.turn_counter = 0
        print(f"🎯 전투 로그 시작: {self.current_battle['battle_id']}")
    
    def log_damage(self, attacker, target, damage_type: str, damage: int, 
                   skill_name: str = None, calculation_details: Dict = None):
        """데미지 로그 기록"""
        if not self.current_battle:
            return
            
        damage_log = {
            "turn": self.turn_counter,
            "timestamp": datetime.datetime.now().isoformat(),
            "attacker": {
                "name": getattr(attacker, 'name', 'Unknown'),
                "class": getattr(attacker, 'character_class', None),
                "level": getattr(attacker, 'level', 1),
                "current_hp": getattr(attacker, 'current_hp', 0),
                "brave_points": getattr(attacker, 'brave_points', 0),
                "physical_attack": getattr(attacker, 'physical_attack', 0),
                "magic_attack": getattr(attacker, 'magic_attack', 0)
            },
            "target": {
                "name": getattr(target, 'name', 'Unknown'),
                "class": getattr(target, 'character_class', None),
                "level": getattr(target, 'level', 1),
                "hp_before": getattr(target, 'current_hp', 0),
                "hp_after": getattr(target, 'current_hp', 0) - damage,
                "brave_before": getattr(target, 'brave_points', 0),
                "physical_defense": getattr(target, 'physical_defense', 0),
                "magic_defense": getattr(target, 'magic_defense', 0)
            },
            "damage_info": {
                "type": damage_type,  # "BRV", "HP", "HEAL"
                "amount": damage,
                "skill_name": skill_name or "기본 공격",
                "calculation": calculation_details or {}
            }
        }
        
        # 데미지 합계 업데이트
        if damage_type == "BRV":
            self.current_battle["damage_summary"]["total_brv_damage"] += damage
        elif damage_type == "HP":
            self.current_battle["damage_summary"]["total_hp_damage"] += damage
            
        if hasattr(attacker, 'character_class'):  # 플레이어
            self.current_battle["damage_summary"]["total_player_damage"] += damage
        else:  # 적
            self.current_battle["damage_summary"]["total_enemy_damage"] += damage
        
        self.current_battle["turns"].append(damage_log)
        
        # 실시간 콘솔 출력
        attacker_name = getattr(attacker, 'name', 'Unknown')
        target_name = getattr(target, 'name', 'Unknown')
        skill_info = f" ({skill_name})" if skill_name else ""
        
        print(f"📊 {attacker_name} → {target_name}: {damage_type} {damage}{skill_info}")
        if calculation_details:
            print(f"   계산: {calculation_details}")
    
    def log_turn_start(self, character):
        """턴 시작 로그"""
        self.turn_counter += 1
        char_name = getattr(character, 'name', 'Unknown')
        char_hp = getattr(character, 'current_hp', 0)
        char_brv = getattr(character, 'brave_points', 0)
        
        turn_log = {
            "turn": self.turn_counter,
            "event": "turn_start",
            "character": char_name,
            "hp": char_hp,
            "brv": char_brv,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if self.current_battle:
            self.current_battle["turns"].append(turn_log)
        
        print(f"🎮 턴 {self.turn_counter}: {char_name} (HP:{char_hp}, BRV:{char_brv})")
    
    def log_skill_use(self, caster, skill_name: str, targets: List, skill_details: Dict = None):
        """스킬 사용 로그"""
        if not self.current_battle:
            return
            
        skill_log = {
            "turn": self.turn_counter,
            "event": "skill_use",
            "timestamp": datetime.datetime.now().isoformat(),
            "caster": getattr(caster, 'name', 'Unknown'),
            "skill_name": skill_name,
            "targets": [getattr(t, 'name', 'Unknown') for t in targets],
            "skill_details": skill_details or {}
        }
        
        self.current_battle["turns"].append(skill_log)
        
        target_names = ", ".join([getattr(t, 'name', 'Unknown') for t in targets])
        print(f"✨ {getattr(caster, 'name', 'Unknown')}이(가) '{skill_name}' 사용 → {target_names}")
    
    def log_status_effect(self, character, effect_name: str, action: str, duration: int = None):
        """상태이상 로그"""
        if not self.current_battle:
            return
            
        status_log = {
            "turn": self.turn_counter,
            "event": "status_effect",
            "timestamp": datetime.datetime.now().isoformat(),
            "character": getattr(character, 'name', 'Unknown'),
            "effect": effect_name,
            "action": action,  # "applied", "removed", "expired"
            "duration": duration
        }
        
        self.current_battle["turns"].append(status_log)
        
        action_text = {"applied": "적용", "removed": "제거", "expired": "만료"}.get(action, action)
        char_name = getattr(character, 'name', 'Unknown')
        print(f"💫 {char_name}: {effect_name} {action_text}")
    
    def log_character_death(self, character):
        """캐릭터 사망 로그"""
        if not self.current_battle:
            return
            
        death_log = {
            "turn": self.turn_counter,
            "event": "character_death",
            "timestamp": datetime.datetime.now().isoformat(),
            "character": getattr(character, 'name', 'Unknown'),
            "final_hp": getattr(character, 'current_hp', 0)
        }
        
        self.current_battle["turns"].append(death_log)
        
        char_name = getattr(character, 'name', 'Unknown')
        print(f"💀 {char_name} 사망")
    
    def end_battle(self, winner: str, battle_result: Dict = None):
        """전투 종료 로그"""
        if not self.current_battle:
            return
            
        self.current_battle["end_time"] = datetime.datetime.now().isoformat()
        self.current_battle["winner"] = winner
        self.current_battle["total_turns"] = self.turn_counter
        
        if battle_result:
            self.current_battle["result"] = battle_result
        
        # 파일에 저장
        self.save_battle_log()
        
        print(f"🏆 전투 종료: {winner} 승리 (총 {self.turn_counter}턴)")
        print(f"💥 총 데미지: 플레이어 {self.current_battle['damage_summary']['total_player_damage']}, 적 {self.current_battle['damage_summary']['total_enemy_damage']}")
    
    def save_battle_log(self):
        """전투 로그를 파일에 저장"""
        if not self.current_battle:
            return
            
        # 기존 로그 불러오기
        all_logs = []
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    all_logs = json.load(f)
            except:
                all_logs = []
        
        # 현재 전투 로그 추가
        all_logs.append(self.current_battle)
        
        # 최근 50개 전투만 보관
        if len(all_logs) > 50:
            all_logs = all_logs[-50:]
        
        # 파일에 저장
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(all_logs, f, ensure_ascii=False, indent=2)
            print(f"📝 전투 로그 저장 완료: {self.log_file}")
        except Exception as e:
            print(f"❌ 로그 저장 실패: {e}")
    
    def get_damage_calculation_details(self, attacker, target, damage_type: str, 
                                     base_damage: int, final_damage: int, 
                                     multipliers: Dict = None) -> Dict:
        """데미지 계산 세부사항 생성"""
        details = {
            "base_damage": base_damage,
            "final_damage": final_damage,
            "attacker_stats": {
                "physical_attack": getattr(attacker, 'physical_attack', 0),
                "magic_attack": getattr(attacker, 'magic_attack', 0),
                "brave_points": getattr(attacker, 'brave_points', 0)
            },
            "target_stats": {
                "physical_defense": getattr(target, 'physical_defense', 0),
                "magic_defense": getattr(target, 'magic_defense', 0),
                "is_broken": getattr(target, 'is_broken_state', False)
            },
            "multipliers": multipliers or {},
            "damage_type": damage_type
        }
        
        return details

# 전역 로거 인스턴스
combat_logger = CombatLogger()
