import tui

def configure_mutations(state):
    """Allows the user to toggle mutation settings, including all/none commands."""
    tui.clear_screen()
    print("--- Configure Mutation Options ---")

    # Define the available mutations and their keys in the state dictionary
    mutation_options = [
        ("Capitalisation", "capitalisation"),
        ("Leet Speak (e.g., a=@, o=0)", "leet_speak"),
        ("Concatenation (Combine words)", "concatenation"),
        ("Suffix/Prefix Addition (Numbers/Symbols)", "affixes")
    ]

    # Ensure the mutation config dictionary exists in the state
    if 'mutation_config' not in state:
        state['mutation_config'] = {}

    # Work with a reference to the config dictionary for easier access
    config = state['mutation_config']

    while True:
        tui.clear_screen() # Re-clear and display each time for updated status
        print("--- Configure Mutation Options ---")
        print("Current Mutation Settings:")
        for i, (display_name, key) in enumerate(mutation_options):
            # Get current status, default to False if key doesn't exist yet
            status = "[X]" if config.get(key, False) else "[ ]"
            print(f" {i+1:2d}. {status} {display_name}")

        print("\nEnter numbers to toggle options (e.g., 1 4).")
        print("Commands: 'all', 'none', 'done'.")

        choice = input("Toggle/Command: ").strip().lower()

        # --- Process Input ---
        action_taken = False # Flag to indicate if a pause is needed

        if choice == 'done':
            break # Exit the configuration loop

        elif choice == 'all':
            print("\nEnabling all mutation options...")
            for _, key in mutation_options:
                config[key] = True
            action_taken = True

        elif choice == 'none':
            print("\nDisabling all mutation options...")
            for _, key in mutation_options:
                config[key] = False
            action_taken = True

        else:
            # Process number toggles
            try:
                indices_to_toggle = set()
                parts = choice.split()
                valid_input = True
                for part in parts:
                    # No range handling needed here, just numbers
                    idx = int(part) - 1
                    if not (0 <= idx < len(mutation_options)):
                         print(f"[Error] Invalid number: {part}. Options are 1-{len(mutation_options)}.")
                         valid_input = False
                         break # Stop processing this input line on first error
                    indices_to_toggle.add(idx)

                if valid_input and indices_to_toggle:
                    toggled_count = 0
                    print() # Add a newline for cleaner toggle feedback
                    for idx in sorted(list(indices_to_toggle)): # Process in order
                         display_name, key = mutation_options[idx]
                         # Toggle the value (True becomes False, False becomes True)
                         current_value = config.get(key, False)
                         config[key] = not current_value
                         print(f" Toggled '{display_name}' to {'ON' if config[key] else 'OFF'}.")
                         toggled_count += 1
                    if toggled_count > 0:
                        action_taken = True # Need pause if something was toggled

            except ValueError:
                print("[Error] Invalid input. Please enter space-separated numbers, 'all', 'none', or 'done'.")
                action_taken = True # Pause even on error

        # Pause only if an action was taken (toggle, all, none, or error)
        if action_taken:
            tui.pause()
            # The loop will then automatically redraw the menu with updated status

    # --- Loop finished (user entered 'done') ---
    print("\nMutation settings saved.")
    # Optional: Print a summary of enabled options here
    enabled_options = [name for name, key in mutation_options if config.get(key, False)]
    if enabled_options:
        print(f"Currently enabled: {', '.join(enabled_options)}")
    else:
        print("All mutations currently disabled.")

    tui.pause() # Pause before returning to the main menu