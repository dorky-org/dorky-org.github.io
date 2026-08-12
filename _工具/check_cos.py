#!/usr/bin/env python3
"""
腾讯云 COS 配置诊断。

用法：
    python3 _工具/check_cos.py

依次检查四件事，哪一步红了就知道问题出在哪：
    0. .env 格式是否规范（长度、前缀、有没有混进空格引号）
    1. 密钥是否有效
    2. 目标存储桶能否访问
    3. 有没有写权限

⚠️ 全程不会打印密钥内容，只输出长度和前 4 位。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    env_file = ROOT / ".env"
    if not env_file.exists():
        print("✗ 找不到 .env，先执行：cp .env.example .env")
        sys.exit(1)

    env = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")

    sid = env.get("COS_SECRET_ID", "")
    skey = env.get("COS_SECRET_KEY", "")
    bucket = env.get("COS_BUCKET", "")
    region = env.get("COS_REGION", "")

    print("\n=== 0. .env 格式 ===")
    ok_id = sid.startswith("AKID") and len(sid) == 36
    ok_key = len(skey) == 32
    print(f"SecretId   长度 {len(sid):>3} (应为 36)  前缀 {sid[:4]!r} (应为 'AKID')  {'✅' if ok_id else '❌'}")
    print(f"SecretKey  长度 {len(skey):>3} (应为 32)                          {'✅' if ok_key else '❌'}")
    print(f"Bucket     {bucket}")
    print(f"Region     {region}")

    for name, val in (("COS_SECRET_ID", sid), ("COS_SECRET_KEY", skey)):
        if " " in val or ":" in val or '"' in val or "'" in val:
            print(f"❌ {name} 里混进了空格/冒号/引号——只保留纯值")

    if not (ok_id and ok_key):
        print("\n先把 .env 改对再往下测。\n")
        sys.exit(1)

    try:
        from qcloud_cos import CosConfig, CosS3Client
    except ImportError:
        print("\n✗ 缺少 SDK：python3 -m pip install cos-python-sdk-v5\n")
        sys.exit(1)

    client = CosS3Client(CosConfig(Region=region, SecretId=sid, SecretKey=skey))

    print("\n=== 1. 密钥是否有效 ===")
    try:
        r = client.list_buckets()
        buckets = r.get("Buckets", {}).get("Bucket", [])
        buckets = [buckets] if isinstance(buckets, dict) else buckets
        print("✅ 有效。账号下的存储桶：")
        for b in buckets:
            mark = " ← 目标" if b["Name"] == bucket else ""
            print(f"   - {b['Name']}  ({b['Location']}){mark}")
    except Exception as e:
        print(f"❌ {e}")
        print("   → 密钥填错了，或者子账号没有 COS 权限")

    print("\n=== 2. 目标存储桶 ===")
    try:
        client.head_bucket(Bucket=bucket)
        print("✅ 存在且可访问")
    except Exception as e:
        print(f"❌ {e}")
        print("   → 检查桶名和地域是否和控制台一致")

    print("\n=== 3. 写权限 ===")
    try:
        client.put_object(Bucket=bucket, Body=b"x", Key="__perm_test.txt")
        client.delete_object(Bucket=bucket, Key="__perm_test.txt")
        print("✅ 可以写入")
    except Exception as e:
        print(f"❌ {e}")
        print("   → 子账号缺少 QcloudCOSFullAccess 策略")
    print()


if __name__ == "__main__":
    main()
