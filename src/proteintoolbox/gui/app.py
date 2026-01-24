import streamlit as st
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from proteintoolbox.skills import bio_skills, sim_skills, design_skills
from proteintoolbox.agents.crew import run_design_task
from stmol import showmol
import py3Dmol

st.set_page_config(page_title="ProteinToolbox", layout="wide")

st.title("🧬 ProteinToolbox")

with st.sidebar:
    st.header("Navigation")
    mode = st.radio("Mode", ["Tools", "Agent Workflow", "About"])

if mode == "Tools":
    st.header("🛠️ Direct Tool Access")
    
    tab1, tab2, tab3 = st.tabs(["Biological Data", "Simulation", "Design"])
    
    with tab1:
        st.subheader("Fetch PDB")
        pdb_id = st.text_input("PDB ID (e.g., 1CRN)", "1CRN")
        if st.button("Fetch Structure"):
            with st.spinner("Downloading..."):
                path = bio_skills.fetch_pdb_structure(pdb_id, "data/pdb")
                st.success(f"Downloaded to {path}")
                
                # Visualize
                with open(path) as f:
                    pdb_str = f.read()
                view = py3Dmol.view(width=400, height=300)
                view.addModel(pdb_str, 'pdb')
                view.setStyle({'cartoon': {'color': 'spectrum'}})
                view.zoomTo()
                showmol(view, height=300, width=400)

    with tab2:
        st.subheader("Minimize Structure")
        input_pdb = st.text_input("Input PDB Path", "data/pdb/pdb1crn.ent")
        output_pdb = st.text_input("Output Path", "minimized.pdb")
        if st.button("Run Minimization"):
            with st.spinner("Running OpenMM..."):
                res = sim_skills.run_minimization(input_pdb, output_pdb)
                st.info(res)
    
    with tab3:
        st.subheader("RFdiffusion (Dry Run)")
        prompt = st.text_input("Prompt", "binder_design")
        if st.button("Generate Backbone"):
            res = design_skills.generate_backbone(prompt, dry_run=True)
            st.code(res, language="bash")

elif mode == "Agent Workflow":
    st.header("🤖 Agentic Design")
    st.markdown("Describe your goal, and the **CrewAI** agents (Librarian, Architect, Technician) will plan and execute it.")
    
    user_request = st.text_area("Design Goal", "Design a nanobody binder for the Spike protein.")
    
    if st.button("Start Workflow"):
        with st.spinner("Agents are working... (Check console for detailed logs)"):
            # Redirect stdout to capture agent logs if possible, but for now just run it
            try:
                result = run_design_task(user_request)
                st.success("Workflow Complete!")
                st.subheader("Result")
                st.markdown(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")

elif mode == "About":
    st.markdown("""
    ## About ProteinToolbox
    
    An AI-powered suite for protein design.
    
    **Architecture**:
    *   **Skills**: Lightweight Python functions for BioPython, OpenMM, etc.
    *   **Agents**: CrewAI agents that orchestrate these skills.
    *   **Registry**: Database of available tools.
    """)
