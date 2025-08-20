import os
import sys 
import agent
import fileIO
import review 
import mutations 
import estimate
import generate 

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Pauses execution until user presses Enter."""
    input("\nPress Enter to continue...")


def display_main_menu(state):
    """Displays the main menu and current status."""
    clear_screen()
    print("=============================================")
    print("      AI-Enhanced Password List Generator    ")
    print("=============================================")
    print()   
    print(f" Status:")
    print(f"  - Azure Endpoint Set: {'Yes' if state['endpoint'] else 'No'}")
    print(f"  - Azure Key Set:      {'Yes' if state['key'] else 'No'}")
    print(f"  - AI Client Ready:    {'Yes' if state['client_ready'] else 'No'}") # Use the flag
    print(f"  - System Prompt File: {state['system_prompt_path']}")
    print(f"  - AI Model:           {state['model_name']}")
    print(f"  - Seed Words:         {len(state['seed_words'])} ({', '.join(state['seed_words'][:5])}{'...' if len(state['seed_words']) > 5 else ''})")
    print(f"  - AI Suggestions:     {len(state['ai_suggestions'])}")
    print(f"  - Words for Engine:   {len(state['words_for_engine'])}")
    config = state.get('mutation_config', {})
    enabled_muts = [key for key, enabled in config.items() if enabled]
    print(f"  - Enabled Mutations:  {len(enabled_muts)} ({', '.join(enabled_muts)})")
    print(f"  - Output File:        {state['output_filename']}")
    print()   
    print("---------------------------------------------")
    print()    
    print(" Main Menu:")
    print("  1. Set Azure Endpoint & Key")
    print("  2. Set System Prompt File")
    print("  3. Set AI Model Name")
    print("  4. Enter/Edit Seed Words")
    print("  5. Run AI Brainstorming (Requires 1, 2, 4)")
    print("  6. Review/Filter AI Suggestions")
    print("  7. Configure Mutations")  
    print("  8. Set Output Filename")
    print("  9. Generate Wordlist")
    print()   
    print(" [type 'exit' to gracefully exit the program]")
    print()   
    print("=============================================")
    print()   

if __name__ == "__main__":
    # Initial state
    app_state = {
        "endpoint": None,
        "key": None,
        "client_ready": False, 
        "system_prompt_path": "CreativePrompt.txt", 
        "model_name": "gpt-4o-mini", 
        "seed_words": [],
        "ai_suggestions": [],
        "words_for_engine": [],
        "mutation_config": {
            "capitalisation": True,
                "leet_speak": False,
                "concatenation": True,
                "affixes": True
            },
        "output_filename": "wordlist.txt"
    }

    while True:
        display_main_menu(app_state)
        choice = input(f"Enter your choice (1-{len(app_state)+1}): ") 
        if choice == '1':
            agent.get_azure_details(app_state)
        elif choice == '2':
            fileIO.set_system_prompt(app_state)
        elif choice == '3':
            agent.set_model_name(app_state)
        elif choice == '4':
            review.get_seed_words(app_state)
        elif choice == '5':
            agent.run_ai_brainstorming(app_state)
        elif choice == '6':
            review.review_filter_suggestions(app_state)
        elif choice == '7':
            mutations.configure_mutations(app_state)
        elif choice == '8':
            fileIO.set_output_filename(app_state)
        elif choice == '9':
            generate.trigger_wordlist_generation(app_state)
        elif choice == 'exit':
            print("Exiting...")
            sys.exit(0)
        else:
            print("\nInvalid choice, please try again.")
            pause()

    print("Goodbye!") 
