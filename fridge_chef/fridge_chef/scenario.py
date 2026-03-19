"""Scenario data for Fridge Chef — what's in the fridge and what can you cook."""


# ---------------------------------------------------------------------------
# Fridge contents — 12 items the player starts with
# ---------------------------------------------------------------------------

FRIDGE_CONTENTS = [
    "eggs",
    "milk",
    "butter",
    "cheddar cheese",
    "bread",
    "tomatoes",
    "onions",
    "garlic",
    "bell pepper",
    "chicken breast",
    "rice",
    "soy sauce",
]


# ---------------------------------------------------------------------------
# Recipe database — ingredient → list of recipes that use it
# Built automatically from INGREDIENTS_DB so every ingredient is searchable.
# ---------------------------------------------------------------------------

def _build_recipe_db(ingredients_db: dict[str, list[str]]) -> dict[str, list[str]]:
    """Invert INGREDIENTS_DB: for each ingredient, list every recipe that uses it."""
    db: dict[str, list[str]] = {}
    for recipe, ingredients in ingredients_db.items():
        for ingredient in ingredients:
            db.setdefault(ingredient, []).append(recipe)
    return db


# ---------------------------------------------------------------------------
# Ingredients database — recipe → full list of ingredients needed
# ---------------------------------------------------------------------------

INGREDIENTS_DB = {
    "omelette": ["eggs", "butter", "cheddar cheese", "bell pepper", "onions", "salt", "pepper"],
    "fried rice": ["rice", "eggs", "soy sauce", "onions", "garlic", "sesame oil", "green onions"],
    "french toast": ["bread", "eggs", "milk", "butter", "cinnamon", "sugar", "vanilla extract"],
    "egg salad sandwich": ["eggs", "bread", "mayonnaise", "mustard", "salt", "pepper"],
    "shakshuka": ["eggs", "tomatoes", "onions", "garlic", "bell pepper", "cumin", "paprika", "olive oil"],
    "carbonara": ["pasta", "eggs", "parmesan cheese", "pancetta", "black pepper", "garlic"],
    "pancakes": ["flour", "milk", "eggs", "butter", "sugar", "baking powder", "salt"],
    "grilled cheese": ["bread", "butter", "cheddar cheese"],
    "garlic bread": ["bread", "butter", "garlic", "parsley"],
    "mac and cheese": ["pasta", "milk", "cheddar cheese", "butter", "flour", "salt"],
    "bruschetta": ["bread", "tomatoes", "garlic", "olive oil", "basil", "salt"],
    "tomato soup": ["tomatoes", "onions", "garlic", "butter", "cream", "basil", "salt", "pepper"],
    "stir fry": ["bell pepper", "onions", "garlic", "soy sauce", "sesame oil", "cornstarch"],
    "chicken stir fry": ["chicken breast", "bell pepper", "soy sauce", "garlic", "onions", "sesame oil", "cornstarch", "ginger"],
    "chicken fried rice": ["chicken breast", "rice", "eggs", "soy sauce", "onions", "garlic", "sesame oil"],
    "chicken quesadilla": ["chicken breast", "cheddar cheese", "tortilla", "bell pepper", "onions", "salsa"],
    "grilled chicken salad": ["chicken breast", "lettuce", "tomatoes", "cucumber", "olive oil", "lemon juice"],
    "chicken curry": ["chicken breast", "rice", "onions", "garlic", "coconut milk", "curry powder", "ginger"],
    "rice bowl": ["rice", "soy sauce", "sesame oil", "green onions", "egg"],
    "stuffed peppers": ["bell pepper", "rice", "tomatoes", "onions", "cheddar cheese", "ground beef"],
    "fajitas": ["bell pepper", "onions", "chicken breast", "tortilla", "lime", "cumin", "chili powder"],
    "pasta alfredo": ["pasta", "butter", "garlic", "parmesan cheese", "cream", "salt", "pepper"],
    "quesadilla": ["tortilla", "cheddar cheese", "salsa"],
    "caprese salad": ["tomatoes", "mozzarella", "basil", "olive oil", "balsamic vinegar"],
    "salsa": ["tomatoes", "onions", "garlic", "jalapeno", "cilantro", "lime juice"],
    "french onion soup": ["onions", "butter", "beef broth", "bread", "gruyere cheese", "thyme"],
    "teriyaki chicken": ["chicken breast", "soy sauce", "sugar", "garlic", "ginger", "cornstarch"],
    "spaghetti bolognese": ["pasta", "ground beef", "tomatoes", "onions", "garlic", "olive oil", "basil"],
}

RECIPE_DB = _build_recipe_db(INGREDIENTS_DB)
