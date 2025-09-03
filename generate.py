import itertools
import tui
from datetime import datetime
import tempfile
import subprocess
import os
import estimate

# --- Helper Mutation Functions ---
# These functions perform a single type of mutation on a given word.

def _apply_capitalisation(word):
    """Generates a set of common capitalisation variations for a single word."""
    variations = {word.lower(), word.title(), word.upper()}
    variations.add(word) # Ensure the original form is included
    return list(variations)

def _apply_leet_speak(word):
    """Generates leet speak variations using a recursive approach for combinatorial substitutions."""
    subs = {
        'a': ['@', '4'], 'A': ['@', '4'],
        'e': ['3'],      'E': ['3'],
        'i': ['1', '!'], 'I': ['1', '!'],
        'o': ['0'],      'O': ['0'],
        's': ['$', '5'], 'S': ['$', '5'],
        't': ['7'],      'T': ['7'],
    }
    forms = {word} # Always include the original, un-leeted word

    # This recursive function explores all combinations of enabled substitutions.
    def generate_leets_recursive(current_word_list, index):
        if index == len(current_word_list):
            forms.add("".join(current_word_list))
            return

        original_char = current_word_list[index]
        # Explore paths without substituting the current character
        generate_leets_recursive(list(current_word_list), index + 1)

        # Explore paths WITH substitutions for the current character
        if original_char in subs:
            for sub_char in subs[original_char]:
                current_word_list[index] = sub_char
                generate_leets_recursive(list(current_word_list), index + 1)
                current_word_list[index] = original_char # Backtrack for other possibilities
    
    # Start the recursion only if there are characters in the word that can be substituted.
    if any(c in subs for c in word):
        generate_leets_recursive(list(word), 0)

    return list(forms)


def _apply_affixes(word):
    """
    Applies a comprehensive set of hardcoded affixes, including dynamically generated years
    and chained (number/symbol) combinations.
    """
    # --- Define Affix Groups ---
    current_year = datetime.now().year
    years_to_generate = 50
    
    full_years = [str(year) for year in range(current_year, current_year - years_to_generate - 1, -1)]
    two_digit_years = [datetime(year, 1, 1).strftime('%y') for year in range(current_year, current_year - years_to_generate - 1, -1)]
    simple_numbers = [str(i) for i in range(10)] + ["0" + str(i) for i in range(10)] + ["123", "12345"]
    
    numeric_affixes = full_years + two_digit_years + simple_numbers
    symbol_affixes = ["!", "@", "#", "$", "%", "^", "&", "*", "?", "_", "-"]

    final_variations = {word} # Start with the base word

    # 1. Apply SINGLE suffixes from all groups
    all_simple_affixes = numeric_affixes + symbol_affixes
    for affix in all_simple_affixes:
        final_variations.add(word + affix)

    # 2. Apply CHAINED SUFFIXES (Pattern: wordNUMBERsymbol)
    for num in numeric_affixes:
        word_with_num = word + num
        for sym in symbol_affixes:
            final_variations.add(word_with_num + sym)

    # 3. Apply CHAINED SUFFIXES (Pattern: wordSYMBOLnumber)
    for sym in symbol_affixes:
        word_with_sym = word + sym
        for num in numeric_affixes:
            final_variations.add(word_with_sym + num)

    return list(final_variations)

def _generate_single_word_core_variations(base_word, mutation_config):
    """
    Creates the "core" variations of a word by handling Capitalisation and Leet Speak.
    If both are enabled, their effects are implicitly combined. Affixes are NOT handled here.
    """
    # Initialize the set with the base word and its lowercase to ensure it always exists.
    forms_after_caps = {base_word.lower(), base_word}
    
    # If capitalisation is on, update the set with more variations.
    if mutation_config.get("capitalisation", False):
        forms_after_caps.update(_apply_capitalisation(base_word))

    # Apply leet speak to all forms generated so far (base word and/or capitalized versions).
    final_core_forms = set()
    if mutation_config.get("leet_speak", False):
        for form_cap in forms_after_caps:
            final_core_forms.update(_apply_leet_speak(form_cap))
    else:
        # If no leet speak, the core forms are just the capitalized forms.
        final_core_forms.update(forms_after_caps)

    return list(final_core_forms)


