# tui.py
import os
import sys # For exiting

# Import the necessary functions from our agent file
import agent

# --- TUI Framework (Mostly similar to before, but calls ai_agent) ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Pauses execution until user presses Enter."""
    input("\nPress Enter to continue...")

def read_prompt_file(filepath: str) -> str | None:
    """Reads content from a given file path."""
    try:
        # Basic check to prevent reading unexpected files, enhance as needed
        if not filepath.endswith(".txt"):
             print(f"[Error] Invalid prompt file extension: {filepath}. Only .txt allowed.")
             return None
        if not os.path.exists(filepath):
            print(f"[Error] Prompt file not found: {filepath}")
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[Error] Failed to read prompt file '{filepath}': {e}")
        return None


def display_main_menu(state):
    """Displays the main menu and current status."""
    clear_screen()
    print("=============================================")
    print("      AI-Enhanced Password List Generator    ")
    print("=============================================")
    print(f" Status:")
    print(f"  - Azure Endpoint Set: {'Yes' if state['endpoint'] else 'No'}")
    print(f"  - Azure Key Set:      {'Yes' if state['key'] else 'No'}")
    print(f"  - AI Client Ready:    {'Yes' if state['client_ready'] else 'No'}") # Use the flag
    print(f"  - System Prompt File: {state['system_prompt_path']}")
    print(f"  - AI Model:           {state['model_name']}")
    print(f"  - Seed Words:         {len(state['seed_words'])} ({', '.join(state['seed_words'][:5])}{'...' if len(state['seed_words']) > 5 else ''})")
    print(f"  - AI Suggestions:     {len(state['ai_suggestions'])}")
    print(f"  - Words for Engine:   {len(state['words_for_engine'])}")
    # Add more status lines for mutation configs later
    print(f"  - Output File:        {state['output_filename']}")
    print("---------------------------------------------")
    print(" Main Menu:")
    print("  1. Set Azure Endpoint & Key")
    print("  2. Set System Prompt File")
    print("  3. Set AI Model Name")
    print("  4. Enter/Edit Seed Words")
    print("  5. Run AI Brainstorming (Requires 1, 2, 4)")
    print("  6. Review/Filter AI Suggestions")
    print("  7. Configure Mutations (Placeholder)") # TODO
    print("  8. Estimate List Size (Placeholder)")    # TODO
    print("  9. Set Output Filename")
    print("  10. GENERATE WORDLIST (Placeholder)")   # TODO
    print("  11. Exit")
    print("=============================================")

def get_azure_details(state):
    """Prompts user for Azure endpoint and key and initializes client via agent."""
    clear_screen()
    print("--- Set Azure OpenAI Credentials ---")
    endpoint = input(f"Enter Azure Endpoint [Current: {state.get('endpoint', 'Not Set')}]: ")
    key = input(f"Enter Azure API Key [Current: {'******' if state.get('key') else 'Not Set'}]: ")

    # Update state immediately even if initialization fails later
    if endpoint:
        state['endpoint'] = endpoint.strip()
    if key:
        state['key'] = key.strip()

    # Attempt to initialize client via the agent function
    if state.get('endpoint') and state.get('key'):
        success, message = agent.initialize_client(state['endpoint'], state['key'])
        state['client_ready'] = success
        print(f"\n{message}") # Display status/error message from agent
    else:
        state['client_ready'] = False
        print("\n[Warning] Endpoint or Key not fully provided. AI Client not initialized.")
    pause()

def set_system_prompt(state):
    """Sets the path to the system prompt file."""
    clear_screen()
    print("--- Set System Prompt File ---")
    print("Enter the path to the system prompt file (e.g., prompt_concise.txt).")
    current_path = state.get('system_prompt_path', 'Not Set')
    new_path = input(f"File path [Current: {current_path}]: ").strip()
    if new_path:
        # Basic check if file exists here, or rely on read error later
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
    pause()

def set_model_name(state):
    """Sets the AI model name (deployment name)."""
    clear_screen()
    print("--- Set AI Model Name ---")
    print("Enter the deployment name of your Azure OpenAI model.")
    current_model = state.get('model_name', 'Not Set')
    new_model = input(f"Model name [Current: {current_model}]: ").strip()
    if new_model:
        state['model_name'] = new_model
        print(f"AI Model set to: {state['model_name']}")
    else:
        print("No changes made.")
    pause()

def get_seed_words(state):
    """Prompts user for seed words."""
    clear_screen()
    print("--- Enter Seed Words ---")
    print("Enter your seed words, separated by commas.")
    current_words = ", ".join(state['seed_words'])
    print(f"Current: {current_words}")
    new_words_str = input("New words: ")
    if new_words_str.strip():
        state['seed_words'] = [word.strip() for word in new_words_str.split(',') if word.strip()]
        # Reset AI suggestions and filtered list when seeds change
        state['ai_suggestions'] = []
        state['words_for_engine'] = list(state['seed_words']) # Default to seeds
        print(f"\nSeed words updated to: {', '.join(state['seed_words'])}")
    else:
        print("No changes made.")
    pause()

