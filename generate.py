import itertools # For more advanced combinations if needed later, though not strictly used here yet
import tui
from datetime import datetime # Make sure to add this import at the top of your file
import tempfile
import subprocess
import os
import estimate

def _apply_capitalisation(word):
    """Generates capitalisation variations for a single word."""
    variations = {word.lower(), word.title(), word.upper()}
    variations.add(word) # Add the original form as well
    return list(variations)

def _apply_leet_speak(word):
    """Generates simple leet speak variations for a single word."""
    subs = {
        'a': ['@', '4'], 'A': ['@', '4'], # Removed original 'a' to ensure change if sub occurs
        'e': ['3'],      'E': ['3'],
        'i': ['1', '!'], 'I': ['1', '!'],
        'o': ['0'],      'O': ['0'],
        's': ['$', '5'], 'S': ['$', '5'],
        't': ['7'],      'T': ['7'],
    }
    forms = {word} # Always include the original form

    # --- Refined Leet Logic for more combinations ---
    # This is a basic recursive approach for simple leet.
    # It will generate more than the previous one but still not fully exhaustive for complex words.
    def generate_leets_recursive(current_word_list, index):
        if index == len(current_word_list):
            forms.add("".join(current_word_list))
            return

        original_char = current_word_list[index]
        generate_leets_recursive(list(current_word_list), index + 1) # Recurse with original char

        if original_char in subs:
            for sub_char in subs[original_char]:
                current_word_list[index] = sub_char
                generate_leets_recursive(list(current_word_list), index + 1) # Recurse with substituted char
                current_word_list[index] = original_char # Backtrack
    
    if any(c in subs for c in word): # Only run recursive if there are substitutable chars
        generate_leets_recursive(list(word), 0)

    # Fallback for very simple single substitutions if recursive is too much or for simple cases
    # (The recursive one should cover these if it works as intended)
    # if 'a' in word.lower(): forms.add(word.replace('a','@').replace('A','@'))
    # if 'e' in word.lower(): forms.add(word.replace('e','3').replace('E','3'))
    # if 'o' in word.lower(): forms.add(word.replace('o','0').replace('O','0'))
    # if 'i' in word.lower(): forms.add(word.replace('i','1').replace('I','1'))
    # if 's' in word.lower(): forms.add(word.replace('s','$').replace('S','$'))
    return list(forms)


def _apply_affixes(word):
    """
    Applies common suffixes and prefixes, including chained number+symbol combinations.
    """
    # --- Define Affix Groups ---
    # User-supplied prefixes/suffixes would be defined here if you re-add that feature.
    # For now, we'll use our generated lists.

    current_year = datetime.now().year
    years_to_generate = 50
    
    # Group 1: Numbers & Years
    full_years = [str(year) for year in range(current_year, current_year - years_to_generate - 1, -1)]
    two_digit_years = [datetime(year, 1, 1).strftime('%y') for year in range(current_year, current_year - years_to_generate - 1, -1)]
    simple_numbers = [str(i) for i in range(10)] + ["0" + str(i) for i in range(10)] + ["123", "12345"]
    
    numeric_affixes = full_years + two_digit_years + simple_numbers

    # Group 2: Symbols
    symbol_affixes = ["!", "@", "#", "$", "%", "^", "&", "*", "?", "_", "-"]

    # --- Generation Logic ---
    final_variations = {word} # Start with the base word

    # 1. Apply single prefixes and suffixes from ALL groups
    all_simple_affixes = numeric_affixes + symbol_affixes
    for affix in all_simple_affixes:
        final_variations.add(word + affix) # e.g., liverpool05
        # final_variations.add(affix + word) # e.g., 05liverpool
        final_variations.add(word + "!")   # e.g., liverpool!

    # 2. Create chained SUFFIXES (Number -> Symbol)
    # Take each numeric suffix, add it to the word, then add a symbol
    for num_suf in numeric_affixes:
        word_with_num_suf = word + num_suf
        for sym_suf in symbol_affixes:
            final_variations.add(word_with_num_suf + sym_suf) # e.g., liverpool05!

    # 3. Create chained PREFIXES (Symbol -> Number) - a common pattern
    # Take each symbol prefix, add it to the word, then add a number
    # for sym_pre in symbol_affixes:
    #     word_with_sym_pre = sym_pre + word
    #     for num_pre in numeric_affixes:
    #         final_variations.add(num_pre + word_with_sym_pre) # e.g., 05!liverpool

    for sym_suf in symbol_affixes:
        word_with_sym_suf = word + sym_suf
        for num_suf in numeric_affixes:
            final_variations.add(word_with_sym_suf + num_suf) # e.g., liverpool!05

    return list(final_variations)

# --- START OF MAJOR CHANGE AREA ---