def generate_wordlist_logic(base_words, mutation_config, output_filename):
    """
    The main memory-safe generation engine. It orchestrates the entire mutation pipeline,
    streams all candidates to a temporary file, and uses external system utilities
    (sort/uniq) for safe, efficient deduplication and final output.
    """
    if not base_words: return 0, "Error: No base words provided for generation."
    if not output_filename: return 0, "Error: Output filename not set."

    print(f"\nStarting wordlist generation for {len(base_words)} base word(s)...")
    print(f"Output will be saved to: {output_filename}")
    print("Mode: Memory-Safe (streaming to disk)")
    
    affixes_enabled = mutation_config.get("affixes", False)
    
    # Create a temporary file to store all generated candidates, avoiding memory overload.
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_f:
        temp_filename = temp_f.name
        print(f"\nGenerating raw candidates to temporary file: {temp_filename}")
        
        raw_candidate_count = 0
        core_forms_for_concatenation_map = {}

        # --- Step 1: Process Single Words ---
        for i, base_word in enumerate(base_words):
            print(f"\rProcessing single-word forms for: '{base_word}'...", end="")

            # Generate the core Caps/Leet variations for the current base word.
            core_variations = _generate_single_word_core_variations(base_word, mutation_config)
            # Store these core forms in a map to be used as components for concatenation later.
            core_forms_for_concatenation_map[base_word] = core_variations

            # Apply final transformations (affixes) and write to the temp file.
            if affixes_enabled:
                for core_form in core_variations:
                    final_variations = _apply_affixes(core_form)
                    for final_form in final_variations:
                        temp_f.write(final_form + "\n")
                        raw_candidate_count += 1
            else:
                for core_form in core_variations:
                    temp_f.write(core_form + "\n")
                    raw_candidate_count += 1
        print() # Add a newline to finalize the progress bar.

        # --- Step 2: Concatenation ---
        if mutation_config.get("concatenation", False) and len(base_words) > 1:
            print("\nProcessing concatenations...")
            for i_idx in range(len(base_words)):
                word1_base = base_words[i_idx]
                print(f"\rConcatenating with '{word1_base}' as first word...", end="")
                for j_idx in range(len(base_words)):
                    if i_idx == j_idx and len(base_words) > 1: continue

                    word2_base = base_words[j_idx]
                    
                    # Retrieve the pre-generated core variations for the pair of words.
                    forms1 = core_forms_for_concatenation_map.get(word1_base, [word1_base])
                    forms2 = core_forms_for_concatenation_map.get(word2_base, [word2_base])

                    # Create all combinations of the component variations.
                    for v1 in forms1:
                        for v2 in forms2:
                            concatenated_word = v1 + v2
                            if affixes_enabled:
                                final_concat_variations = _apply_affixes(concatenated_word)
                                for final_form in final_concat_variations:
                                    temp_f.write(final_form + "\n")
                                    raw_candidate_count += 1
                            else:
                                temp_f.write(concatenated_word + "\n")
                                raw_candidate_count += 1
            print("\nFinished processing concatenations.")

    # --- Step 3: Post-Processing the Temp File ---
    # This step uses powerful system commands to handle massive files efficiently.
    print(f"\nGenerated {raw_candidate_count:,} raw password candidates.")
    print("Now sorting and removing duplicates using system utilities...")

    command = f'sort "{temp_filename}" | uniq > "{output_filename}"'
    
    try:
        # Execute the command. `shell=True` is needed for the pipe `|` to work.
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        message = "[FATAL ERROR] `sort` or `uniq` command not found. Ensure these utilities are in your system's PATH."
        return 0, message
    except subprocess.CalledProcessError as e:
        message = f"[FATAL ERROR] Post-processing failed:\n{e.stderr}"
        return 0, message
    finally:
        # Clean up the large temporary file after processing is complete.
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
                print(f"Cleaned up temporary file.")
            except OSError as e:
                print(f"[Warning] Could not delete temporary file '{temp_filename}': {e}")

    # --- Step 4: Count lines in the final file to get the unique count ---
    try:
        with open(output_filename, 'r', encoding='utf-8') as f:
            final_unique_count = sum(1 for line in f)
        return final_unique_count, f"Successfully generated {final_unique_count:,} unique passwords."
    except Exception as e:
        message = f"Could not count lines in final file, but it was created successfully. Error: {e}"
        return -1, message


def trigger_wordlist_generation(state):
    """
    Main TUI function for Option 10. It shows the user a final resource estimate,
    asks for confirmation, and then calls the main generation engine.
    """
    tui.clear_screen()
    print("--- Generation Preview & Resource Estimate ---\n")

    base_words = state.get('words_for_engine', [])
    mutation_config = state.get('mutation_config', {})
    output_filename = state.get('output_filename', 'wordlist.txt')

    if not base_words:
        print("No words selected for the engine. Cannot generate."); tui.pause(); return
    
    # Show the user a final, detailed estimate before they commit.
    estimate.estimate_list_size(state)
    
    confirm = input("\nProceed with generation? (yes/no): ").strip().lower()
    if confirm == 'yes':
        # Call the main logic function and display its return message.
        count, message = generate_wordlist_logic(base_words, mutation_config, output_filename)
        print(f"\n{message}")
    else:
        print("\nGeneration cancelled.")
    tui.pause()