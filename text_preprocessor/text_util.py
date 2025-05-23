import re

# from text_number import NumberPronunciation
from text_preprocessor.text_number import NumberPronunciation
from text_preprocessor.text_date import DatePronunciation
from text_preprocessor.text_range import RangePronunciation
from text_preprocessor.text_normalizer import TextNormalizer
from text_preprocessor.text_unit import UnitPronunciation

class TextUtil:
    @classmethod
    def _normalize(cls, s: str) -> str:
        if "," in s:
            a,b = s.split(",",1)
            return a.replace(".","") + "," + b
        return s.replace(".","")

    @classmethod
    def _classify_and_pronounce_number(cls, text: str) -> str:
        pattern = re.compile(r"""
            (?P<date>\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b)|
            (?P<range>(?P<ra>\d{1,3}(?:\.\d{3})*(?:,\d+)?)[ ]*[-–][ ]*(?P<rb>\d{1,3}(?:\.\d{3})*(?:,\d+)?))|
            (?P<decimal>\d+(?:\.\d{3})*,\d+)|
            (?P<int>\d+(?:\.\d{3})*)
        """, re.VERBOSE)

        def repl(m):
            if m.group("date"):
                return DatePronunciation.pronounce_date(m.group("date"))
            if m.group("range"):
                a = cls._normalize(m.group("ra")); b = cls._normalize(m.group("rb"))
                return RangePronunciation.pronounce_range(a,b)
            if m.group("decimal"):
                return NumberPronunciation.pronounce_decimal(cls._normalize(m.group("decimal")))
            if m.group("int"):
                return NumberPronunciation.pronounce_integer(cls._normalize(m.group("int")))
            return m.group(0)

        return pattern.sub(repl, text)

    @classmethod
    def classify(cls, text):
        #Xử lý đơn vị
        unit_converter = UnitPronunciation()
        text_formated = unit_converter.normalize_text(text)

        #xử lý số
        text_formated = cls._classify_and_pronounce_number(text_formated)
        
        #Xử lý danh từ
        text_formated = TextNormalizer.normalize(text_formated)
        
        return text_formated

if __name__ == "__main__":
    tests = [
        "năm 2021",
        "năm 1998",
        "năm 1968",
        "90.508",
        "9.050.800.000",
        "20.928",
        "4 ngân hàng",
        "15 tháng này",
        "11 tháng này",
        "21 tháng này",

        "14 tháng này",
        "24 tháng này",
        "40 hàng",
        "409 hàng",
        "401 hàng",
        "12,5 - 13,5",
        "90.508,768",
        "12/3",
        "12/3/2023",
        "01/03/1998",
        "12/03/2023",

        "TP HCM",
        "HCM",
        "HN",
        "AI",
        "Google",
        "VN",
         "Giá là 65 triệu/m², vào hồi 9h sáng nay, "
        "anh nặng 70kg, cao 1m75 và chạy 10km mỗi ngày."
        "cho căn 48–52 m², ngang ngửa với căn hộ thương mại bình dân "
        "Anh Huy (Thanh Xuân) đi xem căn chung cư mini 48 m² có hai phòng ngủ, hai vệ sinh, chủ rao 1,7 tỷ đồng nhưng báo lên gần 2 tỷ sau khi đầu tư PCCC và để lại nội thất, tương đương 42 triệu/m² "
    ]
    for t in tests:
        print(f"{t} → {TextUtil.classify(t)}")