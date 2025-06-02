class FloorManager:
    """Manages multiple dungeon floors and player transitions"""

    def __init__(self):
        self.floors = {}  # Dictionary to store floor data: {floor_number: world_data}
        self.current_floor = 1

    def save_floor(self, floor_number, world):
        """Save current floor state"""
        # Save the essential world data
        floor_data = {
            'tiles': [row[:] for row in world.tiles],  # Deep copy tiles
            'monsters': world.monsters[:],  # Copy monster list
            'rooms': world.rooms[:],  # Copy room list
            'staircases': world.staircases[:]  # Copy staircase list
        }
        self.floors[floor_number] = floor_data

    def load_floor(self, floor_number):
        """Load a previously saved floor, or return None if new floor"""
        return self.floors.get(floor_number, None)

    def has_floor(self, floor_number):
        """Check if floor has been visited before"""
        return floor_number in self.floors