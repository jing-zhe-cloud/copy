# ⌨️ 键盘打字助手

模拟键盘逐字输出文本的桌面工具，支持英文和中文两种模式，适用于需要自动输入大量文本的场景。

## ✨ 功能特性

- **模拟键盘输入** — 将文本内容按照字符逐字模拟键盘输出到目标窗口
- **中/英文双模式** — 英文模式自动切换输入法并通过键盘码输出；中文模式通过剪贴板粘贴非ASCII字符
- **文件导入** — 支持选择 txt 文件或拖拽文件到窗口
- **3 秒倒计时** — 点击开始后有游戏风格倒计时，期间可自由定位光标
- **空格键暂停/继续** — 打字过程中按空格键暂停，窗口回到前台；再次按空格继续，窗口自动沉底
- **断点续打 / 从头开始** — 暂停后可选「从断点继续」或「从头开始」
- **打字速度控制** — 默认每字符 0.05 秒间隔，可在源码中调整

## 🖥️ 界面

无边框暗色主题窗口，自定义拖拽栏，可按标题栏拖动，悬停关闭按钮高亮。

## ⌨️ 快捷键

| 按键 | 场景 | 功能 |
|------|------|------|
| 空格键 | 打字中 / 已暂停 | 暂停 / 继续 |
| 空格键（全局） | 窗口在后台时 | 暂停/继续 |

## 🚀 快速开始

### 直接运行

双击 `dist\TypeSimulator.exe` 启动程序。

### 安装包

双击 `键盘打字助手_Setup.exe` 安装到系统，会自动创建桌面快捷方式和开始菜单项。

### 源码运行

```bash
python type_simulator.py
```

或通过命令行直接加载文件：

```bash
python type_simulator.py "path/to/file.txt"
```

## 🔧 打包

### 打包 EXE

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "TypeSimulator" type_simulator.py
```

### 使用 Inno Setup 打包安装程序

```bash
# 先安装 Inno Setup 6
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

## 📄 文件说明

| 文件 | 说明 |
|------|------|
| `type_simulator.py` | 主程序源码 |
| `setup.iss` | Inno Setup 安装脚本 |
| `dist/TypeSimulator.exe` | 打包后的可执行文件 |
| `键盘打字助手_Setup.exe` | 安装程序 |

## 🛠️ 技术栈

- **Python 3.12** + Tkinter
- **ctypes** — Windows API 调用（键盘模拟、拖拽文件、全局热键、窗口控制）
- **PyInstaller** — 打包为单文件 EXE
- **Inno Setup 6** — 制作安装程序

## ⚠️ 注意事项

- 英文模式下程序会自动将输入法切换到英文（`00000409`）
- 中文模式下非ASCII字符通过剪贴板 Ctrl+V 粘贴
- 部分安全软件可能误报键盘模拟行为，请添加信任