def run_ai_brainstorming(state):
    """Triggers the AI brainstorming process via the agent."""
    clear_screen()
    print("--- Run AI Brainstorming ---")

    # Prerequisites check
    if not state['client_ready']:
        print("[Error] Azure client not ready. Please set endpoint/key first (Option 1).")
        pause()
        return
    if not state['system_prompt_path']:
        print("[Error] System prompt file not set. Please set it first (Option 2).")
        pause()
        return
    if not state['seed_words']:
        print("[Error] No seed words entered. Please enter seed words first (Option 4).")
        pause()
        return

    # Read system prompt content
    system_prompt_content = read_prompt_file(state['system_prompt_path'])
    if system_prompt_content is None:
        # Error message already printed by read_prompt_file
        pause()
        return

    # Prepare user prompt content
    user_prompt_content = f"Expand these seed words: {', '.join(state['seed_words'])}"

    # Call the agent function
    suggestions = agent.get_ai_suggestions(
        system_prompt_content=system_prompt_content,
        user_prompt_content=user_prompt_content,
        model_name=state['model_name']
    )

    if suggestions is not None: # Check if call succeeded (didn't return None)
        # Combine suggestions with original seeds, remove duplicates, keep order roughly
        combined = list(dict.fromkeys(state['seed_words'] + suggestions)) # Simple dedupe
        state['ai_suggestions'] = combined
        # Automatically update words_for_engine to the new suggestions for now
        state['words_for_engine'] = list(state['ai_suggestions'])
        print(f"\nBrainstorming complete. Found {len(state['ai_suggestions'])} unique terms (including originals).")
        print("Use Option 6 to review and filter.")
    else:
        # Error message should have been printed by the agent function
        print("\nAI Brainstorming failed or returned no results.")
    pause()

def review_filter_suggestions(state):
    """Allows user to review and select words for the engine. (Identical to previous version)"""
    clear_screen()
    print("--- Review & Filter AI Suggestions ---")
    source_list = state['ai_suggestions'] if state['ai_suggestions'] else state['seed_words']

    if not source_list:
        print("No words available to review. Enter seed words (Option 4) or run AI (Option 5).")
        pause()
        return

    print("Current words suggested/available:")
    temp_selection = list(state['words_for_engine']) # Start with currently selected
    # Sort source_list for consistent display order during filtering
    source_list.sort()
    for i, word in enumerate(source_list):
        status = "[X]" if word in temp_selection else "[ ]"
        print(f" {i+1:3d}. {status} {word}")

    print("\nEnter numbers to toggle selection (e.g., 1 5 10), 'all', 'none', or 'done'.")

    while True:
        choice = input("Toggle/Command: ").strip().lower()
        if choice == 'done':
            break
        elif choice == 'all':
            temp_selection = list(source_list)
            print(f"Selected all {len(temp_selection)} words.")
        elif choice == 'none':
            temp_selection = []
            print("Deselected all words.")
        else:
            try:
                indices_to_toggle = set()
                parts = choice.split()
                for part in parts:
                    if '-' in part: # Handle ranges like 3-7
                        start, end = map(int, part.split('-'))
                        if start > end or start < 1 or end > len(source_list):
                            raise ValueError(f"Invalid range: {part}")
                        indices_to_toggle.update(range(start - 1, end))
                    else: # Handle single numbers
                        idx = int(part) - 1
                        if not (0 <= idx < len(source_list)):
                             raise ValueError(f"Invalid number: {part}")
                        indices_to_toggle.add(idx)

                if indices_to_toggle:
                    toggled_count = 0
                    for idx in indices_to_toggle:
                        word = source_list[idx]
                        if word in temp_selection:
                            temp_selection.remove(word)
                        else:
                            temp_selection.append(word)
                        toggled_count +=1
                    # Re-display selection count after toggling potentially many items
                    print(f"Toggled {toggled_count} item(s). Currently {len(temp_selection)} selected.")

            except ValueError as e:
                print(f"[Error] Invalid input: {e}. Use space-separated numbers (e.g., 1 5 10), ranges (e.g., 3-7), 'all', 'none', or 'done'.")

    state['words_for_engine'] = temp_selection
    print(f"\nFinal selection: {len(state['words_for_engine'])} words chosen for generation engine.")
    pause()


def set_output_filename(state):
    """Sets the output filename. (Identical to previous version)"""
    clear_screen()
    print("--- Set Output Filename ---")
    current_name = state['output_filename']
    new_name = input(f"Enter filename [Current: {current_name}]: ").strip()
    if new_name:
        state['output_filename'] = new_name
        print(f"Output filename set to: {state['output_filename']}")
    else:
        print("No changes made.")
    pause()

# --- Main Execution ---
if __name__ == "__main__":
    # Initial state
    app_state = {
        "endpoint": None,
        "key": None,
        "client_ready": False, # Flag to track if agent client is ready
        "system_prompt_path": "prompt_concise.txt", # Default prompt file
        "model_name": "gpt-4o-mini", # Default model deployment name
        "seed_words": [],
        "ai_suggestions": [],
        "words_for_engine": [],
        "mutation_config": {}, # Placeholder
        "output_filename": "wordlist.txt"
    }

    # --- Main Application Loop ---
    while True:
        display_main_menu(app_state)
        choice = input(f"Enter your choice (1-{len(app_state)+2}): ") # Dynamic range based on menu items

        if choice == '1':
            get_azure_details(app_state)
        elif choice == '2':
            set_system_prompt(app_state)
        elif choice == '3':
            set_model_name(app_state)
        elif choice == '4':
            get_seed_words(app_state)
        elif choice == '5':
            run_ai_brainstorming(app_state)
        elif choice == '6':
            review_filter_suggestions(app_state)
        elif choice == '7':
            print("\n[Placeholder] Mutation configuration not yet implemented.")
            # TODO: Call function/submenu for mutation settings
            pause()
        elif choice == '8':
            print("\n[Placeholder] Wordlist size estimation not yet implemented.")
            # TODO: Implement estimation logic
            pause()
        elif choice == '9':
            set_output_filename(app_state)
        elif choice == '10':
            print("\n[Placeholder] Wordlist generation not yet implemented.")
            # TODO: Implement call to permutation engine
            pause()
        elif choice == '11':
            print("Exiting...")
            sys.exit(0) # Clean exit
        else:
            print("\nInvalid choice, please try again.")
            pause()

    print("Goodbye!") # Should not be reached if exiting via sys.exit
