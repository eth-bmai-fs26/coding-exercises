"""Hero state management for Quest Hero."""

from dataclasses import dataclass, field


@dataclass
class Hero:
    """The player character in Quest Hero."""

    hearts: int = 3
    gold: int = 0
    inventory: list[str] = field(default_factory=list)
    position: tuple[int, int] = (7, 0)
    visited: set[tuple[int, int]] = field(default_factory=lambda: {(7, 0)})
    journal: list[str] = field(default_factory=list)

    MAX_HEARTS = 3
    WIN_GOLD = 10

    def has_item(self, name: str) -> bool:
        return name in self.inventory

    def add_item(self, name: str) -> None:
        self.inventory.append(name)

    def remove_item(self, name: str) -> bool:
        if name in self.inventory:
            self.inventory.remove(name)
            return True
        return False

    def add_gold(self, amount: int) -> None:
        self.gold += amount

    def spend_gold(self, amount: int) -> bool:
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def take_damage(self, amount: int) -> None:
        self.hearts = max(0, self.hearts - amount)

    def heal(self, amount: int) -> None:
        self.hearts = min(self.MAX_HEARTS, self.hearts + amount)

    @property
    def is_alive(self) -> bool:
        return self.hearts > 0

    @property
    def has_won(self) -> bool:
        return self.gold >= self.WIN_GOLD and self.is_alive

    def status_text(self) -> str:
        inv = ", ".join(self.inventory) if self.inventory else "empty"
        return (
            f"Hearts: {self.hearts}/{self.MAX_HEARTS} | "
            f"Gold: {self.gold} | "
            f"Position: {self.position} | "
            f"Inventory: [{inv}] | "
            f"Visited: {len(self.visited)} cells"
        )
