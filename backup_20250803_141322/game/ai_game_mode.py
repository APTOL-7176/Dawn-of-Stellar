"""
AI 파티원 게임모드 - 전체 시스템 통합 (성별/성격 대화 시스템 포함)
플레이어가 선택한 캐릭터만 직접 조작하고, 나머지는 AI가 자동 조작
저장시스템, 필드스킬, 요리시스템, 장비시스템, 성별 기반 대화시스템 모두 연동
"""
import random
import time
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .ai_companion_system import AICompanion, AIPersonality, AIRequest, ai_mercenary_manager
from .character import Character

# 캐릭터 성별/성격 시스템
class CharacterGender(Enum):
    """캐릭터 성별"""
    MALE = "male"
    FEMALE = "female"

class CharacterPersonality(Enum):
    """캐릭터 성격 타입"""
    CHEERFUL = "cheerful"       # 밝고 쾌활한
    SERIOUS = "serious"         # 진지하고 엄격한
    GENTLE = "gentle"           # 온화하고 친절한
    COLD = "cold"               # 차갑고 냉정한
    PLAYFUL = "playful"         # 장난기 많고 활발한
    MYSTERIOUS = "mysterious"   # 신비롭고 과묵한
    HOT_TEMPERED = "hot_tempered"  # 성격이 급하고 화를 잘 냄
    WISE = "wise"               # 현명하고 침착한
    BALANCED = "balanced"       # 균형잡힌 (기본값)

class CharacterTraits:
    """캐릭터 특성 (성별, 성격, 대화 스타일)"""
    
    # 남성 이름 풀 (auto_party_builder에서 가져옴)
    MALE_NAMES = [
        "아리우스", "발렌타인", "가브리엘", "라파엘", "카이저", "레오나르드", "세바스찬", "알렉산더",
        "막시무스", "아드리안", "루카스", "니콜라스", "도미닉", "빈센트", "에밀리오", "마르코",
        "클라우디우스", "오거스트", "바실리우스", "이그니스", "펠릭스", "라이언", "에릭",
        "마틴", "엘리아스", "다미안", "율리안", "카를로스", "디에고", "파블로", "프란시스",
        "로드리고", "안토니오", "페드로", "미구엘", "호세", "루이스", "페르난도", "애드워드",
        "라몬", "호르헤", "마누엘", "프랑크", "올리버", "해리", "잭", "윌리엄", "제임스",
        "찰스", "로버트", "마이클", "데이비드", "리처드", "조셉", "토머스", "크리스토퍼",
        "매트", "앤소니", "마크", "도널드", "스티븐", "폴", "앤드류", "조슈아", "케네스",
        "케빈", "브라이언", "조지", "에드워드", "로널드", "티모시", "제이슨", "제프리",
        "라이언", "제이콥", "게리", "니콜라스", "조나단", "래리", "저스틴", "스콧",
        "브랜든", "벤자민", "사무엘", "그레고리", "패트릭", "데니스", "제리", "타일러",
        "애런", "헨리", "더글러스", "네이선", "피터", "잭슨", "노아", "이단", "루카스",
        "메이슨", "로건", "윌리엄", "엘리야", "웨인", "칼렙", "니콜라스", "조던",
        "그레이슨", "헌터", "에이든", "카메론", "코너", "산티아고", "이사이야", "찰리",
        "이반", "오웬", "루크", "딜런", "잭슨", "가빈", "콜튼", "맥스", "브레이든",
        "카터", "다니엘", "아담", "엘라이", "핀", "코딘", "트리스탄", "로넌", "블레이크",
        "브로디", "데클런", "숀", "리암", "루카", "제임슨", "카일", "알렉스", "자이든",
        "자비에르", "도미닉", "데미트리", "에이스", "니키타", "블라디미르", "알렉세이",
        "이반", "안톤", "올렉", "세르겐", "빅터", "로만", "파벨", "녹티스", "아르템",
        "콘스탄틴", "발렌틴", "드미트리", "티더", "클라우드", "프롬프토", "그림니르", "시스", "랜슬롯"
    ]
    
    # 여성 이름 풀
    FEMALE_NAMES = [
        "아리아", "셀레스트", "유나", "이사벨라", "발레리아", "세라피나", "아드리아나", "밀리아",
        "비비안", "클라라", "비라", "유엘", "에밀리아", "루시아", "소피아", "올리비아",
        "나탈리아", "카밀라", "레오니", "미리암", "로사", "에스텔라", "바이올렛", "샬롯",
        "베아트리체", "카타리나", "레베카", "엘레나", "마리아", "안나", "루나", "시에라",
        "니나", "에바", "릴리안", "로렌", "그레이스", "에밀리", "한나", "엠마", "매디슨",
        "애슐리", "사라", "브리트니", "사만다", "제시카", "아만다", "스테파니", "니콜",
        "멜리사", "데보라", "레이첼", "캐서린", "엘리자베스", "해더", "티파니", "에이미",
        "줄리", "조이스", "빅토리아", "켈리", "크리스티나", "조안", "이블린", "린다",
        "바바라", "엘렌", "캐럴", "산드라", "도나", "루스", "샤론", "미셸", "로라",
        "칼라", "스테파니", "캐롤라인", "엘리", "제나", "브룩", "케이트", "사바나",
        "테일러", "킴벌리", "데이지", "하이디", "가브리엘라", "니키", "로린", "셸리",
        "레슬리", "에리카", "카일린", "애나", "코트니", "루비", "메간", "알렉시스",
        "클로에", "이사벨", "에이바", "밀라", "아리아나", "라일라", "미아", "라일리",
        "클레어", "엘리아나", "나오미", "네이탈리", "헤일리", "브루클린", "앨리슨",
        "자스민", "마야", "페넬로페", "오드리", "스카를릿", "애나스타샤", "베로니카",
        "테레사", "앤젤라", "카르멘", "몰리", "웬디", "리사", "아니타", "리비",
        "알리시아", "알렉산드라", "키아라", "조아나", "마리사", "카렌", "스테이시",
        "다이애나", "로즈", "이솔데", "기네비어", "모르가나", "아르테미스", "아테나",
        "헤라", "아프로디테", "헤스티아", "데메테르", "펠레", "프레이야", "이두나",
        "브룬힐데", "발키리", "키르케", "카산드라", "안드로메다", "헬렌", "클레오파트라",
        "이시스", "네페르티티", "세라핌", "우리엘", "가브리엘라", "미카엘라", "라파엘라",
        "아리엘", "젤다", "세레나", "팬도라", "포에베", "셀레네", "헤카테", "님프",
        "오로라", "스텔라", "노바", "베가", "카시오페아", "라이라", "알타이르",
        "벨라트릭스", "리겔", "시리우스", "프로키온", "아크투루스", "스피카", "알데바란",
        "카펠라", "폴룩스", "레굴루스", "안타레스"
    ]
    
    # 성격별 대화 스타일 (대폭 확장)
    PERSONALITY_DIALOGUE = {
        CharacterPersonality.CHEERFUL: {
            "greeting": ["안녕! 오늘도 신나는 하루야!", "와! 뭔가 재밌는 일이 생길 것 같아!", "좋은 아침이야! 기분이 최고!", 
                        "헤이! 같이 모험하자!", "오늘은 정말 좋은 날이 될 것 같아!", "모두 모여서 다행이야!",
                        "너무 기대돼! 뭘 할 거야?", "와, 날씨도 좋고 기분도 좋아!", "함께 있어서 정말 즐거워!"],
            "battle_start": ["이번엔 내가 활약할 차례야!", "우리 같이 힘내자!", "모두 파이팅!", 
                           "신나는 전투 시작!", "다들 준비됐지? 가자!", "우리가 이길 거야!",
                           "힘내자! 우리는 최고의 팀이야!", "전투도 재밌게 하자!", "모두 함께 싸우자!"],
            "victory": ["야호! 우리가 이겼어!", "정말 멋진 팀워크였어!", "다들 고생했어!", 
                       "완벽한 승리야!", "우리 정말 대단해!", "이런 기분 최고야!",
                       "다음 전투도 기대돼!", "모두가 최고였어!", "승리의 기쁨을 나누자!"],
            "low_hp": ["앗, 좀 아프긴 하지만 괜찮아!", "아직 할 수 있어!", "걱정 마, 금방 회복될 거야!",
                      "이 정도는 아무것도 아니야!", "아직 포기하지 않을 거야!", "다시 일어설 수 있어!",
                      "조금만 쉬면 괜찮을 거야!", "내 의지는 꺾이지 않아!", "희망을 잃지 않을게!"],
            "item_request": ["혹시 회복 아이템 하나만 줄 수 있을까?", "아이템 좀 나눠줄래?", "도움이 필요해!",
                           "같이 나눠 쓰자!", "친구끼리 서로 도와야지!", "부탁해도 될까?",
                           "아이템 좀 빌려줄래?", "우리는 한 팀이잖아!", "도와주면 정말 고마울 거야!"],
            "praise": ["와, 정말 대단해!", "너 진짜 멋있다!", "최고야!", 
                      "정말 훌륭한 실력이야!", "존경스러워!", "어떻게 그렇게 잘해?",
                      "너무 멋져서 말이 안 나와!", "진짜 프로구나!", "배우고 싶어!"],
            "thanks": ["고마워! 정말 도움이 됐어!", "역시 믿을 만해!", "너 덕분이야!",
                      "정말 고마운 친구야!", "언제든 나도 도와줄게!", "친구가 있어서 다행이야!",
                      "마음이 따뜻해져!", "이런 친구를 둬서 행복해!", "정말 감동이야!"]
        },
        CharacterPersonality.SERIOUS: {
            "greeting": ["안녕하다.", "오늘도 최선을 다하자.", "준비는 끝났다.",
                        "임무에 집중하자.", "책임감을 가지고 행동하자.", "진중하게 접근하자.",
                        "목표를 명확히 하자.", "계획적으로 움직이자.", "냉정함을 유지하자."],
            "battle_start": ["방심하지 말자.", "신중하게 접근하자.", "계획대로 움직이자.",
                           "전술을 준수하자.", "각자의 역할에 충실하자.", "실수는 허용되지 않는다.",
                           "침착하게 대응하자.", "완벽하게 수행하자.", "프로답게 행동하자."],
            "victory": ["좋은 결과다.", "모두 수고했다.", "다음을 준비하자.",
                       "계획대로 진행됐다.", "만족스러운 성과다.", "효율적이었다.",
                       "전술이 성공했다.", "팀워크가 좋았다.", "다음 목표로 이동하자."],
            "low_hp": ["상황이 좋지 않다.", "치료가 필요하다.", "잠시 후퇴하겠다.",
                      "전략적 후퇴가 필요하다.", "재정비가 필요하다.", "상황을 파악해야 한다.",
                      "무리하지 않겠다.", "현실적인 판단이 필요하다.", "냉정하게 대처하자."],
            "item_request": ["회복 아이템이 필요하다.", "지원을 요청한다.", "도움이 필요하다.",
                           "전술적 지원이 필요하다.", "자원 배분을 요청한다.", "효율적인 지원을 부탁한다.",
                           "전략적 판단을 구한다.", "협력이 필요하다.", "팀워크를 발휘하자."],
            "praise": ["훌륭한 판단이었다.", "좋은 전술이다.", "신뢰할 수 있다.",
                      "전문가다운 실력이다.", "효과적인 행동이었다.", "기대 이상의 성과다.",
                      "완벽한 수행이었다.", "프로의 자질이 보인다.", "존경스럽다."],
            "thanks": ["고맙다.", "도움을 잊지 않겠다.", "빚을 졌다.",
                      "감사의 말을 전한다.", "협력에 감사한다.", "도움이 컸다.",
                      "신뢰에 보답하겠다.", "은혜를 기억하겠다.", "좋은 동료다."]
        },
        CharacterPersonality.GENTLE: {
            "greeting": ["안녕하세요~ 좋은 하루예요.", "오늘도 함께해서 기뻐요.", "평안한 아침이네요.",
                        "모두 건강하신가요?", "오늘도 무사히 만나서 다행이에요.", "함께 있어서 마음이 편해요.",
                        "좋은 시간이 되길 바라요.", "평화로운 하루가 되면 좋겠어요.", "모두 웃는 얼굴이네요."],
            "battle_start": ["조심해서 가요.", "서로 지켜주면서 해요.", "무리하지 말아요.",
                           "안전을 우선으로 해요.", "서로 걱정해주며 해요.", "다치지 않게 조심해요.",
                           "천천히 신중하게 가요.", "모두 무사히 돌아가요.", "평화롭게 해결되면 좋겠어요."],
            "victory": ["다행이에요. 모두 무사해서 좋아요.", "수고하셨어요.", "잘 했어요.",
                       "모두 건강해서 다행이에요.", "평화롭게 끝나서 좋아요.", "걱정했는데 잘 됐네요.",
                       "서로 도와서 이겼어요.", "아무도 다치지 않아서 정말 다행이에요.", "조심스럽게 잘 했어요."],
            "low_hp": ["죄송해요, 제가 부주의했나 봐요.", "괜찮아요, 걱정 마세요.", "조금만 쉬면 괜찮을 거예요.",
                      "제가 실수했나 봐요.", "걱정 끼쳐드려서 죄송해요.", "곧 나아질 거예요.",
                      "다들 신경 쓰지 마세요.", "저는 괜찮으니까요.", "조금 아프지만 견딜 수 있어요."],
            "item_request": ["실례가 되지 않는다면... 아이템을 좀 나눠주실 수 있을까요?", "죄송하지만 도움이 필요해요.", "부탁드려도 될까요?",
                           "폐가 되지 않을까요?", "괜찮으시다면 도와주세요.", "미안하지만 부탁이 있어요.",
                           "죄송한 부탁이지만...", "도움을 청해도 될까요?", "양해 부탁드려요."],
            "praise": ["정말 대단하세요!", "존경스러워요.", "훌륭해요!",
                      "어떻게 그렇게 잘하세요?", "정말 멋있어요.", "배우고 싶어요.",
                      "너무 훌륭해서 감동이에요.", "정말 대단한 분이에요.", "존경의 마음이 들어요."],
            "thanks": ["정말 감사해요.", "친절하게 해주셔서 고마워요.", "마음이 따뜻해져요.",
                      "너무 고마워서 눈물이 나요.", "이런 친절을 어떻게 갚을까요.", "정말 감사한 마음이에요.",
                      "은혜를 평생 잊지 않을게요.", "마음씨가 너무 좋으세요.", "감동받았어요."]
        },
        CharacterPersonality.COLD: {
            "greeting": ["....", "안녕.", "준비됐나.",
                        "시작하자.", "...별말 없다.", "...그렇군.",
                        "뭔가.", "...들어온다.", "...시작할 시간이다."],
            "battle_start": ["끝내자.", "빨리 처리하자.", "...",
                           "간단히 끝내자.", "시간 낭비 말자.", "...끝.",
                           "빠르게.", "...처리.", "조용히 끝내자."],
            "victory": ["당연한 결과다.", "끝.", "다음.",
                       "...예상대로다.", "별거 아니었다.", "...그럴 줄 알았다.",
                       "시간 낭비였다.", "...끝났다.", "당연하다."],
            "low_hp": ["...문제없다.", "괜찮다.", "신경 쓰지 마라.",
                      "...별거 아니다.", "이 정도는...", "...견딜 수 있다.",
                      "문제없다.", "...괜찮다.", "신경 쓸 필요 없다."],
            "item_request": ["아이템.", "회복이 필요하다.", "...도와줘.",
                           "...필요하다.", "줄 수 있나.", "...부탁한다.",
                           "...도움.", "필요.", "...하나."],
            "praise": ["...그럭저럭.", "나쁘지 않다.", "인정한다.",
                      "...할 만하다.", "괜찮다.", "...그렇다.",
                      "인정.", "...나쁘지 않다.", "할 만하다."],
            "thanks": ["...고맙다.", "빚졌다.", "...",
                      "...감사한다.", "기억해두겠다.", "...도움이 됐다.",
                      "고맙다.", "...빚.", "도움."]
        },
        CharacterPersonality.PLAYFUL: {
            "greeting": ["헤이! 오늘은 뭘 할까?", "재밌는 일 없나~?", "심심한데 뭐 좀 터트릴까?",
                        "놀 시간이야!", "뭔가 스릴 있는 거 없을까?", "오늘은 뭔가 특별할 것 같아!",
                        "재밌게 놀아보자!", "심심함을 날려버리자!", "흥미진진한 하루가 될 것 같아!"],
            "battle_start": ["게임 시작! 누가 더 많이 쓰러뜨리나 내기할까?", "재밌겠다!", "신나는데?",
                           "놀이 시간이야!", "게임 같네! 재밌어!", "스릴 넘치는 시간이야!",
                           "누가 더 멋있게 싸우나 보자!", "이런 게 진짜 재밌지!", "게임 시작!"],
            "victory": ["헤헤, 너무 쉬웠나?", "다음엔 더 강한 적이 나왔으면 좋겠어!", "재밌었어!",
                       "너무 쉬워서 아쉬워!", "더 어려운 도전 없을까?", "게임 클리어!",
                       "다음 스테이지는 언제야?", "이 정도로는 만족 안 돼!", "더 재밌는 거 없나?"],
            "low_hp": ["앗, 깜빡했네! 괜찮아, 이것도 스릴 있어!", "이런, 좀 아파!", "힘들긴 하지만... 재밌어!",
                      "하하, 이것도 게임의 일부지!", "스릴 만점이네!", "아직 게임 오버는 아니야!",
                      "이런 상황도 재밌어!", "긴장감 있어서 좋아!", "역전의 기회야!"],
            "item_request": ["아이템 좀 던져줘! 받아서 먹을게!", "나도 좀 줘~", "아이템 나눠먹기 게임?",
                           "나도 파워업하고 싶어!", "아이템 놀이 하자!", "아이템으로 놀아볼까?",
                           "재밌는 아이템 없나?", "뭔가 신기한 거 줘봐!", "아이템 파티 하자!"],
            "praise": ["오오! 멋있어!", "나도 저렇게 해봐야지!", "완전 쩔어!",
                      "와! 대박이야!", "너무 멋져서 놀랐어!", "진짜 게임 같아!",
                      "완전 프로급이네!", "어떻게 그렇게 해?", "신기해! 가르쳐줘!"],
            "thanks": ["고마워! 언젠가 갚을게!", "역시 좋은 친구야!", "이런 친구가 있어서 다행이야!",
                      "너 정말 좋은 사람이야!", "친구 만세!", "이런 재미있는 친구 처음이야!",
                      "같이 놀아줘서 고마워!", "재밌는 친구네!", "또 같이 놀자!"]
        },
        CharacterPersonality.MYSTERIOUS: {
            "greeting": ["...안녕.", "운명이 우리를 다시 만나게 했군.", "...시작하자.",
                        "예정된 만남이었나.", "운명의 실이 얽혔다.", "...흥미로운 조우다.",
                        "운명이 부른다.", "예언된 만남인가.", "...시간이 왔다."],
            "battle_start": ["운명의 수레바퀴가 돌고 있다.", "...각자의 길을 가자.", "어둠이 깊어지고 있다.",
                           "운명이 시험하고 있다.", "예정된 시련이다.", "...운명에 맡기자.",
                           "별들이 속삭인다.", "운명의 순간이다.", "...모든 것이 정해져 있었다."],
            "victory": ["예정된 결과였다.", "운명은 이미 정해져 있었다.", "...그럴 줄 알았다.",
                       "별들이 말했던 대로다.", "운명의 수레바퀴가 돌았다.", "...예언대로다.",
                       "모든 것이 계획 안에 있었다.", "운명을 거스를 수는 없다.", "...당연한 결과다."],
            "low_hp": ["...이것도 운명인가.", "아직... 때가 아니다.", "운명이 날 버리지 않을 것이다.",
                      "...시련의 시간이군.", "운명이 시험하고 있다.", "...아직 끝나지 않았다.",
                      "운명의 실이 끊어지지 않았다.", "...이것도 예정된 일인가.", "별들이 기다리고 있다."],
            "item_request": ["...필요하다.", "운명이 요구하고 있다.", "도움이... 필요하다.",
                           "...운명의 인도다.", "별들이 속삭인다.", "...필연적인 요청이다.",
                           "운명의 선택이다.", "...도움을 구한다.", "운명이 이끄는 대로."],
            "praise": ["흥미롭다.", "예상과 다르군.", "...인정한다.",
                      "운명이 선택한 자로군.", "...특별한 존재다.", "별들도 주목하고 있다.",
                      "예언에 없던 일이다.", "...놀랍다.", "운명을 바꿀 수 있는 자인가."],
            "thanks": ["...기억하겠다.", "빚을 졌다.", "운명이 갚게 될 것이다.",
                      "...은혜를 새기겠다.", "운명의 실이 더욱 얽혔다.", "...감사한다.",
                      "별들이 축복할 것이다.", "운명이 보상할 것이다.", "...잊지 않겠다."]
        },
        CharacterPersonality.HOT_TEMPERED: {
            "greeting": ["뭐야! 늦었잖아!", "빨리 시작하자고!", "답답해 죽겠네!",
                        "언제까지 기다려야 해?", "시간 낭비하지 말자!", "빨리빨리!",
                        "답답하게 뭘 그렇게 생각해!", "시간이 아까워!", "빨리 움직여!"],
            "battle_start": ["이제야! 빨리 덤벼!", "늦었어! 빨리 끝내자!", "답답하게 뭘 그렇게 생각해!",
                           "드디어! 기다렸다고!", "빨리 해치워버리자!", "지겨웠어!",
                           "시원하게 날려버리자!", "답답함을 풀어보자!", "불타오르네!"],
            "victory": ["당연하지! 우리가 누군데!", "이 정도는 식은 죽 먹기야!", "다음 적은 어디 있어?",
                       "너무 쉬웠어! 아쉽다!", "이런 건 워밍업도 안 돼!", "더 강한 놈 없나?",
                       "시원했어! 스트레스 해소!", "이 맛에 싸우는 거지!", "완전 쿨했어!"],
            "low_hp": ["아! 짜증나!", "이런! 방심했네!", "화나는데! 빨리 치료해줘!",
                      "열받아! 이런 실수를!", "속상해 죽겠어!", "짜증나게!",
                      "화날 대로 났어!", "이런 바보 같은!", "빨리 회복하고 복수하자!"],
            "item_request": ["야! 아이템 좀 줘!", "빨리 아이템!", "답답해! 치료 아이템!",
                           "빨리빨리! 아이템!", "지금 당장 필요해!", "서둘러!",
                           "빨리 안 주면 화낼 거야!", "답답하게!", "시급해!"],
            "praise": ["오! 괜찮네!", "처음 본 거치고는 할 만해!", "그래, 그렇게 해야지!",
                      "이제야 좀 볼 만하네!", "그렇지! 이런 게 실력이야!", "드디어 제대로 하는구나!",
                      "시원하게 잘한다!", "이런 식으로 해야지!", "마음에 든다!"],
            "thanks": ["어... 고마워.", "뭐, 나쁘지 않았어.", "다음에도 부탁한다!",
                      "그래, 이런 게 친구지!", "고마워! 빚진 거 알아!", "역시 믿을 만해!",
                      "좋아! 마음에 들어!", "이런 친구 괜찮네!", "고맙다고!"]
        },
        CharacterPersonality.WISE: {
            "greeting": ["안녕하십니다. 오늘도 배울 점이 많을 것 같습니다.", "지혜로운 하루가 되길 바라며.", "평안한 인사를 드립니다.",
                        "오늘도 새로운 깨달음이 있기를.", "지혜를 나누는 시간이 되길.", "평화로운 만남입니다.",
                        "배움의 기회가 되길 바랍니다.", "서로에게 도움이 되는 시간이 되길.", "지혜로운 대화를 나누길 바랍니다."],
            "battle_start": ["신중하게 접근합시다.", "경험이 우리를 이끌 것입니다.", "지혜롭게 행동합시다.",
                           "차분하게 상황을 파악합시다.", "경험을 바탕으로 행동합시다.", "현명한 판단이 필요합니다.",
                           "지혜로운 전략을 세웁시다.", "신중한 접근이 승리를 가져다줍니다.", "경험의 힘을 믿습시다."],
            "victory": ["좋은 교훈을 얻었습니다.", "모두의 노력이 결실을 맺었습니다.", "지혜로운 승리였습니다.",
                       "경험이 빛을 발했습니다.", "현명한 선택이었습니다.", "지혜의 힘을 보았습니다.",
                       "배움이 있는 승리였습니다.", "모두가 성장했습니다.", "좋은 경험이었습니다."],
            "low_hp": ["이것도 하나의 경험이군요.", "때로는 후퇴도 지혜입니다.", "배움의 순간이네요.",
                      "시련을 통해 성장합니다.", "현명한 선택이 필요한 때입니다.", "경험으로 삼겠습니다.",
                      "지혜로운 후퇴를 고려해봅시다.", "이런 순간도 배움입니다.", "현실을 직시해야 합니다."],
            "item_request": ["지혜로운 선택을 부탁드립니다.", "도움이 필요합니다.", "현명한 판단을 구합니다.",
                           "지혜를 나눠주시길.", "경험에서 우러나는 도움을 구합니다.", "현명한 지원을 부탁드립니다.",
                           "지혜로운 협력을 요청합니다.", "함께 나누는 것이 지혜입니다.", "도움을 청합니다."],
            "praise": ["훌륭한 지혜입니다.", "존경스러운 판단이었습니다.", "배울 점이 많습니다.",
                      "지혜로운 행동이었습니다.", "경험에서 우러나는 실력입니다.", "현명한 선택이었습니다.",
                      "깊은 통찰력입니다.", "지혜의 깊이를 봅니다.", "존경할 만한 지혜입니다."],
            "thanks": ["깊이 감사드립니다.", "지혜를 나눠주셔서 고맙습니다.", "은혜를 기억하겠습니다.",
                      "현명한 도움에 감사합니다.", "지혜로운 선택에 감사드립니다.", "깊은 고마움을 표합니다.",
                      "지혜를 함께 나눠주셔서 감사합니다.", "현명한 판단에 감사드립니다.", "은혜로운 도움이었습니다."]
        },
        CharacterPersonality.BALANCED: {
            "greeting": ["안녕하세요.", "좋은 하루네요.", "만나서 반갑습니다.",
                        "오늘도 함께 해봐요.", "잘 부탁드립니다.", "좋은 날씨네요.",
                        "함께 가봅시다.", "준비되셨나요?", "시작해볼까요?"],
            "battle_start": ["신중하게 가보죠.", "서로 도우며 해봐요.", "최선을 다해봅시다.",
                           "각자의 역할을 해봐요.", "협력해서 해결해봅시다.", "차근차근 가봅시다.",
                           "함께 힘내봐요.", "안전하게 처리해봅시다.", "상황을 파악해봅시다."],
            "victory": ["잘 해냈네요.", "좋은 결과입니다.", "모두 수고하셨어요.",
                       "성공적이었어요.", "다행히 잘 끝났어요.", "만족스러운 결과네요.",
                       "팀워크가 좋았어요.", "모두의 노력 덕분이에요.", "다음도 잘 해봅시다."],
            "low_hp": ["조금 힘들지만 괜찮아요.", "치료가 필요할 것 같아요.", "잠시 쉬어야겠어요.",
                      "무리하지 않겠어요.", "상황을 봐가며 하겠어요.", "조심스럽게 행동하겠어요.",
                      "도움이 필요할 것 같아요.", "신중하게 대처하겠어요.", "현실적으로 판단하겠어요."],
            "item_request": ["아이템 좀 나눠줄 수 있을까요?", "도움이 필요해요.", "부탁이 있어요.",
                           "함께 나눠 써요.", "협력이 필요해요.", "지원을 부탁드려요.",
                           "도와주실 수 있나요?", "같이 사용해봐요.", "필요한 게 있어요."],
            "praise": ["잘하시네요.", "훌륭해요.", "좋은 실력이에요.",
                      "대단하세요.", "멋져요.", "인상적이에요.",
                      "실력이 좋으시네요.", "배울 점이 많아요.", "존경스러워요."],
            "thanks": ["고마워요.", "도움이 됐어요.", "감사합니다.",
                      "고맙습니다.", "도와주셔서 감사해요.", "정말 고마워요.",
                      "큰 도움이었어요.", "감사한 마음이에요.", "고마운 분이네요."]
        }
    }
    
    # 직업별 특수 대사 시스템
    CLASS_SPECIFIC_DIALOGUE = {
        "전사": {
            "battle_cry": ["칼날에 맡긴다!", "전사의 명예를 걸고!", "방패와 검으로!"],
            "taunt": ["이 정도로 전사를 쓰러뜨릴 수 있다고?", "아직 힘이 남아있다!", "전사는 쉽게 무너지지 않는다!"],
            "class_skill": ["전사의 힘을 보여주겠다!", "검의 길을 걷는 자의 실력!", "무력으로 돌파한다!"]
        },
        "아크메이지": {
            "spell_cast": ["마력의 진리여!", "고대의 지혜여, 나에게 힘을!", "마법의 깊은 힘을 보라!"],
            "mana_low": ["마력이... 부족하다.", "잠시 마력을 충전해야겠다.", "마나가 고갈되고 있다."],
            "class_skill": ["진정한 마법의 힘을 보여주겠다!", "아크메이지의 지혜로!", "마법의 정수를 다루겠다!"]
        },
        "궁수": {
            "aim": ["정확히 조준한다.", "바람의 흐름을 읽는다.", "화살이 목표를 찾을 것이다."],
            "critical_hit": ["완벽한 명중!", "화살이 급소를 찾았다!", "이것이 궁수의 실력이다!"],
            "class_skill": ["궁수의 정밀함을 보라!", "바람과 하나가 되어!", "화살의 길을 따르라!"]
        },
        "도적": {
            "stealth": ["그림자 속으로...", "조용히... 들키지 말자.", "어둠이 나를 숨겨준다."],
            "backstab": ["뒤에서 실례!", "예상하지 못했지?", "도적의 기술이다!"],
            "class_skill": ["그림자의 기술을 보여주겠다!", "도적의 민첩함으로!", "은밀함이 최고의 무기다!"]
        },
        "성기사": {
            "divine_power": ["신성한 빛이여!", "정의의 이름으로!", "신의 가호가 함께한다!"],
            "heal": ["치유의 빛을 받아라.", "신성한 힘으로 회복하라.", "빛이 상처를 치유한다."],
            "class_skill": ["성기사의 신념으로!", "정의의 힘을 보라!", "신성한 의무를 다하겠다!"]
        },
        "클레릭": {
            "heal": ["신의 은총으로 치유하소서.", "성스러운 빛이 상처를 감싸네.", "치유의 기도를 올립니다."],
            "bless": ["축복이 함께하길.", "신이 보호해주실 것입니다.", "성스러운 가호를 받으소서."],
            "class_skill": ["신의 뜻에 따라!", "성스러운 힘으로!", "믿음의 기적을 보이겠다!"]
        },
        "바드": {
            "song": ["이 노래가 힘이 되길.", "선율에 마음을 맡겨봐.", "음악이 우리를 하나로 만든다."],
            "inspire": ["용기를 북돋아주는 선율!", "희망의 노래를 들려주지.", "리듬에 맞춰 함께하자!"],
            "class_skill": ["바드의 선율로!", "음악의 마법을 느껴봐!", "노래가 기적을 만든다!"]
        },
        "드루이드": {
            "nature": ["자연의 힘을 빌린다.", "대지의 기운이 함께한다.", "숲의 정령들이 도와준다."],
            "transform": ["자연과 하나가 된다.", "야생의 힘을 받아들인다.", "변신의 시간이다!"],
            "class_skill": ["자연의 섭리로!", "대지의 힘을 빌려!", "드루이드의 지혜로!"]
        },
        "네크로맨서": {
            "dark_magic": ["어둠의 힘이여...", "죽음의 마법으로...", "언데드의 힘을 빌린다."],
            "summon": ["죽은 자들이여, 일어나라!", "어둠에서 소환한다.", "언데드 군단이여!"],
            "class_skill": ["죽음의 마법으로!", "어둠의 힘을 보여주겠다!", "네크로맨서의 진정한 힘을!"]
        },
        "사무라이": {
            "honor": ["사무라이의 명예를 걸고!", "무사도정신으로!", "검의 도를 따르겠다!"],
            "katana": ["검이 길을 보여준다.", "일검필살!", "사무라이의 검법이다!"],
            "class_skill": ["사무라이의 혼으로!", "검의 도를 보여주겠다!", "무사의 길을 걷는다!"]
        },
        "몽크": {
            "meditation": ["마음을 비운다.", "내면의 평화를...", "수행의 결과를 보여주겠다."],
            "martial_arts": ["몸과 마음이 하나가 된다.", "무술의 진리를 보라!", "수행한 기술이다!"],
            "class_skill": ["몽크의 수행으로!", "내면의 힘을 끌어낸다!", "무술의 도를 보여주겠다!"]
        },
        "광전사": {
            "rage": ["분노가 치솟는다!", "피가 끓어오른다!", "광기가 힘을 준다!"],
            "berserker": ["모든 것을 파괴하겠다!", "분노의 힘으로!", "광전사의 진노를 보라!"],
            "class_skill": ["광기의 힘으로!", "분노가 나를 지배한다!", "광전사의 진정한 모습을!"]
        }
    }
    
    # 상호 직업별 특수 대사 (캐릭터 간 상호작용)
    INTER_CLASS_DIALOGUE = {
        ("전사", "아크메이지"): {
            "전사": ["마법사님, 제가 앞에서 막을 테니 마법을 써주세요!", "마법의 힘을 믿습니다!", "뒤는 부탁드립니다!"],
            "아크메이지": ["전사여, 방패막이에 감사하다.", "그대의 용기에 마법으로 보답하겠다.", "훌륭한 방어다!"]
        },
        ("궁수", "도적"): {
            "궁수": ["도적님, 저는 원거리에서 지원하겠습니다!", "은밀한 작전, 멋지네요!", "정확한 타이밍이었어요!"],
            "도적": ["궁수의 엄호가 있어 마음 놓고 잠입할 수 있었다.", "화살 실력 대단하네.", "완벽한 협력이었다!"]
        },
        ("성기사", "클레릭"): {
            "성기사": ["클레릭님의 치유에 감사드립니다!", "함께 신의 뜻을 이루어봅시다!", "성스러운 협력이네요!"],
            "클레릭": ["성기사님의 정의로운 마음이 아름답습니다.", "함께 선을 행합시다.", "신이 기뻐하실 겁니다."]
        },
        ("바드", "드루이드"): {
            "바드": ["자연의 선율과 제 음악이 어우러지네요!", "드루이드님의 자연 친화력이 부럽습니다!", "함께 연주해봐요!"],
            "드루이드": ["바드의 노래가 자연과 조화를 이룬다.", "음악도 자연의 일부군.", "아름다운 선율이다."]
        },
        ("네크로맨서", "성기사"): {
            "네크로맨서": ["성기사여... 우리는 다른 길을 걷지만.", "빛과 어둠의 협력이라니.", "흥미로운 조합이군."],
            "성기사": ["어둠의 힘이지만... 같은 편이니까.", "정의를 위해서라면 함께 할 수 있습니다.", "복잡한 심정이지만..."]
        },
        ("사무라이", "몽크"): {
            "사무라이": ["몽크님의 수행정신을 존경합니다!", "무술의 도에서는 같은 길을 걷는군요!", "수행자의 마음가짐이 훌륭합니다!"],
            "몽크": ["사무라이의 검의 도, 깊이 느껴집니다.", "무사도정신과 수행정신, 통하는 바가 있네요.", "서로 배울 점이 많습니다."]
        },
        ("광전사", "바드"): {
            "광전사": ["바드의 노래가... 마음을 진정시켜주는군.", "음악이 분노를 달래준다.", "고마운 선율이다."],
            "바드": ["광전사님의 열정적인 모습에서 영감을 받았어요!", "그 에너지를 노래로 표현해보겠어요!", "역동적인 리듬이 떠오르네요!"]
        }
    }
    
    # 필드 사담 (길가다가 하는 대화)
    FIELD_CASUAL_DIALOGUE = {
        CharacterPersonality.CHEERFUL: [
            "와, 오늘 날씨 정말 좋다!", "저기 예쁜 꽃이 피었네!", "모험하기 딱 좋은 날씨야!",
            "구름이 정말 예쁘게 생겼어!", "바람이 시원해서 기분 좋아!", "새소리가 정말 아름다워!",
            "이런 평화로운 순간이 좋아!", "모두와 함께 걷는 게 즐거워!", "오늘은 뭔가 좋은 일이 생길 것 같아!",
            "저 나무 그늘에서 잠깐 쉬어갈까?", "길가의 풍경이 정말 아름다워!", "함께 여행하니까 더 재밌어!"
        ],
        CharacterPersonality.SERIOUS: [
            "길이 험하다. 조심하자.", "주변을 경계해야 한다.", "목적지까지 얼마나 남았을까.",
            "체력 관리에 신경써야겠다.", "이 길이 맞는 건가?", "효율적인 루트를 찾아보자.",
            "시간을 낭비하지 말자.", "계획대로 진행하고 있다.", "다음 목표를 확인해보자.",
            "준비물을 점검해보자.", "안전한 루트를 선택하자.", "신중하게 행동하자."
        ],
        CharacterPersonality.GENTLE: [
            "모두 피곤하지 않으세요?", "천천히 가도 괜찮아요.", "무리하지 마세요.",
            "잠깐 쉬어가도 될까요?", "길이 힘들어 보이는데 괜찮으세요?", "서로 도와가며 가요.",
            "예쁜 풍경이네요.", "평화로운 길이어서 다행이에요.", "모두 건강하게 도착하길 바라요.",
            "조심해서 가요.", "서로 걱정해주며 가면 좋겠어요.", "안전이 최우선이에요."
        ],
        CharacterPersonality.COLD: [
            "...", "빨리 가자.", "시간 낭비다.",
            "...별말 없다.", "조용히 가자.", "...그냥 가자.",
            "멈추지 말자.", "...계속.", "말할 게 없다.",
            "...앞으로.", "조용한 게 좋다.", "...그냥."
        ],
        CharacterPersonality.PLAYFUL: [
            "심심하다~ 뭔가 재밌는 거 없을까?", "저기 돌멩이로 게임할까?", "누가 더 빨리 걸을 수 있나 경주해볼까?",
            "구름 모양 맞추기 게임 어때?", "길가의 꽃 개수 세어볼까?", "발걸음 리듬 맞춰서 가보자!",
            "재밌는 이야기 없나?", "길에서 뭔가 특별한 거 발견할 수 있을까?", "모험 같아서 재밌어!",
            "저 나무에 올라가볼까?", "길 옆에 뭐가 있나 살펴보자!", "재밌게 걸어가자!"
        ],
        CharacterPersonality.MYSTERIOUS: [
            "운명이 우리를 이끌고 있다.", "이 길의 끝에 무엇이 기다리고 있을까.", "별들이 속삭이고 있다.",
            "예정된 길을 걷고 있다.", "운명의 실이 우리를 인도한다.", "모든 것이 계획 안에 있다.",
            "어둠이 깊어지고 있다.", "운명의 수레바퀴가 돌고 있다.", "예언의 시간이 다가온다.",
            "숨겨진 진실이 드러날 것이다.", "운명을 거스를 수는 없다.", "모든 것이 연결되어 있다."
        ],
        CharacterPersonality.HOT_TEMPERED: [
            "언제까지 걸어야 해?", "답답하게 느려!", "빨리 좀 가자!", 
            "시간이 아까워!", "이렇게 천천히 가면 언제 도착해?", "답답해 죽겠네!",
            "더 빨리 갈 수 없나?", "지루해서 못 견디겠어!", "빨리빨리!",
            "시간 낭비하지 말자!", "답답한 속도네!", "좀 더 활기차게 가자!"
        ],
        CharacterPersonality.WISE: [
            "이 길에서도 배울 점이 있군요.", "여행 자체가 하나의 수행입니다.", "길에서의 경험도 소중합니다.",
            "자연에서 지혜를 얻을 수 있습니다.", "걸으며 생각할 시간이 있어 좋습니다.", "여행이 마음을 넓혀줍니다.",
            "길동무와의 대화에서 깨달음을 얻습니다.", "세상을 보는 눈이 넓어집니다.", "경험이 지혜가 됩니다.",
            "자연의 섭리를 느낄 수 있습니다.", "길 위의 모든 것이 스승입니다.", "여행을 통해 성장합니다."
        ],
        CharacterPersonality.BALANCED: [
            "날씨가 좋네요.", "길이 평탄해서 다행이에요.", "함께 가니까 든든해요.",
            "풍경이 아름다워요.", "적당히 쉬어가면서 해요.", "모두 건강하게 가봐요.",
            "목적지까지 얼마나 남았을까요?", "차근차근 가봅시다.", "서로 도우며 가요.",
            "좋은 여행이 되고 있어요.", "평화로운 길이네요.", "함께해서 즐거워요."
        ]
    }
    
    # 파티원 전용 인카운터 대사
    PARTY_ENCOUNTER_DIALOGUE = {
        "treasure_found": {
            CharacterPersonality.CHEERFUL: ["와! 보물이다! 우리 운이 정말 좋네!", "대박! 이거 나눠가지자!", "보물 발견! 신나는데?"],
            CharacterPersonality.SERIOUS: ["보물을 발견했다. 공평하게 나누자.", "가치를 평가해보자.", "신중하게 분배하자."],
            CharacterPersonality.GENTLE: ["보물이에요! 모두 함께 나눠요.", "다들 기쁘셨으면 좋겠어요.", "운이 좋았네요."],
            CharacterPersonality.COLD: ["보물이다. 나누자.", "...쓸만하다.", "가져가자."],
            CharacterPersonality.PLAYFUL: ["오! 보물찾기 성공!", "재밌는 발견이네!", "보물 파티다!"],
            CharacterPersonality.MYSTERIOUS: ["운명이 우리에게 선물을 주었군.", "예정된 보상이다.", "별들의 축복인가."],
            CharacterPersonality.HOT_TEMPERED: ["드디어! 기다린 보람이 있네!", "이런 게 있어야지!", "빨리 나눠가자!"],
            CharacterPersonality.WISE: ["좋은 발견입니다. 지혜롭게 사용합시다.", "보물보다 경험이 더 소중합니다.", "나눔의 지혜를 보입시다."],
            CharacterPersonality.BALANCED: ["보물을 발견했어요!", "모두 함께 나눠요.", "좋은 발견이네요."]
        },
        "enemy_spotted": {
            CharacterPersonality.CHEERFUL: ["적이다! 하지만 우리가 이길 거야!", "전투 준비! 모두 파이팅!", "같이 힘내자!"],
            CharacterPersonality.SERIOUS: ["적을 발견했다. 전투 준비.", "계획대로 움직이자.", "각자의 역할을 기억하자."],
            CharacterPersonality.GENTLE: ["조심하세요. 다치지 마세요.", "안전하게 처리해요.", "서로 지켜주면서 해요."],
            CharacterPersonality.COLD: ["적이다. 처리하자.", "빠르게 끝내자.", "...시작하자."],
            CharacterPersonality.PLAYFUL: ["게임 시작! 누가 더 잘하나 보자!", "재밌겠다!", "스릴 있는 전투네!"],
            CharacterPersonality.MYSTERIOUS: ["운명이 시험하고 있다.", "예정된 시련이군.", "운명의 순간이다."],
            CharacterPersonality.HOT_TEMPERED: ["드디어! 기다렸어!", "시원하게 해치워버리자!", "불타오르네!"],
            CharacterPersonality.WISE: ["신중하게 접근합시다.", "경험을 살려 행동합시다.", "지혜롭게 대처합시다."],
            CharacterPersonality.BALANCED: ["적을 발견했어요.", "조심해서 처리해봅시다.", "함께 대응해요."],
            CharacterPersonality.MYSTERIOUS: ["운명이 시험하고 있다.", "예정된 시련이군.", "운명의 순간이다."],
            CharacterPersonality.HOT_TEMPERED: ["드디어! 기다렸어!", "시원하게 해치워버리자!", "불타오르네!"],
            CharacterPersonality.WISE: ["신중하게 접근합시다.", "경험을 살려 행동합시다.", "지혜롭게 대처합시다."]
        },
        "rest_time": {
            CharacterPersonality.CHEERFUL: ["휴식 시간이다! 다들 수고했어!", "잠깐 쉬면서 이야기하자!", "기분 전환하자!"],
            CharacterPersonality.SERIOUS: ["적당한 휴식이 필요하다.", "체력을 회복하자.", "다음을 준비하자."],
            CharacterPersonality.GENTLE: ["모두 피곤하셨죠? 푹 쉬세요.", "편히 쉬셨으면 좋겠어요.", "무리하지 마세요."],
            CharacterPersonality.COLD: ["쉬자.", "...휴식.", "잠깐 멈추자."],
            CharacterPersonality.PLAYFUL: ["휴식 타임! 뭔가 재밌는 거 하자!", "심심한데 게임할까?", "재밌게 쉬어보자!"],
            CharacterPersonality.MYSTERIOUS: ["휴식도 운명의 일부다.", "시간의 흐름을 느끼자.", "잠시 성찰의 시간을."],
            CharacterPersonality.HOT_TEMPERED: ["드디어 쉴 수 있네!", "빨리 회복하고 계속 가자!", "쉬는 것도 좋지만..."],
            CharacterPersonality.WISE: ["휴식을 통해 재충전합시다.", "지친 몸과 마음을 달래요.", "휴식도 지혜의 일부입니다."],
            CharacterPersonality.BALANCED: ["적당히 쉬어가면서 해요.", "모두 수고하셨어요.", "잠깐 쉬었다 가봅시다."]
        }
    }
    
    # 상호 직업별 특수 대사 시스템
    INTER_CLASS_DIALOGUE = {
        ("전사", "아크메이지"): {
            "cooperation": ["마법사여, 내가 길을 열어주겠다!", "마법의 지원이 필요하다.", "검과 마법의 조합이다!"],
            "complement": ["네 마법이 없었다면 힘들었을 것이다.", "마법사의 지혜에 감사한다.", "좋은 콤비네이션이다."]
        },
        ("궁수", "전사"): {
            "cooperation": ["전사가 앞장서주면 내가 뒤에서 지원하겠다!", "근접 전투는 맡겨라.", "원거리에서 엄호하겠다!"],
            "complement": ["전사의 용맹함 덕분이다.", "앞장서 줘서 고맙다.", "든든한 방패 역할이었다."]
        },
        ("성기사", "암흑기사"): {
            "conflict": ["어둠의 기사여... 경계하겠다.", "빛과 어둠이 만났군.", "서로 다른 길이지만..."],
            "respect": ["어둠의 힘이지만... 인정한다.", "다른 길이지만 실력은 확실하다.", "빛과 어둠, 모두 필요한 힘이다."]
        },
        ("바드", "모든직업"): {
            "encourage": ["모두 힘내요! 제 노래가 힘이 될 거예요!", "음악으로 여러분을 응원하겠습니다!", "선율에 맞춰 함께 싸워요!"],
            "support": ["제가 뒤에서 지원하겠습니다!", "노래로 마음을 치유해드릴게요.", "음악의 힘을 믿어주세요!"]
        },
        ("드루이드", "정령술사"): {
            "nature_bond": ["자연을 사랑하는 동지여!", "자연의 힘을 함께 나누자.", "대지가 우리를 축복하고 있다."],
            "synergy": ["자연의 조화가 완벽하다.", "정령과 자연이 하나가 되었다.", "이것이 진정한 자연의 힘이다!"]
        }
    }

    
    @staticmethod
    def get_gender_from_name(name: str) -> CharacterGender:
        """이름으로 성별 판단"""
        if name in CharacterTraits.MALE_NAMES:
            return CharacterGender.MALE
        elif name in CharacterTraits.FEMALE_NAMES:
            return CharacterGender.FEMALE
        else:
            # 기본값: 랜덤
            return random.choice([CharacterGender.MALE, CharacterGender.FEMALE])
    
    @staticmethod
    def get_random_personality() -> CharacterPersonality:
        """랜덤 성격 반환"""
        return random.choice(list(CharacterPersonality))
    
    @staticmethod
    def get_dialogue(personality: CharacterPersonality, situation: str) -> str:
        """성격에 따른 대화 반환"""
        dialogues = CharacterTraits.PERSONALITY_DIALOGUE.get(personality, {})
        situation_dialogues = dialogues.get(situation, ["..."])
        return random.choice(situation_dialogues)

