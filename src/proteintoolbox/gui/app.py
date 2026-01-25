import streamlit as st
import os
import sys
import pandas as pd
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
        llm_provider = st.selectbox("Provider", ["openai", "anthropic", "gemini", "ollama"])
        
        provider_models = {
            "openai": ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini", "o3-mini", "gpt-4-turbo"],
            "anthropic": ["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest", "claude-3-opus-latest"],
            "gemini": ["gemini-2.0-flash-exp", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
            "ollama": ["llama3.3", "phi4", "mistral-small", "deepseek-r1", "llama3.1:8b"]
        }
        
        selected_model = st.selectbox("Model", provider_models[llm_provider] + ["Other..."])
        
        if selected_model == "Other...":
            llm_model = st.text_input("Custom Model Name")
        else:
            llm_model = selected_model
            
        llm_api_key = st.text_input("API Key", type="password", help="Leave empty if using env vars")
        llm_base_url = st.text_input("Base URL", value="http://localhost:11434" if llm_provider == "ollama" else "", help="Used for Ollama or custom endpoints")

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
    st.header("🛠️ Direct Tool Access")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Registry Browser", "Biological Data", "Simulation", "Design", "Analysis & Validation", "Mutagenesis & Analysis"])
    
    with tab1:
        st.subheader("Tool Registry & Skills")
        st.markdown("Database of available tools for agents and users.")
        
        tools = registry.list_tools()
        for i, t in enumerate(tools):
            with st.expander(f"{t.name} ({t.category})"):
                st.markdown(f"**Description:** {t.description}")
                st.markdown(f"**URL:** {t.url}")
                st.checkbox("Installed", value=t.installed, disabled=True, key=f"chk_{i}_{t.name}")

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
                        st.bar_chart(df, x="Residue", y="SASA")
                        
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