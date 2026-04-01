"""Facility world: the 8x8 military facility map for Metal Gear Agent."""

from typing import Optional

from gear_agent.data import (
    CellType, Cell, NPC_CATALOG, ARMORY_CATALOG, SAFE_ROOM_CATALOG,
)


class FacilityWorld:
    """8x8 military facility grid world."""

    ROWS = 8
    COLS = 8

    def __init__(self):
        self.grid: list[list[Cell]] = []
        self.errand_medical_picked_up = False
        self.errand_medical_delivered = False
        self.errand_message_picked_up = False
        self.errand_message_delivered = False
        self.explosives_given_to_informant = False
        self.explosives_received = False
        self.c4_compound_received = False
        self.mainframe_active = True
        self.mech_active = True
        self.build_map()

    def build_map(self):
        """Construct the 8x8 facility grid."""
        self.grid = [
            [Cell(CellType.CORRIDOR) for _ in range(self.COLS)]
            for _ in range(self.ROWS)
        ]

        # Row 0: 🚪 · 💻 · · 💻 · 📁
        self._set(0, 0, Cell(CellType.ENTRY_POINT,
            description="The facility's ventilation access point. Your insertion route."))
        self._set(0, 2, Cell(CellType.SERVER_ROOM, items=["Detonator Components"],
            description="A darkened server room. Prototype detonator components sit on a workbench."))
        self._set(0, 5, Cell(CellType.SERVER_ROOM, trap=True,
            description="A server room with active motion sensors among the racks."))
        self._set(0, 7, Cell(CellType.INTEL_CACHE, items=["intel_1"],
            description="A classified file cabinet, poorly secured. Intel for the taking."))

        # Row 1: · · · 🧱 · · · ·
        self._set(1, 3, Cell(CellType.REINFORCED_WALL,
            description="Blast-proof reinforced concrete. No way through."))

        # Row 2: 💻 💀₁ · 🧱 · 📻₂ · 💻
        self._set(2, 0, Cell(CellType.SERVER_ROOM, items=["Circuit Board"],
            description="A prototype electronics lab. Military-grade circuit boards line the shelves."))
        self._set(2, 1, Cell(CellType.BOSS_ARENA, boss_name="Security Mainframe",
            description="A cold server chamber. The Security Mainframe's indicator lights pulse ominously."))
        self._set(2, 3, Cell(CellType.REINFORCED_WALL,
            description="Blast-proof reinforced concrete. No way through."))
        self._set(2, 5, Cell(CellType.SAFE_ROOM, safe_room_pos=(2, 5),
            description="A hidden safe room behind a false wall. The operator monitors security feeds."))
        self._set(2, 7, Cell(CellType.SERVER_ROOM,
            description="A quiet monitoring station. Equipment hums softly."))

        # Row 3: · · · · 🕵️₃ · · ·
        self._set(3, 4, Cell(CellType.INFORMANT, npc_id="the_informant",
            description="A shadowy alcove between corridors. Someone waits in the darkness."))

        # Row 4: · 🔧₂ · 🧱 · · 💀₂ ·
        self._set(4, 1, Cell(CellType.ARMORY, armory_pos=(4, 1),
            description="A hidden demolitions workshop. Blast shields line the walls."))
        self._set(4, 3, Cell(CellType.REINFORCED_WALL,
            description="Blast-proof reinforced concrete. No way through."))
        self._set(4, 6, Cell(CellType.BOSS_ARENA, boss_name="Armored Mech",
            description="Heavy tread marks scar the floor. The Armored Mech stands guard."))

        # Row 5: 📁 · · 🕵️₂ · 💻 · ·
        self._set(5, 0, Cell(CellType.INTEL_CACHE, items=["intel_1"],
            description="A dead drop location. Classified intel hidden in a wall panel."))
        self._set(5, 3, Cell(CellType.INFORMANT, npc_id="the_engineer",
            description="A cluttered tech workshop. Screens flicker with schematics."))
        self._set(5, 5, Cell(CellType.SERVER_ROOM,
            description="A backup power control room. Nothing of note."))

        # Row 6: · · 🔧₁ · · · 📁 ·
        self._set(6, 2, Cell(CellType.ARMORY, armory_pos=(6, 2),
            description="A concealed weapons laboratory. Workbenches covered in electronic components."))
        self._set(6, 6, Cell(CellType.INTEL_CACHE, items=["intel_1"],
            description="Loose data drives scattered on the floor. Easy intel."))

        # Row 7: 🦸 🕵️₁ · · 📻₁ · · 💻
        self._set(7, 0, Cell(CellType.CORRIDOR,
            description="The insertion point. Familiar ground."))
        self._set(7, 1, Cell(CellType.INFORMANT, npc_id="the_colonel",
            description="A fortified command post. A veteran officer reviews tactical maps."))
        self._set(7, 4, Cell(CellType.SAFE_ROOM, safe_room_pos=(7, 4),
            description="A secure communications room. The handler monitors incoming transmissions."))
        self._set(7, 7, Cell(CellType.SERVER_ROOM,
            description="A server room at the facility's edge. Equipment is powered down."))

    def _set(self, row: int, col: int, cell: Cell):
        self.grid[row][col] = cell

    def get_cell(self, row: int, col: int) -> Cell:
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            return self.grid[row][col]
        return Cell(CellType.REINFORCED_WALL, description="The edge of the facility.")

    def is_passable(self, row: int, col: int) -> bool:
        if not (0 <= row < self.ROWS and 0 <= col < self.COLS):
            return False
        return self.grid[row][col].cell_type != CellType.REINFORCED_WALL

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
                result[direction] = None
        return result

    def get_visible_description(self, row: int, col: int) -> str:
        """Return a text description of what the operative can see from (row, col)."""
        lines = []
        current = self.get_cell(row, col)
        lines.append(f"You are at position ({row}, {col}).")
        if current.description:
            lines.append(f"Current location: {current.description}")

        adjacent = self.get_adjacent(row, col)
        for direction, cell in adjacent.items():
            if cell is None:
                lines.append(f"  {direction.capitalize()}: Facility perimeter (impassable).")
            else:
                lines.append(f"  {direction.capitalize()}: {cell.cell_type.label} {cell.cell_type.emoji}")
        return "\n".join(lines)
