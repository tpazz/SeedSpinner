# ai_agent.py
import os
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
