#!/usr/bin/env python3
"""
간단한 시드 변화 확인
"""

import hashlib

print("🎲 시드 생성 방식 비교")
print("=" * 50)

# 기존 방식 (매번 달라짐)
import time
import random

print("❌ 기존 방식 (매번 다른 시드):")
for i in range(3):
    old_seed_string = f"{time.time()}_1_핀_{random.randint(1, 10000)}"
    old_seed = int(hashlib.md5(old_seed_string.encode()).hexdigest()[:8], 16)
    print(f"   시도 {i+1}: {old_seed}")

print("\n✅ 새로운 방식 (고정된 시드):")
for i in range(3):
    new_seed_string = f"DawnOfStellar_핀_Session2025_1"
    new_seed = int(hashlib.md5(new_seed_string.encode()).hexdigest()[:8], 16)
    print(f"   시도 {i+1}: {new_seed}")

print("\n🎯 결과:")
print("✅ 새로운 방식은 매번 동일한 시드를 생성합니다!")
print("🎮 이제 아이템이 일관되게 나타날 것입니다!")
