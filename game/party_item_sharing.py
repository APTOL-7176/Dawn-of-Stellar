"""
파티 아이템 공유 시스템
AI 동료들이 공용 인벤토리에서 필요한 아이템을 자동으로 사용
"""
import random
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .character import Character

class ItemSharingPermission(Enum):
    """아이템 공유 권한"""
    FULL_ACCESS = "full_access"         # 모든 아이템 자유 사용
    LIMITED_ACCESS = "limited_access"   # 치료/회복 아이템만 사용
    ASK_PERMISSION = "ask_permission"   # 사용 전 항상 확인
    NO_ACCESS = "no_access"             # 사용 금지

class SharedItemType(Enum):
    """공유 가능한 아이템 타입"""
    HEALING_POTION = "healing_potion"
    MANA_POTION = "mana_potion"
    ANTIDOTE = "antidote"
    BUFF_SCROLL = "buff_scroll"
    FOOD = "food"
    EQUIPMENT = "equipment"
    RARE_ITEM = "rare_item"

class AIItemUsageRecord:
    """AI 아이템 사용 기록"""
    def __init__(self, ai_name: str, item_type: str, reason: str):
        self.ai_name = ai_name
        self.item_type = item_type
        self.reason = reason
        self.timestamp = random.randint(1, 1000)  # 게임 시간 대신 임시값
        self.player_reaction = None  # 플레이어가 좋아했는지/화났는지

