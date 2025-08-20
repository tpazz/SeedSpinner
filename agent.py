# ai_agent.py
import os
import tui
import fileIO
from openai import AzureOpenAI

# Module-level variable to hold the client instance
_client = None

def initialize_client(endpoint: str, key: str) -> tuple[bool, str]:
    """
    Initializes the Azure OpenAI client.

    Args:
        endpoint: The Azure OpenAI endpoint URL.
        key: The Azure OpenAI API key.

    Returns:
        A tuple (success: bool, message: str).
        success is True if client initialized okay, False otherwise.
        message provides status or error details.
    """
    global _client
    if not endpoint or not key:
        _client = None
        return False, "Endpoint and Key are required."
    try:
        print("Initializing Azure OpenAI client...") # Feedback during init
        _client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_version="2024-02-01", # Consider making this configurable too
            api_key=key
        )
        # Optional: Add a simple test call here to verify connection/key
        # e.g., list models, though this might incur a small cost/token usage
        print("Client initialized successfully.")
        return True, "Azure OpenAI client initialized successfully."
    except Exception as e:
        _client = None
        error_message = f"Failed to create Azure OpenAI client: {e}"
        print(f"\n[Error] {error_message}")
        return False, error_message

def get_ai_suggestions(system_prompt_content: str, user_prompt_content: str, model_name: str) -> list[str] | None:
    """
    Calls the Azure OpenAI API to get keyword suggestions.

    Args:
        system_prompt_content: The full content of the system prompt.
        user_prompt_content: The full content for the user message.
        model_name: The deployment name of the model to use.

    Returns:
        A list of suggested words/terms (strings) on success, or None on failure.
    """
    if not _client:
        print("\n[Error] Azure OpenAI client is not initialized.")
        return None

    if not system_prompt_content or not user_prompt_content:
        print("\n[Error] System or User prompt content is missing.")
        return None

    messages = [
        {"role": "system", "content": system_prompt_content.strip()},
        {"role": "user", "content": user_prompt_content.strip()}
    ]

    print(f"\nSending request to AI model '{model_name}'...")
    try:
        completion = _client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        response_content = completion.choices[0].message.content
        print("AI response received.")

        # Process the response: split into lines, strip whitespace, remove empty lines
        suggested_words = [word.strip() for word in response_content.splitlines() if word.strip()]

        if not suggested_words:
             print("[Warning] AI returned an empty list of suggestions.")
             return [] # Return empty list rather than None if call succeeded but no words

        return suggested_words
    except Exception as e:
        print(f"\n[Error] Failed to get response from AI: {e}")
        return None

def run_ai_brainstorming(state):
    """Triggers AI brainstorming and updates words_for_engine with the combined results."""
    tui.clear_screen()
    print("--- Run AI Brainstorming ---\n")

    # Prerequisites check (remains the same)
    if not state['client_ready']:
        print("[Error] Azure client not ready. Please set endpoint/key first (Option 1)."); tui.pause(); return
    if not state['system_prompt_path'] or not os.path.exists(state['system_prompt_path']):
        print("[Error] System prompt file not set or not found. Please set it first (Option 2)."); tui.pause(); return
    if not state['seed_words']:
        print("[Error] No seed words entered. Please enter seed words first (Option 4)."); tui.pause(); return

    # Read system prompt content (remains the same)
    system_prompt_content = fileIO.read_prompt_file(state['system_prompt_path'])
    if system_prompt_content is None: tui.pause(); return

    # Prepare user prompt content (remains the same)
    user_prompt_content = f"Expand these seed words: {', '.join(state['seed_words'])}"

    # Call the agent function (remains the same)
    suggestions = get_ai_suggestions(
        system_prompt_content=system_prompt_content,
        user_prompt_content=user_prompt_content,
        model_name=state['model_name']
    )

    if suggestions is not None: # Check if call succeeded
        # Store the raw suggestions (including seeds) - good for potential future reference
        state['ai_suggestions'] = list(dict.fromkeys(state['seed_words'] + suggestions))

        # --- Key Change Below ---
        # Update words_for_engine directly to the combined & deduplicated list
        state['words_for_engine'] = list(state['ai_suggestions'])
        # --- End Key Change ---

        print(f"\nBrainstorming complete.")
        print(f"Words for engine updated to {len(state['words_for_engine'])} unique terms (Seeds + AI Suggestions).")
        print("Use Option 6 (Review/Filter) to refine this list if needed.")
    else:
        print("\nAI Brainstorming failed or returned no results. Words for engine remain unchanged.")
    tui.pause()


def set_model_name(state):
    """Sets the AI model name (deployment name)."""
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
    """Prompts user for Azure endpoint and key and initializes client via agent."""
    tui.clear_screen()
    print("--- Set Azure OpenAI Credentials ---\n")
    endpoint = input(f"Enter Azure Endpoint [Current: {state.get('endpoint', 'Not Set')}]: ")
    key = input(f"Enter Azure API Key [Current: {'******' if state.get('key') else 'Not Set'}]: ")

    # Update state immediately even if initialization fails later
    if endpoint:
        state['endpoint'] = endpoint.strip()
    if key:
        state['key'] = key.strip()

    # Attempt to initialize client via the agent function
    if state.get('endpoint') and state.get('key'):
        success, message = initialize_client(state['endpoint'], state['key'])
        state['client_ready'] = success
        print(f"\n{message}") # Display status/error message from agent
    else:
        state['client_ready'] = False
        print("\n[Warning] Endpoint or Key not fully provided. AI Client not initialized.")
    tui.pause()

