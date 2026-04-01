"""Data models for Fridge Chef — state tracking for the kitchen agent."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChefState:
    """The kitchen agent's current state — what it knows and has decided."""
    fridge_contents: list[str] = field(default_factory=list)
    possible_recipes: list[str] = field(default_factory=list)
    chosen_recipe: str = ""
    needed_ingredients: list[str] = field(default_factory=list)
    shopping_list: list[str] = field(default_factory=list)
    shopping_done: bool = False
    notes: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """True when the agent has finished (called done)."""
        return self.shopping_done

    def status_text(self) -> str:
        recipe_info = self.chosen_recipe or "(none yet)"
        shopping = ", ".join(self.shopping_list) if self.shopping_list else "(empty)"
        return (
            f"Recipe: {recipe_info} | "
            f"Shopping list: {shopping} | "
            f"Complete: {self.is_complete}"
        )
