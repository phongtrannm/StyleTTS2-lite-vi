import re

digit_text = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

def convert_number_to_text(n):
    n = int(n)
    if n < 10:
        return digit_text[n]
    elif n < 100:
        tens = n // 10
        units = n % 10
        if units == 0:
            return f"{digit_text[tens]} mươi"
        elif units == 1:
            if tens == 1:
                return "mười một"
            else:
                return f"{digit_text[tens]} mươi mốt"
        elif units == 5:
            return f"{digit_text[tens]} mươi lăm"
        else:
            return f"{digit_text[tens]} mươi {digit_text[units]}"
    elif n < 1000:
        hundreds = n // 100
        remainder = n % 100
        if remainder == 0:
            return f"{digit_text[hundreds]} trăm"
        else:
            return f"{digit_text[hundreds]} trăm {convert_number_to_text(remainder)}"
    else:
        return str(n)  # để đơn giản, bạn có thể mở rộng tiếp nếu cần

def convert_decimal_to_text(decimal_str):
    decimal_str = decimal_str.replace(',', '.')
    if '.' in decimal_str:
        int_part, dec_part = decimal_str.split('.')
        int_text = convert_number_to_text(int(int_part))
        dec_text = convert_number_to_text(int(dec_part))
        return f"{int_text} phẩy {dec_text}"
    else:
        return convert_number_to_text(int(decimal_str))

def replace_range_with_words(text):
    pattern = r'(\d{1,3}(?:[.,]\d+)?)[\s]*[-–—][\s]*(\d{1,3}(?:[.,]\d+)?)'

    def replacer(match):
        num1, num2 = match.group(1), match.group(2)
        text1 = convert_decimal_to_text(num1)
        text2 = convert_decimal_to_text(num2)
        return f"{text1} đến {text2}"

    return re.sub(pattern, replacer, text)

# Ví dụ sử dụng
input_text = "Giá vàng quốc tế sáng nay nới rộng lên vùng 12,5 - 13,5 triệu đồng một lượng. Khoảng 9 – 10 người tham gia."
output_text = replace_range_with_words(input_text)
print(output_text)