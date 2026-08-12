#!/usr/bin/env python3
"""
发布助手 —— 把源 md 转成可以直接粘贴到 CSDN / 掘金 / 知乎的发布版。

用法：
    python3 _工具/publish.py                          # 处理 docs/ 下全部 md
    python3 _工具/publish.py docs/数学基础/03-函数      # 只处理指定目录或单个 md
    python3 _工具/publish.py --force                  # 忽略缓存，强制重新上传所有图
    python3 _工具/publish.py --dry-run                # 只看会做什么，不实际上传

它做三件事（**全程不修改任何源文件**）：
    1. SVG → PNG        用 rsvg-convert，3 倍分辨率
    2. PNG → 腾讯云 COS  只上传内容变化过的图
    3. 生成 发布/<同样的相对路径>/xxx.md，图片路径替换成 COS 的 URL

图片命名规则（镜像本地路径，去掉 docs/ 和 assets/）：
    docs/数学基础/03-函数/assets/unit-circle.svg
      → https://<桶>.cos.<地域>.myqcloud.com/数学基础/03-函数/unit-circle.png

URL 固定不变，改图重跑就是覆盖上传，引用它的地方自动更新。
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

# ---------------------------------------------------------------- 配置

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = ROOT / "发布"
CACHE_FILE = ROOT / "_工具" / ".upload-cache.json"
PNG_CACHE = ROOT / "_工具" / ".png-cache"

SCALE = 3          # PNG 相对 SVG 的放大倍数，620 宽的图 → 1860 宽
CACHE_SECONDS = 600  # COS 上图片的缓存时间，短一点方便改图后快速生效

# md 图片语法：![alt](路径) 或 ![alt](路径 "标题")
IMG_RE = re.compile(r'!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')

# 这些前缀说明已经是网址，跳过
SKIP_PREFIXES = ("http://", "https://", "//", "data:")


# ---------------------------------------------------------------- 工具函数

def die(msg):
    print(f"\n✗ {msg}\n", file=sys.stderr)
    sys.exit(1)


def load_env():
    """从项目根目录的 .env 读取配置。不用第三方库，少一个依赖。"""
    env_file = ROOT / ".env"
    if not env_file.exists():
        die("找不到 .env 文件。\n"
            "  请复制 .env.example 为 .env，填入你的腾讯云密钥：\n"
            "    cp .env.example .env")

    env = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

    required = ["COS_SECRET_ID", "COS_SECRET_KEY", "COS_BUCKET", "COS_REGION"]
    missing = [k for k in required if not env.get(k)]
    if missing:
        die(f".env 里缺少这些配置：{', '.join(missing)}")

    # 提前拦住最常见的错误：把控制台上的标签文字一起复制进来了
    sid, skey = env["COS_SECRET_ID"], env["COS_SECRET_KEY"]
    if not (sid.startswith("AKID") and len(sid) == 36):
        die(f"COS_SECRET_ID 格式不对（当前 {len(sid)} 位，前缀 {sid[:4]!r}）。\n"
            "  正确的是 36 位、以 AKID 开头的纯字符串，\n"
            "  不要带 'SecretId:' 这类标签文字、冒号、引号或空格。\n"
            "  详细诊断：python3 _工具/check_cos.py")
    if len(skey) != 32:
        die(f"COS_SECRET_KEY 格式不对（当前 {len(skey)} 位，应为 32 位）。\n"
            "  详细诊断：python3 _工具/check_cos.py")
    return env


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def svg_size(svg: Path):
    """从 SVG 里读出宽度，用于计算输出像素。读不到就返回 None。"""
    try:
        text = svg.read_text(encoding="utf-8", errors="ignore")[:2000]
    except OSError:
        return None
    m = re.search(r'viewBox\s*=\s*["\']\s*[\d.+-]+\s+[\d.+-]+\s+([\d.]+)', text)
    if m:
        return float(m.group(1))
    m = re.search(r'\swidth\s*=\s*["\']([\d.]+)', text)
    return float(m.group(1)) if m else None


def svg_to_png(svg: Path, png: Path) -> bool:
    """用 rsvg-convert 转换。成功返回 True。"""
    png.parent.mkdir(parents=True, exist_ok=True)
    width = svg_size(svg)
    cmd = ["rsvg-convert", "-o", str(png)]
    if width:
        cmd += ["-w", str(int(width * SCALE))]
    else:
        cmd += ["-z", str(SCALE)]   # 读不到宽度就按倍数缩放
    cmd.append(str(svg))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not png.exists():
        print(f"    ✗ 转换失败：{svg.name}")
        if result.stderr.strip():
            print(f"      {result.stderr.strip()}")
        return False
    return True


def cos_key_for(img_abs: Path) -> str:
    """本地路径 → COS 上的对象路径。去掉 docs/ 和 assets/，扩展名统一成 .png。"""
    rel = img_abs.relative_to(DOCS)
    parts = [p for p in rel.parts if p != "assets"]
    filename = Path(parts[-1]).stem + ".png"
    return "/".join(parts[:-1] + [filename])


# ---------------------------------------------------------------- 主流程

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    dry_run = "--dry-run" in sys.argv

    if not shutil.which("rsvg-convert"):
        die("找不到 rsvg-convert，请先安装：\n    brew install librsvg")

    if not DOCS.exists():
        die(f"找不到 docs 目录：{DOCS}")

    # 确定要处理哪些 md
    target = Path(args[0]).resolve() if args else DOCS
    if target.is_file():
        md_files = [target]
    else:
        md_files = sorted(
            p for p in target.rglob("*.md")
            if ".vitepress" not in p.parts and not p.name.startswith("00-")
        )

    if not md_files:
        die(f"在 {target} 下没找到任何 .md 文件")

    env = load_env()
    base_url = f"https://{env['COS_BUCKET']}.cos.{env['COS_REGION']}.myqcloud.com"

    client = None
    if not dry_run:
        try:
            from qcloud_cos import CosConfig, CosS3Client
        except ImportError:
            die("缺少腾讯云 COS SDK，请安装：\n    python3 -m pip install cos-python-sdk-v5")
        client = CosS3Client(CosConfig(
            Region=env["COS_REGION"],
            SecretId=env["COS_SECRET_ID"],
            SecretKey=env["COS_SECRET_KEY"],
        ))

    cache = {} if force else load_cache()
    uploaded = skipped = failed = 0

    print(f"\n{'[试运行] ' if dry_run else ''}共 {len(md_files)} 个 md 文件\n")

    for md in md_files:
        rel_md = md.relative_to(DOCS)
        print(f"── {rel_md}")

        text = md.read_text(encoding="utf-8")
        replacements = {}

        for alt, src in IMG_RE.findall(text):
            if src.startswith(SKIP_PREFIXES):
                continue

            img_abs = (md.parent / src).resolve()
            if not img_abs.exists():
                print(f"    ✗ 图片不存在：{src}")
                failed += 1
                continue

            key = cos_key_for(img_abs)
            digest = sha256(img_abs)

            # 内容没变就跳过上传，但 URL 照样要替换进发布版
            if cache.get(key) == digest:
                skipped += 1
            else:
                if img_abs.suffix.lower() == ".svg":
                    png = PNG_CACHE / key
                    if not svg_to_png(img_abs, png):
                        failed += 1
                        continue
                    upload_from = png
                else:
                    upload_from = img_abs

                size_kb = upload_from.stat().st_size / 1024
                if dry_run:
                    print(f"    ↑ [试运行] {key}  ({size_kb:.0f} KB)")
                else:
                    try:
                        with upload_from.open("rb") as f:
                            client.put_object(
                                Bucket=env["COS_BUCKET"],
                                Body=f,
                                Key=key,
                                ContentType="image/png",
                                CacheControl=f"max-age={CACHE_SECONDS}",
                            )
                    except Exception as e:
                        print(f"    ✗ 上传失败 {key}：{e}")
                        failed += 1
                        continue
                    print(f"    ↑ {key}  ({size_kb:.0f} KB)")
                    cache[key] = digest
                uploaded += 1

            replacements[src] = f"{base_url}/{urllib.parse.quote(key)}"

        # 生成发布版：只替换图片路径，其余一个字不动
        out_text = text
        for src, url in replacements.items():
            out_text = out_text.replace(f"]({src})", f"]({url})")

        out_path = OUT / rel_md
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text, encoding="utf-8")

    if not dry_run:
        save_cache(cache)

    print(f"\n{'─' * 50}")
    print(f"上传 {uploaded} 张 · 跳过 {skipped} 张（未变化） · 失败 {failed} 张")
    print(f"发布版已生成到：{OUT}")
    if failed:
        print("\n⚠️  有失败项，请检查上面的报错")
    print()


if __name__ == "__main__":
    main()
