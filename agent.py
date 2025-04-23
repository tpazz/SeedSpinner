import os
from openai import AzureOpenAI
import json
import argparse

def create_client(endpoint, key):
    try:
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_version="2024-02-01",  
            api_key=key
        )
        return client
    except Exception as e:
        
        raise ValueError(f"Failed to create AzureOpenAI client: {e}")

def generate_completion(client, messages, model_name):
    if not client:
        raise ValueError("AzureOpenAI client is not initialized")
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return completion

def parse_messages(messages_list):
    parsed_messages = []
    if not messages_list:
         raise ValueError("No messages provided. Use --message argument")
    for msg in messages_list:
        try:
            if "|" not in msg:
                 raise ValueError(f"Invalid message format '{msg}'. Use 'role|content' or 'role|@file.txt'")

            role, content = msg.split("|", 1)  

            role = role.strip()
            content = content.strip()

            if not role:
                 raise ValueError(f"Role cannot be empty in message '{msg}'")

            if content.startswith("@"):
                file_path = content[1:]  
                if not file_path:
                     raise ValueError(f"File path cannot be empty after '@' in message '{msg}'")

                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read().strip()  # Read content from file
                    except Exception as e:
                         raise IOError(f"Error reading file '{file_path}': {e}")
                else:
                    raise FileNotFoundError(f"File '{file_path}' specified in message not found")
            elif not content:
                 pass
              
            parsed_messages.append({"role": role, "content": content})

        except ValueError as e:
            raise ValueError(f"Error parsing message '{msg}': {e}")
        except FileNotFoundError as e:
             raise e
        except IOError as e:
             raise e
        except Exception as e:
            raise RuntimeError(f"Unexpected error parsing message '{msg}': {e}")

    return parsed_messages

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with Azure OpenAI API")
    parser.add_argument("--endpoint", type=str, required=True,
                        help="Azure OpenAI endpoint URL (e.g., https://your-resource-name.openai.azure.com/)")
    parser.add_argument("--key", type=str, required=True,
                        help="Azure OpenAI API Key")
    parser.add_argument("--message", type=str, action="append",
                        help="Specify a message in 'role|content' format or 'role|@file.txt'. Can be used multiple times. Example: --message 'user|Hello!'")
    parser.add_argument("--model", type=str, default="gpt-4o-mini",
                        help="Specify the deployment name for Azure OpenAI")
    args = parser.parse_args()

    try:
        # 1. Create the client using arguments
        client = create_client(args.endpoint, args.key)
        # 2. Parse messages (check if messages were provided)
        if not args.message:
             print("Error: No messages provided. Use the --message argument.")
             exit(1)
        messages = parse_messages(args.message)
        # 3. Generate completion using the created client
        response = generate_completion(client, messages, args.model)
        print(response.choices[0].message.content)

    except (ValueError, FileNotFoundError, IOError, RuntimeError) as e:
        print(f"Error: {e}")
        exit(1) 
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1) 
