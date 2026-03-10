"""Game world: map, cells, NPCs, items, and quest data for Quest Hero."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Cell types
# ---------------------------------------------------------------------------

class CellType(Enum):
    OPEN = "open"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    TREASURE = "treasure"
    NPC = "npc"
    SHOP = "shop"
    INN = "inn"
    DRAGON = "dragon"
    CASTLE = "castle"

    @property
    def emoji(self) -> str:
        return {
            CellType.OPEN: "·",
            CellType.FOREST: "\U0001f332",      # 🌲
            CellType.MOUNTAIN: "\u26f0\ufe0f",   # ⛰️
            CellType.TREASURE: "\U0001f48e",     # 💎
            CellType.NPC: "\U0001f9d9",          # 🧙
            CellType.SHOP: "\U0001f3ea",         # 🏪
            CellType.INN: "\U0001f3da\ufe0f",    # 🏚️
            CellType.DRAGON: "\U0001f409",       # 🐉
            CellType.CASTLE: "\U0001f3f0",       # 🏰
        }[self]

    @property
    def label(self) -> str:
        return {
            CellType.OPEN: "Open path",
            CellType.FOREST: "Forest",
            CellType.MOUNTAIN: "Mountain (impassable)",
            CellType.TREASURE: "Treasure",
            CellType.NPC: "NPC",
            CellType.SHOP: "Shop",
            CellType.INN: "Inn",
            CellType.DRAGON: "Dragon",
            CellType.CASTLE: "Castle",
        }[self]


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

@dataclass
class Item:
    name: str
    description: str
    quest_item: bool = False


ITEM_CATALOG: dict[str, Item] = {
    # Quest materials
    "Ember Ore": Item("Ember Ore", "A glowing ore that radiates heat.", quest_item=True),
    "Ghostcaps": Item("Ghostcaps", "Pale mushrooms that glow faintly in the dark.", quest_item=True),
    "Medicine": Item("Medicine", "A herbal remedy brewed by the Forest Witch.", quest_item=True),
    "Moonstone": Item("Moonstone", "A luminous stone that glows like the moon.", quest_item=True),
    "Herbal Tea": Item("Herbal Tea", "A soothing tea from the Southern Inn.", quest_item=True),
    "Letter": Item("Letter", "A sealed letter from the Traveling Merchant.", quest_item=True),
    # Weapons
    "Sunblade": Item("Sunblade", "A fiery sword forged from Ember Ore. Effective against ice creatures.", quest_item=True),
    "Moonstone Lantern": Item("Moonstone Lantern", "A lantern radiating pure moonlight. Effective against shadow creatures.", quest_item=True),
    # Loot
    "Dragon Scales": Item("Dragon Scales", "Shimmering scales from a slain dragon. Valuable to enchanters."),
    # Consumables
    "Bread": Item("Bread", "Simple bread. Restores 1 heart."),
    "Health Potion": Item("Health Potion", "A potent potion. Restores 2 hearts."),
}


# ---------------------------------------------------------------------------
# NPCs
# ---------------------------------------------------------------------------

@dataclass
class NPC:
    name: str
    personality: str
    knowledge: list[str]
    style: str
    greeting: str


NPC_CATALOG: dict[str, NPC] = {
    "old_hermit": NPC(
        name="Old Hermit",
        personality="Cryptic, poetic, speaks in riddles and metaphors. Ancient and wise.",
        knowledge=[
            "The Frost Wyrm lurks in the north (around row 2). It is a creature of ice.",
            "Only a weapon of fire can defeat the Frost Wyrm - 'summer's fury'.",
            "A dwarf blacksmith in the southern markets can forge wondrous weapons, but he needs special ore.",
            "There is treasure nearby to the southwest.",
            "The Forest Witch in the center of the land knows where to find rare materials.",
        ],
        style="Speaks in riddles and poetic metaphors. Uses phrases like 'the cold one', 'summer's fury', 'the burning stones'. Never gives direct coordinates.",
        greeting="Ah, a traveler... The winds whisper of your coming. Sit, and I shall speak of shadows and flame.",
    ),
    "traveling_merchant": NPC(
        name="Traveling Merchant",
        personality="Fast-talking salesman, charismatic, always looking for a deal. Drops hints to sell things.",
        knowledge=[
            "The Shadow Beast lurks in the eastern ruins (around row 4, eastern side). It devours light.",
            "Only pure moonlight can drive the Shadow Beast back.",
            "The innkeeper's wife at the Northern Inn once had a stone that glowed like the moon itself.",
            "There are shops to the south and north that sell useful supplies.",
            "He has a letter that needs delivering to the Old Hermit to the south. Will pay 2 gold for delivery.",
        ],
        style="Fast-talking, uses sales language. Calls the hero 'friend' or 'good customer'. Mentions prices and deals. Never gives direct coordinates.",
        greeting="Well well well! A customer! Or perhaps... a business partner? I have goods, information, and a job for the right adventurer!",
    ),
    "forest_witch": NPC(
        name="Forest Witch",
        personality="Mysterious, speaks about nature, never gives straight directions. Knowledgeable about herbs and materials.",
        knowledge=[
            "Ember Ore can be found in the forest to the northwest, where the western trees grow tallest (the forest at row 2, column 0).",
            "Ghostcap mushrooms grow in the dark forests far to the north (the forest at row 0, column 2).",
            "She can brew medicine from Ghostcaps to heal the sick.",
            "The Northern Innkeeper's wife is ill and needs medicine.",
            "Both the blacksmith and the enchanter can craft powerful weapons from rare materials.",
        ],
        style="Mysterious and nature-focused. Uses phrases like 'the burning stones sleep where...', 'the pale caps grow in shadow'. References plants, seasons, and elements. Never gives direct coordinates.",
        greeting="The forest told me you would come... The roots whisper, the leaves know. Ask, child, and nature shall answer.",
    ),
}


# ---------------------------------------------------------------------------
# Shops and Inns
# ---------------------------------------------------------------------------

@dataclass
class ShopInfo:
    name: str
    description: str
    sells: dict[str, int]           # item_name -> gold cost
    crafts: dict[str, tuple[str, int]]  # result_item -> (required_item, gold_cost)
    buys: dict[str, int]            # item_name -> gold earned


SHOP_CATALOG: dict[tuple[int, int], ShopInfo] = {
    (6, 2): ShopInfo(
        name="Dwarf Blacksmith",
        description="A stout dwarf works the forge, sparks flying. He sells bread and can forge special weapons.",
        sells={"Bread": 1},
        crafts={"Sunblade": ("Ember Ore", 2)},
        buys={},
    ),
    (4, 1): ShopInfo(
        name="Enchanter Shop",
        description="A mysterious shop filled with glowing crystals and arcane instruments.",
        sells={"Health Potion": 2},
        crafts={"Moonstone Lantern": ("Moonstone", 1)},
        buys={"Dragon Scales": 1},
    ),
}


@dataclass
class InnInfo:
    name: str
    description: str
    gives_item: Optional[str] = None  # quest item given on first visit
    needs_item: Optional[str] = None  # quest item the innkeeper wants
    reward_item: Optional[str] = None  # what you get for delivering needs_item
    reward_gold: int = 0


INN_CATALOG: dict[tuple[int, int], InnInfo] = {
    (7, 4): InnInfo(
        name="Southern Inn",
        description="A cozy inn with a warm fireplace. The innkeeper looks worried about his brother up north.",
        gives_item="Herbal Tea",
    ),
    (2, 5): InnInfo(
        name="Northern Inn",
        description="A quiet inn. The innkeeper looks tired and worried about his sick wife.",
        needs_item="Medicine",
        reward_item="Moonstone",
        reward_gold=0,
    ),
}


# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------

@dataclass
class Cell:
    cell_type: CellType
    items: list[str] = field(default_factory=list)  # item names
    npc_id: Optional[str] = None
    dragon_name: Optional[str] = None
    trap: bool = False
    shop_pos: Optional[tuple[int, int]] = None
    inn_pos: Optional[tuple[int, int]] = None
    description: str = ""

    @property
    def npc(self) -> Optional[NPC]:
        if self.npc_id:
            return NPC_CATALOG.get(self.npc_id)
        return None


# ---------------------------------------------------------------------------
# Errand tracking
# ---------------------------------------------------------------------------

@dataclass
class ErrandInfo:
    name: str
    pickup_item: str
    pickup_location: tuple[int, int]
    deliver_item: str
    deliver_to_npc: str
    deliver_location: tuple[int, int]
    reward_gold: int


ERRANDS: dict[str, ErrandInfo] = {
    "medicine_delivery": ErrandInfo(
        name="Medicine Delivery",
        pickup_item="Herbal Tea",
        pickup_location=(7, 4),
        deliver_item="Herbal Tea",
        deliver_to_npc="Northern Innkeeper",
        deliver_location=(2, 5),
        reward_gold=2,
    ),
    "letter_delivery": ErrandInfo(
        name="Letter Delivery",
        pickup_item="Letter",
        pickup_location=(5, 3),  # Merchant gives it via talk
        deliver_item="Letter",
        deliver_to_npc="Old Hermit",
        deliver_location=(7, 1),
        reward_gold=2,
    ),
}


# ---------------------------------------------------------------------------
# Game World
# ---------------------------------------------------------------------------

class GameWorld:
    """8x8 RPG grid world."""

    ROWS = 8
    COLS = 8

    def __init__(self):
        self.grid: list[list[Cell]] = []
        self.errand_tea_picked_up = False
        self.errand_tea_delivered = False
        self.errand_letter_picked_up = False
        self.errand_letter_delivered = False
        self.medicine_given_to_witch = False
        self.medicine_received = False
        self.moonstone_received = False
        self.frost_wyrm_alive = True
        self.shadow_beast_alive = True
        self.build_map()

    def build_map(self):
        """Construct the 8x8 grid exactly as specified."""
        # Initialize with open cells
        self.grid = [
            [Cell(CellType.OPEN) for _ in range(self.COLS)]
            for _ in range(self.ROWS)
        ]

        # Row 0: 🏰 · 🌲 · · 🌲 · 💎
        self._set(0, 0, Cell(CellType.CASTLE, description="An ancient castle stands tall, its banners fluttering in the wind."))
        self._set(0, 2, Cell(CellType.FOREST, items=["Ghostcaps"], description="A dark, dense forest. Strange pale mushrooms grow in the shadows."))
        self._set(0, 5, Cell(CellType.FOREST, trap=True, description="A thick forest with hidden snares among the undergrowth."))
        self._set(0, 7, Cell(CellType.TREASURE, items=["gold_1"], description="A glint of gold catches your eye among the rocks!"))

        # Row 1: · · · ⛰️ · · · ·
        self._set(1, 3, Cell(CellType.MOUNTAIN, description="An impassable mountain peak."))

        # Row 2: 🌲 🐉₁ · ⛰️ · 🏚️₂ · 🌲
        self._set(2, 0, Cell(CellType.FOREST, items=["Ember Ore"], description="A forest of towering western trees. The ground radiates faint warmth."))
        self._set(2, 1, Cell(CellType.DRAGON, dragon_name="Frost Wyrm", description="A chilling mist fills the air. The Frost Wyrm awaits, its icy breath visible."))
        self._set(2, 3, Cell(CellType.MOUNTAIN, description="An impassable mountain peak."))
        self._set(2, 5, Cell(CellType.INN, inn_pos=(2, 5), description="The Northern Inn. The innkeeper looks weary and troubled."))
        self._set(2, 7, Cell(CellType.FOREST, description="A peaceful forest clearing. Birds sing overhead."))

        # Row 3: · · · · 🧙₃ · · ·
        self._set(3, 4, Cell(CellType.NPC, npc_id="forest_witch", description="A small hut surrounded by herbs and strange plants."))

        # Row 4: · 🏪₂ · ⛰️ · · 🐉₂ ·
        self._set(4, 1, Cell(CellType.SHOP, shop_pos=(4, 1), description="The Enchanter Shop glows with arcane energy."))
        self._set(4, 3, Cell(CellType.MOUNTAIN, description="An impassable mountain peak."))
        self._set(4, 6, Cell(CellType.DRAGON, dragon_name="Shadow Beast", description="Darkness pools unnaturally here. The Shadow Beast lurks in the gloom."))

        # Row 5: 💎 · · 🧙₂ · 🌲 · ·
        self._set(5, 0, Cell(CellType.TREASURE, items=["gold_1"], description="A small treasure chest sits half-buried in the dirt!"))
        self._set(5, 3, Cell(CellType.NPC, npc_id="traveling_merchant", description="A colorful wagon is parked here. A merchant waves you over."))
        self._set(5, 5, Cell(CellType.FOREST, description="A quiet forest. Nothing unusual here."))

        # Row 6: · · 🏪₁ · · · 💎 ·
        self._set(6, 2, Cell(CellType.SHOP, shop_pos=(6, 2), description="The Dwarf Blacksmith's forge roars with heat."))
        self._set(6, 6, Cell(CellType.TREASURE, items=["gold_1"], description="Gold coins scattered on the ground!"))

        # Row 7: 🦸 🧙₁ · · 🏚️₁ · · 🌲
        # (7,0) is the hero start — just open
        self._set(7, 0, Cell(CellType.OPEN, description="The starting clearing. Familiar ground."))
        self._set(7, 1, Cell(CellType.NPC, npc_id="old_hermit", description="A weathered hut sits beneath an ancient oak. An old man meditates outside."))
        self._set(7, 4, Cell(CellType.INN, inn_pos=(7, 4), description="The Southern Inn. Warm light spills from the windows."))
        self._set(7, 7, Cell(CellType.FOREST, description="A forest at the edge of the world. The trees thin out here."))

    def _set(self, row: int, col: int, cell: Cell):
        self.grid[row][col] = cell

    def get_cell(self, row: int, col: int) -> Cell:
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            return self.grid[row][col]
        return Cell(CellType.MOUNTAIN, description="The edge of the world.")

    def is_passable(self, row: int, col: int) -> bool:
        if not (0 <= row < self.ROWS and 0 <= col < self.COLS):
            return False
        return self.grid[row][col].cell_type != CellType.MOUNTAIN

    def get_adjacent(self, row: int, col: int) -> dict[str, Optional[Cell]]:
        """Return adjacent cells keyed by direction."""
        directions = {
            "north": (row - 1, col),
            "south": (row + 1, col),
            "east": (row, col + 1),
            "west": (row, col - 1),
        }
        result = {}
        for direction, (r, c) in directions.items():
            if 0 <= r < self.ROWS and 0 <= c < self.COLS:
                result[direction] = self.grid[r][c]
            else:
                result[direction] = None  # out of bounds
        return result

    def get_visible_description(self, row: int, col: int) -> str:
        """Return a text description of what the hero can see from (row, col)."""
        lines = []
        current = self.get_cell(row, col)
        lines.append(f"You are at position ({row}, {col}).")
        if current.description:
            lines.append(f"Current location: {current.description}")

        adjacent = self.get_adjacent(row, col)
        for direction, cell in adjacent.items():
            if cell is None:
                lines.append(f"  {direction.capitalize()}: Edge of the world (impassable).")
            else:
                lines.append(f"  {direction.capitalize()}: {cell.cell_type.label} {cell.cell_type.emoji}")
        return "\n".join(lines)
