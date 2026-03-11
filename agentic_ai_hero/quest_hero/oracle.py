"""NPC Oracle for Quest Hero.

Phase 1: Uses stub_oracle with canned keyword-matched responses.
Phase 2: Students implement build_npc_system_prompt() and ask_npc() using the Gemini API.
"""

from quest_hero.game_world import NPC
from quest_hero.hero import Hero


# ---------------------------------------------------------------------------
# Template for NPC system prompts (reference for students)
# ---------------------------------------------------------------------------

ORACLE_TEMPLATE = """You are {name}, an NPC in a fantasy RPG world.

Personality: {personality}

Your knowledge (share as hints, never reveal directly):
{knowledge}

Speaking style: {style}

The hero currently carries: {inventory}
The hero has {hearts} hearts and {gold} gold.
The hero has visited {visited_count} locations.

Rules:
- Stay in character at all times.
- Give hints and clues, never exact coordinates or step-by-step instructions.
- Use in-world language (say "coins" not "gold points", "the cold one" not "Frost Wyrm").
- Be helpful but mysterious — guide, don't solve.
- Keep responses to 2-3 sentences."""


# ---------------------------------------------------------------------------
# Stub oracle for Phase 1 (provided complete)
# ---------------------------------------------------------------------------

def stub_oracle(npc: NPC, question: str, hero: Hero) -> str:
    """Keyword-matched canned responses for the rule-based agent (Phase 1).

    Returns NPC-flavored hints based on keywords in the question.
    No LLM needed — just pattern matching.
    """
    q = question.lower()
    name = npc.name

    if name == "Old Hermit":
        if any(kw in q for kw in ["frost", "wyrm", "dragon", "cold", "ice", "north"]):
            return ("The cold one stirs in the north... only summer's fury can melt "
                    "its frozen heart. Seek the dwarf in the markets — he forges wonders, "
                    "but needs ore that burns.")
        if any(kw in q for kw in ["fire", "sunblade", "weapon", "sword", "forge"]):
            return ("A blade of fire, yes... the dwarf blacksmith to the south knows the "
                    "craft. But he needs Ember Ore — burning stones from the western forests. "
                    "The witch of the woods knows where they sleep.")
        if any(kw in q for kw in ["treasure", "gold", "money"]):
            return ("Riches? There are treasures scattered across the land. I sense one "
                    "nearby to the southwest... and others far to the north and east.")
        if any(kw in q for kw in ["letter", "deliver", "message"]):
            if hero.has_item("Letter"):
                return ("A letter? For me? How wonderful! Let me read it...")
            return "I receive few messages these days. Perhaps someone seeks a courier?"
        if any(kw in q for kw in ["help", "quest", "what", "who", "where", "how"]):
            return ("The land is troubled, young one. Beasts stir in the shadows, "
                    "and fire sleeps beneath the mountains. Seek the witch in the heart "
                    "of the forest — she sees what others cannot.")
        return ("Hmm... the winds carry many secrets. Ask me of the cold one, "
                "of fire and shadow, and I shall speak what I know.")

    if name == "Traveling Merchant":
        if any(kw in q for kw in ["shadow", "beast", "dark", "east", "light", "moon"]):
            return ("The shadow that lurks in the eastern ruins? Pure moonlight, friend. "
                    "Only thing it fears. I hear the innkeeper's wife up north once had "
                    "a stone that glowed like the moon itself.")
        if any(kw in q for kw in ["moonstone", "lantern", "inn", "innkeeper"]):
            return ("The Northern Inn, yes! The innkeeper there — his wife had a "
                    "Moonstone of incredible power. But she's fallen ill. Perhaps if "
                    "someone brought medicine... the Enchanter Shop can craft a lantern from it.")
        if any(kw in q for kw in ["letter", "deliver", "errand", "job", "work", "task"]):
            return ("Actually, I do have a job for you! I need this letter delivered "
                    "to the Old Hermit down south. 2 gold for the trouble. What do you say?")
        if any(kw in q for kw in ["buy", "sell", "shop", "item", "price"]):
            return ("I'm more of a middleman, friend. But there's a fine blacksmith "
                    "to the south and an enchanter to the north-west. Both craft wonders!")
        if any(kw in q for kw in ["help", "quest", "what", "who", "where", "how"]):
            return ("Looking for work? There's a shadow beast terrorizing the east, "
                    "treasure scattered about, and I've got a letter that needs delivering. "
                    "Plenty of opportunity for a hero like you!")
        return ("Business is business, friend! Ask me about the shadow in the east, "
                "or perhaps you'd like a delivery job?")

    if name == "Forest Witch":
        if any(kw in q for kw in ["ember", "ore", "fire", "burning", "stone"]):
            return ("The burning stones? They sleep where the western trees grow "
                    "tallest, child. A forest to the northwest, where the ground "
                    "itself is warm. Tread carefully.")
        if any(kw in q for kw in ["ghostcap", "mushroom", "medicine", "brew", "cure", "sick", "remedy"]):
            if hero.has_item("Ghostcaps"):
                return ("You have the Ghostcaps! Yes, I can brew a remedy. "
                        "Give them to me and I shall prepare the medicine.")
            return ("Ghostcaps... pale fungi that grow only in the darkest northern "
                    "forests. Bring me three and I can brew a medicine potent enough "
                    "to cure any ailment.")
        if any(kw in q for kw in ["moonstone", "shadow", "light", "moon"]):
            return ("The moon's light is powerful against the darkness. The Northern "
                    "innkeeper's wife carries a Moonstone, but she is ill. Heal her "
                    "and perhaps the stone is yours.")
        if any(kw in q for kw in ["help", "quest", "what", "who", "where", "how"]):
            return ("The forest speaks to me, child. I know where the burning stones "
                    "hide and where the pale caps grow. I can brew remedies from "
                    "nature's gifts. What do you seek?")
        return ("The trees whisper of your journey. Ask me of the burning stones, "
                "the pale mushrooms, or the remedies I brew.")

    return f"{name} looks at you quizzically but says nothing useful."


