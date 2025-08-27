# VRCOSC‑Bilibili

通过 OSC（Open Sound Control）协议将 B 站直播事件桥接到 **VRChat**。
当有人进入、发言、送礼或触发其他直播间事件时，程序可以：

- 在 VRChat 聊天框显示消息
- 更新头像参数（用于动画、表情等）
- 管理自定义参数的累积与衰减

---

## 📦 面向非技术用户

按照以下步骤快速运行本程序。

### 1. 环境需求
- 运行 **Windows / macOS / Linux** 的电脑
- 已安装 **Python 3.11+**
- 已启用 **OSC** 的 **VRChat**（设置 → OSC）
- 使用 **Firefox** 登录的 **Bilibili** 账号（用于获取 Cookie）

### 2. 下载并解压
1. 前往 [GitHub Releases](https://github.com/TZFC/VRCOSC-Bilibili/releases/latest) 下载最新版本。
2. 将压缩包解压到任意文件夹。

### 3. 配置
1. 用文本编辑器打开 `Config.toml`。
2. 设置你的 Bilibili `room_id`。
3. （可选）调整哪些事件会触发聊天消息或头像参数。
4. 保存文件。

### 4. 安装依赖
在项目文件夹打开终端并运行：

```bash
python -m venv .venv
# 激活虚拟环境
# - Windows: .venv\Scripts\activate
# - macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 5. 运行
根据你的系统选择对应脚本：

- **Windows：** 双击 `RUNME.bat`
- **macOS：** 双击 `Mac_RUNME.command`
- **Linux：** 运行 `sh Unix_RUNME.sh`

程序将连接到指定的 B 站直播间。
请在直播时保持窗口打开。

### 6. 停止
在终端按 `Ctrl+C`，或直接关闭窗口。

---

## 🔧 面向开发者的技术说明

### 核心架构
```
Bilibili LiveDanmaku → Event Handlers → OSC Queues → Consumers → VRChat OSC
```

1. **配置**
   - `Config.toml` 由 `app/Utils/config_loader.py` 解析。
   - 用于验证房间号、事件级别、参数列表等。

2. **B 站连接**
   - `app/bili_event_dispatch.py` 使用 `bilibili_api` 中的 `LiveDanmaku`。
   - 事件回调（`@live_danmaku.on(...)`）根据 `CONFIG["events"]` 分发至各处理器。

3. **事件处理器**
   - 位于 `app/EventHandler/`。
   - 每个处理器可：
     - 将消息加入聊天队列
     - 推送通用参数更新
     - 累积动画计数
     - 修改并衰减自定义参数

4. **OSC 队列 / 累加器**
   - 定义于 `app/osc_queue.py`。
   - 队列：`chatbox_queue`、`general_gift_queue`
   - 累加器：`animation_counts`、`set_parameter_value`

5. **消费者**
   - 在 `main.py` 中启动持续的异步循环：
     - `chatbox_loop()`（聊天消息）
     - `general_loop()`（`event_id`/`event_num` 更新）
     - `animation_loop()`（批量动画参数）
     - `parameter_decay_loop()`（自定义参数衰减）

6. **OSC 客户端**
   - `app/osc/vrc_osc.py` 封装 `python-osc` 向 VRChat 发送消息。
   - `app/osc/vrc_osc_singleton_client.py` 使用 `CONFIG["LAN_ip"]` 与 `["LAN_port"]` 维持单例连接。

7. **凭据获取**
   - `app/Utils/browser_credential.py` 从 Firefox 读取 B 站 Cookie。
   - 若获取成功返回 `Credential` 对象，否则匿名连接。

### 数据流示例
1. 观众送礼 → 触发 `SEND_GIFT` 事件。
2. `gift_handler.py` 将 `(event_id, event_num)` 放入 `general_gift_queue`。
3. `general_loop()` 发送 OSC 参数 `/avatar/parameters/event_id` 与 `/avatar/parameters/event_num`。
4. 头像 FX 层根据参数做出反应。

### 开发提示
- 使用 `asyncio.TaskGroup`（Python 3.11+）。
- 如需扩展事件处理，可新增处理函数并在 `bili_event_dispatch.py` 中映射。
- 当前缺少测试，欢迎贡献。
- 许可证为 **GNU GPLv3**。

---

## 📝 许可证
遵循 **GNU General Public License v3.0 or later**。详见 [LICENSE](LICENSE)。
