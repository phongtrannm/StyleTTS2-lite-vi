from text_preprocessor.text_number import NumberPronunciation

class RangePronunciation:
    @staticmethod
    def pronounce_range(a: str, b: str) -> str:
        left  = NumberPronunciation.pronounce_decimal(a) if "," in a else NumberPronunciation.pronounce_integer(a)
        right = NumberPronunciation.pronounce_decimal(b) if "," in b else NumberPronunciation.pronounce_integer(b)
        return f"từ {left} đến {right}"
