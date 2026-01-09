import uuid
import time
from typing import Dict, List
import re

class ConversationManager:
    def __init__(self):
        self.conversation_id = str(uuid.uuid4())
        self.history: List[Dict] = []

    def add_turn(self, user_query: str, assistant_response: str, metadata: Dict):
        self.history.append({
            "timestamp": time.time(),
            "query": user_query,
            "response": assistant_response,
            "metadata": metadata,
            "conversation_id": self.conversation_id
        })
        if len(self.history) > 10:
            self.history = self.history[-10:]

    def get_contextual_query(self, current_query: str) -> str:
        if not self.history:
            return current_query
        last_turn = self.history[-1]
        context = last_turn["query"]
        # Pronoun/reference/follow-up detection
        pronouns = ["it", "that", "this", "they"]
        references = ["same", "also", "too", "previous"]
        follow_ups = ["what about", "how about", "and"]
        pattern = r"\b(" + "|".join(pronouns + references) + r")\b|(" + "|".join(follow_ups) + r")"
        if re.search(pattern, current_query, re.IGNORECASE):
            # Simple rewrite: replace pronouns with context
            rewritten = re.sub(r"\b(it|that|this|they)\b", context, current_query, flags=re.IGNORECASE)
            # Add context for follow-ups
            for phrase in follow_ups:
                if phrase in current_query.lower():
                    rewritten = f"{current_query} for {context}"
                    break
            return rewritten
        return current_query

    def get_history(self, n_turns: int = 3) -> List[Dict]:
        return self.history[-n_turns:]

    def clear_conversation(self):
        self.history = []
        self.conversation_id = str(uuid.uuid4())
