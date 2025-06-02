"""
Item and equipment system for ASCII RPG
Contains all item types, equipment, and creation functions
"""

import random


# =============================================================================
# BASE CLASSES
# =============================================================================

class Item:
    """Base class for all items in the game"""

    def __init__(self, name, symbol='?', description="An item", value=0):
        self.name = name
        self.symbol = symbol
        self.description = description
        self.value = value  # For future trading/selling

    def __str__(self):
        """String representation of the item"""
        return self.name

    def get_info(self):
        """Get detailed information about the item"""
        return f"{self.name}: {self.description}"


class Equipment(Item):
    """Base class for all equippable items"""

    def __init__(self, name, symbol, description, slot, value=0):
        super().__init__(name, symbol, description, value)
        self.slot = slot  # 'weapon', 'armor', 'accessory'
        self.equipped = False  # Is this currently equipped?

    def get_stats_description(self):
        """Override in subclasses to show stat bonuses"""
        return "No special properties"


# =============================================================================
# EQUIPMENT CLASSES
# =============================================================================

class Weapon(Equipment):
    """Weapons that increase attack power"""

    def __init__(self, name, attack_bonus, symbol=')', description="A weapon", value=0, weapon_type="melee"):
        super().__init__(name, symbol, description, "weapon", value)
        self.attack_bonus = attack_bonus
        self.weapon_type = weapon_type  # 'melee', 'ranged', 'magic' for future use

    def get_stats_description(self):
        """Show weapon's attack bonus"""
        return f"Attack: +{self.attack_bonus}"

    def get_info(self):
        """Get detailed weapon information"""
        return f"{self.name}: {self.description} ({self.get_stats_description()})"


class Armor(Equipment):
    """Armor that increases defense"""

    def __init__(self, name, defense_bonus, symbol='[', description="Armor", value=0, armor_type="light"):
        super().__init__(name, symbol, description, "armor", value)
        self.defense_bonus = defense_bonus
        self.armor_type = armor_type  # 'light', 'medium', 'heavy' for future use

    def get_stats_description(self):
        """Show armor's defense bonus"""
        return f"Defense: +{self.defense_bonus}"

    def get_info(self):
        """Get detailed armor information"""
        return f"{self.name}: {self.description} ({self.get_stats_description()})"


class Accessory(Equipment):
    """Accessories that provide various bonuses"""

    def __init__(self, name, symbol='=', description="An accessory", value=0,
                 hp_bonus=0, attack_bonus=0, defense_bonus=0):
        super().__init__(name, symbol, description, "accessory", value)
        self.hp_bonus = hp_bonus
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus

    def get_stats_description(self):
        """Show accessory's bonuses"""
        bonuses = []
        if self.hp_bonus > 0:
            bonuses.append(f"HP: +{self.hp_bonus}")
        if self.attack_bonus > 0:
            bonuses.append(f"Attack: +{self.attack_bonus}")
        if self.defense_bonus > 0:
            bonuses.append(f"Defense: +{self.defense_bonus}")

        return ", ".join(bonuses) if bonuses else "No special properties"

    def get_info(self):
        """Get detailed accessory information"""
        return f"{self.name}: {self.description} ({self.get_stats_description()})"


class SpecialItem(Item):
    """Base class for special/unique items with custom behaviors"""

    def __init__(self, name, symbol, description, value=0):
        super().__init__(name, symbol, description, value)
        self.special = True  # Mark this as a special item