# ---------------------------------------------------------------------------
# Phase 2: LLM-powered oracle (students implement these)
# ---------------------------------------------------------------------------

def build_npc_system_prompt(npc: NPC, hero: Hero) -> str:
    """Build a system prompt for an NPC based on their personality and knowledge.

    TODO (Phase 2): Implement this function.

    Use the ORACLE_TEMPLATE above as a starting point. Fill in:
    - npc.name, npc.personality, npc.knowledge, npc.style
    - hero.inventory, hero.hearts, hero.gold, hero.visited

    The system prompt should make the NPC:
    - Stay in character and never break the fourth wall
    - Give hints based on their knowledge, not direct answers
    - Be aware of what the hero is carrying and has done
    - Keep responses to 2-3 sentences

    Returns:
        str: The system prompt for the NPC.
    """
    # ========================
    # YOUR CODE HERE (Phase 2)
    # ========================
    raise NotImplementedError("TODO: Implement build_npc_system_prompt for Phase 2")


def ask_npc(npc: NPC, question: str, hero: Hero, client) -> str:
    """Ask an NPC a question using the Gemini API.

    TODO (Phase 2): Implement this function.

    Steps:
    1. Call build_npc_system_prompt() to get the system prompt.
    2. Use client.models.generate_content() with:
       - model="gemini-2.0-flash"
       - contents=question
       - config=genai.types.GenerateContentConfig(
             system_instruction=<your system prompt>,
             max_output_tokens=300,
         )
    3. Return response.text

    Args:
        npc: The NPC to talk to.
        question: The hero's question.
        hero: The hero (for context in the system prompt).
        client: A genai.Client() instance.

    Returns:
        str: The NPC's in-character response.
    """
    # ========================
    # YOUR CODE HERE (Phase 2)
    # ========================
    raise NotImplementedError("TODO: Implement ask_npc for Phase 2")
