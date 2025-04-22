import re
import json

class TextNormalizer:
    def __init__(self):
        with open("dataset/abbreviations.json", "r", encoding="utf-8") as f:
            self.abbreviation_map = json.load(f)
        with open("dataset/english_map.json", "r", encoding="utf-8") as f:
            self.english_term_map = json.load(f)

    def normalize_abbreviations(self, text):
        for abbr, full in self.abbreviation_map.items():
            text = re.sub(rf"\b{abbr}\b", full, text)
        return text

    def normalize_english_terms(self, text):
        for term, vn_pron in self.english_term_map.items():
            text = re.sub(rf"\b{term}\b", vn_pron, text, flags=re.IGNORECASE)
        return text

    # def normalize(self, text):
    #     text = text.strip()
    #     text = self.normalize_abbreviations(text)
    #     text = self.normalize_english_terms(text)
    #     return text
    
    @staticmethod
    def normalize(text):
        text_normalizer = TextNormalizer()
        
        text = text.strip()
        text = text_normalizer.normalize_abbreviations(text)
        text = text_normalizer.normalize_english_terms(text)
        return text


class StyleDetector:
    def detect(self, text: str) -> str:
        lower_text = text.lower()
        if "!" in text:
            return "exclamatory"
        elif any(kw in lower_text for kw in ["haha", "vui", "buồn cười", "chọc", "đùa"]):
            return "funny"
        elif any(kw in lower_text for kw in ["thông báo", "lưu ý", "trân trọng", "nghiêm túc", "yêu cầu"]):
            return "serious"
        else:
            return "neutral"
