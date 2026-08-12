#!/usr/bin/env bash
#
# 写完一篇笔记之后，跑这一条就够了。
#
# 用法：
#     ./_工具/发布.sh                    # 用默认提交信息
#     ./_工具/发布.sh "docs: 新增函数模块"  # 自定义提交信息
#
# 依次做四件事：
#     ① 图片：SVG → PNG → 腾讯云 COS，生成 发布/ 里的发布版 md
#     ② 构建检查：本地编译一遍，有死链或语法错就提前发现
#     ③ 安全检查：确认 .env 没被误加进提交
#     ④ 提交并推送，GitHub Actions 自动部署网站

set -euo pipefail

cd "$(dirname "$0")/.."
MSG="${1:-docs: 更新笔记}"

echo ""
echo "① 处理图片、生成发布版"
echo "────────────────────────────────"
python3 _工具/publish.py

echo ""
echo "② 构建检查"
echo "────────────────────────────────"
npm run docs:build --silent

echo ""
echo "③ 提交推送"
echo "────────────────────────────────"

if [ -z "$(git status --porcelain)" ]; then
  echo "没有改动，跳过提交"
else
  git add -A

  # 兜底：万一 .gitignore 被改坏，也不能让密钥推上去
  if git diff --cached --name-only | grep -qE '(^|/)\.env$'; then
    echo ""
    echo "🚨 .env 出现在待提交列表里，已中止！"
    echo "   仓库是公开的，密钥绝对不能提交。"
    echo "   执行：git reset && 检查 .gitignore 里有没有 .env 这一行"
    exit 1
  fi

  git status --short
  git commit -m "$MSG"
  git push
fi

echo ""
echo "────────────────────────────────"
echo "✅ 完成"
echo ""
echo "网站：GitHub Actions 正在自动部署，两三分钟后生效"
echo "平台：打开 发布/ 里对应的 md，全选复制 → 粘进 CSDN"
echo ""
