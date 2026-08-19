+ 学习目标
    - 搭建环境，安装 Python 和 PyCharm
    - 了解如何配置
    - 了解新建项目&运行代码

# Python 介绍
:::info
+ 了解 Python：什么事 python
+ Python 的应用领域：能在哪些方面找工作
+ Python 的版本：工作开发场景下一般用哪个版本，就学哪个版本

:::

+ Python 时时下最流行、最火爆的编程语言之一
    - 1、简单（逻辑简单、语法简单）、易学，适应人群广泛
    - 2、免费、开源
    - 3、应用领域广泛（web 开发、爬虫、人工智能、数据分析、数据挖掘、自动化测试、自动化运帷）
+ Python 现有成就
    - Google 开源机器学习框架：TensorFlow
    - 开源社区主推学习框架：Scikit-learn
    - 百度开源深度学习框架：Paddle
+ Python 版本
    - Python 2.X
    - Python 3.X
        * Python 3.5
        * Python 3.6
        * **<font style="color:#DF2A3F;">Python 3.7</font>**
        * **<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">Python 3.14.6</font>****<font style="color:#DF2A3F;">（2026-06-10，当前最新正式发行版）</font>**

# 计算机组成
:::info
+ 了解 CPU 的作用
+ 了解内存的作用

:::

![画板](assets/计算机组成示意图.jpeg)

# Python 基础课程学习路径
![画板](assets/Python基础课程学习路径图.jpeg)

#  <font style="color:#000000;">解释器的作用 </font>
Python 解释器的作用：**<font style="color:#DF2A3F;">运行文件</font>**

+ Python 解释器种类
    - **<font style="color:#DF2A3F;">CPython</font>**，C 语言开发的解释器（官方），应用广泛的解释器
    - IPython，介于 CPython 的一种交互式解释器
    - 其他解释器
        * PyPy，基于 Python 语言开发的解释器
        * Jython，运行在 Java 平台的解释器，直接把 Python 代码编译成 Java 字节码执行
        * IromPython：运行在微软.Net 平台上的 Python 解释器，可以直接把 Python 代码编译成.Net 的字节码

# 下载 Python 解释器 🔴
+ 下载网址：[https://www.python.org/downloads/](https://www.python.org/downloads/)



![](assets/python官网下载页-1.png)

![](assets/python官网下载页-2.png)

# 安装解释器 🔴
+ 一路继续就行

![](assets/python解释器安装向导-1.png)

![](assets/python解释器安装向导-2.png)

![](assets/python解释器安装向导-3.png)

![](assets/python解释器安装向导-4.png)

![](assets/python解释器安装向导-5.png)



![](assets/python解释器安装向导-6.png)

# 配置环境变量&验证 🔴
+ 1、查看 python 的安装位置
+ 2、打开终端
+ 3、将 Python 直接拖拽到终端，可以得到 Python 的路径，复制路径

```cpp
/Library/Frameworks/Python.framework/Versions/3.14/bin 
```

+ 4、打开配置文件

```cpp
// 终端执行
open -a TextEdit ~/.zshrc
```

+ 5、将 python 路径添加到 PATH

```cpp
# Python 官网pkg环境变量
export PATH="/Library/Frameworks/Python.framework/Versions/3.14/bin:$PATH"
```

+ 6、保存退出，然后执行加载配置

```cpp
// 终端执行
source ~/.zshrc
```

+ 7、 验证

```cpp
python3 --version
```



![](assets/配置环境变量终端操作-1.png)

![](assets/配置环境变量终端操作-2.png)

![](assets/配置环境变量终端操作-3.png)

# PyCharm 的作用
PyCharm 是一种 Python IDE（集成开发环境），带有一整套可以帮助用户在使用 Python 语言开发时提高其效率的工具，内部集成的功能如下：

+ Project 管理
+ 智能提示
+ 语法高亮
+ 代码跳转
+ 调试代码
+ 解释代码（解释器）
+ 框架和库
+ ……

PythonCharm 分为专业版（professional）和社区版（community），社区版是免费的

从 2025.2 开始，JetBrains 合并版本，**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">不再分开社区版 / 专业版安装包</font>**

# PyCharm 下载和安装 🔴
+ 下载网址：[https://www.jetbrains.com.cn/pycharm/download/](https://www.jetbrains.com.cn/pycharm/download/)

![](assets/PyCharm下载页.png)

+ 安装

![](assets/PyCharm安装向导.png)

# 新建项目
![](assets/PyCharm新建项目-1.png)

![](assets/PyCharm新建项目-2.png)

![](assets/PyCharm新建项目-3.png)

# 书写代码&运行
+ 1、新建文件：【右键】-【New】-【Python File】-【输入文件名】-【OK】

![](assets/PyCharm新建python文件-1.png)

![](assets/PyCharm新建python文件-2.png)

+ 2、书写代码

![](assets/PyCharm编写代码示例.png)

+ 3、运行代码：【右键】-【run】

![](assets/PyCharm运行代码菜单.png)

![](assets/PyCharm运行结果输出.png)

# 基本设置
![](assets/PyCharm设置面板总览.png)
+ 1、外观设置

![](assets/PyCharm外观设置-1.png)

![](assets/PyCharm外观设置-2.png)

+ 2、解释器设置

![](assets/PyCharm解释器设置.png)

# Python Console：交互式开发环境
![](assets/PyCharm的Console交互环境.png)

# 通过终端运行 python 的 py 文件
+ 1、进入 python 文件所在目录
+ 2、python3 目标文件
    - 目标文件，可以使用 Tab 补全

```python
python3 文件名
```

