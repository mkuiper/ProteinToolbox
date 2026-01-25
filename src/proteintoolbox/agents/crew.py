from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool as CrewTool
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

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool as CrewTool
from proteintoolbox.registry import ToolRegistry
from proteintoolbox.resources import ResourceManager
from proteintoolbox.skills import bio_skills, sim_skills, docking_skills, analysis_skills, design_skills, search_skills, logic_skills
import os

# Initialize Registry and Resources
registry = ToolRegistry(registry_path=os.path.join(os.getcwd(), "ProteinToolbox/data/tool_registry.json"))
resources = ResourceManager()

# --- Custom Tools for Agents ---

class RegistrySearchTool(CrewTool):
    name: str = "Search Tool Registry"
    description: str = "Search for available protein design tools by name or category."

    def _run(self, query: str) -> str:
        tools = registry.list_tools(category=query)
        if not tools:
            tool = registry.get_tool(query)
            if tool:
                tools = [tool]
            else:
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
    description: str = "Execute a specific python skill. Format: 'skill_name|arg1|arg2'. Available skills: fetch_pdb_structure, run_minimization, generate_backbone, design_sequence, prepare_ligand, run_docking, analyze_sequence, search_pubmed, check_design_constraints, infer_functionality_issues."

    def _run(self, command: str) -> str:
        try:
            parts = command.split("|")
            skill_name = parts[0].strip()
            args = [p.strip() for p in parts[1:]]

            # Bio Skills
            if skill_name == "fetch_pdb_structure":
                return bio_skills.fetch_pdb_structure(args[0], args[1] if len(args) > 1 else "data/pdb")
            
            # Simulation Skills
            elif skill_name == "run_minimization":
                return sim_skills.run_minimization(args[0], args[1] if len(args) > 1 else "minimized.pdb")
            
            # Design Skills
            elif skill_name == "generate_backbone":
                return design_skills.generate_backbone(args[0], args[1] if len(args) > 1 else "output/rfdiffusion")
            elif skill_name == "design_sequence":
                return design_skills.design_sequence(args[0], args[1] if len(args) > 1 else "output/mpnn")
            
            # Docking Skills
            elif skill_name == "prepare_ligand":
                return docking_skills.prepare_ligand(args[0], args[1] if len(args) > 1 else None)
            elif skill_name == "run_docking":
                # Expecting: run_docking|receptor.pdbqt|ligand.pdbqt|0,0,0|20,20,20
                center = [float(x) for x in args[2].split(',')]
                size = [float(x) for x in args[3].split(',')]
                return docking_skills.run_docking(args[0], args[1], center, size, args[4] if len(args) > 4 else "docked.pdbqt")
            
            # Analysis Skills
            elif skill_name == "analyze_sequence":
                return str(analysis_skills.analyze_sequence(args[0]))
            
            # Search Skills
            elif skill_name == "search_pubmed":
                return search_skills.search_pubmed(args[0], int(args[1]) if len(args) > 1 else 5)
            
            # Logic Skills
            elif skill_name == "check_design_constraints":
                # Expecting: check_design_constraints|sequence|{"max_molecular_weight": 50000}
                import json
                try:
                    constraints = json.loads(args[1]) if len(args) > 1 else {}
                except:
                    constraints = {}
                return str(logic_skills.check_design_constraints(args[0], constraints))

            elif skill_name == "infer_functionality_issues":
                return str(logic_skills.infer_functionality_issues(args[0]))
            
            else:
                return f"Error: Unknown skill '{skill_name}'"
        except Exception as e:
            return f"Error executing skill: {str(e)}"

# --- Crew Manager ---