class PocketKitten(SpecialItem):
    """A special companion that occasionally helps in combat"""

    def __init__(self):
        super().__init__(
            name="Pocket Kitten",
            symbol="c",  # 'c' for cat
            description="A tiny, adorable kitten that fits in your pocket. Sometimes helps in fights!",
            value=0  # Priceless!
        )
        self.scratch_chance = 0.15  # 15% chance to scratch per combat round
        self.scratch_damage = 2  # Damage when kitten scratches

    def try_scratch_nearby_monster(self, player, world):
        """Try to scratch a monster adjacent to the player. Returns message if scratch happens."""
        import random

        # Check if kitten decides to help
        if random.random() > self.scratch_chance:
            return None  # Kitten is napping

        # Find adjacent monsters
        adjacent_monsters = []
        directions = [
            (-1, -1), (0, -1), (1, -1),  # Top row
            (-1, 0), (1, 0),  # Middle row (skip center - that's the player)
            (-1, 1), (0, 1), (1, 1)  # Bottom row
        ]

        for dx, dy in directions:
            check_x = player.x + dx
            check_y = player.y + dy
            monster = world.monster_at_position(check_x, check_y)
            if monster and monster.is_alive():
                adjacent_monsters.append(monster)

        if not adjacent_monsters:
            return None  # No monsters to scratch

        # Pick a random adjacent monster to scratch
        target_monster = random.choice(adjacent_monsters)

        # Apply scratch damage
        monster_died = target_monster.take_damage(self.scratch_damage)

        # Create fun message
        scratch_messages = [
            f"Your pocket kitten pounces and scratches the {target_monster.name}!",
            f"*Hiss!* Your kitten claws at the {target_monster.name}!",
            f"Your pocket kitten bravely attacks the {target_monster.name}!",
            f"*Scratch scratch!* Your kitten helps fight the {target_monster.name}!",
            f"Your fearless pocket kitten strikes the {target_monster.name}!"
        ]

        message = random.choice(scratch_messages)
        message += f" ({self.scratch_damage} damage)"

        if monster_died:
            message += f" The {target_monster.name} collapses!"

        return message

    def get_info(self):
        """Get detailed kitten information"""
        return f"{self.name}: {self.description} (Occasionally scratches enemies for {self.scratch_damage} damage)"

# =============================================================================
# CONSUMABLE CLASSES
# =============================================================================

class Consumable(Item):
    """Base class for consumable items"""

    def __init__(self, name, symbol, description, value=0):
        super().__init__(name, symbol, description, value)
        self.consumable = True

    def use(self, target):
        """Use the consumable item. Override in subclasses."""
        return "Nothing happens."


class HealthPotion(Consumable):
    """Potion that restores health"""

    def __init__(self, name="Health Potion", heal_amount=25, symbol='!',
                 description="Restores health when consumed", value=10):
        super().__init__(name, symbol, description, value)
        self.heal_amount = heal_amount

    def use(self, target):
        """Use the health potion on a target (usually the player)"""
        if hasattr(target, 'heal'):
            old_hp = target.current_hp
            target.heal(self.heal_amount)
            actual_healing = target.current_hp - old_hp

            if actual_healing > 0:
                return f"You drink the {self.name} and recover {actual_healing} health!"
            else:
                return f"You drink the {self.name} but you're already at full health."
        else:
            return f"The {self.name} has no effect."

    def get_info(self):
        """Get detailed potion information"""
        return f"{self.name}: {self.description} (Heals {self.heal_amount} HP)"

# =============================================================================
# SPECIAL ITEM FACTORY FUNCTIONS
# =============================================================================

def create_pocket_kitten():
    """Create the unique pocket kitten companion"""
    return PocketKitten()

# =============================================================================
# WEAPON FACTORY FUNCTIONS
# =============================================================================

def create_rusty_dagger():
    """Create a basic starting weapon"""
    return Weapon(
        name="Rusty Dagger",
        attack_bonus=1,
        symbol=')',
        description="A small, rusty blade. Better than nothing.",
        value=5
    )

def create_short_sword():
    """Create a common sword"""
    return Weapon(
        name="Short Sword",
        attack_bonus=3,
        symbol=')',
        description="A well-balanced blade favored by adventurers.",
        value=25
    )

def create_iron_sword():
    """Create a decent iron sword"""
    return Weapon(
        name="Iron Sword",
        attack_bonus=5,
        symbol=')',
        description="A sturdy iron blade with a keen edge.",
        value=50
    )

def create_battle_axe():
    """Create a powerful but heavy axe"""
    return Weapon(
        name="Battle Axe",
        attack_bonus=7,
        symbol=')',
        description="A heavy axe that cleaves through enemies.",
        value=80
    )


# =============================================================================
# ARMOR FACTORY FUNCTIONS
# =============================================================================

def create_leather_armor():
    """Create basic leather armor"""
    return Armor(
        name="Leather Armor",
        defense_bonus=2,
        symbol='[',
        description="Simple leather protection for the torso.",
        value=20
    )

def create_chain_mail():
    """Create chain mail armor"""
    return Armor(
        name="Chain Mail",
        defense_bonus=4,
        symbol='[',
        description="Interlocked metal rings provide good protection.",
        value=60
    )

