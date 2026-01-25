import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
from streamlit_molstar import st_molstar, st_molstar_rcsb

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from proteintoolbox.skills import bio_skills, sim_skills, design_skills, docs_skills, structure_skills, validation_skills
from proteintoolbox.agents.crew import run_design_task
from proteintoolbox.project import ProjectManager
from proteintoolbox.registry import ToolRegistry

st.set_page_config(page_title="ProteinToolbox", layout="wide", page_icon="🧬")

# Initialize Project Manager & Registry
pm = ProjectManager()
registry = ToolRegistry(registry_path=os.path.join(os.getcwd(), "ProteinToolbox/data/tool_registry.json"))

# Session State for Current Project
if 'current_project' not in st.session_state:
    st.session_state.current_project = None

st.title("🧬 ProteinToolbox")

# --- Sidebar ---
with st.sidebar:
    st.header("Project Management")
    
    # Project Selector
    project_list = pm.list_projects()
    selected_project_name = st.selectbox(
        "Current Project", 
        ["None"] + project_list, 
        index=0 if not st.session_state.current_project else project_list.index(st.session_state.current_project.name) + 1 if st.session_state.current_project.name in project_list else 0
    )
    
    if selected_project_name != "None":
        st.session_state.current_project = pm.get_project(selected_project_name)
    else:
        st.session_state.current_project = None

    # Create New Project
    with st.expander("Create New Project"):
        new_proj_name = st.text_input("Name")
        new_proj_desc = st.text_input("Description")
        if st.button("Create"):
            try:
                pm.create_project(new_proj_name, new_proj_desc)
                st.success(f"Created {new_proj_name}")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.divider()
    
    # LLM Settings
    with st.expander("LLM Settings"):
        llm_provider = st.selectbox("Provider", ["openai", "anthropic", "gemini", "deepseek", "ollama"])
        
        provider_models = {
            "openai": ["gpt-5.2", "gpt-5", "gpt-4o", "o3-mini", "o1"],
            "anthropic": ["claude-4.5-opus", "claude-4.5-sonnet", "claude-3-5-sonnet-latest"],
            "gemini": ["gemini-3-pro", "gemini-3-flash", "gemini-3-deep-think", "gemini-2.0-flash-exp"],
            "deepseek": ["deepseek-v3.2", "deepseek-v3", "deepseek-reasoner", "deepseek-chat"],
            "ollama": ["deepseek-v3.2", "llama3.3", "phi4", "mistral-small", "exaone-deep"]
        }
        
        selected_model = st.selectbox("Model", provider_models[llm_provider] + ["Other..."])
        
        if selected_model == "Other...":
            llm_model = st.text_input("Custom Model Name")
        else:
            llm_model = selected_model
            
        llm_api_key = st.text_input("API Key", type="password", help="Leave empty if using env vars or Ollama")
        llm_base_url = st.text_input("Base URL", value="http://localhost:11434" if llm_provider == "ollama" else "https://api.deepseek.com" if llm_provider == "deepseek" else "", help="Used for Ollama, DeepSeek, or custom endpoints")

    st.divider()
    st.header("Navigation")
    mode = st.radio("Mode", ["Workspace", "Agent Workflow", "Tools"])
    
    st.divider()
    show_tutorial = st.toggle("Enable Tutorial Mode", value=False, help="Show helper text and explanations for tools.")
    if show_tutorial:
        st.info("💡 **Tutorial Mode**: Enabled. Look for these blue boxes for guidance.")

# --- Main Area ---

