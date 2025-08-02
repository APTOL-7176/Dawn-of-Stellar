"""
전투 로깅 시스템 - 모든 데미지 계산과 중요한 전투 이벤트를 기록
"""

import datetime
import json
import os
from typing import Dict, List, Any, Optional
from game.balance import GameBalance


class CombatLogger:
    """전투 로그 기록 시스템"""
    
    def __init__(self, log_dir: str = "combat_logs"):
        self.log_dir = log_dir
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"combat_log_{self.session_id}.txt")
        self.json_file = os.path.join(log_dir, f"combat_data_{self.session_id}.json")
        
        # 로그 데이터 저장용
        self.combat_data = {
            "session_info": {
                "start_time": datetime.datetime.now().isoformat(),
                "session_id": self.session_id
            },
            "battles": [],
            "damage_stats": {
                "total_player_damage": 0,
                "total_enemy_damage": 0,
                "total_healing": 0,
                "damage_breakdown": {}
            }
        }
        
        # 디렉토리 생성
        os.makedirs(log_dir, exist_ok=True)
        
        # 로그 파일 초기화
        self._write_log("=" * 80)
        self._write_log(f"🎮 전투 로그 세션 시작: {self.session_id}")
        self._write_log("=" * 80)
    
    def _write_log(self, message: str):
        """로그 파일에 메시지 기록 (콘솔 출력 제거)"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def start_battle(self, party: List, enemies: List):
        """전투 시작 로그"""
        battle_info = {
            "battle_id": len(self.combat_data["battles"]) + 1,
            "start_time": datetime.datetime.now().isoformat(),
            "party": [self._get_character_info(char) for char in party],
            "enemies": [self._get_character_info(char) for char in enemies],
            "turns": [],
            "damage_log": []
        }
        
        self.combat_data["battles"].append(battle_info)
        
        self._write_log("\n" + "🏟️  전투 시작!" + "🏟️ ")
        self._write_log("📋 파티 구성:")
        for i, char in enumerate(party, 1):
            info = self._get_character_info(char)
            self._write_log(f"  {i}. {info['name']} (Lv.{info['level']}) - "
                          f"HP:{info['hp']}/{info['max_hp']} BRV:{info['brv']}/{info['max_brv']}")
            self._write_log(f"     공격:{info['attack']} 방어:{info['defense']} "
                          f"마공:{info['magic_attack']} 마방:{info['magic_defense']} 속도:{info['speed']}")
        
        self._write_log("\n👹 적 구성:")
        for i, enemy in enumerate(enemies, 1):
            info = self._get_character_info(enemy)
            self._write_log(f"  {i}. {info['name']} (Lv.{info['level']}) - "
                          f"HP:{info['hp']}/{info['max_hp']} BRV:{info['brv']}/{info['max_brv']}")
            self._write_log(f"     공격:{info['attack']} 방어:{info['defense']} "
                          f"마공:{info['magic_attack']} 마방:{info['magic_defense']} 속도:{info['speed']}")
        
        self._write_log("-" * 60)
    
    def log_turn_start(self, character, turn_number: int):
        """턴 시작 로그"""
        current_battle = self.combat_data["battles"][-1]
        turn_info = {
            "turn_number": turn_number,
            "character": self._get_character_info(character),
            "actions": []
        }
        current_battle["turns"].append(turn_info)
        
        self._write_log(f"\n🎯 턴 {turn_number}: {character.name}의 차례")
        self._write_log(f"   현재 상태: HP {character.current_hp}/{character.max_hp}, "
                       f"BRV {character.brave_points}/{character.max_brv}")
    
    def log_damage_calculation(self, damage_type: str, attacker, target, 
                             base_damage: int, final_damage: int, 
                             calculation_details: Dict):
        """상세한 데미지 계산 로그"""
        
        # 데미지 통계 업데이트
        if hasattr(attacker, 'character_class'):  # 플레이어
            self.combat_data["damage_stats"]["total_player_damage"] += final_damage
        else:  # 적
            self.combat_data["damage_stats"]["total_enemy_damage"] += final_damage
        
        # 상세 로그 기록
        self._write_log(f"\n💥 {damage_type} 데미지 계산:")
        self._write_log(f"   공격자: {attacker.name} → 대상: {target.name}")
        self._write_log(f"   기본 데미지: {base_damage:,}")
        
        # 계산 과정 상세 기록
        for step, value in calculation_details.items():
            if isinstance(value, (int, float)):
                self._write_log(f"   {step}: {value:,.2f}")
            else:
                self._write_log(f"   {step}: {value}")
        
        self._write_log(f"   ⚡ 최종 데미지: {final_damage:,}")
        
        # JSON 데이터에도 기록
        current_battle = self.combat_data["battles"][-1]
        current_battle["damage_log"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "damage_type": damage_type,
            "attacker": attacker.name,
            "target": target.name,
            "base_damage": base_damage,
            "final_damage": final_damage,
            "calculation_details": calculation_details
        })
    
    def calculate_brv_damage_with_log(self, skill, caster, target, brv_power):
        """BRV 데미지 계산 (로깅 포함)"""
        calculation_details = {}
        
        # 기본 스탯 정보
        base_attack = getattr(caster, 'physical_attack', 100)
        target_defense = getattr(target, 'physical_defense', 50)
        calculation_details["공격자_물리공격력"] = base_attack
        calculation_details["대상_물리방어력"] = target_defense
        
        # 회피 체크
        if self._check_dodge_with_log(caster, target):
            self._write_log(f"💨 회피! {target.name}이(가) {caster.name}의 공격을 피했습니다!")
            return 0
        
        # 기본 데미지 계산
        base_damage = GameBalance.calculate_brave_damage(base_attack, target_defense)
        calculation_details["기본_BRV_데미지"] = base_damage
        
        # 스킬 배율 적용
        skill_damage = int(base_damage * (brv_power / 100.0))
        calculation_details["스킬_배율"] = f"{brv_power}%"
        calculation_details["스킬_배율_적용후"] = skill_damage
        
        # 추가 배율 적용
        skill_damage = int(skill_damage * 1.5)
        calculation_details["기본_스킬_배율_1.5x"] = skill_damage
        
        # 플레이어/적 구분 배율 제거 (balance.py에서 이미 처리됨)
        # 이전에 잘못된 18.75배 보너스가 여기서 적용되고 있었음
        calculation_details["최종_계산값"] = skill_damage
        
        # 랜덤 변수
        import random
        random_factor = random.uniform(0.9, 1.1)
        final_damage = int(skill_damage * random_factor)
        calculation_details["랜덤_배율"] = f"{random_factor:.3f}"
        calculation_details["랜덤_적용후"] = final_damage
        
        # 제한 적용 (버그 방지용: 최소 1, 최대 999999)
        original_damage = final_damage
        final_damage = max(1, min(999999, final_damage))
        if original_damage != final_damage:
            calculation_details["데미지_제한_적용"] = f"{original_damage} → {final_damage}"
        
        # 로그 기록
        self.log_damage_calculation("BRV", caster, target, base_damage, final_damage, calculation_details)
        
        return final_damage
    
    def calculate_hp_damage_with_log(self, skill, caster, target, hp_power):
        """HP 데미지 계산 (로깅 포함)"""
        calculation_details = {}
        
        # BRV 포인트 기반 계산
        brave_points = getattr(caster, 'brave_points', 500)
        
        # 기본 데미지 계산
        base_damage = int(brave_points * (hp_power / 100.0) * 0.10)
        
        # 플레이어/적 구분 배율
        if hasattr(caster, 'character_class'):  # 플레이어
            base_damage = int(base_damage * 1.0)
        else:  # 적 - HP 공격 배율을 1/3로 추가 감소
            base_damage = int(base_damage * 0.01125)  # 0.03375 × (1/3) = 0.01125
        
        # Break 상태 확인
        if hasattr(target, 'is_broken_state') and target.is_broken_state:
            base_damage = int(base_damage * 1.5)
        
        # 취약점 효과
        if hasattr(target, 'temp_vulnerability') and target.temp_vulnerability > 0:
            vulnerability_multiplier = 1.0 + target.temp_vulnerability
            base_damage = int(base_damage * vulnerability_multiplier)
        
        # 최소 데미지 보장
        final_damage = max(base_damage, 10)
        
        # 간소화된 로그만 기록
        self._write_log(f"⚔️ HP 공격: {caster.name} → {target.name} ({final_damage} 데미지)")
        
        return final_damage
    
    def _check_dodge_with_log(self, attacker, target) -> bool:
        """회피 체크 (로깅 포함)"""
        # 간단한 회피 계산 (실제 게임 로직에 맞게 수정 필요)
        attacker_speed = getattr(attacker, 'speed', 100)
        target_speed = getattr(target, 'speed', 100)
        
        dodge_chance = max(0, min(0.3, (target_speed - attacker_speed) / attacker_speed * 0.2))
        
        import random
        is_dodged = random.random() < dodge_chance
        
        if is_dodged:
            self._write_log(f"💨 회피 성공! {target.name}이(가) {attacker.name}의 공격을 피했습니다!")
            self._write_log(f"   회피 확률: {dodge_chance*100:.1f}% (대상 속도:{target_speed}, 공격자 속도:{attacker_speed})")
        
        return is_dodged
    
    def log_healing(self, healer, target, heal_amount: int, actual_heal: int):
        """치유 로그"""
        self.combat_data["damage_stats"]["total_healing"] += actual_heal
        
        self._write_log(f"💚 치유: {healer.name} → {target.name}")
        self._write_log(f"   치유량: {heal_amount:,} (실제: {actual_heal:,})")
        self._write_log(f"   HP: {target.current_hp - actual_heal} → {target.current_hp}")
    
    def log_status_effect(self, caster, target, effect_name: str, effect_details: Dict):
        """상태효과 로그"""
        self._write_log(f"✨ 상태효과: {caster.name} → {target.name}")
        self._write_log(f"   효과: {effect_name}")
        for key, value in effect_details.items():
            self._write_log(f"   {key}: {value}")
    
    def log_battle_end(self, winner: str, battle_duration: float):
        """전투 종료 로그"""
        current_battle = self.combat_data["battles"][-1]
        current_battle["end_time"] = datetime.datetime.now().isoformat()
        current_battle["winner"] = winner
        current_battle["duration_seconds"] = battle_duration
        
        self._write_log(f"\n🏆 전투 종료! 승자: {winner}")
        self._write_log(f"⏱️  전투 시간: {battle_duration:.1f}초")
        self._write_log("-" * 60)
        
        # JSON 파일 저장
        self._save_json_data()
    
    def _get_character_info(self, character) -> Dict:
        """캐릭터 정보 추출"""
        return {
            "name": getattr(character, 'name', 'Unknown'),
            "level": getattr(character, 'level', 1),
            "hp": getattr(character, 'current_hp', 0),
            "max_hp": getattr(character, 'max_hp', 100),
            "brv": getattr(character, 'brave_points', 0),
            "max_brv": getattr(character, 'max_brv', 1000),
            "attack": getattr(character, 'physical_attack', 100),
            "defense": getattr(character, 'physical_defense', 50),
            "magic_attack": getattr(character, 'magic_attack', 100),
            "magic_defense": getattr(character, 'magic_defense', 50),
            "speed": getattr(character, 'speed', 100),
            "character_class": getattr(character, 'character_class', 'Enemy')
        }
    
    def _save_json_data(self):
        """JSON 데이터 저장"""
        try:
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(self.combat_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._write_log(f"❌ JSON 저장 실패: {e}")
    
    def get_session_summary(self) -> Dict:
        """세션 요약 정보 반환"""
        total_battles = len(self.combat_data["battles"])
        stats = self.combat_data["damage_stats"]
        
        return {
            "session_id": self.session_id,
            "total_battles": total_battles,
            "total_player_damage": stats["total_player_damage"],
            "total_enemy_damage": stats["total_enemy_damage"],
            "total_healing": stats["total_healing"],
            "log_file": self.log_file,
            "json_file": self.json_file
        }
