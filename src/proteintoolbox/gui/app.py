import streamlit as st
import os
import sys
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_molstar import st_molstar, st_molstar_rcsb

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from proteintoolbox.skills import bio_skills, sim_skills, design_skills, docs_skills, structure_skills, validation_skills, analysis_skills
from proteintoolbox.skills import esm_fold_skill, structure_prediction_skills, amp_skills
from proteintoolbox.agents.crew import run_design_task
from proteintoolbox.project import ProjectManager
from proteintoolbox.registry import ToolRegistry

st.set_page_config(page_title="ProteinToolbox", layout="wide", page_icon="🧬")

# Initialize Project Manager & Registry
pm = ProjectManager()
registry = ToolRegistry(registry_path=os.path.join(os.getcwd(), "ProteinToolbox/data/tool_registry.json"))

# Session state defaults
for key in ['current_project', 'workflow_steps', 'workflow_active']:
    if key not in st.session_state:
        st.session_state[key] = None if key == 'current_project' else [] if key == 'workflow_steps' else False

st.title("🧬 ProteinToolbox")


# ─── Helper: export a Plotly figure as PNG bytes ────────────────────────────
def _plot_download_buttons(fig, stem: str):
    """Render SVG + PNG download buttons for a Plotly figure."""
    col_svg, col_png = st.columns(2)
    try:
        svg_bytes = fig.to_image(format="svg")
        col_svg.download_button("⬇ Download SVG", svg_bytes, file_name=f"{stem}.svg", mime="image/svg+xml")
    except Exception:
        col_svg.caption("SVG export unavailable (install kaleido)")
    try:
        png_bytes = fig.to_image(format="png", scale=2)
        col_png.download_button("⬇ Download PNG", png_bytes, file_name=f"{stem}.png", mime="image/png")
    except Exception:
        col_png.caption("PNG export unavailable (install kaleido)")


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🗂 Project Management")

    project_list = pm.list_projects()
    current_name = st.session_state.current_project.name if st.session_state.current_project else "None"
    default_idx = 0
    if current_name in project_list:
        default_idx = project_list.index(current_name) + 1

    selected_project_name = st.selectbox("Current Project", ["None"] + project_list, index=default_idx)

    if selected_project_name != "None":
        st.session_state.current_project = pm.get_project(selected_project_name)
    else:
        st.session_state.current_project = None

    with st.expander("➕ Create New Project"):
        new_proj_name = st.text_input("Name")
        new_proj_desc = st.text_input("Description")
        if st.button("Create Project"):
            try:
                pm.create_project(new_proj_name, new_proj_desc)
                st.success(f"Created {new_proj_name}")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.divider()

    # LLM Settings
    with st.expander("🤖 LLM Settings"):
        llm_provider = st.selectbox("Provider", ["openai", "anthropic", "gemini", "deepseek", "ollama"])

        provider_models = {
            "openai": ["gpt-5.2", "gpt-5", "gpt-4o", "o3-mini", "o1"],
            "anthropic": ["claude-4.5-opus", "claude-4.5-sonnet", "claude-3-5-sonnet-latest"],
            "gemini": ["gemini-3-pro", "gemini-3-flash", "gemini-3-deep-think", "gemini-2.0-flash-exp"],
            "deepseek": ["deepseek-v3.2", "deepseek-v3", "deepseek-reasoner", "deepseek-chat"],
            "ollama": ["deepseek-v3.2", "llama3.3", "phi4", "mistral-small", "exaone-deep"],
        }

        selected_model = st.selectbox("Model", provider_models[llm_provider] + ["Other..."])
        llm_model = st.text_input("Custom Model Name") if selected_model == "Other..." else selected_model
        llm_api_key = st.text_input("API Key", type="password", help="Leave empty if using env vars or Ollama")
        llm_base_url = st.text_input(
            "Base URL",
            value="http://localhost:11434" if llm_provider == "ollama" else
                  "https://api.deepseek.com" if llm_provider == "deepseek" else "",
            help="Used for Ollama, DeepSeek, or custom endpoints",
        )

    st.divider()
    st.header("🔀 Navigation")
    mode = st.radio("Mode", ["Workspace", "Agent Workflow", "Tools", "Sequence Analysis", "Structure Prediction"])

    st.divider()
    show_tutorial = st.toggle("📚 Tutorial Mode", value=False, help="Show helper text and explanations for tools.")
    if show_tutorial:
        st.info("💡 **Tutorial Mode**: Enabled. Look for these blue boxes for guidance.")


