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

class LogicTool(CrewTool):
    name: str = "Workflow Logic Analyzer"
    description: str = "Analyzes a proposed plan (list of steps) for logical consistency and suggests refinements. Input: A semicolon-separated list of steps."

    def _run(self, plan_str: str) -> str:
        steps = [s.strip() for s in plan_str.split(';')]
        validation = logic_skills.validate_workflow_logic(steps)
        refinements = logic_skills.propose_refinements(steps)
        
        output = f"Logic Analysis for Plan ({len(steps)} steps):\n"
        output += f"Valid: {validation['valid']}\n"
        if not validation['valid']:
            output += f"Errors: {validation['errors']}\n"
        
        if refinements:
            output += f"Suggestions: {refinements}\n"
        
        if validation['valid'] and not refinements:
            output += "Plan looks logically sound and follows best practices."
            
        return output

class DecompositionTool(CrewTool):
    name: str = "Problem Decomposition"
    description: str = "Decomposes a complex request into a structured set of sub-tasks and constraints using heuristic logic. Input: The user request string."

    def _run(self, request: str) -> str:
        decomposition = logic_skills.decompose_request(request)
        return f"Decomposition Result:\nIntent: {decomposition['intent']}\nImplied Steps: {decomposition['implied_steps']}\nInferred Constraints: {decomposition['inferred_constraints']}"

class ReasoningTool(CrewTool):
    name: str = "Chain of Thought Templates"
    description: str = "Retrieves a structured reasoning template for a specific strategy. Input: Strategy name (e.g., 'scientific_method', 'design_cycle', 'root_cause_analysis', 'first_principles')."

    def _run(self, strategy: str) -> str:
        return logic_skills.get_reasoning_template(strategy)

class ExecuteSkillTool(CrewTool):
    name: str = "Execute Skill"
    description: str = "Execute a specific python skill. Format: 'skill_name|arg1|arg2'. Available skills: fetch_pdb_structure, run_minimization, generate_backbone, design_sequence, prepare_ligand, run_docking, analyze_sequence, search_pubmed, check_design_constraints, infer_functionality_issues, validate_workflow_logic, propose_refinements, decompose_request, get_reasoning_template."

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
                import json
                try:
                    constraints = json.loads(args[1]) if len(args) > 1 else {}
                except:
                    constraints = {}
                return str(logic_skills.check_design_constraints(args[0], constraints))

            elif skill_name == "infer_functionality_issues":
                return str(logic_skills.infer_functionality_issues(args[0]))

            elif skill_name == "validate_workflow_logic":
                steps = [s.strip() for s in args[0].split(';')]
                return str(logic_skills.validate_workflow_logic(steps))
                
            elif skill_name == "propose_refinements":
                steps = [s.strip() for s in args[0].split(';')]
                return str(logic_skills.propose_refinements(steps))

            elif skill_name == "decompose_request":
                return str(logic_skills.decompose_request(args[0]))

            elif skill_name == "get_reasoning_template":
                return str(logic_skills.get_reasoning_template(args[0]))
            
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
        provider = llm_config.get('provider')
        model = llm_config.get('model')
        api_key = llm_config.get('api_key')
        base_url = llm_config.get('base_url')

        if provider == 'openai':
             llm = LLM(model=model, api_key=api_key)
        elif provider == 'anthropic':
             llm = LLM(model=f"anthropic/{model}", api_key=api_key)
        elif provider == 'gemini':
             full_model = model if model.startswith("gemini/") else f"gemini/{model}"
             llm = LLM(model=full_model, api_key=api_key)
        elif provider == 'deepseek':
             llm = LLM(model=f"openai/{model}", api_key=api_key, base_url=base_url or "https://api.deepseek.com")
        elif provider == 'ollama':
             full_model = model if model.startswith("ollama/") else f"ollama/{model}"
             llm = LLM(model=full_model, base_url=base_url)
    
    # --- Agents ---
    
    # 0. Methodologist (New in Iteration 12)
    methodologist = Agent(
        role='Scientific Methodologist',
        goal='Decompose vague requests into rigorous scientific protocols.',
        backstory='You are a master of the scientific method and root cause analysis. You ensure the right questions are asked before work begins.',
        tools=[DecompositionTool(), ReasoningTool()],
        llm=llm,
        verbose=True
    )

    # 1. Literature & Strategy
    librarian = Agent(
        role='Scientific Librarian',
        goal='Identify appropriate tools and prior knowledge for the design task.',
        backstory='Expert in bioinformatics tools and literature.',
        tools=[RegistrySearchTool(), ExecuteSkillTool()],
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
        backstory='Senior scientist who orchestrates the specialist agents. You utilize Logic Tools to verify plans.',
        tools=[LogicTool()],
        llm=llm,
        verbose=True
    )

    # 4. Critique & Logic
    critic = Agent(
        role='Design Critic',
        goal='Validate protein designs against logical constraints and heuristics.',
        backstory='Quality Assurance specialist who ensures designs are physically viable before expensive simulations.',
        tools=[ExecuteSkillTool(), LogicTool()],
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

    task_decompose = Task(
        description=f"Decompose the request: '{user_request}' using 'Problem Decomposition'. Choose a reasoning strategy (e.g., 'scientific_method' or 'design_cycle') and outline the approach.",
        agent=methodologist,
        expected_output="A structured problem decomposition and selected strategy."
    )

    task_research = Task(
        description=f"Search literature (search_pubmed) and registry for relevant info based on the methodologist's decomposition.",
        agent=librarian,
        expected_output="Summary of literature and tools found."
    )

    task_plan = Task(
        description=f"Create a step-by-step workflow based on research and decomposition.",
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
        agents=[methodologist, librarian, architect, sequence_engineer, critic, structure_analyst, report_writer],
        tasks=[task_decompose, task_research, task_plan, task_execute_seq, task_critique, task_execute_struct, task_report],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    return result
