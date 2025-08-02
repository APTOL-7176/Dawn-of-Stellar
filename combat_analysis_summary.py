#!/usr/bin/env python3
"""
전투 데미지 종합 분석 결과 요약
"""

print("="*80)
print("🏟️ 전투 데미지 분석 결과 요약 - 레벨 10")
print("="*80)

print("\n📊 기본 공격 비교 (플레이어 vs 적):")
print("  기준 적: Lv10 몬스터 (HP 1,600 | 공격 230 | 방어 140 | BRV 1,200)")
print("  적 기본 데미지: BRV 503 | HP 1,200")
print("\n  👤 플레이어 평균: BRV 714 (1.42배) | HP 1,650 (1.37배)")
print("  ✅ 결론: 플레이어가 모든 기본 공격에서 우세")

print("\n" + "="*80)
print("📋 직업별 특성 분석")
print("="*80)

# 실제 측정된 데이터 기반
job_data = {
    '시간술사': {'int_brv': 1827, 'max_brv': 1914, 'hp_dmg': 2192, 'best_skill': '시공간 붕괴', 'skill_dmg': 2411},
    '정령술사': {'int_brv': 1751, 'max_brv': 2183, 'hp_dmg': 2101, 'best_skill': '대지 정령의 분노', 'skill_dmg': 2311},
    '아크메이지': {'int_brv': 1687, 'max_brv': 2223, 'hp_dmg': 2024, 'best_skill': '라이트닝 볼트', 'skill_dmg': 1600},
    '철학자': {'int_brv': 1663, 'max_brv': 1989, 'hp_dmg': 1995, 'best_skill': '존재 부정', 'skill_dmg': 1600},
    '암살자': {'int_brv': 1631, 'max_brv': 1989, 'hp_dmg': 1957, 'best_skill': '암살술', 'skill_dmg': 3327},
    '네크로맨서': {'int_brv': 1623, 'max_brv': 2031, 'hp_dmg': 1947, 'best_skill': '죽음의 손길', 'skill_dmg': 3116},
    '도적': {'int_brv': 1561, 'max_brv': 2031, 'hp_dmg': 1873, 'best_skill': '완벽한 도둑질', 'skill_dmg': 936},
    '궁수': {'int_brv': 1507, 'max_brv': 2109, 'hp_dmg': 1808, 'best_skill': '천공의 화살', 'skill_dmg': 1627},
    '몽크': {'int_brv': 1439, 'max_brv': 2223, 'hp_dmg': 1726, 'best_skill': '철의 주먹', 'skill_dmg': 2503},
    '성직자': {'int_brv': 1429, 'max_brv': 2458, 'hp_dmg': 1714, 'best_skill': '신의 심판', 'skill_dmg': 2057},
    '용기사': {'int_brv': 1401, 'max_brv': 3192, 'hp_dmg': 1681, 'best_skill': '드래곤 스피어', 'skill_dmg': 2521},
    '성기사': {'int_brv': 1371, 'max_brv': 2614, 'hp_dmg': 1645, 'best_skill': '천사의 강림', 'skill_dmg': 1600},
    '검투사': {'int_brv': 1361, 'max_brv': 3158, 'hp_dmg': 1633, 'best_skill': '트라이던트 찌르기', 'skill_dmg': 2204},
    '사무라이': {'int_brv': 1343, 'max_brv': 3041, 'hp_dmg': 1611, 'best_skill': '오의 무상베기', 'skill_dmg': 1611},
    '검성': {'int_brv': 1337, 'max_brv': 3091, 'hp_dmg': 1604, 'best_skill': '일섬', 'skill_dmg': 1925},
    '암흑기사': {'int_brv': 1297, 'max_brv': 2983, 'hp_dmg': 1556, 'best_skill': '흡혈', 'skill_dmg': 1945},
    '전사': {'int_brv': 1283, 'max_brv': 2847, 'hp_dmg': 1539, 'best_skill': '돌진 베기', 'skill_dmg': 1600},
    '기사': {'int_brv': 1233, 'max_brv': 2691, 'hp_dmg': 1479, 'best_skill': '성스러운 돌격', 'skill_dmg': 1923},
    '광전사': {'int_brv': 1103, 'max_brv': 3467, 'hp_dmg': 1323, 'best_skill': '무모한 돌격', 'skill_dmg': 1600}
}

