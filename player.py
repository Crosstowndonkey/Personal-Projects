from items import Item, Equipment, Weapon, Armor, Accessory, Consumable, HealthPotion

class Player:
    def __init__(self, x=10, y=10):
        # Position
        self.x = x
        self.y = y

        # Basic stats (we'll expand these later)
        self.max_hp = 100
        self.current_hp = 100
        self.level = 1
        # Combat stats
        self.attack = 5
        self.defense = 2
        self.experience = 0
        self.experience_to_next_level = 20

        # Display character
        self.symbol = '@'
        # Heal over time system
        self.steps_taken = 0  # Track how many steps player has taken
        self.steps_until_heal = self.get_random_heal_interval()  # When next heal happens

        # Inventory and equipment system
        self.inventory = []  # List to hold all items
        self.max_inventory_size = 20  # Maximum items player can carry

        # Equipment slots
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_accessory = None

    def move(self, dx, dy, world_width=20, world_height=20):
        """
        Move the player by dx, dy if the move is valid
        dx, dy: change in x and y coordinates
        Returns True if move was successful, False if blocked
        """
        new_x = self.x + dx
        new_y = self.y + dy

        # Check boundaries (later we'll check for walls too)
        if 1 <= new_x < world_width - 1 and 1 <= new_y < world_height - 1:
            self.x = new_x
            self.y = new_y
            return True
        return False

    def get_position(self):
        """Return player's current position as a tuple"""
        return (self.x, self.y)

    def get_hp_percentage(self):
        """Return health as a percentage for display"""
        return (self.current_hp / self.max_hp) * 100

    def take_damage(self, damage):
        """Reduce player health by damage amount"""
        self.current_hp = max(0, self.current_hp - damage)
        return self.current_hp <= 0  # Return True if player died

    def heal(self, amount):
        """Restore health, but don't exceed maximum"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def get_attack_damage(self):
        """Calculate damage for player's attack using total attack"""
        import random
        base_damage = self.get_total_attack()  # Use total attack instead of just self.attack
        variance = random.randint(-1, 2)  # -1 to +2 damage variance
        return max(1, base_damage + variance)

    def gain_experience(self, amount):
        """Gain experience and possibly level up"""
        self.experience += amount
        if self.experience >= self.experience_to_next_level:
            self.level_up()

    def level_up(self):
        """Level up the player"""
        self.experience -= self.experience_to_next_level
        self.level += 1

        # Increase stats
        old_max_hp = self.max_hp
        self.max_hp += 10
        self.current_hp += 10 # Heal on level up
        self.attack += 1
        self.defense += 1

        # Increase experience needed for max level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)

        return f"Level up! You are now level {self.level}. HP: {old_max_hp}->{self.max_hp}"

    def respawn(self):
        """Reset player after death"""
        self.current_hp = self.max_hp
        # Keep stats but lose some experience
        self.experience = max(0, self.experience - 10)

    def get_random_heal_interval(self):
        """Get a random number of steps until next heal (2-4 steps)"""
        import random
        return random.randint(2, 4)

    def get_random_heal_amount(self):
        """Get a random heal amount (1-3% of max health)"""
        import random
        heal_percentage = random.randint(1, 3)  # 1-3%
        heal_amount = int(self.max_hp * (heal_percentage / 100.0))
        return max(1, heal_amount)  # Always heal at least 1 HP

    def take_step(self):
        """Call this when player takes a step. Returns heal message if healing occurred."""
        self.steps_taken += 1
        self.steps_until_heal -= 1

        # Check if it's time to heal
        if self.steps_until_heal <= 0:
            return self.try_heal_over_time()

        return None  # No healing this step

    def try_heal_over_time(self):
        """Try to heal the player over time. Returns message if healing occurred."""
        # Only heal if player is injured
        if self.current_hp < self.max_hp:
            heal_amount = self.get_random_heal_amount()
            old_hp = self.current_hp
            self.heal(heal_amount)

            # Reset the counter for next heal
            self.steps_until_heal = self.get_random_heal_interval()

            return f"You feel slightly better. (+{heal_amount} HP: {old_hp}->{self.current_hp})"
        else:
            # Player is at full health, reset counter but don't heal
            self.steps_until_heal = self.get_random_heal_interval()
            return None

    def add_item(self, item):
        """Add item to inventory if there's space. Returns True if successful."""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False  # Inventory full

    def remove_item(self, item):
        """Remove item from inventory if it exists. Returns True if successful."""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def has_item(self, item):
        """Check if player has this item in inventory"""
        return item in self.inventory

    def get_inventory_count(self):
        """Get current number of items in inventory"""
        return len(self.inventory)

    def is_inventory_full(self):
        """Check if inventory is at capacity"""
        return len(self.inventory) >= self.max_inventory_size

    def equip_item(self, item):
        """Equip an item if possible. Returns (success, message)"""
        if not isinstance(item, Equipment):
            return (False, f"You can't equip {item.name}.")

        if item not in self.inventory:
            return (False, f"You don't have {item.name} in your inventory.")

        # Handle different equipment types
        if isinstance(item, Weapon):
            return self.equip_weapon(item)
        elif isinstance(item, Armor):
            return self.equip_armor(item)
        elif isinstance(item, Accessory):
            return self.equip_accessory(item)

        return (False, f"Can't equip {item.name}.")

    def equip_weapon(self, weapon):
        """Equip a weapon, unequipping current weapon if any"""
        # Unequip current weapon if equipped
        if self.equipped_weapon:
            self.equipped_weapon.equipped = False
            old_weapon_name = self.equipped_weapon.name
        else:
            old_weapon_name = None

        # Equip new weapon
        self.equipped_weapon = weapon
        weapon.equipped = True

        if old_weapon_name:
            return (True, f"You unequip {old_weapon_name} and equip {weapon.name}.")
        else:
            return (True, f"You equip {weapon.name}.")

    def equip_armor(self, armor):
        """Equip armor, unequipping current armor if any"""
        # Unequip current armor if equipped
        if self.equipped_armor:
            self.equipped_armor.equipped = False
            old_armor_name = self.equipped_armor.name
        else:
            old_armor_name = None

        # Equip new armor
        self.equipped_armor = armor
        armor.equipped = True

        if old_armor_name:
            return (True, f"You unequip {old_armor_name} and equip {armor.name}.")
        else:
            return (True, f"You equip {armor.name}.")

    def equip_accessory(self, accessory):
        """Equip accessory, unequipping current accessory if any"""
        # Unequip current accessory if equipped
        if self.equipped_accessory:
            self.equipped_accessory.equipped = False
            old_accessory_name = self.equipped_accessory.name
        else:
            old_accessory_name = None

        # Equip new accessory
        self.equipped_accessory = accessory
        accessory.equipped = True

        if old_accessory_name:
            return (True, f"You unequip {old_accessory_name} and equip {accessory.name}.")
        else:
            return (True, f"You equip {accessory.name}.")

    def unequip_item(self, slot):
        """Unequip item from specified slot. Returns (success, message)"""
        if slot == "weapon" and self.equipped_weapon:
            weapon_name = self.equipped_weapon.name
            self.equipped_weapon.equipped = False
            self.equipped_weapon = None
            return (True, f"You unequip {weapon_name}.")
        elif slot == "armor" and self.equipped_armor:
            armor_name = self.equipped_armor.name
            self.equipped_armor.equipped = False
            self.equipped_armor = None
            return (True, f"You unequip {armor_name}.")
        elif slot == "accessory" and self.equipped_accessory:
            accessory_name = self.equipped_accessory.name
            self.equipped_accessory.equipped = False
            self.equipped_accessory = None
            return (True, f"You unequip {accessory_name}.")
        else:
            return (False, f"No {slot} equipped.")

    def use_item(self, item):
        """Use a consumable item. Returns (success, message)"""
        if not isinstance(item, Consumable):
            return (False, f"You can't use {item.name}.")

        if item not in self.inventory:
            return (False, f"You don't have {item.name} in your inventory.")

        # Use the item
        message = item.use(self)

        # Remove used consumable from inventory
        self.remove_item(item)

        return (True, message)

    def get_total_attack(self):
        """Calculate total attack including equipment bonuses"""
        total_attack = self.attack

        if self.equipped_weapon:
            total_attack += self.equipped_weapon.attack_bonus

        if self.equipped_accessory and hasattr(self.equipped_accessory, 'attack_bonus'):
            total_attack += self.equipped_accessory.attack_bonus

        return total_attack

    def get_total_defense(self):
        """Calculate total defense including equipment bonuses"""
        total_defense = self.defense

        if self.equipped_armor:
            total_defense += self.equipped_armor.defense_bonus

        if self.equipped_accessory and hasattr(self.equipped_accessory, 'defense_bonus'):
            total_defense += self.equipped_accessory.defense_bonus

        return total_defense

    def get_total_max_hp(self):
        """Calculate total max HP including equipment bonuses"""
        total_max_hp = self.max_hp

        if self.equipped_accessory and hasattr(self.equipped_accessory, 'hp_bonus'):
            total_max_hp += self.equipped_accessory.hp_bonus

        return total_max_hp

    def get_equipment_summary(self):
        """Get a summary of currently equipped items"""
        summary = []

        if self.equipped_weapon:
            summary.append(f"Weapon: {self.equipped_weapon.name}")
        else:
            summary.append("Weapon: None")

        if self.equipped_armor:
            summary.append(f"Armor: {self.equipped_armor.name}")
        else:
            summary.append("Armor: None")

        if self.equipped_accessory:
            summary.append(f"Accessory: {self.equipped_accessory.name}")
        else:
            summary.append("Accessory: None")

        return summary