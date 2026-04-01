"""Data types, enums, and catalogs for Metal Gear Agent."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Cell types
# ---------------------------------------------------------------------------

class CellType(Enum):
    CORRIDOR = "corridor"
    SERVER_ROOM = "server_room"
    REINFORCED_WALL = "reinforced_wall"
    INTEL_CACHE = "intel_cache"
    INFORMANT = "informant"
    ARMORY = "armory"
    SAFE_ROOM = "safe_room"
    BOSS_ARENA = "boss_arena"
    ENTRY_POINT = "entry_point"

    @property
    def emoji(self) -> str:
        return {
            CellType.CORRIDOR: "·",
            CellType.SERVER_ROOM: "\U0001f4bb",       # 💻
            CellType.REINFORCED_WALL: "\U0001f9f1",   # 🧱
            CellType.INTEL_CACHE: "\U0001f4c1",       # 📁
            CellType.INFORMANT: "\U0001f575\ufe0f",   # 🕵️
            CellType.ARMORY: "\U0001f527",             # 🔧
            CellType.SAFE_ROOM: "\U0001f4fb",          # 📻
            CellType.BOSS_ARENA: "\U0001f480",         # 💀
            CellType.ENTRY_POINT: "\U0001f6aa",        # 🚪
        }[self]

    @property
    def label(self) -> str:
        return {
            CellType.CORRIDOR: "Corridor",
            CellType.SERVER_ROOM: "Server Room",
            CellType.REINFORCED_WALL: "Reinforced Wall (impassable)",
            CellType.INTEL_CACHE: "Intel Cache",
            CellType.INFORMANT: "Contact",
            CellType.ARMORY: "Armory",
            CellType.SAFE_ROOM: "Safe Room",
            CellType.BOSS_ARENA: "Boss Arena",
            CellType.ENTRY_POINT: "Entry Point",
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
    "Circuit Board": Item("Circuit Board", "A military-grade circuit board from a prototype lab.", quest_item=True),
    "Detonator Components": Item("Detonator Components", "Precision detonator parts from a weapons lab.", quest_item=True),
    "Plastic Explosives": Item("Plastic Explosives", "Military-grade plastic explosive compound.", quest_item=True),
    "C4 Compound": Item("C4 Compound", "A shaped charge, ready for final assembly.", quest_item=True),
    "Medical Supplies": Item("Medical Supplies", "Field medical kit from the south safe room.", quest_item=True),
    "Encrypted Message": Item("Encrypted Message", "A coded transmission from the Engineer.", quest_item=True),
    # Weapons
    "EMP Device": Item("EMP Device", "An electromagnetic pulse device. Effective against electronic systems.", quest_item=True),
    "C4 Package": Item("C4 Package", "A primed demolition charge. Effective against armored targets.", quest_item=True),
    # Loot
    "Access Codes": Item("Access Codes", "High-level security clearance codes. Valuable intel."),
    "Hostage Data": Item("Hostage Data", "Hostage coordinates and guard rotations. Valuable intel."),
    # Consumables
    "Ration": Item("Ration", "Standard field ration. Restores 1 health."),
    "Medkit": Item("Medkit", "Military first aid kit. Restores 2 health."),
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
    "the_colonel": NPC(
        name="The Colonel",
        personality="Veteran military commander. Terse, authoritative, strategic. Values efficiency.",
        knowledge=[
            "The Security Mainframe controls all facility defenses from the north sector (around row 2). It's a hardened electronic system.",
            "Only an electromagnetic pulse can disable the Security Mainframe — you need an EMP device.",
            "The Weapons Lab in the south wing can fabricate EMP devices, but they need a military-grade circuit board.",
            "There's an intel cache nearby to the southwest.",
            "The Informant in the central sector knows the facility layout better than anyone.",
        ],
        style="Speaks in clipped military jargon. Short, direct sentences. Uses terms like 'operative', 'sector', 'intel'. Never gives grid coordinates.",
        greeting="Operative. Good, you're here. We have a situation. Listen up.",
    ),
    "the_engineer": NPC(
        name="The Engineer",
        personality="Nervous tech specialist, brilliant but anxious. Fascinated by gadgets.",
        knowledge=[
            "The Armored Mech patrols the eastern corridor (around row 4, east side). It's heavily plated.",
            "Only shaped demolition charges can breach the Mech's armor.",
            "The safe room operator up north once had access to C4 compound, but the facility's been in lockdown.",
            "There are supply points to the south and north where equipment can be fabricated.",
            "He has an encrypted transmission that needs to reach the Colonel to the south. Important intel — worth 2 intel points.",
        ],
        style="Nervous techno-babble. Uses 'um' and 'uh'. References circuit diagrams, frequencies, specs. Never gives grid coordinates.",
        greeting="Oh! Y-you're the operative? I wasn't sure you'd make it. I've got intel. Lots of it. And, um, a favor to ask.",
    ),
    "the_informant": NPC(
        name="The Informant",
        personality="Mysterious double agent inside the facility. Speaks in whispers, always watching.",
        knowledge=[
            "Circuit boards can be found in the lab to the northwest, where they store prototype electronics (the server room at row 2, column 0).",
            "Detonator components are kept in the secure server room far to the north (the server room at row 0, column 2).",
            "She can assemble plastic explosives from detonator components — she has the expertise.",
            "The North Safe Room operator needs plastic explosives for a demolition op — he has C4 compound to trade.",
            "Both the Weapons Lab and the Demolitions Workshop can fabricate specialized equipment from raw components.",
        ],
        style="Cryptic whispers. Uses ellipses and sentence fragments. References 'shadows', 'corridors', 'the darkness'. Never gives grid coordinates.",
        greeting="...you made it. Keep your voice down. The cameras are everywhere.",
    ),
}


# ---------------------------------------------------------------------------
# Armories and Safe Rooms
# ---------------------------------------------------------------------------

@dataclass
class ArmoryInfo:
    name: str
    description: str
    sells: dict[str, int]                    # item_name -> intel cost
    crafts: dict[str, tuple[str, int]]       # result_item -> (required_item, intel_cost)
    buys: dict[str, int]                     # item_name -> intel earned


ARMORY_CATALOG: dict[tuple[int, int], ArmoryInfo] = {
    (6, 2): ArmoryInfo(
        name="Weapons Lab",
        description="A concealed weapons laboratory. Workbenches covered in electronic components.",
        sells={"Ration": 1},
        crafts={"EMP Device": ("Circuit Board", 1)},
        buys={},
    ),
    (4, 1): ArmoryInfo(
        name="Demolitions Workshop",
        description="A hidden demolitions workshop. Blast shields line the walls.",
        sells={"Medkit": 2},
        crafts={"C4 Package": ("C4 Compound", 1)},
        buys={"Access Codes": 1, "Hostage Data": 1},
    ),
}


@dataclass
class SafeRoomInfo:
    name: str
    description: str
    gives_item: Optional[str] = None     # quest item given on first visit
    needs_item: Optional[str] = None     # quest item the operator wants
    reward_item: Optional[str] = None    # what you get for delivering needs_item
    reward_intel: int = 0


SAFE_ROOM_CATALOG: dict[tuple[int, int], SafeRoomInfo] = {
    (7, 4): SafeRoomInfo(
        name="South Safe Room",
        description="A secure communications room. The handler looks concerned about a contact up north.",
        gives_item="Medical Supplies",
    ),
    (2, 5): SafeRoomInfo(
        name="North Safe Room",
        description="A hidden safe room behind a false wall. The operator monitors security feeds.",
        needs_item="Plastic Explosives",
        reward_item="C4 Compound",
        reward_intel=0,
    ),
}


# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------

@dataclass
class Cell:
    cell_type: CellType
    items: list[str] = field(default_factory=list)
    npc_id: Optional[str] = None
    boss_name: Optional[str] = None
    trap: bool = False
    armory_pos: Optional[tuple[int, int]] = None
    safe_room_pos: Optional[tuple[int, int]] = None
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
    reward_intel: int


ERRANDS: dict[str, ErrandInfo] = {
    "medical_delivery": ErrandInfo(
        name="Medical Delivery",
        pickup_item="Medical Supplies",
        pickup_location=(7, 4),
        deliver_item="Medical Supplies",
        deliver_to_npc="North Safe Room Operator",
        deliver_location=(2, 5),
        reward_intel=2,
    ),
    "message_delivery": ErrandInfo(
        name="Encrypted Message Delivery",
        pickup_item="Encrypted Message",
        pickup_location=(5, 3),
        deliver_item="Encrypted Message",
        deliver_to_npc="The Colonel",
        deliver_location=(7, 1),
        reward_intel=2,
    ),
}
