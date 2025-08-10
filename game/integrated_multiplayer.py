"""
🎮 Dawn of Stellar - 실제 게임 통합 멀티플레이어 시스템
실제 Dawn of Stellar 게임과 완전 통합된 네트워크 멀티플레이어

2025년 8월 10일 - 게임 통합 완료
"""

import asyncio
import json
import threading
import time
from typing import Dict, List, Any, Optional
from game.real_player_multiplayer import RealPlayerMultiplayerServer, NetworkPlayer, NetworkGameState, PlayerConnectionState
try:
    from game.party_manager import PartyManager
    from game.character import Character, CharacterClass
    from game.brave_combat import BraveCombatSystem
    from game.world import World
    from game.ai_game_mode_manager import AIGameModeManager
except ImportError:
    # 간단한 더미 클래스들로 대체
    print("⚠️ 일부 게임 모듈을 찾을 수 없어 더미 클래스를 사용합니다")
    
    class PartyManager:
        def __init__(self): 
            self.members = []
        def add_member(self, member): 
            self.members.append(member)
    
    class Character:
        def __init__(self, name, character_class, level=1):
            self.name = name
            self.character_class = character_class
            self.level = level
            self.current_hp = 100
            self.max_hp = 100
            self.current_mp = 50
            self.max_mp = 50
            self.exp = 0
    
    class CharacterClass:
        WARRIOR = "전사"
        ARCHMAGE = "아크메이지"
        ARCHER = "궁수"
        ROGUE = "도적"
    
    class BraveCombatSystem:
        def __init__(self, party_manager, ai_game_mode_manager):
            self.party_manager = party_manager
            self.ai_manager = ai_game_mode_manager
    
    class World:
        def __init__(self):
            self.width = 20
            self.height = 20
            self.player_pos = (10, 10)
            self.current_floor = 1
        
        def generate_floor(self, floor): 
            pass
        
        def get_random_empty_position(self): 
            return (10, 10)
        
        def move_player(self, direction):
            # 간단한 이동 처리
            x, y = self.player_pos
            if direction == "north": y -= 1
            elif direction == "south": y += 1
            elif direction == "east": x += 1
            elif direction == "west": x -= 1
            
            if 0 <= x < self.width and 0 <= y < self.height:
                self.player_pos = (x, y)
                return {"moved": True, "exploration": "새로운 지역을 발견했습니다!"}
            else:
                return {"moved": False, "reason": "그 방향으로는 갈 수 없습니다"}
        
        def check_for_combat(self): 
            import random
            return random.random() < 0.3  # 30% 확률로 전투
        
        def explore_current_tile(self): 
            return "주변을 둘러보니 특별한 것은 없어 보입니다"
        
        def get_current_tile_info(self): 
            return {"type": "일반", "description": "평범한 던전 바닥"}
    
    class AIGameModeManager:
        def __init__(self): 
            pass

