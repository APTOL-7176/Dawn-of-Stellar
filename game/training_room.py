"""
트레이닝 룸 호환성 모듈
BattlegroundTrainingCenter를 TrainingRoom으로 import 가능하게 하는 브릿지
"""

from .battleground_training import BattlegroundTrainingCenter

# 호환성을 위한 별칭
TrainingRoom = BattlegroundTrainingCenter

# 기존 코드와의 호환성을 위해 클래스 직접 노출
class TrainingRoom(BattlegroundTrainingCenter):
    """기존 TrainingRoom 클래스와의 호환성을 위한 래퍼"""
    
    def __init__(self, audio_system=None, keyboard=None):
        super().__init__(audio_system, keyboard)
        
    def run(self):
        """기존 run 메서드 호환성"""
        return self.start_training()
        
    def show_training_menu(self):
        """기존 메뉴 호출 호환성"""
        return self.start_training()
    
    def enter_training_room(self, party_manager=None):
        """훈련소 입장 - 기존 코드와의 호환성을 위한 메서드"""
        if party_manager:
            # 파티 멤버 복사
            self.training_party = party_manager.members.copy()
        return self.start_training()