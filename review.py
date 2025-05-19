import tui

def get_seed_words(state):
    """Prompts user for seed words."""
    tui.clear_screen()
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
    tui.pause()


def set_output_filename(state):
    """Sets the output filename. (Identical to previous version)"""
    tui.clear_screen()
    print("--- Set Output Filename ---")
    current_name = state['output_filename']
    new_name = input(f"Enter filename [Current: {current_name}]: ").strip()
    if new_name:
        state['output_filename'] = new_name
        print(f"Output filename set to: {state['output_filename']}")
    else:
        print("No changes made.")
    tui.pause()    

def review_filter_suggestions(state):
    """Allows user to review and refine the current words_for_engine list."""
    tui.clear_screen()
    print("--- Review & Filter Words for Engine ---")

    # --- Key Change Below ---
    # The list to display and filter is ALWAYS the current words_for_engine
    source_list_unsorted = state.get('words_for_engine', [])
    # --- End Key Change ---

    if not source_list_unsorted:
        print("No words available to review (Engine list is empty).")
        print("Enter seed words first (Option 4).")
        tui.pause()
        return

    print("Reviewing the list currently set for the generation engine:")

    # Sort the list for consistent display order during the session
    source_list_sorted = sorted(list(set(source_list_unsorted))) # Ensure unique and sorted

    # --- Key Change Below ---
    # Initialize temp_selection based on the source list itself (which is words_for_engine)
    # This means initially everything in words_for_engine is selected for keeping.
    temp_selection = list(source_list_sorted)
    # --- End Key Change ---

    while True:
        tui.clear_screen() # Redraw screen each time
        print("--- Review & Filter Words for Engine ---")
        print(f"Words currently set for engine ({len(source_list_sorted)} total):")

        # Display the sorted list with current selection status (what will be kept)
        for i, word in enumerate(source_list_sorted):
            status = "[X]" if word in temp_selection else "[ ]" # X means 'keep'
            print(f" {i+1:3d}. {status} {word}")

        print(f"\nKeeping {len(temp_selection)} words for engine.")
        print("\nEnter numbers or ranges to toggle inclusion (e.g., 1 5 10-15).")
        print("Commands: 'all' (keep all), 'none' (keep none), 'done'.")

        choice = input("Toggle/Command: ").strip().lower()

        # --- Process Input (Logic remains the same) ---
        action_taken = False

        if choice == 'done':
            break

        elif choice == 'all':
            # Select all words from the *sorted* source list to keep
            temp_selection = list(source_list_sorted)
            print(f"\nMarked all {len(temp_selection)} words to keep.")
            action_taken = True

        elif choice == 'none':
            temp_selection = []
            print("\nMarked all words for removal (keeping none).")
            action_taken = True

        else:
            # --- Number/Range processing logic remains the same ---
            # (Ensure you have the robust parsing from previous versions here)
            try:
                # ... (parsing logic for numbers/ranges into indices_to_toggle) ...
                indices_to_toggle = set()
                parts = choice.split()
                valid_input = True
                # Example (ensure this part matches your previous correct version):
                for part in parts:
                     if '-' in part: # Handle ranges like 3-7
                         try:
                             start_str, end_str = part.split('-', 1)
                             start = int(start_str); end = int(end_str)
                             if start > end or start < 1 or end > len(source_list_sorted): raise ValueError("Invalid range")
                             indices_to_toggle.update(range(start - 1, end))
                         except ValueError: print(f"[Error] Invalid range: {part}. Use #-#."); valid_input = False; break
                     else: # Handle single numbers
                         try:
                             idx = int(part) - 1
                             if not (0 <= idx < len(source_list_sorted)): raise ValueError("Invalid number")
                             indices_to_toggle.add(idx)
                         except ValueError: print(f"[Error] Invalid number: {part}. Must be 1-{len(source_list_sorted)}."); valid_input = False; break
                if not valid_input: action_taken = True; continue

                if indices_to_toggle:
                    count = 0
                    for idx in sorted(list(indices_to_toggle)):
                        word = source_list_sorted[idx]
                        if word in temp_selection: # If it was marked to keep...
                            temp_selection.remove(word) # ...mark it for removal
                        else: # If it was marked for removal...
                            temp_selection.append(word) # ...mark it to keep
                        count += 1
                    if count > 0: print(f"\nToggled inclusion for {count} item(s)."); action_taken = True
            except Exception as e: print(f"[Error] Could not process input '{choice}': {e}"); action_taken = True

        if action_taken:
            tui.pause()

    # --- Loop finished (user entered 'done') ---
    # Update the actual state['words_for_engine'] with the final list marked for keeping
    state['words_for_engine'] = sorted(list(set(temp_selection))) # Ensure unique and sorted order

    print(f"\nFinal words for engine set to {len(state['words_for_engine'])} words.")
    tui.pause() # Pause before returning to the main menu