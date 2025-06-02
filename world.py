import random

from monster import create_goblin, create_orc, create_rat


class FloorItem:
    """Represents an item lying on the dungeon floor"""

    def __init__(self, item, x, y):
        self.item = item
        self.x = x
        self.y = y
        self.symbol = item.symbol
        self.name = item.name

class Tile:
    """Represents a single tile in the world"""

    def __init__(self, char='#', walkable=False, transparent=False, tile_type='wall'):
        self.char = char  # What character to display
        self.walkable = walkable  # Can player/monsters walk on it?
        self.transparent = transparent  # Can you see through it?
        self.tile_type = tile_type  # 'wall', 'floor', 'door_closed', 'door_open', etc.

        # Door-specific properties
        self.locked = False  # Is the door locked?
        self.broken = False  # Is the door broken/destroyed?


class Door(Tile):
    """Special tile type for doors"""

    def __init__(self, locked=False):
        # Closed door starts as '+'
        super().__init__(char='+', walkable=False, transparent=False, tile_type='door_closed')
        self.locked = locked
        self.broken = False

        # Ensure FOV properties are initialized (in case parent __init__ didn't set them)
        self.explored = False
        self.visible = False

    def open_door(self):
        """Open the door (if not locked)"""
        if self.locked:
            return False  # Can't open locked door

        self.char = '/'
        self.walkable = True
        self.transparent = True
        self.tile_type = 'door_open'
        return True

    def close_door(self):
        """Close the door (if it's open and not broken)"""
        if self.broken or self.tile_type != 'door_open':
            return False

        self.char = '+'
        self.walkable = False
        self.transparent = False
        self.tile_type = 'door_closed'
        return True

    def kick_door(self):
        """Try to kick down the door - returns (success, broke_door)"""
        import random

        if self.tile_type == 'door_open':
            return (True, False)  # Already open

        # Chance to succeed based on door state
        if self.locked:
            success_chance = 0.7  # 70% chance to break locked door
        else:
            success_chance = 0.9  # 90% chance to break unlocked door

        if random.random() < success_chance:
            # Door is broken open permanently
            self.char = '.'  # Broken door becomes floor
            self.walkable = True
            self.transparent = True
            self.tile_type = 'floor'
            self.broken = True
            self.locked = False
            return (True, True)  # Success, door broken
        else:
            return (False, False)  # Failed to break door


class Staircase(Tile):
    """Special tile type for staircases"""

    def __init__(self, direction, target_floor=None):
        if direction == 'down':
            char = '>'
            desc = "downward staircase"
        else:  # up
            char = '<'
            desc = "upward staircase"

        super().__init__(char=char, walkable=True, transparent=True, tile_type='staircase')
        self.direction = direction  # 'up' or 'down'
        self.target_floor = target_floor  # Which floor this leads to
        self.description = desc

        # Ensure FOV properties are initialized
        self.explored = False
        self.visible = False


