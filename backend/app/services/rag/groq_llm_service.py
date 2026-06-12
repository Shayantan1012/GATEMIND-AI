from langchain_core.prompts import ChatPromptTemplate


class GroqLLMService:
    def __init__(self, config):
        self.model = None
        if config.get("GROQ_API_KEY"):
            from langchain_groq import ChatGroq

            self.model = ChatGroq(
                groq_api_key=config["GROQ_API_KEY"],
                model_name=config["GROQ_MODEL"],
                temperature=0.1,
            )

    def generate(self, system_prompt: str, context: str, query: str) -> str:
        if not self.model:
            if not context:
                return "I could not find relevant indexed material for that question."
            return "No LLM provider is configured. Here is the most relevant indexed context:\n\n" + context[:2500]
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "Context:\n{context}\n\nQuestion:\n{query}")]
        )
        return (prompt | self.model).invoke({"context": context, "query": query}).content
