import requests


def lakera_guard(prompt: str, api_key):
    response = requests.post(
        "https://api.lakera.ai/v1/prompt_injection",
        json={"input": prompt},
        headers={"Authorization": f"Bearer {api_key}"},
    ).json()

    flagged = response["results"][0]["flagged"]
    return flagged, response