def _generate_single_word_core_variations(base_word, mutation_config):
    """
    Generates Capitalisation and/or Leet Speak variations.
    If both are ON, Leet is applied to Capitalized versions.
    Affixes are NOT handled by this function.
    This function ALWAYS "combines" Caps and Leet if both are enabled.
    """
    # Start with the base word itself.
    # _apply_capitalisation already includes the original and lowercased versions.
    forms_after_caps = {base_word} # Ensure base_word is a starting point
    if mutation_config.get("capitalisation", False):
        forms_after_caps.update(_apply_capitalisation(base_word))
    else:
        forms_after_caps = {base_word.lower(), base_word} # If no caps, ensure at least lower and original

    # Now apply leet to all forms generated by capitalisation (or just the base_word/lower if caps was off)
    final_core_forms = set()
    if mutation_config.get("leet_speak", False):
        for form_cap in forms_after_caps:
            final_core_forms.update(_apply_leet_speak(form_cap))
    else:
        final_core_forms.update(forms_after_caps) # No leet speak, so use the forms after caps (or just base)

    return list(final_core_forms)


def generate_wordlist_logic(base_words, mutation_config, output_filename):
    """
    Memory-safe wordlist generation engine. Writes all candidates to a temp file,
    then uses external tools (sort/uniq) for safe, efficient processing.
    Returns a tuple: (final_count, message_string).
    """
    if not base_words:
        return 0, "Error: No base words provided for generation."
    if not output_filename:
        return 0, "Error: Output filename not set."

    print(f"\nStarting wordlist generation for {len(base_words)} base word(s)...")
    print(f"Output will be saved to: {output_filename}")
    print("Mode: Memory-Safe (streaming to disk)")
    affixes_enabled = mutation_config.get("affixes", False)
    # Use a secure temporary file that is automatically cleaned up after we are done with it
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_f:
        temp_filename = temp_f.name
        print(f"\nGenerating raw candidates to temporary file: {temp_filename}")
        
        raw_candidate_count = 0
        core_forms_for_concatenation_map = {}

        # --- Step 1: Process Single Words ---
        for i, base_word in enumerate(base_words):
            print(f"\rProcessing single-word forms for: '{base_word}'...", end="")

            core_variations = _generate_single_word_core_variations(base_word, mutation_config)
            core_forms_for_concatenation_map[base_word] = core_variations

            if affixes_enabled:
                for core_form in core_variations:
                    # --- CORRECTION ---
                    # Call the self-contained _apply_affixes function
                    final_variations = _apply_affixes(core_form)
                    # --- END CORRECTION ---
                    for final_form in final_variations:
                        temp_f.write(final_form + "\n")
                        raw_candidate_count += 1
            else:
                for core_form in core_variations:
                    temp_f.write(core_form + "\n")
                    raw_candidate_count += 1
        print() # Newline after the single word progress loop

        # --- Step 2: Concatenation ---
        if mutation_config.get("concatenation", False) and len(base_words) > 1:
            print("\nProcessing concatenations...")
            for i_idx in range(len(base_words)):
                word1_base = base_words[i_idx]
                print(f"\rConcatenating with '{word1_base}' as first word...", end="")
                for j_idx in range(len(base_words)):
                    if i_idx == j_idx and len(base_words) > 1: continue

                    word2_base = base_words[j_idx]
                    
                    forms1 = core_forms_for_concatenation_map.get(word1_base, [word1_base])
                    forms2 = core_forms_for_concatenation_map.get(word2_base, [word2_base])

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
    print(f"\nGenerated {raw_candidate_count:,} raw password candidates.")
    print("Now sorting and removing duplicates using system utilities...")
    print("This may take some time for very large files.")

    # Note: This requires 'sort' and 'uniq' to be available in the system's PATH.
    # This is standard on Linux, macOS, and WSL, but not on vanilla Windows.
    command = f'sort "{temp_filename}" | uniq > "{output_filename}"'
    
    try:
        # Using shell=True for the pipe '|' functionality. Use with caution, but necessary here.
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
    except FileNotFoundError:
        message = "[FATAL ERROR] `sort` or `uniq` command not found. Please ensure these standard utilities are in your system's PATH. The raw temp file has been kept for manual processing."
        # Don't delete temp_filename in this case, so user can process it.
        return 0, message
    except subprocess.CalledProcessError as e:
        message = f"[FATAL ERROR] Post-processing failed:\n{e.stderr}\nThe raw temp file has been kept for manual processing."
        # Don't delete temp_filename in this case
        return 0, message
    finally:
        # In case of success, we must clean up the temporary file.
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
        return -1, message # Use a special value to indicate success but count failed


def trigger_wordlist_generation(state):
    """
    Calculates an estimate, shows it to the user for confirmation,
    and then triggers the wordlist generation.
    """
    tui.clear_screen()
    print("--- Generation Preview & Resource Estimate ---\n")

    base_words = state.get('words_for_engine', [])
    mutation_config = state.get('mutation_config', {})
    output_filename = state.get('output_filename', 'wordlist.txt')

    if not base_words:
        print("No words selected for the engine. Cannot generate."); tui.pause(); return
    
    # 2. Display the detailed estimates to the user
    tui.clear_screen()
    print("--- Generation Preview & Resource Estimate ---\n")
    estimate.estimate_list_size(state)
    
    # 3. Ask for confirmation AFTER showing the estimate
    confirm = input("\nProceed with generation? (yes/no): ").strip().lower()
    if confirm == 'yes':
        # 4. Call the actual generation logic
        count, message = generate_wordlist_logic(base_words, mutation_config, output_filename)
        print(f"\n{message}")
    else:
        print("\nGeneration cancelled.")
    tui.pause()
