import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool as CrewTool

from proteintoolbox.registry import ToolRegistry
from proteintoolbox.resources import ResourceManager
from proteintoolbox.skills import (
    bio_skills, sim_skills, docking_skills, 
    analysis_skills, design_skills, search_skills, logic_skills, graph_reasoning,
    SKILL_REGISTRY, get_skill_description_for_agents
)

# --- Initialize Singletons ---
registry = ToolRegistry(registry_path=os.path.join(os.getcwd(), "ProteinToolbox/data/tool_registry.json"))
resources = ResourceManager()
# Initialize Knowledge Graph once
knowledge_graph = graph_reasoning.DomainKnowledgeGraph()

# --- Tool Definitions ---

class PathfinderTool(CrewTool):
    name: str = "Scientific Pathfinder"
    description: str = "Finds valid scientific workflows between two concepts (e.g., 'Sequence' to 'BindingEnergy')."

    def _run(self, query: str) -> str:
        # Expected input: "StartConcept|EndConcept"
        try:
            parts = query.split('|')
            if len(parts) != 2:
                return "Error: Input must be 'StartConcept|EndConcept'"
            
            start, end = parts[0].strip(), parts[1].strip()
            path = knowledge_graph.find_path(start, end)
            return "\n".join(path)
        except Exception as e:
            return f"Error finding path: {e}"

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
    description: str = "Analyzes a proposed plan (list of steps) for logical consistency. Input: Semicolon-separated steps."

    def _run(self, plan_str: str) -> str:
        steps = [s.strip() for s in plan_str.split(';')]
        validation = logic_skills.validate_workflow_logic(steps)
        refinements = logic_skills.propose_refinements(steps)
        
        output = f"Logic Analysis:\nValid: {validation.get('valid', False)}\n"
        if refinements:
            output += f"Suggestions: {refinements}\n"
        return output

class DecompositionTool(CrewTool):
    name: str = "Problem Decomposition"
    description: str = "Decomposes a complex request into a structured set of sub-tasks."

    def _run(self, request: str) -> str:
        return str(logic_skills.decompose_request(request))

class ReasoningTool(CrewTool):
    name: str = "Chain of Thought Templates"
    description: str = "Retrieves a structured reasoning template for a specific strategy."

    def _run(self, strategy: str) -> str:
        return logic_skills.get_reasoning_template(strategy)

class ExecuteSkillTool(CrewTool):
    name: str = "Execute Skill"
    description: str = get_skill_description_for_agents()

    def _run(self, command: str) -> str:
        try:
            parts = command.split("|")
            skill_name = parts[0].strip()
            args_str = parts[1:]

            if skill_name not in SKILL_REGISTRY:
                return f"Error: Unknown skill '{skill_name}'"

            skill_info = SKILL_REGISTRY[skill_name]
            func = skill_info["function"]
            
            # Simple arg parsing
            args = []
            current_arg = ""
            in_json = False
            for part in args_str:
                if '{' in part: in_json = True
                if in_json:
                    current_arg += part + "|"
                    if '}' in part:
                        in_json = False
                        args.append(current_arg.rstrip('|'))
                        current_arg = ""
                else:
                    args.append(part)

            return str(func(*args))

        except Exception as e:
            return f"Error executing skill '{command}': {e}"

# --- Reusable Tool Instances ---
registry_search_tool = RegistrySearchTool()
resource_check_tool = ResourceCheckTool()
execute_skill_tool = ExecuteSkillTool()
logic_tool = LogicTool()
decomposition_tool = DecompositionTool()
reasoning_tool = ReasoningTool()
pathfinder_tool = PathfinderTool()

# --- Agent Definitions ---
AGENT_DEFINITIONS = [
    {
        "name": "methodologist",
        "role": 'Scientific Methodologist',
        "goal": 'Decompose vague requests into rigorous scientific protocols.',
        "backstory": 'A master of the scientific method and root cause analysis, ensuring the right questions are asked before work begins.',
        "tools": [decomposition_tool, reasoning_tool, pathfinder_tool]
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
        "tools": [logic_tool, pathfinder_tool]
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
        "tools": [execute_skill_tool, logic_tool, pathfinder_tool]
    },
    {
        "name": "report_writer",
        "role": 'Report Writer',
        "goal": 'Synthesize results into a clear scientific report.',
        "backstory": 'A technical writer specializing in biotechnology.',
        "tools": []
    }
]

# --- Main Crew Function ---
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
    
    # Dynamically create agents
    agents = {
        d["name"]:
        Agent(
            role=d["role"],
            goal=d["goal"],
            backstory=d["backstory"],
            tools=d["tools"],
            llm=llm,
            verbose=True
        ) for d in AGENT_DEFINITIONS
    }

    # --- Tasks ---
    # Simplified task definition for prototype
    task_decompose = Task(
        description=f"Decompose the request: '{user_request}'.", 
        agent=agents["methodologist"], 
        expected_output="A structured problem decomposition."
    )
    
    task_research = Task(
        description="Search for relevant tools and literature based on the decomposition.",
        agent=agents["librarian"],
        expected_output="Research summary."
    )

    task_plan = Task(
        description="Create a detailed workflow plan.",
        agent=agents["architect"],
        expected_output="Step-by-step protocol."
    )

    crew = Crew(
        agents=list(agents.values()),
        tasks=[task_decompose, task_research, task_plan], 
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    return result