class PartyItemSharingSystem:
    """파티 아이템 공유 시스템"""
    
    def __init__(self):
        self.sharing_permission = ItemSharingPermission.LIMITED_ACCESS
        self.shared_inventory = {}  # 공용 인벤토리
        self.usage_records = []     # 사용 기록
        self.pending_requests = []  # 사용 요청 대기
        self.daily_usage_limits = {
            SharedItemType.HEALING_POTION: 3,
            SharedItemType.MANA_POTION: 2,
            SharedItemType.ANTIDOTE: 1,
            SharedItemType.BUFF_SCROLL: 1,
            SharedItemType.FOOD: 2
        }
        self.ai_usage_count = {}    # AI별 일일 사용량 추적
        
    def initialize_shared_inventory(self, party_inventory: Dict):
        """공용 인벤토리 초기화"""
        # 기존 인벤토리에서 공유 가능한 아이템들을 공용으로 이동
        shareable_items = {
            "체력 포션": SharedItemType.HEALING_POTION,
            "마나 포션": SharedItemType.MANA_POTION,
            "해독제": SharedItemType.ANTIDOTE,
            "강화 스크롤": SharedItemType.BUFF_SCROLL,
            "건빵": SharedItemType.FOOD,
            "치즈": SharedItemType.FOOD
        }
        
        self.shared_inventory = {}
        for item_name, item_type in shareable_items.items():
            if item_name in party_inventory:
                count = party_inventory.get(item_name, 0)
                if count > 0:
                    self.shared_inventory[item_name] = {
                        "count": count,
                        "type": item_type,
                        "reserved_for_player": max(1, count // 4)  # 25%는 플레이어용으로 예약
                    }
        
        print(f"📦 공용 인벤토리 초기화 완료!")
        self._show_shared_inventory()
    
    def can_ai_use_item(self, ai_name: str, item_name: str, emergency: bool = False) -> Tuple[bool, str]:
        """AI가 아이템을 사용할 수 있는지 확인"""
        if item_name not in self.shared_inventory:
            return False, "아이템이 공용 인벤토리에 없습니다"
        
        item_info = self.shared_inventory[item_name]
        available_count = item_info["count"] - item_info["reserved_for_player"]
        
        if available_count <= 0:
            return False, "사용 가능한 아이템이 없습니다 (플레이어용 예약)"
        
        # 권한 확인
        if self.sharing_permission == ItemSharingPermission.NO_ACCESS:
            return False, "아이템 사용이 금지되어 있습니다"
        
        if self.sharing_permission == ItemSharingPermission.ASK_PERMISSION and not emergency:
            return False, "사용 전 허가가 필요합니다"
        
        # 제한된 접근 모드에서 아이템 타입 확인
        if self.sharing_permission == ItemSharingPermission.LIMITED_ACCESS:
            allowed_types = [SharedItemType.HEALING_POTION, SharedItemType.MANA_POTION, SharedItemType.ANTIDOTE]
            if item_info["type"] not in allowed_types:
                return False, "이 아이템은 제한된 접근 모드에서 사용할 수 없습니다"
        
        # 일일 사용량 확인
        daily_key = f"{ai_name}_{item_info['type'].value}"
        used_today = self.ai_usage_count.get(daily_key, 0)
        daily_limit = self.daily_usage_limits.get(item_info["type"], 999)
        
        if used_today >= daily_limit and not emergency:
            return False, f"일일 사용 한도를 초과했습니다 ({used_today}/{daily_limit})"
        
        return True, "사용 가능"
    
    def request_item_usage(self, ai_name: str, item_name: str, reason: str, emergency: bool = False) -> bool:
        """AI가 아이템 사용을 요청"""
        can_use, message = self.can_ai_use_item(ai_name, item_name, emergency)
        
        if not can_use:
            if self.sharing_permission == ItemSharingPermission.ASK_PERMISSION:
                # 허가 요청을 대기열에 추가
                request = {
                    "ai_name": ai_name,
                    "item_name": item_name,
                    "reason": reason,
                    "emergency": emergency,
                    "timestamp": random.randint(1, 1000)
                }
                self.pending_requests.append(request)
                print(f"💬 {ai_name}: {item_name}을(를) 사용해도 될까요? ({reason})")
                return False
            else:
                print(f"❌ {ai_name}의 {item_name} 사용 실패: {message}")
                return False
        
        # 즉시 사용
        return self._execute_item_usage(ai_name, item_name, reason, emergency)
    
    def _execute_item_usage(self, ai_name: str, item_name: str, reason: str, emergency: bool) -> bool:
        """아이템 사용 실행"""
        if item_name not in self.shared_inventory:
            return False
        
        item_info = self.shared_inventory[item_name]
        
        # 아이템 개수 감소
        item_info["count"] -= 1
        if item_info["count"] <= 0:
            del self.shared_inventory[item_name]
        
        # 사용량 기록
        daily_key = f"{ai_name}_{item_info['type'].value}"
        self.ai_usage_count[daily_key] = self.ai_usage_count.get(daily_key, 0) + 1
        
        # 사용 기록 저장
        record = AIItemUsageRecord(ai_name, item_name, reason)
        self.usage_records.append(record)
        
        # 사용 메시지 표시
        self._show_ai_item_usage(ai_name, item_name, reason, emergency)
        
        return True
    
    def _show_ai_item_usage(self, ai_name: str, item_name: str, reason: str, emergency: bool):
        """AI 아이템 사용 애니메이션"""
        emergency_mark = "🚨 " if emergency else ""
        
        messages = [
            f"{emergency_mark}🤖 {ai_name}이(가) {item_name}을(를) 사용했습니다!",
            f"   💭 이유: {reason}"
        ]
        
        # 상황별 추가 메시지
        if emergency:
            messages.append("   ⚡ 긴급 상황으로 즉시 사용!")
        
        # 사과/고마움 표현 (확률적)
        reactions = [
            f"💬 {ai_name}: 고마워! 덕분에 살았어!",
            f"💬 {ai_name}: 미안, 급해서 먼저 썼어.",
            f"💬 {ai_name}: 다음에 보상할게!",
            f"💬 {ai_name}: 아낄 수 없는 상황이었어.",
            ""  # 아무 말 안함
        ]
        
        reaction = random.choice(reactions)
        if reaction:
            messages.append(reaction)
        
        for msg in messages:
            print(msg)
    
    def handle_pending_requests(self) -> bool:
        """대기 중인 아이템 사용 요청 처리 - 커서 메뉴 방식"""
        if not self.pending_requests:
            return False
        
        try:
            from .cursor_menu_system import create_simple_menu
            
            print(f"\n💬 AI 동료들의 아이템 사용 요청 ({len(self.pending_requests)}개):")
            print("="*60)
            
            # 요청별로 개별 승인/거절 처리
            for i, request in enumerate(self.pending_requests[:]):  # 복사본으로 안전하게 순회
                emergency_mark = "🚨 긴급! " if request["emergency"] else ""
                
                print(f"\n📋 요청 {i+1}/{len(self.pending_requests)}")
                print(f"🤖 요청자: {request['ai_name']}")
                print(f"🧪 아이템: {request['item_name']}")
                print(f"💭 이유: {emergency_mark}{request['reason']}")
                
                # 승인/거절 메뉴
                options = ["✅ 승인", "❌ 거절", "⏭️ 다음에 결정"]
                descriptions = [
                    f"{request['ai_name']}의 {request['item_name']} 사용을 허가합니다",
                    f"{request['ai_name']}의 요청을 거절합니다",
                    "이 요청을 나중에 처리하고 다음 요청으로 넘어갑니다"
                ]
                
                menu = create_simple_menu(
                    f"💬 {request['ai_name']}의 요청",
                    options,
                    descriptions
                )
                
                result = menu.run()
                
                if result == 0:  # 승인
                    success = self._execute_item_usage(
                        request["ai_name"], 
                        request["item_name"], 
                        request["reason"], 
                        request["emergency"]
                    )
                    if success:
                        print(f"✅ {request['ai_name']}의 요청이 승인되었습니다!")
                    else:
                        print(f"❌ 아이템 사용에 실패했습니다.")
                    self.pending_requests.remove(request)
                    
                elif result == 1:  # 거절
                    print(f"❌ {request['ai_name']}의 요청이 거절되었습니다.")
                    self.pending_requests.remove(request)
                    
                elif result == 2 or result == -1:  # 다음에 결정 또는 ESC
                    print(f"⏭️ {request['ai_name']}의 요청을 나중에 처리합니다.")
                    continue
            
            # 남은 요청이 있는지 확인
            if self.pending_requests:
                print(f"\n📋 {len(self.pending_requests)}개의 요청이 아직 대기 중입니다.")
                
                # 일괄 처리 메뉴
                batch_options = ["✅ 모든 요청 승인", "❌ 모든 요청 거절", "📋 개별 검토 계속", "🚪 나가기"]
                batch_descriptions = [
                    "남은 모든 요청을 한번에 승인합니다",
                    "남은 모든 요청을 한번에 거절합니다", 
                    "남은 요청들을 하나씩 다시 검토합니다",
                    "요청 처리를 종료합니다"
                ]
                
                batch_menu = create_simple_menu(
                    "📋 남은 요청 일괄 처리",
                    batch_options,
                    batch_descriptions
                )
                
                batch_result = batch_menu.run()
                
                if batch_result == 0:  # 모든 요청 승인
                    for request in self.pending_requests[:]:
                        self._execute_item_usage(
                            request["ai_name"], 
                            request["item_name"], 
                            request["reason"], 
                            request["emergency"]
                        )
                    print(f"✅ 모든 요청({len(self.pending_requests)}개)이 승인되었습니다!")
                    self.pending_requests.clear()
                    
                elif batch_result == 1:  # 모든 요청 거절
                    rejected_count = len(self.pending_requests)
                    self.pending_requests.clear()
                    print(f"❌ 모든 요청({rejected_count}개)이 거절되었습니다.")
                    
                elif batch_result == 2:  # 개별 검토 계속
                    return self.handle_pending_requests()  # 재귀 호출로 다시 처리
                    
                # batch_result == 3 또는 -1: 나가기
            
            return True
            
        except ImportError:
            # 폴백: 기존 텍스트 방식
            return self._handle_pending_requests_fallback()
        except Exception as e:
            print(f"⚠️ 요청 처리 중 오류: {e}")
            return self._handle_pending_requests_fallback()
    
    def _handle_pending_requests_fallback(self) -> bool:
        """대기 중인 아이템 사용 요청 처리 - 폴백 방식"""
        if not self.pending_requests:
            return False
        
        print(f"\n💬 AI 동료들의 아이템 사용 요청 ({len(self.pending_requests)}개):")
        
        for i, request in enumerate(self.pending_requests):
            emergency_mark = "🚨 " if request["emergency"] else ""
            print(f"{i+1}. {emergency_mark}{request['ai_name']}: {request['item_name']} ({request['reason']})")
        
        print(f"{len(self.pending_requests)+1}. 모두 거절")
        print(f"{len(self.pending_requests)+2}. 모두 승인")
        
        try:
            choice = input("응답 선택: ")
            
            if choice == str(len(self.pending_requests)+1):
                # 모두 거절
                for request in self.pending_requests:
                    print(f"❌ {request['ai_name']}의 요청 거절됨")
                self.pending_requests.clear()
                return True
            
            elif choice == str(len(self.pending_requests)+2):
                # 모두 승인
                for request in self.pending_requests:
                    self._execute_item_usage(
                        request["ai_name"], 
                        request["item_name"], 
                        request["reason"], 
                        request["emergency"]
                    )
                self.pending_requests.clear()
                return True
            
            else:
                # 개별 선택
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(self.pending_requests):
                    request = self.pending_requests.pop(choice_idx)
                    approval = input(f"승인하시겠습니까? (y/n): ").lower() == 'y'
                    
                    if approval:
                        self._execute_item_usage(
                            request["ai_name"], 
                            request["item_name"], 
                            request["reason"], 
                            request["emergency"]
                        )
                    else:
                        print(f"❌ {request['ai_name']}의 요청 거절됨")
                    
                    return True
        
        except ValueError:
            print("❌ 잘못된 입력입니다.")
        
        return False
    
    def set_sharing_permission(self, permission: ItemSharingPermission):
        """아이템 공유 권한 설정"""
        self.sharing_permission = permission
        permission_names = {
            ItemSharingPermission.FULL_ACCESS: "전체 접근 허용",
            ItemSharingPermission.LIMITED_ACCESS: "제한적 접근 (치료/회복만)",
            ItemSharingPermission.ASK_PERMISSION: "사용 전 확인",
            ItemSharingPermission.NO_ACCESS: "사용 금지"
        }
        print(f"📋 아이템 공유 권한이 '{permission_names[permission]}'(으)로 설정되었습니다.")
    
    def _show_shared_inventory(self):
        """공용 인벤토리 표시"""
        if not self.shared_inventory:
            print("📦 공용 인벤토리가 비어있습니다.")
            return
        
        print("\n📦 공용 인벤토리:")
        print("="*50)
        
        for item_name, item_info in self.shared_inventory.items():
            total = item_info["count"]
            reserved = item_info["reserved_for_player"]
            available = total - reserved
            
            print(f"{item_name}: {total}개 (AI 사용가능: {available}개)")
    
    def show_usage_statistics(self):
        """아이템 사용 통계 표시"""
        if not self.usage_records:
            print("📊 아이템 사용 기록이 없습니다.")
            return
        
        print("\n📊 AI 아이템 사용 통계:")
        print("="*50)
        
        # AI별 사용량
        ai_usage = {}
        for record in self.usage_records:
            if record.ai_name not in ai_usage:
                ai_usage[record.ai_name] = {}
            
            item_type = record.item_type
            ai_usage[record.ai_name][item_type] = ai_usage[record.ai_name].get(item_type, 0) + 1
        
        for ai_name, items in ai_usage.items():
            print(f"\n🤖 {ai_name}:")
            for item_type, count in items.items():
                print(f"   {item_type}: {count}개")
        
        # 최근 사용 기록
        print(f"\n📋 최근 사용 기록 (최대 10개):")
        recent_records = self.usage_records[-10:]
        for record in recent_records:
            print(f"   {record.ai_name}: {record.item_type} ({record.reason})")
    
    def emergency_item_usage(self, ai_name: str, character: Character) -> bool:
        """응급 상황 아이템 자동 사용"""
        # HP가 30% 이하면 체력 포션 사용
        if character.current_hp / character.max_hp <= 0.3:
            if "체력 포션" in self.shared_inventory:
                return self.request_item_usage(ai_name, "체력 포션", "위험한 HP 상황", emergency=True)
        
        # MP가 20% 이하면 마나 포션 사용
        if character.current_mp / character.max_mp <= 0.2:
            if "마나 포션" in self.shared_inventory:
                return self.request_item_usage(ai_name, "마나 포션", "MP 부족", emergency=True)
        
        # 중독 상태면 해독제 사용
        if hasattr(character, 'status_effects') and 'poison' in character.status_effects:
            if "해독제" in self.shared_inventory:
                return self.request_item_usage(ai_name, "해독제", "중독 치료", emergency=True)
        
        return False
    
    def suggest_item_sharing_mode(self, party_members: List[Character]) -> ItemSharingPermission:
        """파티 구성에 따른 권장 공유 모드"""
        ai_count = sum(1 for char in party_members if not char.is_alive)  # 임시로 사망자 수로 대체
        total_count = len(party_members)
        
        if ai_count == 0:
            return ItemSharingPermission.NO_ACCESS
        elif ai_count == 1:
            return ItemSharingPermission.LIMITED_ACCESS
        elif ai_count >= total_count // 2:
            return ItemSharingPermission.FULL_ACCESS
        else:
            return ItemSharingPermission.ASK_PERMISSION
    
    def get_sharing_status(self) -> str:
        """공유 시스템 상태 정보"""
        permission_names = {
            ItemSharingPermission.FULL_ACCESS: "전체 접근 허용",
            ItemSharingPermission.LIMITED_ACCESS: "제한적 접근",
            ItemSharingPermission.ASK_PERMISSION: "사용 전 확인",
            ItemSharingPermission.NO_ACCESS: "사용 금지"
        }
        
        status_lines = [
            f"📋 공유 권한: {permission_names[self.sharing_permission]}",
            f"📦 공용 아이템: {len(self.shared_inventory)}종류",
            f"📊 사용 기록: {len(self.usage_records)}건",
            f"💬 대기 요청: {len(self.pending_requests)}건"
        ]
        
        return "\n".join(status_lines)

# 전역 파티 아이템 공유 시스템
party_item_sharing = PartyItemSharingSystem()

def initialize_item_sharing(party_inventory: Dict):
    """아이템 공유 시스템 초기화"""
    return party_item_sharing.initialize_shared_inventory(party_inventory)

def handle_ai_item_request(ai_name: str, item_name: str, reason: str, emergency: bool = False) -> bool:
    """AI 아이템 사용 요청 처리"""
    return party_item_sharing.request_item_usage(ai_name, item_name, reason, emergency)
