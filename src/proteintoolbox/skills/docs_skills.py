import os
import datetime
from typing import List, Dict
from proteintoolbox.skills.bio_skills import get_sequence_from_pdb

def generate_project_report(project_path: str, output_filename: str = "REPORT.md") -> str:
    """
    Generates a Markdown summary report for a project directory.
    
    Args:
        project_path (str): Path to the project directory.
        output_filename (str): Name of the report file to generate.
        
    Returns:
        str: Path to the generated report.
    """
    if not os.path.isdir(project_path):
        raise ValueError(f"Project path {project_path} does not exist.")
        
    project_name = os.path.basename(os.path.normpath(project_path))
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_lines = [
        f"# Project Report: {project_name}",
        f"**Generated**: {timestamp}",
        "",
        "## File Summary",
        "| File Name | Size (Bytes) | Type |",
        "|---|---|---|",
    ]
    
    pdb_files = []
    
    files = sorted(os.listdir(project_path))
    for f in files:
        full_path = os.path.join(project_path, f)
        if os.path.isfile(full_path) and f != output_filename:
            size = os.path.getsize(full_path)
            ext = os.path.splitext(f)[1].lower()
            file_type = ext if ext else "File"
            report_lines.append(f"| {f} | {size} | {file_type} |")
            
            if ext in ['.pdb', '.ent', '.cif']:
                pdb_files.append(f)
                
    report_lines.append("")
    report_lines.append("## Structure Analysis")
    
    if not pdb_files:
        report_lines.append("No structure files found.")
    else:
        for pdb_file in pdb_files:
            report_lines.append(f"### {pdb_file}")
            full_path = os.path.join(project_path, pdb_file)
            try:
                seq = get_sequence_from_pdb(full_path)
                report_lines.append(f"**Sequence Length**: {len(seq)}")
                report_lines.append(f"**Sequence**: `{seq}`")
            except Exception as e:
                report_lines.append(f"*Error analyzing structure: {str(e)}*")
            report_lines.append("")

    output_path = os.path.join(project_path, output_filename)
    with open(output_path, "w") as f:
        f.write("\n".join(report_lines))
        
    return output_path
