import math
from collections import Counter
import os
import datetime # Make sure this is imported
import tui

# --- Helper Functions (Keep these as they are) ---

def _generate_simple_preview(base_words, mutation_config, max_preview=20):
    """
    Generates a robust, varied preview list of up to max_preview passwords
    by sampling each enabled mutation type.
    """
    preview_list = set()

    if not base_words:
        return []

    # 1. Add some of the original base words to start
    for word in base_words:
        if len(preview_list) >= max_preview: break
        preview_list.add(word)

    # Use the first and second words for specific examples
    first_word = base_words[0]
    second_word = base_words[1] if len(base_words) > 1 else base_words[0]

    # 2. Add Capitalisation samples
    if mutation_config.get("capitalisation", False):
        if len(preview_list) < max_preview: preview_list.add(first_word.title())
        if len(preview_list) < max_preview: preview_list.add(first_word.upper())
        if len(preview_list) < max_preview: preview_list.add(second_word.title())

    # 3. Add Leet Speak samples
    if mutation_config.get("leet_speak", False):
        # Create a simple leeted version of the first word
        leet_sample_1 = first_word.lower().replace('e', '3').replace('a', '@').replace('s', '$').replace('o', '0')
        if len(preview_list) < max_preview: preview_list.add(leet_sample_1)
        # Create a simple leeted version of a capitalized second word (to show combination)
        leet_sample_2 = second_word.title().replace('e', '3').replace('a', '@').replace('s', '$').replace('o', '0')
        if len(preview_list) < max_preview: preview_list.add(leet_sample_2)

    # 4. Add Affix samples
    if mutation_config.get("affixes", False):
        if len(preview_list) < max_preview: preview_list.add(first_word + "123")
        if len(preview_list) < max_preview: preview_list.add("!" + first_word)
        if len(preview_list) < max_preview: preview_list.add(second_word.title() + "24") # Show affix on a capitalized word

    # 5. Add Concatenation samples
    if mutation_config.get("concatenation", False) and len(base_words) > 1:
        if len(preview_list) < max_preview: preview_list.add(first_word + second_word)
        if len(preview_list) < max_preview: preview_list.add(second_word + first_word)
        # Show a capitalized concatenation
        if len(preview_list) < max_preview:
             preview_list.add(first_word.title() + second_word.title())

    # 6. Add a complex combined sample if all major mutations are on
    if all(mutation_config.get(k) for k in ["capitalisation", "leet_speak", "affixes", "concatenation"]) and len(base_words) > 1:
        complex_sample = second_word.upper().replace('S', '$').replace('E', '3') + first_word.lower().replace('a','@') + "!"
        if len(preview_list) < max_preview: preview_list.add(complex_sample)

    # 7. Final fill-up with base words if there's still space
    for word in base_words:
        if len(preview_list) >= max_preview: break
        preview_list.add(word)

    return sorted(list(preview_list))[:max_preview]

def _calculate_string_list_char_entropy(string_list):
    # This function is for the preview entropy, its logic is fine.
    # (Your existing _calculate_string_list_char_entropy code goes here)
    # ...
    if not string_list: return 0.0
    char_counts = Counter("".join(string_list))
    total_chars = sum(char_counts.values())
    if total_chars == 0: return 0.0
    entropy = -sum((count/total_chars) * math.log2(count/total_chars) for count in char_counts.values())
    return entropy

# --- New, Accurate Estimation Engine (Keep these as they are) ---

def _estimate_leet_outputs(word, mutation_config):
    """
    Analyzes a word to provide a more accurate upper bound of leet speak variations
    by calculating the combinatorial permutations of enabled substitutions.
    """
    if not mutation_config.get("leet_speak", False):
        return 1

    leet_rules = {
        'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'], 's': ['$', '5'], 't': ['7']
    }
    
    total_combinations = 1
    for char in word:
        lower_char = char.lower()
        if lower_char in leet_rules:
            num_options = 1 + len(leet_rules[lower_char])
            total_combinations *= num_options
            
    return total_combinations

