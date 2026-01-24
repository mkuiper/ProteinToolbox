import streamlit as st
import os
import sys
from streamlit_molstar import st_molstar, st_molstar_rcsb

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from proteintoolbox.skills import bio_skills, sim_skills, design_skills
from proteintoolbox.agents.crew import run_design_task
from proteintoolbox.project import ProjectManager

st.set_page_config(page_title="ProteinToolbox", layout="wide", page_icon="🧬")

# Initialize Project Manager
pm = ProjectManager()

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
    st.header("Navigation")
    mode = st.radio("Mode", ["Workspace", "Agent Workflow", "Tools"])

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

        with col2:
            st.markdown("### Visualization (Mol*)")
            if selected_file:
                file_path = proj.get_full_path(selected_file)
                if selected_file.endswith(".pdb") or selected_file.endswith(".cif") or selected_file.endswith(".ent"):
                    st_molstar(file_path, key="molstar_viewer", height=500)
                else:
                    st.info("Select a structure file to visualize.")

elif mode == "Tools":
    st.header("🛠️ Direct Tool Access")
    
    if not st.session_state.current_project:
        st.warning("Tools generally require an active project to save outputs.")
    
    tab1, tab2, tab3 = st.tabs(["Biological Data", "Simulation", "Design"])
    
    with tab1:
        st.subheader("Fetch PDB")
        pdb_id = st.text_input("PDB ID (e.g., 1CRN)", "1CRN")
        if st.button("Fetch Structure"):
            if st.session_state.current_project:
                output_dir = st.session_state.current_project.path
            else:
                output_dir = "data/temp" # Fallback
            
            with st.spinner("Downloading..."):
                path = bio_skills.fetch_pdb_structure(pdb_id, output_dir)
                st.success(f"Downloaded to {path}")
                if st.session_state.current_project:
                    st.rerun() # Refresh file list

    with tab2:
        st.subheader("Minimize Structure")
        # Allow selecting from project files
        if st.session_state.current_project:
            files = st.session_state.current_project.list_files('.pdb') + st.session_state.current_project.list_files('.ent')
            input_pdb = st.selectbox("Input PDB", files)
            if input_pdb:
                input_path = st.session_state.current_project.get_full_path(input_pdb)
                output_name = st.text_input("Output Filename", f"min_{input_pdb}")
                if st.button("Run Minimization"):
                    output_path = os.path.join(st.session_state.current_project.path, output_name)
                    with st.spinner("Running OpenMM..."):
                        res = sim_skills.run_minimization(input_path, output_path)
                        st.info(res)
                        st.rerun()
        else:
            st.info("Select a project to run simulations.")

    with tab3:
        st.subheader("RFdiffusion (Dry Run)")
        prompt = st.text_input("Prompt", "binder_design")
        if st.button("Generate Backbone"):
            # Mock output dir
            res = design_skills.generate_backbone(prompt, dry_run=True)
            st.code(res, language="bash")

elif mode == "Agent Workflow":
    st.header("🤖 Agentic Design")
    st.markdown("Describe your goal, and the **CrewAI** agents (Librarian, Architect, Technician) will plan and execute it.")
    
    user_request = st.text_area("Design Goal", "Design a nanobody binder for the Spike protein.")
    
    if st.button("Start Workflow"):
        with st.spinner("Agents are working..."):
            try:
                result = run_design_task(user_request)
                st.success("Workflow Complete!")
                st.subheader("Result")
                st.markdown(result)
                
                # If agents generated files, we'd want to refresh the project view
                # Ideally agents should be project-aware (passing project path to them)
            except Exception as e:
                st.error(f"An error occurred: {e}")