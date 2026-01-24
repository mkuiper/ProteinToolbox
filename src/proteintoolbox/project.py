import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional

PROJECTS_ROOT = "data/projects"

class Project:
    def __init__(self, name: str, description: str = "", created_at: str = None):
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now().isoformat()
        self.path = os.path.join(PROJECTS_ROOT, name)
        
    def save_metadata(self):
        os.makedirs(self.path, exist_ok=True)
        meta = {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at
        }
        with open(os.path.join(self.path, "metadata.json"), 'w') as f:
            json.dump(meta, f, indent=2)

    @classmethod
    def load(cls, name: str):
        path = os.path.join(PROJECTS_ROOT, name)
        if not os.path.exists(path):
            return None
        try:
            with open(os.path.join(path, "metadata.json"), 'r') as f:
                data = json.load(f)
                return cls(data["name"], data.get("description", ""), data.get("created_at"))
        except Exception:
            return None

    def list_files(self, extension: str = None) -> List[str]:
        if not os.path.exists(self.path):
            return []
        files = []
        for root, _, filenames in os.walk(self.path):
            for f in filenames:
                if extension and not f.endswith(extension):
                    continue
                # Return relative path from project root
                rel_path = os.path.relpath(os.path.join(root, f), self.path)
                files.append(rel_path)
        return sorted(files)

    def get_full_path(self, rel_path: str) -> str:
        return os.path.join(self.path, rel_path)

    def add_file(self, src_path: str, dest_name: str = None):
        if not dest_name:
            dest_name = os.path.basename(src_path)
        dest_path = os.path.join(self.path, dest_name)
        shutil.copy2(src_path, dest_path)
        return dest_path

class ProjectManager:
    def __init__(self):
        os.makedirs(PROJECTS_ROOT, exist_ok=True)

    def list_projects(self) -> List[str]:
        return [d for d in os.listdir(PROJECTS_ROOT) if os.path.isdir(os.path.join(PROJECTS_ROOT, d))]

    def create_project(self, name: str, description: str = "") -> Project:
        if name in self.list_projects():
            raise ValueError(f"Project '{name}' already exists.")
        proj = Project(name, description)
        proj.save_metadata()
        return proj

    def get_project(self, name: str) -> Optional[Project]:
        return Project.load(name)
