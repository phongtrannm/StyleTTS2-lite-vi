import re

class NumberPronunciationUtil:
    defaultNames = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    rangeNames = ["", "nghìn", "triệu"]

    @staticmethod
    def string_to_number_array(s):
        return [int(ch) for ch in s]

    @staticmethod
    def append_word(s, w):
        if not w:
            return s
        return s + ' ' + w if s else w

    @staticmethod
    def append_ten_name(s, v):
        if v > 1:
            s = NumberPronunciationUtil.append_word(s, NumberPronunciationUtil.defaultNames[v]) + " mươi"
        elif v == 0:
            s = NumberPronunciationUtil.append_word(s, "linh")
        else:
            s = NumberPronunciationUtil.append_word(s, "mười")
        return s

    @staticmethod
    def get_base_name(h, l):
        if h > 1 or l == 0 or (h == 1 and l == 5):
            return {
                0: "",
                1: "mốt",
                4: "tư",
                5: "lăm"
            }.get(l, NumberPronunciationUtil.defaultNames[l])
        return NumberPronunciationUtil.defaultNames[l]

    @staticmethod
    def pronounce_hundreds(s, n, offset, length):
        if length == 1:
            return NumberPronunciationUtil.append_word(s, NumberPronunciationUtil.defaultNames[n[offset]])
        if length == 3:
            s = NumberPronunciationUtil.append_word(s, NumberPronunciationUtil.defaultNames[n[offset]]) + " trăm"
            offset += 1
        ten = n[offset]
        base = n[offset + 1]
        if ten != 0 or base != 0:
            s = NumberPronunciationUtil.append_ten_name(s, ten)
            s = NumberPronunciationUtil.append_word(s, NumberPronunciationUtil.get_base_name(ten, base))
        return s

    @staticmethod
    def pronounce_millions(s, n, offset, length):
        if length <= 3:
            return NumberPronunciationUtil.pronounce_hundreds(s, n, offset, length)
        while length > 0:
            part_length = length % 3 or 3
            range_index = (length - 1) // 3
            if part_length == 3 and all(x == 0 for x in n[offset:offset + 3]):
                pass
            else:
                s = NumberPronunciationUtil.pronounce_hundreds(s, n, offset, part_length)
                s = NumberPronunciationUtil.append_word(s, NumberPronunciationUtil.rangeNames[range_index])
            length -= part_length
            offset += part_length
        return s

    @staticmethod
    def pronounce(number):
        na = NumberPronunciationUtil.string_to_number_array(str(number))
        if len(na) <= 9:
            return NumberPronunciationUtil.pronounce_millions("", na, 0, len(na))
        s = NumberPronunciationUtil.pronounce_millions("", na, 0, len(na) - 9)
        s = NumberPronunciationUtil.append_word(s, "tỷ")
        return NumberPronunciationUtil.pronounce_millions(s, na, len(na) - 9, 9)

def normalize_number_string(number_str):
    """
    Loại bỏ dấu chấm ngăn cách hàng nghìn nhưng giữ dấu phẩy cho phần thập phân.
    Ví dụ:
        "111.111,999" -> "111111,999"
        "1.000.000"   -> "1000000"
    """
    if ',' in number_str:
        int_part, decimal_part = number_str.split(',', 1)
        int_part = int_part.replace('.', '')
        return f"{int_part},{decimal_part}"
    else:
        return number_str.replace('.', '')

def replace_numbers_with_pronunciation(text):
    """
    Tìm và chuyển mọi số trong đoạn text thành cách đọc tiếng Việt.
    Giữ nguyên phần thập phân (chưa đọc), chỉ đọc phần nguyên.
    """
    def replacer(match):
        raw_number = match.group(0)
        normalized = normalize_number_string(raw_number)
        integer_part = normalized.split(',')[0]
        pronunciation = NumberPronunciationUtil.pronounce(integer_part)
        return pronunciation
