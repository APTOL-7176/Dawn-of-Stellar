# Copilot Instructions for Roguelike Game

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a Python-based roguelike game inspired by the classic Rogue game, featuring:
- ASCII character-based graphics
- ATB (Active Time Battle) combat system
- Wound mechanics with HP limitations
- 4-person party system
- Damage calculation based on attack/defense ratios

## Code Style Guidelines
- Use clear, descriptive variable names in Korean or English
- Implement object-oriented design patterns
- Separate game logic into distinct modules
- Use type hints where appropriate
- Follow PEP 8 style guidelines

## Game Mechanics to Remember
- Wounds accumulate at 25% of damage taken
- Maximum wounds can be 75% of max HP
- Wound healing: excess healing above limited max HP heals wounds at 25% rate
- Damage formula: (Attacker ATK / Defender DEF) * modifiers
- ATB system for turn-based combat timing
