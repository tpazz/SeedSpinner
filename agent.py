import os
import tui
import fileIO
from openai import AzureOpenAI

# Module-level variable to hold the single, shared Azure OpenAI client instance.
_client = None

def initialize_client(endpoint: str, key: str) -> tuple[bool, str]:
    """Initializes or re-initializes the global Azure OpenAI client."""
    global _client
    if not endpoint or not key:
        _client = None
        return False, "Endpoint and Key are required."
    try:
        print("Initializing Azure OpenAI client...")
        _client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_version="2024-02-01",
            api_key=key
        )
        print("Client initialized successfully.")
        return True, "Azure OpenAI client initialized successfully."
    except Exception as e:
        _client = None # Ensure client is None on failure
        error_message = f"Failed to create Azure OpenAI client: {e}"
        print(f"\n[Error] {error_message}")
        return False, error_message

def get_ai_suggestions(system_prompt_content: str, user_prompt_content: str, model_name: str) -> list[str] | None:
    """Sends the prompts to the Azure OpenAI API and processes the response."""
    if not _client:
        print("\n[Error] Azure OpenAI client is not initialized.\n")
        return None

    if not system_prompt_content or not user_prompt_content:
        print("\n[Error] System or User prompt content is missing.\n")
        return None

    # Structure the conversation for the chat model
    messages = [
        {"role": "system", "content": system_prompt_content.strip()},
        {"role": "user", "content": user_prompt_content.strip()}
    ]

    print(f"Sending request to AI model '{model_name}'...")
    try:
        completion = _client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        response_content = completion.choices[0].message.content
        print("AI response received.")

        # Process the raw text response into a clean list of words, one per line.
        suggested_words = [word.strip() for word in response_content.splitlines() if word.strip()]

        if not suggested_words:
             print("[Warning] AI returned an empty list of suggestions.")
             return [] # Return an empty list to signify success with no results

        return suggested_words
    except Exception as e:
        print(f"\n[Error] Failed to get response from AI: {e}")
        return None

# --- UI Interaction Functions ---
# These functions are called directly from the TUI menu options.
# They act as a bridge between the user interface and the core AI logic.

def run_ai_brainstorming(state):
    """Orchestrates the AI brainstorming process based on the current application state."""
    tui.clear_screen()
    print("--- Run AI Brainstorming ---\n")

    # Prerequisite checks to ensure the tool is ready for an AI call
    if not state['client_ready']:
        print("[Error] Azure client not ready. Please set endpoint/key first (Option 1)."); tui.pause(); return
    if not state['system_prompt_path'] or not os.path.exists(state['system_prompt_path']):
        print("[Error] System prompt file not set or not found. Please set it first (Option 2)."); tui.pause(); return
    if not state['seed_words']:
        print("[Error] No seed words entered. Please enter seed words first (Option 4)."); tui.pause(); return

    # Read the system prompt from the specified file
    system_prompt_content = fileIO.read_prompt_file(state['system_prompt_path'])
    if system_prompt_content is None: tui.pause(); return # Error is handled in read function

    # Format the user's seed words into a single string for the AI prompt
    user_prompt_content = f"Expand these seed words: {', '.join(state['seed_words'])}"

    # Call the core AI function to get suggestions
    suggestions = get_ai_suggestions(
        system_prompt_content=system_prompt_content,
        user_prompt_content=user_prompt_content,
        model_name=state['model_name']
    )

    if suggestions is not None: # Check for success (None indicates an error)
        # Combine original seeds with AI suggestions, removing duplicates while preserving order
        state['ai_suggestions'] = list(dict.fromkeys(state['seed_words'] + suggestions))
        # Update the main list of words to be used by the generation engine
        state['words_for_engine'] = list(state['ai_suggestions'])
        print(f"\nBrainstorming complete.")
        print(f"Words for engine updated to {len(state['words_for_engine'])} unique terms (Seeds + AI Suggestions).")
        print("Use Option 6 (Review/Filter) to refine this list if needed.")
    else:
        print("\nAI Brainstorming failed or returned no results. Words for engine remain unchanged.")
    tui.pause()

def set_model_name(state):
    """Prompts the user to set the AI model (deployment name) and updates the state."""
    tui.clear_screen()
    print("--- Set AI Model Name ---\n")
    print("Enter the deployment name of your Azure OpenAI model.")
    current_model = state.get('model_name', 'Not Set')
    new_model = input(f"Model name [Current: {current_model}]: ").strip()
    if new_model:
        state['model_name'] = new_model
        print(f"AI Model set to: {state['model_name']}")
    else:
        print("No changes made.")
    tui.pause()    


def get_azure_details(state):
    """Prompts the user for Azure credentials and initializes the AI client."""
    tui.clear_screen()
    print("--- Set Azure OpenAI Credentials ---\n")
    endpoint = input(f"Enter Azure Endpoint [Current: {state.get('endpoint', 'Not Set')}]: ")
    key = input(f"Enter Azure API Key [Current: {'******' if state.get('key') else 'Not Set'}]: ")

    # Update state with any new values provided
    if endpoint:
        state['endpoint'] = endpoint.strip()
    if key:
        state['key'] = key.strip()

    # Attempt to initialize the client only if both endpoint and key are present
    if state.get('endpoint') and state.get('key'):
        success, message = initialize_client(state['endpoint'], state['key'])
        state['client_ready'] = success # Update the 'client_ready' flag for other functions
        print(f"\n{message}")
    else:
        state['client_ready'] = False
        print("\n[Warning] Endpoint or Key not fully provided. AI Client not initialized.")
    tui.pause()