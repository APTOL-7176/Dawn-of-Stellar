"""
고해상도 픽셀 게이지 시스템 - 캐스팅 진행도용
8단계 픽셀 세분화로 부드러운 진행도 표시
"""

def create_ultra_smooth_casting_gauge(progress_percent, length=15, color="\033[95m"):
    """
    초고해상도 캐스팅 게이지 생성
    
    Args:
        progress_percent: 진행률 (0-100)
        length: 게이지 길이 (기본 15칸)
        color: 게이지 색상 (기본 마젠타)
    
    Returns:
        픽셀 단위로 세밀한 게이지 문자열
    """
    # 진행률을 0-1 사이로 정규화
    progress = max(0.0, min(1.0, progress_percent / 100.0))
    
    # 전체 픽셀 수 계산 (길이 * 8 픽셀)
    total_pixels = length * 8
    filled_pixels = int(progress * total_pixels)
    
    # 완전히 채워진 블록 수
    full_blocks = filled_pixels // 8
    remaining_pixels = filled_pixels % 8
    
    # 픽셀 문자들 (0픽셀부터 8픽셀까지)
    pixel_chars = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
    
    # 게이지 구성
    gauge = ""
    
    # 완전히 채워진 블록들
    if full_blocks > 0:
        gauge += color + '█' * full_blocks + '\033[0m'
    
    # 부분적으로 채워진 블록
    if full_blocks < length and remaining_pixels > 0:
        gauge += color + pixel_chars[remaining_pixels] + '\033[0m'
        # 나머지 빈 블록들
        empty_blocks = length - full_blocks - 1
        if empty_blocks > 0:
            gauge += '\033[90m' + '░' * empty_blocks + '\033[0m'
    elif full_blocks < length:
        # 완전히 빈 블록들
        empty_blocks = length - full_blocks
        gauge += '\033[90m' + '░' * empty_blocks + '\033[0m'
    
    return gauge

def test_ultra_smooth_gauge():
    """픽셀 게이지 테스트"""
    print("🔮 초고해상도 캐스팅 게이지 테스트")
    print("=" * 50)
    
    # 다양한 진행률 테스트
    test_values = [0, 5, 12, 23, 37, 45, 58, 67, 78, 84, 91, 97, 100]
    
    for progress in test_values:
        gauge = create_ultra_smooth_casting_gauge(progress, 15)
        print(f"🔮 {progress:3d}% [{gauge}]")

if __name__ == "__main__":
    test_ultra_smooth_gauge()
