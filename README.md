# TxtView Terminal

一个轻量的终端文本查看器，用 Python 编写。它会在真实终端中使用 ANSI 控制序列渲染文本界面，适合阅读 `.txt`、Markdown 片段或带代码块的纯文本内容。

## 功能

- 双击批处理文件后弹出文件选择窗口
- 支持命令行直接传入文件路径
- 自动尝试多种常见文本编码：UTF-8、GBK、GB18030、Big5 等
- 根据终端宽度自动换行
- 支持中文等宽显示宽度处理
- 支持 Markdown 标题、引用、列表的简单着色
- 支持 fenced code block，并在安装 `Pygments` 后提供代码高亮
- 内置多种主题，可用 `t` 键即时切换
- 使用终端备用屏幕显示，退出后恢复原终端内容

## 运行

Windows 下可直接双击：

```text
运行-终端版.bat
```

脚本会自动检查 Python 和 pip，首次运行时会安装代码高亮依赖 `pygments`，然后打开文件选择窗口。

也可以在终端中直接运行：

```bash
python txtview.py
```

或指定要打开的文件：

```bash
python txtview.py sample_code.txt
```

## 主题

可在启动时指定主题：

```bash
python txtview.py --theme Dracula sample_code.txt
```

也可以列出全部主题：

```bash
python txtview.py --list-themes
```

当前内置主题搬自 Codex CLI 内置语法主题名，包括 `ansi`、`base16`、`Catppuccin Frappe`、`Catppuccin Latte`、`Catppuccin Macchiato`、`Catppuccin Mocha`、`Coldark-Cold`、`Coldark-Dark`、`DarkNeon`、`Dracula`、`GitHub`、`gruvbox-dark`、`gruvbox-light`、`InspiredGitHub`、`1337`、`Monokai Extended`、`Nord`、`OneHalfDark`、`OneHalfLight`、`Solarized (dark)`、`Solarized (light)` 等。

还可以通过环境变量设置默认主题：

```powershell
$env:TXTVIEW_THEME="Nord"
python txtview.py sample_code.txt
```

## 快捷键

| 按键 | 功能 |
| --- | --- |
| `↑` / `↓` | 上下滚动 |
| `PageUp` / `PageDown` | 翻页 |
| `Home` / `End` | 跳到开头/结尾 |
| `t` | 切换主题 |
| `q` / `Esc` | 退出 |

## 打包 EXE

Windows 下可双击：

```text
打包成exe.bat
```

脚本会安装或检查 `pyinstaller` 和 `pygments`，然后生成：

```text
dist\txtview.exe
```

注意：该程序依赖真实终端渲染，打包时需要使用 console 模式，不能使用 windowed 模式。

## 文件说明

- `txtview.py`：主程序
- `运行-终端版.bat`：运行入口，负责检查 Python 和依赖
- `打包成exe.bat`：打包入口，生成单文件 exe
- `txtview.spec`：PyInstaller 配置
- `sample_code.txt`：示例文本

## 建议

为了获得更清晰的显示效果，建议使用 Windows Terminal，并选择适合中文和代码显示的等宽字体，例如 Cascadia Mono、JetBrains Mono 或 Maple Mono NF CN。
