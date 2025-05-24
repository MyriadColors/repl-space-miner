# repl-space-miner initialization file
"""
This module initializes the REPL Space Miner game components
"""

# Import key components to make them available at the package level
from . import events as events  # Ensures events module is imported properly
from . import repl as repl
from . import helpers as helpers
from . import data as data
from . import command_handlers as command_handlers
from .classes import (
    game as game,
    ship as ship,
    asteroid as asteroid,
    ore as ore,
    solar_system as solar_system,
    station as station,
)
