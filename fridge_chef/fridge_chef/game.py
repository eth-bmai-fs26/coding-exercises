"""Game engine for Fridge Chef — manages the kitchen simulation state."""

import copy
import random

from fridge_chef.data import ChefState
from fridge_chef.scenario import RECIPE_DB, INGREDIENTS_DB

FRIDGE_SIZE = 12


class KitchenWorld:
    """The kitchen simulation — manages fridge, recipe lookups, and shopping."""

    def __init__(self, seed: int | None = None):
        rng = random.Random(seed)
        all_ingredients = sorted({i for items in INGREDIENTS_DB.values() for i in items})
        self.fridge: list[str] = rng.sample(all_ingredients, FRIDGE_SIZE)
        self.recipe_db: dict[str, list[str]] = copy.deepcopy(RECIPE_DB)
        self.ingredients_db: dict[str, list[str]] = copy.deepcopy(INGREDIENTS_DB)

    def get_fridge_contents(self) -> list[str]:
        return list(self.fridge)

    def search_recipes(self, ingredient: str) -> list[str]:
        """Find recipes that use a given ingredient."""
        ingredient_lower = ingredient.lower().strip()
        for key, recipes in self.recipe_db.items():
            if key.lower() == ingredient_lower:
                return list(recipes)
        return []

    def get_recipe_ingredients(self, recipe: str) -> list[str]:
        """Get the full ingredient list for a recipe."""
        recipe_lower = recipe.lower().strip()
        for key, ingredients in self.ingredients_db.items():
            if key.lower() == recipe_lower:
                return list(ingredients)
        return []

    def fridge_summary(self) -> str:
        if not self.fridge:
            return "Your fridge is empty!"
        items = ", ".join(self.fridge)
        return f"Fridge ({len(self.fridge)} items): {items}"
