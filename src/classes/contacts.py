"""
Module for managing NPC contacts in the game world.
"""

from src.classes.game import Contact

# Terminus Bar Contacts
KELL_VOSS = Contact(
    name="Kell Voss",
    description="A battle-scarred mercenary with cybernetic enhancements and a reputation for getting jobs done.",
    location="Terminus Bar",
    specialty="Combat contracts, security operations, and intel on dangerous sectors.",
    faction="military",
    age=42,
    sex="male",
)

NOVA_VALEN = Contact(
    name="Nova Valen",
    description="An alluring yet deadly bounty hunter with a mysterious past and a reputation for giving targets one last chance.",
    location="Terminus Bar",
    specialty="Tracking fugitives, gathering intelligence, and off-the-books security work.",
    faction="explorers",
    age=34,
    sex="female",
)

ZETA_9 = Contact(
    name="Zeta-9",
    description="A mysterious tech expert with partially synthetic components. Known for custom ship modifications.",
    location="Terminus Bar",
    specialty="Ship upgrades, rare tech, and engineering solutions.",
    faction="scientists",
    age=35,
    sex="male",
)

OBSIDIAN = Contact(
    name="Obsidian",
    description="A cybernetic bartender with optical implants and access to station information networks.",
    location="Terminus Bar",
    specialty="Information brokering, local gossip, and business connections.",
    faction="traders",
    age=28,
    sex="female",
)

# Dictionary mapping contact type to contact objects for easy lookup
TERMINUS_CONTACTS_OBJECTS = {
    "mercenary": KELL_VOSS,
    "bounty_hunter": NOVA_VALEN,
    "engineer": ZETA_9,
    "bartender": OBSIDIAN,
}


# Function to get contact by type
def get_contact(contact_type: str) -> Contact:
    """
    Get a contact object by its type.

    Args:
        contact_type (str): The type of contact to retrieve ("mercenary", "bounty_hunter", "engineer", "bartender")

    Returns:
        Contact: The contact object

    Raises:
        KeyError: If the contact type doesn't exist
    """
    if contact_type in TERMINUS_CONTACTS_OBJECTS:
        return TERMINUS_CONTACTS_OBJECTS[contact_type]
    raise KeyError(f"Contact type '{contact_type}' not found")