if mode == "Workspace":
    if not st.session_state.current_project:
        st.info("Please select or create a project to start working.")
    else:
        proj = st.session_state.current_project
        st.subheader(f"Project: {proj.name}")
        st.markdown(f"*{proj.description}*")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Files")
            
            if show_tutorial:
                st.info("💡 **Files**: Select a file to visualize it on the right. Upload PDB files to add them to your project.")
                
            files = proj.list_files()
            if not files:
                st.warning("No files in project.")
            
            selected_file = st.radio("Select File", files)
            
            # File Upload
            uploaded_file = st.file_uploader("Upload PDB", type=['pdb', 'cif'])
            if uploaded_file:
                # Save uploaded file to project
                save_path = os.path.join(proj.path, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Saved {uploaded_file.name}")
                st.rerun()

            st.divider()
            if st.button("Generate Project Report"):
                report_path = docs_skills.generate_project_report(proj.path)
                st.success(f"Report generated: {os.path.basename(report_path)}")
                st.rerun()
            if show_tutorial:
                st.info("💡 **Report**: Generates a Markdown summary of all files and structures in the project.")

        with col2:
            st.markdown("### Visualization (Mol*)")
            if selected_file:
                file_path = proj.get_full_path(selected_file)
                if selected_file.endswith(".pdb") or selected_file.endswith(".cif") or selected_file.endswith(".ent"):
                    st_molstar(file_path, key="molstar_viewer", height=500)
                else:
                    st.info("Select a structure file to visualize.")

elif mode == "Tools":
    st.header("🛠️ Direct Tool Access & Info")
    
    # Define the tabs
    tab_list = [
        "Meet the Agents", 
        "Browse Skills", 
        "Registry Browser", 
        "Biological Data", 
        "Simulation", 
        "Analysis & Validation", 
        "Mutagenesis & Analysis"
    ]
    tabs = st.tabs(tab_list)
    
    # Tab 1: Meet the Agents
    with tabs[0]:
        st.subheader("The Design Crew")
        st.markdown("This toolbox uses a team of specialized AI agents to handle your request.")
        from proteintoolbox.agents.crew import AGENT_DEFINITIONS
        for agent_def in AGENT_DEFINITIONS:
            with st.expander(f"**{agent_def['role']}**"):
                st.markdown(f"**Goal:** {agent_def['goal']}")
                st.markdown(f"**Backstory:** {agent_def['backstory']}")
                tool_names = [t.name for t in agent_def['tools']] if agent_def['tools'] else ["None"]
                st.markdown(f"**Primary Tools:** `{', '.join(tool_names)}`")

    # Tab 2: Browse Skills
    with tabs[1]:
        st.subheader("Available Skills")
        st.markdown("Dynamically discovered functions available to the agents.")
        from proteintoolbox.skills import SKILL_REGISTRY
        for skill_name, skill_info in sorted(SKILL_REGISTRY.items()):
            with st.expander(f"`{skill_name}{skill_info['signature']}`"):
                st.markdown(f"**Module:** `{skill_info['module']}`")
                st.markdown(skill_info['description'])
                
    # Tab 3: Registry Browser
    with tabs[2]:
        st.subheader("Tool Registry")
        st.markdown("Database of high-level tools and software packages.")
        tools = registry.list_tools()
        for i, t in enumerate(tools):
            with st.expander(f"{t.name} ({t.category})"):
                st.markdown(f"**Description:** {t.description}")
                st.markdown(f"**URL:** {t.url}")
                st.checkbox("Installed", value=t.installed, disabled=True, key=f"chk_{i}_{t.name}")
    
    # ... Other tabs for direct tool access ...
    with tabs[3]:
        st.subheader("Fetch PDB")
        # ... (implementation from file) ...

    with tabs[4]:
        st.subheader("Minimize Structure")
        # ... (implementation from file) ...

    with tabs[5]:
        st.subheader("Structure Analysis & Validation")
        # ... (implementation from file) ...

    with tabs[6]:
        st.subheader("Sequence Mutagenesis & Analysis")
        # ... (implementation from file) ...



elif mode == "Agent Workflow":
    st.header("🤖 Agentic Design")
    st.markdown("Describe your goal, and the **CrewAI** agents (Librarian, Architect, Technician) will plan and execute it.")
    
    user_request = st.text_area("Design Goal", "Design a nanobody binder for the Spike protein.")
    
    if st.button("Start Workflow"):
        llm_config = {
            "provider": llm_provider,
            "api_key": llm_api_key if llm_api_key else None,
            "model": llm_model,
            "base_url": llm_base_url
        }
        
        with st.spinner("Agents are working..."):
            try:
                result = run_design_task(user_request, llm_config)
                st.success("Workflow Complete!")
                st.subheader("Result")
                st.markdown(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")