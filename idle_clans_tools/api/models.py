"""Data models for Idle Clans API responses.

All models use dataclasses with type hints so they're easy to extend and
introspect.  The ``from_dict`` class-methods accept the raw JSON dicts
returned by the API and pull out only the fields we care about; unknown keys
are ignored so the models stay forward-compatible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _get_first(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return None


# ---------------------------------------------------------------------------
# Player models
# ---------------------------------------------------------------------------


@dataclass
class PlayerProfile:
    """Profile information for a single player."""

    username: str
    game_mode: str | None
    clan_name: str | None
    total_experience: int
    combat_level: int
    skills: dict[str, int] = field(default_factory=dict)
    equipment: dict[str, int] = field(default_factory=dict)
    enchantment_boosts: dict[str, int] = field(default_factory=dict)
    upgrades: dict[str, int] = field(default_factory=dict)
    pvm_stats: dict[str, int] = field(default_factory=dict)
    hours_offline: int | float | None = None
    task_type_on_logout: int | None = None
    task_name_on_logout: str | None = None
    active_server_id: str | int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlayerProfile:
        # The API currently exposes player skill xp under "skillExperiences".
        skills = _numeric_map(data.get("skills") or data.get("skillExperiences"))

        total_experience = data.get("totalExperience")
        if not isinstance(total_experience, (int, float)):
            total_experience = sum(skills.values())

        return cls(
            username=data.get("username", ""),
            game_mode=data.get("gameMode"),
            clan_name=data.get("clanName") or data.get("guildName"),
            total_experience=int(total_experience),
            combat_level=int(data.get("combatLevel", 0) or 0),
            skills=skills,
            equipment=_numeric_map(data.get("equipment")),
            enchantment_boosts=_numeric_map(data.get("enchantmentBoosts")),
            upgrades=_numeric_map(data.get("upgrades")),
            pvm_stats=_numeric_map(data.get("pvmStats")),
            hours_offline=_optional_number(data.get("hoursOffline")),
            task_type_on_logout=_optional_int(data.get("taskTypeOnLogout")),
            task_name_on_logout=data.get("taskNameOnLogout"),
            active_server_id=data.get("activeServerId"),
        )


def _numeric_map(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {
        str(name): int(raw_value)
        for name, raw_value in value.items()
        if isinstance(raw_value, (int, float))
    }


def _optional_int(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    return None


def _optional_number(value: Any) -> int | float | None:
    if not isinstance(value, (int, float)):
        return None
    if isinstance(value, float) and not value.is_integer():
        return value
    return int(value)


# ---------------------------------------------------------------------------
# Clan models
# ---------------------------------------------------------------------------


@dataclass
class ClanInfo:
    """Basic information about a clan."""

    name: str
    leader: str
    member_count: int
    total_experience: int
    description: str | None
    is_recruiting: bool | None = None
    language: str | None = None
    category: str | None = None
    tag: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClanInfo:
        description = data.get("description") or data.get("recruitmentMessage")
        return cls(
            name=data.get("name") or data.get("clanName", ""),
            leader=data.get("leader", ""),
            member_count=data.get("memberCount", 0),
            total_experience=data.get("totalExperience", 0),
            description=description,
            is_recruiting=data.get("isRecruiting"),
            language=data.get("language"),
            category=data.get("category"),
            tag=data.get("tag"),
        )


@dataclass
class ClanMember:
    """A single member entry inside a clan's member list."""

    username: str
    rank: str
    total_experience: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClanMember:
        rank = data.get("rank")
        if rank is None:
            rank = data.get("memberRank", "")
        return cls(
            username=data.get("username") or data.get("memberName", ""),
            rank=str(rank or ""),
            total_experience=int(data.get("totalExperience", 0) or 0),
        )


# ---------------------------------------------------------------------------
# Leaderboard models
# ---------------------------------------------------------------------------


@dataclass
class LeaderboardEntry:
    """A single entry on a leaderboard."""

    rank: int
    username: str
    value: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LeaderboardEntry:
        username = data.get("username") or data.get("name") or data.get("clanName", "")
        value = data.get("value")
        if not isinstance(value, (int, float)):
            value = data.get("totalExperience")
        if not isinstance(value, (int, float)):
            fields = data.get("fields")
            if isinstance(fields, dict):
                field_value = next(iter(fields.values()), 0)
                if isinstance(field_value, (int, float)):
                    value = field_value
        if not isinstance(value, (int, float)):
            value = 0

        return cls(
            rank=data.get("rank", 0),
            username=str(username),
            value=int(value),
        )


# ---------------------------------------------------------------------------
# Market / item models
# ---------------------------------------------------------------------------


@dataclass
class MarketItem:
    """A single item listing on the player market."""

    item_id: int
    item_name: str
    price: int
    quantity: int
    seller: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MarketItem:
        price = data.get("price")
        if not isinstance(price, (int, float)):
            price = data.get("lowestPrice")
        if not isinstance(price, (int, float)):
            price = data.get("avgPrice24h")
        if not isinstance(price, (int, float)):
            price = 0

        quantity = data.get("quantity")
        if not isinstance(quantity, (int, float)):
            quantity = data.get("volume")
        if not isinstance(quantity, (int, float)):
            quantity = data.get("tradeVolume1d")
        if not isinstance(quantity, (int, float)):
            quantity = 0

        return cls(
            item_id=data.get("itemId", 0),
            item_name=data.get("itemName") or data.get("name", ""),
            price=int(price),
            quantity=int(quantity),
            seller=data.get("seller"),
        )


@dataclass
class GameItem:
    """Static item metadata from the game-data endpoint."""

    item_id: int
    name: str
    base_value: int
    category: int | None = None
    equipment_slot: int | None = None
    associated_skill: int | None = None
    is_tool: bool | None = None
    discontinued: bool | None = None
    unobtainable: bool | None = None

    @property
    def display_name(self) -> str:
        return self.name.replace("_", " ").title()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameItem:
        return cls(
            item_id=_optional_int(_get_first(data, "ItemId", "itemId")) or 0,
            name=str(_get_first(data, "Name", "itemName", "name") or ""),
            base_value=_optional_int(_get_first(data, "BaseValue", "baseValue")) or 0,
            category=_optional_int(_get_first(data, "Category", "category")),
            equipment_slot=_optional_int(_get_first(data, "EquipmentSlot", "equipmentSlot")),
            associated_skill=_optional_int(_get_first(data, "AssociatedSkill", "associatedSkill")),
            is_tool=_optional_bool(_get_first(data, "IsTool", "isTool")),
            discontinued=_optional_bool(_get_first(data, "Discontinued", "discontinued")),
            unobtainable=_optional_bool(_get_first(data, "Unobtainable", "unobtainable")),
        )
