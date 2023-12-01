import os
import dotenv

dotenv.load_dotenv()

from ..api.OAIService import OpenAIService, OpenAIRateLimiter

OAIRateLimiter = OpenAIRateLimiter(
    max_requests_per_minute = 10000,
    max_tokens_per_minute = 450000
)

OAIService = OpenAIService(
    api_key = os.getenv("OPENAI_API_KEY"),
    token_encoding_name = "cl100k_base",
    max_attempts=5,
    rate_limiter=OAIRateLimiter,
)