print("\n🏆 TOP 5 초기 BRV (빠른 브레이브 축적):")
for i, (job, data) in enumerate(sorted(job_data.items(), key=lambda x: x[1]['int_brv'], reverse=True)[:5], 1):
    print(f"  {i}. {job:8} : {data['int_brv']:,} BRV")

print("\n🏆 TOP 5 최대 BRV (브레이브 한계):")
for i, (job, data) in enumerate(sorted(job_data.items(), key=lambda x: x[1]['max_brv'], reverse=True)[:5], 1):
    print(f"  {i}. {job:8} : {data['max_brv']:,} BRV")

print("\n🏆 TOP 5 HP 공격력:")
for i, (job, data) in enumerate(sorted(job_data.items(), key=lambda x: x[1]['hp_dmg'], reverse=True)[:5], 1):
    enemy_ratio = data['hp_dmg'] / 1200
    print(f"  {i}. {job:8} : {data['hp_dmg']:,} (적 대비 {enemy_ratio:.2f}배)")

print("\n🏆 TOP 5 스킬 데미지:")
for i, (job, data) in enumerate(sorted(job_data.items(), key=lambda x: x[1]['skill_dmg'], reverse=True)[:5], 1):
    print(f"  {i}. {job:8} : {data['best_skill']} ({data['skill_dmg']:,})")

print("\n" + "="*80)
print("⚖️ 밸런스 분석")
print("="*80)

print("\n🎭 직업 분류:")
print("  🗡️ 물리 딜러 계열: 전사, 검성, 용기사, 암흑기사, 검투사, 광전사, 사무라이")
print("     → 특징: 높은 MAX BRV, 안정적인 HP 공격력")
print("     → 광전사: 극단적 스탯 (낮은 INT BRV, 최고 MAX BRV)")

print("\n  🔮 마법사 계열: 아크메이지, 네크로맨서, 정령술사, 시간술사, 철학자")  
print("     → 특징: 높은 INT BRV, 강력한 HP 공격력")
print("     → 시간술사: 최고 INT BRV, 최고 HP 공격력")

print("\n  ⚖️ 균형형: 성기사, 기사, 성직자")
print("     → 특징: 중간 수준의 모든 스탯, 지원 능력")

print("\n  🏃 민첩형: 도적, 암살자, 궁수, 몽크")
print("     → 특징: 높은 INT BRV, 낮은 MAX BRV, 특수 능력")
print("     → 암살자: 가장 강력한 스킬 데미지")

print("\n📊 전투 시스템 밸런스:")
avg_player_brv = 714
avg_player_hp = sum(data['hp_dmg'] for data in job_data.values()) / len(job_data)
enemy_brv = 503
enemy_hp = 1200

print(f"  📈 평균 BRV 공격비 (플레이어/적): {avg_player_brv/enemy_brv:.2f}")
print(f"  📈 평균 HP 공격비 (플레이어/적): {avg_player_hp/enemy_hp:.2f}")
print("\n  ✅ 결론: 전체적으로 플레이어 유리한 밸런스")
print("  ⚖️ BRV 전투: 플레이어 우세 (1.42배)")
print("  ⚖️ HP 전투: 플레이어 우세 (1.47배)")

print("\n🎯 스킬 시스템 특징:")
print("  💥 HP 공격 스킬: 대부분 1,600 고정 데미지 (현재 BRV 기반)")
print("  ⚡ BRV 공격 스킬: 공격력/방어력 비율 기반 (500-1,000 범위)")
print("  🎪 특수 스킬: 버프/디버프/치료/진실간파 등 다양한 효과")
print("  🔥 최강 스킬: 암살술(3,327), 죽음의 손길(3,116), 용기사 스피어(2,521)")

print("\n" + "="*80)
print("📝 권장사항")
print("="*80)
print("  1. 🎯 초보자 추천: 전사, 성기사 (안정적인 밸런스)")
print("  2. 🔥 고딜러 선호: 시간술사, 암살자 (높은 화력)")
print("  3. 🏃 스피드 플레이: 도적, 몽크 (빠른 BRV 축적)")
print("  4. 🧙 전략적 플레이: 철학자, 아크메이지 (다양한 스킬)")
print("  5. ⚖️ 균형잡힌 팀플레이: 성직자, 기사 (지원 능력)")

print("\n⭐ 게임의 전투 시스템이 잘 밸런싱되어 있으며,")
print("   각 직업별로 고유한 특색과 전략이 존재합니다!")
