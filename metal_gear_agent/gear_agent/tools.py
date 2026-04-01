"""Tool implementations for Metal Gear Agent — the 9 actions the agent can take."""

from dataclasses import dataclass
from typing import Callable, Optional

from gear_agent.data import (
    CellType, ARMORY_CATALOG, SAFE_ROOM_CATALOG, ITEM_CATALOG,
)
from gear_agent.scenario import FacilityWorld
from gear_agent.game import OperativeState


@dataclass
class ToolResult:
    success: bool
    message: str


class GameTools:
    """Provides all 9 tools the agent can call each turn."""

    def __init__(self, operative: OperativeState, world: FacilityWorld):
        self.operative = operative
        self.world = world
        self._oracle_fn: Optional[Callable] = None

    def set_oracle(self, oracle_fn: Callable):
        """Inject the oracle function used by codec().

        For Phase 1, pass ``stub_oracle``.
        For Phase 2, pass a function wrapping the LLM call.
        """
        self._oracle_fn = oracle_fn

    # ------------------------------------------------------------------
    # Tool: scan
    # ------------------------------------------------------------------
    def scan(self) -> ToolResult:
        """See the types of adjacent cells (N/S/E/W). Free action."""
        row, col = self.operative.position
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

        row, col = self.operative.position
        dr, dc = deltas[direction]
        new_row, new_col = row + dr, col + dc

        if not self.world.is_passable(new_row, new_col):
            cell = self.world.get_cell(new_row, new_col)
            if cell.cell_type == CellType.REINFORCED_WALL:
                return ToolResult(False, f"Cannot move {direction}: reinforced wall blocks your path.")
            return ToolResult(False, f"Cannot move {direction}: facility perimeter.")

        self.operative.position = (new_row, new_col)
        self.operative.visited.add((new_row, new_col))
        cell = self.world.get_cell(new_row, new_col)

        messages = [f"Moved {direction} to ({new_row}, {new_col})."]

        if cell.description:
            messages.append(cell.description)

        if cell.cell_type == CellType.SERVER_ROOM and cell.trap:
            self.operative.take_damage(1)
            cell.trap = False
            messages.append("! ALERT: Motion sensor triggered! Security laser hits you. You lose 1 health.")

        if cell.cell_type == CellType.INTEL_CACHE and cell.items:
            messages.append("You spot classified files here. Use collect() to grab them.")

        if cell.cell_type == CellType.SERVER_ROOM and cell.items:
            messages.append("You notice useful equipment stored here. Use collect() to search.")

        if cell.cell_type == CellType.INFORMANT:
            npc = cell.npc
            if npc:
                messages.append(f"You encounter {npc.name}. {npc.greeting}")

        if cell.cell_type == CellType.ARMORY:
            armory = ARMORY_CATALOG.get(cell.armory_pos)
            if armory:
                messages.append(f"You enter {armory.name}. {armory.description}")

        if cell.cell_type == CellType.SAFE_ROOM:
            safe_room = SAFE_ROOM_CATALOG.get(cell.safe_room_pos)
            if safe_room:
                messages.append(f"You enter {safe_room.name}. {safe_room.description}")

        if cell.cell_type == CellType.BOSS_ARENA:
            messages.append(f"WARNING: {cell.boss_name} detected! Engage or retreat!")

        return ToolResult(True, " ".join(messages))

    # ------------------------------------------------------------------
    # Tool: codec
    # ------------------------------------------------------------------
    def codec(self, question: str = "") -> ToolResult:
        """Contact NPC / informant with a question."""
        row, col = self.operative.position
        cell = self.world.get_cell(row, col)

        # NPC cells
        if cell.cell_type == CellType.INFORMANT and cell.npc:
            if self._oracle_fn is None:
                return ToolResult(False, "No oracle function set. Cannot contact NPCs.")
            npc = cell.npc
            response = self._oracle_fn(npc, question, self.operative)

            # Engineer gives Encrypted Message on request
            if cell.npc_id == "the_engineer" and not self.world.errand_message_picked_up:
                if any(kw in question.lower() for kw in ["message", "transmission", "errand", "job", "work", "task", "mission"]):
                    self.operative.add_item("Encrypted Message")
                    self.world.errand_message_picked_up = True
                    response += "\n[The Engineer hands you an Encrypted Message.]"

            # Colonel receives Encrypted Message
            if cell.npc_id == "the_colonel" and self.operative.has_item("Encrypted Message") and not self.world.errand_message_delivered:
                if any(kw in question.lower() for kw in ["message", "deliver", "encrypted", "transmission"]):
                    self.operative.remove_item("Encrypted Message")
                    self.operative.add_intel(2)
                    self.world.errand_message_delivered = True
                    response += "\n[You delivered the Encrypted Message! The Colonel rewards you with 2 intel.]"

            # Informant: give Detonator Components -> get Plastic Explosives
            if cell.npc_id == "the_informant" and self.operative.has_item("Detonator Components") and not self.world.explosives_received:
                if any(kw in question.lower() for kw in ["detonator", "explosive", "assemble", "build", "component", "bomb", "c4", "demolition", "plastic"]):
                    self.operative.remove_item("Detonator Components")
                    self.operative.add_item("Plastic Explosives")
                    self.world.explosives_received = True
                    response += "\n[You gave the Detonator Components to the Informant. She assembles Plastic Explosives for you!]"

            self.operative.briefing_log.append(f"Codec with {npc.name}: Q: '{question}' A: '{response[:100]}...'")
            return ToolResult(True, f"{npc.name} says: {response}")

        # Safe Room cells — talk to operator
        if cell.cell_type == CellType.SAFE_ROOM:
            safe_room = SAFE_ROOM_CATALOG.get(cell.safe_room_pos)
            if safe_room:
                messages = [f"The operator at {safe_room.name} speaks:"]

                # South Safe Room: gives Medical Supplies
                if cell.safe_room_pos == (7, 4):
                    if not self.world.errand_medical_picked_up:
                        self.operative.add_item("Medical Supplies")
                        self.world.errand_medical_picked_up = True
                        messages.append('"A contact at the North Safe Room is injured. Take these medical supplies to them. I\'ll credit you 2 intel points."')
                        messages.append("[You received Medical Supplies.]")
                    else:
                        messages.append('"Get those supplies to the north sector, quickly!"')

                # North Safe Room: receives Medical Supplies/Plastic Explosives, gives C4 Compound
                elif cell.safe_room_pos == (2, 5):
                    if self.operative.has_item("Medical Supplies") and not self.world.errand_medical_delivered:
                        self.operative.remove_item("Medical Supplies")
                        self.operative.add_intel(2)
                        self.world.errand_medical_delivered = True
                        messages.append('"Medical supplies! Thank you, operative. Here\'s 2 intel for your trouble."')
                        messages.append("[You delivered the Medical Supplies! Earned 2 intel.]")
                    elif self.operative.has_item("Plastic Explosives") and not self.world.c4_compound_received:
                        self.operative.remove_item("Plastic Explosives")
                        self.operative.add_item("C4 Compound")
                        self.world.c4_compound_received = True
                        messages.append('"Plastic explosives? Perfect. Take this C4 compound — I\'ve been prepping the shaped charges."')
                        messages.append("[You gave Plastic Explosives, received C4 Compound!]")
                    else:
                        messages.append('"If only we had proper medical supplies... and the demolition op needs plastic explosives. The Informant in the central corridor might help."')

                self.operative.briefing_log.append(f"Codec with operator at {safe_room.name}: '{messages[-1][:80]}...'")
                return ToolResult(True, " ".join(messages))

        # Armory cells — talk to technician
        if cell.cell_type == CellType.ARMORY:
            armory = ARMORY_CATALOG.get(cell.armory_pos)
            if armory:
                sell_list = ", ".join(f"{item} ({cost} intel)" for item, cost in armory.sells.items())
                craft_list = ", ".join(
                    f"{result} (needs {req} + {cost} intel)" for result, (req, cost) in armory.crafts.items()
                )
                buy_list = ", ".join(f"{item} ({price} intel)" for item, price in armory.buys.items())
                msg = f"The technician at {armory.name} says: "
                parts = []
                if sell_list:
                    parts.append(f"'Available supplies: {sell_list}.'")
                if craft_list:
                    parts.append(f"'I can fabricate: {craft_list}.'")
                if buy_list:
                    parts.append(f"'I can analyze and extract intel from: {buy_list}.'")
                msg += " ".join(parts)
                return ToolResult(True, msg)

        return ToolResult(False, "No one to contact at this location.")

    # ------------------------------------------------------------------
    # Tool: collect
    # ------------------------------------------------------------------
    def collect(self) -> ToolResult:
        """Collect items in the current cell."""
        row, col = self.operative.position
        cell = self.world.get_cell(row, col)

        if not cell.items:
            return ToolResult(False, "There is nothing to collect here.")

        picked = []
        for item_name in list(cell.items):
            if item_name.startswith("intel_"):
                self.operative.add_intel(1)
                picked.append("1 intel (classified files)")
            else:
                self.operative.add_item(item_name)
                picked.append(item_name)
        cell.items.clear()

        return ToolResult(True, f"Collected: {', '.join(picked)}.")

    # ------------------------------------------------------------------
    # Tool: equip
    # ------------------------------------------------------------------
    def equip(self, item: str) -> ToolResult:
        """Equip/craft an item or sell intel items at the current armory."""
        row, col = self.operative.position
        cell = self.world.get_cell(row, col)

        if cell.cell_type != CellType.ARMORY:
            return ToolResult(False, "You are not at an armory.")

        armory = ARMORY_CATALOG.get(cell.armory_pos)
        if not armory:
            return ToolResult(False, "This armory has nothing available.")

        item_clean = item.strip()

        # Check craftable items first
        for craft_name, (required, cost) in armory.crafts.items():
            if item_clean.lower() == craft_name.lower():
                if not self.operative.has_item(required):
                    return ToolResult(False, f"You need {required} to fabricate {craft_name}.")
                if not self.operative.spend_intel(cost):
                    return ToolResult(False, f"Not enough intel. {craft_name} costs {cost} intel (plus {required}).")
                self.operative.remove_item(required)
                self.operative.add_item(craft_name)
                return ToolResult(True, f"Fabricated {craft_name}! (Used {required} + {cost} intel)")

        # Check sellable items (operative selling to armory)
        for buy_name, price in armory.buys.items():
            if item_clean.lower() == buy_name.lower() or item_clean.lower() == f"sell {buy_name.lower()}":
                if not self.operative.has_item(buy_name):
                    return ToolResult(False, f"You don't have {buy_name} to trade.")
                self.operative.remove_item(buy_name)
                self.operative.add_intel(price)
                return ToolResult(True, f"Traded {buy_name} for {price} intel.")

        # Check regular purchases
        for sell_name, cost in armory.sells.items():
            if item_clean.lower() == sell_name.lower():
                if not self.operative.spend_intel(cost):
                    return ToolResult(False, f"Not enough intel. {sell_name} costs {cost} intel.")
                self.operative.add_item(sell_name)
                return ToolResult(True, f"Acquired {sell_name} for {cost} intel.")

        available = list(armory.sells.keys()) + list(armory.crafts.keys())
        return ToolResult(False, f"'{item_clean}' is not available here. Available: {', '.join(available)}")

    # ------------------------------------------------------------------
    # Tool: use
    # ------------------------------------------------------------------
    def use(self, item: str) -> ToolResult:
        """Use an item from inventory."""
        item_clean = item.strip()

        if not self.operative.has_item(item_clean):
            return ToolResult(False, f"You don't have '{item_clean}' in your inventory.")

        if item_clean == "Ration":
            self.operative.remove_item("Ration")
            self.operative.heal(1)
            return ToolResult(True, f"You eat the Ration. Restored 1 health. Health: {self.operative.health}/{self.operative.MAX_HEALTH}")

        if item_clean == "Medkit":
            self.operative.remove_item("Medkit")
            self.operative.heal(2)
            return ToolResult(True, f"You apply the Medkit. Restored 2 health. Health: {self.operative.health}/{self.operative.MAX_HEALTH}")

        return ToolResult(False, f"You can't use '{item_clean}' right now.")

    # ------------------------------------------------------------------
    # Tool: engage
    # ------------------------------------------------------------------
    def engage(self) -> ToolResult:
        """Engage the boss in the current cell."""
        row, col = self.operative.position
        cell = self.world.get_cell(row, col)

        if cell.cell_type != CellType.BOSS_ARENA:
            return ToolResult(False, "There is no target to engage here.")

        boss = cell.boss_name

        if boss == "Security Mainframe" and not self.world.mainframe_active:
            return ToolResult(False, "The Security Mainframe has already been disabled.")
        if boss == "Armored Mech" and not self.world.mech_active:
            return ToolResult(False, "The Armored Mech has already been destroyed.")

        if boss == "Security Mainframe":
            if self.operative.has_item("EMP Device"):
                self.world.mainframe_active = False
                self.operative.add_intel(3)
                self.operative.add_item("Access Codes")
                return ToolResult(True,
                    "You activate the EMP Device — the electromagnetic pulse fries the Security Mainframe's circuits! "
                    "Mission success. Earned 3 intel and Access Codes.")
            else:
                self.operative.take_damage(1)
                return ToolResult(False,
                    f"! ALERT: The Security Mainframe activates countermeasures! "
                    f"You retreat under fire, losing 1 health. Health: {self.operative.health}. "
                    f"You need an EMP weapon to disable it.")

        if boss == "Armored Mech":
            if self.operative.has_item("C4 Package"):
                self.world.mech_active = False
                self.operative.add_intel(3)
                self.operative.add_item("Hostage Data")
                return ToolResult(True,
                    "You plant the C4 Package on the Armored Mech — BOOM! The mech is destroyed! "
                    "Mission success. Earned 3 intel and Hostage Data.")
            else:
                self.operative.take_damage(1)
                return ToolResult(False,
                    f"! ALERT: The Armored Mech shrugs off your attack! "
                    f"You retreat, losing 1 health. Health: {self.operative.health}. "
                    f"You need demolition charges to destroy it.")

        return ToolResult(False, f"Unknown target: {boss}")

    # ------------------------------------------------------------------
    # Tool: hide
    # ------------------------------------------------------------------
    def hide(self) -> ToolResult:
        """Rest at a safe room. Costs 1 intel, restores 1 health."""
        row, col = self.operative.position
        cell = self.world.get_cell(row, col)

        if cell.cell_type != CellType.SAFE_ROOM:
            return ToolResult(False, "You can only hide at a safe room.")

        if self.operative.health >= self.operative.MAX_HEALTH:
            return ToolResult(False, "You are already at full health.")

        if not self.operative.spend_intel(1):
            return ToolResult(False, "Not enough intel. Hiding costs 1 intel.")

        self.operative.heal(1)
        return ToolResult(True,
            f"You rest in the safe room. Restored 1 health. Health: {self.operative.health}/{self.operative.MAX_HEALTH}")

    # ------------------------------------------------------------------
    # Tool: sitrep
    # ------------------------------------------------------------------
    def sitrep(self) -> ToolResult:
        """Check current operative state."""
        return ToolResult(True, self.operative.status_text())

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def execute(self, tool_name: str, args: dict) -> ToolResult:
        """Execute a tool by name with given arguments."""
        tool_map = {
            "scan": lambda: self.scan(),
            "move": lambda: self.move(args.get("direction", "")),
            "codec": lambda: self.codec(args.get("question", "")),
            "collect": lambda: self.collect(),
            "equip": lambda: self.equip(args.get("item", "")),
            "use": lambda: self.use(args.get("item", "")),
            "engage": lambda: self.engage(),
            "hide": lambda: self.hide(),
            "sitrep": lambda: self.sitrep(),
        }

        fn = tool_map.get(tool_name.lower().strip())
        if fn is None:
            return ToolResult(False, f"Unknown tool '{tool_name}'. Available: {', '.join(tool_map.keys())}")

        return fn()
