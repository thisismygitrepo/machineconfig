
# as per https://github.com/marketplace/models/azure-openai/o1-preview
from openai import OpenAI
from crocodile.file_management import Read, P


gh_token = Read.ini(P.home().joinpath("dotfiles/creds/git/git_host_tokens.ini"))['thisismygitrepo']['newLongterm']
endpoint = "https://models.inference.ai.azure.com"
model_name_preferences = ["o1-preview", "o1-mini", "GPT-4o", "GPT-4-o-mini"]
client__ = OpenAI(
    base_url=endpoint,
    api_key=gh_token,
)

def get_response(client, model_name, messages):
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=model_name
        )
        return response.choices
    except Exception as e:
        print(f"Error with model {model_name}: {e}")
        return None


def interactive_chat():
    conversation_history = []
    model_index = 0
    model_name = model_name_preferences[model_index]
    while True:
        print(f"Using model {model_name}".center(80, "="))
        while True:
            user_input = input("You: ")
            conversation_history.append({"role": "user", "content": user_input})

            while True:
                choices = get_response(client__, model_name, conversation_history)
                if choices is None:
                    model_index += 1
                    model_name = model_name_preferences[model_index % len(model_name_preferences)]
                    print(f"Switching to model {model_name}".center(80, "="))
                    continue
                else:
                    break

            for a_choice in choices:
                response_content = a_choice.message.content
                print("\n" * 5)
                print(f"AI: {response_content}")
                conversation_history.append({"role": "assistant", "content": response_content})

interactive_chat()
