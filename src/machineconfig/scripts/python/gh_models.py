# # as per https://github.com/marketplace/models/azure-openai/o1-preview
# from openai import OpenAI
# from machineconfig.utils.path_reduced import P as PathExtended
# from machineconfig.utils.utils2 import read_ini
# from rich import print as rprint
# from rich.panel import Panel
# from typing import Any


# gh_token = read_ini(PathExtended.home().joinpath("dotfiles/creds/git/git_host_tokens.ini"))['thisismygitrepo']['newLongterm']
# endpoint = "https://models.inference.ai.azure.com"
# model_name_preferences = ["o3-mini", "o1-preview", "o1-mini", "GPT-4o", "GPT-4-o-mini"]
# client__ = OpenAI(
#     base_url=endpoint,
#     api_key=gh_token,
# )


# def get_response(client: Any, model_name: str, messages: list[dict[str, str]]):
#     print(f"""
# ┌────────────────────────────────────────────────────────────────
# │ 🤖 Querying Model: {model_name}
# │    Sending request to API...
# └────────────────────────────────────────────────────────────────""")
#     try:
#         response = client.chat.completions.create(
#             messages=messages,
#             model=model_name
#         )
#         return response.choices
#     except Exception as e:
#         print(f"""
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃ ❌ API Error with model {model_name}
# ┃    {str(e)}
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
#         return None


# def interactive_chat():
#     conversation_history = []
#     model_index = 0
#     model_name = model_name_preferences[model_index]

#     print("""
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃ 🚀 Interactive Chat Started
# ┃    Type your message and press Enter to chat
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

#     while True:
#         header = f" 🤖 Using Model: {model_name} "
#         print(f"\n{header.center(80, '═')}\n")

#         while True:
#             try:
#                 user_input = input("💬 You: ")
#                 conversation_history.append({"role": "user", "content": user_input})

#                 while True:
#                     choices = get_response(client__, model_name, conversation_history)
#                     if choices is None:
#                         model_index += 1
#                         model_name = model_name_preferences[model_index % len(model_name_preferences)]
#                         print(f"""
# ┌────────────────────────────────────────────────────────────────
# │ 🔄 Model Switch
# │    Now using: {model_name}
# └────────────────────────────────────────────────────────────────""")
#                         continue
#                     else:
#                         break

#                 for a_choice in choices:
#                     response_content = a_choice.message.content
#                     print("\n" * 2)
#                     try:
#                         rprint(Panel(
#                             f"{response_content}",
#                             title=f"🤖 AI ({model_name})",
#                             border_style="blue"
#                         ))
#                     except Exception:
#                         # Fallback if rich formatting fails
#                         print(f"""
# ┌────────────────────────────────────────────────────────────────
# │ 🤖 AI ({model_name}):
# │
# {response_content}
# └────────────────────────────────────────────────────────────────""")

#                     conversation_history.append({"role": "assistant", "content": response_content})
#                     print("\n")
#             except KeyboardInterrupt:
#                 print("""
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ┃ 👋 Chat Session Ended
# ┃    Thank you for using the interactive chat!
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
#                 return


# if __name__ == "__main__":
#     interactive_chat()