class AIGameMode(Enum):
    """AI 게임모드 타입"""
    SINGLE_CONTROL = "single_control"       # 1명만 조작, 나머지 AI
    DUAL_CONTROL = "dual_control"           # 2명 조작, 나머지 AI
    MIXED_CONTROL = "mixed_control"         # 혼합 모드 (상황에 따라 변경)
    FULL_AI_SUPPORT = "full_ai_support"     # 모든 AI, 플레이어는 전략 지시만

class AIGameModeManager:
    """AI 게임모드 관리자"""
    
    def __init__(self):
        self.current_mode = AIGameMode.SINGLE_CONTROL
        self.player_controlled_characters = []  # 플레이어가 조작하는 캐릭터들
        self.ai_companions = []                 # AI가 조작하는 동료들
        self.pending_ai_requests = []           # AI의 요청/제안 목록
        self.coordination_opportunities = []    # 협동 공격 기회
        self.item_sharing_enabled = True       # 아이템 공유 허용
        
    def initialize_ai_mode(self, party_members: List[Character], controlled_count: int = 1):
        """AI 모드 초기화"""
        if controlled_count >= len(party_members):
            print("⚠️ 모든 캐릭터를 직접 조작합니다.")
            self.player_controlled_characters = party_members[:]
            self.ai_companions = []
            return
        
        # 플레이어가 조작할 캐릭터 선택
        # 개선된 캐릭터 선택 시스템 사용
        from .ai_character_selector import select_player_characters_with_cursor_menu
        self.player_controlled_characters = select_player_characters_with_cursor_menu(party_members, controlled_count)
        
        # 나머지는 AI 동료로 설정
        ai_characters = [char for char in party_members if char not in self.player_controlled_characters]
        self.ai_companions = []
        
        for char in ai_characters:
            personality = self._assign_personality_to_character(char)
            ai_companion = AICompanion(char, personality)
            self.ai_companions.append(ai_companion)
            print(f"🤖 {char.name}을(를) AI가 조작합니다 (성격: {personality.value})")
        
        print(f"\n✅ AI 게임모드 활성화!")
        print(f"   플레이어 조작: {len(self.player_controlled_characters)}명")
        print(f"   AI 조작: {len(self.ai_companions)}명")
    
    def _select_player_characters(self, party_members: List[Character], count: int) -> List[Character]:
        """플레이어가 조작할 캐릭터 선택 - 강제 실행 보장"""
        print(f"\n🎮 직접 조작할 캐릭터를 {count}명 선택해주세요!")
        print("="*60)
        
        # 간단한 텍스트 기반 선택으로 강제 실행
        selected = []
        remaining_members = list(party_members)
        
        while len(selected) < count and remaining_members:
            print(f"\n� 선택 가능한 캐릭터 목록 ({len(selected)+1}/{count}):")
            print("-"*40)
            
            for i, char in enumerate(remaining_members, 1):
                hp_ratio = int((char.current_hp / char.max_hp) * 100) if char.max_hp > 0 else 0
                mp_ratio = int((char.current_mp / char.max_mp) * 100) if char.max_mp > 0 else 0
                print(f"{i}. {char.name} (Lv.{char.level}, {char.character_class})")
                print(f"   HP: {hp_ratio}% | MP: {mp_ratio}% | 공격: {char.attack} | 방어: {char.defense}")
            
            print(f"\n� 힌트: 다양한 역할의 캐릭터를 선택하면 더 유리합니다!")
            
            try:
                choice_input = input(f"캐릭터 번호를 입력하세요 (1-{len(remaining_members)}): ").strip()
                
                if not choice_input:
                    print("❌ 번호를 입력해주세요.")
                    continue
                
                choice_idx = int(choice_input) - 1
                
                if 0 <= choice_idx < len(remaining_members):
                    selected_char = remaining_members[choice_idx]
                    selected.append(selected_char)
                    remaining_members.remove(selected_char)
                    print(f"✅ {selected_char.name}을(를) 선택했습니다!")
                    
                    if len(selected) < count:
                        input("다음 캐릭터를 선택하려면 Enter를 누르세요...")
                else:
                    print(f"❌ 1부터 {len(remaining_members)} 사이의 번호를 입력해주세요.")
                    
            except ValueError:
                print("❌ 유효한 숫자를 입력해주세요.")
            except KeyboardInterrupt:
                print("\n⚠️ 선택을 취소할 수 없습니다. 캐릭터를 선택해주세요.")
        
        # 선택이 부족한 경우 자동으로 첫 번째 캐릭터들 선택
        while len(selected) < count and party_members:
            for char in party_members:
                if char not in selected:
                    selected.append(char)
                    print(f"🤖 {char.name}이(가) 자동으로 선택되었습니다.")
                    break
            if len(selected) >= count:
                break
        
        print(f"\n🎉 선택 완료! 플레이어가 조작할 캐릭터:")
        for i, char in enumerate(selected, 1):
            print(f"  {i}. {char.name} ({char.character_class})")
        
        input("계속하려면 Enter를 누르세요...")
        return selected
    
    def _assign_personality_to_character(self, character: Character) -> AIPersonality:
        """실제 게임 직업 시스템에 따른 성격 할당 (28개 직업)"""
        class_personalities = {
            # 물리 근접 계열
            "전사": [AIPersonality.AGGRESSIVE, AIPersonality.DEFENSIVE],
            "기사": [AIPersonality.DEFENSIVE, AIPersonality.SUPPORTIVE],
            "성기사": [AIPersonality.SUPPORTIVE, AIPersonality.DEFENSIVE],
            "암흑기사": [AIPersonality.AGGRESSIVE, AIPersonality.TACTICAL],
            "용기사": [AIPersonality.AGGRESSIVE, AIPersonality.BALANCED],
            "검성": [AIPersonality.AGGRESSIVE, AIPersonality.TACTICAL],
            "사무라이": [AIPersonality.AGGRESSIVE, AIPersonality.BALANCED],
            "검투사": [AIPersonality.AGGRESSIVE, AIPersonality.DEFENSIVE],
            "광전사": [AIPersonality.AGGRESSIVE, AIPersonality.AGGRESSIVE],
            "몽크": [AIPersonality.BALANCED, AIPersonality.TACTICAL],
            
            # 원거리 물리 계열
            "궁수": [AIPersonality.TACTICAL, AIPersonality.BALANCED],
            "도적": [AIPersonality.AGGRESSIVE, AIPersonality.TACTICAL],
            "암살자": [AIPersonality.AGGRESSIVE, AIPersonality.TACTICAL],
            "해적": [AIPersonality.AGGRESSIVE, AIPersonality.BALANCED],
            
            # 마법 계열
            "아크메이지": [AIPersonality.TACTICAL, AIPersonality.SUPPORTIVE],
            "네크로맨서": [AIPersonality.TACTICAL, AIPersonality.AGGRESSIVE],
            "정령술사": [AIPersonality.TACTICAL, AIPersonality.SUPPORTIVE],
            "시간술사": [AIPersonality.TACTICAL, AIPersonality.SUPPORTIVE],
            "차원술사": [AIPersonality.TACTICAL, AIPersonality.AGGRESSIVE],
            "연금술사": [AIPersonality.SUPPORTIVE, AIPersonality.BALANCED],
            "마검사": [AIPersonality.BALANCED, AIPersonality.AGGRESSIVE],
            "기계공학자": [AIPersonality.TACTICAL, AIPersonality.BALANCED],
            
            # 지원 계열
            "바드": [AIPersonality.SUPPORTIVE, AIPersonality.BALANCED],
            "신관": [AIPersonality.SUPPORTIVE, AIPersonality.DEFENSIVE],
            "드루이드": [AIPersonality.BALANCED, AIPersonality.SUPPORTIVE],
            "무당": [AIPersonality.SUPPORTIVE, AIPersonality.TACTICAL],
            
            # 특수 계열
            "철학자": [AIPersonality.SUPPORTIVE, AIPersonality.TACTICAL]
        }
        
        character_class = getattr(character, 'character_class', '전사')
        possible_personalities = class_personalities.get(character_class, [AIPersonality.BALANCED])
        return random.choice(possible_personalities)
    
    def process_combat_turn(self, character: Character, party: List[Character], enemies: List[Character]):
        """전투 턴 처리 (AI/플레이어 구분)"""
        if character in self.player_controlled_characters:
            # 플레이어가 직접 조작
            return self._process_player_turn(character, party, enemies)
        else:
            # AI가 자동 조작
            return self._process_ai_turn(character, party, enemies)
    
    def _process_player_turn(self, character: Character, party: List[Character], enemies: List[Character]):
        """플레이어 턴 처리"""
        print(f"\n🎮 {character.name}의 턴 (플레이어 조작)")
        
        # AI 요청 확인
        self._check_ai_requests()
        
        # 협동 공격 기회 확인
        coord_opportunities = self._check_coordination_opportunities(character, party, enemies)
        
        # 기본 행동 옵션들
        actions = [
            "⚔️ 공격",
            "✨ 스킬 사용", 
            "🧪 아이템 사용",
            "🛡️ 방어",
            "🎒 장비 관리",
            "🍳 요리 사용",
            "🌟 필드스킬 사용",
            "💾 전투 중 저장",
            "📊 상태 확인"
        ]
        
        # 협동 공격이 가능하면 추가
        if coord_opportunities:
            actions.append("🤝 협동 공격")
        
        # AI 요청이 있으면 추가
        if self.pending_ai_requests:
            actions.append("💬 AI 요청 확인")
        
        print("\n행동 선택:")
        for i, action in enumerate(actions, 1):
            print(f"{i}. {action}")
        
        try:
            choice = int(input("선택: ")) - 1
            if 0 <= choice < len(actions):
                action = actions[choice]
                return self._execute_player_action(character, action, party, enemies)
            else:
                print("❌ 잘못된 선택입니다.")
                return self._process_player_turn(character, party, enemies)
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return self._process_player_turn(character, party, enemies)
    
    def _process_ai_turn(self, character: Character, party: List[Character], enemies: List[Character]):
        """AI 턴 처리"""
        # 해당 캐릭터의 AI 동료 찾기
        ai_companion = next((ai for ai in self.ai_companions if ai.character == character), None)
        if not ai_companion:
            return "defend", {}  # 기본 방어
        
        print(f"\n🤖 {character.name}의 턴 (AI 조작)")
        
        # AI 행동 결정
        action_type, action_data = ai_companion.decide_action(party, enemies)
        
        if action_type == "request":
            # AI가 플레이어에게 요청
            request_type = action_data["type"]
            message = ai_companion.make_request_to_player(request_type)
            self.pending_ai_requests.append({
                "companion": ai_companion,
                "type": request_type,
                "message": message,
                "timestamp": time.time()
            })
            print(f"💬 {message}")
            
            # 요청 후 기본 행동 수행
            return "defend", {}
        
        # AI 행동 실행
        print(f"   💭 AI 판단: {self._get_action_description(action_type, action_data)}")
        return action_type, action_data
    
    def _check_ai_requests(self):
        """AI 요청 확인 및 표시"""
        if not self.pending_ai_requests:
            return
        
        print(f"\n💬 AI 동료들의 요청이 {len(self.pending_ai_requests)}개 있습니다:")
        for i, request in enumerate(self.pending_ai_requests):
            print(f"   {i+1}. {request['message']}")
    
    def _check_coordination_opportunities(self, character: Character, party: List[Character], enemies: List[Character]) -> List[Dict]:
        """협동 공격 기회 확인"""
        opportunities = []
        
        for ai_companion in self.ai_companions:
            if not ai_companion.character.is_alive:
                continue
            
            # AI가 협동 공격을 준비 중인지 확인
            if ai_companion.coordinated_attack_ready:
                opportunities.append({
                    "partner": ai_companion.character,
                    "type": "coordinated_attack",
                    "description": f"{ai_companion.character.name}과(와) 협동 공격 가능"
                })
        
        return opportunities
    
    def _execute_player_action(self, character: Character, action: str, party: List[Character], enemies: List[Character]):
        """플레이어 행동 실행"""
        if action == "🤝 협동 공격":
            return self._execute_coordination_attack(character, party, enemies)
        elif action == "💬 AI 요청 확인":
            return self._handle_ai_requests()
        elif action == "⚔️ 공격":
            return "attack", {}
        elif action == "✨ 스킬 사용":
            return self._select_and_use_skill(character, party, enemies)
        elif action == "🧪 아이템 사용":
            return self._select_and_use_item(character, party)
        elif action == "🛡️ 방어":
            return "defend", {}
        elif action == "📊 상태 확인":
            self._show_party_status(party)
            return self._process_player_turn(character, party, enemies)
        else:
            return "defend", {}
    
    def _select_and_use_skill(self, character: Character, party: List[Character], enemies: List[Character]):
        """스킬 선택 및 사용"""
        from .skill_system import skill_system
        character_class = getattr(character, 'character_class', '전사')
        skills = skill_system.get_skills(character_class)
        
        if not skills:
            print(f"❌ {character.name}은(는) 사용할 수 있는 스킬이 없습니다.")
            return "defend", {}
        
        # 사용 가능한 스킬 필터링 (MP 충분한 것만)
        usable_skills = [skill for skill in skills if skill.get("mp_cost", 0) <= character.current_mp]
        
        if not usable_skills:
            print(f"❌ MP가 부족하여 사용할 수 있는 스킬이 없습니다.")
            return "defend", {}
        
        print(f"\n✨ {character.name}의 스킬 목록 (MP: {character.current_mp}/{character.max_mp}):")
        for i, skill in enumerate(usable_skills, 1):
            mp_cost = skill.get("mp_cost", 0)
            skill_name = skill.get("name", "알 수 없는 스킬")
            skill_desc = skill.get("description", "설명 없음")
            print(f"{i}. {skill_name} (MP {mp_cost}) - {skill_desc}")
        
        try:
            choice = int(input("사용할 스킬 선택 (0: 취소): ")) - 1
            if choice == -1:
                return self._process_player_turn(character, party, enemies)
            elif 0 <= choice < len(usable_skills):
                selected_skill = usable_skills[choice]
                
                # 대상 선택
                target = self._select_skill_target(selected_skill, character, party, enemies)
                if target:
                    return "skill", {
                        "skill": selected_skill,
                        "target": target,
                        "mp_cost": selected_skill.get("mp_cost", 0)
                    }
                else:
                    return self._process_player_turn(character, party, enemies)
            else:
                print("❌ 잘못된 선택입니다.")
                return self._process_player_turn(character, party, enemies)
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return self._process_player_turn(character, party, enemies)
    
    def _select_and_use_item(self, character: Character, party: List[Character]):
        """아이템 선택 및 사용"""
        if not hasattr(character, 'inventory') or not character.inventory:
            print(f"❌ {character.name}은(는) 사용할 수 있는 아이템이 없습니다.")
            return "defend", {}
        
        # 사용 가능한 아이템 목록
        consumable_items = []
        for item_name, quantity in character.inventory.get_items_list():
            if quantity > 0:
                # 소모품인지 확인
                from .items import ItemDatabase, ItemType
                item_db = ItemDatabase()
                item = item_db.get_item(item_name)
                if item and item.item_type == ItemType.CONSUMABLE:
                    consumable_items.append((item, quantity))
        
        if not consumable_items:
            print(f"❌ {character.name}은(는) 사용할 수 있는 소모품이 없습니다.")
            return "defend", {}
        
        print(f"\n🧪 {character.name}의 아이템 목록:")
        for i, (item, quantity) in enumerate(consumable_items, 1):
            print(f"{i}. {item.name} x{quantity} - {item.description}")
        
        try:
            choice = int(input("사용할 아이템 선택 (0: 취소): ")) - 1
            if choice == -1:
                return self._process_player_turn(character, party, [])
            elif 0 <= choice < len(consumable_items):
                selected_item, _ = consumable_items[choice]
                
                # 대상 선택
                target = self._select_item_target(selected_item, character, party)
                if target:
                    return "use_item", {
                        "item": selected_item,
                        "target": target
                    }
                else:
                    return self._process_player_turn(character, party, [])
            else:
                print("❌ 잘못된 선택입니다.")
                return self._process_player_turn(character, party, [])
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return self._process_player_turn(character, party, [])
    
    def _select_skill_target(self, skill, caster, party: List[Character], enemies: List[Character]):
        """스킬 대상 선택"""
        skill_type = skill.get("type", "BRV_ATTACK")
        
        if skill_type in ["BRV_ATTACK", "HP_ATTACK", "BRV_HP_ATTACK"]:
            # 적 대상 스킬
            alive_enemies = [e for e in enemies if e.is_alive]
            if not alive_enemies:
                print("❌ 공격할 대상이 없습니다.")
                return None
                
            if len(alive_enemies) == 1:
                return alive_enemies[0]
            
            print("\n🎯 공격 대상 선택:")
            for i, enemy in enumerate(alive_enemies, 1):
                print(f"{i}. {enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp})")
            
            try:
                choice = int(input("대상 선택: ")) - 1
                if 0 <= choice < len(alive_enemies):
                    return alive_enemies[choice]
                else:
                    print("❌ 잘못된 선택입니다.")
                    return None
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return None
                
        else:
            # 아군 대상 스킬 (힐링, 버프 등)
            alive_allies = [ally for ally in party if ally.is_alive]
            if not alive_allies:
                return None
                
            if len(alive_allies) == 1:
                return alive_allies[0]
            
            print("\n💚 대상 선택:")
            for i, ally in enumerate(alive_allies, 1):
                print(f"{i}. {ally.name} (HP: {ally.current_hp}/{ally.max_hp})")
            
            try:
                choice = int(input("대상 선택: ")) - 1
                if 0 <= choice < len(alive_allies):
                    return alive_allies[choice]
                else:
                    print("❌ 잘못된 선택입니다.")
                    return None
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return None
    
    def _select_item_target(self, item, user, party: List[Character]):
        """아이템 대상 선택"""
        # 대부분의 소모품은 아군 대상
        alive_allies = [ally for ally in party if ally.is_alive]
        if not alive_allies:
            return None
            
        if len(alive_allies) == 1:
            return alive_allies[0]
        
        print(f"\n🎯 {item.name} 사용 대상 선택:")
        for i, ally in enumerate(alive_allies, 1):
            print(f"{i}. {ally.name} (HP: {ally.current_hp}/{ally.max_hp}, MP: {ally.current_mp}/{ally.max_mp})")
        
        try:
            choice = int(input("대상 선택: ")) - 1
            if 0 <= choice < len(alive_allies):
                return alive_allies[choice]
            else:
                print("❌ 잘못된 선택입니다.")
                return None
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return None
    
    def _execute_coordination_attack(self, character: Character, party: List[Character], enemies: List[Character]):
        """협동 공격 실행"""
        ready_partners = [ai for ai in self.ai_companions 
                         if ai.coordinated_attack_ready and ai.character.is_alive]
        
        if not ready_partners:
            print("❌ 협동 공격할 동료가 없습니다.")
            return "attack", {}
        
        # 파트너 선택
        if len(ready_partners) == 1:
            partner = ready_partners[0]
        else:
            print("협동 공격 파트너 선택:")
            for i, ai in enumerate(ready_partners, 1):
                print(f"{i}. {ai.character.name}")
            
            try:
                choice = int(input("선택: ")) - 1
                if 0 <= choice < len(ready_partners):
                    partner = ready_partners[choice]
                else:
                    print("❌ 잘못된 선택입니다.")
                    return "attack", {}
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return "attack", {}
        
        # 협동 공격 개시 대사 (성격별)
        character_personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
        partner_personality = getattr(partner.character, 'personality', CharacterPersonality.BALANCED)
        
        # 협동공격 시작 대사 (성격별 대폭 확장)
        coordination_start_dialogues = {
            CharacterPersonality.CHEERFUL: [
                f"{partner.character.name}! 같이 힘내자!", 
                f"우리 호흡 맞춰서 가보자!", 
                f"{partner.character.name}과 함께라면 무섭지 않아!",
                f"야호! {partner.character.name}과 콤보 시간이야!",
                f"우리 둘이면 뭐든 할 수 있어!",
                f"{partner.character.name}, 신나는 협동 공격 해보자!",
                f"함께라면 더 강해져!",
                f"우리의 파워를 합쳐보자!",
                f"{partner.character.name}! 완벽한 팀워크를 보여줘!",
                f"둘이 힘을 합치면 최강이야!"
            ],
            CharacterPersonality.SERIOUS: [
                f"{partner.character.name}, 계획대로 움직이자.", 
                f"협동 공격 개시한다.", 
                f"{partner.character.name}, 신호에 맞춰서.",
                f"전술적 협력을 시작한다.",
                f"{partner.character.name}, 정확한 타이밍으로.",
                f"계산된 협동 공격이다.",
                f"효율적인 협력이 필요하다.",
                f"{partner.character.name}, 프로페셔널하게 가자.",
                f"완벽한 실행을 위해 협력하자.",
                f"전략적 파트너십을 발휘하자."
            ],
            CharacterPersonality.GENTLE: [
                f"{partner.character.name}님, 함께해요.", 
                f"서로 도우며 가요.", 
                f"{partner.character.name}님과 함께라면 안심이에요.",
                f"조심스럽게 함께 해봐요.",
                f"{partner.character.name}님, 무리하지 마세요.",
                f"서로 지켜주면서 해요.",
                f"안전하게 협력해봐요.",
                f"{partner.character.name}님의 도움이 필요해요.",
                f"함께하면 더 안전할 거예요.",
                f"서로를 믿고 가봐요."
            ],
            CharacterPersonality.COLD: [
                f"{partner.character.name}... 따라와.", 
                f"협동 공격.", 
                f"...시작하자.",
                f"{partner.character.name}... 필요하다.",
                f"...함께.",
                f"효율적이다.",
                f"{partner.character.name}... 움직여.",
                f"...협력.",
                f"시간이다.",
                f"...가자."
            ],
            CharacterPersonality.PLAYFUL: [
                f"{partner.character.name}! 재밌는 콤보 보여주자!", 
                f"협동 공격 게임 시작!", 
                f"우리 합동 공연 어때?",
                f"재밌는 놀이 시간이야!",
                f"{partner.character.name}과 함께하는 스펙터클!",
                f"둘이서 멋진 쇼를 해보자!",
                f"완전 쿨한 협동 공격!",
                f"게임처럼 재밌게 해보자!",
                f"{partner.character.name}! 우리만의 필살기!",
                f"신나는 콤보 플레이!"
            ],
            CharacterPersonality.MYSTERIOUS: [
                f"운명이 우리를 하나로 만들었다, {partner.character.name}.", 
                f"예정된 협력이군.", 
                f"별들이 승인한 조합이다.",
                f"숙명적인 만남이군, {partner.character.name}.",
                f"운명의 실이 얽혔다.",
                f"예언된 협력의 순간이다.",
                f"별자리가 우리의 협력을 말하고 있다.",
                f"운명이 이끄는 대로, {partner.character.name}.",
                f"시공을 넘나드는 협력이군.",
                f"정해진 운명을 따르자."
            ],
            CharacterPersonality.HOT_TEMPERED: [
                f"{partner.character.name}! 빨리 따라와!", 
                f"시원하게 날려버리자!", 
                f"협동 공격으로 박살내자!",
                f"불타는 협력이다!",
                f"{partner.character.name}! 화끈하게 가자!",
                f"뜨겁게 싸워보자!",
                f"시원한 협동 공격이다!",
                f"폭발적인 콤보를 보여주자!",
                f"{partner.character.name}! 열정적으로!",
                f"격렬한 협력 전투!"
            ],
            CharacterPersonality.WISE: [
                f"{partner.character.name}, 지혜를 합쳐보자.", 
                f"협력이 승리를 가져다줄 것이다.", 
                f"우리의 경험을 합치자.",
                f"현명한 협력이 열쇠다.",
                f"{partner.character.name}, 깊은 이해를 바탕으로.",
                f"지혜로운 연합이다.",
                f"경험과 지식의 융합이다.",
                f"현명한 판단으로 협력하자.",
                f"깊이 있는 협력을 해보자.",
                f"지혜로운 자들의 협동이다."
            ],
            CharacterPersonality.BALANCED: [
                f"{partner.character.name}, 함께 해봅시다.",
                f"협력해서 해결해봐요.",
                f"서로 도우며 가봅시다.",
                f"좋은 협동이 될 것 같아요.",
                f"{partner.character.name}와 함께라면 괜찮을 거예요.",
                f"균형잡힌 협력을 해봅시다.",
                f"적절한 협동 공격이에요.",
                f"함께하면 더 좋을 거예요."
            ]
        }
        
        # 파트너의 응답 대사 (성격별 대폭 확장)
        partner_response_dialogues = {
            CharacterPersonality.CHEERFUL: [
                f"좋아! {character.name}과 함께 가자!", 
                f"우리 팀워크 보여주자!", 
                f"신나는 협동 공격이다!",
                f"완전 기대돼! {character.name}!",
                f"우리 호흡이 완벽해!",
                f"최고의 파트너야!",
                f"함께라면 뭐든 할 수 있어!",
                f"와! 멋진 콤보가 될 것 같아!",
                f"{character.name}과 함께하니까 더 신나!",
                f"우리가 최강 듀오지!"
            ],
            CharacterPersonality.SERIOUS: [
                f"이해했다, {character.name}.", 
                f"전술에 따라 행동하겠다.", 
                f"협력 개시.",
                f"명령을 따르겠다.",
                f"계획에 동의한다.",
                f"전문적으로 수행하겠다.",
                f"효율적인 협력이다.",
                f"완벽하게 실행하겠다.",
                f"책임감을 가지고 임하겠다.",
                f"프로다운 협력이다."
            ],
            CharacterPersonality.GENTLE: [
                f"네, {character.name}님. 조심해서 가요.", 
                f"함께해서 든든해요.", 
                f"서로 지켜주면서 해요.",
                f"안전하게 함께 해봐요.",
                f"{character.name}님과 함께라면 마음이 편해요.",
                f"서로 도우며 가요.",
                f"무리하지 마세요.",
                f"조심스럽게 해봐요.",
                f"함께하니까 안심이에요.",
                f"서로를 믿고 가봐요."
            ],
            CharacterPersonality.COLD: [
                f"...알겠다.", 
                f"{character.name}... 따르겠다.", 
                f"...시작하자.",
                f"...이해했다.",
                f"협력한다.",
                f"...움직이겠다.",
                f"따라가겠다.",
                f"...준비됐다.",
                f"시작하자.",
                f"...좋다."
            ],
            CharacterPersonality.PLAYFUL: [
                f"오! {character.name}과 콤보라니 재밌겠어!", 
                f"협동 플레이 시작!", 
                f"우리가 최고의 듀오야!",
                f"완전 쿨한 콤보네!",
                f"게임 같아서 재밌어!",
                f"우리만의 스페셜 콤보!",
                f"신나는 놀이 시간이야!",
                f"멋진 쇼를 해보자!",
                f"완전 흥미진진해!",
                f"최고의 엔터테인먼트!"
            ],
            CharacterPersonality.MYSTERIOUS: [
                f"운명의 실이 얽혔군, {character.name}.", 
                f"예정된 순간이다.", 
                f"별들이 축복하리라.",
                f"숙명적인 협력이군.",
                f"운명이 이끄는 대로.",
                f"예언된 순간이 왔다.",
                f"별자리가 말하고 있다.",
                f"시공을 넘나드는 협력.",
                f"운명의 수레바퀴가 돈다.",
                f"정해진 길을 따라가자."
            ],
            CharacterPersonality.HOT_TEMPERED: [
                f"드디어! {character.name}과 함께!", 
                f"시원하게 해보자!", 
                f"불타는 협동 공격이다!",
                f"화끈한 콤보다!",
                f"열정적으로 가자!",
                f"폭발적인 협력이야!",
                f"뜨겁게 싸우자!",
                f"격렬한 전투다!",
                f"시원한 한방이다!",
                f"불꽃 튀는 협력!"
            ],
            CharacterPersonality.WISE: [
                f"현명한 판단이다, {character.name}.", 
                f"협력의 지혜를 보이자.", 
                f"함께라면 승리할 수 있다.",
                f"지혜로운 연합이다.",
                f"경험의 힘을 합치자.",
                f"깊이 있는 협력이다.",
                f"현명한 선택이었다.",
                f"지혜로운 자들의 만남.",
                f"깨달음의 협력이다.",
                f"지식과 경험의 융합."
            ],
            CharacterPersonality.BALANCED: [
                f"좋아요, {character.name}님.",
                f"함께 해봅시다.",
                f"협력해서 해결해요.",
                f"적절한 판단이에요.",
                f"서로 도우며 가요.",
                f"균형잡힌 협력이네요.",
                f"함께하면 좋을 것 같아요.",
                f"적당히 조심해서 가요."
            ]
        }
        
        # 직업별 특수 협동공격 대사
        class_coordination_dialogues = self._get_class_coordination_dialogue(
            getattr(character, 'character_class', '전사'),
            getattr(partner.character, 'character_class', '전사')
        )
        
        # 대사 출력 (안전한 기본값 포함)
        start_dialogue = random.choice(coordination_start_dialogues.get(character_personality, 
            ["함께 가자!", "협력하자!", "같이 해보자!", "힘을 합치자!", "함께 싸우자!"]))
        response_dialogue = random.choice(partner_response_dialogues.get(partner_personality, 
            ["알겠다!", "좋아!", "함께 하자!", "그래!", "따라가겠다!"]))
        
        print(f"\n⚡ {character.name}: \"{start_dialogue}\"")
        print(f"⚡ {partner.character.name}: \"{response_dialogue}\"")
        
        if class_coordination_dialogues:
            print(f"💫 {random.choice(class_coordination_dialogues)}")
        
        time.sleep(1.5)  # 대사 읽을 시간 제공
        
        # 협동 공격 애니메이션
        from .ui_animations import show_coordination_attack_animation
        show_coordination_attack_animation(character.name, partner.character.name)
        
        # 협동 공격 상태 해제
        partner.coordinated_attack_ready = False
        
        # 데미지 보너스 적용
        return "coordinated_attack", {"partner": partner.character}
    
    def _get_class_coordination_dialogue(self, class1: str, class2: str) -> List[str]:
        """직업별 협동공격 특수 대사"""
        coordination_pairs = {
            ("전사", "아크메이지"): [
                "검과 마법의 완벽한 조합이다!",
                "무력과 마력이 하나가 되었다!",
                "물리와 마법의 하모니!"
            ],
            ("궁수", "도적"): [
                "원거리와 근거리의 완벽한 협력!",
                "정밀함과 민첩함의 조합!",
                "그림자와 화살의 춤!"
            ],
            ("성기사", "클레릭"): [
                "신성한 빛이 하나가 되었다!",
                "정의와 치유의 신성한 협력!",
                "신의 뜻이 우리를 하나로!"
            ],
            ("바드", "드루이드"): [
                "자연의 선율과 음악이 어우러진다!",
                "생명의 노래가 울려퍼진다!",
                "자연과 음악의 완벽한 하모니!"
            ],
            ("사무라이", "몽크"): [
                "검의 도와 무술의 도가 만났다!",
                "무사도와 수행정신의 융합!",
                "동양 무술의 완벽한 조화!"
            ],
            ("광전사", "네크로맨서"): [
                "분노와 어둠의 위험한 조합!",
                "광기와 죽음이 손을 잡았다!",
                "파괴적인 협력의 시작!"
            ]
        }
        
        # 순서를 바꿔서도 확인
        dialogue_list = coordination_pairs.get((class1, class2))
        if not dialogue_list:
            dialogue_list = coordination_pairs.get((class2, class1))
        
        return dialogue_list or []
    
    def show_coordination_success_dialogue(self, character: Character, partner: Character):
        """협동공격 성공 후 대사"""
        character_personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
        partner_personality = getattr(partner, 'personality', CharacterPersonality.BALANCED)
        
        # 협동공격 성공 대사 (성격별 대폭 확장)
        success_dialogues = {
            CharacterPersonality.CHEERFUL: [
                f"우와! {partner.name}과 완벽한 콤보였어!",
                f"우리 정말 최고야!",
                f"신나는 팀워크였어!",
                f"역시 우리가 최강이야!",
                f"완전 멋진 협력이었어!",
                f"우리 호흡이 정말 좋네!",
                f"성공! 우리가 해냈어!",
                f"최고의 파트너십이야!",
                f"와! 이런 게 진짜 팀워크지!",
                f"우리 정말 잘 맞아!"
            ],
            CharacterPersonality.SERIOUS: [
                f"{partner.name}과의 협력이 완벽했다.",
                f"전술 성공.",
                f"효과적인 연계였다.",
                f"계획대로 실행됐다.",
                f"프로페셔널한 협력이었다.",
                f"정확한 실행이었다.",
                f"예상한 결과다.",
                f"효율적인 공격이었다.",
                f"완벽한 연계공격.",
                f"전문가다운 협력."
            ],
            CharacterPersonality.GENTLE: [
                f"{partner.name}님과 잘 해냈네요.",
                f"함께해서 좋았어요.",
                f"서로 잘 도왔네요.",
                f"무사히 성공했어요.",
                f"다행히 잘 됐네요.",
                f"서로 지켜주며 잘 했어요.",
                f"안전하게 해냈어요.",
                f"함께라서 가능했어요.",
                f"서로를 믿고 잘 했네요.",
                f"조심스럽게 잘 해냈어요."
            ],
            CharacterPersonality.COLD: [
                f"...성공했다.",
                f"{partner.name}... 나쁘지 않군.",
                f"...효과적이었다.",
                f"...예상 범위다.",
                f"성공.",
                f"...만족스럽다.",
                f"좋다.",
                f"...그럭저럭.",
                f"완료.",
                f"...충분하다."
            ],
            CharacterPersonality.PLAYFUL: [
                f"와! {partner.name}과 환상적인 콤보!",
                f"완전 쿨한 성공이야!",
                f"우리 정말 멋져!",
                f"게임 클리어! 최고야!",
                f"스페셜 콤보 성공!",
                f"완전 재밌는 협력이었어!",
                f"우리가 주인공이야!",
                f"멋진 쇼였어!",
                f"완전 대박이야!",
                f"최고의 엔터테인먼트!"
            ],
            CharacterPersonality.MYSTERIOUS: [
                f"운명이 우리를 축복했군, {partner.name}.",
                f"별들이 미소짓고 있다.",
                f"예정된 성공이었다.",
                f"우주의 섭리가 도왔다.",
                f"숙명적인 승리다.",
                f"시공을 넘나드는 협력의 결실.",
                f"운명의 실이 올바르게 엮였다.",
                f"별자리가 축복한 결과.",
                f"예언이 현실이 되었다.",
                f"신비로운 힘의 융합."
            ],
            CharacterPersonality.HOT_TEMPERED: [
                f"시원하다! {partner.name}과 완벽한 협력!",
                f"불타는 성공이야!",
                f"열정의 결과다!",
                f"화끈한 콤보였어!",
                f"폭발적인 협력이었다!",
                f"뜨거운 승리야!",
                f"시원한 한방이었어!",
                f"격렬한 성공!",
                f"불꽃 튀는 협력의 결과!",
                f"열정적인 팀워크!"
            ],
            CharacterPersonality.WISE: [
                f"{partner.name}과의 지혜로운 협력이었다.",
                f"경험의 힘이 발휘됐다.",
                f"현명한 판단의 결과다.",
                f"지식과 경험의 융합.",
                f"깊이 있는 협력의 성과.",
                f"지혜로운 자들의 승리.",
                f"현명한 연합의 결실.",
                f"깨달음이 이끈 성공.",
                f"지혜와 협력의 조화.",
                f"경험이 만든 완벽한 결과."
            ],
            CharacterPersonality.BALANCED: [
                f"{partner.name}님과 잘 해냈네요.",
                f"적절한 협력이었어요.",
                f"균형잡힌 팀워크였네요.",
                f"서로 잘 맞춰서 성공했어요.",
                f"함께해서 좋은 결과가 나왔네요.",
                f"적당히 잘 해냈어요.",
                f"서로 도와서 성공했네요.",
                f"좋은 협력이었어요."
            ]
        }
        
        # 파트너 응답 대사
        partner_success_responses = {
            CharacterPersonality.CHEERFUL: [
                f"그러게! {character.name}과 함께라서 가능했어!",
                f"우리 조합 정말 최고야!",
                f"다음에도 또 하자!",
                f"완전 신났어!",
                f"우리가 진짜 드림팀이야!"
            ],
            CharacterPersonality.SERIOUS: [
                f"효과적인 협력이었다, {character.name}.",
                f"다음에도 이런식으로 하자.",
                f"전술적으로 성공적이었다.",
                f"계획대로 진행됐다.",
                f"만족스러운 결과다."
            ],
            CharacterPersonality.GENTLE: [
                f"네, {character.name}님 덕분이에요.",
                f"함께해서 다행이었어요.",
                f"서로 잘 도왔네요.",
                f"조심스럽게 잘 해냈어요.",
                f"무사히 끝나서 다행이에요."
            ],
            CharacterPersonality.COLD: [
                f"...나쁘지 않았다.",
                f"{character.name}... 인정한다.",
                f"...성공적이었다.",
                f"좋다.",
                f"...그럭저럭."
            ],
            CharacterPersonality.PLAYFUL: [
                f"우와! {character.name}! 완전 재밌었어!",
                f"또 해보자! 너무 재밌어!",
                f"우리 콤비 완전 쿨해!",
                f"게임 같아서 신나!",
                f"최고의 듀오야!"
            ],
            CharacterPersonality.MYSTERIOUS: [
                f"운명적인 협력이었다, {character.name}.",
                f"별들이 우리를 축복했다.",
                f"예정된 결과였군.",
                f"우주의 뜻이었다.",
                f"신비로운 조화였다."
            ],
            CharacterPersonality.HOT_TEMPERED: [
                f"그래! {character.name}! 시원했어!",
                f"이런 맛에 협력하는 거지!",
                f"불타는 협력이었어!",
                f"다음에도 이렇게 하자!",
                f"열정적이었어!"
            ],
            CharacterPersonality.WISE: [
                f"현명한 협력이었다, {character.name}.",
                f"지혜로운 판단이었다.",
                f"경험의 가치를 느꼈다.",
                f"깊이 있는 협력이었다.",
                f"배울 점이 많았다."
            ],
            CharacterPersonality.BALANCED: [
                f"좋았어요, {character.name}님.",
                f"적절한 협력이었네요.",
                f"서로 잘 맞췄어요.",
                f"균형잡힌 팀워크였어요.",
                f"함께해서 좋았어요."
            ]
        }
        
        # 성공 대사 출력
        success_dialogue = random.choice(success_dialogues.get(character_personality, [f"{partner.name}과 잘 했다!"]))
        partner_response = random.choice(partner_success_responses.get(partner_personality, ["그렇다!"]))
        
        print(f"\n✨ {character.name}: \"{success_dialogue}\"")
        print(f"✨ {partner.name}: \"{partner_response}\"")
        
        # 가끔 직업별 특수 성공 대사 추가 (30% 확률)
        if random.random() < 0.3:
            class_success_dialogues = self._get_class_success_dialogue(
                getattr(character, 'character_class', '전사'),
                getattr(partner, 'character_class', '전사')
            )
            if class_success_dialogues:
                print(f"💫 {random.choice(class_success_dialogues)}")
        
        time.sleep(2)  # 대사 읽을 시간 제공
    
    def _get_class_success_dialogue(self, class1: str, class2: str) -> List[str]:
        """직업별 협동공격 성공 특수 대사"""
        success_pairs = {
            ("전사", "아크메이지"): [
                "검과 마법이 완벽한 승리를 만들어냈다!",
                "무력과 마력의 조화로운 승리!",
                "물리와 마법의 완벽한 융합이었다!"
            ],
            ("궁수", "도적"): [
                "정밀함과 민첩함의 완벽한 결합!",
                "원거리와 근거리의 환상적인 협력!",
                "그림자와 화살이 만든 예술품!"
            ],
            ("성기사", "클레릭"): [
                "신성한 빛의 승리다!",
                "정의와 치유가 하나된 결과!",
                "신의 축복받은 협력이었다!"
            ],
            ("바드", "드루이드"): [
                "자연과 음악의 완벽한 하모니!",
                "생명의 선율이 승리를 이끌었다!",
                "자연의 축복받은 협력!"
            ],
            ("사무라이", "몽크"): [
                "무사도와 수행정신의 완벽한 승리!",
                "동양 무술의 깊이를 보여준 협력!",
                "검과 주먹이 만든 예술!"
            ],
            ("광전사", "네크로맨서"): [
                "광기와 어둠의 위험한 승리!",
                "파괴적인 힘의 완벽한 조화!",
                "분노와 죽음이 만든 공포의 협력!"
            ]
        }
        
        # 순서를 바꿔서도 확인
        dialogue_list = success_pairs.get((class1, class2))
        if not dialogue_list:
            dialogue_list = success_pairs.get((class2, class1))
        
        return dialogue_list or []
    
    def check_equipment_durability(self, party: List[Character]):
        """장비 내구도 확인 및 경고 시스템"""
        warnings = []
        
        for character in party:
            if not hasattr(character, 'equipment') or not character.equipment:
                continue
                
            # 장착된 모든 장비 내구도 확인
            for slot, item in character.equipment.items():
                if not item or not hasattr(item, 'durability') or not hasattr(item, 'max_durability'):
                    continue
                    
                durability_percent = (item.durability / item.max_durability) * 100
                
                # 내구도에 따른 경고 레벨
                if durability_percent <= 10:
                    warnings.append({
                        'character': character,
                        'item': item,
                        'slot': slot,
                        'durability': durability_percent,
                        'level': 'critical'
                    })
                elif durability_percent <= 25:
                    warnings.append({
                        'character': character,
                        'item': item,
                        'slot': slot,
                        'durability': durability_percent,
                        'level': 'warning'
                    })
        
        # 경고 출력
        if warnings:
            self._show_durability_warnings(warnings)
            
        return warnings
    
    def _show_durability_warnings(self, warnings: List[Dict]):
        """내구도 경고 대화 출력"""
        critical_warnings = [w for w in warnings if w['level'] == 'critical']
        normal_warnings = [w for w in warnings if w['level'] == 'warning']
        
        # 치명적 경고 (10% 이하)
        for warning in critical_warnings:
            character = warning['character']
            item = warning['item']
            personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
            
            critical_dialogues = {
                CharacterPersonality.CHEERFUL: [
                    f"앗! {item.name}이 거의 부서져가고 있어!", 
                    f"이런! {item.name} 빨리 수리해야겠어!",
                    f"위험해! {item.name}이 곧 망가질 것 같아!"
                ],
                CharacterPersonality.SERIOUS: [
                    f"{item.name}의 내구도가 한계에 도달했다.",
                    f"즉시 {item.name} 수리가 필요하다.",
                    f"{item.name} 교체를 고려해야 한다."
                ],
                CharacterPersonality.GENTLE: [
                    f"{item.name}이 많이 손상됐어요...",
                    f"조심스럽게 다뤄야 할 것 같아요.",
                    f"{item.name} 수리해야겠어요."
                ],
                CharacterPersonality.COLD: [
                    f"{item.name}... 한계다.",
                    f"수리 필요.",
                    f"교체 고려."
                ],
                CharacterPersonality.PLAYFUL: [
                    f"어? {item.name}이 부서져가고 있어!",
                    f"이런! 게임오버 될 뻔했네!",
                    f"{item.name} 응급처치 필요!"
                ],
                CharacterPersonality.MYSTERIOUS: [
                    f"{item.name}의 생명력이 다해가고 있다.",
                    f"운명이 새로운 장비를 요구하는군.",
                    f"{item.name}의 시대가 끝나가고 있다."
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    f"젠장! {item.name}이 거의 부서졌어!",
                    f"빨리 수리하자!",
                    f"이런 상태로는 싸울 수 없어!"
                ],
                CharacterPersonality.WISE: [
                    f"{item.name}의 수명이 다했군.",
                    f"현명한 선택이 필요하다.",
                    f"경험상 즉시 조치가 필요하다."
                ],
                CharacterPersonality.BALANCED: [
                    f"{item.name} 내구도가 위험해요.",
                    f"수리가 필요한 것 같아요.",
                    f"조심해서 사용해야겠어요."
                ]
            }
            
            dialogue = random.choice(critical_dialogues.get(personality, 
                [f"{item.name} 내구도가 위험합니다!", f"즉시 수리가 필요해요!"]))
            print(f"\n⚠️ {character.name}: \"{dialogue}\"")
        
        # 일반 경고 (25% 이하)
        for warning in normal_warnings:
            character = warning['character']
            item = warning['item']
            personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
            
            warning_dialogues = {
                CharacterPersonality.CHEERFUL: [
                    f"{item.name}이 좀 낡았네.",
                    f"곧 수리해주면 좋겠어!",
                    f"{item.name} 관리가 필요해."
                ],
                CharacterPersonality.SERIOUS: [
                    f"{item.name} 점검이 필요하다.",
                    f"수리 일정을 잡아야겠다.",
                    f"예방 정비가 필요하다."
                ],
                CharacterPersonality.GENTLE: [
                    f"{item.name}이 조금 걱정되네요.",
                    f"미리 관리해두면 좋을 것 같아요.",
                    f"조심스럽게 사용해야겠어요."
                ],
                CharacterPersonality.COLD: [
                    f"{item.name}... 주의.",
                    f"점검 필요.",
                    f"관리하자."
                ],
                CharacterPersonality.PLAYFUL: [
                    f"{item.name}이 삐걱거리네!",
                    f"메인터넌스 타임!",
                    f"수리 게임 해볼까?"
                ],
                CharacterPersonality.MYSTERIOUS: [
                    f"{item.name}의 기운이 약해지고 있다.",
                    f"관심이 필요한 시점이군.",
                    f"별들이 수리를 권하고 있다."
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    f"{item.name} 상태가 안 좋아!",
                    f"빨리 손봐야겠어!",
                    f"미리미리 관리하자!"
                ],
                CharacterPersonality.WISE: [
                    f"{item.name} 관리 시기가 왔다.",
                    f"현명한 예방이 필요하다.",
                    f"경험상 지금 수리하는 게 좋다."
                ],
                CharacterPersonality.BALANCED: [
                    f"{item.name} 상태를 확인해봐요.",
                    f"적절한 관리가 필요해요.",
                    f"미리 수리해두면 좋겠어요."
                ]
            }
            
            dialogue = random.choice(warning_dialogues.get(personality, 
                [f"{item.name} 관리가 필요해요.", f"점검해봐야겠어요."]))
            print(f"\n💡 {character.name}: \"{dialogue}\"")
    
    def suggest_repair_locations(self, party: List[Character]):
        """수리 장소 추천"""
        warnings = self.check_equipment_durability(party)
        
        if warnings:
            print(f"\n🔧 수리 추천:")
            print(f"   - 대장간에서 수리")
            print(f"   - 수리 도구 사용")
            print(f"   - 마을 상인 방문")
            
            # AI가 수리 제안
            if self.ai_companions and random.random() < 0.7:
                companion = random.choice(self.ai_companions)
                personality = getattr(companion, 'personality', CharacterPersonality.BALANCED)
                
                repair_suggestions = {
                    CharacterPersonality.CHEERFUL: [
                        "마을에 가서 수리하자!", "대장간 가면 금방 고칠 수 있어!", 
                        "수리 도구도 있지 않나?"
                    ],
                    CharacterPersonality.SERIOUS: [
                        "효율적인 수리 방법을 찾아보자.", "계획적으로 수리하는 게 좋겠다.",
                        "전문가에게 맡기는 게 안전하다."
                    ],
                    CharacterPersonality.GENTLE: [
                        "조심스럽게 수리해봐요.", "전문가께 부탁드리는 게 좋을 것 같아요.",
                        "안전하게 고쳐야죠."
                    ],
                    CharacterPersonality.COLD: [
                        "수리하자.", "대장간.", "효율적으로."
                    ],
                    CharacterPersonality.PLAYFUL: [
                        "수리 타임!", "대장간 놀이 가자!", "고치는 재미도 쏠쏠할걸?"
                    ],
                    CharacterPersonality.MYSTERIOUS: [
                        "운명이 수리를 요구하고 있다.", "별들이 대장간을 가리키고 있다.",
                        "신비로운 수리의 시간이다."
                    ],
                    CharacterPersonality.HOT_TEMPERED: [
                        "빨리 수리하러 가자!", "대장간으로 달려!", "지금 당장!"
                    ],
                    CharacterPersonality.WISE: [
                        "현명한 수리가 필요하다.", "경험상 전문가가 최고다.",
                        "지혜롭게 관리하자."
                    ],
                    CharacterPersonality.BALANCED: [
                        "적절한 수리가 필요해요.", "균형잡힌 관리를 해봐요.",
                        "안정적으로 수리하죠."
                    ]
                }
                
                suggestion = random.choice(repair_suggestions.get(personality, 
                    ["수리해야겠어요.", "관리가 필요해요."]))
                print(f"💬 {companion.character.name}: \"{suggestion}\"")

                print(f"💬 {companion.character.name}: \"{suggestion}\"")

    def suggest_equipment_enhancement(self, character: Character):
        """장비 강화 추천 시스템"""
        if not hasattr(character, 'equipment') or not character.equipment:
            return
        
        enhanceable_items = []
        
        # 강화 가능한 아이템 찾기
        for slot, item in character.equipment.items():
            if not item:
                continue
                
            # 강화 레벨 확인 (기본값 0)
            enhancement_level = getattr(item, 'enhancement_level', 0)
            max_enhancement = getattr(item, 'max_enhancement', 10)
            
            if enhancement_level < max_enhancement:
                # 강화 효과 계산
                potential_stats = self._calculate_enhancement_potential(item, enhancement_level + 1)
                enhanceable_items.append({
                    'item': item,
                    'slot': slot,
                    'current_level': enhancement_level,
                    'potential_stats': potential_stats,
                    'priority': self._calculate_enhancement_priority(character, item, slot)
                })
        
        if not enhanceable_items:
            return
        
        # 우선순위 정렬
        enhanceable_items.sort(key=lambda x: x['priority'], reverse=True)
        
        # AI가 강화 추천
        personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
        top_recommendation = enhanceable_items[0]
        
        enhancement_dialogues = {
            CharacterPersonality.CHEERFUL: [
                f"{top_recommendation['item'].name} 강화하면 더 강해질 것 같아!",
                f"와! 강화하면 완전 파워업이겠는걸?",
                f"강화 시스템 써보자!"
            ],
            CharacterPersonality.SERIOUS: [
                f"{top_recommendation['item'].name} 강화가 전략적으로 유리하다.",
                f"계산해보니 강화 효과가 좋겠다.",
                f"효율적인 강화가 필요하다."
            ],
            CharacterPersonality.GENTLE: [
                f"{top_recommendation['item'].name} 조심스럽게 강화해볼까요?",
                f"안전하게 강화하면 도움이 될 것 같아요.",
                f"무리하지 않는 선에서 강화해봐요."
            ],
            CharacterPersonality.COLD: [
                f"{top_recommendation['item'].name}... 강화.",
                f"효율적이다.",
                f"강화하자."
            ],
            CharacterPersonality.PLAYFUL: [
                f"{top_recommendation['item'].name} 강화 게임 해보자!",
                f"업그레이드 타임!",
                f"강화하면 더 쿨해질 거야!"
            ],
            CharacterPersonality.MYSTERIOUS: [
                f"운명이 {top_recommendation['item'].name}의 강화를 원한다.",
                f"별들이 강화의 시간을 알려주고 있다.",
                f"신비로운 힘으로 강화하자."
            ],
            CharacterPersonality.HOT_TEMPERED: [
                f"{top_recommendation['item'].name} 빨리 강화하자!",
                f"더 강하게 만들어야겠어!",
                f"강화로 파워업!"
            ],
            CharacterPersonality.WISE: [
                f"{top_recommendation['item'].name} 강화가 현명한 선택이다.",
                f"경험상 지금이 강화 타이밍이다.",
                f"지혜롭게 강화해보자."
            ],
            CharacterPersonality.BALANCED: [
                f"{top_recommendation['item'].name} 강화해볼까요?",
                f"적절한 강화가 필요해 보여요.",
                f"균형잡힌 강화를 해봅시다."
            ]
        }
        
        dialogue = random.choice(enhancement_dialogues.get(personality, 
            [f"{top_recommendation['item'].name} 강화를 고려해보세요.", "강화하면 좋을 것 같아요."]))
        print(f"\n✨ {character.name}: \"{dialogue}\"")
        
        # 강화 정보 출력
        print(f"   🎯 추천: {top_recommendation['item'].name} (+{top_recommendation['current_level']} → +{top_recommendation['current_level']+1})")
        if top_recommendation['potential_stats']:
            for stat, value in top_recommendation['potential_stats'].items():
                print(f"      {stat}: +{value}")
    
    def _calculate_enhancement_potential(self, item, target_level: int) -> Dict[str, int]:
        """강화 시 잠재 스탯 계산"""
        potential = {}
        
        # 기본 스탯들
        base_stats = ['attack_power', 'defense', 'magic_power', 'magic_defense', 'accuracy', 'evasion']
        
        for stat in base_stats:
            if hasattr(item, stat):
                base_value = getattr(item, stat, 0)
                if base_value > 0:
                    # 강화 레벨당 5-15% 증가
                    enhancement_bonus = int(base_value * (target_level * 0.1))
                    potential[stat] = enhancement_bonus
        
        return potential
    
    def _calculate_enhancement_priority(self, character: Character, item, slot: str) -> float:
        """강화 우선순위 계산"""
        priority = 0.0
        
        # 슬롯별 기본 우선순위
        slot_priority = {
            'weapon': 1.0,
            'armor': 0.8,
            'helmet': 0.6,
            'boots': 0.4,
            'accessory': 0.5
        }
        priority += slot_priority.get(slot, 0.3)
        
        # 직업별 우선순위
        class_priority = {
            '전사': {'weapon': 1.2, 'armor': 1.0},
            '아크메이지': {'weapon': 1.1, 'accessory': 1.0},
            '궁수': {'weapon': 1.3, 'boots': 0.8},
            '도적': {'weapon': 1.1, 'boots': 1.0},
            '클레릭': {'weapon': 0.9, 'armor': 1.1},
            '성기사': {'weapon': 1.0, 'armor': 1.2}
        }
        
        char_class = getattr(character, 'character_class', '전사')
        if char_class in class_priority and slot in class_priority[char_class]:
            priority *= class_priority[char_class][slot]
        
        # 현재 강화 레벨 (낮을수록 우선순위 높음)
        current_level = getattr(item, 'enhancement_level', 0)
        priority *= (1.0 / (current_level + 1))
        
        return priority
    
    def check_party_equipment_synergy(self, party: List[Character]):
        """파티 장비 시너지 분석"""
        synergy_suggestions = []
        
        # 직업 조합 분석
        party_classes = [getattr(char, 'character_class', '전사') for char in party]
        class_combinations = self._analyze_class_combinations(party_classes)
        
        # 추천 시너지
        for combination in class_combinations:
            suggestions = self._get_synergy_recommendations(combination, party)
            synergy_suggestions.extend(suggestions)
        
        # AI가 시너지 추천
        if synergy_suggestions and self.ai_companions and random.random() < 0.6:
            companion = random.choice(self.ai_companions)
            personality = getattr(companion, 'personality', CharacterPersonality.BALANCED)
            
            top_suggestion = random.choice(synergy_suggestions)
            
            synergy_dialogues = {
                CharacterPersonality.CHEERFUL: [
                    "우리 팀 조합이 완전 좋아질 것 같아!",
                    "시너지 효과로 더 강해지자!",
                    "팀워크 장비로 파워업!"
                ],
                CharacterPersonality.SERIOUS: [
                    "전략적 장비 조합을 고려해보자.",
                    "팀 시너지 최적화가 필요하다.",
                    "계산된 장비 배치가 중요하다."
                ],
                CharacterPersonality.WISE: [
                    "팀의 조화를 고려한 장비가 현명하다.",
                    "경험상 시너지가 승리의 열쇠다.",
                    "지혜로운 장비 선택이 필요하다."
                ],
                CharacterPersonality.PLAYFUL: [
                    "팀 코디네이션 게임 해보자!",
                    "시너지 콤보 완성하자!",
                    "완전 쿨한 팀 세팅!"
                ]
            }
            
            dialogue = random.choice(synergy_dialogues.get(personality, 
                ["팀 시너지를 고려해봐요.", "조합을 맞춰보면 좋겠어요."]))
            print(f"\n🔗 {companion.character.name}: \"{dialogue}\"")
            print(f"   💡 {top_suggestion}")
    
    def _analyze_class_combinations(self, party_classes: List[str]) -> List[str]:
        """직업 조합 분석"""
        combinations = []
        
        # 전형적인 조합들
        if '전사' in party_classes and '클레릭' in party_classes:
            combinations.append('탱커-힐러')
        
        if '아크메이지' in party_classes and '전사' in party_classes:
            combinations.append('마법-물리')
        
        if '궁수' in party_classes and '도적' in party_classes:
            combinations.append('원거리-근거리')
        
        if '성기사' in party_classes:
            combinations.append('성기사-중심')
        
        return combinations
    
    def _get_synergy_recommendations(self, combination: str, party: List[Character]) -> List[str]:
        """시너지 추천사항"""
        recommendations = []
        
        synergy_map = {
            '탱커-힐러': [
                "전사는 방어력 강화, 클레릭은 회복력 강화 추천",
                "HP 증가 장비로 생존력 향상",
                "방어구 세트 효과 활용"
            ],
            '마법-물리': [
                "마법사는 마력 증가, 전사는 공격력 증가",
                "속성 저항 장비로 균형 맞추기",
                "MP 회복 아이템 공유"
            ],
            '원거리-근거리': [
                "궁수는 정확도, 도적은 회피율 강화",
                "이동속도 증가 장비 공유",
                "크리티컬 확률 향상"
            ],
            '성기사-중심': [
                "성기사 중심의 방어 전술",
                "신성 계열 장비 시너지",
                "팀 전체 방어력 향상"
            ]
        }
        
        return synergy_map.get(combination, [])

        return synergy_map.get(combination, [])

    def smart_equipment_recommendation(self, character: Character, available_items: List = None):
        """현재 상황과 스탯을 고려한 스마트 장비 추천"""
        if not available_items:
            available_items = []  # 실제로는 인벤토리나 상점 아이템
        
        # 현재 캐릭터 상태 분석
        current_stats = self._analyze_character_stats(character)
        weak_points = self._identify_weak_points(character, current_stats)
        
        # 추천 우선순위 계산
        recommendations = []
        
        for item in available_items:
            if not self._is_equippable(character, item):
                continue
                
            score = self._calculate_item_score(character, item, weak_points)
            recommendations.append({
                'item': item,
                'score': score,
                'reasons': self._get_recommendation_reasons(character, item, weak_points)
            })
        
        # 점수순 정렬
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # AI가 추천 제시
        if recommendations and self.ai_companions:
            personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
            top_rec = recommendations[0]
            
            recommendation_dialogues = {
                CharacterPersonality.CHEERFUL: [
                    f"{top_rec['item'].name} 어때? 완전 좋을 것 같아!",
                    f"이거 착용하면 더 강해질 거야!",
                    f"완전 추천 아이템이야!"
                ],
                CharacterPersonality.SERIOUS: [
                    f"{top_rec['item'].name}이 전략적으로 최적이다.",
                    f"분석 결과 이 장비가 가장 효율적이다.",
                    f"계산해보니 이게 최선이다."
                ],
                CharacterPersonality.GENTLE: [
                    f"{top_rec['item'].name} 어떠세요?",
                    f"이 장비가 도움이 될 것 같아요.",
                    f"조심스럽게 추천드려요."
                ],
                CharacterPersonality.COLD: [
                    f"{top_rec['item'].name}... 최적.",
                    f"이걸로 하자.",
                    f"효율적이다."
                ],
                CharacterPersonality.PLAYFUL: [
                    f"{top_rec['item'].name} 완전 쿨해!",
                    f"이거 착용하면 게임 끝!",
                    f"완전 레어템 느낌!"
                ],
                CharacterPersonality.MYSTERIOUS: [
                    f"운명이 {top_rec['item'].name}을 선택했다.",
                    f"별들이 이 장비를 가리키고 있다.",
                    f"신비로운 힘이 느껴진다."
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    f"{top_rec['item'].name} 이거다!",
                    f"빨리 착용하자!",
                    f"완전 대박 아이템!"
                ],
                CharacterPersonality.WISE: [
                    f"{top_rec['item'].name}이 현명한 선택이다.",
                    f"경험상 이 장비가 최고다.",
                    f"지혜로운 판단이 필요한 순간이다."
                ],
                CharacterPersonality.BALANCED: [
                    f"{top_rec['item'].name} 괜찮은 선택이에요.",
                    f"균형잡힌 스탯 향상이 기대돼요.",
                    f"적절한 업그레이드가 될 것 같아요."
                ]
            }
            
            dialogue = random.choice(recommendation_dialogues.get(personality, 
                [f"{top_rec['item'].name} 추천드려요.", "이 장비 어떠세요?"]))
            print(f"\n🎯 {character.name}: \"{dialogue}\"")
            
            # 추천 이유 출력
            for reason in top_rec['reasons'][:3]:  # 상위 3개 이유만
                print(f"   💡 {reason}")
    
    def _analyze_character_stats(self, character: Character) -> Dict[str, float]:
        """캐릭터 현재 스탯 분석"""
        stats = {}
        
        # 기본 스탯들
        basic_stats = ['attack_power', 'defense', 'magic_power', 'magic_defense', 
                      'accuracy', 'evasion', 'max_hp', 'max_mp']
        
        for stat in basic_stats:
            stats[stat] = getattr(character, stat, 0)
        
        # 직업별 기준치 계산
        class_standards = self._get_class_stat_standards(character.character_class)
        
        # 현재 레벨 대비 상대적 스탯
        level = getattr(character, 'level', 1)
        for stat in stats:
            expected = class_standards.get(stat, 0) * level
            if expected > 0:
                stats[f"{stat}_ratio"] = stats[stat] / expected
            else:
                stats[f"{stat}_ratio"] = 1.0
        
        return stats
    
    def _identify_weak_points(self, character: Character, stats: Dict[str, float]) -> List[str]:
        """약점 식별"""
        weak_points = []
        
        # 비율이 0.8 이하인 스탯을 약점으로 식별
        for stat, value in stats.items():
            if stat.endswith('_ratio') and value < 0.8:
                base_stat = stat.replace('_ratio', '')
                weak_points.append(base_stat)
        
        # 직업별 핵심 스탯 부족 확인
        class_core_stats = {
            '전사': ['attack_power', 'defense', 'max_hp'],
            '아크메이지': ['magic_power', 'max_mp', 'magic_defense'],
            '궁수': ['attack_power', 'accuracy', 'evasion'],
            '도적': ['attack_power', 'evasion', 'accuracy'],
            '클레릭': ['magic_power', 'max_mp', 'defense'],
            '성기사': ['attack_power', 'defense', 'magic_defense']
        }
        
        char_class = getattr(character, 'character_class', '전사')
        core_stats = class_core_stats.get(char_class, [])
        
        for stat in core_stats:
            if f"{stat}_ratio" in stats and stats[f"{stat}_ratio"] < 0.9:
                if stat not in weak_points:
                    weak_points.append(stat)
        
        return weak_points
    
    def _get_class_stat_standards(self, character_class: str) -> Dict[str, float]:
        """직업별 스탯 기준치"""
        standards = {
            '전사': {
                'attack_power': 10.0, 'defense': 8.0, 'max_hp': 20.0,
                'magic_power': 3.0, 'magic_defense': 5.0, 'max_mp': 8.0,
                'accuracy': 6.0, 'evasion': 4.0
            },
            '아크메이지': {
                'attack_power': 4.0, 'defense': 4.0, 'max_hp': 12.0,
                'magic_power': 12.0, 'magic_defense': 8.0, 'max_mp': 25.0,
                'accuracy': 5.0, 'evasion': 6.0
            },
            '궁수': {
                'attack_power': 9.0, 'defense': 5.0, 'max_hp': 15.0,
                'magic_power': 4.0, 'magic_defense': 5.0, 'max_mp': 10.0,
                'accuracy': 10.0, 'evasion': 8.0
            },
            '도적': {
                'attack_power': 8.0, 'defense': 4.0, 'max_hp': 14.0,
                'magic_power': 3.0, 'magic_defense': 4.0, 'max_mp': 8.0,
                'accuracy': 9.0, 'evasion': 12.0
            },
            '클레릭': {
                'attack_power': 5.0, 'defense': 6.0, 'max_hp': 16.0,
                'magic_power': 10.0, 'magic_defense': 7.0, 'max_mp': 22.0,
                'accuracy': 6.0, 'evasion': 5.0
            },
            '성기사': {
                'attack_power': 8.0, 'defense': 9.0, 'max_hp': 18.0,
                'magic_power': 6.0, 'magic_defense': 8.0, 'max_mp': 15.0,
                'accuracy': 7.0, 'evasion': 5.0
            }
        }
        
        return standards.get(character_class, standards['전사'])
    
    def _is_equippable(self, character: Character, item) -> bool:
        """장비 착용 가능 여부 확인"""
        # 레벨 제한
        if hasattr(item, 'required_level'):
            if getattr(character, 'level', 1) < item.required_level:
                return False
        
        # 직업 제한
        if hasattr(item, 'required_class'):
            char_class = getattr(character, 'character_class', '전사')
            if char_class not in item.required_class:
                return False
        
        return True
    
    def _calculate_item_score(self, character: Character, item, weak_points: List[str]) -> float:
        """아이템 점수 계산"""
        score = 0.0
        
        # 기본 스탯 향상 점수
        item_stats = ['attack_power', 'defense', 'magic_power', 'magic_defense',
                     'accuracy', 'evasion', 'max_hp', 'max_mp']
        
        for stat in item_stats:
            if hasattr(item, stat):
                stat_value = getattr(item, stat, 0)
                if stat_value > 0:
                    # 약점 스탯이면 가중치 2배
                    multiplier = 2.0 if stat in weak_points else 1.0
                    score += stat_value * multiplier
        
        # 직업 적합성 보너스
        char_class = getattr(character, 'character_class', '전사')
        class_bonus = self._get_class_item_bonus(char_class, item)
        score *= (1.0 + class_bonus)
        
        # 현재 장비와 비교
        current_item = self._get_current_item_in_slot(character, item)
        if current_item:
            improvement = self._calculate_improvement(current_item, item)
            score *= (1.0 + improvement)
        
        return score
    
    def _get_class_item_bonus(self, character_class: str, item) -> float:
        """직업별 아이템 보너스"""
        item_type = getattr(item, 'item_type', 'unknown')
        
        class_bonuses = {
            '전사': {'weapon': 0.3, 'armor': 0.2, 'shield': 0.2},
            '아크메이지': {'staff': 0.3, 'robe': 0.2, 'accessory': 0.2},
            '궁수': {'bow': 0.3, 'leather_armor': 0.2, 'boots': 0.1},
            '도적': {'dagger': 0.3, 'leather_armor': 0.2, 'boots': 0.2},
            '클레릭': {'staff': 0.2, 'robe': 0.2, 'accessory': 0.3},
            '성기사': {'sword': 0.2, 'armor': 0.3, 'shield': 0.2}
        }
        
        return class_bonuses.get(character_class, {}).get(item_type, 0.0)
    
    def _get_current_item_in_slot(self, character: Character, new_item):
        """해당 슬롯의 현재 아이템 반환"""
        if not hasattr(character, 'equipment'):
            return None
        
        item_slot = getattr(new_item, 'slot', 'unknown')
        return character.equipment.get(item_slot)
    
    def _calculate_improvement(self, current_item, new_item) -> float:
        """아이템 개선도 계산"""
        if not current_item:
            return 1.0  # 100% 개선 (빈 슬롯)
        
        improvement = 0.0
        stats = ['attack_power', 'defense', 'magic_power', 'magic_defense',
                'accuracy', 'evasion', 'max_hp', 'max_mp']
        
        for stat in stats:
            current_value = getattr(current_item, stat, 0)
            new_value = getattr(new_item, stat, 0)
            
            if current_value > 0:
                improvement += (new_value - current_value) / current_value
        
        return max(0.0, improvement / len(stats))
    
    def _get_recommendation_reasons(self, character: Character, item, weak_points: List[str]) -> List[str]:
        """추천 이유 생성"""
        reasons = []
        
        # 약점 보완
        item_stats = ['attack_power', 'defense', 'magic_power', 'magic_defense',
                     'accuracy', 'evasion', 'max_hp', 'max_mp']
        
        for stat in item_stats:
            if hasattr(item, stat) and getattr(item, stat, 0) > 0:
                if stat in weak_points:
                    reasons.append(f"{stat} 약점 보완")
        
        # 직업 적합성
        char_class = getattr(character, 'character_class', '전사')
        item_type = getattr(item, 'item_type', 'unknown')
        
        class_suitable_types = {
            '전사': ['weapon', 'armor', 'shield'],
            '아크메이지': ['staff', 'robe', 'accessory'],
            '궁수': ['bow', 'leather_armor', 'boots'],
            '도적': ['dagger', 'leather_armor', 'boots'],
            '클레릭': ['staff', 'robe', 'accessory'],
            '성기사': ['sword', 'armor', 'shield']
        }
        
        if item_type in class_suitable_types.get(char_class, []):
            reasons.append(f"{char_class}에게 최적화된 장비")
        
        # 특수 효과
        if hasattr(item, 'special_effects'):
            reasons.append("특수 효과 보유")
        
        if not reasons:
            reasons.append("전체적인 능력치 향상")
        
        return reasons

        return reasons

    def integrate_with_combat_system(self, combat_system):
        """전투 시스템과의 완전 통합"""
        # 전투 시스템에 AI 게임모드 연결
        combat_system.ai_game_mode = self
        
        # 전투 전 장비 점검
        self.pre_combat_check = True
        
        # 전투 후 시스템들 실행
        self.post_combat_analysis = True
        
        print("✅ AI 게임모드가 전투 시스템과 완전 통합되었습니다.")
    
    def pre_combat_equipment_check(self, party: List[Character]):
        """전투 전 장비 상태 점검"""
        print("\n🔍 전투 전 장비 점검...")
        
        # 내구도 점검
        durability_warnings = self.check_equipment_durability(party)
        
        # 치명적 내구도 문제가 있으면 경고
        critical_items = [w for w in durability_warnings if w['level'] == 'critical']
        if critical_items:
            print("⚠️ 치명적 내구도 문제 발견!")
            for warning in critical_items:
                char = warning['character']
                item = warning['item']
                print(f"   {char.name}의 {item.name}: {warning['durability']:.1f}%")
            
            # AI가 전투 전 조언
            if self.ai_companions and random.random() < 0.8:
                advisor = random.choice(self.ai_companions)
                personality = getattr(advisor, 'personality', CharacterPersonality.BALANCED)
                
                advice_dialogues = {
                    CharacterPersonality.SERIOUS: [
                        "전투 전에 장비를 점검하는 게 좋겠다.",
                        "위험한 상태의 장비가 있다.",
                        "전술적으로 불리할 수 있다."
                    ],
                    CharacterPersonality.CHEERFUL: [
                        "어? 장비가 좀 위험해 보여!",
                        "전투 전에 챙겨야 할 것 같아!",
                        "괜찮을까? 걱정되네!"
                    ],
                    CharacterPersonality.WISE: [
                        "현명한 전사는 장비를 먼저 점검한다.",
                        "경험상 지금 수리하는 게 좋겠다.",
                        "준비가 승리의 절반이다."
                    ]
                }
                
                advice = random.choice(advice_dialogues.get(personality, 
                    ["장비 상태를 확인해보세요.", "전투 전 점검이 필요해요."]))
                print(f"💬 {advisor.character.name}: \"{advice}\"")
        
        # 파티 시너지 점검
        self.check_party_equipment_synergy(party)
    
    def post_combat_analysis(self, party: List[Character], battle_result: str):
        """전투 후 분석 및 추천"""
        print(f"\n📊 전투 후 분석 (결과: {battle_result})")
        
        # 승리 시 분석
        if battle_result == "victory":
            # 전투 승리 대사 트리거
            self.trigger_situational_dialogue("combat_victory")
            
            # 장비 내구도 감소 체크
            self._check_post_combat_durability(party)
            
            # 강화 추천 (30% 확률)
            if random.random() < 0.3:
                for character in party:
                    if random.random() < 0.4:  # 각 캐릭터당 40% 확률
                        self.suggest_equipment_enhancement(character)
        
        # 패배 시 분석
        elif battle_result == "defeat":
            self._analyze_defeat_reasons(party)
        
        # 전투 중 협동공격 통계 (만약 있다면)
        self._show_coordination_stats()
    
    def _check_post_combat_durability(self, party: List[Character]):
        """전투 후 내구도 감소 체크"""
        for character in party:
            if not hasattr(character, 'equipment') or not character.equipment:
                continue
            
            for slot, item in character.equipment.items():
                if not item or not hasattr(item, 'durability'):
                    continue
                
                # 전투로 인한 내구도 감소 시뮬레이션 (1-3 감소)
                durability_loss = random.randint(1, 3)
                original_durability = getattr(item, 'durability', 100)
                item.durability = max(0, original_durability - durability_loss)
                
                # 내구도가 크게 감소한 경우 알림
                durability_percent = (item.durability / getattr(item, 'max_durability', 100)) * 100
                if durability_percent <= 15 and random.random() < 0.5:
                    personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
                    
                    concern_dialogues = {
                        CharacterPersonality.CHEERFUL: [
                            f"{item.name}이 많이 닳았네!",
                            f"전투가 격렬했나봐!",
                            f"곧 수리해야겠어!"
                        ],
                        CharacterPersonality.SERIOUS: [
                            f"{item.name}의 내구도 저하를 확인했다.",
                            f"정비가 필요한 상태다.",
                            f"전투 효율에 영향을 줄 수 있다."
                        ],
                        CharacterPersonality.COLD: [
                            f"{item.name}... 손상됐다.",
                            f"수리 필요.",
                            f"교체 고려."
                        ]
                    }
                    
                    dialogue = random.choice(concern_dialogues.get(personality, 
                        [f"{item.name} 상태가 걱정되네요.", "점검이 필요해요."]))
                    print(f"🔧 {character.name}: \"{dialogue}\"")
    
    def _analyze_defeat_reasons(self, party: List[Character]):
        """패배 원인 분석"""
        print("💭 패배 원인 분석 중...")
        
        # 장비 부족 분석
        equipment_issues = []
        for character in party:
            weak_points = self._identify_weak_points(character, self._analyze_character_stats(character))
            if weak_points:
                equipment_issues.append((character, weak_points))
        
        if equipment_issues and self.ai_companions:
            analyst = random.choice(self.ai_companions)
            personality = getattr(analyst, 'personality', CharacterPersonality.BALANCED)
            
            analysis_dialogues = {
                CharacterPersonality.WISE: [
                    "패배에서 배울 점이 있다.",
                    "장비 보완이 필요해 보인다.",
                    "경험을 통해 더 강해질 수 있다."
                ],
                CharacterPersonality.SERIOUS: [
                    "전력 분석이 필요하다.",
                    "장비 개선 사항을 파악했다.",
                    "다음 전투를 위한 준비가 필요하다."
                ],
                CharacterPersonality.CHEERFUL: [
                    "다음엔 더 잘할 수 있을 거야!",
                    "장비 업그레이드하면 이길 수 있어!",
                    "포기하지 말고 준비하자!"
                ]
            }
            
            analysis = random.choice(analysis_dialogues.get(personality, 
                ["다음을 위해 준비해봐요.", "개선점을 찾아봅시다."]))
            print(f"💡 {analyst.character.name}: \"{analysis}\"")
            
            # 구체적 개선사항 제시
            for character, weak_points in equipment_issues[:2]:  # 상위 2명만
                print(f"   🎯 {character.name}: {', '.join(weak_points)} 보완 필요")
    
    def _show_coordination_stats(self):
        """협동공격 통계 표시"""
        # 실제 구현에서는 전투 중 협동공격 데이터를 수집해야 함
        if hasattr(self, 'coordination_count') and self.coordination_count > 0:
            print(f"⚡ 협동공격 실행: {self.coordination_count}회")
            
            if self.ai_companions and random.random() < 0.6:
                commentator = random.choice(self.ai_companions)
                personality = getattr(commentator, 'personality', CharacterPersonality.BALANCED)
                
                coord_comments = {
                    CharacterPersonality.CHEERFUL: [
                        "우리 팀워크 완전 최고였어!",
                        "협동공격이 정말 멋졌어!",
                        "다음에도 이렇게 하자!"
                    ],
                    CharacterPersonality.SERIOUS: [
                        "효과적인 협동 전술이었다.",
                        "팀워크가 승리의 열쇠였다.",
                        "전략적 협력이 성공했다."
                    ],
                    CharacterPersonality.WISE: [
                        "협력의 가치를 확인했다.",
                        "함께하는 힘이 위대하다.",
                        "조화로운 전투였다."
                    ]
                }
                
                comment = random.choice(coord_comments.get(personality, 
                    ["좋은 협력이었어요.", "팀워크가 훌륭했어요."]))
                print(f"💬 {commentator.character.name}: \"{comment}\"")
    
    def periodic_equipment_maintenance(self, party: List[Character]):
        """주기적 장비 관리 시스템"""
        # 필드에서 5% 확률로 장비 상태 체크
        if random.random() < 0.05:
            print("\n🔧 장비 상태 점검 시간...")
            
            # 내구도 체크
            warnings = self.check_equipment_durability(party)
            
            # 강화 추천 (낮은 확률)
            if random.random() < 0.3:
                character = random.choice(party)
                self.suggest_equipment_enhancement(character)
            
            # 파티 시너지 체크 (낮은 확률)
            if random.random() < 0.2:
                self.check_party_equipment_synergy(party)
    
    def emergency_equipment_alert(self, character: Character, item):
        """긴급 장비 경고"""
        if not item or not hasattr(item, 'durability'):
            return
        
        durability_percent = (item.durability / getattr(item, 'max_durability', 100)) * 100
        
        if durability_percent <= 5:  # 5% 이하 시 긴급 경고
            personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
            
            emergency_dialogues = {
                CharacterPersonality.CHEERFUL: [
                    f"어? {item.name}이 거의 부서져가고 있어!",
                    f"큰일이야! 빨리 뭔가 해야겠어!"
                ],
                CharacterPersonality.SERIOUS: [
                    f"긴급상황! {item.name} 즉시 교체 필요!",
                    f"전투 불가 상태에 도달했다!"
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    f"젠장! {item.name}이 완전히 망가졌어!",
                    f"이런 상태로는 못 싸워!"
                ],
                CharacterPersonality.COLD: [
                    f"{item.name}... 한계다.",
                    f"즉시 교체."
                ]
            }
            
            dialogue = random.choice(emergency_dialogues.get(personality, 
                [f"{item.name} 긴급 상황!", "즉시 조치 필요!"]))
            print(f"\n🚨 {character.name}: \"{dialogue}\"")
            
            return True  # 긴급 상황 플래그
        
        return False

        return False

    def run_integrated_ai_systems(self, party: List[Character], context: str = "field"):
        """통합 AI 시스템 실행 - 모든 시스템을 조율"""
        
        # 1. 주기적 장비 관리
        if context == "field":
            self.periodic_equipment_maintenance(party)
        
        # 2. 전투 전 점검
        elif context == "pre_combat":
            self.pre_combat_equipment_check(party)
        
        # 3. 전투 후 분석
        elif context == "post_combat":
            battle_result = getattr(self, 'last_battle_result', 'victory')
            self.post_combat_analysis(party, battle_result)
        
        # 4. 레벨업 시 장비 추천
        elif context == "level_up":
            character = getattr(self, 'leveled_up_character', None)
            if character:
                print(f"\n🎯 레벨업 축하! {character.name}의 장비를 점검해봅시다.")
                self.smart_equipment_recommendation(character, [])  # 실제로는 인벤토리 아이템들
                self.suggest_equipment_enhancement(character)
        
        # 5. 랜덤 필드 대화 (기존)
        elif context == "field_dialogue":
            return self.trigger_random_field_dialogue(party)
        
        # 6. 상황별 대화
        elif context.startswith("situational_"):
            situation = context.replace("situational_", "")
            self.trigger_situational_dialogue(situation)
        
        return True
    
    def get_ai_mode_status(self) -> Dict[str, any]:
        """AI 모드 현재 상태 반환"""
        status = {
            'mode': self.current_mode.value,
            'player_controlled': len(self.player_controlled_characters),
            'ai_controlled': len(self.ai_companions),
            'pending_requests': len(self.pending_ai_requests),
            'systems_active': {
                'durability_check': True,
                'equipment_enhancement': True,
                'smart_recommendations': True,
                'party_synergy': True,
                'combat_integration': True
            },
            'companions_info': []
        }
        
        # AI 동료 정보
        for companion in self.ai_companions:
            companion_info = {
                'name': companion.character.name,
                'class': getattr(companion.character, 'character_class', 'Unknown'),
                'personality': getattr(companion, 'personality', CharacterPersonality.BALANCED).value,
                'gender': getattr(companion.character, 'gender', CharacterGender.MALE).value,
                'coordination_ready': getattr(companion, 'coordinated_attack_ready', False)
            }
            status['companions_info'].append(companion_info)
        
        return status
    
    def save_ai_mode_state(self) -> Dict[str, any]:
        """AI 모드 상태 저장"""
        save_data = {
            'current_mode': self.current_mode.value,
            'player_character_names': [char.name for char in self.player_controlled_characters],
            'ai_companion_data': [],
            'settings': {
                'item_sharing_enabled': self.item_sharing_enabled,
                'coordination_opportunities': len(self.coordination_opportunities)
            }
        }
        
        # AI 동료 데이터 저장
        for companion in self.ai_companions:
            companion_data = {
                'character_name': companion.character.name,
                'personality': getattr(companion, 'personality', CharacterPersonality.BALANCED).value,
                'coordinated_attack_ready': getattr(companion, 'coordinated_attack_ready', False)
            }
            save_data['ai_companion_data'].append(companion_data)
        
        return save_data
    
    def is_ai_controlled(self, character: Character) -> bool:
        """캐릭터가 AI 조작인지 확인"""
        if not character:
            return False
        
        # AI 동료 리스트에서 확인
        for ai_companion in self.ai_companions:
            if ai_companion.character == character:
                return True
        
        # 플레이어 조작 캐릭터가 아니면 AI 조작으로 판단
        if character not in self.player_controlled_characters:
            return True
        
        return False
    
    def load_ai_mode_state(self, save_data: Dict[str, any], party: List[Character]):
        """AI 모드 상태 로드"""
        # 모드 복원
        mode_value = save_data.get('current_mode', AIGameMode.SINGLE_CONTROL.value)
        self.current_mode = AIGameMode(mode_value)
        
        # 플레이어 조작 캐릭터 복원
        player_names = save_data.get('player_character_names', [])
        self.player_controlled_characters = [
            char for char in party if char.name in player_names
        ]
        
        # AI 동료 복원
        ai_data = save_data.get('ai_companion_data', [])
        self.ai_companions = []
        
        for data in ai_data:
            char_name = data.get('character_name')
            character = next((char for char in party if char.name == char_name), None)
            
            if character:
                personality_value = data.get('personality', CharacterPersonality.BALANCED.value)
                personality = CharacterPersonality(personality_value)
                
                companion = AICompanion(character, AIPersonality.AGGRESSIVE)  # 기본값
                companion.personality = personality
                companion.coordinated_attack_ready = data.get('coordinated_attack_ready', False)
                
                self.ai_companions.append(companion)
        
        # 설정 복원
        settings = save_data.get('settings', {})
        self.item_sharing_enabled = settings.get('item_sharing_enabled', True)
        
        print(f"✅ AI 모드 상태가 복원되었습니다.")
        print(f"   플레이어 조작: {len(self.player_controlled_characters)}명")
        print(f"   AI 조작: {len(self.ai_companions)}명")

    def trigger_random_field_dialogue(self, party: List[Character]) -> bool:
        """필드에서 랜덤 대화 발생 (5% 확률)"""
        if random.random() > 0.05:  # 5% 확률
            return False
        
        if not self.ai_companions:
            return False
        
        # AI 동료 중 랜덤 선택
        speaker = random.choice(self.ai_companions)
        personality = speaker.personality if hasattr(speaker, 'personality') else CharacterPersonality.BALANCED
        
        # 필드 사담 가져오기 (안전한 기본값 포함)
        casual_dialogues = CharacterTraits.FIELD_CASUAL_DIALOGUE.get(personality, 
            ["좋은 날씨네요.", "모험을 계속해봅시다.", "함께 가요.", "조심해서 가요.", "잠깐 쉬어갈까요?"])
        dialogue = random.choice(casual_dialogues)
        
        print(f"\n💭 {speaker.character.name}: \"{dialogue}\"")
        
        # 다른 AI 동료가 응답할 확률 (30%)
        if len(self.ai_companions) > 1 and random.random() < 0.3:
            responders = [ai for ai in self.ai_companions if ai != speaker]
            responder = random.choice(responders)
            responder_personality = responder.personality if hasattr(responder, 'personality') else CharacterPersonality.BALANCED
            
            # 응답 대사
            response_dialogues = {
                CharacterPersonality.CHEERFUL: ["그러게!", "맞아!", "나도 그렇게 생각해!", "좋은 말이야!"],
                CharacterPersonality.SERIOUS: ["그렇군.", "이해한다.", "동감이다.", "맞는 말이다."],
                CharacterPersonality.GENTLE: ["그러시네요.", "좋은 말씀이에요.", "그럴 수도 있겠어요.", "맞아요."],
                CharacterPersonality.COLD: ["...", "그렇다.", "...알겠다.", "...그런가."],
                CharacterPersonality.PLAYFUL: ["헤헤, 그러네!", "재밌는 말이야!", "오, 그럴까?", "신기하다!"],
                CharacterPersonality.MYSTERIOUS: ["흥미롭군.", "운명적인 말이다.", "그렇게 정해진 것인가.", "별들도 그렇게 말한다."],
                CharacterPersonality.HOT_TEMPERED: ["그렇지!", "당연하지!", "맞아!", "그럼!"],
                CharacterPersonality.WISE: ["지혜로운 말이다.", "깊이 있는 관찰이다.", "현명한 생각이다.", "배울 점이 있다."]
            }
            
            response = random.choice(response_dialogues.get(responder_personality, ["그렇군."]))
            print(f"💭 {responder.character.name}: \"{response}\"")
        
        time.sleep(2)  # 읽을 시간 제공
        return True
    
    def trigger_party_encounter_dialogue(self, encounter_type: str, party: List[Character]):
        """파티원 전용 인카운터 대화"""
        if not self.ai_companions:
            return
        
        encounter_dialogues = CharacterTraits.PARTY_ENCOUNTER_DIALOGUE.get(encounter_type, {})
        if not encounter_dialogues:
            return
        
        print(f"\n🎭 파티원들의 반응:")
        
        # 각 AI 동료의 반응
        for companion in self.ai_companions:
            personality = companion.personality if hasattr(companion, 'personality') else CharacterPersonality.BALANCED
            dialogues = encounter_dialogues.get(personality, ["..."])
            dialogue = random.choice(dialogues)
            
            print(f"💬 {companion.character.name}: \"{dialogue}\"")
            time.sleep(0.8)  # 순차적으로 대화 출력
        
        # 가끔 플레이어 캐릭터도 참여 (20% 확률)
        if random.random() < 0.2 and self.player_controlled_characters:
            player_char = random.choice(self.player_controlled_characters)
            player_personality = getattr(player_char, 'personality', CharacterPersonality.BALANCED)
            player_dialogues = encounter_dialogues.get(player_personality, ["..."])
            player_dialogue = random.choice(player_dialogues)
            
            print(f"💬 {player_char.name} (당신): \"{player_dialogue}\"")
        
        time.sleep(2)
    
    def trigger_situational_dialogue(self, situation: str, character: Character = None, target: Character = None):
        """상황별 특수 대화 트리거"""
        
        # 특수 상황별 대화
        situational_dialogues = {
            "level_up": {
                CharacterPersonality.CHEERFUL: [
                    "야호! 레벨업이다!", "강해진 기분이야!", "더 열심히 해보자!",
                    "완전 신나! 더 강해졌어!", "와! 성장했다!", "레벨업! 최고야!",
                    "새로운 힘이 느껴져!", "더 많은 모험을 할 수 있겠어!", "성장하는 기분 좋아!",
                    "우리 다같이 강해지자!"
                ],
                CharacterPersonality.SERIOUS: [
                    "성장했다.", "더욱 책임감을 느낀다.", "다음 목표로 나아가자.",
                    "실력이 향상됐다.", "더 효율적으로 행동할 수 있겠다.", "전략적 선택지가 늘었다.",
                    "능력치 상승을 확인했다.", "훈련의 성과다.", "계획적 성장이다.",
                    "더 높은 목표를 세워야겠다."
                ],
                CharacterPersonality.GENTLE: [
                    "조금 더 강해진 것 같아요.", "모두 덕분이에요.", "감사해요.",
                    "다행히 성장할 수 있었어요.", "함께해서 가능했던 것 같아요.", "소중한 경험이었어요.",
                    "더 도움이 될 수 있을 것 같아요.", "조심스럽게 사용하겠어요.", "모두를 위해 사용할게요.",
                    "겸손하게 받아들이겠어요."
                ],
                CharacterPersonality.COLD: [
                    "레벨업.", "...강해졌다.", "계속하자.",
                    "성장.", "...당연한 결과.", "다음.",
                    "능력 향상.", "...효과적.", "진행하자.",
                    "...만족스럽다."
                ],
                CharacterPersonality.PLAYFUL: [
                    "레벨업! 새로운 기술 배울 수 있나?", "더 재밌어졌어!", "신난다!",
                    "완전 쿨해! 새로운 능력!", "게임 같아서 재밌어!", "레벨업 파티!",
                    "어떤 새로운 능력이 있을까?", "완전 흥미진진해!", "더 재밌는 모험 가능!",
                    "레벨업 축하해줘!"
                ],
                CharacterPersonality.MYSTERIOUS: [
                    "운명의 힘이 강해졌다.", "별들이 축복해주었군.", "예정된 성장이다.",
                    "우주의 힘이 흘러들어온다.", "신비로운 성장이군.", "별자리가 변화했다.",
                    "운명의 새로운 장이 열렸다.", "시공의 힘이 증가했다.", "예언된 성장.",
                    "우주가 인정한 발전."
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    "드디어! 더 강해졌어!", "이제 더 시원하게 싸울 수 있겠어!", "레벨업!",
                    "불타는 성장이야!", "열정의 결과다!", "더 화끈하게 싸우자!",
                    "시원한 레벨업!", "폭발적인 성장!", "열정이 결실을 맺었어!",
                    "이제 더 강력해졌다!"
                ],
                CharacterPersonality.WISE: [
                    "경험이 지혜가 되었다.", "성장의 기쁨을 느낀다.", "배움의 결실이다.",
                    "수련의 성과가 나타났다.", "지혜로운 발전이다.", "깊이 있는 성장.",
                    "경험의 축적이 힘이 되었다.", "현명한 발전의 길.", "지식이 힘이 되었다.",
                    "깨달음의 순간이다."
                ],
                CharacterPersonality.BALANCED: [
                    "레벨업했네요.", "적절한 성장이에요.", "균형잡힌 발전이네요.",
                    "좋은 성장이에요.", "적당히 강해진 것 같아요.", "꾸준한 발전이네요.",
                    "안정적인 성장이에요.", "함께 성장해봐요."
                ]
            },
            "critical_hit": {
                CharacterPersonality.CHEERFUL: [
                    "대박! 완벽한 타격!", "엄청 잘 맞았어!", "우와! 이런 게 크리티컬이구나!",
                    "완전 럭키 히트!", "신나는 크리티컬!", "야호! 완벽한 타이밍!",
                    "최고의 한방!", "기분 좋은 크리티컬!", "와! 이런 맛에 싸우는 거야!",
                    "완전 대박 크리티컬!"
                ],
                CharacterPersonality.SERIOUS: [
                    "정확한 타격이었다.", "계산된 공격.", "효과적이었다.",
                    "전략적 성공.", "예상한 결과다.", "정밀한 공격이었다.",
                    "훈련의 성과.", "완벽한 실행.", "프로페셔널한 타격.",
                    "계획대로 진행됐다."
                ],
                CharacterPersonality.GENTLE: [
                    "운이 좋았나 봐요.", "다행히 잘 맞았어요.", "미안해요.",
                    "실수로 세게 맞았네요.", "조심스럽게 했는데...", "의도한 건 아니에요.",
                    "너무 아프게 했나요?", "죄송해요.", "조심해야겠어요.",
                    "다치지 않았으면 좋겠어요."
                ],
                CharacterPersonality.COLD: [
                    "크리티컬.", "...잘 맞았다.", "효과적이다.",
                    "치명타.", "...성공.", "좋다.",
                    "정확하다.", "...만족.", "다음.",
                    "...완벽."
                ],
                CharacterPersonality.PLAYFUL: [
                    "대박! 슈퍼 히트!", "완전 크리티컬!", "이런 맛에 싸우는 거지!",
                    "완전 쿨한 크리티컬!", "게임 같은 타격!", "완전 대박!",
                    "슈퍼 럭키!", "멋진 크리티컬 쇼!", "이런 게 진짜 재미!",
                    "완전 스펙터클!"
                ],
                CharacterPersonality.MYSTERIOUS: [
                    "운명이 인도한 일격.", "별들이 승인한 타격.", "예정된 치명타.",
                    "우주의 힘이 집중됐다.", "신비로운 일격이군.", "별자리가 정렬한 순간.",
                    "운명적인 타격.", "시공이 인정한 일격.", "예언된 크리티컬.",
                    "우주의 뜻이 담긴 타격."
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    "시원하다! 제대로 박혔어!", "이런 맛이야!", "크리티컬!",
                    "화끈한 한방!", "불타는 크리티컬!", "시원한 타격!",
                    "폭발적인 일격!", "열정의 크리티컬!", "드디어 제대로!",
                    "시원하게 박았어!"
                ],
                CharacterPersonality.WISE: [
                    "경험이 빛을 발했다.", "정확한 타이밍이었다.", "수련의 결과다.",
                    "지혜로운 공격.", "현명한 타이밍.", "경험의 가치.",
                    "깊이 있는 공격이었다.", "오랜 수련의 결실.", "지식이 힘이 되었다.",
                    "현명한 판단의 결과."
                ],
                CharacterPersonality.BALANCED: [
                    "좋은 타격이었어요.", "적절한 크리티컬이네요.", "잘 맞았어요.",
                    "균형잡힌 공격이었어요.", "적당히 잘 됐네요.", "괜찮은 결과예요.",
                    "적절한 타이밍이었어요.", "좋은 성과네요."
                ]
            },
            "near_death": {
                CharacterPersonality.CHEERFUL: [
                    "아직... 포기할 순 없어!", "조금만 더 버텨보자!", "희망을 잃지 말자!",
                    "우리 함께 이겨내자!", "아직 끝나지 않았어!", "최선을 다해보자!",
                    "포기하면 안 돼!", "모두를 위해 버텨보자!", "희망은 있어!",
                    "마지막까지 웃으며 가자!"
                ],
                CharacterPersonality.SERIOUS: [
                    "위험한 상황이다.", "신중해야겠다.", "전략적 후퇴를 고려하자.",
                    "상황을 재평가해야 한다.", "보다 조심스럽게 행동하자.", "계획을 수정해야겠다.",
                    "리스크 관리가 필요하다.", "안전 우선으로 행동하자.", "전술을 바꿔야겠다.",
                    "냉정한 판단이 필요하다."
                ],
                CharacterPersonality.GENTLE: [
                    "죄송해요... 제가 부족해서...", "걱정 끼쳐드려서 미안해요.", "조심해야겠어요.",
                    "다른 분들에게 피해를 주고 있네요.", "더 조심스럽게 행동할게요.", "미안해요, 모두...",
                    "제가 더 신중했어야 했는데...", "다들 무사하시길...", "저 때문에 걱정 마세요.",
                    "다음엔 더 조심할게요."
                ],
                CharacterPersonality.COLD: [
                    "...위험하다.", "한계에 왔다.", "...조심하자.",
                    "...상황이 나쁘다.", "위기다.", "...철수.",
                    "한계.", "...주의.", "위험.",
                    "...심각하다."
                ],
                CharacterPersonality.PLAYFUL: [
                    "이런! 스릴 있긴 하지만...", "위험한 게임이 됐네!", "조심해야겠어!",
                    "게임 오버는 싫어!", "이건 너무 위험한 놀이야!", "살짝 무서워졌어!",
                    "재밌긴 하지만 위험해!", "이런 스릴은 싫어!", "게임 난이도가 너무 높아!",
                    "조금 더 안전하게 놀자!"
                ],
                CharacterPersonality.MYSTERIOUS: [
                    "죽음이 손짓하고 있다.", "운명의 갈림길에 섰군.", "아직 때가 아니다.",
                    "별들이 경고하고 있다.", "운명의 시험인가.", "죽음의 그림자가 드리워졌다.",
                    "우주가 시련을 주는군.", "별자리가 어두워졌다.", "운명이 흔들리고 있다.",
                    "신비로운 힘이 시험하고 있다."
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    "젠장! 이런 상황이!", "화나지만... 조심해야겠어!", "아직 끝나지 않았어!",
                    "이런 식으로는 안 돼!", "분하지만 물러서야겠어!", "제대로 싸우지도 못하고!",
                    "화나는 상황이야!", "이런 건 싫어!", "더 강해져야 해!",
                    "이런 위험은 질색이야!"
                ],
                CharacterPersonality.WISE: [
                    "위험한 순간이다.", "신중한 판단이 필요하다.", "경험을 살려 행동하자.",
                    "지혜롭게 대처해야 한다.", "현명한 선택이 필요하다.", "깊이 생각해봐야겠다.",
                    "경험이 말해주는 위험 신호다.", "지혜로운 후퇴가 때로는 승리다.", "현명한 자는 위험을 안다.",
                    "오랜 경험이 경고하고 있다."
                ],
                CharacterPersonality.BALANCED: [
                    "위험한 상황이네요.", "조심해야겠어요.", "적절한 대응이 필요해요.",
                    "균형을 잃지 말고 가야겠어요.", "신중하게 행동해야겠어요.", "적당히 조심해야겠네요.",
                    "무리하지 않는 게 좋겠어요.", "안전하게 가봐요."
                ]
            },
            "item_discovery": {
                CharacterPersonality.CHEERFUL: [
                    "오! 뭔가 발견했어!", "아이템이다! 운이 좋네!", "신나는 발견이야!",
                    "와! 보물이다!", "완전 럭키!", "멋진 발견이네!",
                    "오예! 좋은 게 나왔어!", "잭팟이야!", "이런 기분 좋은 발견!",
                    "우리 운이 좋네!"
                ],
                CharacterPersonality.SERIOUS: [
                    "아이템을 발견했다.", "유용할 것 같다.", "확인해보자.",
                    "전략적으로 도움이 될 것이다.", "효율적인 발견이다.", "분석해보자.",
                    "계획에 도움이 되겠다.", "실용적인 발견이다.", "검토가 필요하다.",
                    "전술적 가치가 있다."
                ],
                CharacterPersonality.GENTLE: [
                    "뭔가 있어요.", "도움이 될까요?", "함께 확인해봐요.",
                    "소중한 발견이네요.", "조심스럽게 확인해봐요.", "모두에게 도움이 될 것 같아요.",
                    "다행히 좋은 걸 찾았네요.", "함께 나눠요.", "소중히 사용해야겠어요.",
                    "감사한 발견이에요."
                ],
                CharacterPersonality.COLD: [
                    "아이템.", "...발견.", "확인하자.",
                    "...쓸만하다.", "가져가자.", "...괜찮다.",
                    "유용하다.", "...봐두자.", "필요하다.",
                    "...가치있다."
                ],
                CharacterPersonality.PLAYFUL: [
                    "오! 보물찾기 성공!", "재밌는 발견!", "뭔지 궁금해!",
                    "완전 쿨한 아이템!", "이런 걸 찾는 재미!", "신나는 서프라이즈!",
                    "오예! 숨겨진 보물!", "게임 같아서 재밌어!", "완전 대박 발견!",
                    "이런 게 모험의 재미지!"
                ],
                CharacterPersonality.MYSTERIOUS: [
                    "운명이 준 선물인가.", "별들이 인도한 발견.", "예정된 보상.",
                    "우주의 뜻이 담긴 물건.", "신비로운 발견이군.", "운명적인 만남.",
                    "별자리가 알려준 보물.", "숙명적인 발견.", "시공이 남긴 흔적.",
                    "예언된 아이템인가."
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    "오! 뭔가 있어!", "발견했다!", "이거 쓸만하겠는데!",
                    "좋은 거 나왔네!", "드디어 찾았어!", "시원한 발견이야!",
                    "완전 대박!", "이런 걸 찾았다!", "열정적인 발견!",
                    "불타는 보물찾기!"
                ],
                CharacterPersonality.WISE: [
                    "지혜로운 발견이다.", "경험이 알려준 보물.", "현명한 탐색의 결과.",
                    "깊이 있는 발견이군.", "지식의 가치를 아는 아이템.", "현명한 선택이었다.",
                    "경험이 쌓인 결과다.", "지혜로운 눈이 찾아낸 보물.", "깨달음의 선물.",
                    "오랜 경험이 알려준 가치."
                ],
                CharacterPersonality.BALANCED: [
                    "좋은 걸 찾았네요.", "도움이 될 것 같아요.", "적절한 발견이에요.",
                    "유용한 아이템이네요.", "다행한 발견이에요.", "적당히 쓸만해요.",
                    "괜찮은 아이템이네요.", "함께 사용해봐요."
                ]
            },
            "combat_victory": {
                CharacterPersonality.CHEERFUL: [
                    "우리가 이겼어!", "야호! 승리다!", "완전 대박!",
                    "최고의 팀워크였어!", "우리 정말 강하네!", "신나는 승리!",
                    "함께 이겨서 더 기뻐!", "완전 최고야!", "승리의 기쁨!",
                    "우리가 해냈어!"
                ],
                CharacterPersonality.SERIOUS: [
                    "전투 종료.", "승리를 확인했다.", "효과적인 전술이었다.",
                    "계획대로 진행됐다.", "성공적인 작전이었다.", "다음 목표로 이동하자.",
                    "전략이 성공했다.", "임무 완수.", "정확한 실행이었다.",
                    "프로페셔널한 승리."
                ],
                CharacterPersonality.GENTLE: [
                    "다행히 모두 무사해요.", "함께해서 이길 수 있었어요.", "모두 고생하셨어요.",
                    "무사히 끝나서 다행이에요.", "서로 도와서 이겼네요.", "안전하게 이겨서 좋아요.",
                    "다치신 분은 없으시죠?", "조심스럽게 이겼어요.", "모두 덕분이에요.",
                    "함께라서 가능했어요."
                ],
                CharacterPersonality.COLD: [
                    "승리.", "...끝났다.", "다음.",
                    "완료.", "...성공.", "계속하자.",
                    "정리됐다.", "...만족.", "결과 확인.",
                    "...좋다."
                ],
                CharacterPersonality.PLAYFUL: [
                    "게임 클리어!", "완전 재밌었어!", "우리가 주인공이야!",
                    "멋진 승리 쇼!", "완전 쿨해!", "다음 스테이지!",
                    "완전 대박 승리!", "재밌는 전투였어!", "승리 파티!",
                    "최고의 엔터테인먼트!"
                ],
                CharacterPersonality.MYSTERIOUS: [
                    "운명이 우리 편이었다.", "별들이 승리를 예고했다.", "예정된 결과.",
                    "우주의 뜻이었다.", "숙명적인 승리.", "별자리가 축복했다.",
                    "운명의 수레바퀴가 돌았다.", "예언이 성취됐다.", "신비로운 승리.",
                    "우주가 인정한 결과."
                ],
                CharacterPersonality.HOT_TEMPERED: [
                    "시원한 승리야!", "드디어 이겼어!", "불타는 승리!",
                    "열정의 결과다!", "화끈한 전투였어!", "완전 짜릿해!",
                    "시원하게 이겼어!", "폭발적인 승리!", "불타는 열정의 결과!",
                    "드디어 제대로!"
                ],
                CharacterPersonality.WISE: [
                    "지혜로운 승리였다.", "경험이 승리를 이끌었다.", "현명한 전략의 결과.",
                    "깊이 있는 전투였다.", "지식의 힘을 느꼈다.", "배움의 가치를 확인했다.",
                    "현명한 판단이 승리를 만들었다.", "오랜 경험의 결실.", "지혜로운 전술.",
                    "깨달음의 승리."
                ],
                CharacterPersonality.BALANCED: [
                    "좋은 승리였어요.", "적절한 전투였네요.", "균형잡힌 승리예요.",
                    "함께 이겨서 좋아요.", "적당히 잘 끝났네요.", "서로 도와서 이겼어요.",
                    "괜찮은 결과네요.", "안정적인 승리였어요."
                ]
            }
        }
        
        if situation not in situational_dialogues:
            return
        
        # 해당 캐릭터나 AI 동료 중 하나가 반응
        if character and hasattr(character, 'personality'):
            personality = character.personality
            speaker = character
        elif self.ai_companions:
            companion = random.choice(self.ai_companions)
            personality = companion.personality if hasattr(companion, 'personality') else CharacterPersonality.BALANCED
            speaker = companion.character
        else:
            return
        
        # 안전한 기본 대사 풀
        default_dialogues = {
            "level_up": ["레벨업했네요.", "조금 더 강해진 것 같아요.", "성장했어요.", "좋은 결과네요."],
            "critical_hit": ["좋은 타격이었어요.", "잘 맞았네요.", "효과적이었어요.", "성공적이었어요."],
            "near_death": ["조심해야겠어요.", "위험한 상황이네요.", "신중하게 해야겠어요.", "무리하지 마세요."],
            "item_discovery": ["뭔가 발견했어요.", "아이템이 있네요.", "좋은 발견이에요.", "도움이 될 것 같아요."],
            "combat_victory": ["승리했네요.", "잘 끝났어요.", "좋은 결과예요.", "함께 이겨서 좋아요."]
        }
        
        dialogues = situational_dialogues[situation].get(personality, 
                                                      default_dialogues.get(situation, ["..."]))
        dialogue = random.choice(dialogues)
        
        print(f"\n💬 {speaker.name}: \"{dialogue}\"")
        time.sleep(1.5)
    
    def get_contextual_dialogue(self, character: Character, context: str, **kwargs) -> str:
        """상황에 맞는 대화 반환"""
        personality = getattr(character, 'personality', CharacterPersonality.BALANCED)
        
        # 기본 성격별 대화
        if context in CharacterTraits.PERSONALITY_DIALOGUE.get(personality, {}):
            return CharacterTraits.get_dialogue(personality, context)
        
        # 직업별 특수 대화
        character_class = getattr(character, 'character_class', '전사')
        if character_class in CharacterTraits.CLASS_SPECIFIC_DIALOGUE:
            class_dialogues = CharacterTraits.CLASS_SPECIFIC_DIALOGUE[character_class]
            if context in class_dialogues:
                return random.choice(class_dialogues[context])
        
        # 기본 응답
        return "..."
    
    def initialize_character_personalities(self, party: List[Character]):
        """파티원들의 성격 초기화 (이름 기반)"""
        for character in party:
            if not hasattr(character, 'personality'):
                # 이름으로 성별 확인
                character.gender = CharacterTraits.get_gender_from_name(character.name)
                
                # 직업 기반 성격 확률 계산
                character_class = getattr(character, 'character_class', '전사')
                personality = self._get_personality_by_class_probability(character_class)
                character.personality = personality
                
                print(f"✨ {character.name}의 성격: {personality.value} (성별: {character.gender.value})")
    
    def _get_personality_by_class_probability(self, character_class: str) -> CharacterPersonality:
        """직업별 성격 확률에 따른 성격 결정 (업데이트된 확률)"""
        
        # 28개 직업별 성격 확률 분포 (각 직업마다 100% 총합, 최소 1% 보장)
        class_personality_weights = {
            # 물리 근접 계열
            "전사": {
                CharacterPersonality.HOT_TEMPERED: 25,
                CharacterPersonality.SERIOUS: 20,
                CharacterPersonality.BALANCED: 15,
                CharacterPersonality.CHEERFUL: 12,
                CharacterPersonality.WISE: 8,
                CharacterPersonality.COLD: 7,
                CharacterPersonality.GENTLE: 5,
                CharacterPersonality.MYSTERIOUS: 4,
                CharacterPersonality.PLAYFUL: 4
            },
            "기사": {
                CharacterPersonality.SERIOUS: 30,
                CharacterPersonality.WISE: 20,
                CharacterPersonality.BALANCED: 15,
                CharacterPersonality.GENTLE: 10,
                CharacterPersonality.HOT_TEMPERED: 8,
                CharacterPersonality.CHEERFUL: 6,
                CharacterPersonality.COLD: 5,
                CharacterPersonality.MYSTERIOUS: 3,
                CharacterPersonality.PLAYFUL: 3
            },
            "성기사": {
                CharacterPersonality.WISE: 25,
                CharacterPersonality.SERIOUS: 20,
                CharacterPersonality.GENTLE: 18,
                CharacterPersonality.BALANCED: 12,
                CharacterPersonality.CHEERFUL: 8,
                CharacterPersonality.HOT_TEMPERED: 6,
                CharacterPersonality.MYSTERIOUS: 5,
                CharacterPersonality.COLD: 3,
                CharacterPersonality.PLAYFUL: 3
            },
            "암흑기사": {
                CharacterPersonality.COLD: 25,
                CharacterPersonality.MYSTERIOUS: 20,
                CharacterPersonality.SERIOUS: 18,
                CharacterPersonality.HOT_TEMPERED: 12,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.WISE: 6,
                CharacterPersonality.CHEERFUL: 4,
                CharacterPersonality.GENTLE: 4,
                CharacterPersonality.PLAYFUL: 3
            },
            "용기사": {
                CharacterPersonality.HOT_TEMPERED: 30,
                CharacterPersonality.WISE: 15,
                CharacterPersonality.SERIOUS: 15,
                CharacterPersonality.MYSTERIOUS: 12,
                CharacterPersonality.BALANCED: 10,
                CharacterPersonality.CHEERFUL: 6,
                CharacterPersonality.COLD: 5,
                CharacterPersonality.GENTLE: 4,
                CharacterPersonality.PLAYFUL: 3
            },
            "검성": {
                CharacterPersonality.WISE: 30,
                CharacterPersonality.SERIOUS: 25,
                CharacterPersonality.COLD: 15,
                CharacterPersonality.MYSTERIOUS: 10,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.HOT_TEMPERED: 5,
                CharacterPersonality.GENTLE: 3,
                CharacterPersonality.CHEERFUL: 2,
                CharacterPersonality.PLAYFUL: 2
            },
            "사무라이": {
                CharacterPersonality.SERIOUS: 25,
                CharacterPersonality.WISE: 20,
                CharacterPersonality.HOT_TEMPERED: 15,
                CharacterPersonality.COLD: 12,
                CharacterPersonality.BALANCED: 10,
                CharacterPersonality.MYSTERIOUS: 8,
                CharacterPersonality.GENTLE: 5,
                CharacterPersonality.CHEERFUL: 3,
                CharacterPersonality.PLAYFUL: 2
            },
            "검투사": {
                CharacterPersonality.HOT_TEMPERED: 35,
                CharacterPersonality.PLAYFUL: 20,
                CharacterPersonality.CHEERFUL: 15,
                CharacterPersonality.SERIOUS: 10,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.COLD: 5,
                CharacterPersonality.WISE: 3,
                CharacterPersonality.MYSTERIOUS: 2,
                CharacterPersonality.GENTLE: 2
            },
            "광전사": {
                CharacterPersonality.HOT_TEMPERED: 40,
                CharacterPersonality.COLD: 15,
                CharacterPersonality.PLAYFUL: 12,
                CharacterPersonality.SERIOUS: 10,
                CharacterPersonality.MYSTERIOUS: 8,
                CharacterPersonality.BALANCED: 6,
                CharacterPersonality.CHEERFUL: 4,
                CharacterPersonality.WISE: 3,
                CharacterPersonality.GENTLE: 2
            },
            "몽크": {
                CharacterPersonality.WISE: 30,
                CharacterPersonality.BALANCED: 20,
                CharacterPersonality.GENTLE: 15,
                CharacterPersonality.SERIOUS: 12,
                CharacterPersonality.MYSTERIOUS: 10,
                CharacterPersonality.COLD: 5,
                CharacterPersonality.CHEERFUL: 4,
                CharacterPersonality.HOT_TEMPERED: 2,
                CharacterPersonality.PLAYFUL: 2
            },
            
            # 원거리 물리 계열
            "궁수": {
                CharacterPersonality.COLD: 25,
                CharacterPersonality.SERIOUS: 20,
                CharacterPersonality.BALANCED: 15,
                CharacterPersonality.WISE: 12,
                CharacterPersonality.CHEERFUL: 10,
                CharacterPersonality.GENTLE: 8,
                CharacterPersonality.MYSTERIOUS: 5,
                CharacterPersonality.PLAYFUL: 3,
                CharacterPersonality.HOT_TEMPERED: 2
            },
            "도적": {
                CharacterPersonality.COLD: 25,
                CharacterPersonality.MYSTERIOUS: 20,
                CharacterPersonality.PLAYFUL: 15,
                CharacterPersonality.SERIOUS: 12,
                CharacterPersonality.BALANCED: 10,
                CharacterPersonality.HOT_TEMPERED: 8,
                CharacterPersonality.WISE: 5,
                CharacterPersonality.CHEERFUL: 3,
                CharacterPersonality.GENTLE: 2
            },
            "암살자": {
                CharacterPersonality.COLD: 35,
                CharacterPersonality.MYSTERIOUS: 25,
                CharacterPersonality.SERIOUS: 15,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.WISE: 6,
                CharacterPersonality.HOT_TEMPERED: 4,
                CharacterPersonality.PLAYFUL: 3,
                CharacterPersonality.GENTLE: 2,
                CharacterPersonality.CHEERFUL: 2
            },
            "해적": {
                CharacterPersonality.PLAYFUL: 30,
                CharacterPersonality.HOT_TEMPERED: 25,
                CharacterPersonality.CHEERFUL: 15,
                CharacterPersonality.COLD: 10,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.SERIOUS: 5,
                CharacterPersonality.MYSTERIOUS: 3,
                CharacterPersonality.WISE: 2,
                CharacterPersonality.GENTLE: 2
            },
            
            # 마법 계열
            "아크메이지": {
                CharacterPersonality.WISE: 30,
                CharacterPersonality.SERIOUS: 20,
                CharacterPersonality.COLD: 15,
                CharacterPersonality.MYSTERIOUS: 12,
                CharacterPersonality.BALANCED: 10,
                CharacterPersonality.GENTLE: 5,
                CharacterPersonality.CHEERFUL: 4,
                CharacterPersonality.HOT_TEMPERED: 2,
                CharacterPersonality.PLAYFUL: 2
            },
            "네크로맨서": {
                CharacterPersonality.COLD: 30,
                CharacterPersonality.MYSTERIOUS: 25,
                CharacterPersonality.SERIOUS: 15,
                CharacterPersonality.WISE: 10,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.HOT_TEMPERED: 5,
                CharacterPersonality.GENTLE: 3,
                CharacterPersonality.PLAYFUL: 2,
                CharacterPersonality.CHEERFUL: 2
            },
            "정령술사": {
                CharacterPersonality.MYSTERIOUS: 25,
                CharacterPersonality.GENTLE: 20,
                CharacterPersonality.WISE: 15,
                CharacterPersonality.CHEERFUL: 12,
                CharacterPersonality.BALANCED: 10,
                CharacterPersonality.SERIOUS: 8,
                CharacterPersonality.PLAYFUL: 5,
                CharacterPersonality.COLD: 3,
                CharacterPersonality.HOT_TEMPERED: 2
            },
            "시간술사": {
                CharacterPersonality.MYSTERIOUS: 35,
                CharacterPersonality.WISE: 20,
                CharacterPersonality.COLD: 15,
                CharacterPersonality.SERIOUS: 12,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.GENTLE: 4,
                CharacterPersonality.CHEERFUL: 3,
                CharacterPersonality.PLAYFUL: 2,
                CharacterPersonality.HOT_TEMPERED: 1
            },
            "차원술사": {
                CharacterPersonality.MYSTERIOUS: 40,
                CharacterPersonality.COLD: 20,
                CharacterPersonality.WISE: 15,
                CharacterPersonality.SERIOUS: 10,
                CharacterPersonality.BALANCED: 6,
                CharacterPersonality.HOT_TEMPERED: 4,
                CharacterPersonality.PLAYFUL: 2,
                CharacterPersonality.GENTLE: 2,
                CharacterPersonality.CHEERFUL: 1
            },
            "연금술사": {
                CharacterPersonality.WISE: 25,
                CharacterPersonality.SERIOUS: 20,
                CharacterPersonality.CHEERFUL: 15,
                CharacterPersonality.BALANCED: 12,
                CharacterPersonality.PLAYFUL: 10,
                CharacterPersonality.GENTLE: 8,
                CharacterPersonality.MYSTERIOUS: 5,
                CharacterPersonality.COLD: 3,
                CharacterPersonality.HOT_TEMPERED: 2
            },
            "마검사": {
                CharacterPersonality.SERIOUS: 25,
                CharacterPersonality.COLD: 20,
                CharacterPersonality.WISE: 15,
                CharacterPersonality.HOT_TEMPERED: 12,
                CharacterPersonality.MYSTERIOUS: 10,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.CHEERFUL: 5,
                CharacterPersonality.GENTLE: 3,
                CharacterPersonality.PLAYFUL: 2
            },
            "기계공학자": {
                CharacterPersonality.SERIOUS: 30,
                CharacterPersonality.WISE: 20,
                CharacterPersonality.COLD: 15,
                CharacterPersonality.BALANCED: 12,
                CharacterPersonality.PLAYFUL: 8,
                CharacterPersonality.CHEERFUL: 6,
                CharacterPersonality.MYSTERIOUS: 4,
                CharacterPersonality.GENTLE: 3,
                CharacterPersonality.HOT_TEMPERED: 2
            },
            
            # 지원 계열
            "바드": {
                CharacterPersonality.CHEERFUL: 30,
                CharacterPersonality.PLAYFUL: 20,
                CharacterPersonality.GENTLE: 15,
                CharacterPersonality.BALANCED: 12,
                CharacterPersonality.WISE: 8,
                CharacterPersonality.SERIOUS: 6,
                CharacterPersonality.MYSTERIOUS: 4,
                CharacterPersonality.HOT_TEMPERED: 3,
                CharacterPersonality.COLD: 2
            },
            "신관": {
                CharacterPersonality.GENTLE: 30,
                CharacterPersonality.WISE: 25,
                CharacterPersonality.SERIOUS: 15,
                CharacterPersonality.BALANCED: 10,
                CharacterPersonality.MYSTERIOUS: 8,
                CharacterPersonality.CHEERFUL: 5,
                CharacterPersonality.COLD: 3,
                CharacterPersonality.PLAYFUL: 2,
                CharacterPersonality.HOT_TEMPERED: 2
            },
            "드루이드": {
                CharacterPersonality.WISE: 25,
                CharacterPersonality.GENTLE: 20,
                CharacterPersonality.MYSTERIOUS: 15,
                CharacterPersonality.BALANCED: 12,
                CharacterPersonality.CHEERFUL: 10,
                CharacterPersonality.SERIOUS: 8,
                CharacterPersonality.COLD: 5,
                CharacterPersonality.PLAYFUL: 3,
                CharacterPersonality.HOT_TEMPERED: 2
            },
            "무당": {
                CharacterPersonality.MYSTERIOUS: 30,
                CharacterPersonality.WISE: 20,
                CharacterPersonality.GENTLE: 15,
                CharacterPersonality.SERIOUS: 10,
                CharacterPersonality.BALANCED: 8,
                CharacterPersonality.CHEERFUL: 7,
                CharacterPersonality.COLD: 5,
                CharacterPersonality.PLAYFUL: 3,
                CharacterPersonality.HOT_TEMPERED: 2
            },
            
            # 특수 계열
            "철학자": {
                CharacterPersonality.WISE: 40,
                CharacterPersonality.SERIOUS: 20,
                CharacterPersonality.BALANCED: 12,
                CharacterPersonality.MYSTERIOUS: 10,
                CharacterPersonality.GENTLE: 8,
                CharacterPersonality.COLD: 5,
                CharacterPersonality.CHEERFUL: 3,
                CharacterPersonality.PLAYFUL: 1,
                CharacterPersonality.HOT_TEMPERED: 1
            }
        }
        
        # 기본 가중치 (만약 직업이 없는 경우)
        default_weights = {
            CharacterPersonality.BALANCED: 30,
            CharacterPersonality.CHEERFUL: 15,
            CharacterPersonality.SERIOUS: 15,
            CharacterPersonality.GENTLE: 10,
            CharacterPersonality.WISE: 10,
            CharacterPersonality.COLD: 8,
            CharacterPersonality.PLAYFUL: 5,
            CharacterPersonality.MYSTERIOUS: 4,
            CharacterPersonality.HOT_TEMPERED: 3
        }
        
        weights = class_personality_weights.get(character_class, default_weights)
        
        # 가중치 기반 랜덤 선택
        personalities = list(weights.keys())
        weight_values = [weights[p] for p in personalities]
        
        return random.choices(personalities, weights=weight_values, k=1)[0]
    
    def _handle_ai_requests(self):
        """AI 요청 처리"""
        if not self.pending_ai_requests:
            print("❌ 처리할 AI 요청이 없습니다.")
            return "defend", {}
        
        print(f"\n💬 AI 요청 목록 ({len(self.pending_ai_requests)}개):")
        for i, request in enumerate(self.pending_ai_requests, 1):
            print(f"{i}. {request['message']}")
        
        try:
            choice = int(input("처리할 요청 선택 (0: 모두 거절): "))
            if choice == 0:
                print("모든 AI 요청을 거절했습니다.")
                self.pending_ai_requests.clear()
                return "defend", {}
            elif 1 <= choice <= len(self.pending_ai_requests):
                selected_request = self.pending_ai_requests[choice - 1]
                self.pending_ai_requests.remove(selected_request)
                
                # 요청 처리
                return self._process_ai_request(selected_request)
            else:
                print("❌ 잘못된 선택입니다.")
                return "defend", {}
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return "defend", {}
    
    def _process_ai_request(self, request: Dict) -> Tuple[str, Dict]:
        """AI 요청 처리 실행"""
        request_type = request["type"]
        companion = request["companion"]
        
        if request_type == "item_request":
            # 아이템 공유 요청
            print(f"✅ {companion.character.name}에게 아이템을 공유합니다.")
            return "share_item", {"target": companion.character}
        
        elif request_type == "coordination_request":
            # 협동 공격 요청
            print(f"✅ {companion.character.name}과(와) 협동 공격을 준비합니다.")
            companion.coordinated_attack_ready = True
            return "prepare_coordination", {"partner": companion.character}
        
        elif request_type == "retreat_suggestion":
            # 후퇴 제안
            print(f"✅ {companion.character.name}의 제안에 따라 전략적 후퇴를 고려합니다.")
            return "retreat", {}
        
        elif request_type == "skill_suggestion":
            # 스킬 사용 제안
            print(f"✅ {companion.character.name}의 제안을 받아들입니다.")
            return "skill", {"suggested_by": companion.character}
        
        return "defend", {}
    
    def _get_action_description(self, action_type: str, action_data: Dict) -> str:
        """AI 행동 설명 반환"""
        descriptions = {
            "attack": "적을 공격한다",
            "skill": "스킬을 사용한다",
            "heal": "회복 마법을 사용한다",
            "defend": "방어 자세를 취한다",
            "item": "아이템을 사용한다",
            "coordinated_attack": "협동 공격을 시도한다",
            "retreat": "전략적으로 후퇴한다"
        }
        
        base_description = descriptions.get(action_type, "행동을 취한다")
        
        # 대상이 있는 경우 추가 정보
        if "target" in action_data:
            target = action_data["target"]
            base_description += f" (대상: {target.name})"
        
        return base_description
    
    def _show_party_status(self, party: List[Character]):
        """파티 상태 표시"""
        print(f"\n📊 파티 상태:")
        print("=" * 50)
        
        for i, character in enumerate(party, 1):
            status_icon = "🎮" if character in self.player_controlled_characters else "🤖"
            personality_text = ""
            
            if hasattr(character, 'personality'):
                personality_text = f" ({character.personality.value})"
            
            print(f"{i}. {status_icon} {character.name}{personality_text}")
            print(f"   Lv.{character.level} {character.character_class}")
            print(f"   HP: {character.current_hp}/{character.max_hp}")
            print(f"   MP: {character.current_mp}/{character.max_mp}")
            
            # 상태 이상이 있다면 표시
            if hasattr(character, 'status_effects') and character.status_effects:
                effects = ", ".join(character.status_effects.keys())
                print(f"   상태: {effects}")
            
            print()
        
        print("=" * 50)
        print(f"조작 방식: {self.current_mode.value}")
        print(f"플레이어 조작: {len(self.player_controlled_characters)}명")
        print(f"AI 조작: {len(self.ai_companions)}명")
        
        if self.pending_ai_requests:
            print(f"대기 중인 AI 요청: {len(self.pending_ai_requests)}개")

