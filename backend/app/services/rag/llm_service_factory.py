from app.services.rag.groq_llm_service import GroqLLMService
from app.services.rag.llm_service import LLMService


class LLMServiceFactory:
    @staticmethod
    def create(config):
        if config.get("GROQ_API_KEY"):
            return GroqLLMService(config)
        return LLMService(config)
