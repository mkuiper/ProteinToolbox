from crewai import Agent, Task, Crew, Process
from crewai.tools import Tool as CrewTool
from proteintoolbox.registry import ToolRegistry
from proteintoolbox.resources import ResourceManager
from proteintoolbox.skills import bio_skills, sim_skills
import os

# Initialize Registry and Resources
registry = ToolRegistry(registry_path=os.path.join(os.getcwd(), "ProteinToolbox/data/tool_registry.json"))
resources = ResourceManager()

# --- Custom Tools for Agents ---

class RegistrySearchTool(CrewTool):
    name: str = "Search Tool Registry"
    description: str = "Search for available protein design tools by name or category."

    def _run(self, query: str) -> str:
        # check if query matches a category
        tools = registry.list_tools(category=query)
        if not tools:
            # check if query matches a specific tool
            tool = registry.get_tool(query)
            if tool:
                tools = [tool]
            else:
                # return all tools if generic search or no match
                tools = registry.list_tools()
        
        result = "Available Tools:\n"
        for t in tools:
            result += f"- {t.name} ({t.category}): {t.description} [Installed: {t.installed}]\n"
        return result

class ResourceCheckTool(CrewTool):
    name: str = "Check System Resources"
    description: str = "Check if GPU/CUDA is available for compute-intensive tasks."

    def _run(self, query: str) -> str:
        status = resources.get_status()
        return f"System Resources: GPU Available: {status['gpu_available']}, Name: {status['gpu_name']}"

class ExecuteSkillTool(CrewTool):
    name: str = "Execute Skill"
    description: str = "Execute a specific python skill. Format: 'skill_name|arg1|arg2'. Available skills: fetch_pdb_structure, run_minimization."

    def _run(self, command: str) -> str:
        try:
            parts = command.split("|")
            skill_name = parts[0].strip()
            args = [p.strip() for p in parts[1:]]

            if skill_name == "fetch_pdb_structure":
                return bio_skills.fetch_pdb_structure(args[0], args[1] if len(args) > 1 else "data/pdb")
            elif skill_name == "run_minimization":
                return sim_skills.run_minimization(args[0], args[1] if len(args) > 1 else "minimized.pdb")
            else:
                return f"Error: Unknown skill '{skill_name}'"
        except Exception as e:
            return f"Error executing skill: {str(e)}"

# --- Agents ---

librarian = Agent(
    role='Scientific Librarian',
    goal='Maintain knowledge of available protein design software and their capabilities.',
    backstory='You are an expert in bioinformatics software. You know what every tool does and its requirements.',
    tools=[RegistrySearchTool(), ResourceCheckTool()],
    verbose=True
)

architect = Agent(
    role='Protein Design Architect',
    goal='Design comprehensive computational experiments to solve protein engineering challenges.',
    backstory='You are a senior scientist with years of experience in structural biology and de novo protein design. You plan the workflow step-by-step.',
    verbose=True
)

technician = Agent(
    role='Computational Lab Technician',
    goal='Execute the computational workflows and run simulations.',
    backstory='You are a skilled bioinformatician who knows how to run Python scripts and CLI tools for protein design.',
    tools=[ExecuteSkillTool()],
    verbose=True
)

# --- Crew Manager ---

def run_design_task(user_request: str):
    print(f"\n--- Starting ProteinToolbox Design Task: {user_request} ---\n")

    # Task 1: Research available tools
    task_research = Task(
        description=f"Analyze the user request: '{user_request}'. Search the registry to identify the best tools for this job. Check if we have the necessary hardware (GPU) for them.",
        agent=librarian,
        expected_output="A list of recommended tools from the registry and confirmation of hardware compatibility."
    )

    # Task 2: Plan the workflow
    task_plan = Task(
        description=f"Based on the recommended tools, create a step-by-step workflow to achieve the goal: '{user_request}'. Identify which specific 'skills' (like fetch_pdb_structure, run_minimization) are needed.",
        agent=architect,
        expected_output="A detailed, numbered experiment protocol with specific skill names mentioned."
    )

    # Task 3: Execution Plan (Simulated/Real)
    task_execute = Task(
        description="Review the protocol. Use the 'Execute Skill' tool to actually run the steps if possible (e.g., if the plan involves fetching a PDB). If a step requires a tool not yet implemented as a skill, describe the manual command.",
        agent=technician,
        expected_output="Result of the executed skills or a script for manual execution."
    )

    crew = Crew(
        agents=[librarian, architect, technician],
        tasks=[task_research, task_plan, task_execute],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    return result