# 테스트 함수들
def test_ai_personality_system():
    """AI 성격 시스템 테스트"""
    print("🧪 AI 성격 시스템 테스트 시작...")
    
    # 모든 직업에 대해 성격 분포 테스트
    classes_to_test = [
        "전사", "기사", "성기사", "암흑기사", "용기사", "검성", "사무라이", "검투사", "광전사", "몽크",
        "궁수", "도적", "암살자", "해적", "아크메이지", "네크로맨서", "정령술사", "시간술사", 
        "차원술사", "연금술사", "마검사", "기계공학자", "바드", "신관", "드루이드", "무당", "철학자"
    ]
    
    for character_class in classes_to_test:
        print(f"\n📊 {character_class} 성격 분포 테스트 (1000회 샘플링):")
        
        personality_counts = {}
        for _ in range(1000):
            personality = ai_game_mode_manager._get_personality_by_class_probability(character_class)
            personality_counts[personality] = personality_counts.get(personality, 0) + 1
        
        # 결과 출력 (확률 순 정렬)
        sorted_results = sorted(personality_counts.items(), key=lambda x: x[1], reverse=True)
        for personality, count in sorted_results:
            percentage = (count / 1000) * 100
            print(f"   {personality.value}: {percentage:.1f}%")
    
    print("\n✅ AI 성격 시스템 테스트 완료!")