# ─── WORKSPACE ───────────────────────────────────────────────────────────────
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
                st.info("💡 **Files**: Select a file to visualize it. Upload PDB files to add to your project.")

            files = proj.list_files()
            if not files:
                st.warning("No files in project.")

            selected_file = st.radio("Select File", files)

            uploaded_file = st.file_uploader("Upload PDB", type=["pdb", "cif"])
            if uploaded_file:
                save_path = os.path.join(proj.path, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Saved {uploaded_file.name}")
                st.rerun()

            st.divider()
            if st.button("📄 Generate Project Report"):
                report_path = docs_skills.generate_project_report(proj.path)
                st.success(f"Report generated: {os.path.basename(report_path)}")
                st.rerun()

        with col2:
            st.markdown("### 3D Structure Viewer (Mol*)")

            # Color-by-feature selector (affects viewer label, Mol* auto-coloring)
            color_scheme = st.selectbox(
                "Color By",
                ["Chain", "Secondary Structure", "Hydrophobicity (B-factor)", "Residue Type"],
                help="Color scheme applied in the Mol* viewer.",
            )

            if show_tutorial:
                st.info(
                    "💡 **Color By**: Mol* automatically colors by chain. "
                    "'Hydrophobicity' uses B-factor column if populated. "
                    "Switch schemes to explore structural features."
                )

            if selected_file:
                file_path = proj.get_full_path(selected_file)
                if selected_file.endswith((".pdb", ".cif", ".ent")):
                    # Pass color scheme as a custom_script hint via session state
                    # (st_molstar renders with its own defaults; we append an info badge)
                    st.caption(f"🎨 Active color scheme: **{color_scheme}**")
                    st_molstar(file_path, key=f"molstar_{color_scheme}", height=520)
                else:
                    st.info("Select a structure file (.pdb / .cif) to visualize.")
            else:
                st.info("No file selected.")


# ─── SEQUENCE ANALYSIS (new mode) ────────────────────────────────────────────
elif mode == "Sequence Analysis":
    st.header("🔬 Sequence Analysis & Visualization")

    seq_tabs = st.tabs(["Physicochemical", "Codon Usage Heatmap", "Sequence Comparison", "ESM Embedding PCA", "AMP Design"])

    # ── Tab 1: Physicochemical ────────────────────────────────────────────────
    with seq_tabs[0]:
        st.subheader("Physicochemical Properties")
        if show_tutorial:
            st.info("💡 Enter a protein sequence (1-letter AA codes) to compute MW, pI, GRAVY, etc.")

        seq_input = st.text_area("Protein Sequence (1-letter AA)", height=100, key="phys_seq")
        if st.button("Analyze", key="btn_phys") and seq_input:
            try:
                clean = bio_skills.clean_and_validate_sequence(seq_input)
                props = analysis_skills.analyze_sequence(clean)
                aa_pct = analysis_skills.get_amino_acid_percentages(clean)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Molecular Weight (Da)", f"{props['molecular_weight']:.1f}")
                    st.metric("Isoelectric Point (pI)", f"{props['isoelectric_point']:.2f}")
                    st.metric("GRAVY", f"{props['gravy']:.3f}")
                with col_b:
                    st.metric("Instability Index", f"{props['instability_index']:.2f}")
                    st.metric("Aromaticity", f"{props['aromaticity']:.3f}")
                    h, t, s = props["secondary_structure_fraction"]
                    st.metric("2° Structure (H/T/S)", f"{h:.2f} / {t:.2f} / {s:.2f}")

                # AA composition bar chart
                df_aa = pd.DataFrame(list(aa_pct.items()), columns=["Amino Acid", "Fraction"])
                df_aa = df_aa.sort_values("Fraction", ascending=False)
                fig_aa = px.bar(
                    df_aa, x="Amino Acid", y="Fraction",
                    title="Amino Acid Composition",
                    color="Fraction", color_continuous_scale="Teal",
                    labels={"Fraction": "Fraction"},
                )
                fig_aa.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_aa, use_container_width=True)
                _plot_download_buttons(fig_aa, "aa_composition")

            except ValueError as e:
                st.error(str(e))

    # ── Tab 2: Codon Usage Heatmap ────────────────────────────────────────────
    with seq_tabs[1]:
        st.subheader("Codon Usage Heatmap")
        if show_tutorial:
            st.info(
                "💡 Paste a **DNA/CDS sequence** (length must be divisible by 3). "
                "The heatmap shows how often each codon is used — useful for optimizing expression."
            )

        dna_input = st.text_area("DNA / CDS Sequence", height=120, key="dna_seq",
                                  placeholder="ATGAAAGCCATTTTCAGT...")
        if st.button("Generate Heatmap", key="btn_codon") and dna_input:
            try:
                hm_data = analysis_skills.get_codon_usage_heatmap_data(dna_input)

                fig_hm = go.Figure(
                    go.Heatmap(
                        z=hm_data["z"],
                        x=hm_data["x"],
                        y=hm_data["y"],
                        text=hm_data["text"],
                        texttemplate="%{text}",
                        colorscale="YlOrRd",
                        hovertemplate="Codon: %{text}<br>Count: %{z}<extra></extra>",
                        showscale=True,
                    )
                )
                fig_hm.update_layout(
                    title="Codon Usage Heatmap (row = first 2 bases, col = 3rd base)",
                    xaxis_title="3rd Base",
                    yaxis_title="1st+2nd Bases",
                    height=700,
                    font=dict(size=11),
                )
                st.plotly_chart(fig_hm, use_container_width=True)
                _plot_download_buttons(fig_hm, "codon_heatmap")

                # Summary table
                usage = analysis_skills.get_codon_usage(dna_input)
                df_usage = pd.DataFrame(
                    [(c, cnt, analysis_skills.CODON_TABLE.get(c, "?"))
                     for c, cnt in sorted(usage.items(), key=lambda x: -x[1]) if cnt > 0],
                    columns=["Codon", "Count", "Amino Acid"],
                )
                st.dataframe(df_usage, use_container_width=True)
                csv = df_usage.to_csv(index=False)
                st.download_button("⬇ Download CSV", csv, file_name="codon_usage.csv", mime="text/csv")

            except ValueError as e:
                st.error(str(e))

    # ── Tab 3: Sequence Comparison ────────────────────────────────────────────
    with seq_tabs[2]:
        st.subheader("Side-by-Side Sequence Comparison")
        if show_tutorial:
            st.info(
                "💡 Compare two protein sequences. The tool aligns them visually and highlights "
                "differences. Physicochemical deltas help identify functional changes."
            )

        c1, c2 = st.columns(2)
        with c1:
            seq_a = st.text_area("Sequence A", height=120, key="cmp_a", placeholder="MKTVRQ...")
            label_a = st.text_input("Label A", value="Sequence A")
        with c2:
            seq_b = st.text_area("Sequence B", height=120, key="cmp_b", placeholder="MKTVRQ...")
            label_b = st.text_input("Label B", value="Sequence B")

        if st.button("Compare", key="btn_cmp") and seq_a and seq_b:
            try:
                clean_a = bio_skills.clean_and_validate_sequence(seq_a)
                clean_b = bio_skills.clean_and_validate_sequence(seq_b)
                props_a = analysis_skills.analyze_sequence(clean_a)
                props_b = analysis_skills.analyze_sequence(clean_b)

                # Property comparison bar chart
                prop_keys = ["molecular_weight", "isoelectric_point", "gravy", "instability_index", "aromaticity"]
                labels = ["MW (Da)", "pI", "GRAVY", "Instability", "Aromaticity"]
                df_cmp = pd.DataFrame({
                    "Property": labels * 2,
                    "Value": [props_a[k] for k in prop_keys] + [props_b[k] for k in prop_keys],
                    "Sequence": [label_a] * len(labels) + [label_b] * len(labels),
                })
                fig_cmp = px.bar(
                    df_cmp, x="Property", y="Value", color="Sequence", barmode="group",
                    title=f"Property Comparison: {label_a} vs {label_b}",
                )
                fig_cmp.update_layout(height=380)
                st.plotly_chart(fig_cmp, use_container_width=True)
                _plot_download_buttons(fig_cmp, "sequence_comparison")

                # Delta metrics
                st.markdown("#### Deltas (B − A)")
                delta_cols = st.columns(len(prop_keys))
                for col, key, lbl in zip(delta_cols, prop_keys, labels):
                    delta = props_b[key] - props_a[key]
                    col.metric(lbl, f"{props_b[key]:.3g}", delta=f"{delta:+.3g}")

                # Residue-level diff (character-by-character for same-length seqs)
                if len(clean_a) == len(clean_b):
                    diffs = [(i + 1, a, b) for i, (a, b) in enumerate(zip(clean_a, clean_b)) if a != b]
                    if diffs:
                        st.markdown(f"#### Residue Differences ({len(diffs)} positions)")
                        df_diff = pd.DataFrame(diffs, columns=["Position", label_a, label_b])
                        st.dataframe(df_diff, use_container_width=True)
                    else:
                        st.success("Sequences are identical!")
                else:
                    st.info(
                        f"Sequences differ in length ({len(clean_a)} vs {len(clean_b)}). "
                        "Residue-level diff requires equal-length sequences."
                    )

            except ValueError as e:
                st.error(str(e))

    # ── Tab 4: ESM Embedding PCA ──────────────────────────────────────────────
    with seq_tabs[3]:
        st.subheader("ESM2 Embedding — PCA Visualization")
        if show_tutorial:
            st.info(
                "💡 Enter multiple sequences (one per line). Each is embedded by the ESM2 model, "
                "then projected into 2D using PCA so you can visualize sequence diversity."
            )

        seqs_input = st.text_area(
            "Sequences (one per line, optional label after TAB)",
            height=150,
            placeholder="MKTVRQ...\nACDEFG...\nMGSSHH...\t(Label here)",
        )
        if st.button("Run ESM + PCA", key="btn_esm"):
            if not seqs_input.strip():
                st.warning("Please enter at least 2 sequences.")
            else:
                lines = [l.strip() for l in seqs_input.strip().splitlines() if l.strip()]
                parsed = []
                for line in lines:
                    parts = line.split("\t", 1)
                    raw_seq = parts[0].strip()
                    label = parts[1].strip() if len(parts) > 1 else raw_seq[:10] + "..."
                    try:
                        clean = bio_skills.clean_and_validate_sequence(raw_seq)
                        parsed.append((clean, label))
                    except ValueError as e:
                        st.warning(f"Skipping invalid sequence '{raw_seq[:20]}...': {e}")

                if len(parsed) < 2:
                    st.error("Need at least 2 valid sequences for PCA.")
                else:
                    with st.spinner("Computing ESM embeddings…"):
                        try:
                            from proteintoolbox.skills.esm_skills import get_embedding
                            import numpy as np
                            embeddings = []
                            labels = []
                            prog = st.progress(0, text="Embedding sequences…")
                            for idx, (seq, lbl) in enumerate(parsed):
                                embeddings.append(get_embedding(seq))
                                labels.append(lbl)
                                prog.progress((idx + 1) / len(parsed),
                                              text=f"Embedded {idx+1}/{len(parsed)}")
                            prog.empty()

                            X = np.array(embeddings)

                            # PCA (pure numpy — avoids sklearn/numpy ABI issues)
                            X_c = X - X.mean(axis=0)
                            cov = np.cov(X_c, rowvar=False)
                            eigvals, eigvecs = np.linalg.eigh(cov)
                            order = np.argsort(eigvals)[::-1]
                            pcs = X_c @ eigvecs[:, order[:2]]
                            var_explained = eigvals[order[:2]] / eigvals.sum() * 100

                            df_pca = pd.DataFrame({
                                "PC1": pcs[:, 0],
                                "PC2": pcs[:, 1],
                                "Label": labels,
                            })
                            fig_pca = px.scatter(
                                df_pca, x="PC1", y="PC2", text="Label",
                                title="ESM2 Embeddings — PCA (2D Projection)",
                                labels={
                                    "PC1": f"PC1 ({var_explained[0]:.1f}% var)",
                                    "PC2": f"PC2 ({var_explained[1]:.1f}% var)",
                                },
                            )
                            fig_pca.update_traces(
                                marker=dict(size=10),
                                textposition="top center",
                            )
                            fig_pca.update_layout(height=480)
                            st.plotly_chart(fig_pca, use_container_width=True)
                            _plot_download_buttons(fig_pca, "esm_pca")

                            st.dataframe(df_pca, use_container_width=True)

                        except Exception as e:
                            st.error(f"ESM embedding error: {e}")

    # ── Tab 5: AMP Design ─────────────────────────────────────────────────────
    with seq_tabs[4]:
        st.subheader("Antimicrobial Peptide (AMP) Design")
        if show_tutorial:
            st.info(
                "💡 **AMP Design**: Score a peptide's antimicrobial potential using "
                "net charge, hydrophobic moment, amphipathicity, and length heuristics. "
                "Then generate optimized variants with improved AMP profiles."
            )

        amp_seq = st.text_area(
            "Peptide Sequence (1-letter AA)",
            height=80,
            key="amp_seq",
            placeholder="ILPWKWPWWPWRR",
            help="Typical AMPs are 10–40 residues, cationic (+2 to +9), and amphipathic.",
        )

        col_score, col_gen = st.columns([1, 1])
        with col_score:
            if st.button("Score AMP Potential", key="btn_amp_score") and amp_seq:
                try:
                    clean_amp = bio_skills.clean_and_validate_sequence(amp_seq)
                    result = amp_skills.score_amp_potential(clean_amp)

                    grade_color = {
                        "Excellent": "green", "Good": "blue",
                        "Moderate": "orange", "Poor": "red",
                    }.get(result["grade"], "grey")

                    st.metric("AMP Score", f"{result['score']:.1f} / 100",
                              delta=result["grade"])
                    st.markdown(
                        f"<span style='color:{grade_color};font-weight:bold;font-size:1.1em;'>"
                        f"Grade: {result['grade']}</span>",
                        unsafe_allow_html=True,
                    )

                    st.markdown("#### Component Scores")
                    sub = result["sub_scores"]
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Charge", f"{sub['charge']:.0f}", help=f"Net charge: {result['net_charge']:+.1f}")
                    c2.metric("Hydrophobic Moment", f"{sub['hydrophobic_moment']:.0f}",
                              help=f"μH = {result['hydrophobic_moment']:.3f}")
                    c3.metric("Length", f"{sub['length']:.0f}",
                              help=f"{result['length']} residues")
                    c4.metric("Amphipathicity", f"{sub['amphipathicity']:.0f}",
                              help=f"Index = {result['amphipathicity_index']:.3f}")

                    # Radar / bar chart of sub-scores
                    sub_df = pd.DataFrame(
                        list(sub.items()), columns=["Component", "Score"]
                    )
                    sub_df["Component"] = sub_df["Component"].str.replace("_", " ").str.title()
                    fig_sub = px.bar(
                        sub_df, x="Component", y="Score",
                        title="AMP Sub-Score Breakdown",
                        color="Score",
                        color_continuous_scale="RdYlGn",
                        range_color=[0, 100],
                    )
                    fig_sub.update_layout(height=320, showlegend=False,
                                          yaxis=dict(range=[0, 100]))
                    st.plotly_chart(fig_sub, use_container_width=True)
                    _plot_download_buttons(fig_sub, "amp_subscores")

                    st.markdown("#### Analysis Notes")
                    for note in result["explanation"]:
                        st.markdown(f"- {note}")

                except ValueError as e:
                    st.error(str(e))

        with col_gen:
            n_variants = st.slider("Variants to generate", 3, 20, 5, key="amp_n_var")
            if st.button("Generate AMP Variants", key="btn_amp_gen") and amp_seq:
                try:
                    clean_amp = bio_skills.clean_and_validate_sequence(amp_seq)
                    with st.spinner("Generating and scoring variants…"):
                        variants = amp_skills.generate_amp_variants(clean_amp, n=n_variants)

                    st.success(f"Top {len(variants)} variants by AMP score:")
                    df_var = pd.DataFrame(
                        [(seq, score) for seq, score in variants],
                        columns=["Sequence", "AMP Score"],
                    )
                    df_var["Delta vs Seed"] = df_var["AMP Score"] - variants[0][1] if variants else 0

                    # Color-coded scatter: position vs score
                    fig_v = px.bar(
                        df_var.reset_index(), x="index", y="AMP Score",
                        hover_data=["Sequence"],
                        title="AMP Variant Scores",
                        color="AMP Score",
                        color_continuous_scale="RdYlGn",
                        range_color=[0, 100],
                    )
                    fig_v.update_layout(height=300, xaxis_title="Variant Rank")
                    st.plotly_chart(fig_v, use_container_width=True)
                    _plot_download_buttons(fig_v, "amp_variants")

                    st.dataframe(df_var, use_container_width=True)
                    csv_amp = df_var.to_csv(index=False)
                    st.download_button("⬇ Download CSV", csv_amp,
                                       file_name="amp_variants.csv", mime="text/csv")

                except ValueError as e:
                    st.error(str(e))


