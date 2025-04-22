import json
import re

class UnitPronunciation:

    def __init__(self, json_config_path = 'dataset/Don_vi_do_luong_Tieng_Viet.json'):
        self.unit_map = self.load_unit_config(json_config_path)
        self.unit_keys = sorted(self.unit_map.keys(), key=lambda x: -len(x))

    def load_unit_config(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            units = json.load(f)
        return {entry["Ký hiệu"]: entry["Tiếng Việt"] for entry in units}

    def normalize_text(self, text: str) -> str:
        normalized = text

        # 1) Xử lý dạng có dấu “/” như “65 triệu/m²”
        for unit in self.unit_keys:
            vi = self.unit_map[unit]
            pattern_slash = re.compile(
                rf'(?P<value>[\d\w\s,\.]+?)\s*/\s*{re.escape(unit)}\b'
            )
            normalized = pattern_slash.sub(lambda m: f"{m.group('value')} trên {vi}", normalized)

        # 2) Xử lý dạng “1m75” → “1 mét 75”
        pattern_mix = re.compile(r'(?P<meters>\d+)m(?P<centi>\d+)\b')
        normalized = pattern_mix.sub(lambda m: f"{m.group('meters')} mét {m.group('centi')}", normalized)

        # 3) Xử lý dạng “số cách đơn vị” như “50 m²”, “100 kg”
        for unit in self.unit_keys:
            vi = self.unit_map[unit]
            pattern_space = re.compile(
                rf'(?P<value>[\d\.,]+)\s+{re.escape(unit)}\b'
            )
            normalized = pattern_space.sub(lambda m: f"{m.group('value')} {vi}", normalized)

        # 4) Xử lý dạng “số liền đơn vị” như “9h”, “70kg”, “10km”
        for unit in self.unit_keys:
            vi = self.unit_map[unit]
            pattern_nospace = re.compile(
                rf'(?P<value>[\d\.,]+){re.escape(unit)}\b'
            )
            normalized = pattern_nospace.sub(lambda m: f"{m.group('value')} {vi}", normalized)

        return normalized
    
# Ví dụ sử dụng
if __name__ == "__main__":
    unit_converter = UnitPronunciation()
    
    sample = (
        "Giá là 65 triệu/m², vào hồi 9h sáng nay, "
        "anh nặng 70kg, cao 1m75 và chạy 10km mỗi ngày."
    )
    print("Trước: ", sample)
    print("Sau:   ", unit_converter.normalize_text(sample))
