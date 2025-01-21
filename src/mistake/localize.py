from googletrans import Translator
from typing import List
from mistake.tokenizer.lexer import keywords_en 
import asyncio
import os
import json

async def trans_keywords_async(keywords: List[str], dest_language: str) -> List[str]:
    translator = Translator()
    tasks = [translator.translate(keyword, dest=dest_language) for keyword in keywords]
    translations = await asyncio.gather(*tasks)
    result = [translation.text for translation in translations]
    return result

def trans_keywords_sync(keywords: List[str], dest_language: str) -> List[str]:
    return asyncio.run(trans_keywords_async(keywords, dest_language))

def translate(dest_language: str):
    
    localizations_path: str = os.path.join(os.path.dirname(__file__), f"./tokenizer/.localizations/{dest_language}.json")

    # make sure the directory exists
    os.makedirs(os.path.dirname(localizations_path), exist_ok=True)

    english = list(keywords_en.keys())

    translated_keywords = trans_keywords_sync(english, dest_language)

    ret = {}
    for i, j in zip(english, translated_keywords):
        ret[j.lower().replace(" ", "_")] = i.lower()
    with open(localizations_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(ret, ensure_ascii=False, indent=4))
    print(f"Translated keywords to {dest_language}")
    return ret

if __name__ == "__main__":
    translate("es")
