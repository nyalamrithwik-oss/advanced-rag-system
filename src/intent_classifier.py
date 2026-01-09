import uuid
from typing import Dict, Any
import json
from openai import OpenAI

class IntentClassifier:
    INTENT_MAP = {
        "factual": "basic",
        "how_to": "multi_query",
        "comparison": "hyde",
        "explanation": "rewritten",
        "troubleshooting": "hybrid_rerank"
    }

    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key or None)

    def classify_intent(self, query: str) -> Dict[str, Any]:
        prompt = (
            "Classify the following user query into one of these intents: factual, how_to, comparison, explanation, troubleshooting. "
            "Return a JSON with: intent, confidence (0-1), suggested_strategy, and reasoning.\n"
            f"Query: {query}\n"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": "You are an expert intent classifier for a RAG system."},
                          {"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=256
            )
            # Parse response
            result = response.choices[0].message.content
            try:
                parsed = json.loads(result)
            except Exception:
                parsed = {"intent": "factual", "confidence": 0.5, "suggested_strategy": "basic", "reasoning": "Default fallback."}
            # Map strategy
            intent = parsed.get("intent", "factual")
            parsed["suggested_strategy"] = self.INTENT_MAP.get(intent, "basic")
            return parsed
        except Exception as e:
            # Fallback if API call fails
            return {"intent": "factual", "confidence": 0.5, "suggested_strategy": "basic", "reasoning": f"Error: {str(e)}"}
