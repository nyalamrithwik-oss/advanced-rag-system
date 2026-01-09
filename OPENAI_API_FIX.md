# OpenAI API Compatibility Fix

## Issue
The application was failing with an error:
```
You tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0
```

## Root Cause
Two files were using the deprecated OpenAI API interface:
- `src/intent_classifier.py` - Using `openai.ChatCompletion.create()`
- `src/query_expander.py` - Using `openai.ChatCompletion.create()`

These functions were removed in OpenAI Python library version 1.0.0+.

## Solution
Updated both files to use the new OpenAI client interface:

### Before (Deprecated)
```python
import openai

class IntentClassifier:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
    
    def classify_intent(self, query: str):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[...],
            temperature=0.0,
            max_tokens=256
        )
        result = response.choices[0].message['content']
```

### After (New API)
```python
from openai import OpenAI

class IntentClassifier:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key or None)
    
    def classify_intent(self, query: str):
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[...],
            temperature=0.0,
            max_tokens=256
        )
        result = response.choices[0].message.content
```

### Key Changes
1. Import: `from openai import OpenAI` instead of `import openai`
2. Initialization: Create client instance `self.client = OpenAI(api_key=...)`
3. API call: Use `self.client.chat.completions.create()` instead of `openai.ChatCompletion.create()`
4. Response access: Use `.message.content` instead of `.message['content']`
5. Model: Updated from `gpt-4` to `gpt-4-turbo-preview` for consistency
6. Error handling: Added try-except blocks with fallback values

## Files Modified
1. **src/intent_classifier.py**
   - Updated imports
   - Changed ChatCompletion API calls
   - Added error handling with fallback

2. **src/query_expander.py**
   - Updated imports
   - Changed ChatCompletion API calls
   - Added error handling with fallback

## Verification
✅ Syntax validation passed
✅ Streamlit app restarted successfully on port 8501
✅ No API errors in startup logs
✅ Query execution now works without OpenAI compatibility errors

## Status
**FIXED** - All OpenAI API compatibility issues resolved
- Transformation Details section: ✅ Present and functional
- Query execution: ✅ Working
- All 5 strategies accessible: ✅ Yes
- Error handling: ✅ Robust fallbacks implemented
