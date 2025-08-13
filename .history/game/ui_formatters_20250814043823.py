"""
아이템 UI 포맷터 모음
- 샵/인벤토리/파티 상태에서 일관된 라인 포맷 제공
"""

from typing import Any, Optional


def _get_attr(obj: Any, name: str, default=None):
    try:
        return getattr(obj, name, default)
    except Exception:
        return default


def _to_rarity_value(rarity_obj) -> Optional[str]:
    if rarity_obj is None:
        return None
    # Enum 호환 (value/name/korean_name 등 지원)
    for attr in ("value", "korean_name", "name"):
        v = getattr(rarity_obj, attr, None)
        if v:
            return str(v)
    return str(rarity_obj)


def get_rarity_label(item: Any) -> Optional[str]:
    try:
        rarity = None
        if isinstance(item, dict):
            rarity = item.get("rarity")
        else:
            rarity = _get_attr(item, "rarity")
        if rarity is None:
            return None
        # rarity가 문자열일 수도 있음
        rarity_val = rarity if isinstance(rarity, str) else _to_rarity_value(rarity)
        return f"[{rarity_val}]" if rarity_val else None
    except Exception:
        return None


def get_durability_percent(item: Any) -> Optional[int]:
    try:
        if isinstance(item, dict):
            cur = item.get("durability") or item.get("current_durability")
            mx = item.get("max_durability")
            if cur is not None and mx:
                return int(cur * 100 / mx) if mx > 0 else None
        else:
            if hasattr(item, "get_durability_percentage"):
                try:
                    return int(item.get_durability_percentage())
                except Exception:
                    pass
            cur = _get_attr(item, "current_durability") or _get_attr(item, "durability")
            mx = _get_attr(item, "max_durability")
            if cur is not None and mx:
                return int(cur * 100 / mx) if mx > 0 else None
    except Exception:
        return None
    return None


def get_durability_emoji(pct: Optional[int]) -> str:
    if pct is None:
        return ""
    if pct > 80:
        color = "🟢"
    elif pct > 50:
        color = "🟡"
    elif pct > 20:
        color = "🟠"
    else:
        color = "🔴"
    return f"{color}{pct}%"


def get_options_summary(item: Any) -> Optional[str]:
    try:
        # dict/객체 양쪽 지원: additional_options 또는 options
        opts = None
        if isinstance(item, dict):
            opts = item.get("additional_options") or item.get("options")
        else:
            opts = _get_attr(item, "additional_options") or _get_attr(item, "options")

        if not opts:
            return None

        # dict이면 key 목록, list면 항목 수 요약
        if isinstance(opts, dict):
            names = [str(k) for k in opts.keys()]
            if not names:
                return None
            # 첫 옵션만 노출, 나머지는 개수로 요약
            if len(names) == 1:
                return f"+{names[0]}"
            return f"+{names[0]} 외 {len(names)-1}"
        elif isinstance(opts, (list, tuple)):
            if len(opts) == 0:
                return None
            first_name = str(opts[0])
            if len(opts) == 1:
                return f"+{first_name}"
            return f"+{first_name} 외 {len(opts)-1}"
        else:
            # 문자열 등 그 외 타입은 직접 표기
            return f"+{str(opts)}"
    except Exception:
        return None


def get_item_name(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("name", "아이템"))
    return str(_get_attr(item, "name", "아이템"))


def format_item_brief(item: Any) -> str:
    """이름 [희귀도] 내구도이모지% +옵션요약 형태로 간결히 포맷"""
    name = get_item_name(item)
    rarity_tag = get_rarity_label(item) or ""
    dur_pct = get_durability_percent(item)
    dur = get_durability_emoji(dur_pct)
    opt = get_options_summary(item) or ""
    parts = [name, rarity_tag, dur, opt]
    return " ".join(x for x in parts if x)
