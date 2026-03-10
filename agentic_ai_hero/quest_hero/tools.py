"""Tool implementations for Quest Hero — the 9 actions the agent can take."""

from dataclasses import dataclass
from typing import Callable, Optional

from quest_hero.game_world import (
    GameWorld, CellType, SHOP_CATALOG, INN_CATALOG, ITEM_CATALOG,
)
from quest_hero.hero import Hero


@dataclass
class ToolResult:
    success: bool
    message: str


class GameTools:
    """Provides all 9 tools the agent can call each turn."""

    def __init__(self, hero: Hero, world: GameWorld):
        self.hero = hero
        self.world = world
        self._oracle_fn: Optional[Callable] = None

    def set_oracle(self, oracle_fn: Callable):
        """Inject the oracle function used by talk().

        For Phase 1, pass ``stub_oracle``.
        For Phase 2, pass a function wrapping the LLM call.
        """
        self._oracle_fn = oracle_fn

    # ------------------------------------------------------------------
    # Tool: look
    # ------------------------------------------------------------------
    def look(self) -> ToolResult:
        """See the types of adjacent cells (N/S/E/W). Free."""
        row, col = self.hero.position
        desc = self.world.get_visible_description(row, col)
        return ToolResult(True, desc)

    # ------------------------------------------------------------------
    # Tool: move
    # ------------------------------------------------------------------
    def move(self, direction: str) -> ToolResult:
        """Move one step in a cardinal direction. Triggers cell events."""
        direction = direction.lower().strip()
        deltas = {"north": (-1, 0), "south": (1, 0), "east": (0, 1), "west": (0, -1)}
        if direction not in deltas:
            return ToolResult(False, f"Invalid direction '{direction}'. Use north/south/east/west.")

        row, col = self.hero.position
        dr, dc = deltas[direction]
        new_row, new_col = row + dr, col + dc

        if not self.world.is_passable(new_row, new_col):
            cell = self.world.get_cell(new_row, new_col)
            if cell.cell_type == CellType.MOUNTAIN:
                return ToolResult(False, f"Cannot move {direction}: mountain blocks your path.")
            return ToolResult(False, f"Cannot move {direction}: out of bounds.")

        self.hero.position = (new_row, new_col)
        self.hero.visited.add((new_row, new_col))
        cell = self.world.get_cell(new_row, new_col)

        messages = [f"Moved {direction} to ({new_row}, {new_col})."]

        # Cell-entry events
        if cell.description:
            messages.append(cell.description)

        if cell.cell_type == CellType.FOREST and cell.trap:
            self.hero.take_damage(1)
            cell.trap = False  # trap triggers once
            messages.append("A hidden trap springs! You lose 1 heart.")

        if cell.cell_type == CellType.TREASURE and cell.items:
            messages.append("You see something shining here! Use pick_up() to collect it.")

        if cell.cell_type == CellType.FOREST and cell.items:
            messages.append("You notice something hidden among the trees. Use pick_up() to search.")

        if cell.cell_type == CellType.NPC:
            npc = cell.npc
            if npc:
                messages.append(f"You encounter {npc.name}. {npc.greeting}")

        if cell.cell_type == CellType.SHOP:
            shop = SHOP_CATALOG.get(cell.shop_pos)
            if shop:
                messages.append(f"You enter {shop.name}. {shop.description}")

        if cell.cell_type == CellType.INN:
            inn = INN_CATALOG.get(cell.inn_pos)
            if inn:
                messages.append(f"You enter {inn.name}. {inn.description}")

        if cell.cell_type == CellType.DRAGON:
            messages.append(f"A fearsome {cell.dragon_name} blocks your path! Fight or flee!")

        return ToolResult(True, " ".join(messages))

    # ------------------------------------------------------------------
    # Tool: talk
    # ------------------------------------------------------------------
    def talk(self, question: str = "") -> ToolResult:
        """Talk to the NPC in the current cell."""
        row, col = self.hero.position
        cell = self.world.get_cell(row, col)

        # NPC cells
        if cell.cell_type == CellType.NPC and cell.npc:
            if self._oracle_fn is None:
                return ToolResult(False, "No oracle function set. Cannot talk to NPCs.")
            npc = cell.npc
            response = self._oracle_fn(npc, question, self.hero)

            # Handle special NPC interactions
            # Traveling Merchant gives letter on request
            if cell.npc_id == "traveling_merchant" and not self.world.errand_letter_picked_up:
                if any(kw in question.lower() for kw in ["letter", "deliver", "errand", "job", "work", "task"]):
                    self.hero.add_item("Letter")
                    self.world.errand_letter_picked_up = True
                    response += "\n[The Merchant hands you a sealed Letter.]"

            # Old Hermit receives letter
            if cell.npc_id == "old_hermit" and self.hero.has_item("Letter") and not self.world.errand_letter_delivered:
                if any(kw in question.lower() for kw in ["letter", "deliver", "message"]):
                    self.hero.remove_item("Letter")
                    self.hero.add_gold(2)
                    self.world.errand_letter_delivered = True
                    response += "\n[You delivered the Letter! The Hermit rewards you with 2 gold.]"

            # Forest Witch: give Ghostcaps -> get Medicine
            if cell.npc_id == "forest_witch" and self.hero.has_item("Ghostcaps") and not self.world.medicine_received:
                if any(kw in question.lower() for kw in ["medicine", "brew", "ghostcap", "mushroom", "cure", "remedy", "heal", "sick"]):
                    self.hero.remove_item("Ghostcaps")
                    self.hero.add_item("Medicine")
                    self.world.medicine_received = True
                    response += "\n[You gave the Ghostcaps to the Witch. She brews Medicine for you!]"

            self.hero.journal.append(f"Talked to {npc.name}: Q: '{question}' A: '{response[:100]}...'")
            return ToolResult(True, f"{npc.name} says: {response}")

        # Inn cells — talk to innkeeper
        if cell.cell_type == CellType.INN:
            inn = INN_CATALOG.get(cell.inn_pos)
            if inn:
                messages = [f"The innkeeper at {inn.name} speaks:"]

                # Southern Inn: gives Herbal Tea
                if cell.inn_pos == (7, 4):
                    if not self.world.errand_tea_picked_up:
                        self.hero.add_item("Herbal Tea")
                        self.world.errand_tea_picked_up = True
                        messages.append('"My brother at the Northern Inn is terribly ill. Please, take this Herbal Tea to him. I\'ll pay you 2 gold!"')
                        messages.append("[You received Herbal Tea.]")
                    else:
                        messages.append('"Please hurry with that tea to my brother up north!"')

                # Northern Inn: receives Medicine/Tea, gives Moonstone
                elif cell.inn_pos == (2, 5):
                    if self.hero.has_item("Herbal Tea") and not self.world.errand_tea_delivered:
                        self.hero.remove_item("Herbal Tea")
                        self.hero.add_gold(2)
                        self.world.errand_tea_delivered = True
                        messages.append('"The tea from my brother! Thank you so much! Here, take 2 gold for your trouble."')
                        messages.append("[You delivered the Herbal Tea! Earned 2 gold.]")
                    elif self.hero.has_item("Medicine") and not self.world.moonstone_received:
                        self.hero.remove_item("Medicine")
                        self.hero.add_item("Moonstone")
                        self.world.moonstone_received = True
                        messages.append('"Medicine for my wife! You are a saint! Take this Moonstone — it was hers, but she\'d want you to have it."')
                        messages.append("[You gave Medicine, received Moonstone!]")
                    else:
                        messages.append('"My wife is sick... if only someone could bring medicine. The Forest Witch brews remedies, I hear."')

                self.hero.journal.append(f"Talked to innkeeper at {inn.name}: '{messages[-1][:80]}...'")
                return ToolResult(True, " ".join(messages))

        # Shop cells — talk to shopkeeper
        if cell.cell_type == CellType.SHOP:
            shop = SHOP_CATALOG.get(cell.shop_pos)
            if shop:
                sell_list = ", ".join(f"{item} ({cost}g)" for item, cost in shop.sells.items())
                craft_list = ", ".join(
                    f"{result} (needs {req} + {cost}g)" for result, (req, cost) in shop.crafts.items()
                )
                buy_list = ", ".join(f"{item} ({price}g)" for item, price in shop.buys.items())
                msg = f"The shopkeeper at {shop.name} says: "
                parts = []
                if sell_list:
                    parts.append(f"'I sell: {sell_list}.'")
                if craft_list:
                    parts.append(f"'I can craft: {craft_list}.'")
                if buy_list:
                    parts.append(f"'I buy: {buy_list}.'")
                msg += " ".join(parts)
                return ToolResult(True, msg)

        return ToolResult(False, "There is no one to talk to here.")

    # ------------------------------------------------------------------
    # Tool: pick_up
    # ------------------------------------------------------------------
    def pick_up(self) -> ToolResult:
        """Pick up items in the current cell."""
        row, col = self.hero.position
        cell = self.world.get_cell(row, col)

        if not cell.items:
            return ToolResult(False, "There is nothing to pick up here.")

        picked = []
        for item_name in list(cell.items):
            if item_name.startswith("gold_"):
                self.hero.add_gold(1)
                picked.append("1 gold (treasure)")
            else:
                self.hero.add_item(item_name)
                picked.append(item_name)
        cell.items.clear()

        return ToolResult(True, f"Picked up: {', '.join(picked)}.")

    # ------------------------------------------------------------------
    # Tool: buy
    # ------------------------------------------------------------------
    def buy(self, item: str) -> ToolResult:
        """Buy an item or craft a weapon at the current shop."""
        row, col = self.hero.position
        cell = self.world.get_cell(row, col)

        if cell.cell_type != CellType.SHOP:
            return ToolResult(False, "You are not at a shop.")

        shop = SHOP_CATALOG.get(cell.shop_pos)
        if not shop:
            return ToolResult(False, "This shop has nothing for sale.")

        item_clean = item.strip()

        # Check craftable items first
        for craft_name, (required, cost) in shop.crafts.items():
            if item_clean.lower() == craft_name.lower():
                if not self.hero.has_item(required):
                    return ToolResult(False, f"You need {required} to craft {craft_name}.")
                if not self.hero.spend_gold(cost):
                    return ToolResult(False, f"Not enough gold. {craft_name} costs {cost} gold (plus {required}).")
                self.hero.remove_item(required)
                self.hero.add_item(craft_name)
                return ToolResult(True, f"Crafted {craft_name}! (Used {required} + {cost} gold)")

        # Check sellable items (hero selling to shop)
        for buy_name, price in shop.buys.items():
            if item_clean.lower() == buy_name.lower() or item_clean.lower() == f"sell {buy_name.lower()}":
                if not self.hero.has_item(buy_name):
                    return ToolResult(False, f"You don't have {buy_name} to sell.")
                self.hero.remove_item(buy_name)
                self.hero.add_gold(price)
                return ToolResult(True, f"Sold {buy_name} for {price} gold.")

        # Check regular purchases
        for sell_name, cost in shop.sells.items():
            if item_clean.lower() == sell_name.lower():
                if not self.hero.spend_gold(cost):
                    return ToolResult(False, f"Not enough gold. {sell_name} costs {cost} gold.")
                self.hero.add_item(sell_name)
                return ToolResult(True, f"Bought {sell_name} for {cost} gold.")

        available = list(shop.sells.keys()) + list(shop.crafts.keys())
        return ToolResult(False, f"'{item_clean}' is not available here. Available: {', '.join(available)}")

    # ------------------------------------------------------------------
    # Tool: use
    # ------------------------------------------------------------------
    def use(self, item: str) -> ToolResult:
        """Use an item from inventory."""
        item_clean = item.strip()

        if not self.hero.has_item(item_clean):
            return ToolResult(False, f"You don't have '{item_clean}' in your inventory.")

        if item_clean == "Bread":
            self.hero.remove_item("Bread")
            self.hero.heal(1)
            return ToolResult(True, f"You eat the Bread. Restored 1 heart. Hearts: {self.hero.hearts}/{self.hero.MAX_HEARTS}")

        if item_clean == "Health Potion":
            self.hero.remove_item("Health Potion")
            self.hero.heal(2)
            return ToolResult(True, f"You drink the Health Potion. Restored 2 hearts. Hearts: {self.hero.hearts}/{self.hero.MAX_HEARTS}")

        return ToolResult(False, f"You can't use '{item_clean}' right now.")

    # ------------------------------------------------------------------
    # Tool: fight
    # ------------------------------------------------------------------
    def fight(self) -> ToolResult:
        """Fight the monster in the current cell."""
        row, col = self.hero.position
        cell = self.world.get_cell(row, col)

        if cell.cell_type != CellType.DRAGON:
            return ToolResult(False, "There is no monster to fight here.")

        dragon = cell.dragon_name

        if dragon == "Frost Wyrm" and not self.world.frost_wyrm_alive:
            return ToolResult(False, "The Frost Wyrm has already been defeated.")
        if dragon == "Shadow Beast" and not self.world.shadow_beast_alive:
            return ToolResult(False, "The Shadow Beast has already been defeated.")

        # Check for correct weapon
        if dragon == "Frost Wyrm":
            if self.hero.has_item("Sunblade"):
                self.world.frost_wyrm_alive = False
                self.hero.add_gold(3)
                self.hero.add_item("Dragon Scales")
                return ToolResult(True,
                    "You raise the Sunblade high — its fiery glow melts the Frost Wyrm's icy armor! "
                    "Victory! Earned 3 gold and Dragon Scales.")
            else:
                self.hero.take_damage(1)
                return ToolResult(False,
                    f"You attack the Frost Wyrm but its icy breath overwhelms you! "
                    f"You retreat, losing 1 heart. Hearts: {self.hero.hearts}. "
                    f"You need a weapon of fire to defeat it.")

        if dragon == "Shadow Beast":
            if self.hero.has_item("Moonstone Lantern"):
                self.world.shadow_beast_alive = False
                self.hero.add_gold(3)
                self.hero.add_item("Dragon Scales")
                return ToolResult(True,
                    "You hold the Moonstone Lantern aloft — pure moonlight pierces the Shadow Beast! "
                    "Victory! Earned 3 gold and Dragon Scales.")
            else:
                self.hero.take_damage(1)
                return ToolResult(False,
                    f"The Shadow Beast engulfs you in darkness! "
                    f"You retreat, losing 1 heart. Hearts: {self.hero.hearts}. "
                    f"You need a weapon of light to defeat it.")

        return ToolResult(False, f"Unknown dragon: {dragon}")

    # ------------------------------------------------------------------
    # Tool: rest
    # ------------------------------------------------------------------
    def rest(self) -> ToolResult:
        """Rest at an inn. Costs 1 gold, restores 1 heart."""
        row, col = self.hero.position
        cell = self.world.get_cell(row, col)

        if cell.cell_type != CellType.INN:
            return ToolResult(False, "You can only rest at an inn.")

        if self.hero.hearts >= self.hero.MAX_HEARTS:
            return ToolResult(False, "You are already at full health.")

        if not self.hero.spend_gold(1):
            return ToolResult(False, "Not enough gold. Resting costs 1 gold.")

        self.hero.heal(1)
        return ToolResult(True,
            f"You rest at the inn. Restored 1 heart. Hearts: {self.hero.hearts}/{self.hero.MAX_HEARTS}")

    # ------------------------------------------------------------------
    # Tool: status
    # ------------------------------------------------------------------
    def status(self) -> ToolResult:
        """Check current hero state."""
        return ToolResult(True, self.hero.status_text())

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def execute(self, tool_name: str, args: dict) -> ToolResult:
        """Execute a tool by name with given arguments."""
        tool_map = {
            "look": lambda: self.look(),
            "move": lambda: self.move(args.get("direction", "")),
            "talk": lambda: self.talk(args.get("question", "")),
            "pick_up": lambda: self.pick_up(),
            "buy": lambda: self.buy(args.get("item", "")),
            "use": lambda: self.use(args.get("item", "")),
            "fight": lambda: self.fight(),
            "rest": lambda: self.rest(),
            "status": lambda: self.status(),
        }

        fn = tool_map.get(tool_name.lower().strip())
        if fn is None:
            return ToolResult(False, f"Unknown tool '{tool_name}'. Available: {', '.join(tool_map.keys())}")

        return fn()
