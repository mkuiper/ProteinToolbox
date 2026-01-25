import networkx as nx
from typing import List, Dict, Any

class ReasoningGraph:
    """
    A Graph-of-Thought (GoT) engine for structuring scientific reasoning.
    Uses a Directed Acyclic Graph (DAG) to model dependencies between
    observations, hypotheses, experiments, and conclusions.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_step(self, step_id: str, description: str, type: str = "general"):
        """
        Adds a reasoning step to the graph.
        
        Args:
            step_id: Unique identifier for the step (e.g., 'step1').
            description: Text description of the thought/action.
            type: Category (observation, hypothesis, experiment, analysis, conclusion).
        """
        self.graph.add_node(step_id, description=description, type=type)

    def add_dependency(self, from_id: str, to_id: str):
        """
        Declares that 'to_id' depends on 'from_id' (from -> to).
        """
        if from_id not in self.graph:
            raise ValueError(f"Source step '{from_id}' not found.")
        if to_id not in self.graph:
            raise ValueError(f"Target step '{to_id}' not found.")
            
        self.graph.add_edge(from_id, to_id)
        
        if not nx.is_directed_acyclic_graph(self.graph):
            self.graph.remove_edge(from_id, to_id)
            raise ValueError(f"Adding dependency {from_id}->{to_id} created a cycle (circular logic).")

    def get_plan(self) -> List[Dict[str, Any]]:
        """
        Returns a linear execution plan based on topological sort.
        """
        if not nx.is_directed_acyclic_graph(self.graph):
             return [{"error": "Graph contains cycles."}]
             
        try:
            order = list(nx.topological_sort(self.graph))
            plan = []
            for step_id in order:
                node = self.graph.nodes[step_id]
                plan.append({
                    "id": step_id,
                    "type": node.get("type", "general"),
                    "description": node.get("description", "")
                })
            return plan
        except Exception as e:
            return [{"error": str(e)}]

    def analyze_graph(self) -> Dict[str, Any]:
        """
        Analyzes the structure of the reasoning graph.
        """
        return {
            "num_steps": self.graph.number_of_nodes(),
            "num_dependencies": self.graph.number_of_edges(),
            "is_valid_dag": nx.is_directed_acyclic_graph(self.graph),
            "roots": [n for n, d in self.graph.in_degree() if d == 0],
            "leaves": [n for n, d in self.graph.out_degree() if d == 0]
        }

class DomainKnowledgeGraph:
    """
    A static ontology of protein design concepts and valid transitions.
    Used for high-level planning and checking if a proposed workflow is scientifically grounded.
    """
    def __init__(self):
        self.ontology = nx.DiGraph()
        self._build_ontology()
        
    def _build_ontology(self):
        # Nodes = Data Types / States
        concepts = [
            "TargetDescription", "GeneSequence", "ProteinSequence", 
            "MSA", "Structure3D", "DockedComplex", "MDTrajectory", 
            "AnalysisReport", "ExperimentalProtocol"
        ]
        self.ontology.add_nodes_from(concepts)
        
        # Edges = Transformations / Methods
        transitions = [
            ("TargetDescription", "ProteinSequence", {"method": "Design/Generation"}),
            ("TargetDescription", "GeneSequence", {"method": "Database Search"}),
            ("GeneSequence", "ProteinSequence", {"method": "Translation"}),
            ("ProteinSequence", "MSA", {"method": "Homology Search"}),
            ("ProteinSequence", "Structure3D", {"method": "Folding (AlphaFold/ESMFold)"}),
            ("MSA", "Structure3D", {"method": "Folding (AlphaFold)"}),
            ("Structure3D", "DockedComplex", {"method": "Docking (Vina/DiffDock)"}),
            ("Structure3D", "MDTrajectory", {"method": "Molecular Dynamics (OpenMM)"}),
            ("DockedComplex", "AnalysisReport", {"method": "Scoring/Interaction Analysis"}),
            ("Structure3D", "AnalysisReport", {"method": "Quality Assessment"}),
            ("ProteinSequence", "AnalysisReport", {"method": "Property Calculation"}),
            ("AnalysisReport", "ExperimentalProtocol", {"method": "Report Synthesis"})
        ]
        self.ontology.add_edges_from([(u, v, k) for u, v, k in transitions])

    def find_path(self, start_concept: str, end_concept: str) -> List[str]:
        """
        Finds a valid scientific path from start to end concept.
        """
        try:
            path = nx.shortest_path(self.ontology, source=start_concept, target=end_concept)
            annotated_path = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                method = self.ontology[u][v].get("method", "Transform")
                annotated_path.append(f"Step {i+1}: Convert {u} to {v} via {method}")
            return annotated_path
        except nx.NetworkXNoPath:
            return [f"No scientific path found from {start_concept} to {end_concept}."]
        except nx.NodeNotFound as e:
            return [str(e)]

    def get_prerequisites(self, concept: str) -> List[str]:
        """Returns direct precursors for a concept."""
        if concept not in self.ontology:
            return []
        return list(self.ontology.predecessors(concept))

def create_standard_workflow(workflow_type: str) -> ReasoningGraph:
    """
    Factory function to create standard scientific reasoning graphs.
    """
    rg = ReasoningGraph()
    
    if workflow_type == "protein_design":
        rg.add_step("obs", "Identify target constraints", "observation")
        rg.add_step("hyp", "Propose fold/sequence strategy", "hypothesis")
        rg.add_step("search", "Search PDB/Literature", "experiment")
        rg.add_step("design", "Generate sequences", "experiment")
        rg.add_step("fold", "Predict structure (Fold)", "experiment")
        rg.add_step("eval", "Evaluate metrics", "analysis")
        
        rg.add_dependency("obs", "hyp")
        rg.add_dependency("hyp", "search")
        rg.add_dependency("search", "design")
        rg.add_dependency("design", "fold")
        rg.add_dependency("fold", "eval")
        
    elif workflow_type == "docking":
        rg.add_step("prep_rec", "Prepare Receptor", "experiment")
        rg.add_step("prep_lig", "Prepare Ligand", "experiment")
        rg.add_step("dock", "Run Vina Docking", "experiment")
        rg.add_step("analyze", "Analyze Binding Energy", "analysis")
        
        rg.add_dependency("prep_rec", "dock")
        rg.add_dependency("prep_lig", "dock")
        rg.add_dependency("dock", "analyze")
        
    return rg
