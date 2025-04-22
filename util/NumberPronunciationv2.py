import re

class NumberPronunciationUtilV2:
    defaultNames = ["không","một","hai","ba","bốn","năm","sáu","bảy","tám","chín"]
    scaleNames   = ["","nghìn","triệu","tỷ"]

    @staticmethod
    def pronounce_under_1000(num: int) -> str:
        if num < 10:
            return NumberPronunciationUtilV2.defaultNames[num]
        if num < 100:
            t, u = divmod(num, 10)
            if t == 1:
                # 10–19: giữ 'một' cho 11
                txt = "mười"
                if u == 1:
                    txt += " một"
                elif u == 5:
                    txt += " lăm"
                elif u != 0:
                    txt += f" {NumberPronunciationUtilV2.defaultNames[u]}"
                return txt
            else:
                # 20–99: dùng 'mốt' cho u == 1
                txt = f"{NumberPronunciationUtilV2.defaultNames[t]} mươi"
                if u == 1:
                    txt += " mốt"
                elif u == 4:
                    txt += " tư"
                elif u == 5:
                    txt += " lăm"
                elif u != 0:
                    txt += f" {NumberPronunciationUtilV2.defaultNames[u]}"
                return txt

        h, rem = divmod(num, 100)
        txt = f"{NumberPronunciationUtilV2.defaultNames[h]} trăm"
        if rem == 0:
            return txt
        if rem < 10:
            txt += f" linh {NumberPronunciationUtilV2.defaultNames[rem]}"
        else:
            txt += " " + NumberPronunciationUtilV2.pronounce_under_1000(rem)
        return txt

    @staticmethod
    def pronounce_three_digits(digits: list[int], leading: bool=True) -> str:
        if len(digits) < 3:
            digits = [0]*(3-len(digits)) + digits
        h, t, u = digits
        parts = []
        if h != 0:
            parts.append(f"{NumberPronunciationUtilV2.defaultNames[h]} trăm")
        elif not leading and (t != 0 or u != 0):
            parts.append("không trăm")
        if t == 0:
            if u != 0:
                parts.append(f"linh {NumberPronunciationUtilV2.defaultNames[u]}")
        elif t == 1:
            txt = "mười"
            if u == 1: txt += " một"
            
            #elif u == 4: txt += " tư"
            
            elif u == 5: txt += " lăm"
            elif u != 0: txt += f" {NumberPronunciationUtilV2.defaultNames[u]}"
            parts.append(txt)
        else:
            txt = f"{NumberPronunciationUtilV2.defaultNames[t]} mươi"
            if u == 1: txt += " mốt"
            elif u == 4: txt += " tư"
            elif u == 5: txt += " lăm"
            elif u != 0: txt += f" {NumberPronunciationUtilV2.defaultNames[u]}"
            parts.append(txt)
        return " ".join(parts)

    @staticmethod
    def pronounce_integer(s: str) -> str:
        s = s.lstrip("0") or "0"
        num = int(s)
        if num < 1000:
            return NumberPronunciationUtilV2.pronounce_under_1000(num)
        pad = (3 - len(s)%3) % 3
        s2 = "0"*pad + s
        chunks = [s2[i:i+3] for i in range(0, len(s2), 3)]
        words = []
        for idx, chunk in enumerate(chunks):
            val = int(chunk)
            if val == 0:
                continue
            if idx == 0 and len(chunks) > 1:
                text3 = NumberPronunciationUtilV2.pronounce_under_1000(val)
            else:
                text3 = NumberPronunciationUtilV2.pronounce_three_digits([int(c) for c in chunk], leading=False)
            scale = NumberPronunciationUtilV2.scaleNames[len(chunks)-idx-1]
            words.append(text3 + (f" {scale}" if scale else ""))
        return " ".join(words)

    @staticmethod
    def pronounce_decimal(s: str) -> str:
        int_part, dec_part = s.split(",",1)
        int_norm = int_part.replace(".", "")
        int_text = NumberPronunciationUtilV2.pronounce_integer(int_norm)
        dec_text = " ".join(NumberPronunciationUtilV2.defaultNames[int(ch)] for ch in dec_part if ch.isdigit())
        return f"{int_text} phẩy {dec_text}"

    @staticmethod
    def pronounce_range(a: str, b: str) -> str:
        left  = NumberPronunciationUtilV2.pronounce_decimal(a) if "," in a else NumberPronunciationUtilV2.pronounce_integer(a)
        right = NumberPronunciationUtilV2.pronounce_decimal(b) if "," in b else NumberPronunciationUtilV2.pronounce_integer(b)
        return f"từ {left} đến {right}"

    @staticmethod
    def pronounce_date(s: str) -> str:
        parts = s.split("/")
        if len(parts)==2:
            d,m = parts
            return f"ngày {NumberPronunciationUtilV2.pronounce_integer(d)} tháng {NumberPronunciationUtilV2.pronounce_integer(m)}"
        if len(parts)==3:
            d,m,y = parts
            return f"ngày {NumberPronunciationUtilV2.pronounce_integer(d)} tháng {NumberPronunciationUtilV2.pronounce_integer(m)} năm {NumberPronunciationUtilV2.pronounce_integer(y)}"
        return s

def normalize(s: str) -> str:
    if "," in s:
        a,b = s.split(",",1)
        return a.replace(".","") + "," + b
    return s.replace(".","")

def classify_and_pronounce_number(text: str) -> str:
    pattern = re.compile(r"""
        (?P<date>\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b)|
        (?P<range>(?P<ra>\d{1,3}(?:\.\d{3})*(?:,\d+)?)[ ]*[-–][ ]*(?P<rb>\d{1,3}(?:\.\d{3})*(?:,\d+)?))|
        (?P<decimal>\d+(?:\.\d{3})*,\d+)|
        (?P<int>\d+(?:\.\d{3})*)
    """, re.VERBOSE)

    def repl(m):
        if m.group("date"):
            return NumberPronunciationUtilV2.pronounce_date(m.group("date"))
        if m.group("range"):
            a = normalize(m.group("ra")); b = normalize(m.group("rb"))
            return NumberPronunciationUtilV2.pronounce_range(a,b)
        if m.group("decimal"):
            return NumberPronunciationUtilV2.pronounce_decimal(normalize(m.group("decimal")))
        if m.group("int"):
            return NumberPronunciationUtilV2.pronounce_integer(normalize(m.group("int")))
        return m.group(0)

    return pattern.sub(repl, text)

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
        "12/03/2023"
    ]
    for t in tests:
        print(f"{t} → {classify_and_pronounce_number(t)}")