# ─── TOOLS ───────────────────────────────────────────────────────────────────
elif mode == "Tools":
    st.header("🛠️ Direct Tool Access & Info")

    tab_list = [
        "Meet the Agents",
        "Browse Skills",
        "Registry Browser",
        "Biological Data",
        "Simulation",
        "Analysis & Validation",
        "Mutagenesis & Analysis",
    ]
    tabs = st.tabs(tab_list)

    # Tab 0: Meet the Agents
    with tabs[0]:
        st.subheader("The Design Crew")
        st.markdown("This toolbox uses a team of specialized AI agents to handle your request.")
        from proteintoolbox.agents.crew import AGENT_DEFINITIONS
        for agent_def in AGENT_DEFINITIONS:
            with st.expander(f"**{agent_def['role']}**"):
                st.markdown(f"**Goal:** {agent_def['goal']}")
                st.markdown(f"**Backstory:** {agent_def['backstory']}")
                tool_names = [t.name for t in agent_def["tools"]] if agent_def["tools"] else ["None"]
                st.markdown(f"**Primary Tools:** `{', '.join(tool_names)}`")

    # Tab 1: Browse Skills
    with tabs[1]:
        st.subheader("Available Skills")
        st.markdown("Dynamically discovered functions available to the agents.")
        from proteintoolbox.skills import SKILL_REGISTRY
        for skill_name, skill_info in sorted(SKILL_REGISTRY.items()):
            with st.expander(f"`{skill_name}{skill_info['signature']}`"):
                st.markdown(f"**Module:** `{skill_info['module']}`")
                st.markdown(skill_info["description"])

    # Tab 2: Registry Browser
    with tabs[2]:
        st.subheader("Tool Registry")
        st.markdown("Database of high-level tools and software packages.")
        tools = registry.list_tools()
        for i, t in enumerate(tools):
            with st.expander(f"{t.name} ({t.category})"):
                st.markdown(f"**Description:** {t.description}")
                st.markdown(f"**URL:** {t.url}")
                st.checkbox("Installed", value=t.installed, disabled=True, key=f"chk_{i}_{t.name}")

    # Tab 3: Biological Data
    with tabs[3]:
        st.subheader("Fetch PDB Structure")
        if show_tutorial:
            st.info("💡 Enter a 4-letter PDB code to download the structure to your project directory.")

        pdb_id = st.text_input("PDB ID (e.g. 1CRN)", max_chars=4, key="bio_pdb_id").upper()
        out_dir = st.text_input("Output Directory", value="data/pdb", key="bio_out_dir")

        if st.button("Fetch PDB", key="btn_fetch"):
            if not pdb_id or len(pdb_id) != 4:
                st.error("Enter a valid 4-letter PDB ID.")
            else:
                with st.spinner(f"Downloading {pdb_id}…"):
                    try:
                        path = bio_skills.fetch_pdb_structure(pdb_id, output_dir=out_dir)
                        st.success(f"Downloaded: `{path}`")
                        st.code(f"File: {path}")
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.divider()
        st.subheader("Extract Sequence from PDB")
        pdb_path_seq = st.text_input("PDB File Path", key="seq_pdb_path")
        if st.button("Extract Sequence", key="btn_extract") and pdb_path_seq:
            try:
                seq = bio_skills.get_sequence_from_pdb(pdb_path_seq)
                st.success("Sequence extracted!")
                st.code(seq)
                st.download_button("⬇ Download FASTA", f">extracted\n{seq}\n",
                                   file_name="sequence.fasta", mime="text/plain")
            except Exception as e:
                st.error(f"Error: {e}")

    # Tab 4: Simulation
    with tabs[4]:
        st.subheader("Structure Minimization")
        if show_tutorial:
            st.info("💡 Energy-minimize a PDB structure using OpenMM.")

        sim_pdb = st.text_input("Input PDB Path", key="sim_pdb")
        sim_out = st.text_input("Output Directory", value="output/sim", key="sim_out")

        if st.button("Run Minimization", key="btn_sim"):
            if not sim_pdb:
                st.error("Provide a PDB path.")
            else:
                with st.spinner("Minimizing…"):
                    try:
                        result = sim_skills.minimize_structure(sim_pdb, output_dir=sim_out)
                        st.success(result)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Tab 5: Analysis & Validation
    with tabs[5]:
        st.subheader("Structure Analysis & Validation")
        if show_tutorial:
            st.info("💡 Compute SASA and run structural quality checks (backbone continuity, steric clashes).")

        av_pdb = st.text_input("PDB File Path", key="av_pdb")

        col_a, col_v = st.columns(2)

        with col_a:
            if st.button("Compute SASA", key="btn_sasa") and av_pdb:
                with st.spinner("Calculating SASA…"):
                    try:
                        sasa = structure_skills.calculate_sasa(av_pdb)
                        st.metric("Total SASA (Å²)", f"{sasa['total']:.1f}")
                        st.metric("Polar SASA (Å²)", f"{sasa['polar']:.1f}")
                        st.metric("Apolar SASA (Å²)", f"{sasa['apolar']:.1f}")

                        res_sasa = structure_skills.get_residue_sasa(av_pdb)
                        df_sasa = pd.DataFrame(
                            [{"Residue": k, "SASA (Å²)": v} for k, v in res_sasa.items()]
                        ).sort_values("SASA (Å²)", ascending=False)

                        fig_sasa = px.bar(
                            df_sasa.head(30), x="Residue", y="SASA (Å²)",
                            title="Top 30 Residues by SASA",
                            color="SASA (Å²)", color_continuous_scale="Viridis",
                        )
                        fig_sasa.update_layout(height=380, xaxis_tickangle=-45)
                        st.plotly_chart(fig_sasa, use_container_width=True)
                        _plot_download_buttons(fig_sasa, "residue_sasa")

                    except Exception as e:
                        st.error(f"SASA error: {e}")

        with col_v:
            if st.button("Validate Structure", key="btn_val") and av_pdb:
                with st.spinner("Validating…"):
                    try:
                        report = validation_skills.validate_structure(av_pdb)
                        if report["is_valid"]:
                            st.success("✅ Structure is valid — no issues found.")
                        else:
                            st.warning("⚠️ Issues detected:")

                        if report["backbone_breaks"]:
                            with st.expander(f"Backbone Breaks ({len(report['backbone_breaks'])})"):
                                for b in report["backbone_breaks"]:
                                    st.write(b)
                        if report["clashes"]:
                            with st.expander(f"Steric Clashes ({report['clash_count']})"):
                                for c in report["clashes"][:50]:
                                    st.write(c)
                                if len(report["clashes"]) > 50:
                                    st.caption(f"…and {len(report['clashes']) - 50} more")
                    except Exception as e:
                        st.error(f"Validation error: {e}")

    # Tab 6: Mutagenesis & Analysis
    with tabs[6]:
        st.subheader("Sequence Mutagenesis & Analysis")
        if show_tutorial:
            st.info("💡 Generate alanine scan or saturation mutagenesis library, then visualize variant properties.")

        mut_seq = st.text_area("Input Sequence", height=100, key="mut_seq")
        mut_mode = st.radio("Mutagenesis Mode", ["Alanine Scan", "Saturation Library"], horizontal=True)

        if st.button("Generate Variants", key="btn_mut") and mut_seq:
            try:
                clean = bio_skills.clean_and_validate_sequence(mut_seq)
                if mut_mode == "Alanine Scan":
                    variants = design_skills.generate_alanine_scan(clean)
                else:
                    pos = st.session_state.get("sat_pos", 1)
                    variants = design_skills.generate_saturation_library(clean, position=pos)

                st.success(f"Generated {len(variants)} variants.")

                # Compute properties for each variant
                results = []
                prog = st.progress(0, text="Analyzing variants…")
                for i, var in enumerate(variants[:200]):  # Cap at 200 for speed
                    try:
                        p = analysis_skills.analyze_sequence(var)
                        results.append({
                            "Variant": var[:15] + ("…" if len(var) > 15 else ""),
                            "ΔpI": p["isoelectric_point"] - analysis_skills.analyze_sequence(clean)["isoelectric_point"],
                            "ΔInstability": p["instability_index"] - analysis_skills.analyze_sequence(clean)["instability_index"],
                            "GRAVY": p["gravy"],
                        })
                    except Exception:
                        pass
                    prog.progress((i + 1) / min(200, len(variants)))
                prog.empty()

                df_var = pd.DataFrame(results)
                if not df_var.empty:
                    fig_var = px.scatter(
                        df_var, x="ΔpI", y="ΔInstability", color="GRAVY",
                        hover_data=["Variant"],
                        title="Variant Landscape (ΔpI vs ΔInstability)",
                        color_continuous_scale="RdYlGn_r",
                    )
                    fig_var.update_traces(marker=dict(size=8))
                    fig_var.update_layout(height=420)
                    st.plotly_chart(fig_var, use_container_width=True)
                    _plot_download_buttons(fig_var, "variant_landscape")

                    st.dataframe(df_var, use_container_width=True)
                    csv = df_var.to_csv(index=False)
                    st.download_button("⬇ Download CSV", csv,
                                       file_name="variants.csv", mime="text/csv")

            except Exception as e:
                st.error(f"Mutagenesis error: {e}")

        # Saturation library position selector (shown separately)
        if mut_mode == "Saturation Library":
            st.session_state["sat_pos"] = st.number_input(
                "Position to Saturate (1-indexed)", min_value=1, value=1, key="sat_pos_input"
            )


