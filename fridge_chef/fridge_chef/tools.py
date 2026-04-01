"""Tool implementations for Fridge Chef — the actions the agent can take."""

from dataclasses import dataclass

from fridge_chef.data import ChefState
from fridge_chef.game import KitchenWorld


@dataclass
class ToolResult:
    success: bool
    message: str


class KitchenTools:
    """All tools the kitchen agent can use each turn."""

    def __init__(self, chef: ChefState, world: KitchenWorld):
        self.chef = chef
        self.world = world

    # ------------------------------------------------------------------
    # Tool: check_fridge
    # ------------------------------------------------------------------
    def check_fridge(self) -> ToolResult:
        """See what's in the fridge."""
        contents = self.world.get_fridge_contents()
        self.chef.fridge_contents = list(contents)
        items = "\n".join(f"  - {item}" for item in contents)
        return ToolResult(True,
            f"Your fridge contains {len(contents)} items:\n{items}"
        )

    # ------------------------------------------------------------------
    # Tool: search_recipes
    # ------------------------------------------------------------------
    def search_recipes(self, ingredient: str = "") -> ToolResult:
        """Search for recipes that use a given ingredient."""
        ingredient = ingredient.strip()
        if not ingredient:
            return ToolResult(False, "Please specify an ingredient to search for.")

        recipes = self.world.search_recipes(ingredient)
        if not recipes:
            return ToolResult(True,
                f"No recipes found for '{ingredient}'. "
                "Try searching for a different ingredient from your fridge."
            )

        self.chef.possible_recipes = list(recipes)
        recipe_list = "\n".join(f"  - {r}" for r in recipes)
        self.chef.notes.append(f"Found {len(recipes)} recipes for {ingredient}")
        return ToolResult(True,
            f"Recipes using '{ingredient}':\n{recipe_list}"
        )

    # ------------------------------------------------------------------
    # Tool: get_ingredients
    # ------------------------------------------------------------------
    def get_ingredients(self, recipe: str = "") -> ToolResult:
        """Get the full ingredient list for a recipe."""
        recipe = recipe.strip()
        if not recipe:
            return ToolResult(False, "Please specify a recipe name.")

        ingredients = self.world.get_recipe_ingredients(recipe)
        if not ingredients:
            return ToolResult(False,
                f"Recipe '{recipe}' not found. Use search_recipes() to find valid recipes."
            )

        self.chef.chosen_recipe = recipe
        self.chef.needed_ingredients = list(ingredients)

        # Determine what's missing from the fridge
        fridge_lower = [item.lower() for item in self.chef.fridge_contents]
        have = []
        missing = []
        for ing in ingredients:
            if ing.lower() in fridge_lower:
                have.append(ing)
            else:
                missing.append(ing)

        have_str = ", ".join(have) if have else "(none)"
        missing_str = ", ".join(missing) if missing else "(none — you have everything!)"

        self.chef.notes.append(f"Checked ingredients for {recipe}: {len(missing)} missing")
        return ToolResult(True,
            f"To make '{recipe}' you need:\n"
            f"  All ingredients: {', '.join(ingredients)}\n\n"
            f"  You have: {have_str}\n"
            f"  Missing: {missing_str}"
        )

    # ------------------------------------------------------------------
    # Tool: add_to_shopping_list
    # ------------------------------------------------------------------
    def add_to_shopping_list(self, item: str = "") -> ToolResult:
        """Add a missing ingredient to the shopping list."""
        item = item.strip()
        if not item:
            return ToolResult(False, "Please specify an item to add.")

        item_lower = item.lower()

        # Check if already in fridge
        fridge_lower = [f.lower() for f in self.chef.fridge_contents]
        if item_lower in fridge_lower:
            return ToolResult(False,
                f"'{item}' is already in your fridge! No need to buy it."
            )

        # Check if already on shopping list
        shopping_lower = [s.lower() for s in self.chef.shopping_list]
        if item_lower in shopping_lower:
            return ToolResult(False,
                f"'{item}' is already on your shopping list."
            )

        self.chef.shopping_list.append(item)
        self.chef.notes.append(f"Added {item} to shopping list")
        return ToolResult(True,
            f"Added '{item}' to shopping list. "
            f"Shopping list now has {len(self.chef.shopping_list)} item(s): "
            f"{', '.join(self.chef.shopping_list)}"
        )

    # ------------------------------------------------------------------
    # Tool: done
    # ------------------------------------------------------------------
    def done(self) -> ToolResult:
        """Signal that you're done — recipe chosen and shopping list ready."""
        if not self.chef.chosen_recipe:
            return ToolResult(False,
                "You haven't chosen a recipe yet! Use get_ingredients() to pick one."
            )

        self.chef.shopping_done = True

        if self.chef.shopping_list:
            items = ", ".join(self.chef.shopping_list)
            msg = (
                f"All done! You're making '{self.chef.chosen_recipe}'.\n"
                f"Shopping list ({len(self.chef.shopping_list)} items): {items}\n"
                f"Head to the store and then start cooking!"
            )
        else:
            msg = (
                f"All done! You're making '{self.chef.chosen_recipe}'.\n"
                f"You have everything you need — start cooking!"
            )

        self.chef.notes.append(f"Done! Recipe: {self.chef.chosen_recipe}")
        return ToolResult(True, msg)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def execute(self, tool_name: str, args: dict) -> ToolResult:
        """Execute a tool by name with given arguments."""
        tool_map = {
            "check_fridge": lambda: self.check_fridge(),
            "search_recipes": lambda: self.search_recipes(args.get("ingredient", "")),
            "get_ingredients": lambda: self.get_ingredients(args.get("recipe", "")),
            "add_to_shopping_list": lambda: self.add_to_shopping_list(args.get("item", "")),
            "done": lambda: self.done(),
        }

        fn = tool_map.get(tool_name.lower().strip())
        if fn is None:
            return ToolResult(False,
                f"Unknown tool '{tool_name}'. Available: {', '.join(tool_map.keys())}"
            )

        return fn()