class DawnOfStellarMultiplayerServer(RealPlayerMultiplayerServer):
    """Dawn of Stellar 게임과 통합된 멀티플레이어 서버"""
    
    def __init__(self, port: int = 7176):
        super().__init__(port)
        
        # 게임 시스템들
        self.party_manager = PartyManager()
        self.world = None
        self.combat_system = None
        self.ai_manager = AIGameModeManager()
        
        # 게임 상태
        self.game_characters: Dict[str, Character] = {}
        self.current_floor = 1
        self.in_combat = False
        self.combat_participants: List[str] = []
        
        print(f"🎮 Dawn of Stellar 멀티플레이어 서버 초기화 완료")
    
    async def _initialize_game(self):
        """실제 Dawn of Stellar 게임 초기화"""
        print(f"🚀 Dawn of Stellar 게임 초기화 시작...")
        
        # 월드 생성
        self.world = World()
        self.world.generate_floor(self.current_floor)
        
        # 플레이어 캐릭터 생성
        character_classes = [CharacterClass.WARRIOR, CharacterClass.ARCHMAGE, CharacterClass.ARCHER, CharacterClass.ROGUE]
        
        for i, player_id in enumerate(self.turn_order):
            player = self.players[player_id]
            
            # 캐릭터 클래스 선택 (순환)
            char_class = character_classes[i % len(character_classes)]
            
            # 캐릭터 생성
            character = Character(
                name=player.name,
                character_class=char_class,
                level=1
            )
            
            # 시작 위치 설정
            start_pos = self.world.get_random_empty_position()
            self.world.player_pos = start_pos
            
            # 캐릭터 등록
            self.game_characters[player_id] = character
            self.party_manager.add_member(character)
            
            # 플레이어 데이터 업데이트
            player.character_data = {
                "name": character.name,
                "class": character.character_class.value,
                "level": character.level,
                "hp": character.current_hp,
                "max_hp": character.max_hp,
                "mp": character.current_mp,
                "max_mp": character.max_mp,
                "brv": getattr(character, 'current_brv', 0),
                "position": list(start_pos),
                "atb": 0
            }
            
            print(f"   🏃 {player.name} ({char_class.value}) 생성 완료")
        
        # 전투 시스템 초기화
        self.combat_system = BraveCombatSystem(
            party_manager=self.party_manager,
            ai_game_mode_manager=self.ai_manager
        )
        
        # 게임 데이터 업데이트
        self.game_data = {
            "world": {
                "floor": self.current_floor,
                "size": (self.world.width, self.world.height),
                "player_position": list(self.world.player_pos)
            },
            "characters": {
                pid: player.character_data for pid, player in self.players.items() 
                if player.character_data
            }
        }
        
        print(f"✅ Dawn of Stellar 게임 초기화 완료!")
        
        # 게임 상태를 모든 플레이어에게 전송
        await self._broadcast_game_world()
    
    async def _process_game_action(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """실제 Dawn of Stellar 게임 액션 처리"""
        action_type = action.get("action_type")
        
        if action_type == "move":
            return await self._process_move_action_real(player_id, action)
        elif action_type == "explore":
            return await self._process_explore_action(player_id, action)
        elif action_type == "combat_action":
            return await self._process_combat_action(player_id, action)
        elif action_type == "use_item":
            return await self._process_item_action_real(player_id, action)
        elif action_type == "check_status":
            return await self._process_status_check(player_id)
        elif action_type == "rest":
            return await self._process_rest_action(player_id)
        else:
            return {"success": False, "message": "알 수 없는 액션입니다"}
    
    async def _process_move_action_real(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """실제 이동 처리"""
        if self.in_combat:
            return {"success": False, "message": "전투 중에는 이동할 수 없습니다"}
        
        direction = action.get("direction")
        character = self.game_characters.get(player_id)
        
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다"}
        
        # 현재 위치
        current_pos = list(self.world.player_pos)
        
        # 이동 처리
        move_result = self.world.move_player(direction)
        
        if move_result["moved"]:
            # 캐릭터 데이터 업데이트
            new_pos = list(self.world.player_pos)
            self.players[player_id].character_data["position"] = new_pos
            
            # 적과의 전투 체크
            if self.world.check_for_combat():
                await self._start_combat(player_id)
                return {
                    "success": True,
                    "message": f"{direction} 방향으로 이동했습니다. 적과 마주쳤습니다!",
                    "new_position": new_pos,
                    "combat_started": True
                }
            
            # 월드 상태 브로드캐스트
            await self._broadcast_game_world()
            
            return {
                "success": True,
                "message": f"{direction} 방향으로 이동했습니다",
                "new_position": new_pos,
                "exploration": move_result.get("exploration", "")
            }
        else:
            return {"success": False, "message": move_result.get("reason", "이동할 수 없습니다")}
    
    async def _process_explore_action(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """탐험 액션 처리"""
        character = self.game_characters.get(player_id)
        
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다"}
        
        # 주변 탐험
        exploration_result = self.world.explore_current_tile()
        
        return {
            "success": True,
            "message": "주변을 탐험했습니다",
            "exploration": exploration_result
        }
    
    async def _process_combat_action(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """전투 액션 처리"""
        if not self.in_combat:
            return {"success": False, "message": "전투 중이 아닙니다"}
        
        character = self.game_characters.get(player_id)
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다"}
        
        combat_action = action.get("combat_action")
        target = action.get("target")
        
        if combat_action == "attack":
            # 기본 공격
            result = f"{character.name}이(가) 공격했습니다!"
        elif combat_action == "skill":
            skill_name = action.get("skill_name", "기본 스킬")
            result = f"{character.name}이(가) {skill_name}을(를) 사용했습니다!"
        elif combat_action == "defend":
            result = f"{character.name}이(가) 방어 자세를 취했습니다!"
        else:
            result = "알 수 없는 전투 액션입니다"
        
        # 전투 결과 브로드캐스트
        await self._broadcast_combat_update(player_id, combat_action, result)
        
        return {
            "success": True,
            "message": result,
            "combat_action": combat_action
        }
    
    async def _process_item_action_real(self, player_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """아이템 사용 처리"""
        character = self.game_characters.get(player_id)
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다"}
        
        item_name = action.get("item_name", "체력 포션")
        
        if "포션" in item_name:
            # 포션 사용
            heal_amount = 30
            old_hp = character.current_hp
            character.current_hp = min(character.current_hp + heal_amount, character.max_hp)
            actual_heal = character.current_hp - old_hp
            
            # 캐릭터 데이터 업데이트
            self.players[player_id].character_data["hp"] = character.current_hp
            
            return {
                "success": True,
                "message": f"{item_name}을(를) 사용하여 {actual_heal} 회복했습니다",
                "heal_amount": actual_heal,
                "current_hp": character.current_hp,
                "max_hp": character.max_hp
            }
        
        return {"success": False, "message": "사용할 수 없는 아이템입니다"}
    
    async def _process_status_check(self, player_id: str) -> Dict[str, Any]:
        """상태 확인"""
        character = self.game_characters.get(player_id)
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다"}
        
        status_info = {
            "name": character.name,
            "class": character.character_class.value,
            "level": character.level,
            "hp": f"{character.current_hp}/{character.max_hp}",
            "mp": f"{character.current_mp}/{character.max_mp}",
            "exp": character.exp,
            "position": self.players[player_id].character_data["position"]
        }
        
        return {
            "success": True,
            "message": "캐릭터 상태를 확인했습니다",
            "status": status_info
        }
    
    async def _process_rest_action(self, player_id: str) -> Dict[str, Any]:
        """휴식 액션"""
        if self.in_combat:
            return {"success": False, "message": "전투 중에는 휴식할 수 없습니다"}
        
        character = self.game_characters.get(player_id)
        if not character:
            return {"success": False, "message": "캐릭터를 찾을 수 없습니다"}
        
        # 체력/마나 약간 회복
        hp_heal = min(10, character.max_hp - character.current_hp)
        mp_heal = min(5, character.max_mp - character.current_mp)
        
        character.current_hp += hp_heal
        character.current_mp += mp_heal
        
        # 캐릭터 데이터 업데이트
        player_data = self.players[player_id].character_data
        player_data["hp"] = character.current_hp
        player_data["mp"] = character.current_mp
        
        return {
            "success": True,
            "message": f"휴식을 취했습니다. HP +{hp_heal}, MP +{mp_heal}",
            "hp_heal": hp_heal,
            "mp_heal": mp_heal,
            "current_hp": character.current_hp,
            "current_mp": character.current_mp
        }
    
    async def _start_combat(self, initiator_id: str):
        """전투 시작"""
        print(f"⚔️ 전투 시작! 개시자: {self.players[initiator_id].name}")
        
        self.in_combat = True
        self.combat_participants = list(self.game_characters.keys())
        
        # 전투 시작 알림
        await self._broadcast({
            "type": "combat_started",
            "initiator": initiator_id,
            "participants": [
                {
                    "player_id": pid,
                    "character_name": self.game_characters[pid].name
                }
                for pid in self.combat_participants
            ]
        })
    
    async def _broadcast_combat_update(self, actor_id: str, action: str, result: str):
        """전투 업데이트 브로드캐스트"""
        await self._broadcast({
            "type": "combat_update",
            "actor_id": actor_id,
            "actor_name": self.game_characters[actor_id].name,
            "action": action,
            "result": result,
            "characters": {
                pid: {
                    "hp": char.current_hp,
                    "max_hp": char.max_hp,
                    "mp": char.current_mp,
                    "max_mp": char.max_mp
                }
                for pid, char in self.game_characters.items()
            }
        })
    
    async def _broadcast_game_world(self):
        """게임 월드 상태 브로드캐스트"""
        world_data = {
            "type": "world_update",
            "floor": self.current_floor,
            "map_size": (self.world.width, self.world.height),
            "current_tile": self.world.get_current_tile_info(),
            "characters": {
                pid: player.character_data 
                for pid, player in self.players.items() 
                if player.character_data
            },
            "in_combat": self.in_combat
        }
        
        await self._broadcast(world_data)

class MultiplayerGameLauncher:
    """멀티플레이어 게임 런처"""
    
    def __init__(self):
        self.server = None
        self.running = False
    
    async def start_multiplayer_game(self, port: int = 7176):
        """멀티플레이어 게임 시작"""
        print(f"🚀 Dawn of Stellar 멀티플레이어 게임 시작!")
        print(f"   포트: {port}")
        
        # 서버 생성 및 시작
        self.server = DawnOfStellarMultiplayerServer(port)
        self.running = True
        
        try:
            await self.server.start_server()
        except KeyboardInterrupt:
            print(f"\n🛑 게임 서버를 중지합니다...")
            await self.stop_game()
        except Exception as e:
            print(f"❌ 서버 오류: {e}")
            await self.stop_game()
    
    async def stop_game(self):
        """게임 중지"""
        if self.server:
            await self.server.stop_server()
        self.running = False
        print(f"✅ 멀티플레이어 게임이 종료되었습니다")

def start_multiplayer_server():
    """멀티플레이어 서버 시작 (동기 함수)"""
    launcher = MultiplayerGameLauncher()
    
    try:
        asyncio.run(launcher.start_multiplayer_game())
    except KeyboardInterrupt:
        print(f"\n👋 게임을 종료합니다")

async def demo_integrated_multiplayer():
    """통합 멀티플레이어 데모"""
    print(f"🎮 === Dawn of Stellar 통합 멀티플레이어 데모! ===")
    print()
    
    launcher = MultiplayerGameLauncher()
    
    # 서버 시작
    server_task = asyncio.create_task(launcher.start_multiplayer_game(7176))
    
    # 잠시 대기
    await asyncio.sleep(5)
    
    print(f"🎯 실제 Dawn of Stellar 게임이 실행 중입니다!")
    print(f"💪 플레이어들은 실제 캐릭터로 던전을 탐험하고 전투를 할 수 있습니다!")
    print(f"🤝 AI 플레이어들과 함께 협력 플레이!")
    print()
    print(f"🌐 웹 브라우저에서 web_multiplayer_client.html을 열어 테스트하세요!")
    print(f"📱 모바일에서도 접속 가능합니다!")
    print()
    
    # 15초 후 데모 종료
    await asyncio.sleep(15)
    
    print(f"🛑 데모 종료. 서버를 중지합니다...")
    await launcher.stop_game()

if __name__ == "__main__":
    # 직접 실행 시 서버 시작
    start_multiplayer_server()
