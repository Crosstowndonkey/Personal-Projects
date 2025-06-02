import random

class Monster:
    def __init__(self, name, symbol, hp, attack, defense, x=0, y=0):
        # Basic Info
        self.name = name
        self.symbol = symbol

        # Position
        self.x = x
        self.y = y

        #combat stats
        self.max_hp = hp
        self.current_hp = hp
        self.attack = attack
        self.defense = defense

        # AI state
        self.target_x = None
        self.target_y = None
        self.has_seen_player = False

    def is_alive(self):
        """Check if monster is still alive"""
        return self.current_hp > 0

    def take_damage(self, damage):
        """Apply damage to monster, return True if monster dies"""
        actual_damage = max(1, damage - self.defense)  # Minimum 1 damage
        self.current_hp -= actual_damage
        return self.current_hp <= 0

    def heal(self, amount):
        """Restore health up to maximum"""
        self.current_hp - min(self.max_hp, self.current_hp + amount)

    def get_attack_damage(self):
        """Calculate damage for this monster's attack"""
        base_damage = self.attack
        variance = random.randint(-2, 3) # -2 to +3 damage variance
        return max(1, base_damage + variance)

def create_goblin(x, y):
    """Factory function to create a goblin"""
    return Monster(
        name="Goblin",
        symbol="g",
        hp=15,
        attack=4,
        defense=1,
        x=x,
        y=y
    )

def create_orc(x, y):
    """Factory function to create an orc"""
    return Monster(
        name="Orc",
        symbol="o",
        hp=25,
        attack=6,
        defense=2,
        x=x,
        y=y
    )

def create_rat(x, y):
    """Factory function to create a rat"""
    return Monster(
        name="Giant Rat",
        symbol="r",
        hp=8,
        attack=2,
        defense=0,
        x=x,
        y=y
    )