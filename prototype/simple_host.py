import asyncio
import websockets
import json
import time

class SimpleHost:
    def __init__(self, port=7176):
        self.port = port
        self.clients = set()
        self.session_id = f"session_{int(time.time())}"
        
    async def handle_client(self, websocket):
        """클라이언트 연결 처리"""
        self.clients.add(websocket)
        print(f"✅ 플레이어 접속! 총 {len(self.clients)}명")
        
        try:
            # 환영 메시지
            welcome = {
                "type": "welcome",
                "session_id": self.session_id,
                "message": "Dawn of Stellar 멀티플레이어에 오신 것을 환영합니다!"
            }
            await websocket.send(json.dumps(welcome))
            
            # 메시지 수신 대기
            async for message in websocket:
                data = json.loads(message)
                print(f"📨 받은 메시지: {data}")
                
                # 다른 클라이언트들에게 브로드캐스트
                if len(self.clients) > 1:
                    broadcast_msg = {
                        "type": "broadcast",
                        "sender": "player",
                        "data": data
                    }
                    await self.broadcast_to_others(websocket, json.dumps(broadcast_msg))
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            print(f"❌ 플레이어 퇴장. 남은 인원: {len(self.clients)}명")
            
    async def broadcast_to_others(self, sender, message):
        """다른 클라이언트들에게 메시지 브로드캐스트"""
        for client in self.clients:
            if client != sender:
                try:
                    await client.send(message)
                except:
                    pass  # 연결 끊긴 클라이언트 무시
                    
    async def start_server(self):
        """서버 시작"""
        print(f"🌟 Dawn of Stellar 호스트 시작 (포트: {self.port})")
        print(f"📡 세션 ID: {self.session_id}")
        print("🎮 클라이언트 접속 대기 중...")
        
        async with websockets.serve(self.handle_client, "localhost", self.port):
            await asyncio.Future()  # 계속 실행

if __name__ == "__main__":
    host = SimpleHost()
    asyncio.run(host.start_server())
