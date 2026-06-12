from app.services.rag.embeddings.local_hash_embeddings import LocalHashEmbeddings



# class EmbeddingFactory:
#     @staticmethod
#     def create(config):
#         if config.get("OPENAI_API_KEY"):
#             from langchain_openai import OpenAIEmbeddings

#             return OpenAIEmbeddings(api_key=config["OPENAI_API_KEY"], model=config["OPENAI_EMBEDDING_MODEL"])
#         return LocalHashEmbeddings()



class EmbeddingFactory:
    @staticmethod
    def create(config):

        if config.get("OPENAI_API_KEY"):
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(
                api_key=config["OPENAI_API_KEY"],
                model=config["OPENAI_EMBEDDING_MODEL"]
            )

        elif config.get("HUGGINGFACE_API_KEY"):
            print("Initializing HuggingFace embeddings with model sentence-transformers/all-MiniLM-L6-v2")
            from langchain_huggingface import HuggingFaceEmbeddings

            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

        return LocalHashEmbeddings()
