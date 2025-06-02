#!/usr/bin/env python3
"""
ASCII RPG - A roguelike inspired by ADOM
Main entry point for the game
"""

from game import Game

def main():
    """Initialize and run the game"""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Re-raise for debugging

if __name__ == "__main__":
    main()