"""
게임 디스플레이 시스템
ASCII 기반 그래픽 표시
"""

from typing import List
import os
import platform
from game.character import Character, PartyManager
from game.ui_formatters import format_item_brief
from game.world import GameWorld
from game.color_text import *


class GameDisplay:
    """터미널 표시 유틸리티 (필요 메서드 최소 구현)
    - show_party_status: 파티 상태를 안전하게 출력
    - clear_screen: 플랫폼별 화면 클리어
    """
    
    def __init__(self):
        """GameDisplay 초기화 - 로-바트 마스터 연결"""
        # 화면 크기 기본값 설정
        self.screen_width = 120
        self.screen_height = 60
        
        self.robart = None
        try:
            # 전역 로-바트 인스턴스 찾기
            global robart
            self.robart = robart
        except Exception:
            try:
                # 로-바트 마스터 생성
                self.robart = RobotAIMaster()
            except Exception:
                pass  # 로-바트 없어도 동작

    def clear_screen(self):
        try:
            # PowerShell/Windows Terminal ANSI 우선
            try:
                print("\033[2J\033[H", end="")
                return
            except Exception:
                pass
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
        except Exception:
            # 최후의 수단: 빈 줄로 밀어내기
            for _ in range(50):
                print()

    def show_party_status(self, party_manager: PartyManager, world: GameWorld = None):
        """상세한 파티 상태 표시 (완전한 정보 제공)"""
        try:
            from game.color_text import bright_cyan, bright_yellow, bright_green, cyan, bright_red, bright_magenta
        except Exception:
            # 컬러가 없어도 동작
            def bright_cyan(x): return x
            def bright_yellow(x): return x
            def bright_green(x): return x
            def cyan(x): return x
            def bright_red(x): return x
            def bright_magenta(x): return x
        
        # party_manager None 체크
        if not party_manager:
            print("❌ 파티 매니저가 없습니다.")
            return
            
        # members 속성 확인
        if not hasattr(party_manager, 'members') or not party_manager.members:
            print("❌ 파티 멤버가 없습니다.")
            return
        
        try:
            print("\n" + "="*70)
            print(f"{'🎭 파티 상태 (상세 정보)':^70}")
            print("="*70)
            
            for i, member in enumerate(party_manager.members, 1):
                if not member:
                    continue
                    
                # 기본 정보
                name = getattr(member, 'name', f'멤버{i}')
                character_class = getattr(member, 'character_class', '알 수 없음')
                level = getattr(member, 'level', 1)
                
                # 체력/마나 정보
                current_hp = getattr(member, 'current_hp', 0)
                max_hp = getattr(member, 'max_hp', 1)
                current_mp = getattr(member, 'current_mp', 0)
                max_mp = getattr(member, 'max_mp', 1)
                is_alive = getattr(member, 'is_alive', True)
                
                # BRV 정보
                brv = getattr(member, 'brv', 0)
                int_brv = getattr(member, 'int_brv', 0)
                
                # 상처 시스템
                wounds = getattr(member, 'wounds', 0)
                
                # ATB 게이지
                atb_gauge = getattr(member, 'atb_gauge', 0)
                
                # 경험치
                experience = getattr(member, 'experience', 0)
                
                # 스탯 정보
                strength = getattr(member, 'strength', 0)
                defense = getattr(member, 'defense', 0)
                magic = getattr(member, 'magic', 0)
                magic_defense = getattr(member, 'magic_defense', 0)
                speed = getattr(member, 'speed', 0)
                luck = getattr(member, 'luck', 0)
                
                # 상태 표시
                status_color = bright_green if is_alive else bright_red
                status = status_color("생존" if is_alive else "전투불능")
                
                # HP/MP 백분율
                hp_percent = int((current_hp / max_hp) * 100) if max_hp > 0 else 0
                mp_percent = int((current_mp / max_mp) * 100) if max_mp > 0 else 0
                atb_percent = int((atb_gauge / 2000) * 100) if atb_gauge else 0
                
                # HP 색상 결정
                if hp_percent >= 75:
                    hp_color = bright_green
                elif hp_percent >= 50:
                    hp_color = bright_yellow
                elif hp_percent >= 25:
                    hp_color = bright_cyan
                else:
                    hp_color = bright_red
                
                # MP 색상 결정
                if mp_percent >= 75:
                    mp_color = bright_cyan
                elif mp_percent >= 50:
                    mp_color = bright_yellow
                else:
                    mp_color = bright_red
                
                print(f"\n📋 {i}. {bright_cyan(name)} (Lv.{level} {character_class}) - {status}")
                print(f"├─ 💗 HP: {hp_color(f'{current_hp}/{max_hp}')} ({hp_percent}%)")
                if wounds > 0:
                    print(f"├─ 🩸 상처: {bright_red(str(wounds))} (영구 피해)")
                print(f"├─ 💙 MP: {mp_color(f'{current_mp}/{max_mp}')} ({mp_percent}%)")
                print(f"├─ ⚡ BRV: {bright_yellow(str(brv))} (기본: {int_brv})")
                print(f"├─ ⏱️ ATB: {bright_magenta(f'{atb_gauge}/2000')} ({atb_percent}%)")
                print(f"├─ 🌟 EXP: {experience}")
                print(f"├─ 📊 스탯: STR:{strength} DEF:{defense} MAG:{magic} MDEF:{magic_defense} SPD:{speed} LUK:{luck}")
                
                # 장비 정보
                if hasattr(member, 'equipped_weapon') and member.equipped_weapon:
                    weapon_name = getattr(member.equipped_weapon, 'name', '무기')
                    print(f"├─ ⚔️ 무기: {weapon_name}")
                
                if hasattr(member, 'equipped_armor') and member.equipped_armor:
                    armor_name = getattr(member.equipped_armor, 'name', '방어구')
                    print(f"├─ 🛡️ 방어구: {armor_name}")
                
                # 상태이상
                if hasattr(member, 'status_effects') and member.status_effects:
                    effects = ", ".join([str(effect) for effect in member.status_effects])
                    print(f"├─ 🔮 상태: {effects}")
                
                # 특성
                if hasattr(member, 'active_traits') and member.active_traits:
                    traits = ", ".join([trait.get('name', str(trait)) if isinstance(trait, dict) else str(trait) for trait in member.active_traits[:3]])
                    if len(member.active_traits) > 3:
                        traits += f" 외 {len(member.active_traits)-3}개"
                    print(f"└─ ✨ 특성: {traits}")
                else:
                    print("└─ ✨ 특성: 없음")
                
                    # 🤖 로-바트 종합 캐릭터 분석 (모든 기능 활용)
                    try:
                        print("🤖 로-바트의 종합 분석")
                        print("─" * 30)
                        
                        # 기본 캐릭터 분석
                        basic_analysis = self.get_robat_character_analysis(member)
                        if basic_analysis:
                            print(f"📊 기본 분석: {basic_analysis}")
                        
                        # 스킬 분석 (로-바트 마스터 활용)
                        if self.robart and hasattr(self.robart, 'get_robart_skill_analysis'):
                            try:
                                skill_analysis = self.robart.get_robart_skill_analysis(member)
                                if skill_analysis:
                                    print(f"⚔️ 스킬 분석: {skill_analysis}")
                            except:
                                pass
                        
                        # 궁극기 분석
                        try:
                            ultimate_analysis = self.get_robart_ultimate_analysis(member)
                            if ultimate_analysis:
                                print(f"💥 궁극기 분석: {ultimate_analysis}")
                        except:
                            pass
                        
                        # 성장 분석
                        try:
                            progression_analysis = self.get_robart_progression_analysis(member)
                            if progression_analysis:
                                print(f"📈 성장 분석: {progression_analysis}")
                        except:
                            pass
                        
                        # 전투 추천
                        try:
                            battle_advice = self.get_robart_battle_commander(member)
                            if battle_advice:
                                print(f"🎯 전투 추천: {battle_advice}")
                        except:
                            pass
                            
                    except Exception as e:
                        print(f"🤖 로-바트 분석 오류: {e}")
                
            print("="*70)
            
            # 🤖 로-바트 파티 종합 분석 & 추천 (모든 기능 활용)
            try:
                print(f"\n{bright_cyan('🤖 로-바트의 파티 종합 분석 & 추천')}")
                print("=" * 70)
                
                # 기본 파티 분석
                party_analysis = self.get_robat_party_analysis(party_manager)
                if party_analysis:
                    print(f"📊 기본 파티 분석:\n{party_analysis}")
                
                # 전체 파티 분석 (로-바트 마스터)
                if self.robart:
                    try:
                        # 전체 분석
                        if hasattr(self.robart, 'get_robart_full_analysis'):
                            full_analysis = self.robart.get_robart_full_analysis(party_manager.members)
                            if full_analysis:
                                print(f"\n🔍 전체 분석:\n{full_analysis}")
                        
                        # 기본 추천
                        if hasattr(self.robart, 'get_robart_basic_recommendation'):
                            basic_rec = self.robart.get_robart_basic_recommendation(party_manager.members)
                            if basic_rec:
                                print(f"\n💡 기본 추천:\n{basic_rec}")
                        
                        # 요리 분석
                        if hasattr(self.robart, 'get_robart_cooking_analysis'):
                            cooking_analysis = self.robart.get_robart_cooking_analysis(party_manager.members)
                            if cooking_analysis:
                                print(f"\n🍽️ 요리 추천:\n{cooking_analysis}")
                                
                        # 로-바트의 한마디
                        if hasattr(self.robart, 'robart_says'):
                            robat_comment = self.robart.robart_says()
                            if robat_comment:
                                print(f"\n🗨️ 로-바트: {robat_comment}")
                                
                    except Exception as e:
                        print(f"로-바트 마스터 분석 오류: {e}")
                        
            except Exception as e:
                print(f"🤖 로-바트 파티 분석 오류: {e}")
                pass  # 파티 분석 실패 시 조용히 넘어감
                
        except Exception as display_error:
            print(f"❌ 파티 상태 표시 중 오류: {display_error}")
            # 폴백: 간단한 표시
            try:
                print("\n🎭 파티 정보 (간단 버전)")
                for i, member in enumerate(party_manager.members, 1):
                    if member:
                        name = getattr(member, 'name', f'멤버{i}')
                        hp = getattr(member, 'current_hp', 0)
                        max_hp = getattr(member, 'max_hp', 1)
                        is_alive = getattr(member, 'is_alive', True)
                        status = "생존" if is_alive else "전투불능"
                        print(f"{i}. {name} - {status} (HP: {hp}/{max_hp})")
            except Exception:
                print("❌ 파티 정보를 표시할 수 없습니다.")
            def bright_green(x):
                return x
            def cyan(x):
                return x

        try:
            self.clear_screen()
            title = "👥 파티 상태"
            print("")
            print("=" * 60)
            print(f"{title:^60}")
            print("=" * 60)

            if not party_manager or not getattr(party_manager, 'members', None):
                print("파티 정보가 없습니다.")
                return

            # 현재 층 정보(있으면 표시)
            try:
                if world and hasattr(world, 'current_level'):
                    print(f"현재 층수: {getattr(world, 'current_level', 1)}층")
            except Exception:
                pass

            for i, member in enumerate(party_manager.members, 1):
                try:
                    name = getattr(member, 'name', f'멤버{i}')
                    clazz = getattr(member, 'character_class', '모험가')
                    chp = getattr(member, 'current_hp', getattr(member, 'hp', 0))
                    mhp = getattr(member, 'max_hp', 0)
                    cmp_ = getattr(member, 'current_mp', getattr(member, 'mp', 0))
                    mmp = getattr(member, 'max_mp', 0)
                    brv = getattr(member, 'brave_points', 0)
                    wounds = getattr(member, 'wounds', 0)

                    print("")
                    print(bright_yellow(f"👤 {i}. {name}") + f" ({clazz})")
                    print(f" - HP: {chp}/{mhp}  |  MP: {cmp_}/{mmp}  |  BRV: {brv}")
                    if wounds:
                        print(f" - 상처: {wounds}")

                    # 간단 장비 요약 (안전한 포맷터 사용)
                    eq_summary = []
                    try:
                        weapon = getattr(member, 'weapon', None) or getattr(member, 'equipped_weapon', None)
                        armor = getattr(member, 'armor', None) or getattr(member, 'equipped_armor', None)
                        acc = None
                        for key in ['accessory1', 'accessory2', 'accessory3', 'equipped_accessory']:
                            val = getattr(member, key, None)
                            if val:
                                acc = val
                                break
                        
                        # 안전한 아이템 포맷팅
                        def safe_format_item(item):
                            if not item:
                                return "없음"
                            try:
                                if callable(format_item_brief):
                                    return format_item_brief(item)
                                else:
                                    # format_item_brief가 None이거나 호출 불가능한 경우 대체
                                    if isinstance(item, dict):
                                        return item.get('name', '알 수 없는 아이템')
                                    elif hasattr(item, 'name'):
                                        return getattr(item, 'name', '알 수 없는 아이템')
                                    else:
                                        return str(item)
                            except Exception:
                                # 모든 예외에 대한 안전한 대안
                                if isinstance(item, dict):
                                    return item.get('name', '알 수 없는 아이템')
                                elif hasattr(item, 'name'):
                                    return getattr(item, 'name', '알 수 없는 아이템')
                                else:
                                    return "장비 있음"
                        
                        if weapon:
                            eq_summary.append(f"🗡️ {safe_format_item(weapon)}")
                        if armor:
                            eq_summary.append(f"🛡️ {safe_format_item(armor)}")
                        if acc:
                            eq_summary.append(f"💍 {safe_format_item(acc)}")
                    except Exception:
                        pass
                    if eq_summary:
                        print(" - 장비: " + ", ".join(eq_summary))
                except Exception as _:
                    print(f" - 정보를 불러올 수 없습니다.")

            print("")
            print("=" * 60)
        except Exception as e:
            print(f"❌ 파티 상태 표시 오류: {e}")

    # 🤖 로-바트 분석 메서드들 (GameDisplay 전용)
    def get_robat_character_analysis(self, character):
        """로-바트의 캐릭터 분석"""
        try:
            if self.robart and hasattr(self.robart, 'analyze_character_status'):
                return self.robart.analyze_character_status(character)
            else:
                # 간단 분석 버전
                name = getattr(character, 'name', '모험가')
                hp_ratio = getattr(character, 'current_hp', 100) / getattr(character, 'max_hp', 100)
                if hp_ratio > 0.8:
                    return f"{name} - 최고 컨디션! 로-바트가 인정하는 실력자!"
                elif hp_ratio > 0.5:
                    return f"{name} - 괜찮은 상태. 로-바트의 조언을 들어보세요!"
                else:
                    return f"{name} - 위험! 로-바트가 즉시 회복을 권장합니다!"
        except Exception:
            return "로-바트 분석 시스템 일시 오류"

    def get_robat_party_analysis(self, party_manager):
        """로-바트의 파티 분석"""
        try:
            if self.robart and hasattr(self.robart, 'analyze_party_comprehensive'):
                return self.robart.analyze_party_comprehensive(party_manager.members)
            else:
                # 간단 분석 버전
                member_count = len(party_manager.members)
                avg_hp = sum(getattr(m, 'current_hp', 100) / getattr(m, 'max_hp', 100) for m in party_manager.members) / member_count
                
                if avg_hp > 0.8:
                    return f"로-바트 분석: {member_count}명의 완벽한 파티! 모든 멤버가 최상의 컨디션입니다!"
                elif avg_hp > 0.5:
                    return f"로-바트 분석: {member_count}명의 안정적인 파티. 일부 조정이 필요하지만 전반적으로 좋습니다."
                else:
                    return f"로-바트 분석: {member_count}명의 파티가 위험 상태! 즉시 회복과 재정비가 필요합니다!"
        except Exception:
            return "로-바트 파티 분석 시스템 일시 오류"

    def get_robart_ultimate_analysis(self, character):
        """로-바트의 궁극 분석"""
        try:
            if self.robart and hasattr(self.robart, 'get_ultimate_analysis_suite'):
                # 캐릭터를 리스트로 감싸서 전달 (RobotAIMaster가 파티 리스트를 기대함)
                return self.robart.get_ultimate_analysis_suite([character], None, "CHARACTER")
            else:
                level = getattr(character, 'level', 1)
                character_class = getattr(character, 'character_class', '모험가')
                return f"레벨 {level} {character_class}의 궁극 분석: 로-바트가 인정하는 성장형 캐릭터!"
        except Exception as e:
            return f"궁극 분석 오류: {e}"

    def get_robart_progression_analysis(self, character):
        """로-바트의 성장 분석"""
        try:
            level = getattr(character, 'level', 1)
            if level < 5:
                return "초보 단계 - 로-바트가 기본기 연마를 추천!"
            elif level < 10:
                return "성장 단계 - 로-바트가 특화 능력 개발을 추천!"
            else:
                return "고수 단계 - 로-바트도 인정하는 실력자!"
        except Exception:
            return "성장 분석 오류"

    def get_robart_battle_commander(self, character):
        """로-바트의 전투 지휘"""
        try:
            hp_ratio = getattr(character, 'current_hp', 100) / getattr(character, 'max_hp', 100)
            if hp_ratio > 0.7:
                return "공격적 전술 권장 - 로-바트의 승리 공식!"
            elif hp_ratio > 0.3:
                return "신중한 전술 권장 - 로-바트의 안전 우선 전략!"
            else:
                return "즉시 후퇴 권장 - 로-바트의 생존 최우선 원칙!"
        except Exception:
            return "전투 지휘 오류"

    def show_game_screen(self, party_manager, world, cooking_system=None):
        """메인 게임 화면 표시 - 풍부한 파티 정보 포함 버전"""
        from game.color_text import bright_cyan, bright_green, green, yellow, red, cyan, bright_yellow, bright_red
        import os
        
        try:
            # 화면 크기 안전하게 설정 (더 넓게)
            safe_width = min(120, max(60, self.screen_width))  # 최소 60, 최대 120자
            safe_height = min(60, max(30, self.screen_height))  # 최소 30, 최대 60줄

            # 화면 클리어 (한 번만)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # 상단 정보 표시
            title = f"차원 공간 {world.current_level}층 - Dawn Of Stellar"
            title_padding = max(0, (safe_width - len(title)) // 2)
            print(f"{' ' * title_padding}{bright_cyan(title)}")
            print()
            
            # 차원 공간 맵 표시 (개선된 크기)
            if hasattr(world, 'get_colored_map_display'):
                # 맵 크기를 적절하게 설정
                map_width = min(40, safe_width - 10)  # 맵 너비 축소 (50 -> 30)
                map_height = min(18, safe_height - 22)  # 맵 높이: 더 줄임 (28 -> 18)
                map_display = world.get_colored_map_display(map_width, map_height)
                
                if map_display and isinstance(map_display, list):
                    for line in map_display:
                        if line and isinstance(line, str):
                            # 맵 라인을 왼쪽 정렬로 출력
                            print(line)
                else:
                    # 백업 맵 표시
                    print("🗺️  차원 공간 지도를 불러올 수 없습니다")
            else:
                print("🗺️  차원 공간 탐험 중...")
            
            print()  # 맵과 파티 상태 사이 여백
            
            # 메인 게임 화면의 파티 상태 정보 표시
            if party_manager and hasattr(party_manager, 'members'):
                alive_members = [m for m in party_manager.members if m.is_alive]
                if alive_members:
                    # 파티 상태 정보
                    alive_count = len(party_manager.get_alive_members())
                    total_count = len(party_manager.members)
                    
                    party_info = f"파티: {alive_count}/{total_count}명 생존 | 층: {world.current_level}"
                    
                    # 골드 정보 안전하게 표시
                    try:
                        gold_info = f" | 골드: {party_manager.party_gold}G"
                    except Exception:
                        gold_info = " | 골드: 0G"
                    
                    # 가방 정보 안전하게 표시 (파티원 인벤토리 + 요리 재료)
                    try:
                        total_weight = 0.0
                        max_weight = 0.0
                        
                        # 파티원들의 인벤토리 무게 계산
                        for member in party_manager.members:
                            if hasattr(member, 'inventory'):
                                total_weight += member.inventory.get_total_weight()
                                max_weight += member.inventory.max_weight
                        
                        # 요리 시스템 무게 추가
                        if cooking_system:
                            cooking_weight = cooking_system.get_total_inventory_weight()
                            total_weight += cooking_weight
                        
                        if max_weight > 0:
                            # 무게 비율에 따른 색상 적용 (현재 무게에만)
                            weight_ratio = total_weight / max_weight
                            if weight_ratio < 0.5:  # 50% 미만: 밝은 청록색 (매우 여유)
                                weight_color = "\033[96m"  # 밝은 청록색
                            elif weight_ratio < 0.7:  # 70% 미만: 초록색 (여유)
                                weight_color = "\033[92m"  # 밝은 초록
                            elif weight_ratio < 0.85:  # 85% 미만: 노란색 (주의)
                                weight_color = "\033[93m"  # 노란색
                            elif weight_ratio < 0.95:  # 95% 미만: 주황색 (경고)
                                weight_color = "\033[38;5;208m"  # 주황색 (256색)
                            else:  # 95% 이상: 빨간색 (위험)
                                weight_color = "\033[91m"  # 빨간색
                            
                            reset_color = "\033[0m"
                            weight_info = f" | 가방: {weight_color}{total_weight:.1f}{reset_color}/{max_weight:.1f}kg"
                        else:
                            weight_info = ""
                    except Exception as e:
                        weight_info = ""
                    
                    print(f"  {party_info}{gold_info}{weight_info}")
                    print("+" + "-" * (safe_width - 10) + "+")
                    
                    # 파티원 상태 표시 (최대 4명)
                    for member in party_manager.members[:4]:
                        if member.is_alive:
                            # HP/MP 비율 계산
                            hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                            mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                            
                            # HP 색상 결정
                            if hp_ratio >= 0.8:
                                hp_color = bright_green; hp_emoji = "💚"
                            elif hp_ratio >= 0.6:
                                hp_color = green; hp_emoji = "💛"
                            elif hp_ratio >= 0.4:
                                hp_color = yellow; hp_emoji = "🧡"
                            elif hp_ratio >= 0.2:
                                hp_color = bright_red; hp_emoji = "❤️"
                            else:
                                hp_color = red; hp_emoji = "💔"
                            
                            mp_color = bright_cyan if mp_ratio >= 0.8 else cyan
                            mp_emoji = "💙"
                            
                            # 직업 이모지
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
                            
                            name_class = f"{class_emoji} {member.name[:10]:10} ({member.character_class[:8]:8})"
                            hp_text = f"{hp_emoji}HP:{hp_color(f'{member.current_hp:3}/{member.max_hp:3}')}"
                            mp_text = f"{mp_emoji}MP:{mp_color(f'{member.current_mp:2}/{member.max_mp:2}')}"
                            print(f"    {name_class} {hp_text} {mp_text}")
                        else:
                            name_class = f"💀 {member.name[:10]:10} ({member.character_class[:8]:8})"
                            print(f"    {name_class} {red('사망')}")

                    print("+" + "-" * (safe_width - 10) + "+")
                    print()
                    print(f"🎮 조작키 | WASD:이동 | I:인벤토리 | F:메뉴 | P:파티 | H:도움말")
                    print()
                    
                    # 게임 정보 표시
                    try:
                        print(f"📊 {bright_cyan('게임 정보')}")
                        
                        # 파티 전투력 계산
                        alive_members = party_manager.get_alive_members()
                        if alive_members:
                            combat_powers = [calculate_combat_power(char) for char in alive_members]
                            avg_combat_power = sum(combat_powers) // len(combat_powers)
                            
                            # 전투력 색상 평가
                            expected_power = world.current_level * 15
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
                        
                        total_gold = sum(getattr(char, 'gold', 0) for char in party_manager.members)
                        print(f"│ 파티: {alive_count}/{len(party_manager.members)}명 생존 | 전투력: {avg_combat_power} ({power_status})")
                        
                        # AI 추천 행동 (로-바트)
                        ai_recommendation = get_ai_recommendation(party_manager, world)
                        print(f"│   로-바트: {ai_recommendation}")
                        
                        # 진행도
                        progress = min(100, (world.current_level / 10) * 100)
                        progress_bar = "█" * int(progress // 10) + "░" * (10 - int(progress // 10))
                        print(f"│ 진행도: [{progress_bar}] {progress:.1f}%")
                        
                        # 위치 정보
                        if hasattr(world, 'player_pos') and world.player_pos:
                            pos_x, pos_y = world.player_pos
                            print(f"📍 위치: ({pos_x}, {pos_y}) | 🗺️ 층: {world.current_level} | 🎯 목표: 계단 찾아 다음 층으로!")
                        
                    except Exception as e:
                        print(f"│ 게임 정보 표시 오류: {e}")
                    
                    # 메시지 버퍼 표시
                    if hasattr(world, 'game') and world.game and hasattr(world.game, 'get_recent_messages'):
                        try:
                            messages = world.game.get_recent_messages()
                            if messages:
                                print("\n📢 최근 상황:")
                                for message in messages[-2:]:  # 최근 2개 메시지만 표시
                                    print(f"  {message}")
                        except:
                            pass
                else:
                    print(f"💀 파티 전멸")
            else:
                print("❌ 파티 정보 없음")
            
            print()  # 여백
            
        except Exception as e:
            # 최종 폴백: 최소한의 정보
            print(f"🎮 Dawn of Stellar - 차원 공간 {getattr(world, 'current_level', 1)}층")
            print(f"📍 위치: {getattr(world, 'player_pos', '?')}")
            print(f"⚠️ 화면 표시 오류: {e}")
            print("게임은 계속 진행됩니다.")
            print(f"🎮 {bright_yellow('H:도움말')} | WASD:이동 | I:인벤토리")


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
                
                # 가방 무게 분석 (실제 파티 매니저 방식 사용)
                try:
                    current_weight = party_manager.get_current_carry_weight()
                    max_weight = party_manager.get_total_carry_capacity()
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
                except Exception as e:
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
        """궁극의 차원 공간 전략 - 층수별 맞춤 전략"""
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
                "message": f"차원 공간 전략 오류: {e}",
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

    def analyze_cooking_materials_enhanced(self, party_manager, world):
        """🤖 로-바트의 완전체 요리 재료 분석 시스템!"""
        try:
            # 두 곳 모두 인벤토리 체크 (파티 인벤토리 + 요리 시스템 인벤토리)
            inventory = getattr(party_manager, 'inventory', {}).copy()
            
            # 요리 시스템 인벤토리도 추가로 확인
            if hasattr(party_manager, 'cooking_system') and party_manager.cooking_system:
                cooking_inventory = getattr(party_manager.cooking_system, 'inventory', {})
                for item, count in cooking_inventory.items():
                    inventory[item] = inventory.get(item, 0) + count
            
            if not inventory:
                return "🤖 로-바트: 요리할 재료가 하나도 없잖아! 재료부터 모아!"
            
            # 재료 타입별 분류 (로-바트 특허 분류법!)
            ingredient_types = {
                '고기류': 0, '채소류': 0, '향신료': 0, 
                '액체류': 0, '과일류': 0, '곡물류': 0
            }
            
            for ingredient_name, count in inventory.items():
                # 재료 타입 추정 (로-바트 AI 판정)
                if any(keyword in ingredient_name for keyword in ['고기', '생선', '육류', '닭', '돼지', '소']):
                    ingredient_types['고기류'] += count
                elif any(keyword in ingredient_name for keyword in ['채소', '버섯', '양파', '당근', '양배추']):
                    ingredient_types['채소류'] += count
                elif any(keyword in ingredient_name for keyword in ['향신료', '소금', '후추', '마늘', '생강']):
                    ingredient_types['향신료'] += count
                elif any(keyword in ingredient_name for keyword in ['물', '우유', '와인', '육수', '국물']):
                    ingredient_types['액체류'] += count
                elif any(keyword in ingredient_name for keyword in ['과일', '딸기', '사과', '배', '포도']):
                    ingredient_types['과일류'] += count
                elif any(keyword in ingredient_name for keyword in ['쌀', '밀', '보리', '빵', '면']):
                    ingredient_types['곡물류'] += count
            
            # 로-바트의 완벽한 균형 체크!
            insufficient_types = [type_name for type_name, count in ingredient_types.items() if count < 2]
            
            if insufficient_types:
                return f"🤖 로-바트 분석: 재료 균형 엉망! {', '.join(insufficient_types)} 더 가져와!"
            
            # 풍족함 레벨 체크
            total_ingredients = sum(ingredient_types.values())
            if total_ingredients >= 30:
                return "🤖 로-바트 감탄: 재료 엄청 많네! 요리 파티 열자!"
            elif total_ingredients >= 15:
                return "🤖 로-바트 만족: 적당한 재료량! 맛있는 요리 가능!"
            else:
                return "🤖 로-바트 아쉬움: 재료 좀 더 모으자~ 부족해!"
                
        except Exception as e:
            return f"🤖 로-바트 당황: 재료 분석 실패... 뭔가 이상해! ({e})"

    def analyze_skill_usage_enhanced(self, members):
        """🤖 로-바트의 스킬 사용 패턴 완전 분석!"""
        try:
            if not members:
                return "🤖 로-바트: 파티원이 없는데 뭘 분석해?!"
            
            skill_problems = []
            mp_wasters = []
            skill_hoarders = []
            
            for member in members:
                name = getattr(member, 'name', '이름없음')
                current_mp = getattr(member, 'current_mp', getattr(member, 'mp', 0))
                max_mp = getattr(member, 'max_mp', 1)
                
                # MP 효율성 체크
                mp_ratio = current_mp / max_mp if max_mp > 0 else 0
                
                # 만땅(100%)인 경우는 제외, 80-99%만 아끼는 사람으로 분류
                if 0.8 <= mp_ratio < 1.0:
                    skill_hoarders.append(name)
                elif mp_ratio < 0.2:
                    mp_wasters.append(name)
                
                # 스킬 사용 가능 여부 체크
                from game.error_logger import log_debug
                log_debug("로바트분석", f"{name} MP 상태 체크", {
                    "current_mp": current_mp,
                    "max_mp": max_mp, 
                    "mp_ratio": f"{mp_ratio:.2f}"
                })
                
                if current_mp < 10:  # 기본 스킬도 못 쓸 정도
                    skill_problems.append(f"{name} (MP 고갈)")
                    log_debug("로바트분석", f"{name} MP 고갈 판정", {
                        "current_mp": current_mp,
                        "판정기준": "10 미만"
                    })
            
            # 로-바트의 신랄한 평가
            comments = []
            if skill_hoarders:
                comments.append(f"🤖 로-바트 지적: {', '.join(skill_hoarders)}! MP 아껴서 뭐해? 써!")
            if mp_wasters:
                comments.append(f"🤖 로-바트 핀잔: {', '.join(mp_wasters)}! MP 관리 좀 해!")
            if skill_problems:
                comments.append(f"🤖 로-바트 경고: {', '.join(skill_problems)} - 회복 필요!")
            
            if not comments:
                return "🤖 로-바트 인정: 스킬 사용 패턴 완벽! 내가 잘 가르쳤지?"
            
            return " ".join(comments)
            
        except Exception as e:
            return f"🤖 로-바트 오류: 스킬 분석 실패... ({e})"

    def analyze_progression_readiness_enhanced(self, members, world):
        """🤖 로-바트의 파티 진행 준비도 완전 체크!"""
        try:
            current_floor = getattr(world, 'current_level', 1)
            
            # 전투력 평가
            combat_powers = [calculate_combat_power(char) for char in members]
            avg_power = sum(combat_powers) // len(combat_powers) if combat_powers else 0
            expected_power = self.get_recommended_power(current_floor)
            
            power_ratio = avg_power / expected_power if expected_power > 0 else 0
            
            # 체력/MP 상태 체크
            health_ratios = []
            mp_ratios = []
            
            for member in members:
                hp_ratio = getattr(member, 'current_hp', 0) / getattr(member, 'max_hp', 1)
                mp_ratio = getattr(member, 'current_mp', 0) / getattr(member, 'max_mp', 1)
                health_ratios.append(hp_ratio)
                mp_ratios.append(mp_ratio)
            
            avg_hp = sum(health_ratios) / len(health_ratios) if health_ratios else 0
            avg_mp = sum(mp_ratios) / len(mp_ratios) if mp_ratios else 0
            
            # 로-바트의 종합 평가
            if power_ratio >= 1.2 and avg_hp >= 0.8 and avg_mp >= 0.6:
                return f"🤖 로-바트 자신감: {current_floor + 1}층 진격! 내 교육의 성과다!"
            elif power_ratio >= 1.0 and avg_hp >= 0.7 and avg_mp >= 0.5:
                return f"🤖 로-바트 허가: {current_floor + 1}층 도전 가능! 조심해서 가!"
            elif power_ratio >= 0.8:
                return f"🤖 로-바트 고민: 전투력은 괜찮은데... 체력/MP 좀 더 채우자"
            else:
                return f"🤖 로-바트 금지: {current_floor}층에서 더 키워! 무리하면 죽어!"
                
        except Exception as e:
            return f"🤖 로-바트 혼란: 진행 분석 오류... ({e})"

    def get_battle_commander_analysis(self, party_members, enemies, battle_state="START"):
        """🤖 로-바트의 전투 지휘관 모드! (완전체 전술 분석)"""
        try:
            # 파티 전투 상태 분석
            party_analysis = self._analyze_party_combat_state_enhanced(party_members)
            enemy_analysis = self._analyze_enemy_threat_enhanced(enemies) if enemies else {}
            
            # 전투 전술 수립
            strategy = self._formulate_battle_strategy_enhanced(party_analysis, enemy_analysis, battle_state)
            
            # 로-바트의 전투 지시
            battle_commands = []
            battle_commands.append(f"🤖 로-바트 지휘: {strategy['main_strategy']}")
            
            if strategy.get('priority_actions'):
                battle_commands.append(f"🎯 우선 행동: {', '.join(strategy['priority_actions'])}")
            
            if strategy.get('warnings'):
                battle_commands.append(f"⚠️ 주의사항: {', '.join(strategy['warnings'])}")
            
            return "\n".join(battle_commands)
            
        except Exception as e:
            return f"🤖 로-바트 패닉: 전투 분석 실패! 각자 알아서 해! ({e})"

    def _analyze_party_combat_state_enhanced(self, members):
        """향상된 파티 전투 상태 분석"""
        if not members:
            return {"status": "NO_PARTY", "power": 0}
        
        total_hp_ratio = 0
        total_mp_ratio = 0
        total_power = 0
        critical_members = []
        
        for member in members:
            hp_ratio = getattr(member, 'hp', 0) / getattr(member, 'max_hp', 1)
            mp_ratio = getattr(member, 'mp', 0) / getattr(member, 'max_mp', 1)
            power = calculate_combat_power(member)
            
            total_hp_ratio += hp_ratio
            total_mp_ratio += mp_ratio
            total_power += power
            
            if hp_ratio < 0.3:
                critical_members.append(getattr(member, 'name', '알 수 없음'))
        
        return {
            "avg_hp_ratio": total_hp_ratio / len(members),
            "avg_mp_ratio": total_mp_ratio / len(members),
            "total_power": total_power,
            "critical_members": critical_members,
            "party_size": len(members)
        }

    def _analyze_enemy_threat_enhanced(self, enemies):
        """향상된 적 위협도 분석"""
        if not enemies:
            return {"threat_level": "NONE"}
        
        total_enemy_power = 0
        boss_count = 0
        special_abilities = []
        
        for enemy in enemies:
            enemy_power = getattr(enemy, 'combat_power', 0)
            total_enemy_power += enemy_power
            
            if 'boss' in str(getattr(enemy, 'type', '')).lower():
                boss_count += 1
            
            # 특수 능력 체크 (예시)
            if hasattr(enemy, 'special_abilities'):
                special_abilities.extend(enemy.special_abilities)
        
        threat_level = "LOW"
        if boss_count > 0:
            threat_level = "BOSS"
        elif total_enemy_power > 1000:
            threat_level = "HIGH"
        elif total_enemy_power > 500:
            threat_level = "MEDIUM"
        
        return {
            "threat_level": threat_level,
            "total_power": total_enemy_power,
            "enemy_count": len(enemies),
            "boss_count": boss_count,
            "special_abilities": special_abilities
        }

    def _formulate_battle_strategy_enhanced(self, party_analysis, enemy_analysis, battle_state):
        """향상된 전투 전략 수립"""
        strategy = {
            "main_strategy": "",
            "priority_actions": [],
            "warnings": []
        }
        
        # 파티 상태 기반 전략
        if party_analysis.get("avg_hp_ratio", 0) < 0.5:
            strategy["main_strategy"] = "회복 우선! 체력부터 채워!"
            strategy["priority_actions"].append("힐러 즉시 회복")
            strategy["warnings"].append("위험 상태 - 신중하게!")
        
        # 적 위협도 기반 전략
        threat_level = enemy_analysis.get("threat_level", "LOW")
        if threat_level == "BOSS":
            strategy["main_strategy"] = "보스전! 모든 스킬 총동원!"
            strategy["priority_actions"].append("버프 스킬 먼저")
            strategy["priority_actions"].append("딜러 집중 공격")
        elif threat_level == "HIGH":
            strategy["main_strategy"] = "강력한 적! 전술적 접근!"
            strategy["priority_actions"].append("탱커 방어 집중")
        else:
            strategy["main_strategy"] = "일반 전투! 효율적으로 처리!"
        
        # 전투 단계별 조정
        if battle_state == "CRITICAL":
            strategy["warnings"].append("위기 상황 - 즉시 대응 필요!")
        
        return strategy

    def get_ultimate_analysis_suite(self, party_manager, world, situation="COMPREHENSIVE"):
        """🤖 로-바트의 궁극 분석 스위트! (모든 분석 총동원)"""
        try:
            analysis_results = []
            
            # 기본 상황 분석 (안전 체크 추가)
            basic_analysis = self.analyze_everything(party_manager, world, situation)
            if basic_analysis is None:
                basic_analysis = {"message": "🤖 로-바트: 분석 시스템 초기화 중..."}
            
            analysis_results.append("=== 🤖 로-바트 기본 분석 ===")
            
            # message가 없거나 비어있을 경우 기본 메시지 제공
            message = basic_analysis.get("message", "")
            if not message or message == "분석 오류":
                # 기본 분석 메시지 생성
                alive_count = len(party_manager.get_alive_members())
                if alive_count > 0:
                    message = f"🤖 로-바트: 파티 {alive_count}명 모두 건재! 내 분석 덕분이지!"
                else:
                    message = "🤖 로-바트: 어? 파티가 위험해!"
            
            analysis_results.append(message)
            
            # 요리 재료 분석
            cooking_analysis = self.analyze_cooking_materials_enhanced(party_manager, world)
            analysis_results.append("\n=== 🍳 요리 재료 분석 ===")
            analysis_results.append(cooking_analysis)
            
            # 스킬 사용 분석
            if hasattr(party_manager, 'members'):
                skill_analysis = self.analyze_skill_usage_enhanced(party_manager.members)
                analysis_results.append("\n=== ✨ 스킬 사용 분석 ===")
                analysis_results.append(skill_analysis)
                
                # 진행 준비도 분석
                progression_analysis = self.analyze_progression_readiness_enhanced(party_manager.members, world)
                analysis_results.append("\n=== 🚀 진행 준비도 분석 ===")
                analysis_results.append(progression_analysis)
            
            # 로-바트의 최종 종합 평가
            analysis_results.append("\n=== 🎯 로-바트 최종 평가 ===")
            analysis_results.append("🤖 내 분석은 항상 완벽하지! 내 조언 잘 따라해!")
            
            return "\n".join(analysis_results)
            
        except Exception as e:
            return f"🤖 로-바트 대혼란: 궁극 분석 시스템 오류! 이럴 리가... ({e})"


# 전역 로-바트 인스턴스 (게임의 자랑스러운 마스코트!)
robart = RobotAIMaster()


def calculate_combat_power(character):
    """캐릭터의 정교한 전투력 계산 - 로바트 권장 수치에 맞춤 조정"""
    try:
        if not hasattr(character, 'is_alive') or not character.is_alive:
            return 0
            
        # === 기본 스탯 기반 전투력 계산 (대폭 축소) ===
        # 실제 스탯을 반영한 기본 전투력 (스케일 축소: /10)
        attack_power = (getattr(character, 'attack', 0) + getattr(character, 'physical_attack', 0)) * 0.1
        magic_power = getattr(character, 'magic_attack', 0) * 0.1
        defense_power = (getattr(character, 'defense', 0) + getattr(character, 'physical_defense', 0)) * 0.08
        magic_def_power = getattr(character, 'magic_defense', 0) * 0.08
        speed_power = getattr(character, 'speed', 0) * 0.06
        
        # === HP/MP 최댓값 기반 생존력 반영 ===
        max_hp = getattr(character, 'max_hp', 100)
        max_mp = getattr(character, 'max_mp', 50)
        
        # HP는 탱킹 능력에 직결되므로 적당한 비중으로 반영 (축소)
        hp_power = max_hp * 0.03  # HP 100당 3점
        # MP는 마법 지속력에 영향 (축소)
        mp_power = max_mp * 0.02  # MP 50당 1점
        
        # 기본 전투력 = 공격력 + 마공 + 방어력 + 속도 + HP 생존력 + MP 지속력
        base_power = attack_power + magic_power + defense_power + magic_def_power + speed_power + hp_power + mp_power
        
        # 레벨 보정 (매우 작게 조정)
        level_bonus = getattr(character, 'level', 1) * 5  # 레벨당 5점만
        
        base_power += level_bonus
        
        # === HP/MP/BRV 상태 보너스 (축소) ===
        # safe 속성 접근
        current_hp = getattr(character, 'hp', getattr(character, 'current_hp', getattr(character, 'max_hp', 100)))
        max_hp = getattr(character, 'max_hp', 100)
        current_mp = getattr(character, 'mp', getattr(character, 'current_mp', getattr(character, 'max_mp', 50)))
        max_mp = getattr(character, 'max_mp', 50)
        
        hp_ratio = current_hp / max_hp if max_hp > 0 else 1
        mp_ratio = current_mp / max_mp if max_mp > 0 else 1
        brv_points = getattr(character, 'brave_points', getattr(character, 'brv_points', 0))
        
        # HP 상태에 따른 보정 (축소)
        if hp_ratio >= 0.8:
            hp_bonus = 5
        elif hp_ratio >= 0.6:
            hp_bonus = 3
        elif hp_ratio >= 0.4:
            hp_bonus = 1
        elif hp_ratio >= 0.2:
            hp_bonus = -2
        else:
            hp_bonus = -5
        
        # MP 상태 보정 (축소)
        mp_bonus = mp_ratio * 3
        
        # BRV 포인트 보정 (축소)
        brv_bonus = min(brv_points * 0.001, 5)  # 최대 5점으로 대폭 축소
        
        # === 핵심 스탯 보너스 (대폭 축소) ===
        # safe 속성 접근으로 수정
        attack_total = getattr(character, 'attack', 0) + getattr(character, 'physical_attack', 0)
        defense_total = getattr(character, 'defense', 0) + getattr(character, 'physical_defense', 0)
        magic_attack_total = getattr(character, 'magic_attack', 0)
        magic_defense_total = getattr(character, 'magic_defense', 0)
        speed_total = getattr(character, 'speed', 0)
        
        # 스탯 보너스를 1.2에서 0.03으로 대폭 축소 (40배 감소)
        stat_bonus = (attack_total + defense_total + magic_attack_total + 
                     magic_defense_total + speed_total) * 0.03
        
        # === 장비 시스템 완전 분석 (축소) ===
        equipment_bonus = 0
        equipment_durability_penalty = 0
        set_bonus = 0
        
        if hasattr(character, 'equipment'):
            equipped_items = []
            for slot, item in character.equipment.items():
                if item:
                    equipped_items.append(item)
                    # 기본 스탯 보너스 (대폭 축소)
                    equipment_bonus += getattr(item, 'attack', 0) * 0.03
                    equipment_bonus += getattr(item, 'defense', 0) * 0.03
                    equipment_bonus += getattr(item, 'magic_attack', 0) * 0.03
                    equipment_bonus += getattr(item, 'magic_defense', 0) * 0.03
                    equipment_bonus += getattr(item, 'speed', 0) * 0.03
                    
                    # 내구도 시스템 반영 (축소)
                    if hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                        durability_ratio = item.durability / item.max_durability if item.max_durability > 0 else 1
                        if durability_ratio < 0.3:
                            equipment_durability_penalty += 3  # 내구도 낮음
                        elif durability_ratio < 0.6:
                            equipment_durability_penalty += 2
                        elif durability_ratio < 0.8:
                            equipment_durability_penalty += 1
                    
                    # 특수 장비 효과 (축소)
                    if hasattr(item, 'special_effects'):
                        for effect in item.special_effects:
                            if 'damage' in effect.lower() or 'attack' in effect.lower():
                                equipment_bonus += 2
                            elif 'defense' in effect.lower() or 'protection' in effect.lower():
                                equipment_bonus += 2
            
            # 세트 장비 보너스 체크 (축소)
            if len(equipped_items) >= 3:
                set_bonus = 4  # 세트 보너스
        
        # === 상처 시스템 정밀 분석 (축소) ===
        wound_penalty = 0
        if hasattr(character, 'wounds') and character.wounds > 0:
            wound_ratio = character.wounds / character.max_hp if character.max_hp > 0 else 0
            if wound_ratio >= 0.6:
                wound_penalty = character.wounds * 0.02  # 심각한 상처
            elif wound_ratio >= 0.4:
                wound_penalty = character.wounds * 0.015
            elif wound_ratio >= 0.2:
                wound_penalty = character.wounds * 0.01
            else:
                wound_penalty = character.wounds * 0.005
        
        # === 버프/디버프 시스템 (축소) ===
        buff_bonus = 0
        debuff_penalty = 0
        
        # 요리 버프 (축소)
        if hasattr(character, 'food_buffs') and character.food_buffs:
            for buff in character.food_buffs:
                buff_bonus += 3  # 요리 버프당 3점
        
        # 상태이상 확인 (축소)
        if hasattr(character, 'status_effects'):
            for effect in character.status_effects:
                if effect in ['독', 'poison', '화상', 'burn']:
                    debuff_penalty += 2
                elif effect in ['축복', 'bless', '강화', 'enhance']:
                    buff_bonus += 4
        
        # === 직업별 특수 보정 (대폭 축소) ===
        class_bonus = 0
        job_class = getattr(character, 'character_class', '')
        
        # 전투 특화 직업
        if job_class in ['전사', '성기사', '암흑기사', '검성', '검투사']:
            class_bonus = getattr(character, 'level', 1) * 0.5
        # 마법 특화 직업
        elif job_class in ['아크메이지', '정령술사', '시간술사', '차원술사']:
            magic_att = getattr(character, 'magic_attack', 0)
            magic_def = getattr(character, 'magic_defense', 0)
            class_bonus = (magic_att + magic_def) * 0.01
        # 균형 직업
        elif job_class in ['궁수', '도적', '바드', '드루이드']:
            class_bonus = getattr(character, 'level', 1) * 0.3
        # 지원 직업
        elif job_class in ['성직자', '연금술사', '기계공학자']:
            class_bonus = mp_ratio * 5  # MP 의존도 높음
        
        # === 최종 전투력 계산 ===
        total_power = (base_power + hp_bonus + mp_bonus + brv_bonus + 
                      stat_bonus + equipment_bonus + set_bonus + 
                      buff_bonus + class_bonus - 
                      equipment_durability_penalty - wound_penalty - debuff_penalty)
        
        return max(0, int(total_power))
        
    except Exception as e:
        print(f"⚠️ 전투력 계산 오류 ({character.name}): {e}")
        return getattr(character, 'level', 1) * 12  # 기본값


def get_ai_recommendation(party_manager, world):
    """🤖 로-바트의 천재적 추천 시스템! (100% 신뢰 가능!)"""
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
                return f"🤖 {analysis['actions'][0]} (내 말을 믿어!)"
            elif "checklist" in analysis:
                return f"🤖 {analysis['checklist'][0]} (역시 내가 최고야!)"
            else:
                return f"🤖 {analysis.get('message', '신중한 탐험 권장')} (흠... 당연한 얘기지?)"
        
        return "🤖 로-바트: 잠깐... 계산 중... (천재도 시간이 필요해!)"
    except Exception as e:
        return f"🤖 로-바트: 어? 뭔가 이상한데? 오류: {e}"


def get_robart_ultimate_analysis(party_manager, world, situation="COMPREHENSIVE"):
    """🤖 로-바트의 궁극 완전체 분석 시스템! (모든 분석 기능 총동원)"""
    return robart.get_ultimate_analysis_suite(party_manager, world, situation)


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
        return {"status": "ERROR", "message": f"🤖 로-바트: 전투 전략 오류! {e}"}


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
        equipment_analysis = robart._analyze_equipment_needs(alive_members)
        if equipment_analysis:
            advice_list.append(f"🤖 로-바트 장비 진단: {equipment_analysis} (내가 다 봤어!)")
        
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
    """🤖 로-바트의 전투 지휘관 (통합 완전체 버전)"""
    return robart.get_battle_commander_analysis(party_members, enemies, battle_state)


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


def analyze_cooking_materials(party_manager, world):
    """🤖 로-바트의 요리 재료 분석 (통합 완전체 버전)"""
    return robart.analyze_cooking_materials_enhanced(party_manager, world)


def analyze_skill_usage(members):
    """🤖 로-바트의 스킬 사용 분석 (통합 완전체 버전)"""
    return robart.analyze_skill_usage_enhanced(members)


def analyze_progression_readiness(members, world):
    """🤖 로-바트의 진행 준비도 분석 (통합 완전체 버전)"""
    return robart.analyze_progression_readiness_enhanced(members, world)

# === 백업 클래스 (사용하지 않음) ===
class GameDisplay_Backup:
    """게임 화면 표시 클래스 - 백업용"""
    
    def __init__(self):
        self.screen_width = 120  # 화면 너비 증가
        self.screen_height = 35  # 화면 높이 증가
        self._last_clear_time = 0  # 화면 클리어 디바운싱
        self._frame_time_limit = 1.0 / 20.0  # 20fps = 0.05초당 1프레임
        self._last_frame_time = 0
        self._frame_buffer = []  # 화면 스택 방지용 버퍼
        
    def clear_screen(self):
        """화면 지우기 - 텍스트 스택 방지 강화 및 20fps 제한"""
        import time
        
        current_time = time.time()
        
        # 20fps 제한: 프레임 간격 체크
        if current_time - self._last_frame_time < self._frame_time_limit:
            # 프레임 제한에 걸렸을 때는 버퍼만 업데이트
            return
        
        self._last_frame_time = current_time
        
        # 화면 스택 방지: 이전 버퍼 완전 클리어
        self._frame_buffer.clear()
        
        # 디바운싱: 너무 빈번한 클리어 방지
        if current_time - self._last_clear_time < 0.025:
            try:
                # 소프트 클리어: 기존 텍스트를 밀어내기
                print("\n" * 5)
                print("─" * 80)  # 구분선
            except:
                pass
            return
        self._last_clear_time = current_time
        
        # 파이프/모바일 모드에서 텍스트 스택 완전 방지
        if os.getenv('SUBPROCESS_MODE') == '1':
            try:
                # 강력한 소프트 클리어: 화면을 완전히 밀어내기
                print("\n" * 25)  # 충분한 줄 수로 이전 내용 밀어내기
                print("═" * 80)   # 명확한 구분선
                print("🎮 Dawn of Stellar - 새 프레임")
                print("═" * 80)
                return
            except Exception:
                return
                
        # 일반 모드에서는 확실한 화면 클리어
        try:
            if platform.system() == "Windows":
                # Windows에서 확실한 클리어 + 스택 방지
                os.system('cls')
                print()  # 첫 줄 공백으로 여백 확보
            else:
                os.system('clear')
                print()
        except Exception:
            # OS 명령어 실패 시 강력한 텍스트 클리어
            print("\033[2J\033[H")  # ANSI 이스케이프 시퀀스로 화면 클리어
            print("\n" * 30)
            print("═" * 80)
    
    def update_display_with_fps_limit(self, content):
        """20fps 제한이 적용된 디스플레이 업데이트"""
        import time
        
        current_time = time.time()
        if current_time - self._last_frame_time >= self._frame_time_limit:
            self.clear_screen()
            print(content)
            self._last_frame_time = current_time
        else:
            # 프레임 제한에 걸렸을 때는 버퍼에 저장
            self._frame_buffer.append(content)
            
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
        
    def show_game_screen_backup(self, party_manager: PartyManager, world: GameWorld, cooking_system=None):
        """메인 게임 화면 표시 - 안정화된 단일 경로 버전"""
        
        # 화면 크기 안전하게 설정 (더 넓게)
        safe_width = min(120, max(80, self.screen_width))  # 최소 80, 최대 120자
        safe_height = min(60, max(30, self.screen_height))  # 최소 30, 최대 60줄

        # 화면 클리어 (한 번만)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 상단 정보 표시
        title = f"차원 공간 {world.current_level}층 - Dawn Of Stellar"
        title_padding = max(0, (safe_width - len(title)) // 2)
        print(f"{' ' * title_padding}{bright_cyan(title)}")
        print()
        print()
        print()
        
        # 차원 공간 맵 표시 (개선된 크기)
        try:
            if hasattr(world, 'get_colored_map_display'):
                # 맵 크기를 더 넓게 설정
                map_width = min(50, safe_width - 10)  # 맵 너비 증가
                map_height = max(14, safe_height - 30)  # 맵 높이: 줄임 (20 -> 14)
                map_display = world.get_colored_map_display(map_width, map_height)
                
                if map_display and isinstance(map_display, list):
                    for line in map_display:
                        if line and isinstance(line, str):
                            # 맵 라인을 중앙 정렬하지 않고 왼쪽 정렬로 출력
                            print(line)
                else:
                    # 백업 맵 표시
                    print("맵 로딩 중...")
                    print(f"위치: {getattr(world, 'player_pos', '?')}")
            else:
                print("맵을 불러올 수 없습니다")
        except Exception as map_error:
            print(f"맵 표시 오류 - 위치: {getattr(world, 'player_pos', '?')}")
        
        print()
        print()
        print()
        print()
        
        # 파티 상태 정보
        alive_count = len(party_manager.get_alive_members())
        total_count = len(party_manager.members)
        
        party_info = f"파티: {alive_count}/{total_count}명 생존 | 층: {world.current_level}"
        
        # 골드 정보 안전하게 표시
        try:
            gold_info = f" | 골드: {party_manager.party_gold}G"
        except Exception:
            gold_info = " | 골드: 0G"
        
        # 가방 정보 안전하게 표시
        try:
            if cooking_system:
                total_weight = cooking_system.get_total_inventory_weight()
                max_weight = cooking_system.get_max_inventory_weight()
                
                # 무게 비율에 따른 색상 적용 (현재 무게에만)
                weight_ratio = total_weight / max_weight if max_weight > 0 else 0
                if weight_ratio < 0.5:  # 50% 미만: 밝은 청록색 (매우 여유)
                    weight_color = "\033[96m"  # 밝은 청록색
                elif weight_ratio < 0.7:  # 70% 미만: 초록색 (여유)
                    weight_color = "\033[92m"  # 밝은 초록
                elif weight_ratio < 0.85:  # 85% 미만: 노란색 (주의)
                    weight_color = "\033[93m"  # 노란색
                elif weight_ratio < 0.95:  # 95% 미만: 주황색 (경고)
                    weight_color = "\033[38;5;208m"  # 주황색 (256색)
                else:  # 95% 이상: 빨간색 (위험)
                    weight_color = "\033[91m"  # 빨간색
                
                reset_color = "\033[0m"
                weight_info = f" | 가방: {weight_color}{total_weight:.1f}{reset_color}/{max_weight:.1f}kg"
            else:
                weight_info = ""
        except Exception:
            weight_info = ""
        
        print(f"  {party_info}{gold_info}{weight_info}")
        print("+" + "-" * (safe_width - 2) + "+")
        
        # 파티원 상태 표시 (최대 4명)
        for member in party_manager.members[:4]:
            if member.is_alive:
                # HP/MP 비율 계산
                hp_ratio = member.current_hp / member.max_hp if member.max_hp > 0 else 0
                mp_ratio = member.current_mp / member.max_mp if member.max_mp > 0 else 0
                
                # HP 색상 결정
                if hp_ratio >= 0.8:
                    hp_color = bright_green; hp_emoji = "💚"
                elif hp_ratio >= 0.6:
                    hp_color = green; hp_emoji = "💛"
                elif hp_ratio >= 0.4:
                    hp_color = yellow; hp_emoji = "🧡"
                elif hp_ratio >= 0.2:
                    hp_color = bright_red; hp_emoji = "❤️"
                else:
                    hp_color = red; hp_emoji = "💔"
                
                mp_color = bright_cyan if mp_ratio >= 0.8 else cyan
                mp_emoji = "💙"
                
                # 직업 이모지
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
                
                name_class = f"{class_emoji} {member.name[:10]:10} ({member.character_class[:8]:8})"
                hp_text = f"{hp_emoji}HP:{hp_color(f'{member.current_hp:3}/{member.max_hp:3}')}"
                mp_text = f"{mp_emoji}MP:{mp_color(f'{member.current_mp:2}/{member.max_mp:2}')}"
                print(f"    {name_class} {hp_text} {mp_text}")
            else:
                name_class = f"💀 {member.name[:10]:10} ({member.character_class[:8]:8})"
                print(f"    {name_class} {red('사망')}")
        
        print("+" + "-" * (safe_width - 2) + "+")
        print()
        print(f"🎮 조작키 | WASD:이동 | I:인벤토리 | F:메뉴 | P:파티 | H:도움말")
        print()
        
        # 게임 정보 표시
        try:
            print(f"📊 {bright_cyan('게임 정보')}")
            
            # 파티 전투력 계산
            alive_members = party_manager.get_alive_members()
            if alive_members:
                combat_powers = [calculate_combat_power(char) for char in alive_members]
                avg_combat_power = sum(combat_powers) // len(combat_powers)
                
                # 전투력 색상 평가
                expected_power = world.current_level * 15
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
            
            total_gold = sum(getattr(char, 'gold', 0) for char in party_manager.members)
            print(f"│ 파티: {alive_count}/{len(party_manager.members)}명 생존 | 전투력: {avg_combat_power} ({power_status})")
            
            # AI 추천 행동 (로-바트)
            ai_recommendation = get_ai_recommendation(party_manager, world)
            print(f"│   로-바트: {ai_recommendation}")
            
            # 진행도
            progress = min(100, (world.current_level / 10) * 100)
            progress_bar = "█" * int(progress // 10) + "░" * (10 - int(progress // 10))
            print(f"│ 진행도: [{progress_bar}] {progress:.1f}%")
            
            # 위치 정보
            if hasattr(world, 'player_pos') and world.player_pos:
                pos_x, pos_y = world.player_pos
                print(f"📍 위치: ({pos_x}, {pos_y}) | 🗺️ 층: {world.current_level} | 🎯 목표: 계단 찾아 다음 층으로!")
            
        except Exception as e:
            print(f"│ 게임 정보 표시 오류: {e}")
        
        # 메시지 버퍼 표시
        if hasattr(world, 'game') and world.game and hasattr(world.game, 'get_recent_messages'):
            try:
                messages = world.game.get_recent_messages()
                if messages:
                    print("\n📢 최근 상황:")
                    for message in messages[-2:]:  # 최근 2개 메시지만 표시
                        print(f"  {message}")
            except:
                pass
            try:
                gold_info = f" | 골드: {party_manager.party_gold}G"
            except:
                gold_info = ""
            
            # 가방 무게 정보 추가 (색깔 포함)
            try:
                # 파티 매니저의 실제 무게 계산 방법 사용
                total_weight = party_manager.get_current_carry_weight()
                max_weight = party_manager.get_total_carry_capacity()
                weight_ratio = total_weight / max_weight if max_weight > 0 else 0
                
                # 무게 비율에 따른 색깔 결정 (더 명확한 색상)
                if weight_ratio < 0.4:  # 40% 미만: 청록색 (매우 여유)
                    weight_color = "\033[96m"  # 밝은 청록색
                elif weight_ratio < 0.7:  # 70% 미만: 초록색 (여유)
                    weight_color = "\033[92m"  # 밝은 초록
                elif weight_ratio < 0.85:  # 85% 미만: 노란색 (주의)
                    weight_color = "\033[93m"  # 노란색
                elif weight_ratio < 0.95:  # 95% 미만: 주황색 (경고)
                    weight_color = "\033[38;5;208m"  # 주황색 (256색)
                else:  # 95% 이상: 깜빡이는 빨간색 (위험)
                    weight_color = "\033[91m\033[5m"  # 깜빡이는 빨간색
                
                reset_color = "\033[0m"
                percentage = int(weight_ratio * 100)
                weight_info = f" | 가방: {weight_color}{total_weight:.1f}{reset_color}/{max_weight:.1f}kg ({percentage}%)"
            except Exception as e:
                # 오류 시 기본 표시
                weight_info = " | 가방: ?/?kg"
            
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
            print(f"\n🎮 {bright_cyan('조작키')} | WASD:이동 | I:인벤토리 | F:메뉴 | P:파티 | {bright_yellow('H:도움말')}")

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
                
                print(f"│ 파티: {alive_count}/{len(party_manager.members)}명 생존 | 전투력: {avg_combat_power} ({power_status})")
                
                # AI 추천 행동
                ai_recommendation = get_ai_recommendation(party_manager, world)
                print(f"│ {ai_recommendation}")
                
                # 차원 공간 통계
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


def show_detailed_party_analysis(party_manager, world=None):
    """🤖 로바트의 완전체 파티 분석 - 말도 안되게 상세함! (모든 로바트 기능 총동원)"""
    try:
        alive_members = party_manager.get_alive_members()
        if not alive_members:
            print("🤖 로-바트: 어? 살아있는 파티원이 없네? 이상한데?")
            return
        
        # 화면 클리어
        import os
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux/Mac
            os.system('clear')
        
        print("=" * 100)
        print("🤖 로-바트의 완전체 파티 분석 보고서 (모든 기능 총동원!)")
        print("=" * 100)
        
        # === 🚀 로바트 궁극 분석 스위트 실행! ===
        if world:
            print("\n🔥 로-바트 궁극 분석 시스템 가동! 🔥")
            print("=" * 60)
            ultimate_analysis = get_robart_ultimate_analysis(party_manager, world, "COMPREHENSIVE")
            print(ultimate_analysis)
            print("=" * 60)
        
        # === 1. 전투력 완전 분석 ===
        print(f"\n📊 전투력 완전 분석 (꼴찌까지 다 찾아줌!)")
        print("-" * 80)
        
        combat_powers = []
        detailed_stats = []
        
        for char in alive_members:
            power = calculate_combat_power(char)
            
            # 상세 스탯 분석
            hp_ratio = char.current_hp / char.max_hp if char.max_hp > 0 else 0
            mp_ratio = char.current_mp / char.max_mp if char.max_mp > 0 else 0
            
            # 개별 능력치들
            phys_attack = getattr(char, 'physical_attack', 0)
            phys_defense = getattr(char, 'physical_defense', 0)
            magic_attack = getattr(char, 'magic_attack', 0) or getattr(char, 'magical_attack', 0)
            magic_defense = getattr(char, 'magic_defense', 0) or getattr(char, 'magical_defense', 0)
            speed = getattr(char, 'speed', 0)
            accuracy = getattr(char, 'accuracy', 0)
            evasion = getattr(char, 'evasion', 0)
            
            # 특수 상태
            wounds = getattr(char, 'wounds', 0)
            atb_gauge = getattr(char, 'atb_gauge', 0)
            brave_points = getattr(char, 'brave_points', 0)
            
            combat_powers.append((char, power))
            detailed_stats.append({
                'char': char,
                'power': power,
                'hp_ratio': hp_ratio,
                'mp_ratio': mp_ratio,
                'phys_attack': phys_attack,
                'phys_defense': phys_defense,
                'magic_attack': magic_attack,
                'magic_defense': magic_defense,
                'speed': speed,
                'accuracy': accuracy,
                'evasion': evasion,
                'wounds': wounds,
                'atb_gauge': atb_gauge,
                'brave_points': brave_points
            })
        
        # 전투력 순으로 정렬 (내림차순)
        combat_powers.sort(key=lambda x: x[1], reverse=True)
        detailed_stats.sort(key=lambda x: x['power'], reverse=True)
        
        total_power = sum(power for _, power in combat_powers)
        avg_power = total_power // len(combat_powers) if combat_powers else 0
        
        print(f"🎯 파티 총 전투력: {total_power:,} | 평균: {avg_power:,}")
        print()
        
        for i, stats in enumerate(detailed_stats):
            char = stats['char']
            power = stats['power']
            rank = i + 1
            percentage = (power / total_power * 100) if total_power > 0 else 0
            
            # 랭킹 아이콘과 평가
            if rank == 1:
                rank_icon = "🥇"
                rank_text = "최강의 에이스!"
            elif rank == 2:
                rank_icon = "🥈"
                rank_text = "든든한 2인자"
            elif rank == 3:
                rank_icon = "🥉"
                rank_text = "준수한 3인자"
            elif rank == len(detailed_stats):
                rank_icon = "💩"
                rank_text = "꼴찌... 키워야 함"
            else:
                rank_icon = f"#{rank}"
                rank_text = "평범함"
            
            # 상태 분석
            health_status = "💚완벽" if stats['hp_ratio'] > 0.9 else "💛양호" if stats['hp_ratio'] > 0.7 else "🧡주의" if stats['hp_ratio'] > 0.5 else "❤️위험" if stats['hp_ratio'] > 0.2 else "💀빈사"
            mana_status = "충만" if stats['mp_ratio'] > 0.8 else "보통" if stats['mp_ratio'] > 0.5 else "부족"
            
            print(f"{rank_icon} {rank}위: {char.name} ({char.character_class}) - {rank_text}")
            print(f"   ⚔️ 전투력: {power:,} ({percentage:.1f}%) | {health_status} | {mana_status}")
            print(f"   📊 물공{stats['phys_attack']:,} 물방{stats['phys_defense']:,} 마공{stats['magic_attack']:,} 마방{stats['magic_defense']:,}")
            print(f"   ⚡ 속도{stats['speed']:,} 명중{stats['accuracy']:,} 회피{stats['evasion']:,} BRV{stats['brave_points']:,}")
            
            if stats['wounds'] > 0:
                print(f"   🩸 상처: {stats['wounds']:,} (치료 필요!)")
            
            # 특수 평가
            if stats['phys_attack'] > stats['magic_attack'] * 2:
                print(f"   💪 물리 특화형 캐릭터")
            elif stats['magic_attack'] > stats['phys_attack'] * 2:
                print(f"   🔮 마법 특화형 캐릭터")
            else:
                print(f"   ⚖️ 균형형 캐릭터")
            
            if stats['speed'] > avg_power * 0.3:
                print(f"   🏃 스피드형 (빠름)")
            elif stats['phys_defense'] + stats['magic_defense'] > avg_power * 0.5:
                print(f"   🛡️ 탱커형 (방어 특화)")
            
            print()
        
        # 전투력 격차 분석
        if len(combat_powers) >= 2:
            strongest = combat_powers[0][1]
            weakest = combat_powers[-1][1]
            gap = strongest - weakest
            gap_ratio = (gap / strongest * 100) if strongest > 0 else 0
            
            print(f"🔍 전투력 격차 분석:")
            print(f"   최강자 vs 꼴찌: {gap:,} 차이 ({gap_ratio:.1f}%)")
            
            if gap_ratio > 70:
                print(f"   🤖 로-바트: 격차 심각! {combat_powers[-1][0].name} 집중 육성 필요!")
            elif gap_ratio > 50:
                print(f"   🤖 로-바트: 격차가 크네. 밸런스 맞춰야겠어!")
            elif gap_ratio > 30:
                print(f"   🤖 로-바트: 적당한 격차. 나쁘지 않아.")
            else:
                print(f"   🤖 로-바트: 완벽한 밸런스! 역시 내 조언 덕분이지?")
        
        # === 2. 장비 완전 분석 ===
        print(f"\n🛡️ 장비 상태 완전 분석 (내구도부터 효과까지 다 체크)")
        print("-" * 80)
        
        total_equipment_score = 0
        equipment_rankings = []
        
        for char in alive_members:
            char_equipment_score = 0
            char_equipment_details = {
                'char': char,
                'equipped_count': 0,
                'total_durability': 0,
                'durability_count': 0,
                'issues': [],
                'bonuses': [],
                'total_bonus_value': 0
            }
            
            # 장착된 장비 분석
            if hasattr(char, 'equipped_items') and char.equipped_items:
                for slot, item in char.equipped_items.items():
                    if item:
                        char_equipment_details['equipped_count'] += 1
                        
                        # 장비 점수 계산 (레벨, 품질 등 고려)
                        item_score = getattr(item, 'level', 1) * 10
                        char_equipment_score += item_score
                        
                        # 내구도 체크
                        if hasattr(item, 'get_durability_percentage'):
                            durability = item.get_durability_percentage()
                            char_equipment_details['total_durability'] += durability
                            char_equipment_details['durability_count'] += 1
                            
                            if durability < 10:
                                char_equipment_details['issues'].append(f"{slot} 거의 파괴됨!")
                            elif durability < 30:
                                char_equipment_details['issues'].append(f"{slot} 위험상태")
                            elif durability < 60:
                                char_equipment_details['issues'].append(f"{slot} 수리필요")
                        
                        # 스탯 보너스 분석
                        if hasattr(item, 'get_effective_stats'):
                            effective_stats = item.get_effective_stats()
                            for stat, value in effective_stats.items():
                                if isinstance(value, (int, float)) and value > 0:
                                    char_equipment_details['total_bonus_value'] += value
                                    if value >= 50:
                                        char_equipment_details['bonuses'].append(f"{stat}+{value}")
            
            char_equipment_details['score'] = char_equipment_score
            equipment_rankings.append(char_equipment_details)
            total_equipment_score += char_equipment_score
        
        # 장비 랭킹 정렬
        equipment_rankings.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"🎯 파티 총 장비 점수: {total_equipment_score:,}")
        print()
        
        for i, eq_data in enumerate(equipment_rankings):
            char = eq_data['char']
            rank = i + 1
            
            avg_durability = (eq_data['total_durability'] / eq_data['durability_count']) if eq_data['durability_count'] > 0 else 100
            max_slots = 6  # 추정
            equipment_ratio = (eq_data['equipped_count'] / max_slots * 100) if max_slots > 0 else 0
            
            # 장비 상태 평가
            if equipment_ratio >= 90 and avg_durability >= 80:
                eq_status = "🟢완벽장비"
            elif equipment_ratio >= 70 and avg_durability >= 60:
                eq_status = "🟡양호장비"
            elif equipment_ratio >= 50:
                eq_status = "🟠부족장비"
            else:
                eq_status = "🔴빈약장비"
            
            print(f"#{rank} {char.name}: {eq_status}")
            print(f"   📦 장착률: {equipment_ratio:.0f}% ({eq_data['equipped_count']}/{max_slots})")
            print(f"   🔧 평균 내구도: {avg_durability:.0f}%")
            print(f"   💎 장비 점수: {eq_data['score']:,}")
            print(f"   📈 총 보너스: {eq_data['total_bonus_value']:,}")
            
            if eq_data['issues']:
                print(f"   ⚠️ 문제: {', '.join(eq_data['issues'])}")
            
            if eq_data['bonuses']:
                print(f"   ✨ 주요보너스: {', '.join(eq_data['bonuses'])}")
            
            print()
        
        # === 3. 역할 및 시너지 분석 ===
        print(f"\n🎯 역할 분석 & 파티 시너지")
        print("-" * 80)
        
        role_analysis = {}
        for char in alive_members:
            char_class = getattr(char, 'character_class', '알 수 없음')
            
            # 상세 역할 분류
            if char_class in ["전사", "성기사", "기사", "광전사"]:
                role = "🛡️ 탱커"
            elif char_class in ["궁수", "도적", "암살자", "사무라이", "검투사"]:
                role = "⚔️ 물리딜러"
            elif char_class in ["아크메이지", "네크로맨서", "정령술사", "시간술사", "연금술사", "차원술사"]:
                role = "🔮 마법딜러"
            elif char_class in ["신관", "드루이드"]:
                role = "💚 힐러"
            elif char_class in ["바드", "철학자"]:
                role = "🎵 서포터"
            else:
                role = "❓ 만능형"
            
            if role not in role_analysis:
                role_analysis[role] = []
            role_analysis[role].append(char)
        
        # 역할별 분석
        for role, chars in role_analysis.items():
            print(f"{role}: {len(chars)}명")
            for char in chars:
                power = calculate_combat_power(char)
                print(f"   • {char.name} (전투력: {power:,})")
        
        # 파티 밸런스 평가
        print(f"\n🎯 파티 밸런스 평가:")
        tank_count = len(role_analysis.get("🛡️ 탱커", []))
        healer_count = len(role_analysis.get("💚 힐러", []))
        dps_count = len(role_analysis.get("⚔️ 물리딜러", [])) + len(role_analysis.get("🔮 마법딜러", []))
        support_count = len(role_analysis.get("🎵 서포터", []))
        
        if tank_count >= 1 and healer_count >= 1 and dps_count >= 2:
            balance_score = "✅ 완벽한 밸런스!"
        elif tank_count >= 1 and dps_count >= 2:
            balance_score = "🟡 준수한 구성"
        elif dps_count >= 3:
            balance_score = "🔴 공격 편중 (위험함)"
        else:
            balance_score = "❌ 불안정한 구성"
        
        print(f"   {balance_score}")
        print(f"   탱커 {tank_count}명, 힐러 {healer_count}명, 딜러 {dps_count}명, 서포터 {support_count}명")
        
        # === 4. 로바트의 완전체 종합 평가 ===
        print(f"\n🤖 로-바트의 완전체 종합 평가 (99.999% 정확함!)")
        print("-" * 80)
        
        # 현재 층수 기반 평가
        current_level = getattr(world, 'current_level', 1) if world else 1
        recommended_power = robart.get_recommended_power(current_level)
        
        power_ratio = avg_power / recommended_power if recommended_power > 0 else 0
        
        if power_ratio >= 1.5:
            power_evaluation = "💪 압도적 전투력! 지루할 정도로 강해!"
        elif power_ratio >= 1.2:
            power_evaluation = "✅ 충분한 전투력! 역시 내 조언 덕분이지?"
        elif power_ratio >= 1.0:
            power_evaluation = "🟡 적당한 전투력. 방심하지 마!"
        elif power_ratio >= 0.8:
            power_evaluation = "🟠 약간 부족함. 조금만 더 키워!"
        elif power_ratio >= 0.6:
            power_evaluation = "🔴 많이 부족함. 집중 육성 필요!"
        else:
            power_evaluation = "💀 심각하게 약함! 당장 강화해!"
        
        print(f"📊 전투력 평가: {power_evaluation}")
        print(f"   현재 평균: {avg_power:,} / 권장: {recommended_power:,} ({power_ratio:.1%})")
        
        # 종합 점수 계산
        total_score = (power_ratio * 40) + (equipment_ratio * 30) + (avg_durability * 0.2) + (len(alive_members) * 5)
        
        if total_score >= 80:
            overall_grade = "S급 완벽 파티!"
        elif total_score >= 70:
            overall_grade = "A급 우수 파티"
        elif total_score >= 60:
            overall_grade = "B급 양호 파티"
        elif total_score >= 50:
            overall_grade = "C급 보통 파티"
        else:
            overall_grade = "D급 개선 필요"
        
        print(f"🏆 종합 등급: {overall_grade} (점수: {total_score:.1f}/100)")
        
        # 로바트의 조언들
        bragging_comment = robart.get_bragging_comment()
        print(f"\n🤖 로-바트의 조언:")
        print(f"   {bragging_comment}")
        
        strongest_char = combat_powers[0][0].name if combat_powers else "???"
        weakest_char = combat_powers[-1][0].name if len(combat_powers) > 1 else "???"
        print(f"   • {strongest_char}이(가) 최강! {weakest_char}이(가) 꼴찌!")
        
        if equipment_rankings:
            best_eq = equipment_rankings[0]['char'].name
            worst_eq = equipment_rankings[-1]['char'].name
            print(f"   • 장비왕: {best_eq}, 장비꼴찌: {worst_eq}")
        
        # 구체적 개선 제안
        print(f"\n💡 구체적 개선 제안:")
        
        if power_ratio < 1.0:
            print(f"   • 전투력 부족! {current_level}층에서 레벨업 추천")
        
        for eq_data in equipment_rankings:
            if eq_data['total_durability'] / max(eq_data['durability_count'], 1) < 50:
                print(f"   • {eq_data['char'].name} 장비 수리 시급!")
        
        if tank_count == 0:
            print(f"   • 탱커 없음! 전사/성기사 추가 권장")
        if healer_count == 0:
            print(f"   • 힐러 없음! 신관/드루이드 추가 권장")
        
        print("=" * 100)
        print("🤖 로-바트: 이 정도면 완벽한 분석이지? 역시 나야! (자화자찬)")
        print("=" * 100)
        
    except Exception as e:
        print(f"🤖 로-바트: 어? 뭔가 이상한데? 분석 중 오류: {e}")
        import traceback
        traceback.print_exc()


# ===== 🤖 로-바트 편의 함수들 (모든 기능 쉽게 사용!) =====

def get_robart_cooking_analysis(party_manager, world):
    """🍳 로-바트의 요리 재료 분석"""
    return robart.analyze_cooking_materials_enhanced(party_manager, world)

def get_robart_skill_analysis(members):
    """✨ 로-바트의 스킬 사용 분석"""
    return robart.analyze_skill_usage_enhanced(members)

def get_robart_progression_analysis(members, world):
    """🚀 로-바트의 진행 준비도 분석"""
    return robart.analyze_progression_readiness_enhanced(members, world)

def get_robart_battle_commander(party_members, enemies, battle_state="START"):
    """⚔️ 로-바트의 전투 지휘관"""
    return robart.get_battle_commander_analysis(party_members, enemies, battle_state)

def get_robart_full_analysis(party_manager, world, situation="COMPREHENSIVE"):
    """🔥 로-바트의 모든 분석 기능 한 번에!"""
    return robart.get_ultimate_analysis_suite(party_manager, world, situation)

def get_robart_basic_recommendation(party_manager, world):
    """💡 로-바트의 기본 추천 (간단 버전)"""
    try:
        analysis = robart.analyze_everything(party_manager, world, "FIELD")
        return analysis.get("message", "🤖 로-바트: 뭔가 이상한데? 신중하게 가!")
    except Exception as e:
        return f"🤖 로-바트: 분석 실패! 각자 알아서 해! ({e})"

def robart_says(message_type="random"):
    """🤖 로-바트의 랜덤 멘트"""
    import random
    
    if message_type == "confidence":
        messages = [
            "🤖 로-바트: 내가 있으니까 걱정 마! 천재잖아!",
            "🤖 로-바트: 당연히 내 분석이 맞지~ 의심하지 마!",
            "🤖 로-바트: 이 정도는 식은 죽 먹기야! 내가 누군데!",
            "🤖 로-바트: 역시 나는 천재야! 칭찬해줘!"
        ]
    elif message_type == "warning":
        messages = [
            "🤖 로-바트: 어? 뭔가 이상한데? 조심해!",
            "🤖 로-바트: 위험해! 내 말 들어!",
            "🤖 로-바트: 이건 좀 위험한데... 신중하게!",
            "🤖 로-바트: 경고! 무리하면 안 돼!"
        ]
    elif message_type == "error":
        messages = [
            "🤖 로-바트: 어라? 뭔가 꼬였네? 이상한데?",
            "🤖 로-바트: 오류 발생! 이런 일이 있을 리가...",
            "🤖 로-바트: 어? 계산이 안 맞네? 버그야?",
            "🤖 로-바트: 이런... 예상 못한 상황이야!"
        ]
    else:  # random
        messages = [
            "🤖 로-바트: 오늘도 내가 최고지!",
            "🤖 로-바트: 내 분석을 믿어! 틀릴 리 없어!",
            "🤖 로-바트: 천재의 조언을 들어!",
            "🤖 로-바트: 역시 나야~ 완벽해!",
            "🤖 로-바트: 내가 도와줄게! 고마워해!",
            "🤖 로-바트: 이것도 모르면서... 내가 알려줄게!"
        ]
    
    return random.choice(messages)

    def get_robat_character_analysis(self, character):
        """🤖 로-바트의 캐릭터별 개인 분석"""
        try:
            name = getattr(character, 'name', '???')
            character_class = getattr(character, 'character_class', '???')
            level = getattr(character, 'level', 1)
            current_hp = getattr(character, 'current_hp', 0)
            max_hp = getattr(character, 'max_hp', 1)
            current_mp = getattr(character, 'current_mp', 0)
            max_mp = getattr(character, 'max_mp', 1)
            
            hp_percent = int((current_hp / max_hp) * 100) if max_hp > 0 else 0
            mp_percent = int((current_mp / max_mp) * 100) if max_mp > 0 else 0
            
            # 캐릭터 상태 평가
            if hp_percent >= 90 and mp_percent >= 80:
                return f"완벽한 컨디션! {name} {character_class}는 내가 키운 거나 다름없어! (자랑)"
            elif hp_percent >= 70 and mp_percent >= 60:
                return f"양호한 상태야~ {name}이(가) 잘 버티고 있네! 내 분석대로지!"
            elif hp_percent >= 50:
                return f"좀 위험해 보이는데? {name} {character_class}는 빨리 회복이 필요해!"
            elif hp_percent >= 30:
                return f"이야! {name}이(가) 위험해! 내가 말했잖아, 조심하라고!"
            else:
                return f"아이고! {name}이(가) 거의 죽어가네! 빨리 치료해!"
                
        except Exception:
            return "어? 분석이 잘 안 되네... 이상한데?"

    def get_robat_party_analysis(self, party_manager):
        """🤖 로-바트의 파티 종합 분석"""
        try:
            if not party_manager or not hasattr(party_manager, 'members'):
                return "파티가 없네? 혼자서는 힘들 텐데..."
            
            members = party_manager.members
            if not members:
                return "파티원이 없어? 빨리 동료를 구해!"
            
            # 파티 분석
            total_members = len(members)
            alive_members = len([m for m in members if getattr(m, 'is_alive', True)])
            total_hp = sum(getattr(m, 'current_hp', 0) for m in members if getattr(m, 'is_alive', True))
            max_total_hp = sum(getattr(m, 'max_hp', 1) for m in members if getattr(m, 'is_alive', True))
            
            party_hp_percent = int((total_hp / max_total_hp) * 100) if max_total_hp > 0 else 0
            
            # 직업 분포 분석
            classes = [getattr(m, 'character_class', '???') for m in members]
            class_counts = {}
            for cls in classes:
                class_counts[cls] = class_counts.get(cls, 0) + 1
            
            # 로-바트의 종합 평가
            analysis_parts = []
            
            # 파티 규모 평가
            if total_members >= 4:
                analysis_parts.append("파티 규모는 완벽해! 4명이면 충분하지!")
            elif total_members >= 3:
                analysis_parts.append("3명도 나쁘지 않아~ 하지만 4명이 더 좋을 텐데?")
            elif total_members >= 2:
                analysis_parts.append("2명이면 좀 부족할 수도... 동료를 더 구해봐!")
            else:
                analysis_parts.append("혼자서는 힘들어! 빨리 파티원을 구해!")
            
            # 생존률 평가
            survival_rate = (alive_members / total_members) * 100 if total_members > 0 else 0
            if survival_rate == 100:
                analysis_parts.append("모두 살아있네! 역시 내 조언을 잘 들었구나!")
            elif survival_rate >= 75:
                analysis_parts.append("대부분 살아있어서 다행이야~")
            elif survival_rate >= 50:
                analysis_parts.append("절반 정도... 좀 위험한데?")
            else:
                analysis_parts.append("이런! 거의 다 죽었네! 빨리 부활시켜!")
            
            # 체력 상태 평가
            if party_hp_percent >= 80:
                analysis_parts.append("파티 체력도 충분해! 완벽한 상태야!")
            elif party_hp_percent >= 60:
                analysis_parts.append("체력이 좀 부족하긴 하지만 괜찮아~")
            elif party_hp_percent >= 40:
                analysis_parts.append("체력이 위험해! 회복 아이템 좀 써봐!")
            else:
                analysis_parts.append("체력이 너무 위험해! 즉시 치료가 필요해!")
            
            # 직업 조합 평가 (간단하게)
            has_warrior = any('전사' in cls or '기사' in cls for cls in classes)
            has_mage = any('마법' in cls or '메이지' in cls for cls in classes)
            has_healer = any('신관' in cls or '바드' in cls for cls in classes)
            
            if has_warrior and has_mage and has_healer:
                analysis_parts.append("직업 조합도 완벽해! 탱커, 딜러, 힐러가 다 있네!")
            elif has_warrior and has_mage:
                analysis_parts.append("전투는 강하지만 힐러가 없네... 회복 아이템을 챙겨!")
            elif has_warrior and has_healer:
                analysis_parts.append("안정적이긴 하지만 화력이 부족할 수도...")
            else:
                analysis_parts.append("직업 조합을 다시 생각해봐! 균형이 중요해!")
            
            return " ".join(analysis_parts)
            
        except Exception as e:
            return f"파티 분석 중 오류가... 이상한데? ({e})"

# ===== 전역 로-바트 인스턴스와 접근자 =====

def get_robart():
    """🤖 로-바트 인스턴스 반환"""
    return robart

def robart_analyze_all(party_manager, world, show_details=True):
    """🔥 로-바트의 완전체 분석 (상세 표시 옵션)"""
    if show_details:
        # 상세 분석 + 화면 출력
        show_detailed_party_analysis(party_manager, world)
    else:
        # 간단 분석만 반환
        return get_robart_full_analysis(party_manager, world)

# 별칭 함수들 (사용 편의성)
robart_cooking = get_robart_cooking_analysis
robart_skills = get_robart_skill_analysis  
robart_progression = get_robart_progression_analysis
robart_battle = get_robart_battle_commander
robart_ultimate = get_robart_full_analysis
