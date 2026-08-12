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

  themeConfig: {
    // ★ 扩展点 1：以后加分类，这里加一行
    nav: [
      { text: '数学基础', link: '/数学基础/' }
      // { text: 'Python', link: '/Python/' },
      // { text: 'ROS', link: '/ROS/' },
    ],

    // ★ 扩展点 2：以后加分类，这里加一个同名 key
    sidebar: {
      '/数学基础/': [
        {
          text: '开始',
          items: [
            { text: '关于这个分类', link: '/数学基础/' },
            { text: '测试页', link: '/数学基础/测试页' }
          ]
        }
        // 整理好一个模块，就在这里加一组：
        // {
        //   text: '高中',
        //   collapsed: false,
        //   items: [
        //     { text: '01 集合与逻辑', link: '/数学基础/高中/01-集合与逻辑/集合与逻辑' }
        //   ]
        // }
      ]
    },

    search: { provider: 'local' },

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
