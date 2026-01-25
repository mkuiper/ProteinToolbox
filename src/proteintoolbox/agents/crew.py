from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool as CrewTool
from proteintoolbox.registry import ToolRegistry
from proteintoolbox.resources import ResourceManager
from proteintoolbox.skills import (
    bio_skills, sim_skills, docking_skills, 
    analysis_skills, design_skills, search_skills, logic_skills
)
import os

# Initialize Registry and Resources
registry = ToolRegistry(registry_path=os.path.join(os.getcwd(), "ProteinToolbox/data/tool_registry.json"))
resources = ResourceManager()

# --- Reusable Tools ---
registry_search_tool = RegistrySearchTool()
resource_check_tool = ResourceCheckTool()
execute_skill_tool = ExecuteSkillTool()
logic_tool = LogicTool()
decomposition_tool = DecompositionTool()
reasoning_tool = ReasoningTool()

# --- Agent Definitions ---
AGENT_DEFINITIONS = [
    {
        "name": "methodologist",
        "role": 'Scientific Methodologist',
        "goal": 'Decompose vague requests into rigorous scientific protocols.',
        "backstory": 'A master of the scientific method and root cause analysis, ensuring the right questions are asked before work begins.',
        "tools": [decomposition_tool, reasoning_tool]
    },
    {
        "name": "librarian",
        "role": 'Scientific Librarian',
        "goal": 'Identify appropriate tools and prior knowledge for the design task.',
        "backstory": 'An expert in bioinformatics tools and literature.',
        "tools": [registry_search_tool, execute_skill_tool]
    },
    {
        "name": "architect",
        "role": 'Protein Design Architect',
        "goal": 'Design the overall experimental workflow.',
        "backstory": 'A senior scientist who orchestrates the specialist agents and verifies plans with logic.',
        "tools": [logic_tool]
    },
    {
        "name": "sequence_engineer",
        "role": 'Sequence Engineer',
        "goal": 'Optimize amino acid sequences for stability and function.',
        "backstory": 'A specialist in protein language models and evolutionary analysis.',
        "tools": [execute_skill_tool]
    },
    {
        "name": "structure_analyst",
        "role": 'Structure Analyst',
        "goal": 'Analyze and validate protein structures.',
        "backstory": 'An expert in molecular dynamics and structural quality metrics.',
        "tools": [execute_skill_tool, resource_check_tool]
    },
    {
        "name": "critic",
        "role": 'Design Critic',
        "goal": 'Validate protein designs against logical constraints and heuristics.',
        "backstory": 'A quality assurance specialist who ensures designs are physically viable.',
        "tools": [execute_skill_tool, logic_tool]
    },
    {
        "name": "report_writer",
        "role": 'Report Writer',
        "goal": 'Synthesize results into a clear scientific report.',
        "backstory": 'A technical writer specializing in biotechnology.',
        "tools": []
    }
]

# --- Crew Manager ---
def run_design_task(user_request: str, llm_config: dict = None):
    print(f"\n--- Starting ProteinToolbox Design Task: {user_request} ---\n")
    
    # Configure LLM
    # ... (LLM setup logic remains the same)
    
    # Dynamically create agents from definitions
    agents = {
        d["name"]:
        Agent(
            role=d["role"],
            goal=d["goal"],
            backstory=d["backstory"],
            tools=d["tools"],
            llm=llm,
            verbose=True
        )
        for d in AGENT_DEFINITIONS
    }

    # --- Tasks ---
    task_decompose = Task(description=f"Decompose the request: '{user_request}'.", agent=agents["methodologist"], expected_output="A structured problem decomposition.")
    # ... (other tasks)

    crew = Crew(
        agents=list(agents.values()),
        tasks=[task_decompose, ...], # Simplified for brevity
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    return result