def create_plate_armor():
    """Create heavy plate armor"""
    return Armor(
        name="Plate Armor",
        defense_bonus=6,
        symbol='[',
        description="Heavy metal plates offer excellent protection.",
        value=150
    )


# =============================================================================
# ACCESSORY FACTORY FUNCTIONS
# =============================================================================

def create_health_ring():
    """Create a ring that boosts health"""
    return Accessory(
        name="Ring of Vitality",
        symbol='=',
        description="A ring that makes you feel more robust.",
        value=30,
        hp_bonus=15
    )

def create_power_amulet():
    """Create an amulet that boosts attack"""
    return Accessory(
        name="Amulet of Strength",
        symbol='=',
        description="An amulet that enhances your physical power.",
        value=40,
        attack_bonus=2
    )

def create_protection_bracelet():
    """Create a bracelet that boosts defense"""
    return Accessory(
        name="Bracelet of Protection",
        symbol='=',
        description="A bracelet that deflects some incoming damage.",
        value=35,
        defense_bonus=2
    )


# =============================================================================
# CONSUMABLE FACTORY FUNCTIONS
# =============================================================================

def create_minor_health_potion():
    """Create a small healing potion"""
    return HealthPotion(
        name="Minor Health Potion",
        heal_amount=15,
        description="A small vial of healing liquid.",
        value=8
    )

def create_health_potion():
    """Create a standard healing potion"""
    return HealthPotion(
        name="Health Potion",
        heal_amount=25,
        description="A bottle of red healing liquid.",
        value=15
    )

def create_greater_health_potion():
    """Create a powerful healing potion"""
    return HealthPotion(
        name="Greater Health Potion",
        heal_amount=50,
        description="A large bottle of potent healing elixir.",
        value=30
    )


# =============================================================================
# RANDOM ITEM GENERATION
# =============================================================================

def get_random_weapon():
    """Get a random weapon based on rarity"""
    roll = random.randint(1, 100)

    if roll <= 40:  # 40% chance - common
        return random.choice([create_rusty_dagger(), create_short_sword()])
    elif roll <= 75:  # 35% chance - uncommon
        return create_iron_sword()
    else:  # 25% chance - rare
        return create_battle_axe()

def get_random_armor():
    """Get a random armor piece based on rarity"""
    roll = random.randint(1, 100)

    if roll <= 50:  # 50% chance - common
        return create_leather_armor()
    elif roll <= 80:  # 30% chance - uncommon
        return create_chain_mail()
    else:  # 20% chance - rare
        return create_plate_armor()

def get_random_accessory():
    """Get a random accessory"""
    accessories = [create_health_ring(), create_power_amulet(), create_protection_bracelet()]
    return random.choice(accessories)

def get_random_potion():
    """Get a random healing potion"""
    roll = random.randint(1, 100)

    if roll <= 60:  # 60% chance - minor
        return create_minor_health_potion()
    elif roll <= 90:  # 30% chance - standard
        return create_health_potion()
    else:  # 10% chance - greater
        return create_greater_health_potion()


def get_random_item():
    """Get a completely random item of any type"""
    # Very small chance for special items in random generation
    roll = random.randint(1, 1000)
    if roll == 1:  # 0.1% chance for pocket kitten
        return create_pocket_kitten()

    # Normal item types
    item_types = ['weapon', 'armor', 'accessory', 'potion']
    item_type = random.choice(item_types)

    if item_type == 'weapon':
        return get_random_weapon()
    elif item_type == 'armor':
        return get_random_armor()
    elif item_type == 'accessory':
        return get_random_accessory()
    else:  # potion
        return get_random_potion()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def compare_equipment(item1, item2):
    """Compare two pieces of equipment to see which is better"""
    if not isinstance(item1, Equipment) or not isinstance(item2, Equipment):
        return "Cannot compare non-equipment items"

    if item1.slot != item2.slot:
        return "Cannot compare different equipment types"

    if isinstance(item1, Weapon) and isinstance(item2, Weapon):
        if item1.attack_bonus > item2.attack_bonus:
            return f"{item1.name} is better (+{item1.attack_bonus - item2.attack_bonus} attack)"
        elif item1.attack_bonus < item2.attack_bonus:
            return f"{item2.name} is better (+{item2.attack_bonus - item1.attack_bonus} attack)"
        else:
            return "Both weapons have equal attack power"

    elif isinstance(item1, Armor) and isinstance(item2, Armor):
        if item1.defense_bonus > item2.defense_bonus:
            return f"{item1.name} is better (+{item1.defense_bonus - item2.defense_bonus} defense)"
        elif item1.defense_bonus < item2.defense_bonus:
            return f"{item2.name} is better (+{item2.defense_bonus - item1.defense_bonus} defense)"
        else:
            return "Both armor pieces have equal defense"

    return "Cannot compare these items"

