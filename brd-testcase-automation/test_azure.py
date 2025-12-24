"""
Test Azure OpenAI Connection
"""
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

print("\n" + "=" * 70)
print("🧪 Testing Azure OpenAI Connection")
print("=" * 70 + "\n")

# Get config
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
api_key = os.getenv('AZURE_OPENAI_API_KEY')
deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')

# Validate config
print("Configuration:")
print(f"  Endpoint: {endpoint}")
print(f"  Deployment: {deployment}")
print(f"  API Version: {api_version}")
print(f"  API Key: {'*' * 20}{api_key[-4:] if api_key else 'NOT SET'}")
print()

if not endpoint or not api_key or not deployment:
    print("❌ Missing Azure OpenAI configuration!")
    print("Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT in .env")
    exit(1)

try:
    # Create Azure OpenAI client
    print("Initializing Azure OpenAI client...")
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    print("✓ Client initialized")
    print()

    # Test API call
    print("Sending test request to Azure OpenAI...")
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Say 'Azure OpenAI is working perfectly!' in Vietnamese."
            }
        ],
        max_tokens=100
    )

    print("✓ Response received!")
    print()
    print("Response:")
    print(f"  {response.choices[0].message.content}")
    print()

    # Show usage
    print("Token Usage:")
    print(f"  Prompt tokens: {response.usage.prompt_tokens}")
    print(f"  Completion tokens: {response.usage.completion_tokens}")
    print(f"  Total tokens: {response.usage.total_tokens}")
    print()

    print("=" * 70)
    print("✅ Azure OpenAI connection successful!")
    print("=" * 70)

except Exception as e:
    print()
    print("=" * 70)
    print("❌ Error connecting to Azure OpenAI:")
    print(f"  {str(e)}")
    print("=" * 70)
    exit(1)