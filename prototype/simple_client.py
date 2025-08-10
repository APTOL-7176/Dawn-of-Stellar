import asyncio
import json
import sys
import threading
import time

try:
    import websockets
except ImportError:
    print("❌ websockets 라이브러리가 필요합니다!")
    print("설치 방법: pip install websockets")
    sys.exit(1)

class SimpleClient:
    def __init__(self, host="localhost", port=7176):
        self.host = host
        self.port = port
        self.websocket = None
        self.running = True
        
    async def connect(self):
        """서버에 접속"""
        try:
            self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
            print(f"✅ 서버에 접속 성공! ({self.host}:{self.port})")
            
            # 메시지 수신 대기 (백그라운드)
            listen_task = asyncio.create_task(self.listen_messages())
            
            # 사용자 입력 대기
            await self.handle_user_input()
            
            # 정리
            listen_task.cancel()
            
        except Exception as e:
            print(f"❌ 접속 실패: {e}")
            
    async def listen_messages(self):
        """서버로부터 메시지 수신"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data["type"] == "welcome":
                    print(f"🎉 {data['message']}")
                    print(f"📡 세션 ID: {data['session_id']}")
                    print("\n💬 메시지를 입력하세요 (quit으로 종료):")
                    
                elif data["type"] == "broadcast":
                    print(f"\n📨 다른 플레이어: {data['data']['message']}")
                    print("💬 메시지 입력: ", end="", flush=True)
                    
        except websockets.exceptions.ConnectionClosed:
            print("\n❌ 서버와의 연결이 끊어졌습니다.")
            self.running = False
            
    def get_input(self, prompt):
        """별도 스레드에서 입력 받기"""
        return input(prompt)
            
    async def handle_user_input(self):
        """사용자 입력 처리"""
        while self.running:
            try:
                # 비동기 입력 받기
                message = await asyncio.get_event_loop().run_in_executor(
                    None, self.get_input, "💬 메시지 입력: "
                )
                
                if message.lower() == "quit":
                    break
                    
                if not message.strip():
                    continue
                    
                # 서버로 메시지 전송
                data = {
                    "type": "chat",
                    "message": message
                }
                await self.websocket.send(json.dumps(data))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 입력 처리 오류: {e}")
                break
                
        if self.websocket:
            await self.websocket.close()

if __name__ == "__main__":
    print("🌟 Dawn of Stellar 멀티플레이어 클라이언트")
    print("="*50)
    
    client = SimpleClient()
    try:
        asyncio.run(client.connect())
    except KeyboardInterrupt:
        print("\n🛑 클라이언트 종료")
