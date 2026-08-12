// 自动扫描 docs/ 目录生成侧边栏。
// 新增一个 md 文件就自动出现在目录里，不用改任何配置。
//
// 规则：
//   - 忽略 assets/、_工具/、隐藏文件、index.md、00- 开头的文件
//   - 目录里只有一个 md 时，扁平化成单个条目（避免 "03-函数 > 函数" 这种冗余嵌套）
//   - 条目标题优先取 md 里的一级标题（# xxx），取不到就用文件名
//   - 排序按文件/目录名，所以用 01- 02- 这样的数字前缀就能控制顺序

import fs from "node:fs";
import path from "node:path";

const IGNORE_DIRS = new Set(["assets", "_工具", "node_modules"]);

/** 从 md 文件里读第一个一级标题 */
function titleOf(file, fallback) {
  try {
    const text = fs.readFileSync(file, "utf-8");
    // 跳过 frontmatter
    const body = text.replace(/^---\n[\s\S]*?\n---\n/, "");
    const m = body.match(/^#\s+(.+)$/m);
    if (m) return m[1].trim();
  } catch {}
  return fallback;
}

/** 01-集合与逻辑 → 01 集合与逻辑 */
function prettify(name) {
  return name.replace(/^(\d+)[-_]/, "$1 ");
}

function isVisible(name) {
  return !name.startsWith(".") && !IGNORE_DIRS.has(name);
}

/**
 * 递归构建某个目录下的条目列表
 * @param dir     绝对路径
 * @param urlBase 对应的网址前缀，如 /数学基础/高中
 */
function build(dir, urlBase) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }

  const dirs = entries
    .filter((e) => e.isDirectory() && isVisible(e.name))
    .sort((a, b) => a.name.localeCompare(b.name, "zh"));

  const files = entries
    .filter(
      (e) =>
        e.isFile() &&
        e.name.endsWith(".md") &&
        e.name !== "index.md" &&
        !e.name.startsWith("00-") &&
        isVisible(e.name)
    )
    .sort((a, b) => a.name.localeCompare(b.name, "zh"));

  const items = [];

  for (const d of dirs) {
    const childDir = path.join(dir, d.name);
    const childUrl = `${urlBase}/${d.name}`;
    const children = build(childDir, childUrl);
    if (children.length === 0) continue;

    // 只有一个条目时扁平化：03-函数/函数.md → 直接显示 "03 函数"
    if (children.length === 1 && children[0].link) {
      items.push({ text: prettify(d.name), link: children[0].link });
    } else {
      items.push({
        text: prettify(d.name),
        collapsed: true,
        items: children,
      });
    }
  }

  for (const f of files) {
    const stem = f.name.replace(/\.md$/, "");
    items.push({
      text: titleOf(path.join(dir, f.name), prettify(stem)),
      link: `${urlBase}/${stem}`,
    });
  }

  return items;
}

/**
 * 生成完整的 sidebar 配置对象。
 * docs/ 下每个一级目录 = 一个分类，各自有独立的侧边栏。
 */
export function autoSidebar(docsRoot) {
  const sidebar = {};

  const categories = fs
    .readdirSync(docsRoot, { withFileTypes: true })
    .filter((e) => e.isDirectory() && isVisible(e.name) && e.name !== ".vitepress")
    .sort((a, b) => a.name.localeCompare(b.name, "zh"));

  for (const c of categories) {
    const items = build(path.join(docsRoot, c.name), `/${c.name}`);
    if (items.length === 0) continue;

    sidebar[`/${c.name}/`] = [
      { text: "开始", items: [{ text: `关于${c.name}`, link: `/${c.name}/` }] },
      { text: c.name, items },
    ];
  }

  return sidebar;
}
