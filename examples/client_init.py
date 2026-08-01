from fancy_fish import config


def init_clients():
    """Example showing how to consume API keys from fancy_fish.config.

    Adjust the example to the specific client libraries you use.
    """
    # OpenAI example (adjust to whichever client library you use)
    # import openai
    # openai.api_key = config.OPENAI_API_KEY

    # Groq example (pseudocode)
    # from groq import GroqClient
    # groq = GroqClient(api_key=config.GROQ_API_KEY)

    # Gemini example (pseudocode)
    # from gemini import GeminiClient
    # gemini = GeminiClient(api_key=config.GEMINI_API_KEY)

    print("Loaded keys:", {
        "OPENAI": bool(config.OPENAI_API_KEY),
        "GROQ": bool(config.GROQ_API_KEY),
        "GEMINI": bool(config.GEMINI_API_KEY),
    })


if __name__ == "__main__":
    init_clients()
