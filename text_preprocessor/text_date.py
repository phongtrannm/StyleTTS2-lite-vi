from text_number import NumberPronunciation

class DatePronunciation:
    @staticmethod
    def pronounce_date(s: str) -> str:
        parts = s.split("/")
        if len(parts)==2:
            d,m = parts
            return f"ngày {NumberPronunciation.pronounce_integer(d)} tháng {NumberPronunciation.pronounce_integer(m)}"
        if len(parts)==3:
            d,m,y = parts
            return f"ngày {NumberPronunciation.pronounce_integer(d)} tháng {NumberPronunciation.pronounce_integer(m)} năm {NumberPronunciation.pronounce_integer(y)}"
        return s
