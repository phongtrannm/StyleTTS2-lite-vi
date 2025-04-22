import re

class NumberPronunciation:
    defaultNames = ["không","một","hai","ba","bốn","năm","sáu","bảy","tám","chín"]
    scaleNames   = ["","nghìn","triệu","tỷ"]

    @staticmethod
    def pronounce_under_1000(num: int) -> str:
        if num < 10:
            return NumberPronunciation.defaultNames[num]
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
                    txt += f" {NumberPronunciation.defaultNames[u]}"
                return txt
            else:
                # 20–99: dùng 'mốt' cho u == 1
                txt = f"{NumberPronunciation.defaultNames[t]} mươi"
                if u == 1:
                    txt += " mốt"
                elif u == 4:
                    txt += " tư"
                elif u == 5:
                    txt += " lăm"
                elif u != 0:
                    txt += f" {NumberPronunciation.defaultNames[u]}"
                return txt

        h, rem = divmod(num, 100)
        txt = f"{NumberPronunciation.defaultNames[h]} trăm"
        if rem == 0:
            return txt
        if rem < 10:
            txt += f" linh {NumberPronunciation.defaultNames[rem]}"
        else:
            txt += " " + NumberPronunciation.pronounce_under_1000(rem)
        return txt

    @staticmethod
    def pronounce_three_digits(digits: list[int], leading: bool=True) -> str:
        if len(digits) < 3:
            digits = [0]*(3-len(digits)) + digits
        h, t, u = digits
        parts = []
        if h != 0:
            parts.append(f"{NumberPronunciation.defaultNames[h]} trăm")
        elif not leading and (t != 0 or u != 0):
            parts.append("không trăm")
        if t == 0:
            if u != 0:
                parts.append(f"linh {NumberPronunciation.defaultNames[u]}")
        elif t == 1:
            txt = "mười"
            if u == 1: txt += " một"
            
            #elif u == 4: txt += " tư"
            
            elif u == 5: txt += " lăm"
            elif u != 0: txt += f" {NumberPronunciation.defaultNames[u]}"
            parts.append(txt)
        else:
            txt = f"{NumberPronunciation.defaultNames[t]} mươi"
            if u == 1: txt += " mốt"
            elif u == 4: txt += " tư"
            elif u == 5: txt += " lăm"
            elif u != 0: txt += f" {NumberPronunciation.defaultNames[u]}"
            parts.append(txt)
        return " ".join(parts)

    @staticmethod
    def pronounce_integer(s: str) -> str:
        s = s.lstrip("0") or "0"
        num = int(s)
        if num < 1000:
            return NumberPronunciation.pronounce_under_1000(num)
        pad = (3 - len(s)%3) % 3
        s2 = "0"*pad + s
        chunks = [s2[i:i+3] for i in range(0, len(s2), 3)]
        words = []
        for idx, chunk in enumerate(chunks):
            val = int(chunk)
            if val == 0:
                continue
            if idx == 0 and len(chunks) > 1:
                text3 = NumberPronunciation.pronounce_under_1000(val)
            else:
                text3 = NumberPronunciation.pronounce_three_digits([int(c) for c in chunk], leading=False)
            scale = NumberPronunciation.scaleNames[len(chunks)-idx-1]
            words.append(text3 + (f" {scale}" if scale else ""))
        return " ".join(words)

    @staticmethod
    def pronounce_decimal(s: str) -> str:
        int_part, dec_part = s.split(",",1)
        int_norm = int_part.replace(".", "")
        int_text = NumberPronunciation.pronounce_integer(int_norm)
        dec_text = " ".join(NumberPronunciation.defaultNames[int(ch)] for ch in dec_part if ch.isdigit())
        return f"{int_text} phẩy {dec_text}"