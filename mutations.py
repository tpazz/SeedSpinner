import tui

def configure_mutations(state):
    """
    Provides an interactive menu for the user to enable or disable
    the various mutation types.
    """
    tui.clear_screen()
    print("--- Configure Mutation Options ---\n")

    # This list defines the mutation options presented to the user.
    # Each tuple contains the display name and the corresponding key in the config dictionary.
    mutation_options = [
        ("Capitalisation", "capitalisation"),
        ("Leet Speak (e.g., a=@, o=0)", "leet_speak"),
        ("Concatenation (Combine words)", "concatenation"),
        ("Suffix/Prefix Addition (Numbers/Symbols)", "affixes")
    ]

    # Ensure the mutation_config dictionary exists in the application state.
    if 'mutation_config' not in state:
        state['mutation_config'] = {}

    config = state['mutation_config']

    # Main interactive loop for the configuration screen.
    while True:
        tui.clear_screen()
        print("--- Configure Mutation Options ---\n")
        print("Current Mutation Settings:")
        # Display each mutation option with its current status ([X] for ON, [ ] for OFF).
        for i, (display_name, key) in enumerate(mutation_options):
            status = "[X]" if config.get(key, False) else "[ ]"
            print(f" {i+1:2d}. {status} {display_name}")

        print("\nEnter numbers to toggle options (e.g., 1 4).")
        print("Commands: 'all', 'none', 'done'.")

        choice = input("Toggle/Command: ").strip().lower()
        
        # A flag to determine if the screen should pause for user feedback.
        action_taken = False

        if choice == 'done':
            break # Exit the configuration loop.

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
            # Handle numeric input for toggling individual options.
            try:
                indices_to_toggle = set()
                parts = choice.split()
                valid_input = True
                for part in parts:
                    idx = int(part) - 1
                    if not (0 <= idx < len(mutation_options)):
                         print(f"[Error] Invalid number: {part}. Options are 1-{len(mutation_options)}.")
                         valid_input = False
                         break
                    indices_to_toggle.add(idx)

                if valid_input and indices_to_toggle:
                    toggled_count = 0
                    print()
                    for idx in sorted(list(indices_to_toggle)):
                         _, key = mutation_options[idx]
                         # Flip the boolean value for the selected mutation key.
                         config[key] = not config.get(key, False)
                         display_name, _ = mutation_options[idx]
                         print(f" Toggled '{display_name}' to {'ON' if config[key] else 'OFF'}.")
                         toggled_count += 1
                    if toggled_count > 0:
                        action_taken = True

            except ValueError:
                print("[Error] Invalid input. Please enter space-separated numbers, 'all', 'none', or 'done'.")
                action_taken = True

        # If a change was made or an error occurred, pause to let the user see the message.
        if action_taken:
            tui.pause()

    # After exiting the loop, show a final summary of the saved settings.
    print("\nMutation settings saved.")
    enabled_options = [name for name, key in mutation_options if config.get(key, False)]
    if enabled_options:
        print(f"Currently enabled: {', '.join(enabled_options)}")
    else:
        print("All mutations currently disabled.")

    tui.pause()