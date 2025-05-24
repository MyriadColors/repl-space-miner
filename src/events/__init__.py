"""
Events module containing various events that can occur during gameplay.
"""

from .ftl_events import (
    get_random_ftl_event as get_random_ftl_event,
    FTLEvent as FTLEvent,
)
from .character_creation import character_creation_event as character_creation_event
from .skill_events import (
    process_skill_xp_from_activity as process_skill_xp_from_activity,
    notify_skill_progress as notify_skill_progress,
)
