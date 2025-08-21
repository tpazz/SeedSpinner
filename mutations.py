import tui

def configure_mutations(state):
    tui.clear_screen()
    print("--- Configure Mutation Options ---\n")

    mutation_options = [
        ("Capitalisation", "capitalisation"),
        ("Leet Speak (e.g., a=@, o=0)", "leet_speak"),
        ("Concatenation (Combine words)", "concatenation"),
        ("Suffix/Prefix Addition (Numbers/Symbols)", "affixes")
    ]

    if 'mutation_config' not in state:
        state['mutation_config'] = {}

    config = state['mutation_config']

    while True:
        tui.clear_screen() 
        print("--- Configure Mutation Options ---\n")
        print("Current Mutation Settings:")
        for i, (display_name, key) in enumerate(mutation_options):
            status = "[X]" if config.get(key, False) else "[ ]"
            print(f" {i+1:2d}. {status} {display_name}")

        print("\nEnter numbers to toggle options (e.g., 1 4).")
        print("Commands: 'all', 'none', 'done'.")

        choice = input("Toggle/Command: ").strip().lower()

        action_taken = False 

        if choice == 'done':
            break

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
                         display_name, key = mutation_options[idx]
                         current_value = config.get(key, False)
                         config[key] = not current_value
                         print(f" Toggled '{display_name}' to {'ON' if config[key] else 'OFF'}.")
                         toggled_count += 1
                    if toggled_count > 0:
                        action_taken = True

            except ValueError:
                print("[Error] Invalid input. Please enter space-separated numbers, 'all', 'none', or 'done'.")
                action_taken = True 

        if action_taken:
            tui.pause()

    print("\nMutation settings saved.")
    enabled_options = [name for name, key in mutation_options if config.get(key, False)]
    if enabled_options:
        print(f"Currently enabled: {', '.join(enabled_options)}")
    else:
        print("All mutations currently disabled.")

    tui.pause() 