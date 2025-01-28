import requests
import os
import json
from typing import List
from mistake.tokenizer.lexer import keywords_en
from concurrent.futures import ThreadPoolExecutor

GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

def translate_keyword(keyword: str, dest_language: str) -> str:
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
        return keyword
    translated_text = response.json()[0][0][0]
    return translated_text


def translate_keywords(keywords: List[str], dest_language: str) -> List[str]:
    def translate_single_keyword(keyword):
        print(f"Translating {keyword}...")
        return translate_keyword(keyword, dest_language)

    with ThreadPoolExecutor() as executor:
        result = list(executor.map(translate_single_keyword, keywords))
        
    return result

def purge_localizations():
    localizations_path = os.path.join(os.path.dirname(__file__), "./tokenizer/.localizations")
    if os.path.exists(localizations_path):
        for file in os.listdir(localizations_path):
            file_path = os.path.join(localizations_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"Purged all localization files in {localizations_path}")
        os.rmdir(localizations_path)
    else:
        print(f"No localization files found in {localizations_path}")

def translate(dest_language: str):
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
