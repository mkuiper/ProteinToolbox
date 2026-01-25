"""
Central Skill Registry for ProteinToolbox

This file dynamically discovers and registers all functions from skill modules.
It creates a SKILL_REGISTRY that can be imported by the GUI and agents.
"""
import inspect
from . import (
    bio_skills,
    sim_skills,
    docking_skills,
    analysis_skills,
    design_skills,
    docs_skills,
    logic_skills,
    search_skills,
    structure_skills,
    validation_skills,
)

# List of all skill modules to be introspected
SKILL_MODULES = [
    bio_skills,
    sim_skills,
    docking_skills,
    analysis_skills,
    design_skills,
    docs_skills,
    logic_skills,
    search_skills,
    structure_skills,
    validation_skills,
]

SKILL_REGISTRY = {}

def register_skills():
    """
    Inspects skill modules and populates the SKILL_REGISTRY.
    """
    for module in SKILL_MODULES:
        # Find all functions in the module
        for name, func in inspect.getmembers(module, inspect.isfunction):
            # Exclude private functions and imported functions
            if not name.startswith('_') and func.__module__ == module.__name__:
                # Use the function's docstring as its description
                description = inspect.getdoc(func) or "No description provided."
                
                # Simplified description for brevity in some displays
                short_desc = description.split('\n')[0]
                
                SKILL_REGISTRY[name] = {
                    "name": name,
                    "module": module.__name__,
                    "function": func,
                    "description": description,
                    "short_description": short_desc,
                    "signature": str(inspect.signature(func)),
                }

# Automatically register skills upon import
register_skills()

def get_skill_description_for_agents():
    """
    Generates a simplified, context-efficient string of available skills for the LLM.
    """
    lines = []
    for name, skill in SKILL_REGISTRY.items():
        lines.append(f"- {name}{skill['signature']}")
    return "Execute a specific python skill. Available skills:\n" + "\n".join(lines)