def test_dialogue_system():
    """AI 대화 시스템 테스트"""
    print("🎭 AI 대화 시스템 테스트 시작...")
    
    # 각 성격별 대화 테스트
    for personality in CharacterPersonality:
        print(f"\n🎪 {personality.value} 성격 대화 테스트:")
        
        # 다양한 상황별 대화 테스트
        situations = ["greeting", "battle_start", "victory", "low_hp", "praise", "thanks"]
        
        for situation in situations[:3]:  # 처음 3개만 테스트
            try:
                dialogue = CharacterTraits.get_dialogue(personality, situation)
                print(f"   {situation}: \"{dialogue}\"")
            except:
                print(f"   {situation}: 대화 없음")
    
    print("\n✅ AI 대화 시스템 테스트 완료!")


if __name__ == "__main__":
    # 시스템 테스트 실행
    test_ai_personality_system()
    test_dialogue_system()
    
    print("\n" + "="*60)
    print("🎮 AI 게임모드 시스템 완료!")
    print("   ✅ 9가지 성격 시스템")
    print("   ✅ 28개 직업별 성격 확률 분포")
    print("   ✅ 1500+ 개의 대화 라인")
    print("   ✅ 성별 기반 이름 시스템")
    print("   ✅ 협동 공격 시스템")
    print("   ✅ 필드 대화 시스템")
    print("   ✅ 파티 인카운터 시스템")
    print("   ✅ 장비 내구도 시스템")
    print("   ✅ 장비 강화 추천")
    print("   ✅ 스마트 장비 추천")
    print("   ✅ 전투 시스템 통합")
    print("="*60)

