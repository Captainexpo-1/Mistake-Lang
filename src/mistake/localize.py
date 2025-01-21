import requests
import os
import json
from typing import List
from mistake.tokenizer.lexer import keywords_en

# Google Translate API endpoint (unofficial)
GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

def translate_keyword(keyword: str, dest_language: str) -> str:
    """Translate a single keyword using a direct request to Google Translate API."""
    params = {
        "client": "gtx",
        "sl": "en",  # Source language (English)
        "tl": dest_language,  # Target language
        "dt": "t",
        "q": keyword
    }

    response = requests.get(GOOGLE_TRANSLATE_URL, params=params)
    if response.status_code != 200:
        print(f"Failed to translate {keyword}. HTTP {response.status_code}")
        return keyword  # Return the original word on failure
    translated_text = response.json()[0][0][0]  # Extract translated text
    return translated_text

def translate_keywords(keywords: List[str], dest_language: str) -> List[str]:
    """Translate a list of keywords using manual HTTP requests."""
    result = []
    for keyword in keywords:
        print(f"Translating {keyword}...")
        translated_text = translate_keyword(keyword, dest_language)
        result.append(translated_text)
    return result

def translate(dest_language: str):
    """Translate all keywords and save them to a JSON file."""

    localizations_path = os.path.join(os.path.dirname(__file__), f"./tokenizer/.localizations/{dest_language}.json")
    os.makedirs(os.path.dirname(localizations_path), exist_ok=True)

    english = list(keywords_en.keys())

    translated_keywords = translate_keywords(english, dest_language)

    ret = {}
    for i, j in zip(english, translated_keywords):
        ret[j.lower().replace(" ", "_")] = i.lower()

    with open(localizations_path, "w", encoding="utf-8") as f:
        json.dump(ret, f, ensure_ascii=False, indent=4)

    print(f"Translated keywords saved to {localizations_path}")
    return ret

if __name__ == "__main__":
    translate("es")
