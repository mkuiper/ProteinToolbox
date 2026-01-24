import json
import os
from typing import List, Dict, Optional
import requests

class Tool:
    def __init__(self, name: str, category: str, description: str, url: str, pip_package: Optional[str] = None, installed: bool = False):
        self.name = name
        self.category = category
        self.description = description
        self.url = url
        self.pip_package = pip_package
        self.installed = installed

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "url": self.url,
            "pip_package": self.pip_package,
            "installed": self.installed
        }

class ToolRegistry:
    def __init__(self, registry_path: str = "ProteinToolbox/data/tool_registry.json"):
        self.registry_path = registry_path
        self.tools: List[Tool] = []
        self.load_registry()

    def load_registry(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                self.tools = [Tool(**t) for t in data.get("tools", [])]
        else:
            print(f"Warning: Registry file not found at {self.registry_path}")

    def save_registry(self):
        data = {"tools": [t.to_dict() for t in self.tools]}
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_tool(self, name: str) -> Optional[Tool]:
        for tool in self.tools:
            if tool.name.lower() == name.lower():
                return tool
        return None

    def list_tools(self, category: Optional[str] = None) -> List[Tool]:
        if category:
            return [t for t in self.tools if t.category.lower() == category.lower()]
        return self.tools

    def update_installation_status(self, tool_name: str, status: bool):
        tool = self.get_tool(tool_name)
        if tool:
            tool.installed = status
            self.save_registry()

    # Mock update checker - in a real app, this would query PyPI or GitHub releases
    def check_for_updates(self):
        print("Checking for tool updates...")
        # Logic to check external versions would go here
        pass