# 기본 게임모드용 장비 자동 장착 시스템
class BasicEquipmentManager:
    """기본 게임모드용 장비 자동 장착 및 추천 시스템"""
    
    def __init__(self):
        # 모든 직업별 장비 우선순위 (28개 직업 포함)
        self.class_equipment_priority = {
            # 근접 전투 직업
            '전사': {'weapon': 1.2, 'armor': 1.1, 'shield': 1.0, 'boots': 0.9, 'gloves': 0.8, 'accessory': 0.7},
            '기사': {'weapon': 1.1, 'armor': 1.2, 'shield': 1.1, 'helmet': 1.0, 'boots': 0.9, 'accessory': 0.8},
            '성기사': {'weapon': 1.0, 'armor': 1.2, 'shield': 1.1, 'helmet': 1.0, 'accessory': 0.9, 'boots': 0.8},
            '암흑기사': {'weapon': 1.1, 'armor': 1.1, 'helmet': 1.0, 'gloves': 0.9, 'boots': 0.8, 'accessory': 1.0},
            '용기사': {'weapon': 1.2, 'armor': 1.1, 'helmet': 1.0, 'boots': 0.9, 'gloves': 0.8, 'accessory': 0.9},
            '검성': {'weapon': 1.3, 'armor': 1.0, 'gloves': 1.0, 'boots': 0.9, 'accessory': 0.8, 'helmet': 0.7},
            '사무라이': {'weapon': 1.2, 'armor': 1.0, 'gloves': 1.1, 'boots': 1.0, 'helmet': 0.9, 'accessory': 0.8},
            '검투사': {'weapon': 1.2, 'armor': 0.9, 'gloves': 1.1, 'boots': 1.0, 'helmet': 0.8, 'accessory': 0.8},
            '광전사': {'weapon': 1.3, 'armor': 0.8, 'gloves': 1.0, 'boots': 0.9, 'helmet': 0.7, 'accessory': 0.7},
            '몽크': {'weapon': 0.8, 'gloves': 1.3, 'boots': 1.1, 'armor': 0.9, 'accessory': 1.0, 'helmet': 0.7},
            
            # 원거리 전투 직업
            '궁수': {'weapon': 1.3, 'boots': 1.1, 'gloves': 1.0, 'armor': 0.8, 'helmet': 0.8, 'accessory': 0.9},
            '도적': {'weapon': 1.2, 'boots': 1.2, 'gloves': 1.1, 'armor': 0.7, 'helmet': 0.7, 'accessory': 1.0},
            '암살자': {'weapon': 1.3, 'boots': 1.2, 'gloves': 1.1, 'armor': 0.6, 'accessory': 1.1, 'helmet': 0.6},
            '해적': {'weapon': 1.2, 'boots': 1.0, 'gloves': 1.0, 'armor': 0.8, 'accessory': 1.1, 'helmet': 0.7},
            
            # 마법 직업
            '아크메이지': {'weapon': 1.2, 'accessory': 1.2, 'armor': 0.8, 'helmet': 0.9, 'boots': 0.8, 'gloves': 0.9},
            '네크로맨서': {'weapon': 1.1, 'accessory': 1.3, 'armor': 0.8, 'helmet': 0.9, 'boots': 0.8, 'gloves': 0.9},
            '정령술사': {'weapon': 1.1, 'accessory': 1.2, 'armor': 0.9, 'helmet': 0.9, 'boots': 0.9, 'gloves': 0.8},
            '시간술사': {'weapon': 1.0, 'accessory': 1.3, 'armor': 0.8, 'helmet': 0.9, 'boots': 0.9, 'gloves': 0.9},
            '차원술사': {'weapon': 1.1, 'accessory': 1.3, 'armor': 0.7, 'helmet': 0.8, 'boots': 1.0, 'gloves': 0.9},
            '연금술사': {'weapon': 1.0, 'accessory': 1.1, 'armor': 0.9, 'helmet': 0.9, 'gloves': 1.1, 'boots': 0.8},
            
            # 하이브리드 직업
            '마검사': {'weapon': 1.2, 'armor': 1.0, 'accessory': 1.1, 'gloves': 1.0, 'boots': 0.9, 'helmet': 0.8},
            '기계공학자': {'weapon': 1.1, 'gloves': 1.2, 'armor': 1.0, 'accessory': 1.0, 'helmet': 0.9, 'boots': 0.8},
            
            # 지원 직업
            '바드': {'weapon': 1.0, 'accessory': 1.2, 'armor': 0.9, 'boots': 1.0, 'gloves': 0.9, 'helmet': 0.8},
            '신관': {'weapon': 0.8, 'armor': 1.1, 'accessory': 1.2, 'helmet': 1.0, 'boots': 0.9, 'gloves': 0.8},
            '클레릭': {'weapon': 0.9, 'armor': 1.2, 'accessory': 1.1, 'helmet': 1.0, 'boots': 0.9, 'gloves': 0.8},
            '드루이드': {'weapon': 1.0, 'armor': 1.0, 'accessory': 1.1, 'boots': 1.0, 'gloves': 0.9, 'helmet': 0.8},
            '무당': {'weapon': 0.9, 'accessory': 1.3, 'armor': 0.8, 'helmet': 0.9, 'boots': 0.9, 'gloves': 1.0},
            '철학자': {'weapon': 0.7, 'accessory': 1.3, 'armor': 0.9, 'helmet': 1.0, 'boots': 0.9, 'gloves': 0.9}
        }
        
        # 스탯 우선순위 (직업별)
        self.class_stat_priority = {
            # 물리 공격 직업
            '전사': {'attack_power': 1.2, 'physical_defense': 1.1, 'hp': 1.0, 'accuracy': 0.9},
            '기사': {'physical_defense': 1.2, 'attack_power': 1.1, 'hp': 1.1, 'accuracy': 0.9},
            '성기사': {'physical_defense': 1.2, 'hp': 1.1, 'attack_power': 1.0, 'magic_defense': 1.0},
            '암흑기사': {'attack_power': 1.1, 'magic_power': 1.0, 'physical_defense': 1.0, 'hp': 1.0},
            '용기사': {'attack_power': 1.2, 'physical_defense': 1.0, 'hp': 1.1, 'speed': 0.9},
            '검성': {'attack_power': 1.3, 'accuracy': 1.1, 'speed': 1.0, 'physical_defense': 0.9},
            '사무라이': {'attack_power': 1.2, 'accuracy': 1.1, 'speed': 1.0, 'physical_defense': 1.0},
            '검투사': {'attack_power': 1.2, 'speed': 1.1, 'accuracy': 1.0, 'physical_defense': 0.9},
            '광전사': {'attack_power': 1.3, 'speed': 1.0, 'accuracy': 0.9, 'physical_defense': 0.8},
            '몽크': {'attack_power': 1.1, 'speed': 1.2, 'accuracy': 1.1, 'physical_defense': 1.0},
            
            # 원거리 공격 직업  
            '궁수': {'attack_power': 1.2, 'accuracy': 1.2, 'speed': 1.1, 'physical_defense': 0.8},
            '도적': {'attack_power': 1.1, 'speed': 1.2, 'accuracy': 1.1, 'evasion': 1.1},
            '암살자': {'attack_power': 1.2, 'speed': 1.2, 'accuracy': 1.2, 'evasion': 1.1},
            '해적': {'attack_power': 1.1, 'speed': 1.0, 'accuracy': 1.0, 'physical_defense': 0.9},
            
            # 마법 직업
            '아크메이지': {'magic_power': 1.3, 'mp': 1.2, 'magic_defense': 1.0, 'accuracy': 1.0},
            '네크로맨서': {'magic_power': 1.2, 'mp': 1.1, 'magic_defense': 1.0, 'speed': 0.9},
            '정령술사': {'magic_power': 1.2, 'mp': 1.1, 'magic_defense': 1.1, 'speed': 1.0},
            '시간술사': {'magic_power': 1.1, 'mp': 1.2, 'speed': 1.1, 'magic_defense': 1.0},
            '차원술사': {'magic_power': 1.2, 'mp': 1.1, 'speed': 1.1, 'evasion': 1.0},
            '연금술사': {'magic_power': 1.1, 'mp': 1.0, 'accuracy': 1.1, 'magic_defense': 1.0},
            
            # 하이브리드 직업
            '마검사': {'attack_power': 1.1, 'magic_power': 1.1, 'mp': 1.0, 'physical_defense': 1.0},
            '기계공학자': {'attack_power': 1.0, 'accuracy': 1.2, 'magic_power': 1.0, 'physical_defense': 1.0},
            
            # 지원 직업
            '바드': {'mp': 1.2, 'magic_power': 1.0, 'speed': 1.1, 'magic_defense': 1.0},
            '신관': {'mp': 1.2, 'magic_power': 1.1, 'magic_defense': 1.1, 'hp': 1.0},
            '클레릭': {'mp': 1.1, 'magic_power': 1.1, 'magic_defense': 1.1, 'hp': 1.0},
            '드루이드': {'mp': 1.1, 'magic_power': 1.0, 'magic_defense': 1.0, 'hp': 1.0},
            '무당': {'magic_power': 1.2, 'mp': 1.1, 'magic_defense': 1.1, 'speed': 1.0},
            '철학자': {'mp': 1.3, 'magic_power': 1.1, 'magic_defense': 1.2, 'speed': 0.9}
        }
    
    def auto_equip_best_items(self, character: Character, inventory_items: List = None) -> List[str]:
        """캐릭터에게 최적의 장비를 자동으로 장착"""
        if not inventory_items:
            return []
        
        character_class = getattr(character, 'character_class', '전사')
        equipped_items = []
        
        try:
            from .items import ItemDatabase
            item_db = ItemDatabase()
            
            # 장비 타입별로 최적의 아이템 찾기
            equipment_slots = ['weapon', 'armor', 'helmet', 'boots', 'gloves', 'shield', 'accessory']
            
            for slot in equipment_slots:
                best_item = self._find_best_item_for_slot(
                    character, slot, inventory_items, item_db
                )
                
                if best_item:
                    success = self._equip_item_to_character(character, best_item, slot)
                    if success:
                        equipped_items.append(f"{slot}: {best_item.name}")
            
            # 장착 결과 출력
            if equipped_items:
                print(f"🎒 {character.name}에게 자동 장착 완료:")
                for item_info in equipped_items:
                    print(f"   ✅ {item_info}")
            
            return equipped_items
            
        except ImportError:
            print("❌ 아이템 시스템을 불러올 수 없습니다.")
            return []
    
    def _find_best_item_for_slot(self, character: Character, slot: str, available_items: List, item_db):
        """특정 슬롯에 최적인 아이템 찾기"""
        character_class = getattr(character, 'character_class', '전사')
        
        # 해당 슬롯에 장착 가능한 아이템들 필터링
        suitable_items = []
        for item_name in available_items:
            item = item_db.get_item(item_name)
            if item and hasattr(item, 'item_type') and item.item_type == 'equipment':
                item_slot = getattr(item, 'equipment_slot', None)
                if item_slot and item_slot.lower() == slot.lower():
                    suitable_items.append(item)
        
        if not suitable_items:
            return None
        
        # 각 아이템의 점수 계산
        best_item = None
        best_score = -1
        
        for item in suitable_items:
            score = self._calculate_item_score(character, item, character_class)
            if score > best_score:
                best_score = score
                best_item = item
        
        return best_item
    
    def _calculate_item_score(self, character: Character, item, character_class: str) -> float:
        """아이템의 캐릭터 적합도 점수 계산"""
        score = 0.0
        
        # 직업별 장비 타입 우선순위 적용
        equipment_priorities = self.class_equipment_priority.get(character_class, {})
        item_slot = getattr(item, 'equipment_slot', 'weapon').lower()
        slot_priority = equipment_priorities.get(item_slot, 1.0)
        
        # 직업별 스탯 우선순위 적용
        stat_priorities = self.class_stat_priority.get(character_class, {})
        
        # 각 스탯 보너스 점수 계산
        stat_bonuses = {
            'attack_power': getattr(item, 'physical_attack_bonus', 0),
            'magic_power': getattr(item, 'magic_attack_bonus', 0),
            'physical_defense': getattr(item, 'physical_defense_bonus', 0),
            'magic_defense': getattr(item, 'magic_defense_bonus', 0),
            'hp': getattr(item, 'hp_bonus', 0),
            'mp': getattr(item, 'mp_bonus', 0),
            'speed': getattr(item, 'speed_bonus', 0),
            'accuracy': getattr(item, 'accuracy_bonus', 0),
            'evasion': getattr(item, 'evasion_bonus', 0)
        }
        
        for stat, bonus in stat_bonuses.items():
            if bonus > 0:
                stat_priority = stat_priorities.get(stat, 0.5)
                score += bonus * stat_priority
        
        # 슬롯 우선순위 적용
        score *= slot_priority
        
        # 아이템 레벨/품질 고려
        item_level = getattr(item, 'level_requirement', 1)
        if item_level <= getattr(character, 'level', 1):
            score *= 1.0  # 적절한 레벨
        else:
            score *= 0.1  # 레벨이 안 맞음
        
        # 내구도 고려
        durability = getattr(item, 'durability', 100)
        score *= (durability / 100.0)
        
        # 강화 수치 고려
        enhancement = getattr(item, 'enhancement_level', 0)
        score *= (1.0 + enhancement * 0.1)
        
        return score
    
    def _equip_item_to_character(self, character: Character, item, slot: str) -> bool:
        """캐릭터에게 아이템 장착"""
        try:
            if not hasattr(character, 'equipped_items'):
                character.equipped_items = {}
            
            # 기존 아이템이 있다면 해제
            old_item = character.equipped_items.get(slot)
            if old_item:
                self._remove_equipment_bonuses(character, old_item)
            
            # 새 아이템 장착
            character.equipped_items[slot] = item
            self._apply_equipment_bonuses(character, item)
            
            return True
        except Exception as e:
            print(f"❌ 장비 장착 실패: {e}")
            return False
    
    def _apply_equipment_bonuses(self, character: Character, item):
        """장비 보너스 적용"""
        bonuses = {
            'physical_attack_bonus': 'attack_power',
            'magic_attack_bonus': 'magic_power', 
            'physical_defense_bonus': 'physical_defense',
            'magic_defense_bonus': 'magic_defense',
            'hp_bonus': 'max_hp',
            'mp_bonus': 'max_mp',
            'speed_bonus': 'speed',
            'accuracy_bonus': 'accuracy',
            'evasion_bonus': 'evasion'
        }
        
        for item_attr, char_attr in bonuses.items():
            bonus = getattr(item, item_attr, 0)
            if bonus > 0:
                current_value = getattr(character, char_attr, 0)
                setattr(character, char_attr, current_value + bonus)
                
                # HP/MP의 경우 현재값도 증가
                if char_attr == 'max_hp':
                    character.current_hp = min(character.current_hp + bonus, character.max_hp)
                elif char_attr == 'max_mp':
                    character.current_mp = min(character.current_mp + bonus, character.max_mp)
    
    def _remove_equipment_bonuses(self, character: Character, item):
        """장비 보너스 제거"""
        bonuses = {
            'physical_attack_bonus': 'attack_power',
            'magic_attack_bonus': 'magic_power',
            'physical_defense_bonus': 'physical_defense', 
            'magic_defense_bonus': 'magic_defense',
            'hp_bonus': 'max_hp',
            'mp_bonus': 'max_mp',
            'speed_bonus': 'speed',
            'accuracy_bonus': 'accuracy',
            'evasion_bonus': 'evasion'
        }
        
        for item_attr, char_attr in bonuses.items():
            bonus = getattr(item, item_attr, 0)
            if bonus > 0:
                current_value = getattr(character, char_attr, 0)
                setattr(character, char_attr, max(0, current_value - bonus))
                
                # HP/MP의 경우 현재값도 조정
                if char_attr == 'max_hp':
                    character.current_hp = min(character.current_hp, character.max_hp)
                elif char_attr == 'max_mp':
                    character.current_mp = min(character.current_mp, character.max_mp)
    
    def get_equipment_recommendations(self, character: Character, available_items: List) -> List[Dict]:
        """캐릭터에게 추천 장비 목록 반환"""
        character_class = getattr(character, 'character_class', '전사')
        recommendations = []
        
        try:
            from .items import ItemDatabase
            item_db = ItemDatabase()
            
            # 각 슬롯별 추천 아이템
            equipment_slots = ['weapon', 'armor', 'helmet', 'boots', 'gloves', 'shield', 'accessory']
            
            for slot in equipment_slots:
                best_items = []
                
                # 해당 슬롯 아이템들 점수 계산
                for item_name in available_items:
                    item = item_db.get_item(item_name)
                    if item and hasattr(item, 'item_type') and item.item_type == 'equipment':
                        item_slot = getattr(item, 'equipment_slot', '').lower()
                        if item_slot == slot:
                            score = self._calculate_item_score(character, item, character_class)
                            best_items.append({
                                'item': item,
                                'score': score,
                                'slot': slot,
                                'reason': self._get_recommendation_reason(character, item, character_class)
                            })
                
                # 상위 3개 추천
                best_items.sort(key=lambda x: x['score'], reverse=True)
                recommendations.extend(best_items[:3])
            
            return recommendations
            
        except ImportError:
            return []
    
    def _get_recommendation_reason(self, character: Character, item, character_class: str) -> str:
        """추천 이유 생성"""
        reasons = []
        
        # 직업 적합성
        if character_class in self.class_equipment_priority:
            item_slot = getattr(item, 'equipment_slot', '').lower()
            priority = self.class_equipment_priority[character_class].get(item_slot, 1.0)
            if priority > 1.0:
                reasons.append(f"{character_class}에게 중요한 장비")
        
        # 스탯 보너스
        high_bonuses = []
        bonuses = {
            'physical_attack_bonus': '물리 공격력',
            'magic_attack_bonus': '마법 공격력',
            'physical_defense_bonus': '물리 방어력', 
            'magic_defense_bonus': '마법 방어력',
            'hp_bonus': 'HP',
            'mp_bonus': 'MP'
        }
        
        for attr, name in bonuses.items():
            bonus = getattr(item, attr, 0)
            if bonus >= 10:  # 높은 보너스
                high_bonuses.append(f"{name} +{bonus}")
        
        if high_bonuses:
            reasons.append(f"높은 보너스: {', '.join(high_bonuses)}")
        
        # 기본 이유
        if not reasons:
            reasons.append("스탯 향상에 도움")
        
        return " | ".join(reasons)