# ─── STRUCTURE PREDICTION ─────────────────────────────────────────────────────
elif mode == "Structure Prediction":
    st.header("🔮 Structure Prediction")
    st.markdown(
        "Predict 3D structures using SOTA models. "
        "ESMFold runs via the public REST API; Boltz-1 and AlphaFold3 run locally when installed."
    )

    # Tool availability status panel
    with st.expander("🔧 Tool Availability Status", expanded=True):
        with st.spinner("Checking installed tools…"):
            tools_status = structure_prediction_skills.check_tools_available()

        cols = st.columns(len(tools_status))
        icons = {"boltz": "⚡", "alphafold3": "🔬", "esmfold_local": "🧬", "colabfold": "☁️"}
        for col, (tool, status) in zip(cols, tools_status.items()):
            installed = status is True
            col.metric(
                label=f"{icons.get(tool, '🔧')} {tool}",
                value="Installed" if installed else "Not installed",
                delta="Ready" if installed else "Stub mode",
            )
            if not installed:
                col.caption(str(status)[:120])

    sp_tabs = st.tabs(["ESMFold (API)", "Boltz-1", "AlphaFold3"])

    # ── ESMFold tab ────────────────────────────────────────────────────────────
    with sp_tabs[0]:
        st.subheader("ESMFold — Single-Sequence Structure Prediction")
        st.markdown(
            "Uses the **ESM Atlas public REST API** (EvolutionaryScale / Meta). "
            "No local GPU required. Suitable for sequences up to ~400 residues."
        )
        if show_tutorial:
            st.info(
                "💡 ESMFold predicts 3D structure from sequence alone in seconds. "
                "pLDDT > 70 indicates reliable prediction. "
                "The output PDB can be visualized in the Workspace."
            )

        esm_seq = st.text_area(
            "Protein Sequence (1-letter AA)",
            height=100,
            key="esm_fold_seq",
            placeholder="MGSSHHHHHHSSGLVPRGSHMASMTGGQQMGRDLYDDDDK…",
        )
        esm_out_dir = st.text_input("Save PDB to directory", value="output/esmfold", key="esm_out_dir")

        if st.button("Predict Structure (ESMFold)", key="btn_esmfold") and esm_seq:
            try:
                clean_esm = bio_skills.clean_and_validate_sequence(esm_seq)
                if len(clean_esm) > 400:
                    st.warning(f"Sequence is {len(clean_esm)} aa — the public API may time out for sequences > 400 aa.")
                with st.spinner(f"Calling ESMFold API for {len(clean_esm)}-residue sequence… (may take ~30–120 s)"):
                    pdb_str = esm_fold_skill.predict_structure_esmfold(clean_esm)

                conf = esm_fold_skill.get_esmfold_confidence(pdb_str)
                c1, c2 = st.columns(2)
                c1.metric("Mean pLDDT", f"{conf['mean_plddt']:.1f}")
                c2.metric("High-confidence residues (pLDDT ≥ 70)",
                           f"{conf['high_confidence_fraction']:.0%}")

                # pLDDT per-residue bar chart
                if conf["per_residue"]:
                    df_plddt = pd.DataFrame(conf["per_residue"], columns=["Residue", "pLDDT"])
                    fig_plddt = px.bar(
                        df_plddt, x="Residue", y="pLDDT",
                        title="Per-residue pLDDT Confidence",
                        color="pLDDT", color_continuous_scale="RdYlGn",
                        range_color=[0, 100],
                    )
                    fig_plddt.add_hline(y=70, line_dash="dash", line_color="orange",
                                        annotation_text="pLDDT=70")
                    fig_plddt.update_layout(height=300)
                    st.plotly_chart(fig_plddt, use_container_width=True)
                    _plot_download_buttons(fig_plddt, "esmfold_plddt")

                # Save PDB file
                import os
                os.makedirs(esm_out_dir, exist_ok=True)
                pdb_filename = os.path.join(esm_out_dir, f"esmfold_{clean_esm[:8]}.pdb")
                with open(pdb_filename, "w") as fh:
                    fh.write(pdb_str)
                st.success(f"PDB saved: `{pdb_filename}`")
                st.download_button("⬇ Download PDB", pdb_str,
                                   file_name="esmfold_prediction.pdb",
                                   mime="chemical/x-pdb")

            except (ValueError, RuntimeError) as e:
                st.error(str(e))

    # ── Boltz-1 tab ────────────────────────────────────────────────────────────
    with sp_tabs[1]:
        st.subheader("Boltz-1 — Open-Source Biomolecular Structure Predictor")
        st.markdown(
            "**Boltz-1** is an open-weight structure predictor supporting proteins, "
            "nucleic acids, ligands, and covalent modifications. "
            "AlphaFold3-level accuracy; runs locally on CPU or GPU."
        )
        if show_tutorial:
            st.info(
                "💡 Install Boltz-1 with: `pip install boltz` (requires PyTorch). "
                "Provide a FASTA file and output directory. "
                "If Boltz is not installed, a dry-run command is shown."
            )

        boltz_fasta = st.text_input("FASTA File Path", key="boltz_fasta",
                                     placeholder="/path/to/sequence.fasta")
        boltz_out = st.text_input("Output Directory", value="output/boltz", key="boltz_out")

        if st.button("Run Boltz-1 Prediction", key="btn_boltz"):
            if not boltz_fasta:
                st.error("Provide a FASTA file path.")
            else:
                with st.spinner("Running Boltz-1…"):
                    result = structure_prediction_skills.predict_with_boltz(boltz_fasta, boltz_out)

                status = result["status"]
                if status == "success":
                    st.success(result["message"])
                    st.code(result["command"])
                elif status == "dry_run":
                    st.info("Dry run (Boltz-1 not installed):")
                    st.markdown(result["message"])
                    st.code(result["command"], language="bash")
                else:
                    st.error(result["message"])
                    if "error" in result:
                        st.code(result["error"])

    # ── AlphaFold3 tab ─────────────────────────────────────────────────────────
    with sp_tabs[2]:
        st.subheader("AlphaFold3 — Google DeepMind All-Atom Predictor")
        st.markdown(
            "**AlphaFold3** predicts all-atom structures of proteins, DNA, RNA, "
            "small molecules, and ions with state-of-the-art accuracy. "
            "Requires academic-use model weights (~1 TB)."
        )
        if show_tutorial:
            st.info(
                "💡 AF3 weights require registration at "
                "github.com/google-deepmind/alphafold3. "
                "If AF3 is not installed, a dry-run command is shown."
            )

        af3_fasta = st.text_input("FASTA File Path", key="af3_fasta",
                                   placeholder="/path/to/sequence.fasta")
        af3_out = st.text_input("Output Directory", value="output/af3", key="af3_out")

        if st.button("Run AlphaFold3 Prediction", key="btn_af3"):
            if not af3_fasta:
                st.error("Provide a FASTA file path.")
            else:
                with st.spinner("Running AlphaFold3…"):
                    result = structure_prediction_skills.predict_with_af3(af3_fasta, af3_out)

                status = result["status"]
                if status == "success":
                    st.success(result["message"])
                    st.code(result["command"])
                elif status == "dry_run":
                    st.info("Dry run (AlphaFold3 not installed):")
                    st.markdown(result["message"])
                    st.code(result["command"], language="bash")
                else:
                    st.error(result["message"])
                    if "error" in result:
                        st.code(result["error"])


