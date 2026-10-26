"""Render readable SS2 panels, preserving every canonical message exactly once."""
import re
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/diagrams/Use-case detail-scenario/SS2/Sequence diagrams'
GENERATED = ROOT / 'docs/report/assets/sequence_panels'
JAR = ROOT / 'tools/plantuml.jar'
CONFIG = {
    'UC_SS2_02_NguyenAnhTai_sequence': [
        ((1, 2), 'Xác thực, lựa chọn xe và chi phí'),
        ((3,), 'Đặt cọc và xác nhận giữ chỗ'),
        ((4,), 'Hủy đơn và hết hạn Check-in'),
    ],
    'UC_SS2_04_NguyenAnhTai_sequence': [
        ((1, 2), 'Xác thực phiên và lập hóa đơn'),
        ((3,), 'Thanh toán và quyết toán tiền cọc'),
        ((4, 5), 'Mở barie và giải phóng tài nguyên'),
    ],
}


def main():
    GENERATED.mkdir(parents=True, exist_ok=True)
    for name, panels in CONFIG.items():
        text = (SOURCE / f'{name}.puml').read_text()
        points = list(re.finditer(r'^autonumber (\d+)\.1\s*$', text, re.M))
        header = text[:points[0].start()]
        # The panels live under report/assets, not the canonical SS2 directory.
        header = header.replace('!include ../../../common.puml',
                                '!include ../../../diagrams/common.puml')
        end = text.index('@enduml', points[-1].start())
        chunks = {int(match[1]): text[match.start():points[i+1].start() if i+1 < len(points) else end] for i, match in enumerate(points)}
        ordered = [group for groups, _ in panels for group in groups]
        if ordered != list(chunks) or ''.join(chunks[g] for g in ordered) != text[points[0].start():end]:
            raise ValueError(f'Panel coverage changed or omitted canonical content: {name}')
        for number, (groups, title) in enumerate(panels, 1):
            panel_name = f'{name}_p{number}'
            panel_header = header.replace('@startuml ' + name, '@startuml ' + panel_name)
            panel_header = re.sub(r'^title .*$', f'title "{name[:10]} - Phần {number}/{len(panels)}: {title}"', panel_header, flags=re.M)
            continuation = f'\nnote over UI, AppState #LightCyan\n  Phần {number}/{len(panels)} - Nhóm nghiệp vụ: {", ".join(map(str, groups))}\n  Đọc theo thứ tự các phần; thông điệp giữ số của sơ đồ gốc.\nend note\n'
            path = GENERATED / f'{panel_name}.puml'
            path.write_text(panel_header + continuation + ''.join(chunks[g] for g in groups) + '@enduml\n')
            subprocess.run(['java', '-DPLANTUML_LIMIT_SIZE=16384', '-jar', str(JAR), '-Playout=smetana', '-charset', 'UTF-8', '-tpng', str(path)], check=True, capture_output=True)
            image_path = path.with_suffix('.png')
            (SOURCE / image_path.name).write_bytes(image_path.read_bytes())
            with Image.open(image_path) as image:
                print(f'{panel_name}: {image.size}; canonical groups {groups}')


if __name__ == '__main__':
    main()
