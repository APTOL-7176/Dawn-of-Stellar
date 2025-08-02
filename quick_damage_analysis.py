#!/usr/bin/env python3
"""
전투 데미지 비교 분석 시스템 - 전체 직업 자동 분석
"""

import random
from game.brave_combat import BraveCombatSystem
from game.character import Character
from game.new_skill_system import NewSkillSystem

class QuickCombatAnalyzer:
    """빠른 전투 데미지 분석기"""
    
    def __init__(self):
        self.combat_system = BraveCombatSystem()
        self.skill_system = NewSkillSystem()
        
    def create_test_character(self, class_name: str, level: int = 10) -> Character:
        """테스트용 캐릭터 생성"""
        base_hp = 800 + (level * 50)
        base_attack = 150 + (level * 10)
        base_magic = 120 + (level * 8)
        base_defense = 100 + (level * 6)
        base_speed = 80 + (level * 3)
        
        character = Character(
            name=f"{class_name}",
            character_class=class_name,
            max_hp=base_hp,
            physical_attack=base_attack,
            magic_attack=base_magic,
            physical_defense=base_defense,
            magic_defense=base_defense,
            speed=base_speed
        )
        
        character.brave_points = getattr(character, 'int_brv', 1000)
        character.max_brave_points = getattr(character, 'max_brv', 3000)
        
        return character
    
    def create_test_enemy(self, level: int = 10):
        """테스트용 적 생성"""
        class TestEnemy:
            def __init__(self, level):
                self.name = f"Lv{level}몬스터"
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
                self.attack = self.physical_attack
                self.defense = self.physical_defense
                
            def take_damage(self, damage):
                actual = min(damage, self.current_hp)
                self.current_hp -= actual
                if self.current_hp <= 0:
                    self.current_hp = 0
                    self.is_alive = False
                self.wounds = min(self.wounds + int(actual * 0.25), self.max_wounds)
                return actual
                
        return TestEnemy(level)
    
    def calculate_basic_damage(self, attacker, target):
        """기본 공격 데미지 계산 - 실제 게임 시스템 기반"""
        from game.balance import GameBalance
        
        # BRV 공격 데미지 - 실제 게임 시스템 사용
        brv_damage = GameBalance.calculate_brave_damage(
            attacker.physical_attack, 
            target.physical_defense, 
            1.0  # 기본 공격 배율
        )
        
        # HP 공격 데미지 (현재 BRV 기준) - 실제 게임 시스템 기반
        base_hp_damage = attacker.brave_points
        from game.balance import GameBalance
        
        # 새로운 계산 방식 적용
        if hasattr(attacker, 'character_class'):  # 플레이어
            hp_damage = int(base_hp_damage * 0.5 * 0.8 * GameBalance.HP_DAMAGE_MULTIPLIER * 10)
        else:  # 적
            hp_damage = int(base_hp_damage * 0.5 * 0.7 * GameBalance.HP_DAMAGE_MULTIPLIER * 10)
        
        return brv_damage, hp_damage
    
    def analyze_character_skills(self, character):
        """캐릭터 스킬 분석"""
        try:
            skills = self.skill_system.get_class_skills(character.character_class)
            skill_analysis = []
            
            for skill in skills[:6]:
                skill_name = skill.get('name', '알 수 없는 스킬')
                skill_type = skill.get('type')
                
                # 데미지 추정
                estimated_damage = 0
                damage_type = "특수"
                
                if skill.get('brv_power', 0) > 0:
                    brv_power = skill.get('brv_power', 100)
                    estimated_damage = int((character.physical_attack / 140) * brv_power * 4)  # 표준 방어력 140 기준
                    damage_type = "BRV"
                
                if skill.get('hp_power', 0) > 0:
                    hp_power = skill.get('hp_power', 100)
                    base_hp = character.brave_points * (hp_power / 100)
                    estimated_damage = int(base_hp * 1.2)  # 플레이어 배율
                    damage_type = "HP"
                
                mp_cost = skill.get('mp_cost', 0)
                efficiency = estimated_damage / max(mp_cost, 1)
                
                skill_analysis.append({
                    'name': skill_name,
                    'type': damage_type,
                    'damage': estimated_damage,
                    'mp_cost': mp_cost,
                    'efficiency': efficiency
                })
            
            return skill_analysis
        except:
            return []
    
    def run_quick_analysis(self):
        """빠른 전체 분석"""
        print("="*90)
        print("🏟️ 전투 데미지 비교 분석 - 레벨 10 (전직업 요약)")
        print("="*90)
        
        # 테스트할 직업들
        test_classes = ['전사', '검성', '용기사', '암흑기사', '검투사', '광전사', '사무라이',
                       '아크메이지', '네크로맨서', '정령술사', '시간술사', '철학자',
                       '성기사', '기사', '성직자', '도적', '암살자', '궁수', '몽크']
        
        enemy = self.create_test_enemy(10)
        
        print(f"🎯 기준 적: {enemy.name}")
        print(f"📊 적 스탯: HP{enemy.max_hp:,} | 공격{enemy.physical_attack:,} | 방어{enemy.physical_defense:,} | BRV{enemy.brave_points:,}")
        print("\n" + "-"*90)
        
        enemy_brv, enemy_hp = self.calculate_basic_damage(enemy, self.create_test_character('전사', 10))
        
        print(f"👹 적 기본 데미지: BRV {enemy_brv:,} | HP {enemy_hp:,}")
        print("\n" + "="*90)
        print("📋 직업별 분석 결과")
        print("="*90)
        
        results = []
        
        for class_name in test_classes:
            try:
                player = self.create_test_character(class_name, 10)
                player_brv, player_hp = self.calculate_basic_damage(player, enemy)
                skills = self.analyze_character_skills(player)
                
                # 최고 데미지 스킬 찾기
                best_skill = max(skills, key=lambda x: x['damage']) if skills else None
                
                # BRV 스탯 정보
                int_brv = getattr(player, 'int_brv', 'N/A')
                max_brv = getattr(player, 'max_brv', 'N/A')
                
                results.append({
                    'class': class_name,
                    'brv_damage': player_brv,
                    'hp_damage': player_hp,
                    'int_brv': int_brv,
                    'max_brv': max_brv,
                    'best_skill': best_skill,
                    'brv_ratio': player_brv / enemy_brv if enemy_brv > 0 else 0,
                    'hp_ratio': player_hp / enemy_hp if enemy_hp > 0 else 0
                })
                
                # 결과 출력
                brv_vs_enemy = f"{player_brv/enemy_brv:.2f}x" if enemy_brv > 0 else "N/A"
                hp_vs_enemy = f"{player_hp/enemy_hp:.2f}x" if enemy_hp > 0 else "N/A"
                
                print(f"🏷️ {class_name:8} | BRV: {player_brv:4,} ({brv_vs_enemy:>5}) | HP: {player_hp:4,} ({hp_vs_enemy:>5}) | INT/MAX BRV: {int_brv:4}/{max_brv:4}", end="")
                
                if best_skill and best_skill['damage'] > 0:
                    print(f" | 최강스킬: {best_skill['name']} ({best_skill['damage']:,})")
                else:
                    print(" | 최강스킬: 특수효과형")
                    
            except Exception as e:
                print(f"❌ {class_name}: 분석 실패 ({e})")
                continue
        
        # 종합 통계
        print("\n" + "="*90)
        print("📊 종합 통계")
        print("="*90)
        
        if results:
            # BRV 공격 순위
            brv_ranking = sorted(results, key=lambda x: x['brv_damage'], reverse=True)
            print("🥇 BRV 공격력 TOP 5:")
            for i, result in enumerate(brv_ranking[:5], 1):
                print(f"  {i}. {result['class']:8} : {result['brv_damage']:,} (적 대비 {result['brv_ratio']:.2f}배)")
            
            # HP 공격 순위
            hp_ranking = sorted(results, key=lambda x: x['hp_damage'], reverse=True)
            print("\n🥇 HP 공격력 TOP 5:")
            for i, result in enumerate(hp_ranking[:5], 1):
                print(f"  {i}. {result['class']:8} : {result['hp_damage']:,} (적 대비 {result['hp_ratio']:.2f}배)")
            
            # INT BRV 순위
            int_brv_ranking = sorted([r for r in results if isinstance(r['int_brv'], int)], 
                                   key=lambda x: x['int_brv'], reverse=True)
            print("\n💎 초기 BRV TOP 5:")
            for i, result in enumerate(int_brv_ranking[:5], 1):
                print(f"  {i}. {result['class']:8} : {result['int_brv']:,}")
            
            # MAX BRV 순위
            max_brv_ranking = sorted([r for r in results if isinstance(r['max_brv'], int)], 
                                   key=lambda x: x['max_brv'], reverse=True)
            print("\n💎 최대 BRV TOP 5:")
            for i, result in enumerate(max_brv_ranking[:5], 1):
                print(f"  {i}. {result['class']:8} : {result['max_brv']:,}")
            
            # 밸런스 분석
            print("\n⚖️ 밸런스 분석:")
            avg_brv_ratio = sum(r['brv_ratio'] for r in results) / len(results)
            avg_hp_ratio = sum(r['hp_ratio'] for r in results) / len(results)
            
            print(f"  📈 평균 BRV 공격비 (플레이어/적): {avg_brv_ratio:.2f}")
            print(f"  📈 평균 HP 공격비 (플레이어/적): {avg_hp_ratio:.2f}")
            
            if avg_brv_ratio > 1.5:
                print("  🔥 BRV 전투: 플레이어 압도적 유리")
            elif avg_brv_ratio > 1.2:
                print("  ✅ BRV 전투: 플레이어 유리")
            elif avg_brv_ratio > 0.8:
                print("  ⚖️ BRV 전투: 균형")
            else:
                print("  ⚠️ BRV 전투: 적 유리")
                
            if avg_hp_ratio > 1.5:
                print("  🔥 HP 전투: 플레이어 압도적 유리")
            elif avg_hp_ratio > 1.2:
                print("  ✅ HP 전투: 플레이어 유리")
            elif avg_hp_ratio > 0.8:
                print("  ⚖️ HP 전투: 균형")
            else:
                print("  ⚠️ HP 전투: 적 유리")


def main():
    analyzer = QuickCombatAnalyzer()
    analyzer.run_quick_analysis()


if __name__ == "__main__":
    main()
