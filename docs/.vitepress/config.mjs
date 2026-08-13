import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { autoSidebar } from './sidebar.mjs'

// docs/ 的绝对路径（本文件在 docs/.vitepress/ 下，往上一层就是 docs/）
const DOCS_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

// 新增或删除 md 文件时自动重启 dev server。
//
// 为什么需要：侧边栏是 autoSidebar() 在「配置求值那一刻」扫一次磁盘生成的。
// 新建一篇笔记不会改动配置文件，VitePress 就不会重启，侧边栏一直停在启动时的
// 快照上——新笔记必须手动 Ctrl+C 重启才看得到。
//
// 为什么不用 server.restart()：本站开了 search.provider = 'local'，
// Vite 层的 restart 会让 MiniSearch 把同一篇文章重复入库，
// 报 "duplicate ID" 并 "server restart failed"，重启实际不生效。
// 改成碰一下本配置文件的时间戳，走 VitePress 自带的配置热重启，那条路径是好的。
function restartOnNewMarkdown() {
  const CONFIG_FILE = fileURLToPath(import.meta.url)
  const sep = path.sep
  const isNote = (file) =>
    file.endsWith('.md') &&
    file.includes(`${sep}docs${sep}`) &&
    !file.includes(`${sep}发布${sep}`) &&
    !file.includes(`${sep}node_modules${sep}`)

  return {
    name: 'restart-on-new-md',
    apply: 'serve',          // 只在 dev 生效，不影响 build
    configureServer(server) {
      // 重启后新 watcher 会把已有文件重放一遍 add 事件，
      // 静默期内不理会，否则一次新增会连环触发好几次重启
      const bootedAt = Date.now()
      const GRACE_MS = 2000
      let timer

      const touchConfig = (file) => {
        if (!isNote(file)) return
        if (Date.now() - bootedAt < GRACE_MS) return
        clearTimeout(timer)   // 批量新增合并成一次重启
        timer = setTimeout(() => {
          server.config.logger.info(`\n侧边栏有变动：${path.basename(file)}`)
          const now = new Date()
          fs.utimesSync(CONFIG_FILE, now, now)
        }, 200)
      }

      server.watcher.on('add', touchConfig)
      server.watcher.on('unlink', touchConfig)
    }
  }
}

export default {
  lang: 'zh-CN',
  title: '具身智能学习笔记',
  description: '从应用层开发转向具身智能的完整学习记录',

  markdown: {
    math: true          // 开启 LaTeX 公式（配合 markdown-it-mathjax3）
  },

  // 不发布到网站的内容
  srcExclude: [
    '**/00-写作规范与要求.md',
    '**/_工具/**'
  ],

  vite: {
    plugins: [restartOnNewMarkdown()]
  },

  themeConfig: {
    // ★ 扩展点 1：以后加分类，这里加一行
    nav: [
      { text: '数学基础', link: '/数学基础/' },
      { text: '编程基础', link: '/编程基础/' }
      // { text: 'ROS', link: '/ROS/' },
    ],

    // 侧边栏自动扫描 docs/ 生成，新增 md 文件无需改配置
    sidebar: autoSidebar(DOCS_ROOT),

    search: {
      provider: 'local',
      options: {
        miniSearch: {
          options: {
            // 中文按单字切分，英文/数字保持整词。不加这个，中文搜不到
            tokenize: (text) =>
              text.split(
                /[\n\r\p{Z}\p{P}]+|(?![a-zA-Z])(?=[\p{Script=Han}])|(?<=[\p{Script=Han}])(?![a-zA-Z])/u
              )
          },
          searchOptions: {
            combineWith: 'AND',   // 所有字都要命中，否则中文单字会匹配出一堆无关结果
            fuzzy: 0.2,
            prefix: true
          }
        },
        // 搜索框界面汉化
        translations: {
          button: {
            buttonText: '搜索文档',
            buttonAriaLabel: '搜索文档'
          },
          modal: {
            displayDetails: '显示详细列表',
            resetButtonTitle: '清除查询条件',
            backButtonTitle: '返回',
            noResultsText: '没有找到相关结果',
            footer: {
              selectText: '选择',
              selectKeyAriaLabel: '回车',
              navigateText: '切换',
              navigateUpKeyAriaLabel: '上箭头',
              navigateDownKeyAriaLabel: '下箭头',
              closeText: '关闭',
              closeKeyAriaLabel: 'esc'
            }
          }
        }
      }
    },

    // TODO: 把 your-username 换成你的 GitHub 用户名
    socialLinks: [
      { icon: 'github', link: 'https://github.com/your-username' }
    ],

    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一页', next: '下一页' },
    darkModeSwitchLabel: '主题',
    returnToTopLabel: '返回顶部',
    lastUpdated: { text: '最后更新' }
  }
}
