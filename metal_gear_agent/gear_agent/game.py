"""Operative state management for Metal Gear Agent."""

from dataclasses import dataclass, field


@dataclass
class OperativeState:
    """The player character in Metal Gear Agent."""

    health: int = 3
    intel: int = 0
    inventory: list[str] = field(default_factory=list)
    position: tuple[int, int] = (7, 0)
    visited: set[tuple[int, int]] = field(default_factory=lambda: {(7, 0)})
    briefing_log: list[str] = field(default_factory=list)

    MAX_HEALTH = 3
    WIN_INTEL = 10

    def has_item(self, name: str) -> bool:
        return name in self.inventory

    def add_item(self, name: str) -> None:
        self.inventory.append(name)

    def remove_item(self, name: str) -> bool:
        if name in self.inventory:
            self.inventory.remove(name)
            return True
        return False

    def add_intel(self, amount: int) -> None:
        self.intel += amount

    def spend_intel(self, amount: int) -> bool:
        if self.intel >= amount:
            self.intel -= amount
            return True
        return False

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    def heal(self, amount: int) -> None:
        self.health = min(self.MAX_HEALTH, self.health + amount)

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    @property
    def has_won(self) -> bool:
        return self.intel >= self.WIN_INTEL and self.is_alive

    def status_text(self) -> str:
        inv = ", ".join(self.inventory) if self.inventory else "empty"
        return (
            f"Health: {self.health}/{self.MAX_HEALTH} | "
            f"Intel: {self.intel} | "
            f"Position: {self.position} | "
            f"Inventory: [{inv}] | "
            f"Visited: {len(self.visited)} cells"
        )