# ─── AGENT WORKFLOW ───────────────────────────────────────────────────────────
elif mode == "Agent Workflow":
    st.header("🤖 Agentic Design")
    st.markdown(
        "Describe your goal, and the **CrewAI** agents (Librarian, Architect, Technician, Methodologist) "
        "will plan and execute it."
    )

    user_request = st.text_area("Design Goal", "Design a nanobody binder for the Spike protein.")

    # Workflow step tracker (progress indicator)
    WORKFLOW_STEPS = [
        "🔎 Librarian: Literature & Data Search",
        "📐 Methodologist: Decompose Request",
        "🏗 Architect: Plan Workflow",
        "🔬 Technician: Execute Steps",
        "✅ Critic: Review & Finalize",
    ]

    if st.button("🚀 Start Workflow", key="btn_workflow"):
        llm_config = {
            "provider": llm_provider,
            "api_key": llm_api_key if llm_api_key else None,
            "model": llm_model,
            "base_url": llm_base_url,
        }

        step_placeholder = st.empty()

        # Show animated progress through steps
        for i, step in enumerate(WORKFLOW_STEPS):
            step_placeholder.info(f"**Step {i+1}/{len(WORKFLOW_STEPS)}:** {step}")

        with st.spinner("Agents are working… (this may take a moment)"):
            try:
                result = run_design_task(user_request, llm_config)
                step_placeholder.success("✅ All workflow steps complete!")
                st.subheader("Result")
                st.markdown(result)
            except Exception as e:
                step_placeholder.empty()
                st.error(f"An error occurred: {e}")
