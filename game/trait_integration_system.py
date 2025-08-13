"""
호환 레이어: 기존 코드가 import 하는 trait_integration_system를 제공
현재 실제 구현은 trait_combat_integration로 이관됨. 여기선 래핑만 제공합니다.
"""
from __future__ import annotations

from typing import Any

from .trait_combat_integration import TraitCombatIntegrator as _Impl


def get_trait_processor() -> _Impl:
    return _Impl()


def apply_trait_effects_to_damage(caster: Any, target: Any, base_damage: int, damage_type: str) -> int:
    # 단일 통합 데미지 훅이 필요하면 여기서 분기 가능
    return _Impl.apply_attack_trait_effects(caster, target, base_damage)


def apply_trait_effects_to_defense(target: Any, incoming_damage: int, damage_type: str) -> int:
    return _Impl.apply_defense_trait_effects(target, incoming_damage)


def trigger_special_abilities(caster: Any, target: Any):
    # 필요 시 특수 능력 트리거 연결. 현재는 no-op
    return None