def _calculate_upper_bound_estimate(base_words, mutation_config):
    """
    Calculates a more pessimistic and realistic upper bound for lines, file size, and memory.
    This function mirrors the main generation logic's multiplicative nature.
    """
    num_base_words = len(base_words)
    if num_base_words == 0:
        return {'lines': 0, 'size_bytes': 0, 'memory_bytes': 0}

    # Factors and Affix Lists - this part remains the same
    num_common_numbers = len([str(i) for i in range(10)] + ["0" + str(i) for i in range(10)] + ["123", "007", "12345"])
    current_year = datetime.datetime.now().year
    num_years = len([str(y) for y in range(current_year, current_year - 51, -1)]) * 2
    num_common_symbols = 11
    total_affix_count = num_common_numbers + num_years + num_common_symbols
    affix_application_factor = 1 + total_affix_count * 2 if mutation_config.get("affixes", False) else 1

    # Estimate Core Variations for EACH word - this part remains the same
    estimated_core_variations_map = {}
    for word in base_words:
        caps_factor = 3 if mutation_config.get("capitalisation", False) else 1
        leet_factor = _estimate_leet_outputs(word.lower(), mutation_config)
        estimated_core_variations_map[word] = caps_factor * leet_factor

    # Calculate Total Lines - this part remains the same
    estimated_lines_single_raw = 0
    for word in base_words:
        estimated_lines_single_raw += estimated_core_variations_map[word] * affix_application_factor
    estimated_lines_concat_raw = 0
    if mutation_config.get("concatenation", False):
        for word1 in base_words:
            for word2 in base_words:
                num_pairs = estimated_core_variations_map[word1] * estimated_core_variations_map[word2]
                estimated_lines_concat_raw += num_pairs * affix_application_factor
    estimated_total_lines_raw = estimated_lines_single_raw + estimated_lines_concat_raw

    # Estimate File Size and Memory - this part remains the same
    avg_word_length = sum(len(w) for w in base_words) / num_base_words
    avg_len_factor_concat = 2.0 if mutation_config.get("concatenation", False) else 1.0
    avg_affix_len = 3.0 if mutation_config.get("affixes", False) else 0.0
    estimated_avg_pass_len = (avg_word_length * avg_len_factor_concat) + avg_affix_len
    estimated_file_size_bytes = estimated_total_lines_raw * (estimated_avg_pass_len + 1)
    avg_obj_overhead = 60
    estimated_memory_for_set_bytes = estimated_total_lines_raw * (avg_obj_overhead + estimated_avg_pass_len)

    return {
        'lines': estimated_total_lines_raw,
        'size_bytes': estimated_file_size_bytes,
        'memory_bytes': estimated_memory_for_set_bytes
    }    

# --- START OF FIX: Replace your old `estimate_list_size` with this corrected version ---

def estimate_list_size(state):
    """
    Main TUI function. It calls the accurate estimation engine and then formats the output.
    """

    base_words = state.get('words_for_engine', [])
    mutation_config = state.get('mutation_config', {})

    if not base_words:
        print("No words selected for the engine. Cannot estimate or preview.")
        tui.pause()
        return

    # --- Display Info (same as your old function) ---
    print(f"Estimating based on {len(base_words)} base word(s) in 'Words for Engine'.")
    print("Enabled mutations:")
    enabled_mutations_display = []
    for key, display_name in [
        ("capitalisation", "Capitalisation"), ("leet_speak", "Leet Speak"),
        ("concatenation", "Concatenation"), ("affixes", "Suffixes/Prefixes")
    ]:
        if mutation_config.get(key, False):
            enabled_mutations_display.append(display_name)
    if enabled_mutations_display:
        print(f"  - {', '.join(enabled_mutations_display)}")
    else:
        print("  - No mutations enabled (list will contain base words only).")
    print("\n-------------------------------------")

    # --- Preview Generation (same as your old function) ---
    preview_passwords = _generate_simple_preview(base_words, mutation_config, max_preview=20)
    if preview_passwords:
        print("\nPreview of potential generated passwords (sample unique examples):")
        for i, p_word in enumerate(preview_passwords):
            print(f"  {i+1:2d}. {p_word}")
        preview_entropy = _calculate_string_list_char_entropy(preview_passwords)
        if preview_entropy is not None:
            print("\n-------------------------------------\n")
            print(f"Approx. Character Entropy of this Preview: {preview_entropy:.3f} bits/char")
    else:
        print("Preview: No example passwords generated.")
    print("\n-------------------------------------")
    
    # --- HERE IS THE FIX: Call the correct, accurate estimation engine ---
    estimates = _calculate_upper_bound_estimate(base_words, mutation_config)

    # --- Display the results from the accurate engine ---
    print(f"\n~ Max Passwords (upper bound): ~{int(estimates['lines']):,}")
    
    # File size formatting
    size_bytes = estimates['size_bytes']
    if size_bytes < 1024: size_display = f"{size_bytes:.0f} Bytes"
    elif size_bytes < 1024**2: size_display = f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3: size_display = f"{size_bytes / (1024**2):.2f} MB"
    else: size_display = f"{size_bytes / (1024**3):.2f} GB"
    print(f"~ Max File Size (upper bound): ~{size_display}")
    print("\n-------------------------------------")
    tui.pause()

# --- END OF FIX ---