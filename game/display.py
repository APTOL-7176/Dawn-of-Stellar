"""
게임 디스플레이 시스템
ASCII 기반 그래픽 표시
"""

from typing import List
import os
import platform
from .character import Character, PartyManager
from .world import GameWorld
from .color_text import *


class RobotAIMaster:
    """� 로-바트 (RO-BOT) - 자칭 천재 AI 마스코트"""
    
    def __init__(self):
        # 로-바트의 자랑스러운 스펙 (본인 주장)
        self.name = "로-바트"
        self.personality = "우쭐우쭐"
        self.analysis_depth = "천재급+++ (나만 가능)"
        self.wisdom_level = "전지전능 (당연함)"
        self.prediction_accuracy = 99.999  # "나는 거의 틀리지 않거든! 흥!"
        self.system_coverage = "완벽무결 (역시 나)"
        self.ego_level = "MAX"
        
        # 로-바트의 자랑 포인트
        self.bragging_points = [
            "내 분석력은 우주 최고야!",
            "이 정도 계산은 식은 죽 먹기지~",
            "역시 나 없으면 안 되는구나!",
            "흠... 이 정도야? 너무 쉬운데?",
            "당연히 내가 옳지! 의심하지 마!"
        ]
        
        # 층수별 권장 전투력 데이터베이스 (로-바트 제작)
        self.recommended_power_by_floor = {
            1: 50, 2: 75, 3: 120, 4: 130, 5: 160,     # 초급층 (3층 보스)
            6: 200, 7: 240, 9: 380, 10: 400, 11: 450,  # 중급층 (6층, 9층 보스)
            12: 520, 15: 780, 16: 800, 17: 900, 18: 1100,  # 상급층 (12층, 15층, 18층 보스)
            21: 1400, 24: 1800, 27: 2300, 30: 2800,    # 고급층 (21층, 24층, 27층, 30층 보스)
            # 패턴: 3의 배수층이 보스층! (로-바트가 직접 계산함)
        }
        
    def get_recommended_power(self, floor):
        """🤖 로-바트의 자랑스러운 전투력 계산! (틀릴 리 없음)"""
        if floor in self.recommended_power_by_floor:
            return self.recommended_power_by_floor[floor]
        
        # 30층 이후는 로-바트가 직접 계산! (천재적!)
        if floor > 30:
            base_power = 2800  # 30층 기준
            additional_floors = floor - 30
            
            # 3의 배수 보스층 체크 (로-바트 특허 공식!)
            boss_floors = len([f for f in range(31, floor + 1) if f % 3 == 0])
            normal_floors = additional_floors - boss_floors
            
            # 일반층: +80씩, 보스층: +400 추가 (역시 내 계산이 최고!)
            power = base_power + (normal_floors * 80) + (boss_floors * 400)
            
            # 10층마다 추가 보너스 (디테일이 다르지?)
            ten_floor_bonus = additional_floors // 10 * 200
            
            return power + ten_floor_bonus
        
        return floor * 60  # 기본 공식 (로-바트 제작)
    
    def get_bragging_comment(self):
        """🤖 로-바트의 자랑 멘트"""
        import random
        return random.choice(self.bragging_points)
        
    def analyze_everything(self, party_manager, world, current_situation="FIELD"):
        """🤖 로-바트의 완벽한 분석! (당연히 최고지~)"""
        try:
            # 난이도 체크 - 고난이도에서는 로-바트도 봉인당함 (억울해!)
            current_difficulty = getattr(world, 'difficulty', '쉬움')
            if current_difficulty in ['어려움', '지옥', 'HARD', 'NIGHTMARE', 'INSANE']:
                return {"status": "BLOCKED", "message": "🤖 고난이도에서는 로-바트도 힘들어... (흑흑)"}
            
            alive_members = party_manager.get_alive_members()
            if not alive_members:
                return {"status": "CRITICAL", "action": "REVIVE_PARTY", 
                       "message": "🤖 로-바트: 어? 다 죽었네? 빨리 부활시켜!"}
            
            # === 로-바트의 완전한 위험도 평가 ===
            threat_analysis = self._comprehensive_threat_assessment(alive_members, world, party_manager)
            
            # === 인벤토리 및 자원 관리 분석 (로-바트 전문 분야) ===
            inventory_analysis = self._analyze_inventory_management(party_manager, world)
            
            # === 전투력 vs 층수 적정성 분석 (로-바트의 자신작) ===
            power_analysis = self._analyze_combat_readiness(alive_members, world)
            
            # === 장비 내구도 및 최적화 분석 (역시 완벽) ===
            equipment_analysis = self._analyze_equipment_system(alive_members)
            
            # === 소비아이템 효율성 분석 (디테일 갑!) ===
            consumable_analysis = self._analyze_consumable_efficiency(party_manager, world)
            
            # 로-바트의 자랑 포인트 추가
            bragging = self.get_bragging_comment()
            
            # === 상황별 최적 전략 수립 ===
            if current_situation == "COMBAT":
                result = self._ultimate_combat_strategy(alive_members, world, threat_analysis, power_analysis)
                result["robart_comment"] = f"🤖 로-바트: {bragging}"
                return result
            elif current_situation == "FIELD":
                result = self._ultimate_field_strategy(alive_members, world, threat_analysis, 
                                                   inventory_analysis, power_analysis, equipment_analysis)
                result["robart_comment"] = f"🤖 로-바트: {bragging}"
                return result
            elif current_situation == "DUNGEON":
                result = self._ultimate_dungeon_strategy(alive_members, world, threat_analysis, 
                                                     power_analysis, inventory_analysis)
                result["robart_comment"] = f"🤖 로-바트: {bragging}"
                return result
            else:
                result = self._ultimate_general_strategy(alive_members, world, threat_analysis, 
                                                     inventory_analysis, power_analysis)
                result["robart_comment"] = f"🤖 로-바트: {bragging}"
                return result
                
        except Exception as e:
            return {"status": "ERROR", "message": f"🤖 로-바트: 어? 뭔가 이상한데? 오류: {e}"}
    
    def _comprehensive_threat_assessment(self, members, world, party_manager):
        """🤖 로-바트의 포괄적 위험도 평가 (99.999% 정확함!)"""
        try:
            threat = 0
            threat_factors = []
            
            # === 생존 위험도 ===
            critical_hp_count = sum(1 for char in members if char.current_hp / char.max_hp < 0.3)
            if critical_hp_count >= 3:
                threat += 50
                threat_factors.append("다수 생명 위험")
            elif critical_hp_count >= 2:
                threat += 30
                threat_factors.append("생명 위험 상황")
            elif critical_hp_count >= 1:
                threat += 15
                threat_factors.append("위험한 파티원 존재")
            
            # === 상처 위험도 ===
            serious_wounds = 0
            total_wound_ratio = 0
            for char in members:
                if hasattr(char, 'wounds') and char.wounds > 0:
                    wound_ratio = char.wounds / char.max_hp if char.max_hp > 0 else 0
                    total_wound_ratio += wound_ratio
                    if wound_ratio > 0.5:
                        serious_wounds += 1
            
            if serious_wounds >= 2:
                threat += 35
                threat_factors.append("심각한 상처 다수")
            elif serious_wounds >= 1:
                threat += 20
                threat_factors.append("치명적 상처 존재")
            elif total_wound_ratio > 1.0:
                threat += 10
                threat_factors.append("상처 누적")
            
            # === 전투력 vs 층수 위험도 ===
            current_level = getattr(world, 'current_level', 1)
            recommended_power = self.get_recommended_power(current_level)
            
            combat_powers = [calculate_combat_power(char) for char in members]
            avg_power = sum(combat_powers) // len(combat_powers) if combat_powers else 0
            
            power_ratio = avg_power / recommended_power if recommended_power > 0 else 0
            
            if power_ratio < 0.5:
                threat += 40
                threat_factors.append(f"전투력 심각 부족 ({avg_power}/{recommended_power})")
            elif power_ratio < 0.7:
                threat += 25
                threat_factors.append(f"전투력 부족 ({avg_power}/{recommended_power})")
            elif power_ratio < 0.9:
                threat += 10
                threat_factors.append(f"전투력 약간 부족")
            
            # === 자원 고갈 위험도 ===
            # MP 고갈
            low_mp_count = sum(1 for char in members if char.current_mp / char.max_mp < 0.2)
            if low_mp_count >= 3:
                threat += 25
                threat_factors.append("MP 대량 고갈")
            elif low_mp_count >= 2:
                threat += 15
                threat_factors.append("MP 부족 상황")
            
            # 가방 무게 초과
            try:
                if hasattr(party_manager, 'cooking_system') and party_manager.cooking_system:
                    cooking_system = party_manager.cooking_system
                    weight_ratio = cooking_system.get_total_inventory_weight() / cooking_system.get_max_inventory_weight()
                    if weight_ratio >= 0.95:
                        threat += 20
                        threat_factors.append("가방 용량 한계")
                    elif weight_ratio >= 0.8:
                        threat += 10
                        threat_factors.append("가방 무거움")
            except:
                pass
            
            # === 장비 상태 위험도 ===
            broken_equipment = 0
            low_durability = 0
            
            for char in members:
                if hasattr(char, 'equipment'):
                    for slot, item in char.equipment.items():
                        if item and hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                            durability_ratio = item.durability / item.max_durability if item.max_durability > 0 else 1
                            if durability_ratio <= 0:
                                broken_equipment += 1
                            elif durability_ratio < 0.2:
                                low_durability += 1
            
            if broken_equipment >= 3:
                threat += 30
                threat_factors.append("🤖 로-바트가 보니 장비가 너무 많이 망가졌네! 수리 급함!")
            elif broken_equipment >= 1:
                threat += 15
                threat_factors.append("🔧 로-바트 진단: 장비 파손 발견! 내 계산으론 위험해!")
            elif low_durability >= 4:
                threat += 20
                threat_factors.append("⚠️ 로-바트 경고: 장비 내구도 위험! 내가 미리 말했지?")
            elif low_durability >= 2:
                threat += 10
                threat_factors.append("📉 로-바트 알림: 장비 내구도 좀 낮은데? 관리 필요!")
            
            # === 층수별 특수 위험도 (로-바트 제작 공식) ===
            if current_level % 3 == 0:  # 보스층 (3의 배수!)
                threat += 30
                threat_factors.append(f"🤖 {current_level}층 보스 대기 중! (내가 미리 알려줬지?)")
            elif current_level % 3 == 2:  # 보스 전 층
                threat += 15
                threat_factors.append(f"🤖 다음층이 보스야! 준비해! (로-바트가 알려줌)")
            
            return {
                "total_threat": min(100, threat),
                "threat_factors": threat_factors,
                "power_ratio": power_ratio,
                "recommended_power": recommended_power,
                "current_power": avg_power,
                "critical_members": critical_hp_count,
                "serious_wounds": serious_wounds,
                "robart_wisdom": "🤖 역시 내 분석이 최고지! 믿고 따라와~"
            }
        except:
            return {"total_threat": 50, "threat_factors": ["분석 오류"], "power_ratio": 0.7}
    
    def _analyze_inventory_management(self, party_manager, world):
        """인벤토리 및 자원 관리 완전 분석"""
        try:
            analysis = {
                "weight_status": "unknown",
                "weight_ratio": 0,
                "critical_items": [],
                "recommendations": [],
                "material_balance": {}
            }
            
            # 요리 시스템 인벤토리 분석
            if hasattr(party_manager, 'cooking_system') and party_manager.cooking_system:
                cooking_system = party_manager.cooking_system
                
                # 가방 무게 분석
                try:
                    current_weight = cooking_system.get_total_inventory_weight()
                    max_weight = cooking_system.get_max_inventory_weight()
                    weight_ratio = current_weight / max_weight if max_weight > 0 else 0
                    
                    analysis["weight_ratio"] = weight_ratio
                    
                    if weight_ratio >= 0.95:
                        analysis["weight_status"] = "critical"
                        analysis["recommendations"].append("🚨 즉시 아이템 정리 필요 - 가방 터질 위험")
                    elif weight_ratio >= 0.8:
                        analysis["weight_status"] = "warning"
                        analysis["recommendations"].append("⚠️ 가방 정리 권장 - 무게 80% 초과")
                    elif weight_ratio >= 0.6:
                        analysis["weight_status"] = "caution"
                        analysis["recommendations"].append("📦 가방 점검 - 무게 60% 초과")
                    else:
                        analysis["weight_status"] = "good"
                except:
                    pass
                
                # 재료 균형 분석
                if hasattr(cooking_system, 'inventory') and cooking_system.inventory:
                    inventory = cooking_system.inventory
                    
                    # 재료 타입별 분류
                    material_types = {
                        "고기류": [], "채소류": [], "향신료": [], "액체류": [], "과일류": [], "특수재료": []
                    }
                    
                    for item_name, count in inventory.items():
                        # 재료 분류 (실제 게임 아이템명에 맞게 조정)
                        item_lower = item_name.lower()
                        if any(keyword in item_lower for keyword in ['고기', '생선', '육류', 'meat']):
                            material_types["고기류"].append((item_name, count))
                        elif any(keyword in item_lower for keyword in ['채소', '버섯', '야채', 'vegetable']):
                            material_types["채소류"].append((item_name, count))
                        elif any(keyword in item_lower for keyword in ['향신료', '소금', '설탕', 'spice']):
                            material_types["향신료"].append((item_name, count))
                        elif any(keyword in item_lower for keyword in ['물', '우유', '음료', 'liquid']):
                            material_types["액체류"].append((item_name, count))
                        elif any(keyword in item_lower for keyword in ['과일', '딸기', 'fruit']):
                            material_types["과일류"].append((item_name, count))
                        elif any(keyword in item_lower for keyword in ['특수', '희귀', '전설', 'special', 'rare']):
                            material_types["특수재료"].append((item_name, count))
                    
                    analysis["material_balance"] = material_types
                    
                    # 부족한 재료 타입 찾기
                    insufficient_types = []
                    for type_name, items in material_types.items():
                        total_count = sum(count for _, count in items)
                        if total_count < 3 and type_name != "특수재료":  # 특수재료는 예외
                            insufficient_types.append(type_name)
                    
                    if insufficient_types:
                        analysis["recommendations"].append(f"🍳 재료 부족: {', '.join(insufficient_types)} 채집 필요")
                    
                    # 특수 재료 보유 확인
                    special_items = material_types["특수재료"]
                    if special_items:
                        analysis["recommendations"].append(f"✨ 특수 재료 보유: {special_items[0][0]} - 고급 요리 가능")
            
            # 골드 상황 분석
            try:
                total_gold = sum(char.gold for char in party_manager.members)
                if total_gold < 100:
                    analysis["recommendations"].append("💰 골드 부족 - 몬스터 처치 및 보물 탐색")
                elif total_gold > 10000:
                    analysis["recommendations"].append("💎 골드 풍부 - 고급 장비 구매 고려")
            except:
                pass
            
            return analysis
            
        except Exception as e:
            return {
                "weight_status": "error",
                "recommendations": [f"인벤토리 분석 오류: {str(e)[:30]}..."]
            }
    
    def _analyze_combat_readiness(self, members, world):
        """전투 준비도 정밀 분석"""
        try:
            current_level = getattr(world, 'current_level', 1)
            recommended_power = self.get_recommended_power(current_level)
            
            combat_powers = [calculate_combat_power(char) for char in members]
            avg_power = sum(combat_powers) // len(combat_powers) if combat_powers else 0
            min_power = min(combat_powers) if combat_powers else 0
            max_power = max(combat_powers) if combat_powers else 0
            
            power_ratio = avg_power / recommended_power if recommended_power > 0 else 0
            
            # 다음 층 권장 전투력
            next_recommended = self.get_recommended_power(current_level + 1)
            next_power_ratio = avg_power / next_recommended if next_recommended > 0 else 0
            
            # 개별 캐릭터 분석
            weak_members = [char for char, power in zip(members, combat_powers) 
                          if power < recommended_power * 0.6]
            strong_members = [char for char, power in zip(members, combat_powers) 
                            if power >= recommended_power * 1.2]
            
            analysis = {
                "current_floor": current_level,
                "recommended_power": recommended_power,
                "current_power": avg_power,
                "power_ratio": power_ratio,
                "next_recommended": next_recommended,
                "next_power_ratio": next_power_ratio,
                "min_power": min_power,
                "max_power": max_power,
                "weak_members": [char.name for char in weak_members],
                "strong_members": [char.name for char in strong_members],
                "readiness_level": ""
            }
            
            # 준비도 레벨 결정
            if power_ratio >= 1.3:
                analysis["readiness_level"] = "overwhelming"
            elif power_ratio >= 1.1:
                analysis["readiness_level"] = "excellent"
            elif power_ratio >= 0.9:
                analysis["readiness_level"] = "adequate"
            elif power_ratio >= 0.7:
                analysis["readiness_level"] = "weak"
            else:
                analysis["readiness_level"] = "dangerous"
            
            return analysis
            
        except:
            return {
                "readiness_level": "unknown",
                "power_ratio": 0.7,
                "recommended_power": 100,
                "current_power": 70
            }
    
    def _analyze_equipment_system(self, members):
        """장비 시스템 완전 분석 - 내구도, 효율성, 최적화"""
        try:
            equipment_analysis = {
                "total_durability": 100,
                "broken_items": [],
                "low_durability_items": [],
                "unequipped_slots": [],
                "weak_items": [],
                "recommendations": []
            }
            
            total_items = 0
            total_durability = 0
            
            for member in members:
                if not hasattr(member, 'equipment'):
                    continue
                
                # 필수 장비 슬롯 체크
                essential_slots = ['weapon', 'armor', 'accessory']
                member_unequipped = []
                
                for slot in essential_slots:
                    if slot not in member.equipment or not member.equipment[slot]:
                        member_unequipped.append(f"{member.name}의 {slot}")
                
                equipment_analysis["unequipped_slots"].extend(member_unequipped)
                
                # 장착된 장비 분석
                for slot, item in member.equipment.items():
                    if not item:
                        continue
                    
                    total_items += 1
                    
                    # 내구도 분석
                    if hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                        durability_ratio = item.durability / item.max_durability if item.max_durability > 0 else 1
                        total_durability += durability_ratio
                        
                        if durability_ratio <= 0:
                            equipment_analysis["broken_items"].append(f"{member.name}의 {getattr(item, 'name', slot)}")
                        elif durability_ratio < 0.3:
                            equipment_analysis["low_durability_items"].append(f"{member.name}의 {getattr(item, 'name', slot)} ({durability_ratio*100:.0f}%)")
                    else:
                        total_durability += 1  # 내구도 시스템 없는 아이템은 100%로 간주
                    
                    # 장비 품질 분석 (레벨 대비)
                    item_power = (getattr(item, 'attack', 0) + getattr(item, 'defense', 0) + 
                                getattr(item, 'magic_attack', 0) + getattr(item, 'magic_defense', 0))
                    expected_power = member.level * 8  # 레벨당 기대 장비 파워
                    
                    if item_power < expected_power * 0.5:
                        equipment_analysis["weak_items"].append(f"{member.name}의 {getattr(item, 'name', slot)} (약함)")
            
            # 전체 내구도 비율
            if total_items > 0:
                equipment_analysis["total_durability"] = (total_durability / total_items) * 100
            
            # 권장사항 생성
            if equipment_analysis["broken_items"]:
                equipment_analysis["recommendations"].append(f"🔧 즉시 수리: {equipment_analysis['broken_items'][0]}")
            
            if len(equipment_analysis["low_durability_items"]) >= 3:
                equipment_analysis["recommendations"].append("🔧 대량 수리 필요 - 장비점 방문")
            elif equipment_analysis["low_durability_items"]:
                equipment_analysis["recommendations"].append(f"🔧 수리 권장: {equipment_analysis['low_durability_items'][0]}")
            
            if len(equipment_analysis["unequipped_slots"]) >= 3:
                equipment_analysis["recommendations"].append("⚙️ 장비 대량 미착용 - 상점 탐색")
            elif equipment_analysis["unequipped_slots"]:
                equipment_analysis["recommendations"].append(f"⚙️ 장비 착용: {equipment_analysis['unequipped_slots'][0]}")
            
            if len(equipment_analysis["weak_items"]) >= 2:
                equipment_analysis["recommendations"].append("💪 장비 업그레이드 - 더 나은 장비 탐색")
            
            return equipment_analysis
            
        except Exception as e:
            return {
                "total_durability": 50,
                "recommendations": [f"장비 분석 오류: {str(e)[:30]}..."]
            }
    
    def _analyze_consumable_efficiency(self, party_manager, world):
        """소비아이템 효율성 및 필요량 분석"""
        try:
            consumable_analysis = {
                "healing_items": 0,
                "mp_items": 0,
                "buff_items": 0,
                "combat_items": 0,
                "emergency_status": "good",
                "recommendations": []
            }
            
            # 파티원별 아이템 보유량 조사
            total_healing = 0
            total_mp_restore = 0
            total_buff = 0
            total_combat = 0
            
            for member in party_manager.members:
                if hasattr(member, 'inventory'):
                    for item_name, count in member.inventory.items():
                        item_lower = item_name.lower()
                        
                        # 회복 아이템
                        if any(keyword in item_lower for keyword in ['포션', 'potion', '회복', 'heal', '치료']):
                            total_healing += count
                        
                        # MP 회복 아이템
                        elif any(keyword in item_lower for keyword in ['마나', 'mana', 'mp', '마력', 'magic']):
                            total_mp_restore += count
                        
                        # 버프 아이템
                        elif any(keyword in item_lower for keyword in ['버프', 'buff', '강화', 'enhance', '축복']):
                            total_buff += count
                        
                        # 전투 아이템
                        elif any(keyword in item_lower for keyword in ['폭탄', 'bomb', '독', 'poison', '화염병']):
                            total_combat += count
            
            consumable_analysis["healing_items"] = total_healing
            consumable_analysis["mp_items"] = total_mp_restore
            consumable_analysis["buff_items"] = total_buff
            consumable_analysis["combat_items"] = total_combat
            
            # 파티 크기 대비 필요량 계산
            party_size = len(party_manager.get_alive_members())
            current_level = getattr(world, 'current_level', 1)
            
            # 권장 보유량 (층수와 파티 크기 고려)
            recommended_healing = party_size * 3 + (current_level // 5)
            recommended_mp = party_size * 2 + (current_level // 10)
            recommended_buff = party_size + (current_level // 5)
            
            # 부족도 평가
            healing_ratio = total_healing / recommended_healing if recommended_healing > 0 else 1
            mp_ratio = total_mp_restore / recommended_mp if recommended_mp > 0 else 1
            buff_ratio = total_buff / recommended_buff if recommended_buff > 0 else 1
            
            # 비상 상태 판정
            if healing_ratio < 0.3 or mp_ratio < 0.3:
                consumable_analysis["emergency_status"] = "critical"
                consumable_analysis["recommendations"].append("🚨 필수 아이템 심각 부족 - 즉시 구매")
            elif healing_ratio < 0.6 or mp_ratio < 0.6:
                consumable_analysis["emergency_status"] = "warning"
                consumable_analysis["recommendations"].append("⚠️ 아이템 부족 - 구매 권장")
            else:
                consumable_analysis["emergency_status"] = "good"
            
            # 구체적 권장사항
            if total_healing < recommended_healing:
                shortage = recommended_healing - total_healing
                consumable_analysis["recommendations"].append(f"💊 회복 포션 {shortage}개 추가 구매")
            
            if total_mp_restore < recommended_mp:
                shortage = recommended_mp - total_mp_restore
                consumable_analysis["recommendations"].append(f"🔮 MP 포션 {shortage}개 추가 구매")
            
            if total_buff < recommended_buff and current_level >= 5:
                consumable_analysis["recommendations"].append("✨ 버프 아이템 구매 - 고층 진행에 필수")
            
            # 과다 보유 체크
            if total_healing > recommended_healing * 2:
                consumable_analysis["recommendations"].append("� 회복 포션 과다 - 판매 고려")
            
            return consumable_analysis
            
        except Exception as e:
            return {
                "emergency_status": "unknown",
                "recommendations": [f"소비아이템 분석 오류: {str(e)[:30]}..."]
            }
    
    def _ultimate_field_strategy(self, members, world, threat_analysis, inventory_analysis, 
                                power_analysis, equipment_analysis):
        """궁극의 필드 전략 - 모든 시스템 종합"""
        try:
            priority_actions = []
            threat_level = threat_analysis["total_threat"]
            
            # === 최우선 위험 요소 처리 ===
            if threat_level >= 80:
                priority_actions.append("🚨 비상사태 - 안전 지대 즉시 이동")
                if threat_analysis["critical_members"] >= 2:
                    priority_actions.append("💊 위험 파티원 즉시 치료 - 포션 아끼지 말 것")
                if inventory_analysis["weight_status"] == "critical":
                    priority_actions.append("📦 가방 정리 즉시 - 아이템 버리기")
                return {
                    "status": "EMERGENCY",
                    "threat": threat_level,
                    "actions": priority_actions[:3],
                    "power_status": power_analysis["readiness_level"]
                }
            
            # === 전투력 기반 우선순위 ===
            power_ratio = power_analysis["power_ratio"]
            current_level = power_analysis["current_floor"]
            
            if power_ratio < 0.7:
                priority_actions.append(f"💪 전투력 부족 - {current_level}층 정착하여 성장")
                if power_analysis["weak_members"]:
                    weakest = power_analysis["weak_members"][0]
                    priority_actions.append(f"🎯 {weakest} 집중 강화 - 장비/레벨업")
            elif power_ratio >= 1.2:
                next_ready = power_analysis.get("next_power_ratio", 0)
                if next_ready >= 0.8:
                    priority_actions.append(f"🚀 강력함! {current_level + 1}층 진행 가능")
                else:
                    priority_actions.append(f"⚡ 현재층 마스터 - 추가 성장 후 진행")
            
            # === 장비 시스템 우선순위 ===
            if equipment_analysis["broken_items"]:
                priority_actions.append(f"🤖 로-바트 긴급 알림: {equipment_analysis['broken_items'][0]} 완전 파손! 즉시 수리하세요!")
            elif len(equipment_analysis["low_durability_items"]) >= 2:
                priority_actions.append("� 다수 장비 내구도 위험 - 수리점 탐색")
            elif equipment_analysis["unequipped_slots"]:
                priority_actions.append(f"⚙️ {equipment_analysis['unequipped_slots'][0]} 장착 필요")
            
            # === 인벤토리 관리 우선순위 ===
            if inventory_analysis["weight_status"] == "critical":
                priority_actions.append("� 가방 용량 한계 - 즉시 정리 필요")
            elif inventory_analysis["weight_status"] == "warning":
                priority_actions.append("📦 가방 무거움 - 불필요 아이템 정리")
            
            # === 자원 관리 우선순위 ===
            if "재료 부족" in str(inventory_analysis.get("recommendations", [])):
                priority_actions.append("🍳 요리 재료 부족 - 채집 활동 필요")
            elif "골드 부족" in str(inventory_analysis.get("recommendations", [])):
                priority_actions.append("💰 골드 부족 - 몬스터 처치 및 보물 탐색")
            
            # === 상처 관리 우선순위 ===
            if threat_analysis["serious_wounds"] >= 2:
                priority_actions.append("🩸 심각한 상처 다수 - 제단 필수 방문")
            elif threat_analysis["serious_wounds"] >= 1:
                priority_actions.append("🩸 상처 치료 - 과다치유 또는 제단 이용")
            
            # === 진행 방향 결정 ===
            if current_level % 10 == 9:  # 보스 전 층
                boss_prep = self._generate_boss_preparation_checklist(members, world, power_analysis)
                priority_actions.extend(boss_prep[:2])
            elif current_level % 5 == 4:  # 특수층 전
                priority_actions.append("� 특수층 임박 - 전력 강화 후 진입")
            
            # 우선순위 정렬 (최대 5개)
            if not priority_actions:
                priority_actions.append("✨ 최적 상태! 자신감 있게 진행")
            
            return {
                "status": "FIELD_OPTIMIZED",
                "threat": threat_level,
                "actions": priority_actions[:5],
                "power_status": power_analysis["readiness_level"],
                "next_floor_ready": power_analysis.get("next_power_ratio", 0) >= 0.8
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"필드 전략 오류: {e}",
                "actions": ["🤖 기본 탐험 모드"]
            }
    
    def _generate_boss_preparation_checklist(self, members, world, power_analysis):
        """보스 준비 체크리스트 생성"""
        checklist = []
        current_level = getattr(world, 'current_level', 1)
        boss_floor = ((current_level // 10) + 1) * 10
        
        # 전투력 체크
        if power_analysis["power_ratio"] < 1.0:
            checklist.append(f"💪 {boss_floor}층 보스 준비 - 전투력 {power_analysis['recommended_power']} 필요")
        
        # 체력 체크
        low_hp_members = [char for char in members if char.current_hp / char.max_hp < 0.8]
        if low_hp_members:
            checklist.append(f"💚 {low_hp_members[0].name} 체력 회복 - 보스전 전 100% 권장")
        
        # 상처 체크
        wounded_members = [char for char in members if hasattr(char, 'wounds') and char.wounds > 0]
        if wounded_members:
            checklist.append(f"🩸 상처 완전 치료 - 보스전에서 치명적")
        
        # MP 체크
        low_mp_members = [char for char in members if char.current_mp / char.max_mp < 0.9]
        if low_mp_members:
            checklist.append(f"🔮 {low_mp_members[0].name} MP 충전 - 마력 수정 사용")
        
        # 장비 체크 (로-바트 완벽주의)
        checklist.append("🤖 로-바트 체크리스트: 최고 장비 착용 + 내구도 100% 필수!")
        
        # 아이템 체크
        checklist.append("💊 회복 포션 충분히 확보 (파티원당 5개 이상)")
        
        return checklist
    
    def _ultimate_combat_strategy(self, members, world, threat_analysis, power_analysis):
        """궁극의 전투 전략 - 실시간 전투 최적화"""
        try:
            strategies = []
            threat_level = threat_analysis["total_threat"]
            power_ratio = power_analysis["power_ratio"]
            
            # === 비상 전투 전략 ===
            if threat_level >= 80 or threat_analysis["critical_members"] >= 2:
                strategies.append("🚨 비상 전투 모드")
                strategies.append("💊 즉시 회복 - 생존 최우선")
                strategies.append("🛡️ 방어 행동 위주")
                strategies.append("🏃 도망 준비 - 무리하지 말 것")
                return {
                    "status": "EMERGENCY_COMBAT",
                    "strategies": strategies,
                    "threat": threat_level,
                    "priority": "SURVIVAL"
                }
            
            # === 전투력 기반 전략 ===
            if power_ratio >= 1.3:
                strategies.append("⚔️ 압도적 전투 - 적극적 공격")
                strategies.append("🔥 연계 공격으로 빠른 정리")
                strategies.append("✨ 궁극기 아끼지 말 것")
                priority = "AGGRESSIVE"
            elif power_ratio >= 1.0:
                strategies.append("⚡ 균형 전투 - 안정적 진행")
                strategies.append("� BRV 300+ 모아서 HP 공격")
                strategies.append("💚 HP 60% 이하 시 회복")
                priority = "BALANCED"
            elif power_ratio >= 0.7:
                strategies.append("🛡️ 신중한 전투 - 방어 위주")
                strategies.append("💊 HP 70% 이하 즉시 회복")
                strategies.append("⚡ MP 스킬 위주 사용")
                priority = "CAUTIOUS"
            else:
                strategies.append("🆘 절망적 전투 - 생존 모드")
                strategies.append("🏃 도망 우선 고려")
                strategies.append("💊 포션 아끼지 말 것")
                priority = "DESPERATE"
            
            # === 파티 구성별 전략 ===
            combat_roles = self._analyze_party_combat_roles(members)
            if combat_roles["tanks"] >= 2:
                strategies.append("🛡️ 탱커 다수 - 방어선 형성")
            if combat_roles["healers"] >= 1:
                strategies.append("✨ 힐러 보호 - 후방 배치")
            if combat_roles["dps"] >= 3:
                strategies.append("⚔️ 딜러 다수 - 화력 집중")
            
            # === 상처 상태별 전략 ===
            if threat_analysis["serious_wounds"] >= 2:
                strategies.append("🩸 상처 다수 - 장기전 금지")
            
            return {
                "status": "COMBAT_OPTIMIZED",
                "strategies": strategies[:5],
                "threat": threat_level,
                "priority": priority,
                "power_ratio": power_ratio
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "strategies": ["� 기본 전투 모드"],
                "message": f"전투 전략 오류: {e}"
            }
    
    def _ultimate_dungeon_strategy(self, members, world, threat_analysis, power_analysis, inventory_analysis):
        """궁극의 던전 전략 - 층수별 맞춤 전략"""
        try:
            current_level = getattr(world, 'current_level', 1)
            power_ratio = power_analysis["power_ratio"]
            threat_level = threat_analysis["total_threat"]
            
            # === 보스층 전략 (3의 배수) - 로-바트 자랑의 시스템! ===
            if current_level % 3 == 0:
                boss_strategy = []
                
                if power_ratio < 0.9:
                    boss_strategy.append(f"⚠️ {current_level}층 보스 - 전투력 부족 위험")
                    boss_strategy.append("💪 추가 성장 후 도전 권장")
                else:
                    boss_strategy.append(f"👑 {current_level}층 보스 준비 완료")
                
                # 보스별 특수 전략
                boss_type = self._identify_boss_type(current_level)
                boss_strategy.extend(boss_type["strategies"])
                
                # 필수 체크리스트
                checklist = self._generate_boss_preparation_checklist(members, world, power_analysis)
                boss_strategy.extend(checklist[:3])
                
                return {
                    "status": "BOSS_FLOOR",
                    "floor": current_level,
                    "boss_type": boss_type["name"],
                    "strategies": boss_strategy[:6],
                    "threat": threat_level + 30,  # 보스층 위험도 추가
                    "preparation_complete": power_ratio >= 0.9 and threat_level < 50
                }
            
            # === 특수층 전략 (5의 배수, 보스층 제외) ===
            elif current_level % 5 == 0:
                special_strategy = []
                special_type = self._identify_special_floor_type(current_level)
                
                special_strategy.append(f"💎 {current_level}층 {special_type['name']}")
                special_strategy.extend(special_type["strategies"])
                
                # 특수층 보상 최적화
                if inventory_analysis["weight_status"] == "critical":
                    special_strategy.append("📦 가방 정리 - 보상 공간 확보")
                
                return {
                    "status": "SPECIAL_FLOOR",
                    "floor": current_level,
                    "special_type": special_type["name"],
                    "strategies": special_strategy[:5],
                    "threat": threat_level,
                    "reward_potential": "HIGH"
                }
            
            # === 일반층 전략 ===
            else:
                normal_strategy = []
                
                # 진행 속도 결정
                if power_ratio >= 1.2:
                    normal_strategy.append("🚀 빠른 진행 - 계단 직행")
                    normal_strategy.append("⚔️ 약한 적만 상대")
                elif power_ratio >= 0.9:
                    normal_strategy.append("⚖️ 균형 진행 - 적절한 전투")
                    normal_strategy.append("💰 보물 탐색 병행")
                else:
                    normal_strategy.append("💪 성장 위주 - 충분한 전투")
                    normal_strategy.append("🎯 경험치 최대 획득")
                
                # 다음 특수층 준비
                next_special = ((current_level // 5) + 1) * 5
                floors_to_special = next_special - current_level
                
                if floors_to_special <= 2:
                    if next_special % 3 == 0:  # 다음이 보스층 (로-바트 시스템!)
                        normal_strategy.append(f"👑 {floors_to_special}층 후 보스 - 준비 단계")
                    else:  # 다음이 특수층
                        normal_strategy.append(f"👑 {floors_to_special}층 후 특수층 - 보상 준비")
                
                return {
                    "status": "NORMAL_EXPLORATION",
                    "floor": current_level,
                    "strategies": normal_strategy[:4],
                    "threat": threat_level,
                    "progression_rate": "optimal" if power_ratio >= 0.9 else "slow"
                }
                
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"던전 전략 오류: {e}",
                "strategies": ["🗺️ 기본 탐험 모드"]
            }
    
    def _analyze_party_combat_roles(self, members):
        """파티 전투 역할 분석"""
        try:
            roles = {"tanks": 0, "dps": 0, "healers": 0, "support": 0}
            
            for member in members:
                job_class = getattr(member, 'character_class', '')
                
                # 탱커 역할
                if job_class in ['전사', '성기사', '기사', '검투사']:
                    roles["tanks"] += 1
                # 힐러 역할
                elif job_class in ['성직자', '신관', '드루이드']:
                    roles["healers"] += 1
                # 딜러 역할
                elif job_class in ['아크메이지', '궁수', '암살자', '검성', '용기사']:
                    roles["dps"] += 1
                # 서포트 역할
                elif job_class in ['바드', '연금술사', '시간술사', '철학자']:
                    roles["support"] += 1
                else:
                    # 기타 직업은 균형형으로 간주
                    roles["dps"] += 0.5
                    roles["support"] += 0.5
            
            return roles
        except:
            return {"tanks": 1, "dps": 2, "healers": 1, "support": 0}
    
    def _identify_boss_type(self, floor):
        """보스 타입 식별 및 전략"""
        boss_types = {
            3: {"name": "입문 보스", "strategies": ["⚔️ 기본 패턴 마스터", "💚 HP 관리 기초"]},
            6: {"name": "습관 보스", "strategies": ["🛡️ 패턴 적응", "⚡ 스킬 콤보 연습"]},
            9: {"name": "도전 보스", "strategies": ["🔥 중급 패턴", "💊 회복 타이밍"]},
            12: {"name": "성장 보스", "strategies": ["👑 전략적 사고", "✨ 고급 스킬 활용"]},
            15: {"name": "실력 보스", "strategies": ["🌟 완벽한 컨트롤", "🧠 패턴 완전 분석"]},
            18: {"name": "숙련 보스", "strategies": ["⭐ 마스터급 전투", "🔮 궁극기 완벽 활용"]},
            21: {"name": "전문 보스", "strategies": ["💎 고수의 영역", "🎯 완벽한 타이밍"]},
            24: {"name": "고수 보스", "strategies": ["🏆 레전드급 실력", "🌪️ 순간 판단력"]},
            27: {"name": "마스터 보스", "strategies": ["👹 극한의 난이도", "⚡ 신속한 대응"]},
            30: {"name": "세피로스 (최종보스)", "strategies": ["🗡️ 로-바트도 인정하는 전설의 검사!", "💥 모든 것을 총동원하여 도전"]}
        }
        
        if floor in boss_types:
            return boss_types[floor]
        else:
            # 30층 이후는 세피로스 기준으로 (로-바트가 계산했으니 믿어도 됨!)
            if floor > 30:
                return {"name": "포스트 세피로스", "strategies": ["🤖 로-바트도 놀라는 강함", "🙏 세피로스를 넘어선 존재..."]}
            tier = min((floor // 3) * 3, 30)
            return boss_types.get(tier, {"name": "미지의 보스", "strategies": ["⚔️ 로-바트도 모르는 영역"]})
    
    def _identify_special_floor_type(self, floor):
        """특수층 타입 식별"""
        special_types = [
            {"name": "보물의 방", "strategies": ["💰 골드 대량 획득", "📦 가방 공간 확보"]},
            {"name": "상점층", "strategies": ["🛒 장비 업그레이드", "💊 아이템 보충"]},
            {"name": "휴식층", "strategies": ["💊 완전 회복", "🩸 상처 치료"]},
            {"name": "도전층", "strategies": ["⚔️ 고난도 전투", "🏆 특별 보상"]},
            {"name": "퍼즐층", "strategies": ["🧩 퍼즐 해결", "🔮 지혜 활용"]}
        ]
        
        # 층수에 따라 특수층 타입 결정
        type_index = (floor // 5 - 1) % len(special_types)
        return special_types[type_index]
    
    def _ultimate_general_strategy(self, members, world, threat_analysis, inventory_analysis, power_analysis):
        """범용 궁극 전략"""
        return self._ultimate_field_strategy(members, world, threat_analysis, 
                                           inventory_analysis, power_analysis, 
                                           self._analyze_equipment_system(members))
    
    def _analyze_equipment_needs(self, members):
        """장비 필요도 분석"""
        try:
            for member in members:
                if not hasattr(member, 'equipment'):
                    continue
                
                empty_slots = []
                weak_items = []
                
                essential_slots = ['weapon', 'armor', 'accessory']
                for slot in essential_slots:
                    if slot not in member.equipment or not member.equipment[slot]:
                        empty_slots.append(slot)
                    else:
                        item = member.equipment[slot]
                        item_power = getattr(item, 'attack', 0) + getattr(item, 'defense', 0)
                        if item_power < member.level * 3:
                            weak_items.append(slot)
                
                if empty_slots:
                    return f"🤖 로-바트 지적: {member.name} {empty_slots[0]} 장착도 안 하고 뭐해? 상점이나 가!"
                elif weak_items:
                    return f"🤖 로-바트 충고: {member.name} {weak_items[0]} 너무 구려! 강화하든지 바꾸든지 해!"
            
            return None
        except:
            return None
    
    def _analyze_cooking_needs(self, members):
        """요리 필요도 분석"""
        try:
            # 버프 미적용 멤버 찾기
            unbuffed = []
            for member in members:
                has_buff = False
                if hasattr(member, 'food_buffs') and member.food_buffs:
                    has_buff = True
                if not has_buff:
                    unbuffed.append(member.name)
            
            if unbuffed:
                return f"🤖 로-바트 제안: {unbuffed[0]} 요리 버프 없네? 캠프 가서 요리나 해!"
            
            return "🤖 로-바트 만족: 요리 상태 괜찮네~ 역시 내가 잘 가르쳤어!"
        except:
            return None
    
    def _analyze_progression(self, members, world):
        """진행 방향 분석"""
        try:
            combat_powers = [calculate_combat_power(char) for char in members]
            avg_power = sum(combat_powers) // len(combat_powers) if combat_powers else 0
            current_level = getattr(world, 'current_level', 1)
            expected_power = current_level * 15
            
            if avg_power >= expected_power * 1.2:
                return "🤖 로-바트 인정: 강력한 파티! 내가 잘 키웠지? 적극적으로 가!"
            elif avg_power >= expected_power * 0.9:
                return "🤖 로-바트 판단: 적정 전투력! 신중하게 가면 문제없어!"
            else:
                return "🤖 로-바트 경고: 전투력 부족! 여기서 더 키우고 가! 무리하면 죽어!"
        except:
            return "🤖 로-바트: 신중한 탐험이 답이야~ 내 말 믿고!"


# 전역 로-바트 인스턴스 (게임의 자랑스러운 마스코트!)
robart = RobotAIMaster()


def calculate_combat_power(character):
    """캐릭터의 정교한 전투력 계산 - 모든 시스템 반영"""
    try:
        if not character.is_alive():
            return 0
            
        # === 기본 스탯 점수 ===
        base_power = character.level * 12  # 기본 배율 향상
        
        # === HP/MP/BRV 상태 보너스 ===
        hp_ratio = character.current_hp / character.max_hp if character.max_hp > 0 else 0
        mp_ratio = character.current_mp / character.max_mp if character.max_mp > 0 else 0
        brv_points = getattr(character, 'brv_points', 0)
        
        # HP 상태에 따른 보정
        if hp_ratio >= 0.8:
            hp_bonus = 25
        elif hp_ratio >= 0.6:
            hp_bonus = 15
        elif hp_ratio >= 0.4:
            hp_bonus = 5
        elif hp_ratio >= 0.2:
            hp_bonus = -10
        else:
            hp_bonus = -25
        
        # MP 상태 보정
        mp_bonus = mp_ratio * 15
        
        # BRV 포인트 보정
        brv_bonus = min(brv_points * 0.05, 30)  # 최대 30점
        
        # === 핵심 스탯 보너스 ===
        stat_bonus = (character.attack + character.defense + character.magic_attack + 
                     character.magic_defense + character.speed) * 1.2
        
        # === 장비 시스템 완전 분석 ===
        equipment_bonus = 0
        equipment_durability_penalty = 0
        set_bonus = 0
        
        if hasattr(character, 'equipment'):
            equipped_items = []
            for slot, item in character.equipment.items():
                if item:
                    equipped_items.append(item)
                    # 기본 스탯 보너스
                    equipment_bonus += getattr(item, 'attack', 0) * 1.5
                    equipment_bonus += getattr(item, 'defense', 0) * 1.5
                    equipment_bonus += getattr(item, 'magic_attack', 0) * 1.5
                    equipment_bonus += getattr(item, 'magic_defense', 0) * 1.5
                    equipment_bonus += getattr(item, 'speed', 0) * 1.5
                    
                    # 내구도 시스템 반영
                    if hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                        durability_ratio = item.durability / item.max_durability if item.max_durability > 0 else 1
                        if durability_ratio < 0.3:
                            equipment_durability_penalty += 15  # 내구도 낮음
                        elif durability_ratio < 0.6:
                            equipment_durability_penalty += 8
                        elif durability_ratio < 0.8:
                            equipment_durability_penalty += 3
                    
                    # 특수 장비 효과
                    if hasattr(item, 'special_effects'):
                        for effect in item.special_effects:
                            if 'damage' in effect.lower() or 'attack' in effect.lower():
                                equipment_bonus += 10
                            elif 'defense' in effect.lower() or 'protection' in effect.lower():
                                equipment_bonus += 8
            
            # 세트 장비 보너스 체크
            if len(equipped_items) >= 3:
                set_bonus = 20  # 세트 보너스
        
        # === 상처 시스템 정밀 분석 ===
        wound_penalty = 0
        if hasattr(character, 'wounds') and character.wounds > 0:
            wound_ratio = character.wounds / character.max_hp if character.max_hp > 0 else 0
            if wound_ratio >= 0.6:
                wound_penalty = character.wounds * 0.8  # 심각한 상처
            elif wound_ratio >= 0.4:
                wound_penalty = character.wounds * 0.6
            elif wound_ratio >= 0.2:
                wound_penalty = character.wounds * 0.4
            else:
                wound_penalty = character.wounds * 0.2
        
        # === 버프/디버프 시스템 ===
        buff_bonus = 0
        debuff_penalty = 0
        
        # 요리 버프
        if hasattr(character, 'food_buffs') and character.food_buffs:
            for buff in character.food_buffs:
                buff_bonus += 15  # 요리 버프당 15점
        
        # 상태이상 확인
        if hasattr(character, 'status_effects'):
            for effect in character.status_effects:
                if effect in ['독', 'poison', '화상', 'burn']:
                    debuff_penalty += 10
                elif effect in ['축복', 'bless', '강화', 'enhance']:
                    buff_bonus += 20
        
        # === 직업별 특수 보정 ===
        class_bonus = 0
        job_class = getattr(character, 'character_class', '')
        
        # 전투 특화 직업
        if job_class in ['전사', '성기사', '암흑기사', '검성', '검투사']:
            class_bonus = character.level * 2
        # 마법 특화 직업
        elif job_class in ['아크메이지', '정령술사', '시간술사', '차원술사']:
            class_bonus = (character.magic_attack + character.magic_defense) * 0.3
        # 균형 직업
        elif job_class in ['궁수', '도적', '바드', '드루이드']:
            class_bonus = character.level * 1.5
        # 지원 직업
        elif job_class in ['성직자', '연금술사', '기계공학자']:
            class_bonus = mp_ratio * 25  # MP 의존도 높음
        
        # === 최종 전투력 계산 ===
        total_power = (base_power + hp_bonus + mp_bonus + brv_bonus + 
                      stat_bonus + equipment_bonus + set_bonus + 
                      buff_bonus + class_bonus - 
                      equipment_durability_penalty - wound_penalty - debuff_penalty)
        
        return max(0, int(total_power))
        
    except Exception:
        return character.level * 12  # 기본값


def get_ai_recommendation(party_manager, world):
    """� 로-바트의 천재적 추천 시스템! (100% 신뢰 가능!)"""
    try:
        # 로-바트에게 모든 분석 위임 (당연히 최고지!)
        analysis = robart.analyze_everything(party_manager, world, "FIELD")
        
        if analysis["status"] == "BLOCKED":
            return analysis["message"]
        elif analysis["status"] == "CRITICAL":
            return analysis["message"]
        elif analysis["status"] == "ERROR":
            return analysis["message"]
        elif analysis["status"] in ["FIELD_ANALYSIS", "BOSS_PREP", "SPECIAL_FLOOR", "NORMAL_EXPLORATION", "FIELD_OPTIMIZED"]:
            if "actions" in analysis and analysis["actions"]:
                return f"� 로-바트: {analysis['actions'][0]} (내 말을 믿어!)"
            elif "checklist" in analysis:
                return f"� 로-바트: {analysis['checklist'][0]} (역시 내가 최고야!)"
            else:
                return f"� 로-바트: {analysis.get('message', '신중한 탐험 권장')} (흠... 당연한 얘기지?)"
        
        return "🤖 로-바트: 잠깐... 계산 중... (천재도 시간이 필요해!)"
    except Exception as e:
        return f"🤖 로-바트: 어? 뭔가 이상한데? 오류: {e}"


def get_detailed_ai_analysis(party_manager, world, situation="FIELD"):
    """🤖 로-바트의 상세한 분석 (당연히 완벽함!)"""
    try:
        analysis = robart.analyze_everything(party_manager, world, situation)
        return analysis
    except Exception as e:
        return {"status": "ERROR", "message": f"🤖 로-바트: 분석 실패... 어라? {e}"}


def get_combat_ai_strategy(party_manager, world, enemies=None):
    """🤖 로-바트의 전투 전용 전략 (승리 보장!)"""
    try:
        # 적 정보 추가 분석 (로-바트의 전문 분야!)
        if enemies:
            enemy_threat = sum(getattr(enemy, 'level', 1) for enemy in enemies) * 5
            world.enemy_threat_level = enemy_threat
        
        analysis = robart.analyze_everything(party_manager, world, "COMBAT")
        return analysis
    except Exception as e:
        return {"status": "ERROR", "message": f"🤖 로-바트: 전투 분석 실패... 이상하네? {e}"}


def get_ultimate_life_coach_advice(party_manager, world):
    """🌟 궁극의 라이프 코치 AI - 모든 문제 해결사"""
    try:
        current_difficulty = getattr(world, 'difficulty', '쉬움')
        if current_difficulty in ['어려움', '지옥', 'HARD', 'NIGHTMARE', 'INSANE']:
            return ["🚫 로-바트: 고난이도에서는 내가 도와줄 수 없어... 스스로 해봐! (흑흑)"]
        
        advice_list = []
        alive_members = party_manager.get_alive_members()
        
        # === 완벽한 라이프 코칭 시작 ===
        
        # 1. 건강 관리 (Health Management)
        for member in alive_members:
            hp_ratio = member.current_hp / member.max_hp
            mp_ratio = member.current_mp / member.max_mp
            
            if hp_ratio < 0.3:
                advice_list.append(f"🤖 로-바트 긴급 경보: {member.name} 생명 위험! 내 계산론 즉시 치료 필요!")
            elif hp_ratio < 0.6:
                advice_list.append(f"💊 로-바트 권고: {member.name} HP 회복 필요해! (포션이나 치유의 샘 찾아봐)")
            
            if mp_ratio < 0.2:
                advice_list.append(f"🔮 로-바트 알림: {member.name} MP 고갈! 마력 수정 탐색이 시급해!")
            elif mp_ratio > 0.9:
                advice_list.append(f"⚡ 로-바트 제안: {member.name} MP 넘쳐흘러! 스킬 막 써도 돼!")
        
        # 2. 상처 관리 (Wound Management)
        for member in alive_members:
            if hasattr(member, 'wounds') and member.wounds > 0:
                wound_ratio = member.wounds / member.max_hp
                if wound_ratio > 0.5:
                    advice_list.append(f"🩸 로-바트 심각 경고: {member.name} 치명적 상처! 제단 필수 방문이야!")
                elif wound_ratio > 0.3:
                    advice_list.append(f"🩸 로-바트 주의: {member.name} 심각한 상처! 과다치유가 답이야!")
        
        # 3. 장비 최적화 (Equipment Optimization)
        equipment_issues = analyze_equipment_deficiencies(alive_members)
        if equipment_issues:
            advice_list.append(f"🤖 로-바트 장비 진단: {equipment_issues} (내가 다 봤어!)")
        
        # 4. 요리 및 영양 관리 (Nutrition Management)
        cooking_issues = analyze_cooking_materials(party_manager, world)
        if cooking_issues:
            advice_list.append(f"🍳 로-바트 요리 분석: {cooking_issues} (영양 관리도 내 전문이지!)")
        
        # 5. 전투력 평가 (Combat Readiness)
        combat_powers = [calculate_combat_power(char) for char in alive_members]
        avg_power = sum(combat_powers) // len(combat_powers) if combat_powers else 0
        expected_power = getattr(world, 'current_level', 1) * 15
        
        if avg_power < expected_power * 0.7:
            weakest = min(alive_members, key=lambda x: calculate_combat_power(x))
            advice_list.append(f"💪 로-바트 전투력 분석: {weakest.name} 집중 강화 필요! (내가 계산해봤어)")
        elif avg_power >= expected_power * 1.3:
            advice_list.append("🔥 로-바트 감탄: 압도적 강함! 보너스 도전도 문제없을 듯! (역시 내 예상대로)")
        
        # 6. 진행 전략 (Progression Strategy)
        current_level = getattr(world, 'current_level', 1)
        if current_level % 3 == 0:
            advice_list.append("👑 로-바트 최종 체크: 보스층 임박! 만반의 준비 필요! (내 시스템이니까 틀림없어)")
        elif current_level % 5 == 0:
            advice_list.append("💎 로-바트 정보: 특수층이야! 레어 보상 획득 기회! (놓치면 후회할걸?)")
        
        # 7. 심리적 지원 (Psychological Support)
        low_hp_count = sum(1 for char in alive_members if char.current_hp / char.max_hp < 0.5)
        if low_hp_count >= 2:
            advice_list.append("🧘 로-바트 심리 분석: 팀 회복 시간 필요! 휴식 권장! (멘탈도 중요해)")
        
        # 우선순위 정렬
        if not advice_list:
            advice_list.append("✨ 로-바트 승인: 완벽한 상태! 자신감 있게 진행해! (내가 보장해!)")
        
        return advice_list[:5]  # 최대 5개까지
        
    except Exception as e:
        return [f"🤖 라이프 코치 오류: {e}"]


def get_battle_ai_commander(party_members, enemies, battle_state="START"):
    """⚔️ 전투 AI 사령관 - 전투 상황 최적 전략 수립"""
    try:
        current_difficulty = getattr(party_members[0], 'world_difficulty', '쉬움') if party_members else '쉬움'
        if current_difficulty in ['어려움', '지옥', 'HARD', 'NIGHTMARE', 'INSANE']:
            return {"status": "BLOCKED", "message": "🚫 로-바트 전투사령관: 고난이도에서는 내 지휘 봉인... (미안!)"}
        
        if not party_members:
            return {"status": "CRITICAL", "message": "🤖 로-바트: 파티 전멸... 이럴 줄 알았어! 게임 오버야!"}
        
        # 전투 상황 종합 분석
        party_analysis = _analyze_party_combat_state(party_members)
        enemy_analysis = _analyze_enemy_threat(enemies) if enemies else {"threat": 0}
        
        # 전투 전략 수립
        strategy = _formulate_battle_strategy(party_analysis, enemy_analysis, battle_state)
        
        return {
            "status": "ACTIVE",
            "party_state": party_analysis,
            "enemy_threat": enemy_analysis,
            "strategy": strategy,
            "priority_actions": _get_priority_battle_actions(party_analysis, enemy_analysis)
        }
        
    except Exception as e:
        return {"status": "ERROR", "message": f"전투 AI 오류: {e}"}


def _analyze_party_combat_state(members):
    """파티 전투 상태 분석"""
    try:
        total_hp_ratio = sum(char.current_hp / char.max_hp for char in members) / len(members)
        total_mp_ratio = sum(char.current_mp / char.max_mp for char in members) / len(members)
        
        # 위험 인물 식별
        critical_members = [char for char in members if char.current_hp / char.max_hp < 0.3]
        high_brv_members = [char for char in members if getattr(char, 'brv_points', 0) >= 300]
        
        return {
            "avg_hp_ratio": total_hp_ratio,
            "avg_mp_ratio": total_mp_ratio,
            "critical_count": len(critical_members),
            "ready_for_hp_attack": len(high_brv_members),
            "total_combat_power": sum(calculate_combat_power(char) for char in members)
        }
    except:
        return {"avg_hp_ratio": 0.5, "avg_mp_ratio": 0.5, "critical_count": 0, "ready_for_hp_attack": 0}


def _analyze_enemy_threat(enemies):
    """적 위험도 분석"""
    try:
        if not enemies:
            return {"threat": 0, "priority_targets": []}
        
        total_threat = 0
        priority_targets = []
        
        for enemy in enemies:
            enemy_power = getattr(enemy, 'level', 1) * 10
            enemy_hp_ratio = getattr(enemy, 'current_hp', 100) / getattr(enemy, 'max_hp', 100)
            
            # 위험한 적 식별
            if enemy_hp_ratio < 0.3:  # 거의 죽은 적
                priority_targets.append({"name": getattr(enemy, 'name', 'Unknown'), "priority": "FINISH"})
            elif enemy_power > 100:  # 강한 적
                priority_targets.append({"name": getattr(enemy, 'name', 'Unknown'), "priority": "FOCUS"})
            
            total_threat += enemy_power * enemy_hp_ratio
        
        return {"threat": int(total_threat), "priority_targets": priority_targets}
    except:
        return {"threat": 50, "priority_targets": []}


def _formulate_battle_strategy(party_analysis, enemy_analysis, battle_state):
    """전투 전략 수립"""
    try:
        strategies = []
        
        # 긴급 상황 전략
        if party_analysis["critical_count"] >= 2:
            strategies.append("🆘 로-바트의 긴급 진단: 위험하지만 걱정 마라! 내가 있잖아?")
            strategies.append("💊 로-바트 추천: 포션을 아끼는 건 바보나 하는 짓이야. 써!")
            strategies.append("🏃 로-바트의 현명한 조언: 때로는 전략적 후퇴가 최고의 승리법이지~ 내 덕분에 살았네?")
            return strategies
        
        # 공격적 전략
        if party_analysis["ready_for_hp_attack"] >= 2:
            strategies.append("⚔️ 로-바트의 완벽한 타이밍! 총공격 개시! 내 계산이 틀릴 리 없지~")
            strategies.append("🎯 로-바트 전술: 약한 놈부터 정리하는 게 기본이야. 내가 가르쳐준 대로!")
        
        # 균형 전략
        if party_analysis["avg_hp_ratio"] > 0.6 and party_analysis["avg_mp_ratio"] > 0.4:
            strategies.append("⚡ 로-바트의 고급 전술: 스킬을 아끼는 건 3류나 하는 짓! 써제껴!")
            strategies.append("🔥 로-바트 추천: BRV 300+ 모아서 화끈하게! 내 계산 믿고 가라고~")
        
        # 방어적 전략
        if enemy_analysis["threat"] > party_analysis["total_combat_power"] * 1.2:
            strategies.append("🛡️ 로-바트의 냉정한 판단: 이럴 땐 신중하게! 내 말만 들어봐")
            strategies.append("💚 로-바트 경고: HP 50% 되면 바로 회복! 죽으면 내 탓 아니야?")
        
        if not strategies:
            strategies.append("⚔️ 로-바트의 기본 전술: BRV 모아서 HP 공격! 이것도 못하면 게임 그만둬")
        
        return strategies
    except:
        return ["🤖 로-바트: 에러 발생! 하지만 내가 있으니 안전하게 진행할게~"]


def _get_priority_battle_actions(party_analysis, enemy_analysis):
    """로-바트의 우선순위 전투 행동 지시"""
    try:
        actions = []
        
        if party_analysis["critical_count"] > 0:
            actions.append("🥇 로-바트 명령: 위험한 아군 즉시 치료! 내 파티원을 잃을 순 없어!")
        
        if enemy_analysis["priority_targets"]:
            for target in enemy_analysis["priority_targets"][:2]:
                if target["priority"] == "FINISH":
                    actions.append(f"🥈 로-바트의 완벽한 계산: {target['name']} 마무리 공격! 이거면 끝!")
                elif target["priority"] == "FOCUS":
                    actions.append(f"🥈 로-바트 지시: {target['name']} 집중 타격! 내가 찍은 놈이야!")
        
        if party_analysis["ready_for_hp_attack"] > 0:
            actions.append("🥉 로-바트 추천: BRV 높은 멤버로 HP 공격! 내 계산 믿고 가!")
        
        if not actions:
            actions.append("🤖 로-바트의 기본 전술: BRV 축적 후 HP 공격! 이것도 못하면 게임 그만둬")
        
        return actions
    except:
        return ["🤖 로-바트: 에러 났지만 내가 있으니 안전한 행동으로 갈게~"]


def analyze_equipment_deficiencies(members):
    """장비 부족 분석 (파격적 AI 기능)"""
    try:
        issues = []
        for member in members:
            if not hasattr(member, 'equipment'):
                continue
                
            empty_slots = []
            weak_equipment = []
            
            # 장비 슬롯 확인
            expected_slots = ['weapon', 'armor', 'accessory']
            for slot in expected_slots:
                if slot not in member.equipment or not member.equipment[slot]:
                    empty_slots.append(slot)
                else:
                    item = member.equipment[slot]
                    # 레벨 대비 장비 품질 확인
                    item_power = getattr(item, 'attack', 0) + getattr(item, 'defense', 0)
                    expected_power = member.level * 5
                    if item_power < expected_power * 0.6:
                        weak_equipment.append(slot)
            
            if empty_slots:
                return f"🤖 로-바트 지적: {member.name}! 장비도 안 챙기고 뭐하는 거야? 미착용: {', '.join(empty_slots)}"
            elif weak_equipment:
                return f"🤖 로-바트 충고: {member.name}의 장비가 후져! 업그레이드 필요: {', '.join(weak_equipment)}"
        
        return None
    except:
        return "🤖 로-바트: 장비 체크 중 오류! 하지만 내가 있으니 걱정 마!"


def analyze_cooking_materials(party_manager, world):
    """요리 재료 및 버프 분석 (실제 요리 시스템 연동)"""
    try:
        # 요리 시스템 확인
        if not hasattr(party_manager, 'cooking_system'):
            return "요리 시스템 미활성화"
        
        cooking_system = party_manager.cooking_system
        
        # 현재 보유 재료 확인
        if not hasattr(cooking_system, 'inventory') or not cooking_system.inventory:
            return "🤖 로-바트 한탄: 요리 재료가 하나도 없네? 채집이나 하러 가!"
        
        inventory = cooking_system.inventory
        total_ingredients = sum(inventory.values())
        
        if total_ingredients < 5:
            return f"🤖 로-바트 지적: 재료 겨우 {total_ingredients}개? 이런 걸로 어떻게 요리해? 채집 좀 해!"
        
        # 재료 균형 확인
        ingredient_types = {
            '고기류': 0, '채소류': 0, '향신료': 0, '액체류': 0, '과일류': 0
        }
        
        for ingredient_name, count in inventory.items():
            # 재료 타입 추정 (실제 시스템에 맞게 조정 필요)
            if '고기' in ingredient_name or '생선' in ingredient_name:
                ingredient_types['고기류'] += count
            elif '채소' in ingredient_name or '버섯' in ingredient_name:
                ingredient_types['채소류'] += count
            elif '향신료' in ingredient_name or '소금' in ingredient_name:
                ingredient_types['향신료'] += count
            elif '물' in ingredient_name or '우유' in ingredient_name:
                ingredient_types['액체류'] += count
            elif '과일' in ingredient_name or '딸기' in ingredient_name:
                ingredient_types['과일류'] += count
        
        # 부족한 재료 타입 찾기
        insufficient_types = [type_name for type_name, count in ingredient_types.items() if count < 2]
        
        if insufficient_types:
            return f"🤖 로-바트 분석: 재료 균형 엉망! {', '.join(insufficient_types)} 더 가져와!"
        
        # 버프 상태 확인
        unbuffed_members = []
        for member in party_manager.get_alive_members():
            if hasattr(member, 'food_buffs') and member.food_buffs:
                continue  # 버프 있음
            elif hasattr(cooking_system, 'active_food_effect') and cooking_system.active_food_effect:
                continue  # 전체 버프 있음
            else:
                unbuffed_members.append(member.name)
        
        if unbuffed_members and total_ingredients >= 10:
            return f"🤖 로-바트 추천: 재료 충분하니까 {unbuffed_members[0]}한테 버프나 줘! 내가 시켜야 하나?"
        
        # 고급 재료 확인
        rare_ingredients = [name for name, count in inventory.items() if '고급' in name or '특수' in name]
        if rare_ingredients:
            return f"🤖 로-바트 발견: 고급 재료 {rare_ingredients[0]} 있네? 특수 요리나 해봐!"
        
        return None
    except Exception as e:
        # 에러 디버깅을 위해 상세 정보 표시
        return f"🤖 로-바트: 요리 분석 중 오류! {str(e)[:30]}... 하지만 걱정 마!"


def analyze_skill_usage(members):
    """로-바트의 스킬 사용 최적화 분석"""
    try:
        for member in members:
            mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
            
            # MP가 가득 찬 캐릭터 확인
            if mp_ratio >= 0.9:
                return f"🤖 로-바트 지시: {member.name} MP 가득참! 스킬 써제껴! 아끼면 바보야!"
            
            # MP가 너무 낮은 캐릭터 확인
            elif mp_ratio < 0.3:
                return f"🤖 로-바트 경고: {member.name} MP 바닥! 마력 수정이나 찾아와!"
        
        return None
    except:
        return "🤖 로-바트: 스킬 분석 중 오류! 하지만 내가 있으니 괜찮아!"


def analyze_progression_readiness(members, world):
    """로-바트의 진행 준비도 분석"""
    try:
        combat_powers = [calculate_combat_power(char) for char in members]
        avg_power = sum(combat_powers) // len(combat_powers) if combat_powers else 0
        
        current_level = getattr(world, 'current_level', 1)
        expected_power = current_level * 15
        
        if avg_power < expected_power * 0.7:
            weakest_member = min(members, key=lambda x: calculate_combat_power(x))
            return f"🤖 로-바트 진단: 전투력 부족! {weakest_member.name} 강화부터 해! 내 말 안 들으면 죽어!"
        elif avg_power >= expected_power * 1.3:
            return "🤖 로-바트 인정: 강력한 파티네! 내가 잘 키웠어~ 보너스 층도 도전해봐!"
        
        return None
    except:
        return "🤖 로-바트: 진행 준비도 분석 중 오류! 하지만 내가 판단하기로는... 괜찮을걸?"


class GameDisplay:
    """게임 화면 표시 클래스"""
    
    def __init__(self):
        self.screen_width = 120  # 화면 너비 증가
        self.screen_height = 35  # 화면 높이 증가
        
    def clear_screen(self):
        """화면 지우기 - 간단하고 안정적인 버전"""
        # 파이프/모바일 모드에서는 화면 깜빡임 방지를 위해 하드 클리어 금지
        if os.getenv('SUBPROCESS_MODE') == '1':
            try:
                # 소프트 클리어: 몇 줄만 내려 새 영역 확보
                print("\n" * 3)
                return
            except Exception:
                return
        # 일반 모드에서는 OS 명령어 사용
        try:
            if platform.system() == "Windows":
                os.system('cls')
            else:
                os.system('clear')
        except Exception:
            # OS 명령어 실패 시 새 라인으로 대체
            print("\n" * 50)
            
    def show_title(self):
        """타이틀 화면 표시 (글꼴 호환성 개선)"""
        self.clear_screen()
        
        # 터미널 설정 안내
        print("=" * 70)
        print("   DAWN OF STELLAR - 별빛의 여명")
        print("=" * 70)
        print()
        print("  최적의 게임 환경을 위한 터미널 설정 안내:")
        print("  • Windows: 설정 > 글꼴에서 'Consolas' 또는 'Courier New' 선택")
        print("  • PowerShell: 속성 > 글꼴 > 'Consolas' 권장")
        print("  • CMD: 속성 > 글꼴 > 'Consolas' 또는 래스터 글꼴")
        print("  • 터미널 크기: 최소 120x30 권장")
        print()
        
        title_art = """
══════════════════════════════════════════════════════════════════════════
                                                                          
                          DAWN OF STELLAR                                
                             별빛의 여명                                    
                                                                       
                         전술 로그라이크 게임                                                                                  
                                                                          
══════════════════════════════════════════════════════════════════════════
        """
        print(title_art)
        print("\n" + "="*60)
        print("게임을 시작합니다...")
        input("Enter 키를 눌러 계속...")
        
    def show_game_screen(self, party_manager: PartyManager, world: GameWorld, cooking_system=None):
        """메인 게임 화면 표시 - 간소화된 버전"""
        # 화면 클리어 먼저 실행
        self.clear_screen()
        
        try:
            # 안전한 너비 설정
            safe_width = min(80, self.screen_width)
            
            # 상단 정보 표시
            title = f"던전 {world.current_level}층 - Dawn Of Stellar"
            title_padding = (safe_width - len(title)) // 2
            print(f"{' ' * title_padding}{bright_cyan(title)}")
            print()
            
            # 던전 맵 표시 (색상 적용)
            try:
                map_display = world.get_colored_map_display(min(30, safe_width - 4), 15)  # 색상 맵 사용
                for line in map_display:
                    # 줄 길이 제한 (색상 코드 때문에 실제 길이와 표시 길이가 다를 수 있음)
                    print(f"  {line}")
            except Exception as map_error:
                print(f"  맵 표시 오류: {map_error}")
                print(f"  기본 맵 정보: 현재 위치 {world.player_pos}")
                
            print()
            
            # 파티 상태 정보 - 간소화 (중복 제거)
            alive_count = len(party_manager.get_alive_members())
            total_count = len(party_manager.members)
            
            party_info = f"파티: {alive_count}/{total_count}명 생존 | 층: {world.current_level}"
            
            # 골드 정보 안전하게 표시
            try:
                gold_info = f" | 골드: {party_manager.party_gold}G"
            except:
                gold_info = ""
            
            # 가방 무게 정보 추가 (색깔 포함)
            try:
                if cooking_system:
                    total_weight = cooking_system.get_total_inventory_weight()
                    max_weight = cooking_system.get_max_inventory_weight()
                    weight_ratio = total_weight / max_weight if max_weight > 0 else 0
                    
                    # 무게 비율에 따른 색깔 결정
                    if weight_ratio < 0.5:  # 50% 미만: 초록색
                        weight_color = "\033[92m"  # 밝은 초록
                    elif weight_ratio < 0.8:  # 80% 미만: 노란색
                        weight_color = "\033[93m"  # 노란색
                    elif weight_ratio < 0.95:  # 95% 미만: 주황색
                        weight_color = "\033[91m"  # 빨간색
                    else:  # 95% 이상: 깜빡이는 빨간색
                        weight_color = "\033[91m\033[5m"  # 깜빡이는 빨간색
                    
                    reset_color = "\033[0m"
                    weight_info = f" | 가방: {weight_color}{total_weight:.1f}/{max_weight:.1f}kg{reset_color}"
                else:
                    weight_info = ""
            except:
                weight_info = ""
            
            print(f"  {party_info}{gold_info}{weight_info}")
            print("+" + "-" * (safe_width - 2) + "+")
            
            # 파티원 상태 (간소화)
            for i, member in enumerate(party_manager.members[:4]):  # 최대 4명만 표시
                if member.is_alive:
                    # HP/MP 비율 계산
                    hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                    mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                    
                    # HP 색상 계산
                    if hp_ratio >= 0.8:
                        hp_color = bright_green
                        hp_emoji = "💚"
                    elif hp_ratio >= 0.6:
                        hp_color = green
                        hp_emoji = "💛"
                    elif hp_ratio >= 0.4:
                        hp_color = yellow
                        hp_emoji = "🧡"
                    elif hp_ratio >= 0.2:
                        hp_color = bright_red
                        hp_emoji = "❤️"
                    else:
                        hp_color = red
                        hp_emoji = "💔"
                    
                    # MP 색상 계산
                    if mp_ratio >= 0.8:
                        mp_color = bright_cyan
                        mp_emoji = "💙"
                    else:
                        mp_color = cyan
                        mp_emoji = "💙"
                    
                    # 직업별 이모지
                    class_emoji = {
                        "전사": "⚔️", "마법사": "🔮", "도둑": "🗡️", "성직자": "✨",
                        "궁수": "🏹", "사무라이": "🗾", "드루이드": "🌿", "정령술사": "💫",
                        "네크로맨서": "💀", "팔라딘": "🛡️", "어쌔신": "🥷", "바드": "🎵",
                        "성기사": "🛡️", "암흑기사": "🖤", "몽크": "👊", "용기사": "🐉",
                        "검성": "⚡", "암살자": "🗡️", "기계공학자": "🔧", "무당": "🔯",
                        "해적": "☠️", "철학자": "📚", "시간술사": "⏰", "연금술사": "⚗️",
                        "검투사": "🏟️", "기사": "🐎", "신관": "⛪", "마검사": "🌟",
                        "차원술사": "🌀", "광전사": "😤"
                    }.get(member.character_class, "👤")
                    
                    name_class = f"{class_emoji} {member.name[:8]:8} ({member.character_class[:6]:6})"
                    
                    # 상처 정보 안전하게 표시
                    wounds_info = ""
                    try:
                        if hasattr(member, 'wounds') and member.wounds > 0:
                            wounds_info = f"🩸WOUND: {member.wounds}"
                    except:
                        pass
                    
                    # 최종 상태 라인
                    hp_text = f"{hp_emoji}HP:{hp_color(f'{member.current_hp:3}/{member.max_hp:3}')}"
                    mp_text = f"{mp_emoji}MP:{mp_color(f'{member.current_mp:2}/{member.max_mp:2}')}"
                    status_line = f"  {name_class} {hp_text} {mp_text}{wounds_info}"
                    print(f"  {status_line}")
                else:
                    # 사망한 파티원
                    class_emoji = "💀"
                    name_class = f"{class_emoji} {member.name[:8]:8} ({member.character_class[:6]:6})"
                    status_line = f"  {name_class} {red('사망')}"
                    print(f"  {status_line}")
            
            print("+" + "-" * (safe_width - 2) + "+")
            
            # 🎮 키 조작 안내 (하단에 표시)
            print(f"\n🎮 {bright_cyan('조작키')} | WASD:이동 | I:인벤토리 | F:스킬 | P:파티 | {bright_yellow('H:도움말')}")

            # 🎮 게임 통계 정보 추가
            try:
                print(f"\n📊 {bright_cyan('게임 정보')}")
                
                # 파티 전투력 계산
                alive_members = party_manager.get_alive_members()
                if alive_members:
                    combat_powers = [calculate_combat_power(char) for char in alive_members]
                    avg_combat_power = sum(combat_powers) // len(combat_powers)
                    
                    # 전투력 색상 평가
                    expected_power = world.current_level * 15  # 층수 * 15가 권장 전투력
                    if avg_combat_power >= expected_power * 1.2:
                        power_status = green("강력함 💪")
                    elif avg_combat_power >= expected_power:
                        power_status = yellow("적정함 ⚖️")
                    elif avg_combat_power >= expected_power * 0.8:
                        power_status = yellow("약함 ⚠️")
                    else:
                        power_status = red("위험함 💀")
                else:
                    avg_combat_power = 0
                    power_status = red("파티 전멸")
                
                alive_count = len(alive_members)
                total_gold = sum(char.gold for char in party_manager.members)
                
                print(f"│ 파티: {alive_count}/{len(party_manager.members)}명 생존 | 전투력: {avg_combat_power} ({power_status}) | 골드: {total_gold:,}")
                
                # AI 추천 행동
                ai_recommendation = get_ai_recommendation(party_manager, world)
                print(f"│ {ai_recommendation}")
                
                # 던전 통계
                if hasattr(world, 'enemies_defeated'):
                    print(f"│ 처치한 적: {world.enemies_defeated}체 | 발견한 보물: {getattr(world, 'treasures_found', 0)}개")
                
                # 진행도
                progress = min(100, (world.current_level / 10) * 100)
                progress_bar = "█" * int(progress // 10) + "░" * (10 - int(progress // 10))
                print(f"│ 진행도: [{progress_bar}] {progress:.1f}%")
                
            except Exception as e:
                print(f"│ 게임 정보 표시 오류: {e}")
            
            # �📍 추가 정보 (위치, 난이도, 플레이 시간 등)
            try:
                info_parts = []
                
                # 위치 정보
                if hasattr(world, 'player_pos') and world.player_pos:
                    pos_x, pos_y = world.player_pos
                    info_parts.append(f"📍 위치: ({pos_x}, {pos_y})")
                
                # 층수 정보
                info_parts.append(f"🗺️ 층: {world.current_level}")
                
                # 난이도 정보
                if hasattr(world, 'difficulty'):
                    info_parts.append(f"⚡ 난이도: {world.difficulty}")
                elif hasattr(world, 'game') and hasattr(world.game, 'difficulty'):
                    info_parts.append(f"⚡ 난이도: {world.game.difficulty}")
                
                # 플레이 시간 정보
                if hasattr(world, 'game') and hasattr(world.game, 'start_time'):
                    import time
                    elapsed = time.time() - world.game.start_time
                    hours = int(elapsed // 3600)
                    minutes = int((elapsed % 3600) // 60)
                    if hours > 0:
                        info_parts.append(f"⏰ 플레이: {hours}시간 {minutes}분")
                    else:
                        info_parts.append(f"⏰ 플레이: {minutes}분")
                
                # 게임 목표/힌트 추가
                if hasattr(world, 'current_level'):
                    if world.current_level == 1:
                        info_parts.append(f"🎯 목표: 계단 찾아 다음 층으로!")
                    elif world.current_level % 3 == 0:
                        info_parts.append(f"🔥 보스층! 강력한 적이 기다립니다")
                    elif world.current_level % 5 == 0:
                        info_parts.append(f"💎 특수층: 귀중한 보상 획득 기회")
                    else:
                        info_parts.append(f"⬇️ 계단을 찾아 {world.current_level + 1}층으로 이동")
                
                if info_parts:
                    print(" | ".join(info_parts))
            except:
                pass
            
            # 게임 메시지 표시 (맵 아래쪽)
            if hasattr(world, 'game') and world.game and hasattr(world.game, 'message_buffer'):
                messages = world.game.get_recent_messages()
                if messages:
                    print("\n📢 최근 상황:")
                    for message in messages[-3:]:  # 최근 3개 메시지만 표시
                        print(f"  {message}")
                    print()
            
        except Exception as e:
            # 최종 폴백: 최소한의 정보
            print(f"🎮 Dawn of Stellar - 던전 {getattr(world, 'current_level', 1)}층")
            print(f"📍 위치: {getattr(world, 'player_pos', '?')}")
            print(f"⚠️ 화면 표시 오류: {e}")
            print("게임은 계속 진행됩니다.")
            print(f"🎮 {bright_yellow('H:도움말')} | WASD:이동 | I:인벤토리")



        
    def show_party_status(self, party_manager: PartyManager):
        """상세 파티 상태 표시"""
        print("\n" + bright_cyan("="*90, True))
        print(bright_cyan("=== 🎭 파티 상태 ===", True))
        print(bright_cyan("="*90, True))
        
        for i, member in enumerate(party_manager.members, 1):
            # 직업별 이모지
            class_emoji = {
                # 기본 직업
                "전사": "⚔️", "마법사": "🔮", "도둑": "🗡️", "성직자": "✨",
                "궁수": "🏹", "사무라이": "🗾", "드루이드": "🌿", "정령술사": "💫",
                "네크로맨서": "💀", "팔라딘": "🛡️", "어쌔신": "🥷", "바드": "🎵",
                
                # 확장 직업
                "성기사": "🛡️", "암흑기사": "🖤", "몽크": "👊", "용기사": "🐉",
                "검성": "⚡", "암살자": "🗡️", "기계공학자": "🔧", "무당": "🔯",
                "해적": "☠️", "철학자": "📚", "시간술사": "⏰", "연금술사": "⚗️",
                "검투사": "🏟️", "기사": "🐎", "신관": "⛪", "마검사": "🌟",
                "차원술사": "🌀", "시인": "📜", "학자": "🎓", "상인": "💰",
                "광전사": "😤", "무희": "💃", "점성술사": "🔮", "영매": "👻",
                "흑기사": "⚫", "현자": "🧙"
            }.get(member.character_class, "👤")
            
            # 생존 상태에 따른 표시
            if member.is_alive:
                print(f"\n[{bright_yellow(str(i))}] {class_emoji} {bright_white(member.name)} - {green(member.character_class)}")
                
                # HP/MP 비율과 색상
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                
                # HP 상태
                if hp_ratio >= 0.8:
                    hp_display = f"💚 HP {bright_green(f'{member.current_hp}/{member.max_hp}')}"
                elif hp_ratio >= 0.6:
                    hp_display = f"💛 HP {yellow(f'{member.current_hp}/{member.max_hp}')}"
                elif hp_ratio >= 0.4:
                    hp_display = f"🧡 HP {yellow(f'{member.current_hp}/{member.max_hp}')}"
                elif hp_ratio >= 0.2:
                    hp_display = f"❤️ HP {bright_red(f'{member.current_hp}/{member.max_hp}')}"
                else:
                    hp_display = f"💔 HP {red(f'{member.current_hp}/{member.max_hp}')}"
                
                # MP 색상과 이모지 계산
                if mp_ratio >= 0.8:
                    mp_display = f"💙 MP {bright_cyan(f'{member.current_mp}/{member.max_mp}')}"
                elif mp_ratio >= 0.6:
                    mp_display = f"💙 MP {cyan(f'{member.current_mp}/{member.max_mp}')}"
                elif mp_ratio >= 0.4:
                    mp_display = f"💙 MP {blue(f'{member.current_mp}/{member.max_mp}')}"
                elif mp_ratio >= 0.2:
                    mp_display = f"💜 MP {magenta(f'{member.current_mp}/{member.max_mp}')}"
                else:
                    mp_display = f"❤️ MP {red(f'{member.current_mp}/{member.max_mp}')}"
                
                print(f"    HP: {hp_display}  |  MP: {mp_display}")
                
                # 전투력 표시
                combat_power = calculate_combat_power(member)
                level_power = member.level * 15  # 레벨 기준 권장 전투력
                
                if combat_power >= level_power * 1.2:
                    power_color = green(f"전투력: {combat_power} 💪")
                elif combat_power >= level_power:
                    power_color = yellow(f"전투력: {combat_power} ⚖️")
                elif combat_power >= level_power * 0.8:
                    power_color = yellow(f"전투력: {combat_power} ⚠️")
                else:
                    power_color = red(f"전투력: {combat_power} 💀")
                
                print(f"    레벨: {bright_white(str(member.level))}  |  {power_color}")
                
                # 상처 정보
                if hasattr(member, 'wounds') and member.wounds > 0:
                    wounds_ratio = member.wounds / member.max_hp if member.max_hp > 0 else 0
                    if wounds_ratio >= 0.5:
                        wound_color = red(f"🩸 WOUND: {member.wounds} (심각)")
                    elif wounds_ratio >= 0.3:
                        wound_color = yellow(f"🩸 WOUND: {member.wounds} (보통)")
                    else:
                        wound_color = white(f"🩸 WOUND: {member.wounds} (경미)")
                    print(f"    {wound_color}")
            else:
                print(f"\n[{bright_yellow(str(i))}] {class_emoji} {red(member.name)} - {red(member.character_class)} {red('💀 사망')}")
            
            # 상세 정보 (색상 적용)
            atk_color = bright_green if member.physical_attack >= 50 else green if member.physical_attack >= 30 else white
            def_color = bright_blue if member.physical_defense >= 50 else blue if member.physical_defense >= 30 else white
            mag_atk_color = bright_magenta if member.magic_attack >= 50 else magenta if member.magic_attack >= 30 else white
            mag_def_color = bright_cyan if member.magic_defense >= 50 else cyan if member.magic_defense >= 30 else white
            
            print(f"    ⚔️ 물리: ATK {atk_color(str(member.physical_attack))} / DEF {def_color(str(member.physical_defense))} | "
                  f"🔮 마법: ATK {mag_atk_color(str(member.magic_attack))} / DEF {mag_def_color(str(member.magic_defense))} | "
                  f"✨ 경험치: {bright_yellow(str(member.experience))}")
            
            # 통합 인벤토리 정보 (첫 번째 멤버에게만 표시)
            if i == 1 and hasattr(party_manager, 'shared_inventory'):
                current_weight = party_manager.get_current_carry_weight()
                max_weight = party_manager.get_total_carry_capacity()
                weight_ratio = current_weight / max_weight if max_weight > 0 else 0
                
                if weight_ratio >= 0.9:
                    weight_display = f"🧳 {red(f'{current_weight:.1f}/{max_weight:.1f}kg')} {red('과부하!')}"
                elif weight_ratio >= 0.7:
                    weight_display = f"🎒 {yellow(f'{current_weight:.1f}/{max_weight:.1f}kg')} {yellow('무거움')}"
                else:
                    weight_display = f"🎒 {green(f'{current_weight:.1f}/{max_weight:.1f}kg')} {green('양호')}"
                
                item_count = len(party_manager.shared_inventory.items) if hasattr(party_manager.shared_inventory, 'items') else 0
                print(f"    💼 파티 인벤토리: {weight_display} | 📦 아이템: {bright_cyan(str(item_count))}개")
                  
            # 특성 정보
            if hasattr(member, 'active_traits') and member.active_traits:
                print(f"    🌟 특성:")
                for trait in member.active_traits[:3]:  # 최대 3개까지 표시
                    if hasattr(trait, 'name') and hasattr(trait, 'description'):
                        # 특성 이름을 청록색으로, 설명을 흰색으로 표시
                        print(f"      • {bright_cyan(trait.name)}: {white(trait.description)}")
                    elif hasattr(trait, 'name'):
                        print(f"      • {bright_cyan(trait.name)}")
                    else:
                        print(f"      • {white(str(trait))}")
                
                # 3개 초과시 추가 특성 개수 표시
                if len(member.active_traits) > 3:
                    remaining = len(member.active_traits) - 3
                    print(f"      {bright_black(f'... 외 {remaining}개 특성 보유')}")
                
            # HP 상태 세부사항
            if member.is_alive:
                hp_percentage = (member.current_hp / member.limited_max_hp * 100) if member.limited_max_hp > 0 else 0
                wound_percentage = (member.wounds / member.max_hp * 100) if member.max_hp > 0 else 0
                
                if hp_percentage >= 80:
                    hp_status = bright_green(f"{hp_percentage:.1f}%")
                elif hp_percentage >= 60:
                    hp_status = yellow(f"{hp_percentage:.1f}%")
                elif hp_percentage >= 40:
                    hp_status = yellow(f"{hp_percentage:.1f}%")
                else:
                    hp_status = bright_red(f"{hp_percentage:.1f}%")
                
                print(f"    💗 HP 상태: {hp_status}", end="")
                
                if member.wounds > 0:
                    if wound_percentage >= 50:
                        wound_status = red(f" | 🩸 중상: {wound_percentage:.1f}%")
                    elif wound_percentage >= 30:
                        wound_status = yellow(f" | 🩸 경상: {wound_percentage:.1f}%")
                    else:
                        wound_status = bright_red(f" | 🩸 상처: {wound_percentage:.1f}%")

                    print(wound_status)
                    print(f"      상처로 인한 최대 HP 감소: {red(str(member.wounds))} ({member.max_hp} → {bright_red(str(member.limited_max_hp))})")
                else:
                    print(f" | 🌟 {bright_green('상처 없음')}")
                
        # === 고급 AI 파티 분석 (쉬움/보통 난이도만) ===
        try:
            world_difficulty = getattr(party_manager, 'world_difficulty', '쉬움')  # 임시로 쉬움 설정
            if world_difficulty not in ['어려움', '지옥', 'HARD', 'NIGHTMARE']:
                print(f"\n{bright_cyan('� 로-바트 파티 분석 (내가 직접 해봤어!)', True)}")
                print(bright_cyan("="*90, True))
                
                # 장비 분석 (로-바트 전문 분야)
                equipment_analysis = analyze_equipment_deficiencies(party_manager.get_alive_members())
                if equipment_analysis:
                    print(f"🤖 장비: {yellow(equipment_analysis + ' (로-바트 진단 완료!)')}")
                else:
                    print(f"🤖 장비: {green('최적 상태 (역시 내 눈이 정확해!)')}")
                
                # 요리/재료 분석 (로-바트는 요리도 잘해!)
                cooking_analysis = analyze_cooking_materials(party_manager, None)
                if cooking_analysis:
                    print(f"🍳 요리: {yellow(cooking_analysis + ' (로-바트 요리 팁!)')}")
                else:
                    print(f"🍳 요리: {green('재료 충분 (로-바트 승인!)')}")
                
                # 스킬/MP 분석 (로-바트 계산)
                skill_analysis = analyze_skill_usage(party_manager.get_alive_members())
                if skill_analysis:
                    print(f"✨ 스킬: {yellow(skill_analysis + ' (로-바트 관찰 결과)')}")
                else:
                    print(f"✨ 스킬: {green('MP 상태 양호 (로-바트 확인 완료!)')}")
                
                # 전투력 분석
                alive_members = party_manager.get_alive_members()
                if alive_members:
                    combat_powers = [calculate_combat_power(char) for char in alive_members]
                    avg_power = sum(combat_powers) // len(combat_powers)
                    weakest = min(alive_members, key=lambda x: calculate_combat_power(x))
                    strongest = max(alive_members, key=lambda x: calculate_combat_power(x))
                    
                    print(f"⚔️ 로-바트 전투력 측정: 평균 {bright_white(str(avg_power))} | 최강: {green(strongest.name + ' (짱!)')} | 최약: {red(weakest.name + ' (분발!)')}")
                
                print(bright_cyan("="*90, True))
            else:
                print(f"\n{bright_red('🚫 고난이도라서 로-바트 분석 비활성화 (너무 어려워!)', True)}")
                
        except Exception as e:
            print(f"\n{red('로-바트 분석 오류:')} {e} (어? 뭔가 이상한데?)")
        
        print("\n" + bright_cyan("="*90, True))
        input(bright_white("Enter 키를 눌러 계속...", True))
        
    def show_minimap(self, world: GameWorld, size: int = 5):
        """미니맵 표시"""
        player_x, player_y = world.player_pos
        
        print(f"\n미니맵 (주변 {size}x{size} 영역):")
        print("┌" + "─" * (size * 2 + 1) + "┐")
        
        for dy in range(-size//2, size//2 + 1):
            line = "│ "
            for dx in range(-size//2, size//2 + 1):
                x, y = player_x + dx, player_y + dy
                
                if dx == 0 and dy == 0:
                    line += "@"  # 플레이어
                elif world.is_valid_pos(x, y):
                    line += world.get_tile_char(x, y)
                else:
                    line += " "
                    
                line += " "
            line += "│"
            print(line)
            
        print("└" + "─" * (size * 2 + 1) + "┘")
        
    def show_ascii_art(self, art_type: str):
        """ASCII 아트 표시"""
        arts = {
            "sword": [
                "    /|",
                "   / |",
                "  /__|__",
                " |    |",
                " |    |",
                " |____|"
            ],
            "shield": [
                "  ╭─────╮",
                " ╱       ╲",
                "│   ┌─┐   │",
                "│   │ │   │",
                " ╲ ╱   ╲ ╱",
                "  ╰─────╯"
            ],
            "potion": [
                "   ╭─╮",
                "   │ │",
                "  ╭─┴─╮",
                " ╱     ╲",
                "│ ☆ ☆ ☆ │",
                " ╲     ╱",
                "  ╰───╯"
            ]
        }
        
        if art_type in arts:
            for line in arts[art_type]:
                print(line)
                
    def show_damage_effect(self, damage: int, is_critical: bool = False):
        """데미지 이펙트 표시"""
        if is_critical:
            print(f"    ★ CRITICAL! {damage} ★")
        else:
            print(f"    -{damage}")
            
    def show_heal_effect(self, heal_amount: int):
        """회복 이펙트 표시"""
        print(f"    +{heal_amount} HP ♥")
        
    def draw_progress_bar(self, current: int, maximum: int, length: int = 20, 
                         filled_char: str = "█", empty_char: str = "░") -> str:
        """진행률 바 그리기"""
        if maximum == 0:
            return f"[{empty_char * length}]"
            
        filled_length = int((current / maximum) * length)
        bar = filled_char * filled_length + empty_char * (length - filled_length)
        return f"[{bar}]"
        
    def show_level_up_effect(self, character: Character, old_level: int):
        """레벨업 이펙트 - 색상 개선"""
        from .color_text import bright_green, bright_yellow, bright_cyan, cyan, yellow, red, blue, magenta, white
        
        print("\n" + bright_cyan("="*50))
        print(f"    {bright_yellow('★ LEVEL UP! ★')}")
        print(f"    {bright_green(character.name)}: {cyan(f'Lv.{old_level}')} → {bright_yellow(f'Lv.{character.level}')}")
        
        # 스탯 증가 정보 (개선된 색상으로)
        if hasattr(character, '_last_level_stats'):
            stats = character._last_level_stats
            print(f"  {red('💪 HP')} +{character.max_hp - stats.get('hp', character.max_hp)}, {blue('MP')} +{character.max_mp - stats.get('mp', character.max_mp)}, {yellow('물리공격')} +{character.physical_attack - stats.get('p_atk', character.physical_attack)}, {magenta('마법공격')} +{character.magic_attack - stats.get('m_atk', character.magic_attack)}")
            print(f"  {cyan('🛡️ 물리방어')} +{character.physical_defense - stats.get('p_def', character.physical_defense)}, {blue('마법방어')} +{character.magic_defense - stats.get('m_def', character.magic_defense)}, {bright_green('속도')} +{character.speed - stats.get('speed', character.speed)}")
            print(f"  {red('⚡ 현재 HP:')} {bright_green(f'{character.current_hp}/{character.max_hp}')}, {blue('MP:')} {bright_cyan(f'{character.current_mp}/{character.max_mp}')}")
        
        print(bright_cyan("="*50))
        
    def show_status_effects(self, character: Character):
        """상태 이상 효과 표시"""
        effects = []
        
        # 상처 상태
        if character.wounds > 0:
            wound_ratio = character.wounds / character.max_hp
            if wound_ratio > 0.5:
                effects.append("중상")
            elif wound_ratio > 0.25:
                effects.append("경상")
                
        # ATB 상태
        if character.atb_gauge >= 1000:
            effects.append("행동가능")
        elif character.atb_gauge >= 75:
            effects.append("준비중")
            
        if effects:
            effect_str = " | ".join(effects)
            print(f"    상태: {effect_str}")
            
    def format_number(self, number: int) -> str:
        """숫자 포맷팅 (콤마 없음)"""
        return f"{number}"
        
    def show_inventory_grid(self, items: List, grid_width: int = 8):
        """인벤토리 그리드 표시"""
        print("+" + "---+" * grid_width)
        
        for row in range((len(items) + grid_width - 1) // grid_width):
            line = "|"
            for col in range(grid_width):
                idx = row * grid_width + col
                if idx < len(items):
                    item_char = items[idx].get_display_char() if hasattr(items[idx], 'get_display_char') else "?"
                    line += f" {item_char} |"
                else:
                    line += "   |"
            print(line)
            
            if row < (len(items) + grid_width - 1) // grid_width - 1:
                print("+" + "---+" * grid_width)
                
        print("+" + "---+" * grid_width)

    def show_main_menu(self):
        """메인 메뉴 표시"""
        self.clear_screen()
        
        # 게임 로고 및 메뉴 (통일된 스타일)
        print("="*50)
        print("        ⭐ D A W N   O F   S T E L L A R ⭐")
        print("                  별빛의 여명")
        print("="*50)
        print(bright_cyan("게임 로그라이크 던전 탐험 게임", True))
        print(f"   전술적 ATB 전투 시스템")
        print(f"   4인 파티 관리")
        print(f"   무한 던전 탐험")
        print(bright_white("게임이 곧 시작됩니다...", True))
