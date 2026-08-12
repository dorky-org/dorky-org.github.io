#!/usr/bin/env python3
"""Markdown 文档校验脚本（语雀兼容性检查）

用法：
    python3 _工具/validate_md.py "05-平面向量与解三角形/*.md"
    python3 _工具/validate_md.py "0*/*.md" "10-*/*.md"

检查以下几条会导致语雀渲染出错的问题：
  1. $$...$$ 独立公式块 —— 会导致公式居中，且干扰大纲解析
  2. ``` 代码围栏 —— 曾破坏语雀解析器
  3. 公式内的裸字符 < > ' " & —— 语雀导入时会转义成 HTML 实体，
     KaTeX 读不懂，报"非法 TeX 公式"。必须换成 \\lt \\gt ^{\\prime} 等命令
  4. 图片引用与 assets/ 下实际文件是否一一对应
  5. 目录中的条目与正文二级标题是否一致
"""
import re, sys, glob, os

MATH = re.compile(r'\$[^$\n]*\$')
# 公式内禁止出现的裸字符 → 应改用的 LaTeX 命令
FORBIDDEN = {'<': r'\lt', '>': r'\gt', "'": r'^{\prime}', '"': '（改用中文引号或去掉）'}


def check(path):
    errs = []
    s = open(path, encoding='utf-8').read()
    lines = s.split('\n')

    for i, line in enumerate(lines, 1):
        if '$$' in line:
            errs.append(f"L{i}: 出现 $$ 独立公式块（语雀会居中并可能吞掉标题）")
        if line.strip().startswith('```'):
            errs.append(f"L{i}: 出现代码围栏 ```")
        for m in MATH.finditer(line):
            span = m.group(0)
            for ch, fix in FORBIDDEN.items():
                if ch in span:
                    errs.append(f'L{i}: 公式内含裸字符 {ch!r}（应改用 {fix}）: {span[:40]}')

    # 图片引用 vs 实际文件
    d = os.path.dirname(path)
    refs = set(re.findall(r'!\[[^\]]*\]\(assets/([^)]+)\)', s))
    adir = os.path.join(d, 'assets')
    files = set(os.listdir(adir)) if os.path.isdir(adir) else set()
    for miss in sorted(refs - files):
        errs.append(f"引用了不存在的图片: assets/{miss}")
    for unused in sorted(files - refs):
        errs.append(f"图片存在但未被引用: assets/{unused}")

    # 目录 vs 正文标题
    heads = [h.strip() for h in re.findall(r'^## (.+)$', s, re.M)
             if h.strip() not in ('目录',) and not h.strip().startswith('写在前面')]
    toc = re.findall(r'^- \[([^\]]+)\]\(#', s, re.M)
    if toc:
        for t in toc:
            if t.strip() not in heads:
                errs.append(f"目录条目在正文中找不到对应标题: {t}")
        for h in heads:
            if h not in [t.strip() for t in toc]:
                errs.append(f"正文标题未出现在目录中: {h}")
    return errs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    paths = []
    for pat in sys.argv[1:]:
        paths += glob.glob(pat)
    bad = 0
    for p in sorted(paths):
        e = check(p)
        if e:
            bad += 1
            print(f"=== {p} ===")
            for x in e[:12]:
                print("  ", x)
    print(f"\n检查 {len(paths)} 个文件，{bad} 个有问题")


if __name__ == '__main__':
    main()
