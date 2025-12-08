# load_dotenv()
# PYDANTIC_AI_GATEWAY_API_KEY = os.getenv("PYDANTIC_AI_GATEWAY_API_KEY", "")
import logfire
from google.genai.types import HarmBlockThreshold, HarmCategory
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModelSettings

logfire.configure()
logfire.instrument_pydantic_ai()



settings = GoogleModelSettings(
    temperature=0.2,
    max_tokens=1024,
    # google_thinking_config={'thinking_budget': 128},
    google_safety_settings=[
        {
            "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
    ],
)

agent = Agent("gateway/google-vertex:gemini-2.5-flash", model_settings=settings)

result = agent.run_sync("Hello world!")
result2 = agent.run_sync("Tell me a joke about the UK company Motorway")


print(result.output)
print(result2.output)
