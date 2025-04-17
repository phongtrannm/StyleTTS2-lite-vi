from util.NumberPronunciation import NumberPronunciationUtil
import re

def normalize_number_string(number_str):
    """
    Chuẩn hóa chuỗi số:
    - Loại bỏ dấu chấm (.) ngăn cách hàng nghìn.
    - Giữ lại dấu phẩy (,) cho phần thập phân.
    Ví dụ: "1.234.567,89" => "1234567,89"
    """
    # Loại bỏ mọi dấu chấm không nằm sau dấu phẩy
    if ',' in number_str:
        int_part, decimal_part = number_str.split(',', 1)
        int_part = int_part.replace('.', '')
        return f"{int_part},{decimal_part}"
    else:
        return number_str.replace('.', '')

def main():
    raw_input = "111.111,999"
    normalized = normalize_number_string(raw_input)

    # Chỉ lấy phần nguyên để phát âm
    integer_part = normalized.split(',')[0]

    pronunciation = NumberPronunciationUtil.pronounce(integer_part)

    print(f"Số gốc: {raw_input}")
    print(f"Số sau chuẩn hóa: {normalized}")
    print(f"Cách đọc phần nguyên: {pronunciation}")

if __name__ == "__main__":
    main()
