

# as per https://github.com/marketplace/models/azure-openai/o1-preview

from openai import OpenAI
from crocodile.file_management import Read, P

gh_token = Read.ini(P.home().joinpath("dotfiles/creds/git/git_host_tokens.ini"))['thisismygitrepo']['newLongterm']

endpoint = "https://models.inference.ai.azure.com"
model_name = "o1-preview"

client = OpenAI(
    base_url=endpoint,
    api_key=gh_token,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
    model=model_name
)

print(response.choices[0].message.content)

