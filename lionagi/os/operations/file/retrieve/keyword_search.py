class TextRetrievalStrategy:
    def retrieve(self, query: str, method: str, context: Optional[str] = None) -> Any:
        if method == "keyword":
            return self.keyword_search(query)
        elif method == "semantic":
            return self.semantic_search(query)
        # Additional methods can be added here
        else:
            raise ValueError(f"Unknown method: {method}")

    def keyword_search(self, query: str) -> Any:
        # Implement keyword search logic
        pass

    def semantic_search(self, query: str) -> Any:
        # Implement semantic search logic
        pass
