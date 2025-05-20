from pygame import Vector2


class IsSpaceObject:
    """Base class for all space objects with position and ID"""

    def __init__(self, position: Vector2, id: int) -> None:
        self.position: Vector2 = position
        self.id: int = id

    def get_position(self) -> Vector2:
        return self.position

    def set_position(self, new_position: Vector2) -> None:
        self.position = new_position

    def get_id(self):
        return self.id


class CanMove:
    """Mixin for objects that can move"""

    def __init__(self, speed: float):
        self.speed: float = speed

    def get_speed(self):
        return self.speed

    def set_speed(self, new_speed):
        self.speed = new_speed
