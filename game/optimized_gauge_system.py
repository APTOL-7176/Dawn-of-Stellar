"""
최적화된 게이지 시스템
깜빡임 최소화와 성능 향상을 위한 통합 게이지 모듈
"""

from .combat_visual import Color

class OptimizedGaugeSystem:
    """최적화된 게이지 시스템 클래스"""
    
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
                color = Color.BRIGHT_GREEN
            elif hp_ratio > 0.6:
                color = Color.GREEN  
            elif hp_ratio > 0.4:
                color = Color.YELLOW
            elif hp_ratio > 0.2:
                color = Color.BRIGHT_RED
            else:
                color = Color.RED
        elif gauge_type.lower() == "mp":
            # MP 하트 색상에 따른 게이지 색상
            if mp_ratio > 0.8:
                color = Color.BRIGHT_CYAN
            elif mp_ratio > 0.6:
                color = Color.CYAN  
            elif mp_ratio > 0.4:
                color = Color.BLUE
            elif mp_ratio > 0.2:
                color = Color.MAGENTA
            else:
                color = Color.RED
        elif gauge_type.lower() == "atb":
            # ATB 게이지 색상 로직
            if is_casting:
                color = Color.BRIGHT_MAGENTA
            elif ratio >= 1.0:
                color = Color.YELLOW  # 주황색 (꽉 참)
            elif atb_speed_state == "fast":
                color = Color.BRIGHT_CYAN  # 밝은 하늘색 (빠른 상태)
            elif atb_speed_state == "slow":
                color = Color.BLUE  # 파란색 (느린 상태)
            elif atb_speed_state == "stunned":
                color = Color.WHITE  # 회색 (기절/정지)
            else:
                color = Color.CYAN  # 하늘색 (기본)
        else:
            color = Color.WHITE
        
        # 완전히 새로운 게이지 생성 로직 - 길이 일관성 보장
        filled_length = ratio * length  # 실제 채워야 할 길이 (소수점 포함)
        full_blocks = int(filled_length)  # 완전히 채워진 블록 수
        partial_amount = filled_length - full_blocks  # 부분 블록의 채움 정도
        
        gauge_content = ""
        
        # 1. 완전히 채워진 블록들 추가
        if full_blocks > 0:
            gauge_content += color + "█" * full_blocks + Color.RESET
        
        # 2. 부분 블록 처리 (정확한 1개 블록 공간만 사용)
        if full_blocks < length and partial_amount > 0:
            if partial_amount >= 0.875:
                gauge_content += color + "▉" + Color.RESET
            elif partial_amount >= 0.75:
                gauge_content += color + "▊" + Color.RESET
            elif partial_amount >= 0.625:
                gauge_content += color + "▋" + Color.RESET
            elif partial_amount >= 0.5:
                gauge_content += color + "▌" + Color.RESET
            elif partial_amount >= 0.375:
                gauge_content += color + "▍" + Color.RESET
            elif partial_amount >= 0.25:
                gauge_content += color + "▎" + Color.RESET
            elif partial_amount >= 0.125:
                gauge_content += color + "▏" + Color.RESET
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
        arrow = "▶" if character == current_char else " "
        
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
        
        # 클래스 아이콘
        character_class = getattr(character, 'character_class', '모험가')
        class_icons = {
            '전사': '⚔️', '아크메이지': '🔮', '궁수': '🏹', '도적': '🗡️',
            '성기사': '🛡️', '암흑기사': '💀', '몽크': '👊', '바드': '🎵', '네크로맨서': '💀',
            '용기사': '🐉', '검성': '⚔️', '정령술사': '🌟', '암살자': '🔪', '기계공학자': '🔧',
            '무당': '🔯', '해적': '🏴‍☠️', '사무라이': '🗾', '드루이드': '🌿', '철학자': '📘',
            '시간술사': '⏰', '연금술사': '⚗️', '검투사': '🏛️', '기사': '🐎', '신관': '✨',
            '마검사': '⚡', '차원술사': '🌌', '광전사': '💥',
            '모험가': '🎭', 'Enemy': '👹'
        }
        class_icon = class_icons.get(character_class, '🎭')
        
        # 색상 설정
        # 이름 색상 (턴이 온 캐릭터는 하늘색)
        name_color = Color.BRIGHT_CYAN if character == current_char else Color.BRIGHT_WHITE
        
        # HP 하트 색상과 이모지
        if hp_ratio > 0.8:
            hp_heart_color = Color.BRIGHT_GREEN
            hp_heart = "💚"  # 녹색 하트
        elif hp_ratio > 0.6:
            hp_heart_color = Color.GREEN
            hp_heart = "💚"  # 녹색 하트
        elif hp_ratio > 0.4:
            hp_heart_color = Color.YELLOW
            hp_heart = "💛"  # 노란 하트
        elif hp_ratio > 0.2:
            hp_heart_color = Color.BRIGHT_RED
            hp_heart = "🧡"  # 주황 하트
        else:
            hp_heart_color = Color.RED
            hp_heart = "❤️"  # 빨간 하트
        
        # MP 하트 색상과 이모지
        if mp_ratio > 0.8:
            mp_heart_color = Color.BRIGHT_CYAN
            mp_heart = "💙"  # 파란 하트
        elif mp_ratio > 0.6:
            mp_heart_color = Color.CYAN
            mp_heart = "💙"  # 파란 하트
        elif mp_ratio > 0.4:
            mp_heart_color = Color.BLUE
            mp_heart = "💜"  # 보라 하트
        elif mp_ratio > 0.2:
            mp_heart_color = Color.MAGENTA
            mp_heart = "💜"  # 보라 하트
        else:
            mp_heart_color = Color.RED
            mp_heart = "❤️"  # 빨간 하트
        
        # BRV 색상
        if brv == 0:
            brv_color = Color.RED
        elif brv <= 299:
            brv_color = Color.YELLOW  # 주황색
        elif brv == max_brv:
            brv_color = Color.BRIGHT_MAGENTA
        else:
            brv_color = Color.BRIGHT_YELLOW
        
        # SPD 숫자 색상
        if speed >= avg_speed * 1.3:
            spd_color = Color.GREEN
        elif speed <= avg_speed * 0.7:
            spd_color = Color.RED
        else:
            spd_color = Color.WHITE
        
        # 게이지 생성
        hp_gauge = OptimizedGaugeSystem.create_clean_gauge(hp, max_hp, 10, "hp", hp_ratio, mp_ratio, is_casting, atb_speed_state)
        mp_gauge = OptimizedGaugeSystem.create_clean_gauge(mp, max_mp, 10, "mp", hp_ratio, mp_ratio, is_casting, atb_speed_state)
        
        # ATB 게이지 처리 - 값 범위 안정화
        atb_gauge = max(0, min(1000, getattr(character, 'atb_gauge', 0)))  # 0-1000 범위 강제
        atb_ready_threshold = 1000  # ATB_MAX 1000에 맞춤
        
        # 상태이상 체크 - 아이콘으로 표시
        status_effects = []
        if hasattr(character, 'is_broken') and character.is_broken:
            status_effects.append(f"{Color.RED}💥BREAK{Color.RESET}")
        if hasattr(character, 'is_poisoned') and character.is_poisoned:
            status_effects.append(f"{Color.BRIGHT_GREEN}🧪독{Color.RESET}")
        if hasattr(character, 'is_burning') and character.is_burning:
            status_effects.append(f"{Color.BRIGHT_RED}🔥화상{Color.RESET}")
        if hasattr(character, 'is_frozen') and character.is_frozen:
            status_effects.append(f"{Color.BRIGHT_CYAN}❄️빙결{Color.RESET}")
        if hasattr(character, 'is_stunned') and character.is_stunned:
            status_effects.append(f"{Color.BRIGHT_YELLOW}😵기절{Color.RESET}")
        
        # 캐스팅 정보
        casting_info = ""
        if is_casting:
            skill_name = getattr(character, 'casting_skill', {}).get('name', '스킬') if hasattr(character, 'casting_skill') else '스킬'
            casting_info = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
        
        status_str = " ".join(status_effects) + casting_info
        
        # 레이아웃 생성
        # ATB 계산 로직 통일 - 완전 안정화된 계산
        atb_gauge = max(0, min(10000, atb_gauge))  # 0-10000 범위 강제
        
        if atb_gauge >= atb_ready_threshold:
            atb_percent = 100
            atb_display = f"{Color.YELLOW}⚡ READY{Color.RESET}"
        else:
            # ATB 퍼센트 계산 - 부동소수점 오차 방지
            raw_percent = (atb_gauge / atb_ready_threshold) * 100
            atb_percent = max(0, min(100, int(round(raw_percent))))  # 반올림 후 정수화
            
            # ATB 게이지 색상 결정
            if is_casting:
                atb_color = Color.BRIGHT_MAGENTA
            elif atb_speed_state == "fast":
                atb_color = Color.BRIGHT_CYAN
            elif atb_speed_state == "slow":
                atb_color = Color.BLUE
            elif atb_speed_state == "stunned":
                atb_color = Color.WHITE
            else:
                atb_color = Color.CYAN
            atb_display = f"{atb_color}{atb_percent}%{Color.RESET}"
        
        # ATB 게이지 바 생성 (실제 ATB 값 사용)
        atb_bar = OptimizedGaugeSystem.create_clean_gauge(atb_gauge, atb_ready_threshold, 10, "atb", hp_ratio, mp_ratio, is_casting, atb_speed_state)
        
        if character == current_char:
            # 턴이 온 경우 - 화살표 표시
            line = (f"{arrow} {class_icon} {Color.BRIGHT_WHITE}Lv.{level}{Color.RESET} {name_color}{name}{Color.RESET}\n"
                    f"{hp_heart}{Color.RESET} {Color.BRIGHT_WHITE}HP:{Color.RESET} {hp_heart_color}{hp}{Color.RESET} {Color.BRIGHT_WHITE}/ {max_hp}{Color.RESET} {hp_gauge} | "
                    f"{mp_heart}{Color.RESET} {Color.BRIGHT_WHITE}MP:{Color.RESET} {mp_heart_color}{mp}{Color.RESET} {Color.BRIGHT_WHITE}/ {max_mp}{Color.RESET} {mp_gauge} | "
                    f"⚡ {Color.BRIGHT_WHITE}BRV:{Color.RESET} {brv_color}{brv}{Color.RESET} |\n"
                    f"⌛ {Color.BRIGHT_WHITE}TIME:{Color.RESET} {atb_bar} {atb_display} | {Color.BRIGHT_WHITE}SPD:{Color.RESET} {spd_color}{speed}{Color.RESET} {status_str}")
        else:
            # 대기 중인 경우
            line = (f"{arrow} {class_icon} {Color.BRIGHT_WHITE}Lv.{level}{Color.RESET} {name_color}{name}{Color.RESET}\n"
                    f"{hp_heart}{Color.RESET} {Color.BRIGHT_WHITE}HP:{Color.RESET} {hp_heart_color}{hp}{Color.RESET} {Color.BRIGHT_WHITE}/ {max_hp}{Color.RESET} {hp_gauge} | "
                    f"{mp_heart}{Color.RESET} {Color.BRIGHT_WHITE}MP:{Color.RESET} {mp_heart_color}{mp}{Color.RESET} {Color.BRIGHT_WHITE}/ {max_mp}{Color.RESET} {mp_gauge} | "
                    f"⚡ {Color.BRIGHT_WHITE}BRV:{Color.RESET} {brv_color}{brv}{Color.RESET} |\n"
                    f"⏳ {Color.BRIGHT_WHITE}TIME:{Color.RESET} {atb_bar} {atb_display} | {Color.BRIGHT_WHITE}SPD:{Color.RESET} {spd_color}{speed}{Color.RESET} {status_str}")
        
        return line
    
    @staticmethod
    def show_optimized_party_status(party, current_char=None) -> str:
        """최적화된 파티 상태 표시"""
        lines = []
        lines.append(f"{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        lines.append(f"{Color.BRIGHT_WHITE}🛡️ 아군 파티 상태{Color.RESET}")
        lines.append(f"{Color.BRIGHT_BLUE}{'─'*70}{Color.RESET}")
        
        for member in party:
            if member.is_alive and hasattr(member, 'character_class') and member.character_class != 'Enemy':
                lines.append(OptimizedGaugeSystem.create_status_line(member, current_char, party))
        
        return "\n".join(lines)
    
    @staticmethod 
    def show_optimized_enemy_status(enemies) -> str:
        """최적화된 적군 상태 표시"""
        lines = []
        lines.append(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
        lines.append(f"{Color.BRIGHT_WHITE}⚔️ 적군 상태{Color.RESET}")
        lines.append(f"{Color.BRIGHT_RED}{'─'*70}{Color.RESET}")
        
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
                    atb_status = f"{Color.YELLOW}⚡ READY{Color.RESET}"
                    atb_bar = OptimizedGaugeSystem.create_clean_gauge(1000, 1000, 10, "atb", hp_ratio, mp_ratio, is_casting, atb_speed_state)
                else:
                    atb_percent = int((atb_gauge / 1000) * 100)  # 1000 기준으로 변경
                    # ATB 게이지 색상 결정
                    if is_casting:
                        atb_color = Color.BRIGHT_MAGENTA
                    elif atb_speed_state == "fast":
                        atb_color = Color.BRIGHT_CYAN
                    elif atb_speed_state == "slow":
                        atb_color = Color.BLUE
                    elif atb_speed_state == "stunned":
                        atb_color = Color.WHITE
                    else:
                        atb_color = Color.CYAN
                    atb_status = f"{atb_color}{atb_percent}%{Color.RESET}"
                    atb_bar = OptimizedGaugeSystem.create_clean_gauge(atb_gauge, 1000, 10, "atb", hp_ratio, mp_ratio, is_casting, atb_speed_state)
                
                # HP 하트 색상과 이모지
                if hp_ratio > 0.8:
                    hp_heart_color = Color.BRIGHT_GREEN
                    hp_heart = "💚"
                elif hp_ratio > 0.6:
                    hp_heart_color = Color.GREEN
                    hp_heart = "💚"
                elif hp_ratio > 0.4:
                    hp_heart_color = Color.YELLOW
                    hp_heart = "💛"
                elif hp_ratio > 0.2:
                    hp_heart_color = Color.BRIGHT_RED
                    hp_heart = "🧡"
                else:
                    hp_heart_color = Color.RED
                    hp_heart = "❤️"
                
                # BRV 색상 (같은 로직)
                if brv == 0:
                    brv_color = Color.RED
                elif brv <= 299:
                    brv_color = Color.YELLOW  # 주황색
                elif brv == max_brv:
                    brv_color = Color.BRIGHT_MAGENTA
                else:
                    brv_color = Color.BRIGHT_YELLOW
                
                # SPD 숫자 색상 (같은 로직)
                if speed >= avg_speed * 1.3:
                    spd_color = Color.GREEN
                elif speed <= avg_speed * 0.7:
                    spd_color = Color.RED
                else:
                    spd_color = Color.WHITE
                
                # 상태이상 체크 - 아이콘으로 표시 (BREAK 제외 - brave_combat.py에서 이미 표시)
                status_effects = []
                # BREAK 상태는 brave_combat.py에서 이미 표시하므로 여기서는 제외
                if hasattr(enemy, 'is_poisoned') and enemy.is_poisoned:
                    status_effects.append(f"{Color.BRIGHT_GREEN}🧪독{Color.RESET}")
                if hasattr(enemy, 'is_burning') and enemy.is_burning:
                    status_effects.append(f"{Color.BRIGHT_RED}🔥화상{Color.RESET}")
                if hasattr(enemy, 'is_frozen') and enemy.is_frozen:
                    status_effects.append(f"{Color.BRIGHT_CYAN}❄️빙결{Color.RESET}")
                if hasattr(enemy, 'is_stunned') and enemy.is_stunned:
                    status_effects.append(f"{Color.BRIGHT_YELLOW}😵기절{Color.RESET}")
                
                # 캐스팅 정보
                casting_info = ""
                if is_casting:
                    skill_name = getattr(enemy, 'casting_skill', {}).get('name', '스킬') if hasattr(enemy, 'casting_skill') else '스킬'
                    casting_info = f" {Color.BRIGHT_MAGENTA}[CASTING: {skill_name}]{Color.RESET}"
                
                status_str = " " + " ".join(status_effects) + casting_info if (status_effects or casting_info) else ""
                
                lines.append(f"▶ ⚔️ {Color.BRIGHT_WHITE}{enemy.name}{Color.RESET}{status_str}")
                lines.append(f"  {hp_heart}{Color.RESET} {Color.BRIGHT_WHITE}HP:{Color.RESET} {hp_heart_color}{hp}{Color.RESET} {Color.BRIGHT_WHITE}/ {max_hp}{Color.RESET} {hp_gauge} | ⚡ {Color.BRIGHT_WHITE}BRV:{Color.RESET} {brv_color}{brv}{Color.RESET}")
                lines.append(f"  ⏳ {atb_bar} {atb_status} | {Color.BRIGHT_WHITE}SPD:{Color.RESET} {spd_color}{speed}{Color.RESET}{status_str}")
        
        return "\n".join(lines)

# 전역 인스턴스
optimized_gauge = OptimizedGaugeSystem()