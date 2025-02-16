import pygame

color_example = (0 ,0, 0)

colors: dict[str, tuple[int, int, int]] = {
    "black": (0, 0, 0),
    "gray16": (16, 16, 16),
    "gray24": (24, 24, 24),
    "gray32": (32, 32, 32),
    "gray48": (48, 48, 48),
    "gray64": (64, 64, 64),
    "gray80": (80, 80, 80),
    "gray96": (96, 96, 96),
    "gray112": (112, 112, 112),
    "gray128": (128, 128, 128),
    "gray144": (144, 144, 144),
    "gray160": (160, 160, 160),
    "gray176": (176, 176, 176),
    "gray192": (192, 192, 192),
    "gray208": (208, 208, 208),
    "gray224": (224, 224, 224),
    "gray240": (240, 240, 240),
    "white": (255, 255, 255),
    "red16": (16, 0, 0),
    "red32": (32, 0, 0),
    "red48": (48, 0, 0),
    "red64": (64, 0, 0),
    "red80": (80, 0, 0),
    "red96": (96, 0, 0),
    "red112": (112, 0, 0),
    "red128": (128, 0, 0),
    "red144": (144, 0, 0),
    "red160": (160, 0, 0),
    "red176": (176, 0, 0),
    "red192": (192, 0, 0),
    "red208": (208, 0, 0),
    "red224": (224, 0, 0),
    "red240": (240, 0, 0),
    "red": (255, 0, 0),
    "green16": (0, 16, 0),
    "green32": (0, 32, 0),
    "green48": (0, 48, 0),
    "green64": (0, 64, 0),
    "green80": (0, 80, 0),
    "green96": (0, 96, 0),
    "green112": (0, 112, 0),
    "green128": (0, 128, 0),
    "green144": (0, 144, 0),
    "green160": (0, 160, 0),
    "green176": (0, 176, 0),
    "green192": (0, 192, 0),
    "green208": (0, 208, 0),
    "green224": (0, 224, 0),
    "green240": (0, 240, 0),
    "green": (0, 255, 0),
    "blue16": (0, 0, 16),
    "blue32": (0, 0, 32),
    "blue48": (0, 0, 48),
    "blue64": (0, 0, 64),
    "blue80": (0, 0, 80),
    "blue96": (0, 0, 96),
    "blue112": (0, 0, 112),
    "blue128": (0, 0, 128),
    "blue144": (0, 0, 144),
    "blue160": (0, 0, 160),
    "blue176": (0, 0, 176),
    "blue192": (0, 0, 192),
    "blue208": (0, 0, 208),
    "blue224": (0, 0, 224),
    "blue240": (0, 0, 240),
    "blue": (0, 0, 255),
    "yellow16": (16, 16, 0),
    "yellow32": (32, 32, 0),
    "yellow48": (48, 48, 0),
    "yellow64": (64, 64, 0),
    "yellow80": (80, 80, 0),
    "yellow96": (96, 96, 0),
    "yellow112": (112, 112, 0),
    "yellow128": (128, 128, 0),
    "yellow144": (144, 144, 0),
    "yellow160": (160, 160, 0),
    "yellow176": (176, 176, 0),
    "yellow192": (192, 192, 0),
    "yellow208": (208, 208, 0),
    "yellow224": (224, 224, 0),
    "yellow": (255, 255, 0),
    "pastel_green": (83, 145, 84),
    "pastel_blue": (80, 106, 136),
    "pastel_red": (129, 39, 23),
}

def find_color_by_name(color_str: str) -> dict[str, tuple[int, int, int]] | None:
    if color_str in colors:
        return {color_str: colors[color_str]}
    
    return None

def color_name_to_pygame_color(color_str: str) -> pygame.color.Color | None:
    color_info = find_color_by_name(color_str)
    if color_info is None:
        return None
    rgb = list(color_info.values())[0]
    return pygame.color.Color(r=rgb[0], g=rgb[1], b=rgb[2])

def get_color(color_str: str):
    return colors[color_str]

def does_color_exist(color_str: str):
    return color_str in colors
