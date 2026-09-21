# 一箭又一箭 · One More Arrow

福州大学软件工程课程第二次个人作业。使用 Python 和 Pygame 开发，借助 ChatGPT 与 Codex 完成需求讨论、代码编写、调试和测试。

玩家需要观察箭头方向和阻挡关系，按合适的顺序点击箭头，让所有箭头飞出棋盘。

- 学号：102401411
- [课程主页](https://edu.cnblogs.com/campus/fzu/202601SofwareEngineering)
- [作业要求](https://edu.cnblogs.com/campus/fzu/202601SofwareEngineering/homework/16717)

## 游戏规则

1. 点击箭头后，程序检查其前方是否有其他箭头阻挡。
2. 无阻挡时，箭头飞出棋盘并消失；有阻挡时，箭头变红、移动后返回，并消耗一次失误机会。
3. 每关有三次失误机会，清空棋盘即通关，机会耗尽则失败。
4. 通关后可直接进入下一关，也可重新挑战或返回选关。
5. 前三关全部采用单格箭头；第四至第十二关加入占用 2～3 格的长箭头，点击任意占用格均可选中。

## 主要功能

- 7×7 棋盘，四方向箭头，十二个固定且经过可解性验证的关卡。
- 同页网格选关，默认窗口四列三行，窄窗口可滚动查看。
- 三星评价和逐关解锁，保存各关最佳星级。
- 游戏中和失败后可连续撤销本关操作，恢复箭头或剩余失误次数。
- 自动保存进度，重开后可继续；支持旧存档转换和损坏存档处理。
- 中文界面、窗口缩放适配、悬停反馈、抗锯齿箭头与动画。
- 七种合成音效，支持静音及音效设置保存。

星级根据通关时的剩余失误次数计算：剩余三次为三星、两次为两星、一次为一星。撤销会恢复操作前的失误次数。重新开始或进入另一关会清空本关撤销记录。

## 开发环境

| 项目 | 环境 |
| --- | --- |
| 开发与本人试玩平台 | macOS |
| 自动测试 Python 版本 | Python 3.9.6 |
| 图形与音频库 | Pygame 2.6.1 |
| AIGC 工具 | ChatGPT、Codex |

程序会自动查找 macOS 的冬青黑体、Windows 的微软雅黑／黑体／宋体，以及常见 Linux 中文字体路径。macOS 已完成运行与回归测试；Windows 字体路径通过模拟测试，尚未在真实 Windows 电脑上完成整套验证。

## 下载项目

无需安装 Git：点击仓库右上方 **Code → Download ZIP**，然后解压。必须先解压整个文件夹，不能直接在压缩包中打开 `main.py`。

也可以使用 Git 下载：

```bash
git clone https://github.com/bookiii98/one-more-arrow.git
```

ZIP 解压后的文件夹通常叫 `one-more-arrow-main`，Git 下载的文件夹叫 `one-more-arrow`。以下命令均在包含 `main.py` 和 `requirements.txt` 的目录中运行。

## 安装和运行

### macOS

如果通过 ZIP 下载并解压在“下载”文件夹中：

```bash
cd ~/Downloads/one-more-arrow-main
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

若文件夹放在其他位置，先把 `cd` 后面的路径替换为实际路径。

### Windows（PowerShell）

先安装 Python（建议使用 Python 3.12），安装时勾选 **Add python.exe to PATH**。打开解压后的项目文件夹，在资源管理器地址栏输入 `powershell` 并回车，然后依次执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

如果提示找不到 `python`，确认 Python 已安装并重新打开终端；也可以用 `py -3 -m venv .venv` 创建环境。后续两行仍保持不变。

以上命令直接使用虚拟环境中的 Python，不需要运行激活脚本，也不需要修改 PowerShell 执行策略。以后再次启动，只需进入项目目录执行最后一行。

### 中文字体配置

一般的中文 Windows 和 macOS 系统无需修改代码。Windows 字体目录通过 `WINDIR` 自动定位，不要求系统必须安装在 C 盘。

如果系统缺少上述字体，程序会在终端提示 `No Chinese font found`。请安装支持简体中文的字体，或通过环境变量指定本机的字体文件路径：

Windows PowerShell 示例（请替换为实际存在的路径）：

```powershell
$env:ONE_MORE_ARROW_FONT = 'C:\Windows\Fonts\msyh.ttc'
.\.venv\Scripts\python.exe main.py
```

macOS／Linux 示例：

```bash
export ONE_MORE_ARROW_FONT='/实际路径/中文字体.ttf'
.venv/bin/python main.py
```

支持 `.ttf`、`.ttc`、`.otf` 字体文件；文件本身必须包含中文字符。不要把 macOS 的系统字体路径直接复制到 Windows 使用。

### 常见运行问题

- **提示缺少 pygame**：用上面虚拟环境中的 Python 再执行安装依赖命令，确保安装和运行使用同一个环境。
- **窗口打不开或出现报错**：从终端启动，保留报错内容便于定位，不要只双击 `.py` 文件。
- **保存失败**：把项目解压到有写入权限的目录，例如“下载”或“文档”，不要放在系统受保护的安装目录。
- **没有音频设备**：游戏会自动禁用音效，不影响基础玩法。

游戏不需要 API Key、网络服务或额外下载美术、音效素材。首次安装依赖需要网络。当前提供 Python 源码版，尚未打包成独立可执行程序。

## 操作说明

| 操作 | 功能 |
| --- | --- |
| 鼠标左键 | 点击箭头和按钮 |
| 选择关卡 | 进入已经解锁的关卡 |
| 继续游戏 | 恢复保存的棋盘 |
| 重新开始／重新挑战 | 恢复本关初始布局和三次失误机会 |
| 撤销一步 | 撤回本关上一次有效点击；没有记录时按钮置灰 |
| 返回关卡 | 回到选关界面 |
| 继续下一关 | 通关后直接进入下一关 |
| 鼠标滚轮／触控板 | 在选关页上下滚动 |
| M 键 | 随时切换音效开关 |

首页和选关页右上角也有音效开关。音频设备不可用时显示“音效不可用”，游戏仍可正常进行。

## 游戏截图

### 开始界面

![开始界面](https://img2024.cnblogs.com/blog/3847942/202609/3847942-20260921160836072-60863758.png)

### 十二关同页选择

![关卡选择](https://img2024.cnblogs.com/blog/3847942/202609/3847942-20260921160429078-1842518710.png)

### 游戏过程

![游戏过程](https://img2024.cnblogs.com/blog/3847942/202609/3847942-20260921161744761-982748605.png)

### 通关结果

![通关结果](https://img2024.cnblogs.com/blog/3847942/202609/3847942-20260921160524512-97083013.png)

### 失败与重试

![失败界面](https://img2024.cnblogs.com/blog/3847942/202609/3847942-20260921160542978-1672114306.png)

以上为本人博客中使用的游戏截图，图片托管于博客园；图片显示需要网络，不影响游戏离线运行。

## 项目结构

```text
one-more-arrow/
├── README.md                # 项目与运行说明
├── requirements.txt         # Python 依赖
├── main.py                  # 初始化、状态协调、事件循环
├── config.py                # 窗口、字体、颜色和尺寸配置
├── levels.py                # 固定关卡、关卡名及旧关卡兼容数据
├── game_logic.py            # 路径检测、游戏规则、动画状态、撤销
├── ui.py                    # 界面布局与绘制
├── progress.py              # 存档校验、保存和恢复
├── audio.py                 # 本地合成和播放短音效
├── test_fonts.py            # 跨平台字体查找与中文渲染
├── test_game.py             # 基础玩法和完整通关流程
├── test_basic_levels.py     # 单格基础关卡与兼容处理
├── test_progress.py         # 保存进度与异常处理
├── test_undo.py             # 撤销与记录恢复
├── test_level_selection.py  # 网格选关、滚动和进度兼容
└── test_audio.py            # 音效触发、静音和设备异常
```

## 存档说明

存档自动保存在项目目录下的 `saves/progress.json`，包含当前关卡、剩余箭头、失误次数、最佳星级、解锁状态、撤销记录和音效设置。

程序先写临时文件，再替换正式存档。读取失败时会尝试保留 `.damaged` 副本，并使用初始进度。旧版前三关的长箭头存档会转换为单格，保留进度并清空受规则变化影响的旧撤销记录。

`saves/`、Python 缓存、虚拟环境和重构前的备份不纳入版本管理。需要重置全部进度时，先关闭游戏，再自行备份并移走 `saves/progress.json`。

## 测试

在项目根目录执行以下命令。环境变量只对当前终端会话生效，测试后恢复，避免随后运行游戏时仍处于无窗口模式。

macOS：

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m unittest -v
```

Windows PowerShell：

```powershell
$oldVideo = $env:SDL_VIDEODRIVER
$oldAudio = $env:SDL_AUDIODRIVER
try {
    $env:SDL_VIDEODRIVER = 'dummy'
    $env:SDL_AUDIODRIVER = 'dummy'
    .\.venv\Scripts\python.exe -m unittest -v
} finally {
    $env:SDL_VIDEODRIVER = $oldVideo
    $env:SDL_AUDIODRIVER = $oldAudio
}
```

当前共 25 项自动测试，在 macOS 无窗口环境运行通过。测试套件包含游戏功能与跨平台字体查找检查。Windows 路径测试使用临时目录模拟，不等同于真实 Windows 系统验收。

测试覆盖四方向路径判断、多格点击、十二关连续通关、碰撞失败、重新开始、单页选关、窗口缩放、撤销、存档兼容和音效设置等。无窗口及模拟音频模式用于验证逻辑，不会打开可玩的窗口或播放实际声音。

本人另已完成十二关试玩，以及基本操作、动画、窗口缩放、音效和保存恢复检查。

## AIGC 与素材说明

ChatGPT 用于需求讨论与方案分析，Codex 用于代码修改、重构和测试。开发者负责提出需求、反馈问题、决定功能取舍和实际试玩。

界面和箭头通过程序绘制，短音效由 `audio.py` 本地合成，关卡为本项目开发过程中生成、筛选并固定的数据。未使用原商业游戏的代码、美术、音效或关卡。
