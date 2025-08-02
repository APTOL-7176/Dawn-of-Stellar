#!/usr/bin/env python3
"""
전투 데미지 비교 분석 시스템
플레이어 vs 적의 실제 데미지를 비교분석합니다.
"""

import random
from game.brave_combat import BraveCombatSystem
from game.character import Character
from game.new_skill_system import NewSkillSystem

class CombatAnalyzer:
    """전투 데미지 분석기"""
    
    def __init__(self):
        self.combat_system = BraveCombatSystem()
        self.skill_system = NewSkillSystem()
        
    def create_test_character(self, class_name: str, level: int = 10) -> Character:
        """테스트용 캐릭터 생성"""
        # 레벨에 따른 기본 스탯 계산
        base_hp = 800 + (level * 50)
        base_attack = 150 + (level * 10)
        base_magic = 120 + (level * 8)
        base_defense = 100 + (level * 6)
        base_speed = 80 + (level * 3)
        
        character = Character(
            name=f"테스트_{class_name}",
            character_class=class_name,
            max_hp=base_hp,
            physical_attack=base_attack,
            magic_attack=base_magic,
            physical_defense=base_defense,
            magic_defense=base_defense,
            speed=base_speed
        )
        
        # 초기 BRV 설정
        character.brave_points = getattr(character, 'int_brv', 1000)
        character.max_brave_points = getattr(character, 'max_brv', 3000)
        
        return character
    
    def create_test_enemy(self, level: int = 10):
        """테스트용 적 생성"""
        class TestEnemy:
            def __init__(self, level):
                self.name = f"레벨{level} 테스트몬스터"
                self.level = level
                self.max_hp = 1000 + (level * 60)
                self.current_hp = self.max_hp
                self.physical_attack = 140 + (level * 9)
                self.magic_attack = 110 + (level * 7)
                self.physical_defense = 90 + (level * 5)
                self.magic_defense = 90 + (level * 5)
                self.speed = 70 + (level * 2)
                self.brave_points = 800 + (level * 40)
                self.max_brave_points = 2500 + (level * 100)
                self.is_alive = True
                self.wounds = 0
                self.max_wounds = int(self.max_hp * 0.75)
                
                # 호환성을 위한 속성들
                self.attack = self.physical_attack
                self.defense = self.physical_defense
                
            def take_damage(self, damage):
                actual = min(damage, self.current_hp)
                self.current_hp -= actual
                if self.current_hp <= 0:
                    self.current_hp = 0
                    self.is_alive = False
                # 상처 추가
                self.wounds = min(self.wounds + int(actual * 0.25), self.max_wounds)
                return actual
                
            def heal(self, amount):
                healed = min(amount, self.max_hp - self.current_hp)
                self.current_hp += healed
                return healed
                
        return TestEnemy(level)
    
    def test_basic_attacks(self, attacker, target):
        """기본 공격 테스트"""
        print(f"\n📊 === {attacker.name} 기본 공격 분석 ===")
        
        # HP 복사 (원본 보존)
        original_hp = target.current_hp
        original_brv = target.brave_points
        
        results = {
            'brv_damage': 0,
            'hp_damage': 0,
            'brv_attack_count': 0,
            'hp_attack_count': 0
        }
        
        # BRV 공격 테스트 (10회)
        brv_damages = []
        for i in range(10):
            target.current_hp = original_hp
            target.brave_points = original_brv
            
            # 기본 BRV 공격 시뮬레이션
            if hasattr(attacker, 'character_class'):  # 플레이어
                brv_damage = int((attacker.physical_attack / target.physical_defense) * 400)
            else:  # 적
                brv_damage = int((attacker.physical_attack / target.physical_defense) * 350)
            
            brv_damages.append(brv_damage)
        
        avg_brv = sum(brv_damages) / len(brv_damages)
        results['brv_damage'] = int(avg_brv)
        
        # HP 공격 테스트 (브레이브 포인트 기반)
        hp_damages = []
        for i in range(10):
            target.current_hp = original_hp
            
            # 현재 브레이브 포인트로 HP 공격
            base_hp_damage = attacker.brave_points
            if hasattr(attacker, 'character_class'):  # 플레이어
                hp_damage = int(base_hp_damage * 1.2)
            else:  # 적
                hp_damage = int(base_hp_damage * 1.0)
            
            hp_damages.append(hp_damage)
        
        avg_hp = sum(hp_damages) / len(hp_damages)
        results['hp_damage'] = int(avg_hp)
        
        # 결과 출력
        print(f"  ⚡ 평균 BRV 데미지: {results['brv_damage']:,}")
        print(f"  💥 평균 HP 데미지: {results['hp_damage']:,} (현재 BRV: {attacker.brave_points:,} 기준)")
        print(f"  📈 공격력: {attacker.physical_attack:,} vs 방어력: {target.physical_defense:,}")
        print(f"  ⚖️ 공격/방어 비율: {attacker.physical_attack/target.physical_defense:.2f}")
        
        return results
    
    def test_character_skills(self, character, target):
        """캐릭터 스킬 테스트"""
        print(f"\n🎯 === {character.name} 스킬 분석 ===")
        
        try:
            skills = self.skill_system.get_class_skills(character.character_class)
            skill_results = []
            
            for skill in skills[:6]:  # 처음 6개 스킬만 테스트
                original_hp = target.current_hp
                original_brv = target.brave_points
                
                skill_name = skill.get('name', '알 수 없는 스킬')
                skill_type = skill.get('type')
                
                # 스킬 타입별 예상 데미지 계산
                estimated_damage = 0
                
                if skill.get('brv_power', 0) > 0:
                    brv_power = skill.get('brv_power', 100)
                    estimated_damage += int((character.physical_attack / target.physical_defense) * brv_power * 0.01)
                
                if skill.get('hp_power', 0) > 0:
                    hp_power = skill.get('hp_power', 100)
                    base_hp = character.brave_points * (hp_power / 100)
                    if hasattr(character, 'character_class'):
                        estimated_damage += int(base_hp * 1.2)
                    else:
                        estimated_damage += int(base_hp * 1.0)
                
                # MP 비용
                mp_cost = skill.get('mp_cost', 0)
                
                skill_results.append({
                    'name': skill_name,
                    'type': str(skill_type),
                    'estimated_damage': estimated_damage,
                    'mp_cost': mp_cost,
                    'brv_power': skill.get('brv_power', 0),
                    'hp_power': skill.get('hp_power', 0)
                })
                
                # 결과 출력
                damage_type = "BRV" if skill.get('brv_power', 0) > 0 else "HP" if skill.get('hp_power', 0) > 0 else "특수"
                print(f"  📋 {skill_name} ({damage_type})")
                print(f"     💀 예상 데미지: {estimated_damage:,}")
                print(f"     💧 MP 비용: {mp_cost}")
                if skill.get('brv_power', 0) > 0:
                    print(f"     ⚡ BRV 배율: {skill.get('brv_power')}%")
                if skill.get('hp_power', 0) > 0:
                    print(f"     💥 HP 배율: {skill.get('hp_power')}%")
                
                # 원상복구
                target.current_hp = original_hp
                target.brave_points = original_brv
            
            return skill_results
            
        except Exception as e:
            print(f"❌ 스킬 분석 중 오류: {e}")
            return []
    
    def run_full_comparison(self, player_class: str, level: int = 10):
        """전체 비교 분석 실행"""
        print("="*80)
        print(f"🏟️ 전투 데미지 비교 분석 - 레벨 {level}")
        print("="*80)
        
        # 캐릭터들 생성
        player = self.create_test_character(player_class, level)
        enemy = self.create_test_enemy(level)
        enemy_copy = self.create_test_enemy(level)
        
        print(f"\n👤 플레이어: {player.name}")
        print(f"   📊 스탯: HP{player.max_hp:,} | 공격{player.physical_attack:,} | 방어{player.physical_defense:,} | BRV{player.brave_points:,}")
        
        print(f"\n👹 적: {enemy.name}")
        print(f"   📊 스탯: HP{enemy.max_hp:,} | 공격{enemy.physical_attack:,} | 방어{enemy.physical_defense:,} | BRV{enemy.brave_points:,}")
        
        # 1. 플레이어 기본 공격 분석
        player_basic = self.test_basic_attacks(player, enemy_copy)
        
        # 2. 적 기본 공격 분석  
        enemy_basic = self.test_basic_attacks(enemy, player)
        
        # 3. 플레이어 스킬 분석
        player_skills = self.test_character_skills(player, enemy_copy)
        
        # 4. 비교 분석 결과
        self.print_comparison_summary(player_basic, enemy_basic, player_skills, player.name, enemy.name)
    
    def print_comparison_summary(self, player_basic, enemy_basic, player_skills, player_name, enemy_name):
        """비교 분석 결과 요약"""
        print("\n" + "="*80)
        print("📈 비교 분석 결과 요약")
        print("="*80)
        
        print(f"\n🥊 기본 공격 비교:")
        print(f"  👤 {player_name} BRV 공격: {player_basic['brv_damage']:,}")
        print(f"  👹 {enemy_name} BRV 공격: {enemy_basic['brv_damage']:,}")
        brv_ratio = player_basic['brv_damage'] / enemy_basic['brv_damage'] if enemy_basic['brv_damage'] > 0 else 0
        print(f"  ⚖️ BRV 공격 비율 (플레이어/적): {brv_ratio:.2f}")
        
        print(f"\n💥 HP 공격 비교:")
        print(f"  👤 {player_name} HP 공격: {player_basic['hp_damage']:,}")
        print(f"  👹 {enemy_name} HP 공격: {enemy_basic['hp_damage']:,}")
        hp_ratio = player_basic['hp_damage'] / enemy_basic['hp_damage'] if enemy_basic['hp_damage'] > 0 else 0
        print(f"  ⚖️ HP 공격 비율 (플레이어/적): {hp_ratio:.2f}")
        
        if player_skills:
            print(f"\n🎯 {player_name} 최강 스킬 TOP 3:")
            sorted_skills = sorted(player_skills, key=lambda x: x['estimated_damage'], reverse=True)
            for i, skill in enumerate(sorted_skills[:3], 1):
                efficiency = skill['estimated_damage'] / max(skill['mp_cost'], 1)
                print(f"  {i}. {skill['name']}")
                print(f"     💀 데미지: {skill['estimated_damage']:,}")
                print(f"     💧 MP: {skill['mp_cost']} (효율: {efficiency:.1f})")
        
        print(f"\n🎖️ 종합 평가:")
        if brv_ratio > 1.5:
            print("  ⚡ BRV 공격: 플레이어 압도적 우세")
        elif brv_ratio > 1.2:
            print("  ⚡ BRV 공격: 플레이어 우세")
        elif brv_ratio > 0.8:
            print("  ⚡ BRV 공격: 균형")
        else:
            print("  ⚡ BRV 공격: 적 우세")
            
        if hp_ratio > 1.5:
            print("  💥 HP 공격: 플레이어 압도적 우세")
        elif hp_ratio > 1.2:
            print("  💥 HP 공격: 플레이어 우세")
        elif hp_ratio > 0.8:
            print("  💥 HP 공격: 균형")
        else:
            print("  💥 HP 공격: 적 우세")


def main():
    """메인 실행 함수"""
    analyzer = CombatAnalyzer()
    
    # 테스트할 직업들
    test_classes = ['전사', '철학자', '아크메이지', '성기사', '도적']
    
    for class_name in test_classes:
        try:
            analyzer.run_full_comparison(class_name, level=10)
            print("\n" + "🔄 다음 분석을 위해 Enter를 누르세요...")
            input()
        except Exception as e:
            print(f"❌ {class_name} 분석 중 오류: {e}")
            continue


if __name__ == "__main__":
    main()
