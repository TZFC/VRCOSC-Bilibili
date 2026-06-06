# VRCOSC-Bilibili (v3)

[English (User Guide)](README.md) | [中文 (用户指南)](README-zh-CN.md) | [English (Developer Guide)](README-dev.md) | [中文 (开发者指南)](README-dev-zh-CN.md)

欢迎使用 **VRCOSC-Bilibili**，这是连接哔哩哔哩（Bilibili）直播与 VRChat 最简单的方式！
本程序可以无缝地将您的 B站直播间与 VRChat 的 OSC 系统连接起来，允许您通过直播弹幕、礼物或醒目留言（Super Chat）等事件来触发模型动画、移动角色、控制相机或在聊天框中打字。

## 🚀 快速开始

1. **启动程序**
   只需双击 Start.bat。首次启动时会弹出一个加载界面，自动设置 Python 环境并下载所需的依赖项（这可能需要一两分钟）。完成后，程序会自动在浏览器中打开一个类似 Unity 界面的网页。您全程无需接触命令行！

2. **登录 B 站**
   在主设置界面中，点击 **Auto-Scan Browsers for Login（自动扫描浏览器登录）**。程序将安全地在您安装的浏览器（Chrome、Firefox、Edge 等）中搜索已登录的 B站账号，并展示您的个人资料卡片以供选择。高级用户也可以使用手动方式填写 Cookie。

3. **配置连接**
   输入您的 **Bilibili Room ID（直播间号）**。OSC 端口已经默认配置为 VRChat 的标准端口（向 VRChat 发送为 9000，接收为 9001），通常不需要修改。然后点击 **Save & Apply Config（保存并应用配置）**。

4. **创建第一条规则！**
   点击左侧 **Hierarchy（层级）** 面板中的 + 按钮，添加一条新规则。

## 🎛️ 如何编写规则（类似 Unity Inspector 面板）

当您选中一条规则时，右侧的面板（**Inspector（检查器）**）将允许您对其进行详细配置：

### Triggers（触发条件，"如果..."）
选择触发规则的 B站直播事件：
- **Event Type（事件类型）:** 可选弹幕（Danmaku）、礼物（Gift）、醒目留言（SC）、大航海（Guard）或入场（Enter）。
- **Keyword（关键词）:** 想在别人发弹幕说“跳”的时候触发动画？在这里填写“跳”（仅对弹幕生效）。
- **Min Value（最低价值）:** 对于礼物或 SC，您可以指定触发操作所需的最低价格（元）。

### Action（执行动作，"那么..."）
选择 VRChat 中发生的操作：
- **Endpoint（OSC 地址）:** 发送到 VRChat 的 OSC 终端地址。例如：
  - /avatar/parameters/Dance (触发模型上的某个参数)
  - /chatbox/input (在聊天框中打字)
  - /input/Jump (让角色跳跃)
  - /usercamera/Capture (使用相机拍照)
- **Action Type（动作类型）:** Set (设定一个特定值)、Toggle (在真/假之间切换) 或 Add (增加一个数值)。
- **Value（值）:** 发送的具体值（例如 "true"，"false"，"1.5"，或是发送到聊天框的文字）。

### Sync Mode (双向同步模式)
VRChat 模型是可交互的。如果用户在 VR 中通过 Action Menu 手动更改了某个参数：
- **Overwrite（覆盖）:** 程序将非常固执，立即用规则中设定的状态覆盖用户在游戏中的手动更改。
- **Respect（尊重）:** 程序将监听 VRChat，并接受用户的手动更改，与游戏内状态保持同步。

## 📦 分享配置

想与朋友分享您复杂的模型触发设置吗？
在 Hierarchy（层级）面板中使用 **Exp**（导出）按钮将您的规则下载为 .json 文件，并使用 **Imp**（导入）按钮加载其他人的配置！

---
*提示：请确保您已在 VRChat 游戏中启用了 OSC (操作菜单 > Options > OSC > Enabled)。*
