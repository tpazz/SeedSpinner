import tui
import os

# --- UI Interaction Functions ---
# These functions are called from the TUI menu to handle file-related settings.

def set_system_prompt(state):
    """Prompts the user to set the file path for the AI's system prompt."""
    tui.clear_screen()
    print("--- Set System Prompt File ---\n")
    print("Enter the path to the system prompt file (e.g., CreativePrompt.txt).")
    current_path = state.get('system_prompt_path', 'Not Set')
    new_path = input(f"File path [Current: {current_path}]: ").strip()
    
    if new_path:
        # Perform basic validation on the user-provided file path.
        if os.path.exists(new_path):
             if new_path.endswith(".txt"):
                 state['system_prompt_path'] = new_path
                 print(f"System prompt file set to: {state['system_prompt_path']}")
             else:
                 print("[Error] Invalid file type. Please provide a .txt file.")
        else:
             print(f"[Error] File not found: {new_path}")
             print("Please ensure the file exists in the current directory or provide the full path.")
    else:
        print("No changes made.")
    tui.pause()

def read_prompt_file(filepath: str) -> str | None:
    """Safely reads the content of a text file and returns it as a string."""
    try:
        # Validate the file before attempting to read it.
        if not filepath.endswith(".txt"):
             print(f"[Error] Invalid prompt file extension: {filepath}. Only .txt allowed.")
             return None
        if not os.path.exists(filepath):
            print(f"[Error] Prompt file not found: {filepath}")
            return None
            
        # Open and read the file content.
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        # Catch any potential IO errors during file reading.
        print(f"[Error] Failed to read prompt file '{filepath}': {e}")
        return None    

def set_output_filename(state):
    """Prompts the user to set the name for the final wordlist file."""
    tui.clear_screen()
    print("--- Set Output Filename ---\n")
    current_name = state['output_filename']
    new_name = input(f"Enter filename [Current: {current_name}]: ").strip()
    if new_name:
        state['output_filename'] = new_name
        print(f"Output filename set to: {state['output_filename']}")
    else:
        print("No changes made.")
    tui.pause()