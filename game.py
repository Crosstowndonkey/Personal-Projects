from blessed import Terminal
from player import Player
from world import World
from monster import Monster
from floor_manager import FloorManager
from items import *  # Import all item classes


class Game:
    def __init__(self):
        self.terminal = Terminal()
        self.world = World(width=80, height=25)

        # Place player at a random floor position
        start_x, start_y = self.world.get_random_floor_position()
        self.player = Player(x=start_x, y=start_y)
        self.running = True

        # Message system
        self.messages = []
        self.max_messages = 5

        # Auto-explore system
        self.auto_exploring = False
        self.auto_target = None

        # Floor management
        self.floor_manager = FloorManager()

        # Give player starting equipment
        self.give_player_starting_equipment()

        # Add welcome message
        self.add_message("Welcome to ASCII RPG!")

    def show_inventory_message(self, message, duration=1.5):
        """Show a temporary message at the bottom of the inventory screen"""
        print(self.terminal.move_xy(2, self.terminal.height - 1) + message)
        self.terminal.inkey(timeout=duration)

    def add_message(self, message):
        """Add a message to the message log"""
        self.messages.append(message)
        # Keep only the most recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def draw_world(self):
        """Draw the game world with FOV"""
        # Clear screen
        print(self.terminal.home + self.terminal.clear)

        # Update field of view from player position
        self.world.update_fov(self.player.x, self.player.y, radius=8)

        # Draw the world tiles with visibility
        for y in range(self.world.height):
            for x in range(self.world.width):
                char = self.world.get_tile_display_char(x, y)
                print(self.terminal.move_xy(x, y) + char)

    def draw_player(self):
        """Draw the player character"""
        print(self.terminal.move_xy(self.player.x, self.player.y) + self.player.symbol)

    def draw_monsters(self):
        """Draw all visible monsters"""
        visible_monsters = self.world.get_monsters_in_fov()
        for monster in visible_monsters:
            print(self.terminal.move_xy(monster.x, monster.y) + monster.symbol)

    def draw_floor_items(self):
        """Draw all visible floor items"""
        visible_items = self.world.get_visible_floor_items()
        for floor_item in visible_items:
            print(self.terminal.move_xy(floor_item.x, floor_item.y) + floor_item.symbol)

    def draw_ui(self):
        """Draw the user interface (stats, instructions, etc.)"""
        ui_x = self.world.width + 2  # Start UI to the right of the game world

        print(self.terminal.move_xy(ui_x, 1) + "ASCII RPG")
        print(self.terminal.move_xy(ui_x, 3) + f"Level: {self.player.level}")
        print(self.terminal.move_xy(ui_x, 4) + f"HP: {self.player.current_hp}/{self.player.get_total_max_hp()}")
        print(self.terminal.move_xy(ui_x, 5) + f"Attack: {self.player.get_total_attack()}")
        print(self.terminal.move_xy(ui_x, 6) + f"Defense: {self.player.get_total_defense()}")
        print(self.terminal.move_xy(ui_x, 7) + f"Floor: {self.world.current_floor}")

        # Movement instructions
        print(self.terminal.move_xy(ui_x, 8) + "Movement (Numpad):")
        print(self.terminal.move_xy(ui_x, 9) + "7 8 9")
        print(self.terminal.move_xy(ui_x, 10) + "4 5 6")
        print(self.terminal.move_xy(ui_x, 11) + "1 2 3")
        print(self.terminal.move_xy(ui_x, 12) + "5: Wait")

        if self.auto_exploring:
            print(self.terminal.move_xy(ui_x, 13) + "0: Cancel auto-explore")
        else:
            print(self.terminal.move_xy(ui_x, 13) + "0: Auto-explore")

        print(self.terminal.move_xy(ui_x, 14) + "Door Actions:")
        print(self.terminal.move_xy(ui_x, 15) + "O: Open door")
        print(self.terminal.move_xy(ui_x, 16) + "K: Kick door")
        print(self.terminal.move_xy(ui_x, 17) + "C: Close door")

        print(self.terminal.move_xy(ui_x, 19) + "H: Use stairs")
        print(self.terminal.move_xy(ui_x, 20) + "I: Inventory")
        print(self.terminal.move_xy(ui_x, 21) + "P: Drink potion")
        print(self.terminal.move_xy(ui_x, 23) + "Q: Quit")

        # Show auto-explore status
        if self.auto_exploring:
            print(self.terminal.move_xy(ui_x, 23) + "AUTO-EXPLORING...")

    def handle_input(self):
        """Handle player input and return True if game should continue"""
        key = self.terminal.inkey()

        if key.lower() == 'q':
            self.running = False
            return False

        # Inventory screen
        elif key.lower() == 'i':
            self.stop_auto_explore()
            self.show_inventory_screen()
            self.handle_inventory_input()
            return True

        # Use/drink potion
        elif key.lower() == 'p':
            self.stop_auto_explore()
            message = self.try_use_potion()
            self.add_message(message)
            return True

        # Auto-explore command
        elif key == '0':  # Numpad 0
            if self.auto_exploring:
                # If already auto-exploring, stop it
                self.stop_auto_explore()
                self.add_message("Auto-explore cancelled.")
            else:
                # If not auto-exploring, start it
                self.start_auto_explore()
            return True

        # Door interaction commands
        elif key.lower() == 'o':  # Open door
            self.stop_auto_explore()  # Stop auto-explore on manual action
            message = self.get_direction_and_act('open')
            self.add_message(message)
            return True

        elif key.lower() == 'k':  # Kick door
            self.stop_auto_explore()
            message = self.get_direction_and_act('kick')
            self.add_message(message)
            return True

        elif key.lower() == 'c':  # Close door
            self.stop_auto_explore()
            message = self.get_direction_and_act('close')
            self.add_message(message)
            return True

        # Staircase interaction
        elif key.lower() == 'h':  # Use stairs
            self.stop_auto_explore()
            message = self.try_use_stairs()
            if message:
                self.add_message(message)
            return True

        # Handle movement with numpad (8-directional)
        movement_map = {
            '8': (0, -1),  # Up
            '2': (0, 1),  # Down
            '4': (-1, 0),  # Left
            '6': (1, 0),  # Right
            '5': (0, 0),  # Wait/pass turn
            # Diagonal movements
            '7': (-1, -1),  # Up-left
            '9': (1, -1),  # Up-right
            '1': (-1, 1),  # Down-left
            '3': (1, 1),  # Down-right
        }

        if key in movement_map:
            self.stop_auto_explore()  # Stop auto-explore on manual movement
            dx, dy = movement_map[key]
            if dx != 0 or dy != 0:  # If it's actual movement
                # Check if the new position is walkable
                new_x = self.player.x + dx
                new_y = self.player.y + dy
                # Check for monsters first
                monster = self.world.monster_at_position(new_x, new_y)
                if monster:
                    # Combat! Player attacks monster
                    message, monster_died = self.world.handle_combat(self.player, monster)
                    self.add_message(message)

                    if monster_died:
                        self.add_message(f"You killed the {monster.name}!")

                        # Try to drop loot before removing the monster
                        loot_message = self.world.drop_loot_from_monster(monster, self.world.current_floor)
                        if loot_message:
                            self.add_message(loot_message)

                        # Gain experience
                        exp_gained = monster.max_hp // 2  # Simple exp formula
                        self.player.gain_experience(exp_gained)

                        # Check for level up
                        if self.player.experience >= self.player.experience_to_next_level:
                            level_msg = self.player.level_up()
                            self.add_message(level_msg)

                        # Check if pocket kitten wants to help finish off enemies
                        kitten_message = self.check_kitten_scratch()
                        if kitten_message:
                            self.add_message(kitten_message)

                        # Remove dead monster and move into its space
                        self.world.remove_dead_monsters()
                        success = self.player.move(dx, dy, self.world.width, self.world.height)
                        # Handle heal over time when player moves
                        heal_message = self.player.take_step()
                        if heal_message:
                            self.add_message(heal_message)
                    # If monster survived, player doesn't move
                elif self.world.is_walkable(new_x, new_y):
                    success = self.player.move(dx, dy, self.world.width, self.world.height)

                    # Check for item pickup
                    floor_item = self.world.item_at_position(new_x, new_y)
                    if floor_item:
                        if self.player.add_item(floor_item.item):
                            self.world.pickup_item_at_position(new_x, new_y)
                            self.add_message(f"You pick up {floor_item.item.name}.")
                        else:
                            self.add_message(f"Your inventory is full! Can't pick up {floor_item.item.name}.")

                    # Handle heal over time when player moves
                    heal_message = self.player.take_step()
                    if heal_message:
                        self.add_message(heal_message)
                else:
                    # Get more specific feedback about what's blocking
                    tile = self.world.get_tile(new_x, new_y)
                    if tile and tile.tile_type == 'door_closed':
                        self.add_message("The door blocks your way.")
                    else:
                        self.add_message("You can't move there.")
            else:
                # Waiting/passing turn
                self.add_message("You wait.")

            # Update monster AI after any player action (including waiting)
            self.world.update_monster_ai(self.player.x, self.player.y)
            # Update monster AI and handle their attacks
            self.handle_monster_turn()
            return True

        return True  # Continue game for any other key

    def start_auto_explore(self):
        """Start auto-exploring toward the nearest unexplored area"""
        # Find nearest unexplored area
        target = self.world.find_nearest_unexplored(self.player.x, self.player.y)

        if target is None:
            self.add_message("No unexplored areas remaining.")
            self.auto_exploring = False
            return

        self.auto_exploring = True
        self.auto_target = target
        self.add_message("Auto-exploring...")

        # Take the first step
        self.continue_auto_explore()

    def continue_auto_explore(self):
        """Continue auto-exploring if active"""
        if not self.auto_exploring or self.auto_target is None:
            return

        target_x, target_y = self.auto_target

        # Check if we can see the target area now (exploration complete for this target)
        if (0 <= target_x < self.world.width and 0 <= target_y < self.world.height and
                self.world.tiles[target_y][target_x].explored):
            # This area is now explored, find a new target
            self.start_auto_explore()
            return

        # Find next step toward target
        next_step = self.world.find_path_to(self.player.x, self.player.y, target_x, target_y)

        if next_step is None:
            # Can't reach target, try to find a new one
            self.add_message("Path blocked, stopping auto-explore.")
            self.auto_exploring = False
            return

        dx, dy = next_step
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # Check if we can move there
        # Check for monsters first
        monster = self.world.monster_at_position(new_x, new_y)
        if monster:
            self.add_message(f"Monster spotted! Stopping auto-explore.")
            self.auto_exploring = False
        elif self.world.is_walkable(new_x, new_y):
            self.player.move(dx, dy, self.world.width, self.world.height)
            # Handle heal over time during auto-explore
            heal_message = self.player.take_step()
            if heal_message:
                self.add_message(heal_message)

            # Check if any monsters are visible after moving (FOV is updated in render)
            visible_monsters = self.world.get_monsters_in_fov()
            if visible_monsters:
                monster_names = [monster.name for monster in visible_monsters]
                if len(monster_names) == 1:
                    self.add_message(f"{monster_names[0]} spotted! Stopping auto-explore.")
                else:
                    self.add_message(f"Monsters spotted! Stopping auto-explore.")
                self.auto_exploring = False
                return

            # Update monster AI after auto-explore movement
            self.world.update_monster_ai(self.player.x, self.player.y)
        else:
            # Path is blocked (maybe door appeared, etc.)
            self.add_message("Path blocked, stopping auto-explore.")
            self.auto_exploring = False

    def stop_auto_explore(self, show_message=False):
        """Stop auto-exploring"""
        if self.auto_exploring:
            self.auto_exploring = False
            self.auto_target = None
            if show_message:
                self.add_message("Auto-explore stopped.")

    def handle_monster_turn(self):
        """Handle monster AI and attacks"""
        for monster in self.world.monsters:
            if not monster.is_alive():
                continue

            # Check if monster can see player
            if (0 <= monster.x < self.world.width and
                    0 <= monster.y < self.world.height and
                    self.world.tiles[monster.y][monster.x].visible):
                # Monster sees player
                monster.has_seen_player = True
                monster.target_x = self.player.x
                monster.target_y = self.player.y

            # Move or attack
            if monster.has_seen_player and monster.target_x is not None:
                result = self.world.move_monster_toward_target(monster, self.player.x, self.player.y)

                if result == "attack_player":
                    # Monster attacks player
                    message, player_died = self.world.handle_combat(monster, self.player)
                    self.add_message(message)

                    if player_died:
                        self.handle_player_death()
                    else:
                        # Check if pocket kitten wants to help after monster attacks
                        kitten_message = self.check_kitten_scratch()
                        if kitten_message:
                            self.add_message(kitten_message)

    def handle_player_death(self):
        """Handle player death and respawn"""
        self.add_message("You have died!")
        self.add_message("Respawning...")

        # Respawn player
        self.player.respawn()
        respawn_x, respawn_y = self.world.get_random_respawn_position()
        self.player.x = respawn_x
        self.player.y = respawn_y

        self.add_message(f"You respawn at a safe location.")
        # Reset all monster AI - they lose track of the player
        for monster in self.world.monsters:
            monster.has_seen_player = False
            monster.target_x = None
            monster.target_y = None

    def try_use_stairs(self):
        """Try to use stairs at current position"""
        staircase = self.world.get_staircase_at_position(self.player.x, self.player.y)

        if not staircase:
            return "There are no stairs here."

        if not staircase.visible:
            return "You can't see any stairs here."

        # Save current floor
        self.floor_manager.save_floor(self.world.current_floor, self.world)

        current_floor = self.world.current_floor

        # Force correct target floor calculation if it's wrong
        if staircase.direction == 'down':
            target_floor = current_floor + 1
            self.add_message(f"You descend to floor {target_floor}.")
        else:  # direction == 'up'
            target_floor = current_floor - 1
            self.add_message(f"You ascend to floor {target_floor}.")

        # Debug message
        self.add_message(f"Moving from floor {current_floor} to floor {target_floor}")

        # Load or generate target floor
        if self.floor_manager.has_floor(target_floor):
            self.load_existing_floor(target_floor, current_floor)
        else:
            self.generate_new_floor(target_floor, current_floor)

        return None

    def load_existing_floor(self, floor_number, came_from_floor):
        """Load a previously visited floor"""
        floor_data = self.floor_manager.load_floor(floor_number)

        # Create new world with saved data
        self.world = World(width=80, height=25)
        self.world.current_floor = floor_number
        self.world.tiles = floor_data['tiles']
        self.world.monsters = floor_data['monsters']
        self.world.rooms = floor_data['rooms']
        self.world.staircases = floor_data['staircases']

        # Place player at the correct staircase based on where they came from
        player_placed = False
        for x, y, direction, target in self.world.staircases:
            # If we came from below (lower floor number), place at up staircase
            # If we came from above (higher floor number), place at down staircase
            if ((came_from_floor < floor_number and direction == 'up') or
                    (came_from_floor > floor_number and direction == 'down')):
                self.player.x = x
                self.player.y = y
                player_placed = True
                break

        if not player_placed:
            # Fallback: place at random floor position
            start_x, start_y = self.world.get_random_floor_position()
            self.player.x = start_x
            self.player.y = start_y

    def generate_new_floor(self, floor_number, came_from_floor):
        """Generate a new floor"""
        # Create new world
        self.world = World(width=80, height=25)
        self.world.current_floor = floor_number

        # Place player at the correct staircase based on where they came from
        player_placed = False
        for x, y, direction, target in self.world.staircases:
            # If we came from below (lower floor), place at up staircase
            # If we came from above (higher floor), place at down staircase
            if ((came_from_floor < floor_number and direction == 'up') or
                    (came_from_floor > floor_number and direction == 'down')):
                self.player.x = x
                self.player.y = y
                player_placed = True
                break

        if not player_placed:
            # Fallback: place at random floor position
            start_x, start_y = self.world.get_random_floor_position()
            self.player.x = start_x
            self.player.y = start_y

    def get_direction_and_act(self, action):
        """Get direction from player and perform door action"""
        # For now, we'll check all adjacent tiles for doors
        # Later we can make this more sophisticated with direction input

        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),  # Cardinal directions
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # Diagonals
        ]

        door_positions = []

        # Find all adjacent doors that are visible
        for dx, dy in directions:
            check_x = self.player.x + dx
            check_y = self.player.y + dy

            tile = self.world.get_tile(check_x, check_y)
            if (tile and tile.tile_type.startswith('door') and
                    tile.visible):  # Only interact with visible doors
                door_positions.append((check_x, check_y))

        if not door_positions:
            return f"No visible doors nearby to {action}."

        # If only one door, act on it
        if len(door_positions) == 1:
            x, y = door_positions[0]
            if action == 'open':
                success, message = self.world.try_open_door(x, y)
            elif action == 'kick':
                success, message = self.world.try_kick_door(x, y)
            elif action == 'close':
                success, message = self.world.try_close_door(x, y)
            return message

        # Multiple doors - for now, just act on the first one
        # Later we can add direction selection
        x, y = door_positions[0]
        if action == 'open':
            success, message = self.world.try_open_door(x, y)
        elif action == 'kick':
            success, message = self.world.try_kick_door(x, y)
        elif action == 'close':
            success, message = self.world.try_close_door(x, y)
        return message

    def draw_messages_at_bottom(self):
        """Draw messages at the bottom of the screen as a backup"""
        # Draw messages below the map
        msg_y = self.world.height + 1

        # Clear the message area first (write spaces to overwrite old text)
        for i in range(3):  # Clear 3 lines for messages
            print(self.terminal.move_xy(0, msg_y + i) + " " * 80)  # Clear 80 characters

        # Show recent messages on separate lines
        if self.messages:
            print(self.terminal.move_xy(0, msg_y) + "Messages:")

            # Show last few messages on individual lines
            recent_messages = self.messages[-3:]  # Last 3 messages
            for i, message in enumerate(recent_messages):
                # Truncate long messages to fit screen
                display_message = message[:75] + "..." if len(message) > 75 else message
                print(self.terminal.move_xy(0, msg_y + 1 + i) + f"  {display_message}")
        else:
            print(self.terminal.move_xy(0, msg_y) + "Messages: (none yet)")

    def render(self):
        """Draw everything on screen"""
        self.draw_world()
        self.draw_floor_items()  # Add this line
        self.draw_player()
        self.draw_monsters()
        self.draw_ui()
        self.draw_messages_at_bottom()

    def show_inventory_screen(self):
        """Display the interactive inventory and equipment screen"""
        # Clear screen
        print(self.terminal.home + self.terminal.clear)

        # Title
        print(self.terminal.move_xy(2, 1) + "=== INTERACTIVE INVENTORY & EQUIPMENT ===")

        # Player stats with equipment bonuses
        stats_y = 3
        print(self.terminal.move_xy(2, stats_y) + f"Level: {self.player.level}")
        print(self.terminal.move_xy(2, stats_y + 1) + f"HP: {self.player.current_hp}/{self.player.get_total_max_hp()}")
        print(self.terminal.move_xy(2,
                                    stats_y + 2) + f"Attack: {self.player.get_total_attack()} (Base: {self.player.attack})")
        print(self.terminal.move_xy(2,
                                    stats_y + 3) + f"Defense: {self.player.get_total_defense()} (Base: {self.player.defense})")

        # Equipment section
        equip_y = stats_y + 5
        print(self.terminal.move_xy(2, equip_y) + "=== EQUIPPED ===")

        equipment_summary = self.player.get_equipment_summary()
        for i, line in enumerate(equipment_summary):
            print(self.terminal.move_xy(2, equip_y + 1 + i) + line)

        # Inventory section with numbered items
        inv_y = equip_y + 5
        print(self.terminal.move_xy(2,
                                    inv_y) + f"=== INVENTORY ({self.player.get_inventory_count()}/{self.player.max_inventory_size}) ===")

        if not self.player.inventory:
            print(self.terminal.move_xy(2, inv_y + 1) + "Empty")
            self.current_inventory_items = []  # Store for input handling
        else:
            # Create numbered list of all items
            self.current_inventory_items = []  # Store items with their numbers
            current_y = inv_y + 1
            item_number = 1

            # Group items by type for better display
            from items import SpecialItem
            weapons = [item for item in self.player.inventory if isinstance(item, Weapon)]
            armor = [item for item in self.player.inventory if isinstance(item, Armor)]
            accessories = [item for item in self.player.inventory if isinstance(item, Accessory)]
            consumables = [item for item in self.player.inventory if isinstance(item, Consumable)]
            special_items = [item for item in self.player.inventory if isinstance(item, SpecialItem)]

            if weapons:
                print(self.terminal.move_xy(4, current_y) + "Weapons:")
                current_y += 1
                for weapon in weapons:
                    equipped_marker = " (equipped)" if weapon.equipped else ""
                    print(self.terminal.move_xy(6,
                                                current_y) + f"{item_number}) {weapon.symbol} {weapon.name}{equipped_marker}")
                    print(self.terminal.move_xy(8, current_y + 1) + f"   {weapon.get_stats_description()}")
                    self.current_inventory_items.append((item_number, weapon))
                    item_number += 1
                    current_y += 2

            if armor:
                print(self.terminal.move_xy(4, current_y) + "Armor:")
                current_y += 1
                for armor_piece in armor:
                    equipped_marker = " (equipped)" if armor_piece.equipped else ""
                    print(self.terminal.move_xy(6,
                                                current_y) + f"{item_number}) {armor_piece.symbol} {armor_piece.name}{equipped_marker}")
                    print(self.terminal.move_xy(8, current_y + 1) + f"   {armor_piece.get_stats_description()}")
                    self.current_inventory_items.append((item_number, armor_piece))
                    item_number += 1
                    current_y += 2

            if accessories:
                print(self.terminal.move_xy(4, current_y) + "Accessories:")
                current_y += 1
                for accessory in accessories:
                    equipped_marker = " (equipped)" if accessory.equipped else ""
                    print(self.terminal.move_xy(6,
                                                current_y) + f"{item_number}) {accessory.symbol} {accessory.name}{equipped_marker}")
                    print(self.terminal.move_xy(8, current_y + 1) + f"   {accessory.get_stats_description()}")
                    self.current_inventory_items.append((item_number, accessory))
                    item_number += 1
                    current_y += 2

            if consumables:
                print(self.terminal.move_xy(4, current_y) + "Consumables:")
                current_y += 1
                for consumable in consumables:
                    print(self.terminal.move_xy(6, current_y) + f"{item_number}) {consumable.symbol} {consumable.name}")
                    self.current_inventory_items.append((item_number, consumable))
                    item_number += 1
                    current_y += 1

            if special_items:
                print(self.terminal.move_xy(4, current_y) + "Special Items:")
                current_y += 1
                for special_item in special_items:
                    print(self.terminal.move_xy(6,
                                                current_y) + f"{item_number}) {special_item.symbol} {special_item.name}")
                    print(self.terminal.move_xy(8, current_y + 1) + f"   {special_item.description}")
                    self.current_inventory_items.append((item_number, special_item))
                    item_number += 1
                    current_y += 2

        # Instructions
        instructions_y = self.terminal.height - 6
        print(self.terminal.move_xy(2, instructions_y) + "ACTIONS:")
        print(self.terminal.move_xy(2, instructions_y + 1) + "1-9: Select item to equip/use")
        print(self.terminal.move_xy(2, instructions_y + 2) + "U: Unequip (W)eapon/(A)rmor/A(c)cessory")
        print(self.terminal.move_xy(2, instructions_y + 3) + "D: Drop selected item")
        print(self.terminal.move_xy(2, instructions_y + 4) + "C: Compare equipment")
        print(self.terminal.move_xy(2, instructions_y + 5) + "ESC/I: Return to game")

    def handle_inventory_input(self):
        """Handle input while in inventory screen - loops until player exits"""
        while True:
            key = self.terminal.inkey()

            # Exit inventory
            if key.lower() == 'i' or key.name == 'KEY_ESCAPE':
                return  # Return to main game

            # Handle item selection (1-9)
            elif key.isdigit() and key != '0':
                item_num = int(key)
                if hasattr(self, 'current_inventory_items') and self.current_inventory_items:
                    # Find the item with this number
                    selected_item = None
                    for num, item in self.current_inventory_items:
                        if num == item_num:
                            selected_item = item
                            break

                    if selected_item:
                        message = self.handle_item_action(selected_item)
                        self.add_message(message)
                        # Refresh the inventory screen
                        self.show_inventory_screen()
                    else:
                        # Show error message briefly
                        print(
                            self.terminal.move_xy(2, self.terminal.height - 1) + f"No item #{item_num} - Press any key")
                        self.terminal.inkey()  # Wait for keypress
                        self.show_inventory_screen()  # Refresh screen

            # Handle unequip
            elif key.lower() == 'u':
                self.handle_unequip_menu()
                self.show_inventory_screen()  # Refresh after unequip

            # Handle item dropping (placeholder for now)
            elif key.lower() == 'd':
                print(self.terminal.move_xy(2, self.terminal.height - 1) + "Drop feature coming soon! - Press any key")
                self.terminal.inkey()  # Wait for keypress
                self.show_inventory_screen()  # Refresh screen

            # Handle equipment comparison (placeholder for now)
            elif key.lower() == 'c':
                print(
                    self.terminal.move_xy(2, self.terminal.height - 1) + "Compare feature coming soon! - Press any key")
                self.terminal.inkey()  # Wait for keypress
                self.show_inventory_screen()  # Refresh screen

            # Any other key - show help
            else:
                print(self.terminal.move_xy(2,
                                            self.terminal.height - 1) + "Invalid key! Use 1-9 to select items, I/ESC to exit - Press any key")
                self.terminal.inkey()  # Wait for keypress
                self.show_inventory_screen()  # Refresh screen

    def handle_item_action(self, item):
        """Handle the primary action for an item (equip equipment, use consumables)"""
        from items import Equipment, Consumable, SpecialItem

        if isinstance(item, Equipment):
            if item.equipped:
                # Item is already equipped, unequip it
                if isinstance(item, Weapon):
                    success, message = self.player.unequip_item("weapon")
                elif isinstance(item, Armor):
                    success, message = self.player.unequip_item("armor")
                elif isinstance(item, Accessory):
                    success, message = self.player.unequip_item("accessory")
                return message
            else:
                # Equip the item
                success, message = self.player.equip_item(item)
                return message

        elif isinstance(item, Consumable):
            # Use the consumable
            success, message = self.player.use_item(item)
            return message

        elif isinstance(item, SpecialItem):
            # Special items can't be used directly
            return f"The {item.name} is a special item and can't be used directly."

        else:
            return f"You can't use the {item.name}."

    def handle_unequip_menu(self):
        """Handle the unequip submenu"""
        # Show unequip options
        menu_y = self.terminal.height - 8
        print(self.terminal.move_xy(2, menu_y) + "UNEQUIP:")
        print(self.terminal.move_xy(2, menu_y + 1) + "W: Unequip weapon")
        print(self.terminal.move_xy(2, menu_y + 2) + "A: Unequip armor")
        print(self.terminal.move_xy(2, menu_y + 3) + "C: Unequip accessory")
        print(self.terminal.move_xy(2, menu_y + 4) + "ESC: Cancel")

        while True:
            key = self.terminal.inkey()

            if key.name == 'KEY_ESCAPE':
                return
            elif key.lower() == 'w':
                success, message = self.player.unequip_item("weapon")
                self.add_message(message)
                return
            elif key.lower() == 'a':
                success, message = self.player.unequip_item("armor")
                self.add_message(message)
                return
            elif key.lower() == 'c':
                success, message = self.player.unequip_item("accessory")
                self.add_message(message)
                return

    def try_use_potion(self):
        """Try to use the first healing potion in inventory"""
        # Look for the first healing potion in inventory
        potion = None
        for item in self.player.inventory:
            if isinstance(item, HealthPotion):
                potion = item
                break

        if not potion:
            return "You don't have any healing potions."

        # Check if player needs healing
        if self.player.current_hp >= self.player.get_total_max_hp():
            return "You're already at full health."

        # Use the potion
        success, message = self.player.use_item(potion)
        return message

    def handle_inventory_input(self):
        """Handle input while in inventory screen"""
        key = self.terminal.inkey()
        # For now, any key closes inventory - we'll add more functionality later
        return False  # Return to main game

    def give_player_starting_equipment(self):
        """Give the player some basic starting equipment"""
        from items import create_rusty_dagger, create_minor_health_potion, create_pocket_kitten

        # Give starting weapon
        starting_weapon = create_rusty_dagger()
        if self.player.add_item(starting_weapon):
            success, message = self.player.equip_item(starting_weapon)
            if success:
                self.add_message("You start with a rusty dagger equipped.")

        # Give starting potion
        starting_potion = create_minor_health_potion()
        if self.player.add_item(starting_potion):
            self.add_message("You start with a minor health potion.")

        # Give pocket kitten
        pocket_kitten = create_pocket_kitten()
        if self.player.add_item(pocket_kitten):
            self.add_message("A tiny kitten climbs into your pocket! *purr*")

    def check_kitten_scratch(self):
        """Check if player has pocket kitten and if it wants to scratch"""
        from items import PocketKitten

        # Look for pocket kitten in inventory
        pocket_kitten = None
        for item in self.player.inventory:
            if isinstance(item, PocketKitten):
                pocket_kitten = item
                break

        if not pocket_kitten:
            return None  # No kitten, no scratches

        # Let kitten try to scratch
        scratch_message = pocket_kitten.try_scratch_nearby_monster(self.player, self.world)

        # If kitten killed a monster, clean up
        if scratch_message and "collapses!" in scratch_message:
            self.world.remove_dead_monsters()

        return scratch_message

    def run(self):
        """Main game loop"""
        with self.terminal.cbreak(), self.terminal.hidden_cursor():
            while self.running:
                self.render()

                # If auto-exploring, check for cancellation input first
                if self.auto_exploring:
                    # Check if there's input available (non-blocking)
                    key = self.terminal.inkey(timeout=0.1)  # 0.1 second timeout
                    if key == '0':
                        self.stop_auto_explore()
                        self.add_message("Auto-explore cancelled.")
                    elif key and key != '':  # Any other key stops auto-explore
                        self.stop_auto_explore()
                        # Process the key normally
                        if key.lower() == 'q':
                            self.running = False
                            break
                        # For other keys, just stop auto-explore
                    else:
                        # No input, continue auto-exploring
                        self.continue_auto_explore()
                else:
                    # Normal input handling
                    self.handle_input()

        # Game ended
        print(self.terminal.clear + "Thanks for playing!")