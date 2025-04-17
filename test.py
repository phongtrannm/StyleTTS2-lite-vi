import re
from util.NumberPronunciationv2 import classify_and_pronounce_number

def main():
    raw_input = "Theo số liệu của Bộ Nội vụ, tính đến hết năm 2021, cả nước có có 90.508 thôn, tổ dân phố. Trong đó, có 69.580 thôn và 20.928 tổ dân phố."
    result = classify_and_pronounce_number(raw_input)
    print(f'raw_input: {raw_input}')
    print(f'result: {result}')


    print(f'---------')
    raw_input2 = "Giá vàng miếng SJC đang được Ngân hàng Nhà nước ấn định, bằng cách niêm yết giá bán cho 4 ngân hàng quốc doanh và SJC, song chênh lệch giữa thị trường trong nước và quốc tế sáng nay nới rộng lên vùng 12,5 - 13,5 triệu đồng một lượng."
    result2 = classify_and_pronounce_number(raw_input2)
    print(f'raw_input2: {raw_input2}')
    print(f'result2: {result2}')

if __name__ == "__main__":
    main()