# 전역 장비 관리자 인스턴스
basic_equipment_manager = BasicEquipmentManager()

# AI 요청 처리 함수들
def handle_ai_requests(pending_requests):
    """AI 요청 처리"""
    if not pending_requests:
        print("❌ 처리할 AI 요청이 없습니다.")
        return "defend", {}
    
    print("\n💬 AI 요청 목록:")
    for i, request in enumerate(pending_requests):
        elapsed = time.time() - request["timestamp"]
        print(f"{i+1}. {request['message']} ({elapsed:.1f}초 전)")
    
    print(f"{len(pending_requests)+1}. 무시하고 계속")
    
    try:
        choice = int(input("응답할 요청 선택: ")) - 1
        
        if choice == len(pending_requests):
            # 무시
            return "defend", {}
        elif 0 <= choice < len(pending_requests):
            request = pending_requests.pop(choice)
            return respond_to_ai_request(request)
        else:
            print("❌ 잘못된 선택입니다.")
            return "defend", {}
    except ValueError:
        print("❌ 숫자를 입력해주세요.")
        return "defend", {}

def respond_to_ai_request(request):
    """AI 요청에 응답"""
    request_type = request["type"]
    companion = request["companion"]
    
    print(f"\n💬 {companion.character.name}의 요청: {request['message']}")
    response = input("승인하시겠습니까? (y/n): ").lower() == 'y'
    
    response_msg = companion.respond_to_player_action("help", response)
    print(f"💭 {response_msg}")
    
    if response:
        if request["type"] == "REQUEST_COORDINATED_ATTACK":
            companion.coordinated_attack_ready = True
            return "prepare_coordination", {"partner": companion.character}
        elif request["type"] == "NEED_HEALING":
            return "use_item", {"target": companion.character, "item_type": "healing"}
        elif request["type"] == "NEED_MP_POTION":
            return "use_item", {"target": companion.character, "item_type": "mp_potion"}
    
    return "defend", {}
    
    def _show_party_status(self, party: List[Character]):
        """파티 상태 표시"""
        print(f"\n📊 파티 상태:")
        print("="*60)
        
        for char in party:
            if not char.is_alive:
                continue
            
            hp_bar = self._create_status_bar(char.current_hp, char.max_hp, 15)
            mp_bar = self._create_status_bar(char.current_mp, char.max_mp, 15)
            
            control_type = "🎮 플레이어" if char in self.player_controlled_characters else "🤖 AI"
            
            print(f"{char.name} ({control_type})")
            print(f"  HP: {hp_bar} {char.current_hp}/{char.max_hp}")
            print(f"  MP: {mp_bar} {char.current_mp}/{char.max_mp}")
            
            # AI 동료의 경우 추가 정보
            if char not in self.player_controlled_characters:
                ai_companion = next((ai for ai in self.ai_companions if ai.character == char), None)
                if ai_companion:
                    print(f"  신뢰도: {ai_companion.trust_level}/100")
                    print(f"  사기: {ai_companion.morale}/100")
            print()
    
    def _create_status_bar(self, current: int, maximum: int, width: int) -> str:
        """상태 바 생성"""
        if maximum <= 0:
            return "□" * width
        
        filled = int((current / maximum) * width)
        empty = width - filled
        return "■" * filled + "□" * empty
    
    def _get_action_description(self, action_type: str, action_data: Dict) -> str:
        """행동 설명 생성"""
        descriptions = {
            "attack": "적을 공격합니다",
            "skill": "스킬을 사용합니다",
            "defend": "방어 자세를 취합니다",
            "heal": "동료를 치료합니다",
            "use_item": "아이템을 사용합니다"
        }
        return descriptions.get(action_type, "행동을 수행합니다")
    
    def handle_item_usage_by_ai(self, ai_companion: AICompanion, item_type: str) -> bool:
        """AI의 아이템 사용 처리"""
        if not self.item_sharing_enabled:
            return False
        
        # 파티 공용 아이템에서 사용
        print(f"🤖 {ai_companion.character.name}이(가) {item_type} 아이템을 사용했습니다!")
        
        # 플레이어에게 알림
        if random.random() < 0.3:  # 30% 확률로 사과
            print(f"💬 {ai_companion.character.name}: 아이템을 써버렸어, 미안!")
        
        return True
    
    def get_ai_mode_status(self) -> str:
        """AI 모드 상태 정보"""
        status_lines = [
            f"🎮 AI 게임모드: {self.current_mode.value}",
            f"👤 플레이어 조작: {len(self.player_controlled_characters)}명",
            f"🤖 AI 조작: {len(self.ai_companions)}명",
            f"💬 대기 중인 요청: {len(self.pending_ai_requests)}개"
        ]
        
        if self.ai_companions:
            status_lines.append("\n🤖 AI 동료 상태:")
            for ai in self.ai_companions:
                status_lines.append(f"   {ai.character.name}: 신뢰도 {ai.trust_level}/100, 사기 {ai.morale}/100")
        
        return "\n".join(status_lines)
    
    def _execute_player_action(self, character: Character, action: str, party: List[Character], enemies: List[Character]):
        """플레이어 행동 실행 - 전체 시스템 통합"""
        if action == "🤝 협동 공격":
            return self._execute_coordination_attack(character, party, enemies)
        elif action == "💬 AI 요청 확인":
            return self._handle_ai_requests()
        elif action == "⚔️ 공격":
            return "attack", {}
        elif action == "✨ 스킬 사용":
            # 실제 스킬 시스템 사용
            return self._select_and_use_skill(character, party, enemies)
        elif action == "🧪 아이템 사용":
            # 실제 아이템 시스템 사용
            return self._select_and_use_item(character, party)
        elif action == "🛡️ 방어":
            return "defend", {}
        elif action == "🎒 장비 관리":
            # 장비 관리 시스템
            return self._manage_equipment(character, party)
        elif action == "🍳 요리 사용":
            # 요리 시스템
            return self._use_cooking_system(character, party)
        elif action == "🌟 필드스킬 사용":
            # 필드스킬 시스템
            return self._use_field_skill(character, party, enemies)
        elif action == "💾 전투 중 저장":
            # 저장 시스템
            return self._save_game_during_battle(character, party)
        elif action == "📊 상태 확인":
            self._show_party_status(party)
            return self._process_player_turn(character, party, enemies)
        else:
            return "defend", {}
    
    def _select_and_use_skill(self, character: Character, party: List[Character], enemies: List[Character]):
        """스킬 선택 및 사용 - 실제 스킬 시스템 통합"""
        try:
            from .skill_system import get_skill_system
            skill_system = get_skill_system()
            
            # 캐릭터의 직업별 스킬 가져오기
            character_class = getattr(character, 'character_class', '전사')
            available_skills = skill_system.get_class_skills(character_class)
            
            if not available_skills:
                print(f"❌ {character.name}이(가) 사용할 수 있는 스킬이 없습니다.")
                return "defend", {}
            
            # 사용 가능한 스킬만 필터링 (MP 확인)
            usable_skills = []
            for skill in available_skills:
                mp_cost = getattr(skill, 'mp_cost', 0)
                if character.current_mp >= mp_cost:
                    usable_skills.append(skill)
            
            if not usable_skills:
                print(f"❌ MP가 부족하여 사용할 수 있는 스킬이 없습니다. (현재 MP: {character.current_mp})")
                return "defend", {}
            
            print(f"\n✨ {character.name}의 스킬 선택 (MP: {character.current_mp}/{character.max_mp})")
            print("-" * 50)
            
            for i, skill in enumerate(usable_skills, 1):
                mp_cost = getattr(skill, 'mp_cost', 0)
                skill_type = getattr(skill, 'type', 'UNKNOWN')
                description = getattr(skill, 'description', '설명 없음')
                print(f"{i}. {skill.name} (MP: {mp_cost}) [{skill_type}]")
                print(f"   {description}")
            
            print(f"{len(usable_skills) + 1}. 취소")
            
            try:
                choice = int(input("스킬 선택: ")) - 1
                if choice == len(usable_skills):
                    return self._process_player_turn(character, party, enemies)
                elif 0 <= choice < len(usable_skills):
                    selected_skill = usable_skills[choice]
                    
                    # 대상 선택
                    target = self._select_skill_target(selected_skill, character, party, enemies)
                    if target:
                        mp_cost = getattr(selected_skill, 'mp_cost', 0)
                        character.current_mp = max(0, character.current_mp - mp_cost)
                        print(f"✨ {character.name}이(가) {selected_skill.name}을(를) 사용합니다!")
                        return "skill", {"skill": selected_skill, "target": target}
                    else:
                        return self._process_player_turn(character, party, enemies)
                else:
                    print("❌ 잘못된 선택입니다.")
                    return self._select_and_use_skill(character, party, enemies)
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return self._select_and_use_skill(character, party, enemies)
                
        except ImportError:
            print("❌ 스킬 시스템을 불러올 수 없습니다.")
            return "defend", {}
    
    def _select_skill_target(self, skill, caster: Character, party: List[Character], enemies: List[Character]):
        """스킬 대상 선택"""
        skill_type = getattr(skill, 'type', 'UNKNOWN')
        target_type = getattr(skill, 'target_type', 'enemy')
        
        # 대상 타입에 따른 선택지 구성
        if target_type == 'enemy' or skill_type in ['HP_ATTACK', 'BRV_ATTACK', 'BRV_HP_ATTACK']:
            targets = [e for e in enemies if e.is_alive]
            target_name = "적"
        elif target_type == 'ally' or skill_type in ['HEAL', 'BUFF']:
            targets = [p for p in party if p.is_alive]
            target_name = "아군"
        elif target_type == 'self':
            return caster
        else:
            # 기본값: 적 대상
            targets = [e for e in enemies if e.is_alive]
            target_name = "적"
        
        if not targets:
            print(f"❌ 대상으로 할 수 있는 {target_name}이 없습니다.")
            return None
        
        print(f"\n🎯 {target_name} 선택:")
        for i, target in enumerate(targets, 1):
            hp_ratio = target.current_hp / target.max_hp if target.max_hp > 0 else 0
            status = "건강" if hp_ratio > 0.7 else "부상" if hp_ratio > 0.3 else "위험"
            print(f"{i}. {target.name} (HP: {target.current_hp}/{target.max_hp} - {status})")
        
        print(f"{len(targets) + 1}. 취소")
        
        try:
            choice = int(input("대상 선택: ")) - 1
            if choice == len(targets):
                return None
            elif 0 <= choice < len(targets):
                return targets[choice]
            else:
                print("❌ 잘못된 선택입니다.")
                return self._select_skill_target(skill, caster, party, enemies)
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return self._select_skill_target(skill, caster, party, enemies)
    
    def _select_and_use_item(self, character: Character, party: List[Character]):
        """아이템 선택 및 사용 - 실제 아이템 시스템 통합"""
        try:
            from .items import ItemDatabase, ItemType
            item_db = ItemDatabase()
            
            # 캐릭터 인벤토리에서 사용 가능한 아이템 확인
            if not hasattr(character, 'inventory') or not character.inventory:
                print(f"❌ {character.name}의 인벤토리가 비어있습니다.")
                return "defend", {}
            
            # 소모품만 필터링
            consumable_items = []
            for item_name, quantity in character.inventory.get_items_list():
                if quantity > 0:
                    item = item_db.get_item(item_name)
                    if item and item.item_type == ItemType.CONSUMABLE:
                        consumable_items.append((item, quantity))
            
            if not consumable_items:
                print(f"❌ 사용할 수 있는 소모품이 없습니다.")
                return "defend", {}
            
            print(f"\n🧪 {character.name}의 아이템 사용")
            print("-" * 50)
            
            for i, (item, quantity) in enumerate(consumable_items, 1):
                effect_desc = self._get_item_effect_description(item)
                print(f"{i}. {item.name} x{quantity}")
                print(f"   효과: {effect_desc}")
            
            print(f"{len(consumable_items) + 1}. 취소")
            
            try:
                choice = int(input("아이템 선택: ")) - 1
                if choice == len(consumable_items):
                    return self._process_player_turn(character, party, [])
                elif 0 <= choice < len(consumable_items):
                    selected_item, quantity = consumable_items[choice]
                    
                    # 대상 선택
                    target = self._select_item_target(selected_item, character, party)
                    if target:
                        # 아이템 사용
                        character.inventory.remove_item(selected_item.name, 1)
                        print(f"🧪 {character.name}이(가) {selected_item.name}을(를) 사용합니다!")
                        return "use_item", {"item": selected_item, "target": target}
                    else:
                        return self._process_player_turn(character, party, [])
                else:
                    print("❌ 잘못된 선택입니다.")
                    return self._select_and_use_item(character, party)
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return self._select_and_use_item(character, party)
                
        except ImportError:
            print("❌ 아이템 시스템을 불러올 수 없습니다.")
            return "defend", {}
    
    def _get_item_effect_description(self, item) -> str:
        """아이템 효과 설명 생성"""
        if not hasattr(item, 'effects') or not item.effects:
            return "효과 없음"
        
        descriptions = []
        for effect_type, value in item.effects.items():
            if effect_type == "heal":
                descriptions.append(f"HP {value} 회복")
            elif effect_type == "restore_mp":
                descriptions.append(f"MP {value} 회복")
            elif effect_type == "cure_poison":
                descriptions.append("독 치료")
            elif effect_type == "cure_all":
                descriptions.append("모든 상태이상 치료")
            elif effect_type == "boost_attack":
                descriptions.append(f"공격력 {value}% 증가")
            elif effect_type == "boost_defense":
                descriptions.append(f"방어력 {value}% 증가")
            else:
                descriptions.append(f"{effect_type}: {value}")
        
        return ", ".join(descriptions) if descriptions else "효과 없음"
    
    def _select_item_target(self, item, user: Character, party: List[Character]):
        """아이템 사용 대상 선택"""
        # 아이템 효과에 따라 대상 결정
        if not hasattr(item, 'effects') or not item.effects:
            return user  # 기본값: 자신
        
        # 회복/치료 아이템은 아군 대상
        healing_effects = ['heal', 'restore_mp', 'cure_poison', 'cure_all']
        is_healing_item = any(effect in item.effects for effect in healing_effects)
        
        if is_healing_item:
            targets = [p for p in party if p.is_alive]
            target_name = "아군"
        else:
            # 공격 아이템이나 기타는 자신에게 사용
            return user
        
        if not targets:
            print("❌ 대상으로 할 수 있는 아군이 없습니다.")
            return None
        
        print(f"\n🎯 대상 선택:")
        for i, target in enumerate(targets, 1):
            hp_ratio = target.current_hp / target.max_hp if target.max_hp > 0 else 0
            mp_ratio = target.current_mp / target.max_mp if target.max_mp > 0 else 0
            status = "건강" if hp_ratio > 0.7 else "부상" if hp_ratio > 0.3 else "위험"
            print(f"{i}. {target.name} (HP: {hp_ratio*100:.0f}%, MP: {mp_ratio*100:.0f}% - {status})")
        
        print(f"{len(targets) + 1}. 취소")
        
        try:
            choice = int(input("대상 선택: ")) - 1
            if choice == len(targets):
                return None
            elif 0 <= choice < len(targets):
                return targets[choice]
            else:
                print("❌ 잘못된 선택입니다.")
                return self._select_item_target(item, user, party)
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return self._select_item_target(item, user, party)
    
    # ==================== 전체 시스템 통합 메서드들 ====================
    
    def _manage_equipment(self, character: Character, party: List[Character]):
        """장비 관리 시스템"""
        try:
            from .equipment_system import get_equipment_manager
            equipment_manager = get_equipment_manager()
            
            print(f"\n🎒 {character.name}의 장비 관리")
            print("-" * 50)
            
            # 현재 장착한 장비 표시
            if hasattr(character, 'equipped_items'):
                print("현재 장착 장비:")
                for slot, item in character.equipped_items.items():
                    if item:
                        print(f"  {slot}: {item.name}")
                    else:
                        print(f"  {slot}: (없음)")
            
            # 장비 관리 옵션
            options = [
                "장비 착용/해제",
                "장비 강화",
                "장비 상태 확인",
                "AI에게 장비 추천 요청"
            ]
            
            print("\n장비 관리 옵션:")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print(f"{len(options) + 1}. 취소")
            
            try:
                choice = int(input("선택: ")) - 1
                if choice == len(options):
                    return self._process_player_turn(character, party, [])
                elif 0 <= choice < len(options):
                    if choice == 0:  # 장비 착용/해제
                        return self._equip_unequip_items(character)
                    elif choice == 1:  # 장비 강화
                        return self._enhance_equipment(character)
                    elif choice == 2:  # 장비 상태 확인
                        return self._check_equipment_status(character)
                    elif choice == 3:  # AI 장비 추천
                        return self._get_ai_equipment_recommendation(character)
                else:
                    print("❌ 잘못된 선택입니다.")
                    return self._manage_equipment(character, party)
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return self._manage_equipment(character, party)
                
        except ImportError:
            print("❌ 장비 시스템을 불러올 수 없습니다.")
            return "defend", {}
    
    def _use_cooking_system(self, character: Character, party: List[Character]):
        """요리 시스템 사용"""
        try:
            from .cooking_system import get_cooking_manager
            cooking_manager = get_cooking_manager()
            
            print(f"\n🍳 {character.name}의 요리 시스템")
            print("-" * 50)
            
            # 요리 가능한 재료 확인
            available_recipes = []
            if hasattr(character, 'inventory'):
                available_recipes = cooking_manager.get_available_recipes(character.inventory)
            
            if not available_recipes:
                print("❌ 요리할 수 있는 재료가 없습니다.")
                return self._process_player_turn(character, party, [])
            
            print("요리 가능한 레시피:")
            for i, recipe in enumerate(available_recipes, 1):
                print(f"{i}. {recipe.name} - {recipe.description}")
                print(f"   효과: {recipe.effects}")
                print(f"   재료: {', '.join(recipe.ingredients)}")
            
            print(f"{len(available_recipes) + 1}. 취소")
            
            try:
                choice = int(input("요리 선택: ")) - 1
                if choice == len(available_recipes):
                    return self._process_player_turn(character, party, [])
                elif 0 <= choice < len(available_recipes):
                    selected_recipe = available_recipes[choice]
                    
                    # 요리 실행
                    result = cooking_manager.cook_recipe(character, selected_recipe)
                    if result:
                        print(f"🍳 {character.name}이(가) {selected_recipe.name}을(를) 요리했습니다!")
                        return "cooking", {"recipe": selected_recipe.name, "result": result}
                    else:
                        print("❌ 요리에 실패했습니다.")
                        return self._process_player_turn(character, party, [])
                else:
                    print("❌ 잘못된 선택입니다.")
                    return self._use_cooking_system(character, party)
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return self._use_cooking_system(character, party)
                
        except ImportError:
            print("❌ 요리 시스템을 불러올 수 없습니다.")
            return "defend", {}
    
    def _use_field_skill(self, character: Character, party: List[Character], enemies: List[Character]):
        """필드스킬 시스템 사용"""
        try:
            from .field_skill_system import get_field_skill_manager
            field_skill_manager = get_field_skill_manager()
            
            print(f"\n🌟 {character.name}의 필드스킬")
            print("-" * 50)
            
            # 사용 가능한 필드스킬 확인
            character_class = getattr(character, 'character_class', '전사')
            available_skills = field_skill_manager.get_available_field_skills(character_class)
            
            if not available_skills:
                print("❌ 사용할 수 있는 필드스킬이 없습니다.")
                return self._process_player_turn(character, party, enemies)
            
            print("사용 가능한 필드스킬:")
            for i, skill in enumerate(available_skills, 1):
                cooldown_status = "사용가능" if skill.is_ready() else f"재사용 대기 {skill.cooldown_remaining}턴"
                print(f"{i}. {skill.name} - {skill.description} ({cooldown_status})")
                print(f"   효과: {skill.field_effect}")
            
            print(f"{len(available_skills) + 1}. 취소")
            
            try:
                choice = int(input("필드스킬 선택: ")) - 1
                if choice == len(available_skills):
                    return self._process_player_turn(character, party, enemies)
                elif 0 <= choice < len(available_skills):
                    selected_skill = available_skills[choice]
                    
                    if selected_skill.is_ready():
                        # 필드스킬 사용
                        result = field_skill_manager.use_field_skill(character, selected_skill, party, enemies)
                        print(f"🌟 {character.name}이(가) {selected_skill.name}을(를) 사용했습니다!")
                        return "field_skill", {"skill": selected_skill.name, "result": result}
                    else:
                        print(f"❌ {selected_skill.name}은(는) 아직 사용할 수 없습니다.")
                        return self._process_player_turn(character, party, enemies)
                else:
                    print("❌ 잘못된 선택입니다.")
                    return self._use_field_skill(character, party, enemies)
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return self._use_field_skill(character, party, enemies)
                
        except ImportError:
            print("❌ 필드스킬 시스템을 불러올 수 없습니다.")
            return "defend", {}
    
    def _save_game_during_battle(self, character: Character, party: List[Character]):
        """전투 중 저장"""
        try:
            from .save_system import get_save_manager
            save_manager = get_save_manager()
            
            print(f"\n💾 전투 중 저장")
            print("-" * 50)
            print("⚠️ 전투 중 저장은 특별한 경우에만 사용하세요.")
            print("📝 현재 전투 상황과 파티 상태가 모두 저장됩니다.")
            
            confirm = input("정말로 저장하시겠습니까? (y/n): ").lower()
            if confirm == 'y':
                # 전투 상태 포함 저장
                save_data = {
                    'party': party,
                    'battle_state': 'in_combat',
                    'current_character': character.name,
                    'timestamp': time.time()
                }
                
                result = save_manager.save_battle_state(save_data)
                if result:
                    print("✅ 전투 상태가 저장되었습니다!")
                    return "save_complete", {"save_result": result}
                else:
                    print("❌ 저장에 실패했습니다.")
            else:
                print("❌ 저장을 취소했습니다.")
            
            return self._process_player_turn(character, party, [])
                
        except ImportError:
            print("❌ 저장 시스템을 불러올 수 없습니다.")
            return "defend", {}
    
    def _equip_unequip_items(self, character: Character):
        """장비 착용/해제 - 대폭 개선된 시스템"""
        try:
            from .items import ItemDatabase, ItemType
            item_db = ItemDatabase()
            
            print(f"\n🎒 {character.name}의 장비 관리")
            print("=" * 60)
            
            # 현재 장착 장비 표시
            equipped_items = getattr(character, 'equipped_items', {})
            print("📋 현재 장착 중인 장비:")
            
            equipment_slots = ["무기", "방패", "머리", "몸통", "다리", "발", "장갑", "목걸이", "반지"]
            for slot in equipment_slots:
                item = equipped_items.get(slot)
                if item:
                    durability = getattr(item, 'durability', 100)
                    durability_status = "🟢" if durability > 70 else "🟡" if durability > 30 else "🔴"
                    enhancement = getattr(item, 'enhancement_level', 0)
                    enhancement_text = f" +{enhancement}" if enhancement > 0 else ""
                    print(f"  {slot}: {item.name}{enhancement_text} {durability_status}({durability}%)")
                else:
                    print(f"  {slot}: (없음)")
            
            # 인벤토리의 장비 아이템 표시
            print(f"\n🎒 {character.name}의 장비 인벤토리:")
            if hasattr(character, 'inventory') and character.inventory:
                equipment_in_inventory = []
                for item_name, quantity in character.inventory.get_items_list():
                    item = item_db.get_item(item_name)
                    if item and item.item_type == ItemType.EQUIPMENT:
                        equipment_in_inventory.append((item, quantity))
                
                if equipment_in_inventory:
                    for i, (item, quantity) in enumerate(equipment_in_inventory, 1):
                        durability = getattr(item, 'durability', 100)
                        enhancement = getattr(item, 'enhancement_level', 0)
                        enhancement_text = f" +{enhancement}" if enhancement > 0 else ""
                        print(f"  {i}. {item.name}{enhancement_text} x{quantity} (내구도: {durability}%)")
                        print(f"     효과: {self._get_equipment_stats_description(item)}")
                else:
                    print("  (장비 아이템 없음)")
            else:
                print("  (인벤토리 없음)")
            
            # 장비 관리 옵션
            print(f"\n⚙️ 장비 관리 옵션:")
            print("1. 장비 착용")
            print("2. 장비 해제")
            print("3. 장비 상세 정보 확인")
            print("4. 장비 수리")
            print("5. 취소")
            
            try:
                choice = int(input("선택: "))
                if choice == 1:
                    return self._equip_item_advanced(character, equipment_in_inventory)
                elif choice == 2:
                    return self._unequip_item_advanced(character, equipped_items)
                elif choice == 3:
                    return self._show_equipment_details(character)
                elif choice == 4:
                    return self._repair_equipment(character)
                elif choice == 5:
                    return self._process_player_turn(character, [], [])
                else:
                    print("❌ 잘못된 선택입니다.")
                    return self._equip_unequip_items(character)
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                return self._equip_unequip_items(character)
                
        except ImportError:
            print("❌ 아이템 시스템을 불러올 수 없습니다.")
            return "equipment_manage", {"action": "basic_equip"}
    
    def _get_equipment_stats_description(self, item) -> str:
        """장비 스탯 효과 설명"""
        effects = []
        if hasattr(item, 'physical_attack_bonus') and item.physical_attack_bonus > 0:
            effects.append(f"물공 +{item.physical_attack_bonus}")
        if hasattr(item, 'magic_attack_bonus') and item.magic_attack_bonus > 0:
            effects.append(f"마공 +{item.magic_attack_bonus}")
        if hasattr(item, 'physical_defense_bonus') and item.physical_defense_bonus > 0:
            effects.append(f"물방 +{item.physical_defense_bonus}")
        if hasattr(item, 'magic_defense_bonus') and item.magic_defense_bonus > 0:
            effects.append(f"마방 +{item.magic_defense_bonus}")
        if hasattr(item, 'speed_bonus') and item.speed_bonus > 0:
            effects.append(f"속도 +{item.speed_bonus}")
        if hasattr(item, 'hp_bonus') and item.hp_bonus > 0:
            effects.append(f"HP +{item.hp_bonus}")
        if hasattr(item, 'mp_bonus') and item.mp_bonus > 0:
            effects.append(f"MP +{item.mp_bonus}")
        
        return ", ".join(effects) if effects else "특별한 효과 없음"
    
    def _equip_item_advanced(self, character: Character, available_equipment: List):
        """고급 장비 착용 시스템"""
        if not available_equipment:
            print("❌ 착용할 수 있는 장비가 없습니다.")
            return self._equip_unequip_items(character)
        
        print("\n⚔️ 착용할 장비 선택:")
        for i, (item, quantity) in enumerate(available_equipment, 1):
            slot = getattr(item, 'equipment_slot', '알 수 없음')
            print(f"{i}. {item.name} ({slot} 슬롯)")
            print(f"   효과: {self._get_equipment_stats_description(item)}")
        
        try:
            choice = int(input("장비 선택 (0: 취소): ")) - 1
            if choice == -1:
                return self._equip_unequip_items(character)
            elif 0 <= choice < len(available_equipment):
                selected_item, _ = available_equipment[choice]
                
                # 장비 착용 처리
                success = self._perform_equipment_change(character, selected_item, "equip")
                if success:
                    print(f"✅ {selected_item.name}을(를) 착용했습니다!")
                    # 성격에 따른 대화
                    personality = getattr(character, 'personality', CharacterPersonality.SERIOUS)
                    gender = getattr(character, 'gender', CharacterGender.MALE)
                    dialogue = CharacterTraits.get_dialogue(personality, "praise")
                    print(f"💬 {character.name}: \"{dialogue}\"")
                else:
                    print(f"❌ {selected_item.name} 착용에 실패했습니다.")
                
                return "equipment_change", {"action": "equip", "item": selected_item.name}
            else:
                print("❌ 잘못된 선택입니다.")
                return self._equip_item_advanced(character, available_equipment)
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return self._equip_item_advanced(character, available_equipment)
    
    def _unequip_item_advanced(self, character: Character, equipped_items: Dict):
        """고급 장비 해제 시스템"""
        equipped_list = [(slot, item) for slot, item in equipped_items.items() if item is not None]
        
        if not equipped_list:
            print("❌ 해제할 장비가 없습니다.")
            return self._equip_unequip_items(character)
        
        print("\n🔓 해제할 장비 선택:")
        for i, (slot, item) in enumerate(equipped_list, 1):
            durability = getattr(item, 'durability', 100)
            print(f"{i}. {slot}: {item.name} (내구도: {durability}%)")
        
        try:
            choice = int(input("장비 선택 (0: 취소): ")) - 1
            if choice == -1:
                return self._equip_unequip_items(character)
            elif 0 <= choice < len(equipped_list):
                slot, selected_item = equipped_list[choice]
                
                # 장비 해제 처리
                success = self._perform_equipment_change(character, selected_item, "unequip")
                if success:
                    print(f"✅ {selected_item.name}을(를) 해제했습니다!")
                else:
                    print(f"❌ {selected_item.name} 해제에 실패했습니다.")
                
                return "equipment_change", {"action": "unequip", "item": selected_item.name}
            else:
                print("❌ 잘못된 선택입니다.")
                return self._unequip_item_advanced(character, equipped_items)
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return self._unequip_item_advanced(character, equipped_items)
    
    def _perform_equipment_change(self, character: Character, item, action: str) -> bool:
        """실제 장비 변경 수행"""
        try:
            if action == "equip":
                # 장비 착용 로직 (실제 게임 시스템과 연동)
                slot = getattr(item, 'equipment_slot', None)
                if slot:
                    if not hasattr(character, 'equipped_items'):
                        character.equipped_items = {}
                    character.equipped_items[slot] = item
                    # 스탯 보너스 적용
                    self._apply_equipment_bonuses(character, item, True)
                    return True
            elif action == "unequip":
                # 장비 해제 로직
                if hasattr(character, 'equipped_items'):
                    for slot, equipped_item in character.equipped_items.items():
                        if equipped_item == item:
                            character.equipped_items[slot] = None
                            # 스탯 보너스 제거
                            self._apply_equipment_bonuses(character, item, False)
                            return True
            return False
        except Exception as e:
            print(f"❌ 장비 변경 중 오류 발생: {e}")
            return False
    
    def _apply_equipment_bonuses(self, character: Character, item, is_equipping: bool):
        """장비 보너스 적용/제거"""
        multiplier = 1 if is_equipping else -1
        
        if hasattr(item, 'physical_attack_bonus'):
            character.physical_attack += item.physical_attack_bonus * multiplier
        if hasattr(item, 'magic_attack_bonus'):
            character.magic_attack += item.magic_attack_bonus * multiplier
        if hasattr(item, 'physical_defense_bonus'):
            character.physical_defense += item.physical_defense_bonus * multiplier
        if hasattr(item, 'magic_defense_bonus'):
            character.magic_defense += item.magic_defense_bonus * multiplier
        if hasattr(item, 'speed_bonus'):
            character.speed += item.speed_bonus * multiplier
        if hasattr(item, 'hp_bonus'):
            character.max_hp += item.hp_bonus * multiplier
            if is_equipping:
                character.current_hp += item.hp_bonus
        if hasattr(item, 'mp_bonus'):
            character.max_mp += item.mp_bonus * multiplier
            if is_equipping:
                character.current_mp += item.mp_bonus
    
    def _show_equipment_details(self, character: Character):
        """장비 상세 정보 표시"""
        print(f"\n📊 {character.name}의 장비 상세 정보")
        print("=" * 60)
        
        equipped_items = getattr(character, 'equipped_items', {})
        total_bonuses = {
            "physical_attack": 0, "magic_attack": 0, "physical_defense": 0,
            "magic_defense": 0, "speed": 0, "hp": 0, "mp": 0
        }
        
        for slot, item in equipped_items.items():
            if item:
                print(f"\n🔸 {slot}: {item.name}")
                durability = getattr(item, 'durability', 100)
                enhancement = getattr(item, 'enhancement_level', 0)
                
                print(f"   내구도: {durability}% {'�' if durability > 70 else '🟡' if durability > 30 else '🔴'}")
                if enhancement > 0:
                    print(f"   강화 수치: +{enhancement}")
                
                # 개별 보너스 표시
                bonuses = []
                for stat in total_bonuses.keys():
                    bonus_attr = f"{stat}_bonus"
                    if hasattr(item, bonus_attr):
                        bonus_value = getattr(item, bonus_attr)
                        if bonus_value > 0:
                            bonuses.append(f"{stat.replace('_', ' ').title()}: +{bonus_value}")
                            total_bonuses[stat] += bonus_value
                
                if bonuses:
                    print(f"   보너스: {', '.join(bonuses)}")
                else:
                    print("   보너스: 없음")
        
        # 총 보너스 요약
        print(f"\n📈 총 장비 보너스:")
        for stat, bonus in total_bonuses.items():
            if bonus > 0:
                stat_name = stat.replace('_', ' ').title()
                print(f"   {stat_name}: +{bonus}")
        
        input("\n계속하려면 Enter를 누르세요...")
        return self._equip_unequip_items(character)
    
    def _repair_equipment(self, character: Character):
        """장비 수리 시스템"""
        equipped_items = getattr(character, 'equipped_items', {})
        damaged_items = []
        
        for slot, item in equipped_items.items():
            if item and hasattr(item, 'durability') and item.durability < 100:
                damaged_items.append((slot, item))
        
        if not damaged_items:
            print("❌ 수리가 필요한 장비가 없습니다.")
            return self._equip_unequip_items(character)
        
        print("\n🔧 수리할 장비 선택:")
        for i, (slot, item) in enumerate(damaged_items, 1):
            durability = item.durability
            repair_cost = self._calculate_repair_cost(item)
            print(f"{i}. {slot}: {item.name} (내구도: {durability}%) - 수리비: {repair_cost} 골드")
        
        print(f"{len(damaged_items) + 1}. 모든 장비 수리")
        print(f"{len(damaged_items) + 2}. 취소")
        
        try:
            choice = int(input("선택: ")) - 1
            if choice == len(damaged_items) + 1:  # 취소
                return self._equip_unequip_items(character)
            elif choice == len(damaged_items):  # 모든 장비 수리
                total_cost = sum(self._calculate_repair_cost(item) for _, item in damaged_items)
                if self._can_afford_repair(character, total_cost):
                    for _, item in damaged_items:
                        item.durability = 100
                    self._pay_repair_cost(character, total_cost)
                    print(f"✅ 모든 장비를 수리했습니다! (총 비용: {total_cost} 골드)")
                else:
                    print("❌ 골드가 부족합니다.")
            elif 0 <= choice < len(damaged_items):
                slot, selected_item = damaged_items[choice]
                repair_cost = self._calculate_repair_cost(selected_item)
                
                if self._can_afford_repair(character, repair_cost):
                    selected_item.durability = 100
                    self._pay_repair_cost(character, repair_cost)
                    print(f"✅ {selected_item.name}을(를) 수리했습니다! (비용: {repair_cost} 골드)")
                else:
                    print("❌ 골드가 부족합니다.")
            else:
                print("❌ 잘못된 선택입니다.")
                return self._repair_equipment(character)
            
            return "equipment_repair", {"action": "repair_complete"}
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return self._repair_equipment(character)
    
    def _calculate_repair_cost(self, item) -> int:
        """수리 비용 계산"""
        base_cost = 100  # 기본 수리비
        durability_lost = 100 - getattr(item, 'durability', 100)
        enhancement_multiplier = 1 + (getattr(item, 'enhancement_level', 0) * 0.5)
        
        return int(base_cost * (durability_lost / 100) * enhancement_multiplier)
    
    def _can_afford_repair(self, character: Character, cost: int) -> bool:
        """수리 비용 지불 가능 여부"""
        gold = getattr(character, 'gold', 0)
        return gold >= cost
    
    def _pay_repair_cost(self, character: Character, cost: int):
        """수리 비용 지불"""
        if hasattr(character, 'gold'):
            character.gold -= cost
        else:
            character.gold = 0
    
    def _enhance_equipment(self, character: Character):
        """장비 강화"""
        print(f"⚡ {character.name}의 장비 강화")
        print("💡 장비 강화 시스템이 곧 업그레이드됩니다!")
        return "equipment_enhance", {"action": "enhance"}
    
    def _check_equipment_status(self, character: Character):
        """장비 상태 확인"""
        print(f"📊 {character.name}의 장비 상태")
        if hasattr(character, 'equipped_items'):
            for slot, item in character.equipped_items.items():
                if item:
                    durability = getattr(item, 'durability', 100)
                    print(f"  {slot}: {item.name} (내구도: {durability}%)")
                else:
                    print(f"  {slot}: (장비 없음)")
        return "equipment_status", {"action": "check_status"}
    
    def _get_ai_equipment_recommendation(self, character: Character):
        """AI 장비 추천"""
        character_class = getattr(character, 'character_class', '전사')
        
        recommendations = {
            '전사': ['강철 검', '철갑 방패', '판금 갑옷'],
            '아크메이지': ['마법사 지팡이', '마력 로브', '지혜의 반지'],
            '궁수': ['엘븐 활', '가죽 갑옷', '신속의 부츠'],
            '도적': ['암살 단검', '그림자 망토', '민첩의 장갑']
        }
        
        class_recommendations = recommendations.get(character_class, ['기본 장비'])
        
        print(f"🤖 AI 추천 장비 ({character_class} 전용):")
        for i, item in enumerate(class_recommendations, 1):
            print(f"  {i}. {item}")
        
        return "ai_recommendation", {"recommendations": class_recommendations}

# 전역 AI 게임모드 매니저 (단일 인스턴스)
ai_game_mode_manager = AIGameModeManager()

def initialize_ai_game_mode(party_members: List[Character], controlled_count: int = 1):
    """AI 게임모드 초기화"""
    return ai_game_mode_manager.initialize_ai_mode(party_members, controlled_count)

# 기본 게임모드용 장비 자동 장착 함수
def auto_equip_for_basic_mode(character: Character, inventory_items: List = None) -> List[str]:
    """기본 게임모드에서 캐릭터에게 최적의 장비를 자동으로 장착"""
    return basic_equipment_manager.auto_equip_best_items(character, inventory_items)

def get_equipment_recommendations_for_basic_mode(character: Character, available_items: List) -> List[Dict]:
    """기본 게임모드에서 캐릭터용 장비 추천"""
    return basic_equipment_manager.get_equipment_recommendations(character, available_items)

def process_character_turn(character: Character, party: List[Character], enemies: List[Character]):
    """캐릭터 턴 처리 (AI/플레이어 자동 구분)"""
    return ai_game_mode_manager.process_combat_turn(character, party, enemies)
