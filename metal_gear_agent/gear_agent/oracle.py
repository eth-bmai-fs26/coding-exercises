"""NPC Oracle for Metal Gear Agent.

Phase 1: Uses stub_oracle with canned keyword-matched responses.
Phase 2: Uses llm_oracle powered by the Gemini API.
"""

from gear_agent.data import NPC
from gear_agent.game import OperativeState


# ---------------------------------------------------------------------------
# Template for NPC system prompts
# ---------------------------------------------------------------------------

ORACLE_TEMPLATE = """You are {name}, a contact in a military stealth operation.

Personality: {personality}

Your knowledge (share as hints, never reveal directly):
{knowledge}

Speaking style: {style}

The operative currently carries: {inventory}
The operative has {health} health and {intel} intel points.
The operative has explored {visited_count} locations.

Rules:
- Stay in character at all times.
- Give hints and clues, never exact coordinates or step-by-step instructions.
- Use in-world language (say "intel" not "points", "the mainframe" not "Boss A").
- Be helpful but guarded — guide, don't solve.
- Keep responses to 2-3 sentences."""


# ---------------------------------------------------------------------------
# Stub oracle for Phase 1 (provided complete)
# ---------------------------------------------------------------------------

def stub_oracle(npc: NPC, question: str, operative: OperativeState) -> str:
    """Keyword-matched canned responses for the rule-based agent (Phase 1).

    Returns NPC-flavored hints based on keywords in the question.
    No LLM needed — just pattern matching.
    """
    q = question.lower()
    name = npc.name

    if name == "The Colonel":
        if any(kw in q for kw in ["mainframe", "security", "defense", "north", "electronic"]):
            return ("The Security Mainframe controls the facility's defenses in the north sector. "
                    "Only an electromagnetic pulse can take it offline. The Weapons Lab in the "
                    "south wing can fabricate an EMP device — but they need a circuit board.")
        if any(kw in q for kw in ["emp", "weapon", "device", "circuit", "board"]):
            return ("An EMP device is your best bet against the Mainframe. The Weapons Lab to "
                    "the south can build one if you bring them a military-grade circuit board. "
                    "The Informant knows where to find one.")
        if any(kw in q for kw in ["intel", "cache", "files", "data"]):
            return ("Intel caches are scattered across the facility. I know of one "
                    "nearby to the southwest. There are others far to the north and east.")
        if any(kw in q for kw in ["message", "deliver", "encrypted", "transmission"]):
            if operative.has_item("Encrypted Message"):
                return "An encrypted transmission? Let me see it... This is valuable intel."
            return "I haven't received any messages lately. Perhaps someone needs a courier?"
        if any(kw in q for kw in ["help", "mission", "what", "who", "where", "how", "brief"]):
            return ("The facility is locked down. A Security Mainframe controls the defenses, "
                    "and an Armored Mech patrols the east wing. The Informant in the central "
                    "sector has eyes everywhere — make contact.")
        return ("Stay focused, operative. Ask me about the facility defenses, "
                "the mainframe, or enemy assets, and I'll brief you.")

    if name == "The Engineer":
        if any(kw in q for kw in ["mech", "armored", "east", "armor", "vehicle", "tank"]):
            return ("The Armored Mech in the eastern corridor? Only shaped demolition charges "
                    "can breach that armor. The safe room operator up north once had access to "
                    "C4 compound, but things have been... complicated.")
        if any(kw in q for kw in ["c4", "demolition", "explosive", "charge", "compound"]):
            return ("C4 compound... the North Safe Room operator had some stockpiled. But he "
                    "needs plastic explosives first — the Informant in the central sector might "
                    "be able to, um, help with that. The Demolitions Workshop can assemble the final package.")
        if any(kw in q for kw in ["message", "transmission", "errand", "job", "work", "task", "mission"]):
            return ("Actually, I do have something! I intercepted an encrypted transmission "
                    "that needs to reach the Colonel down south. 2 intel points for the delivery. "
                    "What do you say?")
        if any(kw in q for kw in ["equip", "supply", "armory", "fabricat", "craft"]):
            return ("There's a Weapons Lab to the south and a Demolitions Workshop to the "
                    "north-west. Both can fabricate specialized equipment from raw components!")
        if any(kw in q for kw in ["help", "what", "who", "where", "how", "brief"]):
            return ("Looking for work? There's an Armored Mech terrorizing the east wing, "
                    "intel caches scattered about, and I've got a transmission that needs delivering. "
                    "Plenty of opportunity for a skilled operative!")
        return ("I'm, um, always happy to help with tech stuff. Ask me about the mech, "
                "demolitions, or maybe you want a delivery job?")

    if name == "The Informant":
        if any(kw in q for kw in ["circuit", "board", "electronics", "prototype"]):
            return ("Circuit boards... they're stored in the northwest lab, where they "
                    "keep the prototype electronics. The ground there hums with power. "
                    "Tread carefully.")
        if any(kw in q for kw in ["detonator", "explosive", "assemble", "build", "component", "bomb", "c4", "demolition", "plastic"]):
            if operative.has_item("Detonator Components"):
                return ("You have the detonator components... Give them to me. "
                        "I can assemble plastic explosives from these parts.")
            return ("Detonator components... they're kept in the dark server room to the far "
                    "north. Bring them to me and I can assemble something useful.")
        if any(kw in q for kw in ["guard", "patrol", "shadow", "mech", "security"]):
            return ("The guards follow predictable patterns. The real threats are the "
                    "automated systems — the Mainframe in the north and the Mech in the east. "
                    "Both need specialized equipment to neutralize.")
        if any(kw in q for kw in ["help", "mission", "what", "who", "where", "how", "brief"]):
            return ("...I see everything in this facility. I know where the components "
                    "are hidden and what the enemy is protecting. I can build things from "
                    "raw parts. What do you need?")
        return ("...the corridors have many secrets. Ask me about components, "
                "the guards, or what I can build for you.")

    return f"{name} looks at you but says nothing useful."


# ---------------------------------------------------------------------------
# LLM-powered oracle for Phase 2 (provided complete)
# ---------------------------------------------------------------------------

def build_npc_system_prompt(npc: NPC, operative: OperativeState) -> str:
    """Build a system prompt for an NPC based on their personality and knowledge."""
    knowledge_str = "\n".join(f"- {k}" for k in npc.knowledge)
    inventory_str = ", ".join(operative.inventory) if operative.inventory else "nothing"

    return ORACLE_TEMPLATE.format(
        name=npc.name,
        personality=npc.personality,
        knowledge=knowledge_str,
        style=npc.style,
        inventory=inventory_str,
        health=operative.health,
        intel=operative.intel,
        visited_count=len(operative.visited),
    )


def llm_oracle(npc: NPC, question: str, operative: OperativeState, client) -> str:
    """Ask an NPC a question using the Gemini API.

    Args:
        npc: The NPC to contact.
        question: The operative's question.
        operative: The operative (for context in the system prompt).
        client: A genai.Client() instance.

    Returns:
        str: The NPC's in-character response.
    """
    from google import genai

    system_prompt = build_npc_system_prompt(npc, operative)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=300,
        ),
    )

    return response.text
