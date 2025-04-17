from util.NumberPronunciation import format_text_with_numbers_readable
import re

def normalize_number_string(number_str):
    """
    Chuẩn hóa chuỗi số:
    - Loại bỏ dấu chấm (.) ngăn cách hàng nghìn.
    - Giữ lại dấu phẩy (,) cho phần thập phân.
    Ví dụ: "1.234.567,89" => "1234567,89"
    """
    if ',' in number_str:
        int_part, decimal_part = number_str.split(',', 1)
        int_part = int_part.replace('.', '')
        return f"{int_part},{decimal_part}"
    else:
        return number_str.replace('.', '')

def main():
    raw_input = "Theo số liệu của Bộ Nội vụ, tính đến hết năm 2021, cả nước có có 90.508 thôn, tổ dân phố. Trong đó, có 69.580 thôn và 20.928 tổ dân phố."

    result = format_text_with_numbers_readable(raw_input)
    print(result)

if __name__ == "__main__":
    main()
