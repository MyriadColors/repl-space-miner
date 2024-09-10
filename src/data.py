from dataclasses import dataclass
from random import choice

from src.classes.ore import Ore

# This will be used to generate random names
name_parts = [
    'ha', 'he', 'hi', 'ho', 'hu', 'ca', 'ce', 'ci', 'co', 'cu',
    'sa', 'se', 'si', 'so', 'su', 'ja', 'ji', 'je', 'jo', 'ju', 'an',
    'pa', 'pe', 'pi', 'po', 'pu', 'ta', 'te', 'ti', 'to', 'tu',
    'kle', 'ke', 'ki', 'ko', 'ku', 'sha', 'she', 'shi', 'sho', 'shu',
    'hor', 'cer', 'cur', 'her', 'hur', 'sar', 'arn', 'irn', 'kler',
    'ka', 'la', 'nar', 'kar', 'bar', 'dar', 'blar', 'ger', 'yur',
    'zor', 'for', 'wor', 'gor', 'noth', 'roth', 'moth', 'zoth',
    'loth', 'nith', 'lith', 'sith', 'dith', 'ith', 'oth', 'orb', 'urb',
    'er', 'zer', 'ze', 'zera', 'ter', 'nor', 'za', 'zi', 'di', 'mi',
    'per', 'pir', 'pera', 'par', 'sta', 'mor', 'kur', 'ker', 'ni'
                                                             'ler', 'der', 'ber', 'shar', 'sher', 'mer', 'wer', 'fer',
    'fra'
    'gra', 'bra', 'zir', 'dir', 'tir', 'sir', 'mir', 'nir', 'por',
    'lir', 'bir', 'dra', 'tha', 'the', 'tho',
    'ta', 'te', 'ti', 'to', 'tu', 'ba', 'be', 'bi', 'bo', 'tis', 'ris',
    'beur', 'bu', 'cu', 'lur', 'mur', 'da', 'de', 'di', 'do', 'ka',
    'ke', 'ki', 'ko', 'ku', 'la', 'le', 'li', 'lo', 'lu', 'loo', 'koo',
    'lee', 'kee', 'du', 'lor', 'der', 'ser', 'per', 'fu', 'fer', 'ler',
    'zer', 'wi', 'na', 'ne', 'no', 'noo', 'ra', 'ri', 'ro', 'roo', 'va',
    've', 'vi', 'vo', 'vu', 'bre', 'dre', 'pre', 'tre', 'gre']


def generate_random_name(parts_num: int) -> str:
    return (''.join(choice(name_parts) for _ in range(parts_num))).capitalize()


@dataclass
class OreCargo:
    ore: Ore
    quantity: int
    buy_price: float
    sell_price: float


upgrade_data: dict = {
    "speed": {
        "price": 100_000,
        "multiplier": 1.05,
        "description": "Increases the ship's speed by 5%",
    },
    "mining_speed": {
        "price": 250_000,
        "multiplier": 1.05,
        "description": "Increases the ship's mining speed by 5%",
    },
    "fuel_consumption": {
        "price": 100_000,
        "multiplier": 1.05,
        "description": "Increases the ship's fuel consumption by 5%",
    },
    "fuel_capacity": {
        "price": 150_000,
        "multiplier": 1.05,
        "description": "Increases the ship's fuel capacity by 5%",
    },
    "cargo_capacity": {
        "price": 150_000,
        "multiplier": 1.05,
        "description": "Increases the ship's cargo capacity by 5%",
    }

}