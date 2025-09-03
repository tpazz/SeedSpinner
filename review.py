import tui

def get_seed_words(state):
    """Prompts the user to enter their initial comma-separated seed words."""
    tui.clear_screen()
    print("--- Enter Seed Words ---\n")
    print("Enter your seed words, separated by commas.")
    current_words = ", ".join(state['seed_words'])
    print(f"Current: {current_words}")
    new_words_str = input("New words: ")
    
    # Process the new input only if the user entered something.
    if new_words_str.strip():
        # Split the input string by commas and strip whitespace from each word.
        state['seed_words'] = [word.strip() for word in new_words_str.split(',') if word.strip()]
        
        # When new seed words are entered, reset any previous AI suggestions.
        state['ai_suggestions'] = []
        # The list of words for the generation engine is reset to match the new seeds.
        state['words_for_engine'] = list(state['seed_words'])
        print(f"\nSeed words updated to: {', '.join(state['seed_words'])}")
    else:
        print("No changes made.")
    tui.pause()

def review_filter_suggestions(state):
    """
    Provides an interactive menu for the user to review and select which words
    (from seeds and AI suggestions) will be used by the generation engine.
    """
    tui.clear_screen()
    print("--- Review & Filter Words for Engine ---\n")

    # The list of all available words to choose from is the current 'words_for_engine' list.
    source_list_unsorted = state.get('words_for_engine', [])

    if not source_list_unsorted:
        print("No words available to review (Engine list is empty)."); tui.pause(); return

    print("Reviewing the list currently set for the generation engine:")

    # Ensure the list is unique and sorted for a consistent display during filtering.
    source_list_sorted = sorted(list(set(source_list_unsorted)))
   
    # `temp_selection` holds the words the user decides to keep during this session.
    # It starts by including all available words.
    temp_selection = list(source_list_sorted)

    # Main interactive loop for the filtering screen.
    while True:
        tui.clear_screen()
        print("--- Review & Filter Words for Engine ---")
        print(f"Words currently set for engine ({len(source_list_sorted)} total):")

        # Display all available words with their current selection status ([X] = keep).
        for i, word in enumerate(source_list_sorted):
            status = "[X]" if word in temp_selection else "[ ]"
            print(f" {i+1:3d}. {status} {word}")

        print(f"\nKeeping {len(temp_selection)} words for engine.")
        print("\nEnter numbers or ranges to toggle inclusion (e.g., 1 5 10-15).")
        print("Commands: 'all' (keep all), 'none' (keep none), 'done'.")

        choice = input("Toggle/Command: ").strip().lower()
        action_taken = False

        if choice == 'done':
            break

        elif choice == 'all':
            # Mark all words to be kept.
            temp_selection = list(source_list_sorted)
            print(f"\nMarked all {len(temp_selection)} words to keep.")
            action_taken = True

        elif choice == 'none':
            # Mark all words for removal.
            temp_selection = []
            print("\nMarked all words for removal (keeping none).")
            action_taken = True

        else:
            # Handle numeric input for toggling individual words or ranges.
            try:
                indices_to_toggle = set()
                parts = choice.split()
                valid_input = True
                for part in parts:
                     if '-' in part: # Handle ranges like "3-7"
                         try:
                             start_str, end_str = part.split('-', 1)
                             start, end = int(start_str), int(end_str)
                             if start > end or start < 1 or end > len(source_list_sorted): raise ValueError("Invalid range")
                             indices_to_toggle.update(range(start - 1, end))
                         except ValueError: print(f"[Error] Invalid range: {part}. Use #-#."); valid_input = False; break
                     else: # Handle single numbers like "1", "5"
                         try:
                             idx = int(part) - 1
                             if not (0 <= idx < len(source_list_sorted)): raise ValueError("Invalid number")
                             indices_to_toggle.add(idx)
                         except ValueError: print(f"[Error] Invalid number: {part}. Must be 1-{len(source_list_sorted)}."); valid_input = False; break
                if not valid_input: action_taken = True; continue

                # Toggle the selection status for the chosen indices.
                if indices_to_toggle:
                    count = 0
                    for idx in sorted(list(indices_to_toggle)):
                        word = source_list_sorted[idx]
                        if word in temp_selection:
                            temp_selection.remove(word)
                        else:
                            temp_selection.append(word)
                        count += 1
                    if count > 0: print(f"\nToggled inclusion for {count} item(s)."); action_taken = True
            except Exception as e: print(f"[Error] Could not process input '{choice}': {e}"); action_taken = True

        if action_taken:
            tui.pause()

    # After the user is done, update the main application state with their final selection.
    state['words_for_engine'] = sorted(list(set(temp_selection)))

    print(f"\nFinal words for engine set to {len(state['words_for_engine'])} words.")
    tui.pause()