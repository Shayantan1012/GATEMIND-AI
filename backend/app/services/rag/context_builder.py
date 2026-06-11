class ContextBuilder:
    def build(self, documents: list[dict], learning_profile: dict | None = None) -> str:
        sections = []
        if learning_profile:
            sections.append(f"User learning profile: {learning_profile}")
        for index, document in enumerate(documents, 1):
            source = document.get("metadata", {}).get("source", "unknown")
            page = document.get("metadata", {}).get("page_no", "?")
            sections.append(f"[{index}] Source: {source}, page: {page}\n{document.get('content', '')}")
        return "\n\n".join(sections)