# =============================================================================
# LOOT SYSTEM
# =============================================================================

def get_loot_for_monster(monster_name, floor_level=1):
    """Get appropriate loot for a specific monster type"""
    import random

    # Base drop chance (mon be modified by monster type)
    base_drop_chance = 0.4 #40% chance for basic monsters

    # Floor Scaling - higher floors have slightly better drop rates
    floor_bonus = min(0.1, floor_level * 0.01) # +1% per floor, max +10%
    drop_chance = base_drop_chance + floor_bonus

    # Check if monster drops anything at all
    if random.random() > drop_chance:
        return None # No loot this time

    # Monster-specific loot tables
    if monster_name.lower() == "giant rat":
        return get_rat_loot(floor_level)
    elif monster_name.lower() == "goblin":
        return get_goblin_loot(floor_level)
    elif monster_name.lower() == "orc":
        return get_orc_loot(floor_level)
    else:
        # Default loot for unknown monsters
        return get_random_basic_loot(floor_level)

def get_rat_loot(floor_level):
    """Loot table for rats - mostly consumables"""
    import random

    # Rats are weak but sometimes carry useful consumables
    roll = random.random(1, 100)

    if roll <= 70: # 70% chance
        return create_minor_health_potion()
    elif roll <= 90: # 20% chance
        return create_health_potion()
    else: # 10% chance - rats found something shiny
        if floor_level >= 3:
            return get_random_accessory()
        else:
            create_rusty_dagger()

def get_goblin_loot(floor_level):
    """Loot table for goblins - weapons and some armor"""
    import random

    # Goblins are fighters, they carry weapons and basic gear.
    roll = random.randint(1, 100)

    if roll <= 40: # 40% chance - weapons
        if floor_level >= 5:
            return random.choice([create_iron_sword(), create_short_sword()])
        else:
            return random.choice([create_rusty_dagger(), create_short_sword()])
    elif roll <= 65: # 25% chance - armor
        if floor_level >= 4:
            return create_chain_mail()
        else:
            return create_leather_armor()
    elif roll <= 85: # 20% chance - accessories
        return random.choice([create_minor_health_potion(), create_health_potion()])
    else: # 15% chance - accessories
        return get_random_accessory()

def get_orc_loot(floor_level):
    """Loot table for orcs - better weapons and armor"""
    import random

    # Orcs are strong and well-equipped
    roll = random.randint(1, 100)

    if roll <= 35: # 35% chance - good weapons
        if floor_level >= 6:
            return create_battle_axe()
        elif floor_level >= 3:
            return create_iron_sword()
        else:
            return create_short_sword()
    elif roll <= 60: # 25% chance - good armor
        if floor_level >= 5:
            return create_plate_armor()
        elif floor_level >= 3:
            return create_chain_mail()
        else:
            return create_leather_armor()
    elif roll <= 80: # 20% chance - healing items
        if floor_level >= 4:
            return create_greater_health_potion()
        else:
            return create_health_potion()
    else:
        return get_random_accessory()

def get_random_basic_loot(floor_level):
    """Default loot table for unknown monsters"""
    import random

    # Simple loot table for basic monsters
    roll = random.randint(1, 100)

    if roll <= 50: # 50% chance - consumables
        return get_random_potion()
    elif roll <= 75: # 25% chance - weapons
        return get_random_weapon()
    elif roll <= 90: # 15% chance - armor
        return get_random_armor()
    else: # 10% chance - accessories
        return get_random_accessory()

def get_floor_scaled_item(base_item, floor_level):
    """Scale item quality based on floor level (for future enhancement"""
    # For now, just return the base item
    # later i will add item quality scaling here
    return base_item