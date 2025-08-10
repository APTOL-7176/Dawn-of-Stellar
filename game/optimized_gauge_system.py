"""
최적화된 게이지 시스템
깜빡임 최소화와 성능 향상을 위한 통합 게이지 모듈
중복 표시 방지 시스템 포함
"""

from .color_text import Color  # color_text.Color로 통일
import time


# 안전한 색상 상수 정의
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'DIM': '\033[2m', 
    'UNDERLINE': '\033[4m',
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'BRIGHT_BLACK': '\033[90m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_YELLOW': '\033[93m',
    'BRIGHT_BLUE': '\033[94m',
    'BRIGHT_MAGENTA': '\033[95m',
    'BRIGHT_CYAN': '\033[96m',
    'BRIGHT_WHITE': '\033[97m',
    'BG_BLACK': '\033[40m',
    'BG_RED': '\033[41m',
    'BG_GREEN': '\033[42m',
    'BG_YELLOW': '\033[43m',
    'BG_BLUE': '\033[44m',
    'BG_MAGENTA': '\033[45m',
    'BG_CYAN': '\033[46m',
    'BG_WHITE': '\033[47m'
}

def get_color(color_name):
    """안전한 색상 코드 반환"""
    return COLORS.get(color_name, '')

class OptimizedGaugeSystem:
    """최적화된 게이지 시스템 클래스"""
    
    # 클래스 변수: 마지막 게이지 표시 시간 추적
    _last_gauge_display_time = {}
    _gauge_display_cooldown = 0.1  # 0.1초 간격으로 제한
    
    @staticmethod
    def _can_display_gauge(character_name: str) -> bool:
        """게이지 표시 가능 여부 확인 (중복 방지)"""
        current_time = time.time()
        last_time = OptimizedGaugeSystem._last_gauge_display_time.get(character_name, 0)
        
        # 쿨다운 시간이 지났는지 확인만 하고, 시간은 업데이트하지 않음
        return current_time - last_time >= OptimizedGaugeSystem._gauge_display_cooldown
    
    @staticmethod
    def _update_display_time(character_name: str):
        """게이지 표시 시간 업데이트"""
        OptimizedGaugeSystem._last_gauge_display_time[character_name] = time.time()
    
    @staticmethod
    def _force_display_gauge(character_name: str):
        """강제로 게이지 표시 허용 (쿨다운 무시)"""
        # 쿨다운을 초과한 시간으로 설정하여 다음 체크에서 통과하도록 함
        OptimizedGaugeSystem._last_gauge_display_time[character_name] = time.time() - OptimizedGaugeSystem._gauge_display_cooldown - 0.01
    
    @staticmethod
    def display_brv_change(character, old_brv: int, new_brv: int, change_reason: str = "") -> str:
        """BRV 변화 표시 (중복 방지)"""
        character_name = getattr(character, 'name', 'Unknown')
        
        # 중복 표시 방지 체크
        if not OptimizedGaugeSystem._can_display_gauge(character_name):
            return ""  # 중복이면 아무것도 표시하지 않음
        
        # BRV 변화량 계산
        brv_change = new_brv - old_brv
        change_symbol = "⬆️" if brv_change > 0 else "⬇️" if brv_change < 0 else "➡️"
        change_text = f"({brv_change:+d})" if brv_change != 0 else ""
        
        # 게이지 생성
        max_brv = getattr(character, 'max_brave_points', 9999)
        brv_gauge = OptimizedGaugeSystem.create_clean_gauge(new_brv, max_brv, 20, "brv")
        
        # 색상 설정
        if new_brv == 0:
            brv_color = get_color('RED')
        elif new_brv <= 299:
            brv_color = get_color('YELLOW')
        elif new_brv == max_brv:
            brv_color = get_color('BRIGHT_MAGENTA')
        else:
            brv_color = get_color('BRIGHT_YELLOW')
        
        # 결과 문자열
        result = f"💫 {character_name}: ⚡ {brv_gauge} {brv_color}{new_brv}/{max_brv}{get_color('RESET')}"
        if change_text:
            result += f" {change_text} {change_symbol}"
        if change_reason:
            result += f" {change_reason}"
        
        # 성공적으로 표시했으므로 시간 업데이트
        OptimizedGaugeSystem._update_display_time(character_name)
        
        return result
    
    @staticmethod
    def create_compact_character_status(character, shadow_system=None) -> str:
        """컴팩트한 캐릭터 상태 표시 생성"""
        # 기본 정보
        level = getattr(character, 'level', 1)
        name = getattr(character, 'name', '알 수 없음')
        job = getattr(character, 'character_class', '모험가')  # job 대신 character_class 사용
        
        # 직업 아이콘 (main.py와 통일) - 이모지 깨짐 방지
        job_icons = {
            # 기본 4클래스
            "전사": "⚔️",
            "아크메이지": "🔮",
            "궁수": "🏹",
            "도적": "🗡️",
            
            # 추가 클래스들
            "성기사": "🛡️",
            "암흑기사": "💀",
            "몽크": "👊",
            "바드": "🎵",
            "네크로맨서": "☠️",
            "용기사": "🐉",
            "검성": "⚡",
            "정령술사": "🌟",
            "암살자": "🌑",
            "기계공학자": "🔧",
            "무당": "🔯",
            "해적": "🏴‍☠️",
            "사무라이": "🗾",
            "드루이드": "🌿",
            "철학자": "📚",
            "시간술사": "⏰",
            "연금술사": "⚗️",
            "검투사": "🏛️",
            "기사": "🐎",
            "신관": "⛪",
            "마검사": "✨",
            "차원술사": "🌌",
            "광전사": "🔥",
            
            # 기타 (이모지 깨짐 방지)
            "모험가": "🎭",
            "적": "🔸",
            "Enemy": "🔸"
        }
        job_icon = job_icons.get(job, "👤")  # 기본값: 👤
        
        # HP/MP 정보
        hp_current = getattr(character, 'current_hp', 0)
        hp_max = getattr(character, 'max_hp', 1)
        mp_current = getattr(character, 'current_mp', 0)
        mp_max = getattr(character, 'max_mp', 1)
        brv_current = getattr(character, 'brv', 0)
        if brv_current == 0:
            # 다른 가능한 BRV 속성명들 확인
            brv_current = getattr(character, 'brave_points', 0)
            if brv_current == 0:
                brv_current = getattr(character, 'current_brv', 0)
            if brv_current == 0:
                brv_current = getattr(character, 'brave', 0)
        speed = getattr(character, 'speed', 50)
        
        # ATB 게이지 정보 - 2025.08.10 수정: ATB_MAX=2000 맞춤
        atb_current = getattr(character, 'atb_gauge', 0)
        atb_max = 2000  # ATB_MAX 상수값 사용 (brave_combat.py와 동일)
        atb_ratio = atb_current / atb_max if atb_max > 0 else 0
        
        # 그림자 정보 (암살자만)
        shadow_display = ""
        if shadow_system and job == "암살자":
            shadow_count = shadow_system.get_shadow_count(character)
            if shadow_count > 0:
                shadow_icons = "🌑 " * shadow_count
                shadow_display = f" {shadow_icons}{shadow_count}"
        
        # 🛡️ 전사 자세 정보 (전사만)
        stance_display = ""
        if job == "전사" or "전사" in job:
            try:
                from .warrior_system import get_warrior_system
                warrior_system = get_warrior_system()
                stance_icon = warrior_system.get_stance_icon(character)
                stance_display = f" {stance_icon}"
            except Exception:
                pass  # 전사 시스템을 사용할 수 없는 경우 무시
        
        # 🎯 캐릭터별 기믹 표시 (모든 직업) - 이모지 + 영어 대문자 형식 + 강제 표시 (0도 표시)
        mechanics_display = ""
        character_class = getattr(character, 'character_class', '모험가')  # 캐릭터 클래스 가져오기
        
        # 궁수 조준 포인트 - 항상 표시
        if character_class == "궁수":
            aim_points = getattr(character, 'aim_points', 0)
            precision_points = getattr(character, 'precision_points', 0) 
            mechanics_display += f" 🎯AIM: {aim_points + precision_points}"
        
        # 도적 독 스택 - 항상 표시
        elif character_class == "도적":
            poison_stacks = getattr(character, 'poison_stacks', 0)
            venom_power = getattr(character, 'venom_power', 0)
            mechanics_display += f" ☠️VENOM: {poison_stacks + venom_power}"
        
        # 암살자 그림자 - 항상 표시
        elif character_class == "암살자":
            shadow_count = getattr(character, 'shadow_count', 0)
            shadows = getattr(character, 'shadows', 0)
            mechanics_display += f" 👤SHADOW: {shadow_count + shadows}"
        
        # 검성 검기 - 항상 표시
        elif character_class == "검성":
            sword_aura = getattr(character, 'sword_aura', 0)
            sword_aura_stacks = getattr(character, 'sword_aura_stacks', 0)
            mechanics_display += f" ⚔️AURA: {sword_aura + sword_aura_stacks}"
        
        # 바드 멜로디 - 항상 표시 (DO, RE, MI 형태)
        elif character_class == "바드":
            # melody_notes 리스트가 있으면 우선 사용
            melody_notes_list = getattr(character, 'melody_notes', None)
            if melody_notes_list and isinstance(melody_notes_list, list) and len(melody_notes_list) > 0:
                # 음표 번호를 음계명으로 변환
                note_names = ["DO", "RE", "MI", "FA", "SO", "LA", "TI"]
                melody_display = "/".join([note_names[note] for note in melody_notes_list if 0 <= note < len(note_names)])
                if melody_display:
                    mechanics_display += f" 🎵MELODY: {melody_display}"
                else:
                    mechanics_display += f" 🎵MELODY: 0"
            else:
                # 기존 방식 (melody_stacks 사용)
                melody_stacks = getattr(character, 'melody_stacks', 0)
                song_power = getattr(character, 'song_power', 0)
                total_melody = melody_stacks + song_power
                
                # DO, RE, MI, FA, SO, LA, TI 음계 표시 (7음계, 0~7)
                melody_notes = ["", "DO", "RE", "MI", "FA", "SO", "LA", "TI"]
                if total_melody > 0 and total_melody < len(melody_notes):
                    mechanics_display += f" 🎵MELODY: {melody_notes[total_melody]}"
                elif total_melody >= len(melody_notes):
                    mechanics_display += f" 🎵HARMONY: {total_melody}"  # 7을 넘으면 하모니
                else:
                    mechanics_display += f" 🎵MELODY: {total_melody}"
        
        # 광전사 분노 - 항상 표시
        elif character_class == "광전사":
            rage_stacks = getattr(character, 'rage_stacks', 0)
            berserk_level = getattr(character, 'berserk_level', 0)
            mechanics_display += f" 😡RAGE: {rage_stacks + berserk_level}"
        
        # 아크메이지 원소 카운트 - 항상 표시
        elif character_class == "아크메이지":
            fire_count = getattr(character, 'fire_count', 0)
            ice_count = getattr(character, 'ice_count', 0)
            lightning_count = getattr(character, 'lightning_count', 0)
            mechanics_display += f" 🔥FIRE: {fire_count}"
            if ice_count > 0 or fire_count == 0:  # 공간 절약
                mechanics_display += f" ❄️ICE: {ice_count}"
            if lightning_count > 0 or (fire_count == 0 and ice_count == 0):
                mechanics_display += f" ⚡THUNDER: {lightning_count}"
        
        # 몽크 기 에너지 - 항상 표시
        elif character_class == "몽크":
            chi_points = getattr(character, 'chi_points', 0)
            ki_energy = getattr(character, 'ki_energy', 0)
            strike_marks = getattr(character, 'strike_marks', 0)
            mechanics_display += f" 🥋CHI: {chi_points + ki_energy + strike_marks}"
        
        # 전사 자세/스탠스 - 항상 표시 (6가지 태세)
        elif character_class == "전사":
            # current_stance 숫자나 warrior_stance 문자열 둘 다 지원
            current_stance = getattr(character, 'current_stance', None)
            warrior_stance = getattr(character, 'warrior_stance', None)
            warrior_focus = getattr(character, 'warrior_focus', 0)
            
            # current_stance 숫자가 있으면 우선 사용
            if current_stance is not None:
                stance_names = ["⚔️ATK", "🛡️DEF", "⚖️BAL", "💀BERSERK", "🛠️GUARD", "⚡SPEED"]
                if 0 <= current_stance < len(stance_names):
                    mechanics_display += f" {stance_names[current_stance]}"
                else:
                    mechanics_display += f" 🔶STANCE: UNKNOWN"
            # warrior_stance 문자열 사용
            elif warrior_stance == 'attack':
                mechanics_display += f" ⚔️STANCE: ATK"
            elif warrior_stance == 'defense':
                mechanics_display += f" 🛡️STANCE: DEF"
            elif warrior_stance == 'balanced':
                mechanics_display += f" ⚖️STANCE: BAL"
            elif warrior_stance == 'berserker':
                mechanics_display += f" 💀STANCE: BERSERK"
            elif warrior_stance == 'guardian':
                mechanics_display += f" 🛠️STANCE: GUARD"
            elif warrior_stance == 'speed':
                mechanics_display += f" ⚡STANCE: SPEED"
            else:
                # 기본값 제거하고 실제 스탠스 확인
                stance_attr = getattr(character, 'stance', None)
                if stance_attr:
                    mechanics_display += f" ⚖️STANCE: {stance_attr.upper()}"
                else:
                    mechanics_display += f" ⚖️STANCE: BAL"  # 최후 폴백
            if warrior_focus > 0:
                mechanics_display += f" 🎯FOCUS: {warrior_focus}"
        
        # 용기사 드래곤 파워 - 항상 표시
        elif character_class == "용기사":
            dragon_marks = getattr(character, 'dragon_marks', 0)
            dragon_power = getattr(character, 'dragon_power', 0)
            mechanics_display += f" 🐉DRAGON: {dragon_marks + dragon_power}"
        
        # 검투사 투기장 포인트 - 항상 표시
        elif character_class == "검투사":
            arena_points = getattr(character, 'arena_points', 0)
            gladiator_experience = getattr(character, 'gladiator_experience', 0)
            mechanics_display += f" 🏟️ARENA: {arena_points + gladiator_experience}"
        
        # 네크로맨서 영혼/언데드 파워 - 항상 표시
        elif character_class == "네크로맨서":
            soul_count = getattr(character, 'soul_count', 0)
            undead_power = getattr(character, 'undead_power', 0)
            necromancy_stacks = getattr(character, 'necromancy_stacks', 0)
            mechanics_display += f" 👻SOUL: {soul_count + undead_power + necromancy_stacks}"
        
        # 정령술사 정령 동조 - 항상 표시
        elif character_class == "정령술사":
            spirit_attunement = getattr(character, 'spirit_attunement', 0)
            elemental_harmony = getattr(character, 'elemental_harmony', 0)
            spirit_bond = getattr(character, 'spirit_bond', 0)
            mechanics_display += f" 🌟SPIRIT: {spirit_attunement + elemental_harmony + spirit_bond}"
        
        # 시간술사 시공 에너지 - 항상 표시
        elif character_class == "시간술사":
            time_energy = getattr(character, 'time_energy', 0)
            chrono_power = getattr(character, 'chrono_power', 0)
            temporal_stacks = getattr(character, 'temporal_stacks', 0)
            mechanics_display += f" 🕰️TIME: {time_energy + chrono_power + temporal_stacks}"
        
        # 연금술사 화학 반응 - 항상 표시
        elif character_class == "연금술사":
            reaction_stacks = getattr(character, 'reaction_stacks', 0)
            alchemy_power = getattr(character, 'alchemy_power', 0)
            chemical_energy = getattr(character, 'chemical_energy', 0)
            mechanics_display += f" ⚗️REACTION: {reaction_stacks + alchemy_power + chemical_energy}"
        
        # 차원술사 차원 균열 - 항상 표시
        elif character_class == "차원술사":
            dimension_rifts = getattr(character, 'dimension_rifts', 0)
            dimension_power = getattr(character, 'dimension_power', 0)
            dimensional_energy = getattr(character, 'dimensional_energy', 0)
            mechanics_display += f" 🌀RIFT: {dimension_rifts + dimension_power + dimensional_energy}"
        
        # 기계공학자 오버차지/기계 - 항상 표시
        elif character_class == "기계공학자":
            overcharge_stacks = getattr(character, 'overcharge_stacks', 0)
            mechanical_power = getattr(character, 'mechanical_power', 0)
            tech_energy = getattr(character, 'tech_energy', 0)
            mechanics_display += f" 🔧CHARGE: {overcharge_stacks + mechanical_power + tech_energy}"
        
        # 무당 영력 - 항상 표시
        elif character_class == "무당":
            spiritual_power = getattr(character, 'spiritual_power', 0)
            shaman_energy = getattr(character, 'shaman_energy', 0)
            spirit_power = getattr(character, 'spirit_power', 0)
            mechanics_display += f" 🔮MYSTIC: {spiritual_power + shaman_energy + spirit_power}"
        
        # 해적 보물/전리품 - 항상 표시
        elif character_class == "해적":
            treasure_stacks = getattr(character, 'treasure_stacks', 0)
            pirate_loot = getattr(character, 'pirate_loot', 0)
            plunder_count = getattr(character, 'plunder_count', 0)
            mechanics_display += f" 🏴‍☠️TREASURE: {treasure_stacks + pirate_loot + plunder_count}"
        
        # 사무라이 검의 도/기 - 항상 표시
        elif character_class == "사무라이":
            bushido_spirit = getattr(character, 'bushido_spirit', 0)
            sword_spirit = getattr(character, 'sword_spirit', 0)
            samurai_focus = getattr(character, 'samurai_focus', 0)
            mechanics_display += f" ⛩️BUSHIDO: {bushido_spirit + sword_spirit + samurai_focus}"
        
        # 드루이드 자연의 힘 - 항상 표시
        elif character_class == "드루이드":
            nature_power = getattr(character, 'nature_power', 0)
            druid_harmony = getattr(character, 'druid_harmony', 0)
            wild_energy = getattr(character, 'wild_energy', 0)
            mechanics_display += f" 🌿NATURE: {nature_power + druid_harmony + wild_energy}"
        
        # 철학자 깨달음/지혜 - 항상 표시
        elif character_class == "철학자":
            wisdom_stacks = getattr(character, 'wisdom_stacks', 0)
            enlightenment = getattr(character, 'enlightenment', 0)
            philosophy_power = getattr(character, 'philosophy_power', 0)
            mechanics_display += f" 📚WISDOM: {wisdom_stacks + enlightenment + philosophy_power}"
        
        # 기사 명예/기사도 - 항상 표시
        elif character_class == "기사":
            honor_points = getattr(character, 'honor_points', 0)
            chivalry_power = getattr(character, 'chivalry_power', 0)
            knight_spirit = getattr(character, 'knight_spirit', 0)
            mechanics_display += f" 🏇HONOR: {honor_points + chivalry_power + knight_spirit}"
        
        # 신관 신앙심/성력 - 항상 표시
        elif character_class == "신관":
            faith_power = getattr(character, 'faith_power', 0)
            divine_energy = getattr(character, 'divine_energy', 0)
            holy_power = getattr(character, 'holy_power', 0)
            faith_points = getattr(character, 'faith_points', 0)
            mechanics_display += f" ⛪FAITH: {faith_power + divine_energy + holy_power + faith_points}"
        
        # 마검사 마검 동조 - 항상 표시
        elif character_class == "마검사":
            magic_sword_sync = getattr(character, 'magic_sword_sync', 0)
            mystic_blade_power = getattr(character, 'mystic_blade_power', 0)
            sword_magic_fusion = getattr(character, 'sword_magic_fusion', 0)
            mechanics_display += f" 🗡️SYNC: {magic_sword_sync + mystic_blade_power + sword_magic_fusion}"
        
        # 성기사 성스러운 힘 - 항상 표시
        elif character_class == "성기사":
            holy_blessing = getattr(character, 'holy_blessing', 0)
            paladin_power = getattr(character, 'paladin_power', 0)
            sacred_energy = getattr(character, 'sacred_energy', 0)
            holy_power = getattr(character, 'holy_power', 0)
            mechanics_display += f" ✨HOLY: {holy_blessing + paladin_power + sacred_energy + holy_power}"
        
        # 암흑기사 어둠의 힘 - 항상 표시
        elif character_class == "암흑기사":
            dark_power = getattr(character, 'dark_power', 0)
            shadow_energy = getattr(character, 'shadow_energy', 0)
            darkness_stacks = getattr(character, 'darkness_stacks', 0)
            mechanics_display += f" 🌑DARK: {dark_power + shadow_energy + darkness_stacks}"
        
        # 상처 시스템 - 0이 아닐 때만 표시 (이모지 없이)
        if hasattr(character, 'wounds') and character.wounds > 0:
            mechanics_display += f" WOUND: {character.wounds}"
        
        # 암살자 그림자 (shadow_system에서 가져온 것과 중복 방지)
        # HP/MP 게이지 생성 (10칸)
        hp_gauge = OptimizedGaugeSystem.create_visual_gauge(hp_current, hp_max, 10)
        mp_gauge = OptimizedGaugeSystem.create_visual_gauge(mp_current, mp_max, 10)
        
        # ATB 게이지 생성 (10칸) - 캐스팅 상태 고려
        is_casting = getattr(character, 'is_casting', False)
        if is_casting:
            # 캐스팅 중일 때는 캐스팅 진행률 표시
            casting_duration = getattr(character, 'casting_duration', 250)
            casting_start_atb = getattr(character, 'casting_start_atb', 0)
            
            if casting_duration > 0 and casting_start_atb >= 0:
                # ATB 기반 캐스팅 진행도 계산
                casting_elapsed_atb = atb_current - casting_start_atb
                casting_progress = min(1.0, max(0.0, casting_elapsed_atb / casting_duration))
                casting_percent = int(casting_progress * 100)
            else:
                casting_percent = 0
            
            atb_gauge = OptimizedGaugeSystem.create_visual_gauge(casting_percent, 100, 10)
            atb_status = f"🔮 {casting_percent}%"  # 더 명확하게 표시
        else:
            # 일반 ATB 게이지 - 2025.08.10 수정: ATB_MAX=2000 기준으로 수정
            atb_gauge = OptimizedGaugeSystem.create_visual_gauge(atb_current, 2000, 10)
            
            # ATB 상태 표시 - READY 임계값 1000 사용
            if atb_current >= 1000:
                atb_status = "⚡ READY"
            else:
                atb_percent = int((atb_current / 1000) * 100)  # 1000 기준으로 백분율 계산
                atb_status = f"⏳ {atb_percent}%"
        
        # 최종 문자열 조합
        status_line = f"▶ {job_icon} Lv.{level} {name}{shadow_display}{stance_display}{mechanics_display}\n"
        status_line += f"💚 HP: {hp_current} / {hp_max} {hp_gauge} | 💙 MP: {mp_current} / {mp_max} {mp_gauge} | ⚡ BRV: {brv_current} |\n"
        status_line += f"⌛ TIME: {atb_gauge} {atb_status} | SPD: {speed}"
        
        return status_line
    
    @staticmethod
    def create_visual_gauge(current: int, maximum: int, length: int = 10) -> str:
        """시각적 게이지 생성 (█ 문자 사용)"""
        if maximum <= 0:
            return "{" + "░" * length + "}"
        
        ratio = min(1.0, current / maximum)
        filled_length = int(ratio * length)
        empty_length = length - filled_length
        
        filled = "█" * filled_length
        empty = "░" * empty_length
        
        return "{" + filled + empty + "}"
    
    @staticmethod
    def create_clean_gauge(current: int, maximum: int, length: int = 10, gauge_type: str = "hp", hp_ratio: float = 1.0, mp_ratio: float = 1.0, is_casting: bool = False, atb_speed_state: str = "normal") -> str:
        """정교한 색상 로직을 가진 게이지 생성 - 길이 보장 강화"""
        if maximum <= 0:
            return "{" + " " * length + "}"
            
        # 정확한 비율 계산
        ratio = min(1.0, current / maximum)
        
        # 게이지 타입별 색상 설정
        if gauge_type.lower() == "hp":
            # HP 하트 색상에 따른 게이지 색상
            if hp_ratio > 0.8:
                color = get_color('BRIGHT_GREEN')
            elif hp_ratio > 0.6:
                color = get_color('GREEN')  
            elif hp_ratio > 0.4:
                color = get_color('YELLOW')
            elif hp_ratio > 0.2:
                color = get_color('BRIGHT_RED')
            else:
                color = get_color('RED')
        elif gauge_type.lower() == "mp":
            # MP 하트 색상에 따른 게이지 색상
            if mp_ratio > 0.8:
                color = get_color('BRIGHT_CYAN')
            elif mp_ratio > 0.6:
                color = get_color('CYAN')  
            elif mp_ratio > 0.4:
                color = get_color('BLUE')
            elif mp_ratio > 0.2:
                color = get_color('MAGENTA')
            else:
                color = get_color('RED')
        elif gauge_type.lower() == "brv":
            # BRV 게이지 색상 로직
            if current == 0:
                color = get_color('RED')
            elif current <= 299:
                color = get_color('YELLOW')
            elif current == maximum:
                color = get_color('BRIGHT_MAGENTA')
            else:
                color = get_color('BRIGHT_YELLOW')
        elif gauge_type.lower() == "atb":
            # ATB 게이지 색상 로직
            if is_casting:
                color = get_color('BRIGHT_MAGENTA')
            elif ratio >= 1.0:
                color = get_color('YELLOW')  # 주황색 (꽉 참)
            elif atb_speed_state == "fast":
                color = get_color('BRIGHT_CYAN')  # 밝은 하늘색 (빠른 상태)
            elif atb_speed_state == "slow":
                color = get_color('BLUE')  # 파란색 (느린 상태)
            elif atb_speed_state == "stunned":
                color = get_color('WHITE')  # 회색 (기절/정지)
            else:
                color = get_color('CYAN')  # 하늘색 (기본)
        else:
            color = get_color('WHITE')
        
        # 완전히 새로운 게이지 생성 로직 - 길이 일관성 보장
        filled_length = ratio * length  # 실제 채워야 할 길이 (소수점 포함)
        full_blocks = int(filled_length)  # 완전히 채워진 블록 수
        partial_amount = filled_length - full_blocks  # 부분 블록의 채움 정도
        
        gauge_content = ""
        
        # 1. 완전히 채워진 블록들 추가
        if full_blocks > 0:
            gauge_content += color + "█" * full_blocks + get_color('RESET')
        
        # 2. 부분 블록 처리 (정확한 1개 블록 공간만 사용)
        if full_blocks < length and partial_amount > 0:
            if partial_amount >= 0.875:
                gauge_content += color + "▉" + get_color('RESET')
            elif partial_amount >= 0.75:
                gauge_content += color + "▊" + get_color('RESET')
            elif partial_amount >= 0.625:
                gauge_content += color + "▋" + get_color('RESET')
            elif partial_amount >= 0.5:
                gauge_content += color + "▌" + get_color('RESET')
            elif partial_amount >= 0.375:
                gauge_content += color + "▍" + get_color('RESET')
            elif partial_amount >= 0.25:
                gauge_content += color + "▎" + get_color('RESET')
            elif partial_amount >= 0.125:
                gauge_content += color + "▏" + get_color('RESET')
            else:
                # 부분 블록이 너무 작으면 빈 공간으로 처리
                gauge_content += " "
            used_blocks = full_blocks + 1
        else:
            used_blocks = full_blocks
        
        # 3. 나머지 공간은 빈 블록으로 채움
        remaining_blocks = length - used_blocks
        if remaining_blocks > 0:
            gauge_content += " " * remaining_blocks
        
        return "{" + gauge_content + "}"
    
    @staticmethod
    def create_status_line(character, current_char=None, all_characters=None) -> str:
        """정확한 색상 로직을 가진 캐릭터 상태 표시"""
        # 현재 턴 캐릭터 표시
        arrow = "▶ " if character == current_char else "  "
        
        # 기본 정보
        level = getattr(character, 'level', 1)
        name = character.name
        hp = character.current_hp
        max_hp = character.max_hp
        mp = character.current_mp
        max_mp = character.max_mp
        brv = getattr(character, 'brave_points', 0)
        max_brv = getattr(character, 'max_brave_points', 9999)
        speed = getattr(character, 'speed', 50)
        
        # 비율 계산
        hp_ratio = hp / max_hp if max_hp > 0 else 0
        mp_ratio = mp / max_mp if max_mp > 0 else 0
        
        # 캐스팅 상태 체크
        is_casting = hasattr(character, 'is_casting') and character.is_casting
        
        # 평균 속도 계산 (전체 캐릭터 기준)
        if all_characters:
            avg_speed = sum(getattr(char, 'speed', 50) for char in all_characters) / len(all_characters)
        else:
            avg_speed = 50
        
        # ATB 속도 상태 판단
        if hasattr(character, 'is_stunned') and character.is_stunned:
            atb_speed_state = "stunned"
        elif is_casting:
            atb_speed_state = "casting"
        elif speed >= avg_speed * 1.3:
            atb_speed_state = "fast"
        elif speed <= avg_speed * 0.7:
            atb_speed_state = "slow"
        else:
            atb_speed_state = "normal"
        
        # 클래스 아이콘 (main.py와 통일)
        character_class = getattr(character, 'character_class', '모험가')
        class_icons = {
            # 기본 4클래스
            "전사": "⚔️",
            "아크메이지": "🔮",
            "궁수": "🏹",
            "도적": "🗡️",
            
            # 추가 클래스들
            "성기사": "🛡️",
            "암흑기사": "💀",
            "몽크": "👊",
            "바드": "🎵",
            "네크로맨서": "☠️",
            "용기사": "🐉",
            "검성": "⚡",
            "정령술사": "🌟",
            "암살자": "🌑",
            "기계공학자": "🔧",
            "무당": "🔯",
            "해적": "🏴‍☠️",
            "사무라이": "🗾",
            "드루이드": "🌿",
            "철학자": "📜",
            "시간술사": "⏰",
            "연금술사": "⚗️",
            "검투사": "🏛️",
            "기사": "🐎",
            "신관": "⛪",
            "마검사": "✨",
            "차원술사": "🌌",
            "광전사": "💥",
            
            # 기타
            "모험가": "🎭", 
            "Enemy": "👹"
        }
        class_icon = class_icons.get(character_class, '👤')
        
        # 색상 설정
        # 이름 색상 (턴이 온 캐릭터는 하늘색)
        name_color = get_color('BRIGHT_CYAN') if character == current_char else get_color('BRIGHT_WHITE')
        
        # HP 하트 색상과 이모지
        if hp_ratio > 0.8:
            hp_heart_color = get_color('BRIGHT_GREEN')
            hp_heart = "💚"  # 녹색 하트
        elif hp_ratio > 0.6:
            hp_heart_color = get_color('GREEN')
            hp_heart = "💚"  # 녹색 하트
        elif hp_ratio > 0.4:
            hp_heart_color = get_color('YELLOW')
            hp_heart = "💛"  # 노란 하트
        elif hp_ratio > 0.2:
            hp_heart_color = get_color('BRIGHT_RED')
            hp_heart = "🧡"  # 주황 하트
        else:
            hp_heart_color = get_color('RED')
            hp_heart = "❤️"  # 빨간 하트
        
        # MP 하트 색상과 이모지
        if mp_ratio > 0.8:
            mp_heart_color = get_color('BRIGHT_CYAN')
            mp_heart = "💙"  # 파란 하트
        elif mp_ratio > 0.6:
            mp_heart_color = get_color('CYAN')
            mp_heart = "💙"  # 파란 하트
        elif mp_ratio > 0.4:
            mp_heart_color = get_color('BLUE')
            mp_heart = "💜"  # 보라 하트
        elif mp_ratio > 0.2:
            mp_heart_color = get_color('MAGENTA')
            mp_heart = "💜"  # 보라 하트
        else:
            mp_heart_color = get_color('RED')
            mp_heart = "❤️"  # 빨간 하트
        
        # BRV 색상
        if brv == 0:
            brv_color = get_color('RED')
        elif brv <= 299:
            brv_color = get_color('YELLOW')  # 주황색
        elif brv == max_brv:
            brv_color = get_color('BRIGHT_MAGENTA')
        else:
            brv_color = get_color('BRIGHT_YELLOW')
        
        # SPD 숫자 색상
        if speed >= avg_speed * 1.3:
            spd_color = get_color('GREEN')
        elif speed <= avg_speed * 0.7:
            spd_color = get_color('RED')
        else:
            spd_color = get_color('WHITE')
        
        # 게이지 생성
        hp_gauge = OptimizedGaugeSystem.create_clean_gauge(hp, max_hp, 10, "hp", hp_ratio, mp_ratio, is_casting, atb_speed_state)
        mp_gauge = OptimizedGaugeSystem.create_clean_gauge(mp, max_mp, 10, "mp", hp_ratio, mp_ratio, is_casting, atb_speed_state)
        
        # ATB 게이지 처리 - 2025.08.10 수정: ATB_MAX=2000, READY=1000 맞춤
        atb_gauge = max(0, getattr(character, 'atb_gauge', 0))  # 자연스러운 범위 (제한 없음)
        atb_ready_threshold = 1000  # ATB_READY_THRESHOLD와 동일
        atb_max_threshold = 2000  # ATB_MAX와 동일
        
        # 상태이상 체크 - 영어 대문자로 표시
        status_effects = []
        
        # BREAK 상태 우선 확인
        if hasattr(character, 'is_broken') and character.is_broken:
            status_effects.append(f"{get_color('RED')}BREAK{get_color('RESET')}")
            
        # 독 상태는 여러 방법으로 체크 - 강력한 방법
        poison_detected = False
        if hasattr(character, 'status_manager') and character.status_manager:
            if character.status_manager.has_status('독'):
                poison_detected = True
                status_effects.append(f"{get_color('BRIGHT_GREEN')}POISON{get_color('RESET')}")
        
        if not poison_detected and hasattr(character, 'is_poisoned') and character.is_poisoned:
            poison_detected = True
            # 독 정보가 있으면 상세히 표시
            poison_turns = getattr(character, 'poison_turns', 0)
            poison_damage = getattr(character, 'poison_damage', 0)
            if poison_turns > 0 and poison_damage > 0:
                status_effects.append(f"{get_color('BRIGHT_GREEN')}POISON: {poison_damage}{get_color('RESET')}")
            else:
                status_effects.append(f"{get_color('BRIGHT_GREEN')}POISON{get_color('RESET')}")
        
        # 독 턴수 기반 체크 (추가 안전장치)
        if not poison_detected and hasattr(character, 'poison_turns') and getattr(character, 'poison_turns', 0) > 0:
            poison_turns = getattr(character, 'poison_turns', 0)
            poison_damage = getattr(character, 'poison_damage', 0)
            status_effects.append(f"{get_color('BRIGHT_GREEN')}POISON: {poison_damage}{get_color('RESET')}")
            
        if hasattr(character, 'is_burning') and character.is_burning:
            status_effects.append(f"{get_color('BRIGHT_RED')}BURN{get_color('RESET')}")
        if hasattr(character, 'is_frozen') and character.is_frozen:
            status_effects.append(f"{get_color('BRIGHT_CYAN')}FREEZE{get_color('RESET')}")
        if hasattr(character, 'is_stunned') and character.is_stunned:
            status_effects.append(f"{get_color('BRIGHT_YELLOW')}STUN{get_color('RESET')}")
        
        # 캐스팅 정보 - 강력한 방법
        casting_info = ""
        if is_casting:
            if hasattr(character, 'casting_skill') and character.casting_skill:
                # casting_skill이 딕셔너리인지 문자열인지 확인
                if isinstance(character.casting_skill, dict):
                    skill_name = character.casting_skill.get('name', '스킬')
                elif isinstance(character.casting_skill, str):
                    skill_name = character.casting_skill
                else:
                    skill_name = str(character.casting_skill)
            else:
                skill_name = "알 수 없는 스킬"
            casting_info = f" {get_color('BRIGHT_MAGENTA')}[CASTING: {skill_name}]{get_color('RESET')}"
        
        # 🎯 직업별 기믹 강제 표시 (모든 직업, 0도 표시) - create_compact_character_status와 통일
        mechanics_display = ""
        
        # 궁수 조준 포인트 - 항상 표시
        if character_class == "궁수":
            aim_points = getattr(character, 'aim_points', 0)
            precision_points = getattr(character, 'precision_points', 0) 
            mechanics_display += f" {get_color('BRIGHT_GREEN')}🎯AIM: {aim_points + precision_points}{get_color('RESET')}"
        
        # 도적 독 스택 - 항상 표시
        elif character_class == "도적":
            poison_stacks = getattr(character, 'poison_stacks', 0)
            venom_power = getattr(character, 'venom_power', 0)
            mechanics_display += f" {get_color('BRIGHT_GREEN')}☠️VENOM: {poison_stacks + venom_power}{get_color('RESET')}"
        
        # 암살자 그림자 - 항상 표시
        elif character_class == "암살자":
            shadow_count = getattr(character, 'shadow_count', 0)
            shadows = getattr(character, 'shadows', 0)
            mechanics_display += f" {get_color('BRIGHT_BLACK')}👤SHADOW: {shadow_count + shadows}{get_color('RESET')}"
        
        # 검성 검기 - 항상 표시
        elif character_class == "검성":
            sword_aura = getattr(character, 'sword_aura', 0)
            sword_aura_stacks = getattr(character, 'sword_aura_stacks', 0)
            mechanics_display += f" {get_color('BRIGHT_YELLOW')}⚔️AURA: {sword_aura + sword_aura_stacks}{get_color('RESET')}"
        
        # 바드 멜로디 - 항상 표시 (DO, RE, MI 형태)
        elif character_class == "바드":
            melody_stacks = getattr(character, 'melody_stacks', 0)
            song_power = getattr(character, 'song_power', 0)
            total_melody = melody_stacks + song_power
            
            # DO, RE, MI, FA, SO, LA, TI 음계 표시 (7음계, 0~7)
            melody_notes = ["", "DO", "RE", "MI", "FA", "SO", "LA", "TI"]
            if total_melody > 0 and total_melody < len(melody_notes):
                mechanics_display += f" {get_color('BRIGHT_CYAN')}🎵MELODY: {melody_notes[total_melody]}{get_color('RESET')}"
            elif total_melody >= len(melody_notes):
                mechanics_display += f" {get_color('BRIGHT_CYAN')}🎵HARMONY: {total_melody}{get_color('RESET')}"  # 7을 넘으면 하모니
            else:
                mechanics_display += f" {get_color('BRIGHT_CYAN')}🎵MELODY: {total_melody}{get_color('RESET')}"
        
        # 광전사 분노 - 항상 표시 (0일 때도 표시)
        elif character_class == "광전사":
            rage_stacks = getattr(character, 'rage_stacks', 0)
            berserk_level = getattr(character, 'berserk_level', 0)
            mechanics_display += f" {get_color('BRIGHT_RED')}💢RAGE: {rage_stacks + berserk_level}{get_color('RESET')}"
        
        # 아크메이지 원소 카운트 - 항상 표시
        elif character_class == "아크메이지":
            fire_count = getattr(character, 'fire_count', 0)
            ice_count = getattr(character, 'ice_count', 0)
            lightning_count = getattr(character, 'lightning_count', 0)
            mechanics_display += f" {get_color('BRIGHT_RED')}🔥FIRE: {fire_count}{get_color('RESET')}"
            mechanics_display += f" {get_color('BRIGHT_CYAN')}❄️ICE: {ice_count}{get_color('RESET')}"
            mechanics_display += f" {get_color('BRIGHT_YELLOW')}⚡THUNDER: {lightning_count}{get_color('RESET')}"
        
        # 몽크 기 에너지 - 항상 표시
        elif character_class == "몽크":
            chi_points = getattr(character, 'chi_points', 0)
            ki_energy = getattr(character, 'ki_energy', 0)
            strike_marks = getattr(character, 'strike_marks', 0)
            mechanics_display += f" {get_color('BRIGHT_YELLOW')}🥋CHI: {chi_points + ki_energy + strike_marks}{get_color('RESET')}"
        
        # 전사 자세/스탠스 - 항상 표시 (6가지 태세로 확장)
        elif character_class == "전사":
            warrior_stance = getattr(character, 'warrior_stance', None)
            warrior_focus = getattr(character, 'warrior_focus', 0)
            if warrior_stance == 'attack':
                mechanics_display += f" {get_color('BRIGHT_RED')}⚔️STANCE: ATK{get_color('RESET')}"
            elif warrior_stance == 'defense':
                mechanics_display += f" {get_color('BRIGHT_BLUE')}🛡️STANCE: DEF{get_color('RESET')}"
            elif warrior_stance == 'balanced':
                mechanics_display += f" {get_color('BRIGHT_YELLOW')}⚖️STANCE: BAL{get_color('RESET')}"
            elif warrior_stance == 'berserker':
                mechanics_display += f" {get_color('BRIGHT_RED')}💀STANCE: BERSERK{get_color('RESET')}"
            elif warrior_stance == 'guardian':
                mechanics_display += f" {get_color('BRIGHT_CYAN')}🛠️STANCE: GUARD{get_color('RESET')}"
            elif warrior_stance == 'speed':
                mechanics_display += f" {get_color('BRIGHT_GREEN')}⚡STANCE: SPEED{get_color('RESET')}"
            else:
                mechanics_display += f" {get_color('BRIGHT_WHITE')}🔶STANCE: NONE{get_color('RESET')}"
            if warrior_focus > 0:
                mechanics_display += f" {get_color('BRIGHT_YELLOW')}🎯FOCUS: {warrior_focus}{get_color('RESET')}"
        
        # 용기사 드래곤 파워 - 항상 표시
        elif character_class == "용기사":
            dragon_marks = getattr(character, 'dragon_marks', 0)
            dragon_power = getattr(character, 'dragon_power', 0)
            mechanics_display += f" {get_color('BRIGHT_RED')}🐉DRAGON: {dragon_marks + dragon_power}{get_color('RESET')}"
        
        # 검투사 투기장 포인트 - 항상 표시
        elif character_class == "검투사":
            arena_points = getattr(character, 'arena_points', 0)
            gladiator_experience = getattr(character, 'gladiator_experience', 0)
            mechanics_display += f" {get_color('BRIGHT_YELLOW')}🏛️ARENA: {arena_points + gladiator_experience}{get_color('RESET')}"
        
        # 네크로맨서 영혼/언데드 파워 - 항상 표시
        elif character_class == "네크로맨서":
            soul_count = getattr(character, 'soul_count', 0)
            undead_power = getattr(character, 'undead_power', 0)
            necromancy_stacks = getattr(character, 'necromancy_stacks', 0)
            mechanics_display += f" {get_color('BRIGHT_BLACK')}💀SOUL: {soul_count + undead_power + necromancy_stacks}{get_color('RESET')}"
        
        # 정령술사 정령 동조 - 항상 표시
        elif character_class == "정령술사":
            spirit_attunement = getattr(character, 'spirit_attunement', 0)
            elemental_harmony = getattr(character, 'elemental_harmony', 0)
            spirit_bond = getattr(character, 'spirit_bond', 0)
            mechanics_display += f" {get_color('BRIGHT_CYAN')}🌟SPIRIT: {spirit_attunement + elemental_harmony + spirit_bond}{get_color('RESET')}"
        
        # 시간술사 시공 에너지 - 항상 표시
        elif character_class == "시간술사":
            time_energy = getattr(character, 'time_energy', 0)
            chrono_power = getattr(character, 'chrono_power', 0)
            temporal_stacks = getattr(character, 'temporal_stacks', 0)
            mechanics_display += f" {get_color('BRIGHT_MAGENTA')}⏰TIME: {time_energy + chrono_power + temporal_stacks}{get_color('RESET')}"
        
        # 연금술사 화학 반응 - 항상 표시
        elif character_class == "연금술사":
            reaction_stacks = getattr(character, 'reaction_stacks', 0)
            alchemy_power = getattr(character, 'alchemy_power', 0)
            chemical_energy = getattr(character, 'chemical_energy', 0)
            mechanics_display += f" {get_color('BRIGHT_GREEN')}⚗️REACTION: {reaction_stacks + alchemy_power + chemical_energy}{get_color('RESET')}"
        
        # 차원술사 차원 균열 - 항상 표시
        elif character_class == "차원술사":
            dimension_rifts = getattr(character, 'dimension_rifts', 0)
            dimension_power = getattr(character, 'dimension_power', 0)
            dimensional_energy = getattr(character, 'dimensional_energy', 0)
            mechanics_display += f" {get_color('BRIGHT_MAGENTA')}🌌RIFT: {dimension_rifts + dimension_power + dimensional_energy}{get_color('RESET')}"
        
        # 기계공학자 오버차지/기계 - 항상 표시
        elif character_class == "기계공학자":
            overcharge_stacks = getattr(character, 'overcharge_stacks', 0)
            mechanical_power = getattr(character, 'mechanical_power', 0)
            tech_energy = getattr(character, 'tech_energy', 0)
            mechanics_display += f" {get_color('BRIGHT_CYAN')}🔧CHARGE: {overcharge_stacks + mechanical_power + tech_energy}{get_color('RESET')}"
        
        # 무당 영력 - 항상 표시
        elif character_class == "무당":
            spiritual_power = getattr(character, 'spiritual_power', 0)
            shaman_energy = getattr(character, 'shaman_energy', 0)
            spirit_power = getattr(character, 'spirit_power', 0)
            mechanics_display += f" {get_color('BRIGHT_MAGENTA')}🔯MYSTIC: {spiritual_power + shaman_energy + spirit_power}{get_color('RESET')}"
        
        # 해적 보물/전리품 - 항상 표시
        elif character_class == "해적":
            treasure_stacks = getattr(character, 'treasure_stacks', 0)
            pirate_loot = getattr(character, 'pirate_loot', 0)
            plunder_count = getattr(character, 'plunder_count', 0)
            mechanics_display += f" {get_color('BRIGHT_YELLOW')}🏴‍☠️TREASURE: {treasure_stacks + pirate_loot + plunder_count}{get_color('RESET')}"
        
        # 사무라이 검의 도/기 - 항상 표시
        elif character_class == "사무라이":
            bushido_spirit = getattr(character, 'bushido_spirit', 0)
            sword_spirit = getattr(character, 'sword_spirit', 0)
            samurai_focus = getattr(character, 'samurai_focus', 0)
            mechanics_display += f" {get_color('BRIGHT_WHITE')}🗾BUSHIDO: {bushido_spirit + sword_spirit + samurai_focus}{get_color('RESET')}"
        
        # 드루이드 자연의 힘 - 항상 표시
        elif character_class == "드루이드":
            nature_power = getattr(character, 'nature_power', 0)
            druid_harmony = getattr(character, 'druid_harmony', 0)
            wild_energy = getattr(character, 'wild_energy', 0)
            mechanics_display += f" {get_color('BRIGHT_GREEN')}🌿NATURE: {nature_power + druid_harmony + wild_energy}{get_color('RESET')}"
        
        # 철학자 깨달음/지혜 - 항상 표시
        elif character_class == "철학자":
            wisdom_stacks = getattr(character, 'wisdom_stacks', 0)
            enlightenment = getattr(character, 'enlightenment', 0)
            philosophy_power = getattr(character, 'philosophy_power', 0)
            mechanics_display += f" {get_color('BRIGHT_WHITE')}📚WISDOM: {wisdom_stacks + enlightenment + philosophy_power}{get_color('RESET')}"
        
        # 기사 명예/기사도 - 항상 표시
        elif character_class == "기사":
            honor_points = getattr(character, 'honor_points', 0)
            chivalry_power = getattr(character, 'chivalry_power', 0)
            knight_spirit = getattr(character, 'knight_spirit', 0)
            mechanics_display += f" {get_color('BRIGHT_WHITE')}🐎HONOR: {honor_points + chivalry_power + knight_spirit}{get_color('RESET')}"
        
        # 신관 신앙심/성력 - 항상 표시
        elif character_class == "신관":
            faith_power = getattr(character, 'faith_power', 0)
            divine_energy = getattr(character, 'divine_energy', 0)
            holy_power = getattr(character, 'holy_power', 0)
            faith_points = getattr(character, 'faith_points', 0)
            mechanics_display += f" {get_color('BRIGHT_YELLOW')}⛪FAITH: {faith_power + divine_energy + holy_power + faith_points}{get_color('RESET')}"
        
        # 마검사 마검 동조 - 항상 표시
        elif character_class == "마검사":
            magic_sword_sync = getattr(character, 'magic_sword_sync', 0)
            mystic_blade_power = getattr(character, 'mystic_blade_power', 0)
            sword_magic_fusion = getattr(character, 'sword_magic_fusion', 0)
            mechanics_display += f" {get_color('BRIGHT_MAGENTA')}⚡SYNC: {magic_sword_sync + mystic_blade_power + sword_magic_fusion}{get_color('RESET')}"
        
        # 성기사 성스러운 힘 - 항상 표시
        elif character_class == "성기사":
            holy_blessing = getattr(character, 'holy_blessing', 0)
            paladin_power = getattr(character, 'paladin_power', 0)
            sacred_energy = getattr(character, 'sacred_energy', 0)
            holy_power = getattr(character, 'holy_power', 0)
            mechanics_display += f" {get_color('BRIGHT_YELLOW')}✨HOLY: {holy_blessing + paladin_power + sacred_energy + holy_power}{get_color('RESET')}"
        
        # 암흑기사 어둠의 힘 - 항상 표시
        elif character_class == "암흑기사":
            dark_power = getattr(character, 'dark_power', 0)
            shadow_energy = getattr(character, 'shadow_energy', 0)
            darkness_stacks = getattr(character, 'darkness_stacks', 0)
            mechanics_display += f" {get_color('BRIGHT_BLACK')}🌑DARK: {dark_power + shadow_energy + darkness_stacks}{get_color('RESET')}"
        
        # 상처 시스템 - 0이 아닐 때만 표시, 심각도별 색상과 핏방울 이모지
        if hasattr(character, 'wounds') and character.wounds > 0:
            wound_ratio = character.wounds / character.max_hp if character.max_hp > 0 else 0
            if wound_ratio >= 0.5:  # 중태 (≥ 50%)
                mechanics_display += f" {get_color('RED')}🩸WOUND: {character.wounds}{get_color('RESET')}"
            elif wound_ratio >= 0.3:  # 중상 (30% ~ 50%)
                mechanics_display += f" {get_color('BRIGHT_RED')}🩸WOUND: {character.wounds}{get_color('RESET')}"
            else:  # 경상 (< 30%)
                mechanics_display += f" {get_color('YELLOW')}🩸WOUND: {character.wounds}{get_color('RESET')}"
        
        status_str = " ".join(status_effects) + casting_info
        
        # 레이아웃 생성
        # ATB 계산 로직 통일 - 완전 안정화된 계산
        atb_gauge = max(0, atb_gauge)  # 자연스러운 범위 (제한 없음)
        atb_ready_threshold = 1000  # ATB_MAX 1000에 맞춤
        
        # 캐스팅 중일 때는 캐스팅 진행도 표시 - Method 4 적용
        if is_casting:
            # 🎯 Method 4: BraveCombatSystem의 계산 사용
            try:
                # BraveCombatSystem에서 Method 4 계산 가져오기
                if hasattr(character, 'combat_system_ref') and character.combat_system_ref:
                    casting_progress_ratio = character.combat_system_ref.calculate_casting_progress_method4(character)
                    cast_percent = int(casting_progress_ratio * 100)
                    cast_percent = max(0, min(100, cast_percent))
                    atb_display = f"{get_color('BRIGHT_MAGENTA')}CAST {cast_percent}%{get_color('RESET')}"
                    # Method 4 진행도로 게이지 표시
                    atb_bar = OptimizedGaugeSystem.create_clean_gauge(cast_percent, 100, 10, "atb", hp_ratio, mp_ratio, True, "casting")
                elif hasattr(character, 'casting_progress') and hasattr(character, 'casting_duration'):
                    # 기존 방식 폴백
                    casting_progress = getattr(character, 'casting_progress', 0)
                    casting_duration = getattr(character, 'casting_duration', 1000)
                    cast_percent = int((casting_progress / casting_duration) * 100) if casting_duration > 0 else 0
                    cast_percent = max(0, min(100, cast_percent))
                    atb_display = f"{get_color('BRIGHT_MAGENTA')}CAST {cast_percent}%{get_color('RESET')}"
                    # 캐스팅 게이지는 현재 진행도로 표시
                    atb_bar = OptimizedGaugeSystem.create_clean_gauge(casting_progress, casting_duration, 10, "atb", hp_ratio, mp_ratio, True, "casting")
                else:
                    # 🎭 강력한 폴백: 캐스팅 중이지만 진행도가 없는 경우
                    atb_display = f"{get_color('BRIGHT_MAGENTA')}CASTING...{get_color('RESET')}"
                    # 기본 50% 진행도로 표시
                    atb_bar = OptimizedGaugeSystem.create_clean_gauge(500, 1000, 10, "atb", hp_ratio, mp_ratio, True, "casting")
            except Exception as e:
                # 오류 시 폴백
                atb_display = f"{get_color('BRIGHT_MAGENTA')}CASTING...{get_color('RESET')}"
                atb_bar = OptimizedGaugeSystem.create_clean_gauge(500, 1000, 10, "atb", hp_ratio, mp_ratio, True, "casting")
        elif atb_gauge >= atb_ready_threshold:
            atb_percent = 100
            atb_display = f"{get_color('YELLOW')}⚡ READY{get_color('RESET')}"
            atb_bar = OptimizedGaugeSystem.create_clean_gauge(atb_gauge, atb_ready_threshold, 10, "atb", hp_ratio, mp_ratio, is_casting, atb_speed_state)
        else:
            # ATB 퍼센트 계산 - 부동소수점 오차 방지
            raw_percent = (atb_gauge / atb_ready_threshold) * 100
            atb_percent = max(0, min(100, int(round(raw_percent))))  # 반올림 후 정수화
            
            # ATB 게이지 색상 결정
            if is_casting:
                atb_color = get_color('BRIGHT_MAGENTA')
            elif atb_speed_state == "fast":
                atb_color = get_color('BRIGHT_CYAN')
            elif atb_speed_state == "slow":
                atb_color = get_color('BLUE')
            elif atb_speed_state == "stunned":
                atb_color = get_color('WHITE')
            else:
                atb_color = get_color('CYAN')
            atb_display = f"{atb_color}{atb_percent}%{get_color('RESET')}"
            atb_bar = OptimizedGaugeSystem.create_clean_gauge(atb_gauge, atb_ready_threshold, 10, "atb", hp_ratio, mp_ratio, is_casting, atb_speed_state)
        
        if character == current_char:
            # 턴이 온 경우 - 화살표 표시
            line = (f"{arrow} {class_icon} {get_color('BRIGHT_WHITE')}Lv.{level}{get_color('RESET')} {name_color}{name}{get_color('RESET')}{mechanics_display}\n"
                    f"{hp_heart}{get_color('RESET')} {get_color('BRIGHT_WHITE')}HP: {get_color('RESET')} {hp_heart_color}{hp}{get_color('RESET')} {get_color('BRIGHT_WHITE')}/ {max_hp}{get_color('RESET')} {hp_gauge} | "
                    f"{mp_heart}{get_color('RESET')} {get_color('BRIGHT_WHITE')}MP: {get_color('RESET')} {mp_heart_color}{mp}{get_color('RESET')} {get_color('BRIGHT_WHITE')}/ {max_mp}{get_color('RESET')} {mp_gauge} | "
                    f"⚡ {get_color('BRIGHT_WHITE')}BRV: {get_color('RESET')} {brv_color}{brv}{get_color('RESET')} |\n"
                    f"⌛ {get_color('BRIGHT_WHITE')}TIME: {get_color('RESET')} {atb_bar} {atb_display} | {get_color('BRIGHT_WHITE')}SPD: {get_color('RESET')} {spd_color}{speed}{get_color('RESET')} {status_str}")
        else:
            # 대기 중인 경우
            line = (f"{arrow} {class_icon} {get_color('BRIGHT_WHITE')}Lv.{level}{get_color('RESET')} {name_color}{name}{get_color('RESET')}{mechanics_display}\n"
                    f"{hp_heart}{get_color('RESET')} {get_color('BRIGHT_WHITE')}HP: {get_color('RESET')} {hp_heart_color}{hp}{get_color('RESET')} {get_color('BRIGHT_WHITE')}/ {max_hp}{get_color('RESET')} {hp_gauge} | "
                    f"{mp_heart}{get_color('RESET')} {get_color('BRIGHT_WHITE')}MP: {get_color('RESET')} {mp_heart_color}{mp}{get_color('RESET')} {get_color('BRIGHT_WHITE')}/ {max_mp}{get_color('RESET')} {mp_gauge} | "
                    f"⚡ {get_color('BRIGHT_WHITE')}BRV: {get_color('RESET')} {brv_color}{brv}{get_color('RESET')} |\n"
                    f"⏳ {get_color('BRIGHT_WHITE')}TIME: {get_color('RESET')} {atb_bar} {atb_display} | {get_color('BRIGHT_WHITE')}SPD: {get_color('RESET')} {spd_color}{speed}{get_color('RESET')} {status_str}")
        
        return line
    
    @staticmethod
    def show_optimized_party_status(party, current_char=None) -> str:
        """최적화된 파티 상태 표시 - 헤더 없이 깔끔하게"""
        lines = []
        lines.append("🛡️ 아군")  # 간단한 구분만
        
        for member in party:
            if member.is_alive and hasattr(member, 'character_class') and member.character_class != 'Enemy':
                lines.append(OptimizedGaugeSystem.create_status_line(member, current_char, party))
        
        return "\n".join(lines)
    
    @staticmethod 
    def show_optimized_enemy_status(enemies) -> str:
        """최적화된 적군 상태 표시 - 헤더 없이 깔끔하게"""
        lines = []
        lines.append("⚔️ 적군")  # 간단한 구분만
        
        for enemy in enemies:
            if enemy.is_alive:
                # 적군도 같은 로직 적용 (MP만 제외)
                hp = enemy.current_hp
                max_hp = enemy.max_hp
                brv = getattr(enemy, 'brave_points', 0)
                max_brv = getattr(enemy, 'max_brave_points', 9999)
                speed = getattr(enemy, 'speed', 40)
                
                hp_ratio = hp / max_hp if max_hp > 0 else 0
                mp_ratio = 1.0  # 적군은 기본값
                is_casting = hasattr(enemy, 'is_casting') and enemy.is_casting
                
                # 평균 속도 계산 (모든 적군 기준)
                if enemies:
                    avg_speed = sum(getattr(e, 'speed', 40) for e in enemies if e.is_alive) / len([e for e in enemies if e.is_alive])
                else:
                    avg_speed = 40
                
                # ATB 속도 상태 판단
                if hasattr(enemy, 'is_stunned') and enemy.is_stunned:
                    atb_speed_state = "stunned"
                elif is_casting:
                    atb_speed_state = "casting"
                elif speed >= avg_speed * 1.3:
                    atb_speed_state = "fast"
                elif speed <= avg_speed * 0.7:
                    atb_speed_state = "slow"
                else:
                    atb_speed_state = "normal"
                
                hp_gauge = OptimizedGaugeSystem.create_clean_gauge(hp, max_hp, 10, "hp", hp_ratio, mp_ratio, is_casting, atb_speed_state)
                
                # ATB 정확한 계산
                atb_gauge = getattr(enemy, 'atb_gauge', 0)
                if atb_gauge >= 1000:  # ATB_MAX 1000에 맞춤
                    atb_status = f"{get_color('YELLOW')}⚡ READY{get_color('RESET')}"
                    atb_bar = OptimizedGaugeSystem.create_clean_gauge(1000, 1000, 10, "atb", hp_ratio, mp_ratio, is_casting, atb_speed_state)
                else:
                    atb_percent = int((atb_gauge / 1000) * 100)  # 1000 기준으로 변경
                    # ATB 게이지 색상 결정
                    if is_casting:
                        atb_color = get_color('BRIGHT_MAGENTA')
                    elif atb_speed_state == "fast":
                        atb_color = get_color('BRIGHT_CYAN')
                    elif atb_speed_state == "slow":
                        atb_color = get_color('BLUE')
                    elif atb_speed_state == "stunned":
                        atb_color = get_color('WHITE')
                    else:
                        atb_color = get_color('CYAN')
                    atb_status = f"{atb_color}{atb_percent}%{get_color('RESET')}"
                    atb_bar = OptimizedGaugeSystem.create_clean_gauge(atb_gauge, 1000, 10, "atb", hp_ratio, mp_ratio, is_casting, atb_speed_state)
                
                # HP 하트 색상과 이모지
                if hp_ratio > 0.8:
                    hp_heart_color = get_color('BRIGHT_GREEN')
                    hp_heart = "💚"
                elif hp_ratio > 0.6:
                    hp_heart_color = get_color('GREEN')
                    hp_heart = "💚"
                elif hp_ratio > 0.4:
                    hp_heart_color = get_color('YELLOW')
                    hp_heart = "💛"
                elif hp_ratio > 0.2:
                    hp_heart_color = get_color('BRIGHT_RED')
                    hp_heart = "🧡"
                else:
                    hp_heart_color = get_color('RED')
                    hp_heart = "❤️"
                
                # BRV 색상 (같은 로직)
                if brv == 0:
                    brv_color = get_color('RED')
                elif brv <= 299:
                    brv_color = get_color('YELLOW')  # 주황색
                elif brv == max_brv:
                    brv_color = get_color('BRIGHT_MAGENTA')
                else:
                    brv_color = get_color('BRIGHT_YELLOW')
                
                # SPD 숫자 색상 (같은 로직)
                if speed >= avg_speed * 1.3:
                    spd_color = get_color('GREEN')
                elif speed <= avg_speed * 0.7:
                    spd_color = get_color('RED')
                else:
                    spd_color = get_color('WHITE')
                
                # 상태이상 체크 - 영어 대문자로 표시 
                status_effects = []
                
                # BREAK 상태 우선 확인
                if hasattr(enemy, 'is_broken') and enemy.is_broken:
                    status_effects.append(f"{get_color('RED')}BREAK{get_color('RESET')}")
                
                # 독 상태는 여러 방법으로 체크 - 강력한 방법
                poison_detected = False
                if hasattr(enemy, 'status_manager') and enemy.status_manager:
                    if enemy.status_manager.has_status('독'):
                        poison_detected = True
                        status_effects.append(f"{get_color('BRIGHT_GREEN')}POISON{get_color('RESET')}")
                
                if not poison_detected and hasattr(enemy, 'is_poisoned') and enemy.is_poisoned:
                    poison_detected = True
                    # 독 정보가 있으면 상세히 표시
                    poison_turns = getattr(enemy, 'poison_turns', 0)
                    poison_damage = getattr(enemy, 'poison_damage', 0)
                    if poison_turns > 0 and poison_damage > 0:
                        status_effects.append(f"{get_color('BRIGHT_GREEN')}POISON: {poison_damage}{get_color('RESET')}")
                    else:
                        status_effects.append(f"{get_color('BRIGHT_GREEN')}POISON{get_color('RESET')}")
                
                # 독 턴수 기반 체크 (추가 안전장치)
                if not poison_detected and hasattr(enemy, 'poison_turns') and getattr(enemy, 'poison_turns', 0) > 0:
                    poison_turns = getattr(enemy, 'poison_turns', 0)
                    poison_damage = getattr(enemy, 'poison_damage', 0)
                    status_effects.append(f"{get_color('BRIGHT_GREEN')}POISON: {poison_damage}{get_color('RESET')}")
                    
                if hasattr(enemy, 'is_burning') and enemy.is_burning:
                    status_effects.append(f"{get_color('BRIGHT_RED')}BURN{get_color('RESET')}")
                if hasattr(enemy, 'is_frozen') and enemy.is_frozen:
                    status_effects.append(f"{get_color('BRIGHT_CYAN')}FREEZE{get_color('RESET')}")
                if hasattr(enemy, 'is_stunned') and enemy.is_stunned:
                    status_effects.append(f"{get_color('BRIGHT_YELLOW')}STUN{get_color('RESET')}")
                
                # 캐스팅 정보
                casting_info = ""
                if is_casting:
                    # casting_skill 안전하게 처리
                    casting_skill = getattr(enemy, 'casting_skill', None)
                    if isinstance(casting_skill, dict):
                        skill_name = casting_skill.get('name', '스킬')
                    elif isinstance(casting_skill, str):
                        skill_name = casting_skill
                    elif casting_skill:
                        skill_name = str(casting_skill)
                    else:
                        skill_name = '스킬'
                    casting_info = f" {get_color('BRIGHT_MAGENTA')}[CASTING: {skill_name}]{get_color('RESET')}"
                
                status_str = " " + " ".join(status_effects) + casting_info if (status_effects or casting_info) else ""
                
                # 적 아이콘 가져오기 - BraveCombatSystem에서 구현된 아이콘 사용
                enemy_icon = "⚔️"  # 기본 아이콘
                try:
                    # BraveCombatSystem 인스턴스가 있다면 아이콘 시스템 사용
                    import sys
                    if hasattr(sys.modules.get('__main__'), 'combat_system'):
                        combat_system = getattr(sys.modules['__main__'], 'combat_system', None)
                        if hasattr(combat_system, 'get_enemy_icon'):
                            enemy_icon = combat_system.get_enemy_icon(enemy.name)
                        elif hasattr(combat_system, 'enemy_icons'):
                            # 직접 아이콘 매칭
                            name_lower = enemy.name.lower()
                            if any(keyword in name_lower for keyword in ["쥐", "rat", "mouse"]):
                                enemy_icon = "🐭"
                            elif any(keyword in name_lower for keyword in ["늑대", "wolf"]):
                                enemy_icon = "🐺"
                            elif any(keyword in name_lower for keyword in ["드래곤", "dragon", "용"]):
                                enemy_icon = "🐉"
                            elif any(keyword in name_lower for keyword in ["오크", "orc"]):
                                enemy_icon = "🗡️"
                            elif any(keyword in name_lower for keyword in ["슬라임", "slime"]):
                                enemy_icon = "🟢"
                            elif any(keyword in name_lower for keyword in ["거미", "spider"]):
                                enemy_icon = "🕷️"
                            elif any(keyword in name_lower for keyword in ["고블린", "goblin"]):
                                enemy_icon = "👹"
                            elif any(keyword in name_lower for keyword in ["해골", "skeleton"]):
                                enemy_icon = "💀"
                            elif any(keyword in name_lower for keyword in ["좀비", "zombie"]):
                                enemy_icon = "🧟"
                            elif any(keyword in name_lower for keyword in ["보스", "boss", "왕", "마왕"]):
                                enemy_icon = "👑"
                except Exception as e:
                    # 오류 발생시 기본 아이콘 사용
                    enemy_icon = "⚔️"
                
                lines.append(f"▶ {enemy_icon} {get_color('BRIGHT_WHITE')}{enemy.name}{get_color('RESET')}{status_str}")
                lines.append(f"   {hp_heart}{get_color('RESET')} {get_color('BRIGHT_WHITE')}HP: {get_color('RESET')} {hp_heart_color}{hp}{get_color('RESET')} {get_color('BRIGHT_WHITE')}/ {max_hp}{get_color('RESET')} {hp_gauge} | ⚡ {get_color('BRIGHT_WHITE')}BRV: {get_color('RESET')} {brv_color}{brv}{get_color('RESET')}")
                lines.append(f"   ⏳ {atb_bar} {atb_status} | {get_color('BRIGHT_WHITE')}SPD: {get_color('RESET')} {spd_color}{speed}{get_color('RESET')}")
        
        return "\n".join(lines)

    @staticmethod
    def clear_all_gauge_cooldowns():
        """모든 게이지 쿨다운 초기화 (전투 시작/종료 시 사용)"""
        OptimizedGaugeSystem._last_gauge_display_time.clear()
    
    @staticmethod
    def show_single_gauge_update(character, gauge_type: str = "brv", old_value: int = 0, new_value: int = 0, reason: str = "") -> str:
        """단일 게이지 업데이트 표시 (중복 방지)"""
        character_name = getattr(character, 'name', 'Unknown')
        
        # 중복 표시 방지
        if not OptimizedGaugeSystem._can_display_gauge(character_name):
            return ""
        
        if gauge_type.lower() == "brv":
            return OptimizedGaugeSystem.display_brv_change(character, old_value, new_value, reason)
        elif gauge_type.lower() == "hp":
            return OptimizedGaugeSystem._display_hp_change(character, old_value, new_value, reason)
        elif gauge_type.lower() == "mp":
            return OptimizedGaugeSystem._display_mp_change(character, old_value, new_value, reason)
        else:
            return ""
    
    @staticmethod
    def _display_hp_change(character, old_hp: int, new_hp: int, change_reason: str = "") -> str:
        """HP 변화 표시"""
        character_name = getattr(character, 'name', 'Unknown')
        
        # 중복 표시 방지 체크
        if not OptimizedGaugeSystem._can_display_gauge(character_name):
            return ""  # 중복이면 아무것도 표시하지 않음
        
        hp_change = new_hp - old_hp
        change_symbol = "💚" if hp_change > 0 else "💔" if hp_change < 0 else "➡️"
        change_text = f"({hp_change:+d})" if hp_change != 0 else ""
        
        max_hp = getattr(character, 'max_hp', 1)
        hp_ratio = new_hp / max_hp if max_hp > 0 else 0
        hp_gauge = OptimizedGaugeSystem.create_clean_gauge(new_hp, max_hp, 20, "hp", hp_ratio)
        
        result = f"💫 {character_name}: 💚 {hp_gauge} {new_hp}/{max_hp}"
        if change_text:
            result += f" {change_text} {change_symbol}"
        if change_reason:
            result += f" {change_reason}"
        
        # 성공적으로 표시했으므로 시간 업데이트
        OptimizedGaugeSystem._update_display_time(character_name)
        
        return result
    
    @staticmethod
    def _display_mp_change(character, old_mp: int, new_mp: int, change_reason: str = "") -> str:
        """MP 변화 표시"""
        character_name = getattr(character, 'name', 'Unknown')
        
        # 중복 표시 방지 체크
        if not OptimizedGaugeSystem._can_display_gauge(character_name):
            return ""  # 중복이면 아무것도 표시하지 않음
        
        mp_change = new_mp - old_mp
        change_symbol = "💙" if mp_change > 0 else "💧" if mp_change < 0 else "➡️"
        change_text = f"({mp_change:+d})" if mp_change != 0 else ""
        
        max_mp = getattr(character, 'max_mp', 1)
        mp_ratio = new_mp / max_mp if max_mp > 0 else 0
        mp_gauge = OptimizedGaugeSystem.create_clean_gauge(new_mp, max_mp, 20, "mp", 1.0, mp_ratio)
        
        result = f"💫 {character_name}: 💙 {mp_gauge} {new_mp}/{max_mp}"
        if change_text:
            result += f" {change_text} {change_symbol}"
        if change_reason:
            result += f" {change_reason}"
        
        # 성공적으로 표시했으므로 시간 업데이트
        OptimizedGaugeSystem._update_display_time(character_name)
        
        return result

# 전역 인스턴스
optimized_gauge = OptimizedGaugeSystem()
