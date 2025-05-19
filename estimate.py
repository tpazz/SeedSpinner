import math # For log2
from collections import Counter # For character frequency counting
import os # Keep os for file exists checks if needed elsewhere
import tui

# ... (your existing helper functions like _apply_capitalisation, etc.) ...
# ... (_generate_simple_preview function) ...

def _generate_simple_preview(base_words, mutation_config, max_preview=10):
    """
    Generates a small preview list of potential passwords.
    This is a simplified generator, not the full engine.
    """
    preview_list = set() # Use a set to get unique examples quickly

    if not base_words:
        return list(preview_list)

    # Limit processing to a few base words for preview speed
    words_to_preview = base_words[:max(3, max_preview // 5)] # Preview 3 words or 1/5th of max_preview

    for base_word in words_to_preview:
        if len(preview_list) >= max_preview: break

        current_forms = {base_word} # Start with the base word

        # 1. Capitalisation
        if mutation_config.get("capitalisation", False):
            new_caps = set()
            for form in current_forms:
                if len(preview_list) >= max_preview: break
                new_caps.add(form.lower())
                new_caps.add(form.title())
                new_caps.add(form.upper())
            current_forms.update(new_caps)
            for p in new_caps:
                if len(preview_list) < max_preview: preview_list.add(p)
                else: break
        else: # Add base form if no caps
            if len(preview_list) < max_preview: preview_list.add(base_word)


        # 2. Leet Speak (Very Simple Preview Version)
        if mutation_config.get("leet_speak", False):
            new_leets = set()
            temp_current_forms_for_leet = set(current_forms) # Apply leet to existing forms
            for form in temp_current_forms_for_leet:
                if len(preview_list) >= max_preview: break
                leet_form = form.replace('a', '@').replace('A', '@') \
                               .replace('e', '3').replace('E', '3') \
                               .replace('o', '0').replace('O', '0') \
                               .replace('i', '1').replace('I', '1') \
                               .replace('s', '$').replace('S', '$')
                if leet_form != form: # Add only if changed
                    new_leets.add(leet_form)
            current_forms.update(new_leets)
            for p in new_leets:
                if len(preview_list) < max_preview: preview_list.add(p)
                else: break

        # 3. Suffix/Prefix Addition (Simple Preview Version)
        if mutation_config.get("affixes", False):
            simple_affixes = ["123", "!", "2024"] # A few example affixes
            new_affixed = set()
            temp_current_forms_for_affix = set(current_forms) # Apply affixes to existing forms
            for form in temp_current_forms_for_affix:
                if len(preview_list) >= max_preview: break
                for affix in simple_affixes:
                    new_affixed.add(form + affix)
                    new_affixed.add(affix + form)
            current_forms.update(new_affixed)
            for p in new_affixed:
                if len(preview_list) < max_preview: preview_list.add(p)
                else: break

        # Add all current forms for this base_word to preview_list (up to max_preview)
        for form in current_forms:
            if len(preview_list) < max_preview:
                preview_list.add(form)
            else:
                break
        if len(preview_list) >= max_preview: break


    # 4. Concatenation (Simple Preview - combine first few base words)
    if mutation_config.get("concatenation", False) and len(base_words) > 1:
        if len(preview_list) < max_preview:
            preview_list.add(base_words[0] + base_words[1 % len(base_words)]) # word1word2
        if len(preview_list) < max_preview and len(base_words) > 1:
            # A simple capitalized concat
            word1_cap = base_words[0].title() if mutation_config.get("capitalisation", False) else base_words[0]
            word2_cap = base_words[1 % len(base_words)].title() if mutation_config.get("capitalisation", False) else base_words[1 % len(base_words)]
            preview_list.add(word1_cap + word2_cap)

    # Ensure the list is sorted for consistent preview display
    return sorted(list(preview_list))[:max_preview]

def _calculate_string_list_char_entropy(string_list):
    """
    Calculates the Shannon entropy of the character distribution in a list of strings.
    Returns the entropy value (bits per character) or None if the list is empty/invalid.
    """
    if not string_list:
        return 0.0 # Or None, depending on how you want to handle empty preview

    char_counts = Counter()
    total_chars = 0

    for s in string_list:
        if not isinstance(s, str): # Basic type check
            continue
        password = s.strip() # Should already be clean from preview generator
        if not password:
            continue
        char_counts.update(password)
        total_chars += len(password)

    if total_chars == 0:
        return 0.0

    entropy = 0.0
    for char_code in char_counts:
        probability = char_counts[char_code] / total_chars
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy


def estimate_list_size(state):
    """
    Estimates the potential size of the wordlist, shows a preview,
    and preview entropy, reflecting the current generation logic.
    """
    tui.clear_screen()
    print("--- Estimate Wordlist Size & Preview ---")

    base_words = state.get('words_for_engine', [])
    mutation_config = state.get('mutation_config', {})

    if not base_words:
        print("No words selected for the engine. Cannot estimate or preview.")
        print("Please enter seed words (Option 4) and optionally run AI/filter.")
        tui.pause()
        return

    num_base_words = len(base_words)
    avg_word_length = sum(len(w) for w in base_words) / num_base_words if num_base_words > 0 else 0
    
    print(f"Estimating based on {num_base_words} base word(s) in 'Words for Engine'.")
    print("Enabled mutations:")
    enabled_mutations_display = []
    # "combine_mutations" is no longer a user toggle, it's implicit for Caps/Leet
    for key, display_name in [
        ("capitalisation", "Capitalisation"), ("leet_speak", "Leet Speak"),
        ("concatenation", "Concatenation"), ("affixes", "Suffixes/Prefixes")
    ]:
        if mutation_config.get(key, False):
            enabled_mutations_display.append(display_name)
    
    if enabled_mutations_display:
        print(f"  - {', '.join(enabled_mutations_display)}")
        if mutation_config.get("capitalisation") and mutation_config.get("leet_speak"):
            print("    (Note: Capitalisation and Leet Speak effects will be combined)")
    else:
        print("  - No mutations enabled (list will contain base words only).")
    print("-------------------------------------")

    # --- Preview Generation ---
    # Ensure _generate_simple_preview and _calculate_string_list_char_entropy are defined
    # and accessible in this scope (e.g., imported or defined in the same file)
    preview_passwords = _generate_simple_preview(base_words, mutation_config, max_preview=20) # Increased max_preview
    if preview_passwords:
        print("\nPreview of potential generated passwords (sample unique examples):")
        for i, p_word in enumerate(preview_passwords):
            print(f"  {i+1:2d}. {p_word}")
        
        preview_entropy = _calculate_string_list_char_entropy(preview_passwords)
        if preview_entropy is not None:
            print("\n-------------------------------------\n")
            print(f"Approx. Character Entropy of this Preview: {preview_entropy:.3f} bits/char")
            print("(Based on the sample above; full list entropy may differ.)\n")
    else:
        print("Preview: No example passwords generated (check base words/mutations).")
    print("-------------------------------------")

    # --- Estimation Logic (Reflecting implicit Caps+Leet combine, then Affixes) ---
    
    # 1. Calculate core variations per word (Caps and/or Leet, implicitly combined)
    # This factor represents the output of _generate_single_word_core_variations
    core_variations_per_word_factor = 1.0
    
    # If only capitalisation is ON (or if neither, but we start with base)
    if mutation_config.get("capitalisation", False):
        # _apply_capitalisation typically returns {word, Word, WORD, original} -> ~3-4 distinct forms.
        # Let's use a factor of 3 for word, Word, WORD.
        factor_from_caps = 3 
    else:
        factor_from_caps = 1 # Just the base word (or its lowercase)

    # If Leet is ON, it applies to each of the capitalized forms (or base if caps off)
    if mutation_config.get("leet_speak", False):
        # Estimate how many distinct forms _apply_leet_speak creates from ONE input string.
        # This is highly dependent on your _apply_leet_speak implementation.
        # If it's recursive and creates many, this factor could be high.
        # For a simpler leet that might make 3-5 variants including original:
        leet_expansion_factor = 4 # Example: input -> input, leet1, leet2, leet3
        core_variations_per_word_factor = factor_from_caps * leet_expansion_factor
    else:
        core_variations_per_word_factor = factor_from_caps

    # 2. Calculate affix factor (applied to core variations and concatenated strings)
    num_common_affixes = 20 # Matches your _apply_affixes list size (approx)
    affix_application_factor = 1 # Represents the word itself (no affix)
    if mutation_config.get("affixes", False):
        # Each core variation can get (num_common_affixes * 2) new forms + itself
        affix_application_factor = (1 + num_common_affixes * 2)

    # 3. Calculate lines from single words
    # Each base word produces 'core_variations_per_word_factor' forms.
    # Each of those then gets 'affix_application_factor' forms.
    estimated_lines_single = num_base_words * core_variations_per_word_factor * affix_application_factor
    
    # 4. Calculate lines from concatenation
    estimated_lines_concat = 0
    if mutation_config.get("concatenation", False) and num_base_words > 1:
        # Number of raw pairs of original base words.
        # If self-concatenation is allowed (e.g., test+test, apple+apple):
        num_raw_pairs = num_base_words * num_base_words
        # If self-concatenation is skipped:
        # num_raw_pairs = num_base_words * (num_base_words - 1) 
        # Assuming your current concat loop DOES include self-concat for estimation.

        # Each word in the pair contributes its 'core_variations_per_word_factor'
        # So, a concatenated pair before affixing has:
        # core_variations_per_word_factor * core_variations_per_word_factor possibilities
        variations_per_raw_concatenated_pair = core_variations_per_word_factor * core_variations_per_word_factor
        
        # These concatenated strings are then affixed
        estimated_lines_concat = num_raw_pairs * variations_per_raw_concatenated_pair * affix_application_factor
    
    estimated_lines = estimated_lines_single + estimated_lines_concat

    # Note: This addition might overcount if a fully formed single word is identical to a
    # fully formed concatenated word (unlikely with typical inputs but possible).
    # Deduplication in the actual generation handles this.

    print(f"\nEstimated Maximum Lines (upper bound): ~{int(estimated_lines):,}")
    
    # --- File Size Estimation (using the new estimated_lines) ---
    avg_len_factor_concat = 1.0
    if mutation_config.get("concatenation", False) and num_base_words > 1:
        # If concatenating, average length roughly doubles, but some words are short, some long.
        # Let's assume the core variations don't change length much, so concat doubles avg_word_length.
        avg_len_factor_concat = 2.0 
    
    avg_affix_len_contribution = 0
    if mutation_config.get("affixes", False):
        # Average length of one of your common_affixes
        # e.g., "123" is 3, "!" is 1. Average might be 2-3.
        avg_affix_len_contribution = 2.5 

    # Base average length + potential doubling from concat + potential affix length
    estimated_avg_pass_len = (avg_word_length * avg_len_factor_concat) + avg_affix_len_contribution
    estimated_avg_pass_len = max(estimated_avg_pass_len, 1) # Ensure at least 1

    estimated_file_size_bytes = estimated_lines * (estimated_avg_pass_len + 1) # +1 for newline

    if estimated_file_size_bytes < 1024:
        size_display = f"{estimated_file_size_bytes:.0f} Bytes"
    elif estimated_file_size_bytes < 1024**2:
        size_display = f"{estimated_file_size_bytes / 1024:.2f} KB"
    elif estimated_file_size_bytes < 1024**3:
        size_display = f"{estimated_file_size_bytes / (1024**2):.2f} MB"
    else:
        size_display = f"{estimated_file_size_bytes / (1024**3):.2f} GB"

    print(f"Estimated Maximum File Size: ~{size_display}\n")
    print("-------------------------------------")
    tui.pause()

# calculate_wordlist_char_entropy (for files) and trigger_wordlist_generation
# remain the same as the previous version that included them.