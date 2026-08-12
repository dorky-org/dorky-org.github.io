#!/usr/bin/env python3
"""SVG 配图校验脚本

用法：
    python3 _工具/validate_svg.py "04-三角函数与恒等变换/assets/*.svg"
    python3 _工具/validate_svg.py "0*/assets/*.svg"

检查三件事：
  1. XML 良构性（能否被解析）
  2. 图形元素坐标是否越出 viewBox（会被裁切）
  3. 文字的估算渲染宽度是否越出 viewBox（最容易漏掉的一项）

字符宽度估算：中日韩全角 1.0×字号，窄字符（括号/斜杠/空格）0.32×，
运算符 0.62×，字母数字 0.57×。再按 text-anchor 换算实际横向区间。
"""
import xml.etree.ElementTree as ET
import re, sys, glob, unicodedata

NARROW = set("()[]/|.,'`:; −-")
OPS = set("=+<>≥≤≠×÷±≈")


def char_width(c, fs):
    if unicodedata.east_asian_width(c) in ('W', 'F'):
        return fs
    if c in NARROW:
        return fs * 0.32
    if c in OPS:
        return fs * 0.62
    if c.isdigit() or c.isalpha():
        return fs * 0.57
    return fs * 0.5


def text_width(s, fs):
    return sum(char_width(c, fs) for c in s)


def parse_translate(t):
    m = re.search(r'translate\(([-\d.]+)[, ]+([-\d.]+)\)', t or '')
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)


def collect_text(el):
    parts = [el.text or '']
    for c in el:
        if c.tag.split('}')[-1] == 'tspan':
            parts.append(c.text or '')
        parts.append(c.tail or '')
    return ''.join(parts)


def check(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return [f"XML PARSE ERROR: {e}"]
    vb = root.get('viewBox')
    if not vb:
        return ["NO viewBox"]
    vx, vy, vw, vh = map(float, vb.split())
    errs = []

    def walk(el, ox, oy, fs, anchor):
        tag = el.tag.split('}')[-1]
        tx, ty = parse_translate(el.get('transform'))
        ox, oy = ox + tx, oy + ty
        fs = float(el.get('font-size', fs))
        anchor = el.get('text-anchor', anchor)
        pts = []

        if tag in ('circle', 'ellipse'):
            cx = float(el.get('cx', 0)); cy = float(el.get('cy', 0))
            r = float(el.get('r', el.get('rx', 0)))
            pts = [(cx - r, cy - r), (cx + r, cy + r)]
        elif tag == 'line':
            pts = [(float(el.get('x1', 0)), float(el.get('y1', 0))),
                   (float(el.get('x2', 0)), float(el.get('y2', 0)))]
        elif tag == 'rect':
            x = float(el.get('x', 0)); y = float(el.get('y', 0))
            pts = [(x, y), (x + float(el.get('width', 0)), y + float(el.get('height', 0)))]
        elif tag in ('polygon', 'polyline'):
            n = list(map(float, el.get('points', '').replace(',', ' ').split()))
            pts = list(zip(n[0::2], n[1::2]))
        elif tag == 'text':
            x = float(el.get('x', 0)); y = float(el.get('y', 0))
            s = collect_text(el); w = text_width(s, fs)
            if anchor == 'middle':
                x0, x1 = x - w / 2, x + w / 2
            elif anchor == 'end':
                x0, x1 = x - w, x
            else:
                x0, x1 = x, x + w
            if ox + x0 < vx - 2 or ox + x1 > vx + vw + 2:
                errs.append(f'TEXT overflow x[{ox+x0:.0f},{ox+x1:.0f}] vs width {vw:.0f}: "{s[:24]}"')
            if not (vy - 2 <= oy + y <= vy + vh + 2):
                errs.append(f"TEXT baseline y={oy+y:.0f} outside height {vh:.0f}")

        for px, py in pts:
            if not (vx - 2 <= ox + px <= vx + vw + 2 and vy - 2 <= oy + py <= vy + vh + 2):
                errs.append(f"{tag} point ({ox+px:.1f},{oy+py:.1f}) outside viewBox {vb}")

        for c in el:
            if c.tag.split('}')[-1] != 'tspan':
                walk(c, ox, oy, fs, anchor)

    walk(root, 0.0, 0.0, 16.0, 'start')
    return errs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    bad = 0
    files = sorted(glob.glob(sys.argv[1]))
    for p in files:
        e = check(p)
        if e:
            bad += 1
            print(f"=== {p} ===")
            for x in e[:8]:
                print("  ", x)
    print(f"\n检查 {len(files)} 个文件，{bad} 个有问题")
    # 顺带提醒裸根号（应改用 <path> 手工绘制）
    naked = [p for p in files if '√' in open(p, encoding='utf-8').read()]
    if naked:
        print("⚠ 以下文件含裸露的 √ 字符（应改用 <path> 手工画根号）：")
        for p in naked:
            print("  ", p)


if __name__ == '__main__':
    main()