def run_design_task(user_request: str, llm_config: dict = None):
    print(f"\n--- Starting ProteinToolbox Design Task: {user_request} ---\n")
    
    # Configure LLM
    llm = None
    if llm_config:
        # Check for provider specific handling
        if llm_config.get('provider') == 'openai':
             llm = LLM(model=llm_config.get('model', 'gpt-4o'), api_key=llm_config.get('api_key'))
        elif llm_config.get('provider') == 'anthropic':
             llm = LLM(model=llm_config.get('model', 'claude-3-5-sonnet-20240620'), api_key=llm_config.get('api_key'))
        elif llm_config.get('provider') == 'gemini':
             llm = LLM(model=llm_config.get('model', 'gemini/gemini-1.5-pro-latest'), api_key=llm_config.get('api_key'))
        elif llm_config.get('provider') == 'ollama':
             llm = LLM(model=llm_config.get('model', 'ollama/llama3'), base_url=llm_config.get('base_url'))
    
    # Fallback to env var if no config passed
    if not llm and not os.environ.get("OPENAI_API_KEY"):
         # Ideally we might allow running without LLM for pure tool usage, but Agents need it.
         pass 

    # --- Agents ---
    
    # 1. Literature & Strategy
    librarian = Agent(
        role='Scientific Librarian',
        goal='Identify appropriate tools and prior knowledge for the design task.',
        backstory='Expert in bioinformatics tools and literature.',
        tools=[RegistrySearchTool(), ExecuteSkillTool()], # Added ExecuteSkillTool for search_pubmed
        llm=llm,
        verbose=True
    )

    # 2. Design Core
    sequence_engineer = Agent(
        role='Sequence Engineer',
        goal='Optimize amino acid sequences for stability and function.',
        backstory='Specialist in protein language models (ProteinMPNN) and evolutionary analysis.',
        tools=[ExecuteSkillTool()],
        llm=llm,
        verbose=True
    )

    structure_analyst = Agent(
        role='Structure Analyst',
        goal='Analyze and validat protein structures.',
        backstory='Expert in molecular dynamics and structural quality metrics.',
        tools=[ExecuteSkillTool(), ResourceCheckTool()],
        llm=llm,
        verbose=True
    )

    # 3. Coordination
    architect = Agent(
        role='Protein Design Architect',
        goal='Design the overall experimental workflow.',
        backstory='Senior scientist who orchestrates the specialist agents.',
        llm=llm,
        verbose=True
    )

    # 4. Critique & Logic
    critic = Agent(
        role='Design Critic',
        goal='Validate protein designs against logical constraints and heuristics.',
        backstory='Quality Assurance specialist who ensures designs are physically viable before expensive simulations.',
        tools=[ExecuteSkillTool()],
        llm=llm,
        verbose=True
    )

    # 5. Reporting
    report_writer = Agent(
        role='Report Writer',
        goal='Synthesize results into a clear scientific report.',
        backstory='Technical writer specializing in biotechnology.',
        llm=llm,
        verbose=True
    )

    # --- Tasks ---

    task_research = Task(
        description=f"Analyze request: '{user_request}'. Search literature (search_pubmed) and registry for relevant info.",
        agent=librarian,
        expected_output="Summary of literature and tools found."
    )

    task_plan = Task(
        description=f"Create a step-by-step workflow based on librarian's research.",
        agent=architect,
        expected_output="Detailed protocol."
    )

    task_execute_seq = Task(
        description="Execute sequence design steps if applicable (using 'Execute Skill' for design_sequence).",
        agent=sequence_engineer,
        expected_output="Designed sequences or status."
    )

    task_critique = Task(
        description="Validate the designed sequences using 'check_design_constraints' and 'infer_functionality_issues'. Report any violations.",
        agent=critic,
        expected_output="Validation report with Pass/Fail status."
    )

    task_execute_struct = Task(
        description="Execute structure analysis/simulation steps (using 'Execute Skill' for run_minimization, analyze_sequence, etc.).",
        agent=structure_analyst,
        expected_output="Structure analysis report."
    )

    task_report = Task(
        description="Compile all findings into a final report.",
        agent=report_writer,
        expected_output="Final textual report of the design run."
    )

    crew = Crew(
        agents=[librarian, architect, sequence_engineer, critic, structure_analyst, report_writer],
        tasks=[task_research, task_plan, task_execute_seq, task_critique, task_execute_struct, task_report],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    return result
