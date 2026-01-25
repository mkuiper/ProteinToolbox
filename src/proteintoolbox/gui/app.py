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
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Meet the Agents", "Registry Browser", "Biological Data", 
        "Simulation", "Analysis & Validation", "Mutagenesis & Analysis"
    ])
    
    with tab1:
        st.subheader("The Design Crew")
        st.markdown("This toolbox uses a team of specialized AI agents to handle your request.")
        
        # This part of the code now needs to be defined in app.py or imported
        from proteintoolbox.agents.crew import AGENT_DEFINITIONS
        
        for agent_def in AGENT_DEFINITIONS:
            with st.expander(f"**{agent_def['role']}**"):
                st.markdown(f"**Goal:** {agent_def['goal']}")
                st.markdown(f"**Backstory:** {agent_def['backstory']}")
                
                tool_names = [t.name for t in agent_def['tools']] if agent_def['tools'] else ["None"]
                st.markdown(f"**Primary Tools:** `{', '.join(tool_names)}`")

    with tab2:
        st.subheader("Tool Registry & Skills")
        st.markdown("Database of available tools for agents and users.")
        # ... (rest of the tab remains the same)

    with tab2:
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

    with tab3:
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

    with tab4:
        st.subheader("RFdiffusion (Dry Run)")
        prompt = st.text_input("Prompt", "binder_design")
        if st.button("Generate Backbone"):
            # Mock output dir
            res = design_skills.generate_backbone(prompt, dry_run=True)
            st.code(res, language="bash")

    with tab5:
        st.subheader("Structure Analysis & Validation")
        if st.session_state.current_project:
            files = st.session_state.current_project.list_files('.pdb') + st.session_state.current_project.list_files('.ent')
            target_pdb = st.selectbox("Select Structure", files, key="analysis_select")
            
            if target_pdb:
                target_path = st.session_state.current_project.get_full_path(target_pdb)
                
                if st.button("Run Full Analysis"):
                    with st.spinner("Analyzing..."):
                        # 1. Validation
                        st.markdown("#### 1. Validation Report")
                        val_res = validation_skills.validate_structure(target_path)
                        
                        if val_res["is_valid"]:
                            st.success("Structure is Valid (No breaks or clashes found).")
                        else:
                            st.error(f"Structure has issues! Clashes: {val_res['clash_count']}, Breaks: {len(val_res['backbone_breaks'])}")
                            
                        if val_res["clashes"]:
                            with st.expander("Clash Details"):
                                for c in val_res["clashes"]:
                                    st.write(f"- {c}")
                        if val_res["backbone_breaks"]:
                            with st.expander("Backbone Breaks"):
                                for b in val_res["backbone_breaks"]:
                                    st.write(f"- {b}")

                        # 2. SASA Calculation
                        st.markdown("#### 2. Solvent Accessible Surface Area (SASA)")
                        sasa_total = structure_skills.calculate_sasa(target_path)
                        
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("Total SASA", f"{sasa_total['total']:.2f} Å²")
                        col_b.metric("Polar SASA", f"{sasa_total['polar']:.2f} Å²")
                        col_c.metric("Apolar SASA", f"{sasa_total['apolar']:.2f} Å²")
                        
                        # 3. Residue Plot
                        st.markdown("#### 3. Residue Accessibility Profile")
                        res_sasa = structure_skills.get_residue_sasa(target_path)
                        
                        # Prepare data for plotting
                        # Sort by residue number if possible, but keys are strings like "A:10_ALA"
                        # We will just plot as is or try to sort
                        data_items = list(res_sasa.items())
                        # Basic sort attempt
                        try:
                            # Extract number from "A:10_ALA" -> 10
                            data_items.sort(key=lambda x: int(x[0].split(':')[1].split('_')[0]))
                        except:
                            pass # Fallback to default order
                        
                        df = pd.DataFrame(data_items, columns=["Residue", "SASA"])
                        
                        # Plotly Chart
                        fig = px.bar(
                            df, 
                            x="Residue", 
                            y="SASA", 
                            title="Residue Solvent Accessible Surface Area",
                            labels={"SASA": "SASA (Å²)"},
                            hover_data=["Residue", "SASA"]
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
        else:
            st.info("Select a project to run analysis.")

    with tab6:
        st.subheader("Sequence Mutagenesis & Analysis")
        seq_input = st.text_area("Input Amino Acid Sequence", "MKTIIALSYIFCLVFADYKDDDDK")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Analyze Sequence"):
                props = analysis_skills.analyze_sequence(seq_input)
                st.dataframe(props)
                
                comp = analysis_skills.get_amino_acid_percentages(seq_input)
                st.bar_chart(comp)
        
        with col2:
            st.markdown("#### Variant Generator")
            scan_type = st.selectbox("Scan Type", ["Alanine Scanning", "Saturation Mutagenesis"])
            
            sat_pos = 1
            if scan_type == "Saturation Mutagenesis":
                sat_pos = st.number_input("Position to mutate (1-based)", min_value=1, max_value=len(seq_input), value=1)
            
            if st.button("Generate & Analyze Variants"):
                variants = {}
                if scan_type == "Alanine Scanning":
                    variants = design_skills.generate_alanine_scan(seq_input)
                else:
                    variants = design_skills.generate_saturation_library(seq_input, sat_pos)
                
                st.write(f"Generated {len(variants)} variants.")
                
                # Analyze all variants
                results = []
                base_props = analysis_skills.analyze_sequence(seq_input)
                
                for name, var_seq in variants.items():
                    p = analysis_skills.analyze_sequence(var_seq)
                    row = {"Variant": name, "Sequence": var_seq}
                    # Calculate Deltas
                    row["d_MW"] = p["molecular_weight"] - base_props["molecular_weight"]
                    row["d_pI"] = p["isoelectric_point"] - base_props["isoelectric_point"]
                    row["d_Instability"] = p["instability_index"] - base_props["instability_index"]
                    results.append(row)
                
                df_res = pd.DataFrame(results)
                
                # Plotly Scatter Plot for Variants
                if not df_res.empty:
                    st.markdown("##### Variant Landscape")
                    fig_var = px.scatter(
                        df_res,
                        x="d_pI",
                        y="d_Instability",
                        color="d_MW",
                        hover_name="Variant",
                        hover_data=["Sequence"],
                        title="Variant Properties (Delta from Wild Type)",
                        labels={
                            "d_pI": "Δ Isoelectric Point",
                            "d_Instability": "Δ Instability Index",
                            "d_MW": "Δ Molecular Weight"
                        }
                    )
                    st.plotly_chart(fig_var, use_container_width=True)

                st.dataframe(df_res.style.background_gradient(subset=["d_pI", "d_Instability"], cmap="RdBu"))


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