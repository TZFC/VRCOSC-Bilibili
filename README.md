# VRCOSC‑Bilibili

For a Chinese translation, see [README-cn.md](README-cn.md).

Bridge Bilibili livestream events to **VRChat** through the OSC (Open Sound Control) protocol.
When someone joins, chats, sends gifts, or triggers other events in your Bilibili room, the application can:

- Display messages in your VRChat chatbox
- Update avatar parameters (for animations, blend shapes, etc.)
- Accumulate and decay custom parameters over time

---

## 📦 For non‑technical users

Follow these steps to get the application running with minimal setup.

### 1. Requirements
- **Windows / macOS / Linux** computer
- **Python 3.11+** installed
- **VRChat** running with **OSC** enabled (`Settings → OSC`)
- A **Bilibili** account logged into **Firefox** (cookies are used to authenticate)

### 2. Download and extract
1. Grab the latest release from  
   [GitHub Releases](https://github.com/TZFC/VRCOSC-Bilibili/releases/latest).
2. Unzip the archive to any folder.

### 3. Configure
1. Open `Config.toml` in a text editor.
2. Set your Bilibili `room_id`.
3. (Optional) Adjust which events trigger chat messages or avatar parameters.
4. Save the file.

### 4. Install dependencies
Open a terminal/command prompt in the project folder and run:

```bash
python -m venv .venv
# Activate the environment
# - Windows: .venv\Scripts\activate
# - macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Run
Choose the script for your operating system:

- **Windows:** double‑click `RUNME.bat`
- **macOS:** double‑click `Mac_RUNME.command`
- **Linux:** run `sh Unix_RUNME.sh`

A console window appears and connects to the specified Bilibili room.  
Keep the window open while streaming.

### 6. Stop
Press `Ctrl+C` in the console, or close the window.

---

## 🔧 Technical design for developers

### Core architecture
```
Bilibili LiveDanmaku → Event Handlers → OSC Queues → Consumers → VRChat OSC
```

1. **Configuration**
   - `Config.toml` is parsed by `app/Utils/config_loader.py`.
   - Validates room ID, event levels, parameter lists, etc.

2. **Bilibili connection**
   - `app/bili_event_dispatch.py` uses `LiveDanmaku` from `bilibili_api`.
   - Event callbacks (`@live_danmaku.on(...)`) dispatch to handlers based on `CONFIG["events"]`.

3. **Event handlers**
   - Located in `app/EventHandler/`.
   - Each handler can:
     - Queue chatbox messages
     - Queue general parameter updates
     - Accumulate animation counts
     - Modify and decay custom parameters

4. **OSC queues / accumulators**
   - Defined in `app/osc_queue.py`.
   - Queues: `chatbox_queue`, `general_gift_queue`
   - Accumulators: `animation_counts`, `set_parameter_value`

5. **Consumers**
   - Continuous async loops started in `main.py`:
     - `chatbox_loop()` (chatbox messages)
     - `general_loop()` (general `event_id`/`event_num` updates)
     - `animation_loop()` (batch animation parameters)
     - `parameter_decay_loop()` (decaying custom parameters)

6. **OSC client**
   - `app/osc/vrc_osc.py` wraps `python-osc` to send messages to VRChat.
   - `app/osc/vrc_osc_singleton_client.py` ensures a single shared connection, using `CONFIG["LAN_ip"]` and `["LAN_port"]`.

7. **Credential retrieval**
   - `app/Utils/browser_credential.py` pulls Bilibili cookies from Firefox.
   - Returns a `Credential` object if available; otherwise connects anonymously.

### Key data flow example
1. Viewer sends gift → `SEND_GIFT` event.
2. `gift_handler.py` pushes `(event_id, event_num)` to `general_gift_queue`.
3. `general_loop()` sends OSC parameters `/avatar/parameters/event_id` and `/avatar/parameters/event_num`.
4. Avatar’s FX layer reacts accordingly.

### Development notes
- Uses `asyncio.TaskGroup` (Python 3.11+).
- Expand event handling by adding new handler functions and mapping them in `bili_event_dispatch.py`.
- Tests are currently absent; contributions welcome.
- Licensed under **GNU GPLv3**.

---

## 📝 License
GNU General Public License v3.0 or later. See [LICENSE](LICENSE) for details.
