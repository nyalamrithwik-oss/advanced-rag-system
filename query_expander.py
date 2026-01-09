from typing import Dict, Any, List
import json
import re
from openai import OpenAI

ACRONYM_DICT = {
    "B2B": "business-to-business",
    "ROI": "return on investment",
    "CRM": "customer relationship management",
    "KPI": "key performance indicator",
    "LTV": "lifetime value",
    "CAC": "customer acquisition cost",
    "MQL": "marketing qualified lead",
    "SQL": "sales qualified lead"
}

class QueryExpander:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key or None)

    def expand_query(self, query: str, domain: str = "sales") -> Dict[str, Any]:
        detected_acronyms = {a: ACRONYM_DICT[a] for a in ACRONYM_DICT if a in query}
        prompt = (
            "Expand the following query for better retrieval in the domain of " + domain + ". "
            "Generate up to 5 variations, expand acronyms, and add related terms. "
            "Return JSON: expanded_queries, detected_acronyms, related_terms.\n"
            f"Query: {query}\n"
            f"Acronym dictionary: {ACRONYM_DICT}\n"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": "You are an expert query expander for sales."},
                          {"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=256
            )
            result = response.choices[0].message.content
            try:
                parsed = json.loads(result)
            except Exception:
                parsed = {"expanded_queries": [query], "detected_acronyms": detected_acronyms, "related_terms": []}
            # Limit to 5 variations
            parsed["expanded_queries"] = parsed.get("expanded_queries", [query])[:5]
            return {
                "original": query,
                "expanded_queries": parsed["expanded_queries"],
                "detected_acronyms": parsed.get("detected_acronyms", detected_acronyms),
                "related_terms": parsed.get("related_terms", [])
            }
        except Exception as e:
            # Fallback if API call fails
            return {
                "original": query,
                "expanded_queries": [query],
                "detected_acronyms": detected_acronyms,
                "related_terms": []
            }
