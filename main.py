import sys
import os
# Add the src directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from proteintoolbox.agents.crew import run_design_task
from proteintoolbox.registry import ToolRegistry

def main():
    print("==================================================")
    print("          ProteinToolbox - AI Design Suite        ")
    print("==================================================")
    
    # Simple CLI loop
    while True:
        print("\nOptions:")
        print("1. Run a Design Agent Task")
        print("2. List Available Tools")
        print("3. Exit")
        
        choice = input("\nEnter choice: ")
        
        if choice == '1':
            request = input("Describe your design goal (e.g., 'Design an antibody for target X'): ")
            if request:
                result = run_design_task(request)
                print("\n\n##################################################")
                print("FINAL WORKFLOW PLAN:")
                print(result)
                print("##################################################\n")
        elif choice == '2':
            reg = ToolRegistry(registry_path="ProteinToolbox/data/tool_registry.json")
            print("\n--- Registry ---")
            for t in reg.list_tools():
                print(f"[{'x' if t.installed else ' '}] {t.name} ({t.category})")
        elif choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

