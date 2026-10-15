from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI


def get_azure_openai_client() -> AzureOpenAI:
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )

    return AzureOpenAI(
        azure_endpoint="https://2fidiaguilar-8765-resource.services.ai.azure.com",
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21",
    )