class Room:
    """Represents a rectangular room"""

    def __init__(self, x, y, width, height):
        self.x = x  # Top-left corner x
        self.y = y  # Top-left corner y
        self.width = width  # Room width
        self.height = height  # Room height

    def center(self):
        """Return the center coordinates of the room"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        return (center_x, center_y)

    def intersects(self, other_room):
        """Check if this room overlaps with another room"""
        return (self.x <= other_room.x + other_room.width and
                self.x + self.width >= other_room.x and
                self.y <= other_room.y + other_room.height and
                self.y + self.height >= other_room.y)


class World:
    """Manages the game world/dungeon"""

    def __init__(self, width=80, height=25):
        self.width = width
        self.height = height
        self.rooms = []
        self.monsters = []
        # Floor management
        self.current_floor = 1
        self.staircases = []

        # Create the tile grid - start with all empty space
        self.tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                # Create empty space tiles by default
                empty_tile = Tile(char=' ', walkable=False, transparent=True)
                row.append(empty_tile)
            self.tiles.append(row)

        # Generate the dungeon
        self.generate_dungeon()

        # Add walls around rooms and corridors
        self.add_walls()

        # Initialize FOV properties for all tiles
        self.initialize_fov_properties()
        self.spawn_monsters()
        # Add staircases
        self.add_staircases()
        # Initialize floor items
        self.floor_items = []

    def generate_dungeon(self):
        """Generate a simple dungeon with rooms and corridors"""
        # Try to place several rooms
        max_rooms = 10
        room_min_size = 6
        room_max_size = 12

        for attempt in range(max_rooms):
            # Random room dimensions and position
            room_width = random.randint(room_min_size, room_max_size)
            room_height = random.randint(room_min_size, room_max_size)

            # Random position (leave space for walls)
            x = random.randint(1, self.width - room_width - 1)
            y = random.randint(1, self.height - room_height - 1)

            new_room = Room(x, y, room_width, room_height)

            # Check if room overlaps with existing rooms
            room_overlaps = False
            for existing_room in self.rooms:
                if new_room.intersects(existing_room):
                    room_overlaps = True
                    break

            if not room_overlaps:
                # Room is valid, add it to the world
                self.create_room(new_room)
                self.rooms.append(new_room)

                # Connect to previous room with a corridor
                if len(self.rooms) > 1:
                    self.create_corridor(self.rooms[-2], new_room)

    def create_room(self, room):
        """Carve out a room in the tile grid"""
        for y in range(room.y + 1, room.y + room.height - 1):
            for x in range(room.x + 1, room.x + room.width - 1):
                # Create floor tiles
                floor_tile = Tile(char='.', walkable=True, transparent=True)
                self.tiles[y][x] = floor_tile

    def create_corridor(self, room1, room2):
        """Create an L-shaped corridor between two rooms"""
        # Get center points of both rooms
        x1, y1 = room1.center()
        x2, y2 = room2.center()

        # Create L-shaped corridor
        # First horizontal, then vertical
        if random.randint(0, 1) == 0:
            # Move horizontally first, then vertically
            self.create_h_tunnel(x1, x2, y1)
            self.create_v_tunnel(y1, y2, x2)
        else:
            # Move vertically first, then horizontally
            self.create_v_tunnel(y1, y2, x1)
            self.create_h_tunnel(x1, x2, y2)

        # Add doors at room entrances (sometimes)
        self.maybe_add_doors_to_room(room1)
        self.maybe_add_doors_to_room(room2)

    def create_h_tunnel(self, x1, x2, y):
        """Create a horizontal tunnel"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                floor_tile = Tile(char='.', walkable=True, transparent=True)
                self.tiles[y][x] = floor_tile

    def create_v_tunnel(self, y1, y2, x):
        """Create a vertical tunnel"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                floor_tile = Tile(char='.', walkable=True, transparent=True)
                self.tiles[y][x] = floor_tile

    def is_walkable(self, x, y):
        """Check if a position can be walked on"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x].walkable
        return False

    def get_tile_char(self, x, y):
        """Get the display character for a position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x].char
        return ' '  # Outside world bounds

    def maybe_add_doors_to_room(self, room):
        """Add doors only at narrow chokepoints (1-tile wide passages)"""
        door_positions = []

        # Check each edge of the room for potential door locations
        # Top edge
        for x in range(room.x + 1, room.x + room.width - 1):
            y = room.y
            if (y > 0 and
                    self.tiles[y - 1][x].char == '.' and  # Corridor above
                    self.tiles[y][x].char == '.' and  # Floor below (room entrance)
                    self.is_narrow_corridor_entrance(x, y - 1, 'vertical')):
                door_positions.append((x, y))

        # Bottom edge
        for x in range(room.x + 1, room.x + room.width - 1):
            y = room.y + room.height - 1
            if (y < self.height - 1 and
                    self.tiles[y + 1][x].char == '.' and  # Corridor below
                    self.tiles[y][x].char == '.' and  # Floor above (room entrance)
                    self.is_narrow_corridor_entrance(x, y + 1, 'vertical')):
                door_positions.append((x, y))

        # Left edge
        for y in range(room.y + 1, room.y + room.height - 1):
            x = room.x
            if (x > 0 and
                    self.tiles[y][x - 1].char == '.' and  # Corridor to left
                    self.tiles[y][x].char == '.' and  # Floor to right (room entrance)
                    self.is_narrow_corridor_entrance(x - 1, y, 'horizontal')):
                door_positions.append((x, y))

        # Right edge
        for y in range(room.y + 1, room.y + room.height - 1):
            x = room.x + room.width - 1
            if (x < self.width - 1 and
                    self.tiles[y][x + 1].char == '.' and  # Corridor to right
                    self.tiles[y][x].char == '.' and  # Floor to left (room entrance)
                    self.is_narrow_corridor_entrance(x + 1, y, 'horizontal')):
                door_positions.append((x, y))

        # Place doors at some of these positions
        for x, y in door_positions:
            if random.random() < 0.5:  # 50% chance for each valid door spot
                # 25% chance door is locked
                is_locked = random.random() < 0.25
                door = Door(locked=is_locked)
                self.tiles[y][x] = door

    def is_narrow_corridor_entrance(self, x, y, direction):
        """Check if this position is a narrow corridor entrance to a room"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        if self.tiles[y][x].char != '.':
            return False  # Not a corridor

        if direction == 'vertical':
            # For vertical corridor (going up/down), check left and right sides
            left_blocked = (x == 0 or self.tiles[y][x - 1].char in ['#', ' '])
            right_blocked = (x == self.width - 1 or self.tiles[y][x + 1].char in ['#', ' '])

            # Must be blocked on both sides to be narrow
            return left_blocked and right_blocked

        elif direction == 'horizontal':
            # For horizontal corridor (going left/right), check above and below
            top_blocked = (y == 0 or self.tiles[y - 1][x].char in ['#', ' '])
            bottom_blocked = (y == self.height - 1 or self.tiles[y + 1][x].char in ['#', ' '])

            # Must be blocked on both sides to be narrow
            return top_blocked and bottom_blocked

        return False
    def is_narrow_passage(self, x, y, direction):
        """Check if position (x,y) is part of a 1-tile wide passage"""
        if direction == 'horizontal':
            # For a horizontal corridor to be narrow, it should have walls above AND below
            above_blocked = (y <= 0 or self.tiles[y - 1][x].char != '.')
            below_blocked = (y >= self.height - 1 or self.tiles[y + 1][x].char != '.')
            return above_blocked and below_blocked

        elif direction == 'vertical':
            # For a vertical corridor to be narrow, it should have walls left AND right
            left_blocked = (x <= 0 or self.tiles[y][x - 1].char != '.')
            right_blocked = (x >= self.width - 1 or self.tiles[y][x + 1].char != '.')
            return left_blocked and right_blocked

        return False

    def add_walls(self):
        """Add walls adjacent to floor tiles"""
        # Go through every tile
        for y in range(self.height):
            for x in range(self.width):
                # If this tile is empty space, check if it should be a wall
                if self.tiles[y][x].char == ' ':
                    should_be_wall = False

                    # Check all 8 adjacent positions
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue  # Skip the center tile

                            adj_x, adj_y = x + dx, y + dy

                            # If adjacent tile is within bounds and is a floor
                            if (0 <= adj_x < self.width and
                                    0 <= adj_y < self.height and
                                    self.tiles[adj_y][adj_x].char == '.'):
                                should_be_wall = True
                                break

                        if should_be_wall:
                            break

                    # Convert empty space to wall if adjacent to floor
                    if should_be_wall:
                        wall_tile = Tile(char='#', walkable=False, transparent=False)
                        self.tiles[y][x] = wall_tile

    def get_tile(self, x, y):
        """Get the tile object at a position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def try_open_door(self, x, y):
        """Try to open a door at position (x, y). Returns (success, message)"""
        tile = self.get_tile(x, y)

        if not tile or tile.tile_type != 'door_closed':
            return (False, "There's no closed door here.")

        if isinstance(tile, Door):
            if tile.open_door():
                return (True, "You open the door.")
            else:
                return (False, "The door is locked!")

        return (False, "Something went wrong.")

    def try_kick_door(self, x, y):
        """Try to kick down a door at position (x, y). Returns (success, message)"""
        tile = self.get_tile(x, y)

        if not tile or not tile.tile_type.startswith('door'):
            return (False, "There's no door here to kick.")

        if tile.tile_type == 'door_open':
            return (False, "The door is already open.")

        if isinstance(tile, Door):
            success, broke = tile.kick_door()
            if success:
                if broke:
                    return (True, "You kick the door down! It splinters apart.")
                else:
                    return (True, "You kick the door open.")
            else:
                return (False, "You kick the door but it holds firm.")

        return (False, "Something went wrong.")

    def try_close_door(self, x, y):
        """Try to close an open door at position (x, y). Returns (success, message)"""
        tile = self.get_tile(x, y)

        if not tile or tile.tile_type != 'door_open':
            return (False, "There's no open door here.")

        if isinstance(tile, Door):
            if tile.close_door():
                return (True, "You close the door.")
            else:
                return (False, "The door can't be closed.")

        return (False, "Something went wrong.")

    def initialize_fov_properties(self):
        """Ensure all tiles have FOV properties initialized"""
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if not hasattr(tile, 'visible'):
                    tile.visible = False
                if not hasattr(tile, 'explored'):
                    tile.explored = False

    def spawn_monsters(self):
        """Spawn monsters in random rooms"""
        import random

        # Monster spawn chances per room
        spawn_chance = 0.4  # 30% chance a room has monsters

        for room in self.rooms:
            if random.random() < spawn_chance:
                # Decide how many monsters (1-3)
                num_monsters = random.randint(1, 2)

                for _ in range(num_monsters):
                    # Find random position in room
                    attempts = 0
                    while attempts < 20:  # Try up to 20 times
                        monster_x = random.randint(room.x + 1, room.x + room.width - 2)
                        monster_y = random.randint(room.y + 1, room.y + room.height - 2)

                        # Check if position is clear
                        if (self.is_walkable(monster_x, monster_y) and
                                not self.monster_at_position(monster_x, monster_y)):

                            # Choose monster type randomly
                            monster_type = random.choice(['rat', 'goblin', 'orc'])

                            if monster_type == 'rat':
                                monster = create_rat(monster_x, monster_y)
                            elif monster_type == 'goblin':
                                monster = create_goblin(monster_x, monster_y)
                            else:  # orc
                                monster = create_orc(monster_x, monster_y)

                            self.monsters.append(monster)
                            break

                        attempts += 1

    def add_staircases(self):
        """Add staircases to the current floor"""
        # First floor only has down staircase
        if self.current_floor == 1:
            self.place_staircase('down')
        else:
            # Other floors have both up and down
            self.place_staircase('up', self.current_floor - 1)  # Back to previous floor
            self.place_staircase('down')  # To next floor

    def place_staircase(self, direction, target_floor=None):
        """Place a staircase in a random room"""
        if not self.rooms:
            return

        # Try to place staircase in a random room
        attempts = 0
        while attempts < 50:
            room = random.choice(self.rooms)

            # Find random position in room
            x = random.randint(room.x + 1, room.x + room.width - 2)
            y = random.randint(room.y + 1, room.y + room.height - 2)

            # Check if position is clear (no monsters, no other staircases)
            if (self.is_walkable(x, y) and
                    not self.monster_at_position(x, y) and
                    not self.staircase_at_position(x, y)):

                if direction == 'down':
                    target_floor = self.current_floor + 1

                staircase = Staircase(direction, target_floor)
                self.tiles[y][x] = staircase
                self.staircases.append((x, y, direction, target_floor))
                break

            attempts += 1

    def staircase_at_position(self, x, y):
        """Check if there's a staircase at the given position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.tiles[y][x]
            return isinstance(tile, Staircase)
        return False

    def get_staircase_at_position(self, x, y):
        """Get staircase at position if it exists"""
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.tiles[y][x]
            if isinstance(tile, Staircase):
                return tile
        return None

    def monster_at_position(self, x, y):
        """Check if there's a monster at the given position"""
        for monster in self.monsters:
            if monster.x == x and monster.y == y and monster.is_alive():
                return monster
        return None

    def get_monsters_in_fov(self):
        """Get all monsters currently visible to the player"""
        visible_monsters = []
        for monster in self.monsters:
            if (monster.is_alive() and
                    0 <= monster.x < self.width and
                    0 <= monster.y < self.height and
                    self.tiles[monster.y][monster.x].visible):
                visible_monsters.append(monster)
        return visible_monsters

    def update_monster_ai(self, player_x, player_y):
        """Update AI for all monsters"""
        for monster in self.monsters:
            if not monster.is_alive():
                continue

            # Check if monster can see player
            if (0 <= monster.x < self.width and
                    0 <= monster.y < self.height and
                    self.tiles[monster.y][monster.x].visible):
                # Monster sees player - start chasing
                monster.has_seen_player = True
                monster.target_x = player_x
                monster.target_y = player_y

            # Move monster if it has a target
            if monster.has_seen_player and monster.target_x is not None:
                self.move_monster_toward_target(monster, player_x, player_y)

    def move_monster_toward_target(self, monster, player_x, player_y):
        """Move monster one step toward its target"""
        if monster.target_x is None or monster.target_y is None:
            return "no_target"

        # Calculate direction to target
        dx = 0
        dy = 0

        if monster.target_x > monster.x:
            dx = 1
        elif monster.target_x < monster.x:
            dx = -1

        if monster.target_y > monster.y:
            dy = 1
        elif monster.target_y < monster.y:
            dy = -1

        # Try to move
        new_x = monster.x + dx
        new_y = monster.y + dy

        # Check if new position has the player (for attack)
        if new_x == player_x and new_y == player_y:
            return "attack_player"
        elif (self.is_walkable(new_x, new_y) and
              not self.monster_at_position(new_x, new_y)):
            monster.x = new_x
            monster.y = new_y
            return "moved"

        return "blocked"

    def handle_combat(self, attacker, defender):
        """Handle combat between two entities"""
        import random

        # Calculate damage
        if hasattr(attacker, 'get_attack_damage'):
            damage = attacker.attack + random.randint(-1, 1)

        else:
            damage = attacker.attack + random.randint(-1, 1)

        # Apply Defense
        if hasattr(defender, 'defense'):
            actual_damage = max(1, damage - defender.defense)
        else:
            actual_damage = damage

        # Apply damage
        defender_died = defender.take_damage(actual_damage)

        # Create combat message
        if hasattr(attacker, 'name') and hasattr(defender, 'name'):
            message = f"{attacker.name} attacks {defender.name} for {actual_damage} damage!"
        elif hasattr(attacker, 'name'):
            message = f"{attacker.name} attacks you for {actual_damage} damage!"
        else:
            message = f"You attack {defender.name} for {actual_damage} damage!"

        return message, defender_died

    def remove_dead_monsters(self):
        """Remove dead monsters from the world"""
        self.monsters = [monster for monster in self.monsters if monster.is_alive()]

    def drop_loot_from_monster(self, monster, floor_level):
        """Try to drop loot from a defeated monster"""
        from items import get_loot_for_monster

        # Get loot for this monster type
        loot_item = get_loot_for_monster(monster.name, floor_level)

        if loot_item:
            # Try to place the item on the ground near the monster
            drop_positions = [
                (monster.x, monster.y),  # Same position as monster
                (monster.x + 1, monster.y), (monster.x - 1, monster.y),  # Adjacent positions
                (monster.x, monster.y + 1), (monster.x, monster.y - 1),
                (monster.x + 1, monster.y + 1), (monster.x - 1, monster.y - 1),
                (monster.x + 1, monster.y - 1), (monster.x - 1, monster.y + 1)
            ]

            # Find first valid drop position
            for drop_x, drop_y in drop_positions:
                if (0 <= drop_x < self.width and 0 <= drop_y < self.height and
                        self.is_walkable(drop_x, drop_y) and
                        not self.monster_at_position(drop_x, drop_y) and
                        not self.item_at_position(drop_x, drop_y)):

                    # Create floor item
                    floor_item = FloorItem(loot_item, drop_x, drop_y)

                    # Add to world items list (we'll create this)
                    if not hasattr(self, 'floor_items'):
                        self.floor_items = []
                    self.floor_items.append(floor_item)

                    return f"The {monster.name} drops {loot_item.name}!"

            # If no valid position found, no drop message
            return None

        return None  # No loot dropped

    def item_at_position(self, x, y):
        """Check if there's an item on the ground at this position"""
        if not hasattr(self, 'floor_items'):
            return None

        for floor_item in self.floor_items:
            if floor_item.x == x and floor_item.y == y:
                return floor_item
        return None

    def pickup_item_at_position(self, x, y):
        """Pick up item from the ground at this position"""
        if not hasattr(self, 'floor_items'):
            return None

        for floor_item in self.floor_items:
            if floor_item.x == x and floor_item.y == y:
                self.floor_items.remove(floor_item)
                return floor_item.item
        return None

    def get_visible_floor_items(self):
        """Get all floor items that are currently visible"""
        if not hasattr(self, 'floor_items'):
            return []

        visible_items = []
        for floor_item in self.floor_items:
            if (0 <= floor_item.x < self.width and
                    0 <= floor_item.y < self.height and
                    self.tiles[floor_item.y][floor_item.x].visible):
                visible_items.append(floor_item)
        return visible_items

    def get_random_respawn_position(self):
        """Get a safe respawn position (away from monsters)"""
        attempts = 0
        while attempts < 50:
            x, y = self.get_random_floor_position()

            # Check if position is far enough from monsters
            safe = True
            for monster in self.monsters:
                if monster.is_alive():
                    distance = abs(x - monster.x) + abs(y - monster.y)
                    if distance < 5:  # Must be at least 5 tiles away
                        safe = False
                        break

            if safe:
                return (x, y)

            attempts += 1

        # Fallback: just return any floor position
        return self.get_random_floor_position()

        # Fallback: just return any floor position
        return self.get_random_floor_position()

    def update_fov(self, player_x, player_y, radius=8):
        """Update field of view from player position using raycasting"""
        import math

        # Clear all current visibility
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x].visible = False

        # Player position is always visible
        if 0 <= player_x < self.width and 0 <= player_y < self.height:
            self.tiles[player_y][player_x].visible = True
            self.tiles[player_y][player_x].explored = True

        # Cast rays in all directions
        # We'll use more rays for smoother FOV
        num_rays = 360  # One ray per degree

        for i in range(num_rays):
            # Calculate ray direction
            angle = (i * math.pi * 2) / num_rays
            ray_dx = math.cos(angle)
            ray_dy = math.sin(angle)

            # Cast this ray
            self.cast_ray(player_x, player_y, ray_dx, ray_dy, radius)

    def cast_ray(self, start_x, start_y, dx, dy, max_distance):
        """Cast a single ray and mark visible tiles"""
        # Start from player position
        current_x = float(start_x)
        current_y = float(start_y)

        # Step along the ray
        for distance in range(max_distance):
            # Move along ray
            current_x += dx
            current_y += dy

            # Convert to grid coordinates
            grid_x = int(round(current_x))
            grid_y = int(round(current_y))

            # Check bounds
            if not (0 <= grid_x < self.width and 0 <= grid_y < self.height):
                break

            # Mark this tile as visible and explored
            tile = self.tiles[grid_y][grid_x]
            tile.visible = True
            tile.explored = True

            # If this tile blocks vision, stop the ray here
            if not tile.transparent:
                break

    def get_tile_display_char(self, x, y):
        """Get the character to display for a tile based on visibility"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return ' '

        tile = self.tiles[y][x]

        # Ensure tile has FOV properties (defensive programming)
        if not hasattr(tile, 'visible'):
            tile.visible = False
        if not hasattr(tile, 'explored'):
            tile.explored = False

        if tile.visible:
            # Currently visible - show normal character
            return tile.char
        elif tile.explored:
            # Explored but not visible - show faded version
            # We'll use different characters for faded versions
            if tile.char == '#':
                return '▓'  # Faded wall
            elif tile.char == '.':
                return '·'  # Faded floor
            elif tile.char == '+':
                return '⸱'  # Faded closed door
            elif tile.char == '/':
                return '⸱'  # Faded open door
            else:
                return '░'  # Generic faded character
        else:
            # Never explored - completely hidden
            return ' '

    def find_nearest_unexplored(self, start_x, start_y):
        """Find the nearest unexplored tile from the given position"""
        from collections import deque

        # BFS to find nearest unexplored area
        queue = deque([(start_x, start_y, 0)])  # (x, y, distance)
        visited = set()
        visited.add((start_x, start_y))

        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),  # Cardinal directions
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # Diagonals
        ]

        while queue:
            x, y, distance = queue.popleft()

            # Check if this position is unexplored and walkable or adjacent to walkable
            if not self.tiles[y][x].explored:
                # Check if there's a walkable tile adjacent to this unexplored tile
                for dx, dy in directions:
                    adj_x, adj_y = x + dx, y + dy
                    if (0 <= adj_x < self.width and 0 <= adj_y < self.height and
                            self.tiles[adj_y][adj_x].walkable and
                            self.tiles[adj_y][adj_x].explored):
                        return (x, y)  # Return the unexplored tile position

            # Add adjacent positions to queue
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy

                if (0 <= new_x < self.width and 0 <= new_y < self.height and
                        (new_x, new_y) not in visited):
                    visited.add((new_x, new_y))
                    queue.append((new_x, new_y, distance + 1))

        return None  # No unexplored areas found

    def find_path_to(self, start_x, start_y, target_x, target_y):
        """Find a path from start to target using BFS. Returns next step or None."""
        from collections import deque

        if start_x == target_x and start_y == target_y:
            return None

        # BFS to find path
        queue = deque([(start_x, start_y, [])])  # (x, y, path)
        visited = set()
        visited.add((start_x, start_y))

        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),  # Cardinal directions first
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # Then diagonals
        ]

        while queue:
            x, y, path = queue.popleft()

            # Try each direction
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy

                # Check bounds
                if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                    continue

                # Skip if already visited
                if (new_x, new_y) in visited:
                    continue

                # Check if we can move to this tile
                tile = self.tiles[new_y][new_x]
                if not tile.walkable:
                    continue

                new_path = path + [(dx, dy)]

                # Check if we reached the target or got close to it
                distance_to_target = abs(new_x - target_x) + abs(new_y - target_y)
                if distance_to_target <= 1:  # Adjacent to target or on target
                    return new_path[0] if new_path else None  # Return first step

                visited.add((new_x, new_y))
                queue.append((new_x, new_y, new_path))

        return None  # No path found

    def get_random_floor_position(self):
        """Return a random walkable position (useful for placing player/monsters)"""
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.is_walkable(x, y):
                return (x, y)
            attempts += 1

        # Fallback: return center of first room
        if self.rooms:
            return self.rooms[0].center()
        return (self.width // 2, self.height // 2)