import requests

model_owner = "mistralai"
model_name = "mistral-7b-instruct-v0.1"
api_key = "r8_Ez1niBpNFVqMTv5gHRbc9ROhvNsCQo93ZCsPj"

response = requests.get(
    url=f"https://api.replicate.com/v1/models/{model_owner}/{model_name}",
    headers={"Authorization": f"Token {api_key}"},
)

print(response.json())
print(response.ok)