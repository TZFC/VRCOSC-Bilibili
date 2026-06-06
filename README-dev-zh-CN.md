# VRCOSC-Bilibili (v3) - 开发者指南

[English (User Guide)](README.md) | [中文 (用户指南)](README-zh-CN.md) | [English (Developer Guide)](README-dev.md) | [中文 (开发者指南)](README-dev-zh-CN.md)

欢迎阅读 **VRCOSC-Bilibili** 的开发者指南。本文档概述了技术架构、设计模式以及贡献或修改代码库的说明。

## 🏗️ 架构概述

v3 版本的重写采用了基于 **Python FastAPI 后端** 和 **React + Vite 前端** 的现代、轻量且强大的架构。它通过 PyInstaller 打包成一个独立的 Windows 可执行文件。

### 1. 后端 (FastAPI + SQLModel)
- **API 与 WebSockets (main.py)**: 后端的入口点。它承载了用于 UI 配置的 REST 接口以及用于实时日志流的 WebSocket 接口。它利用 FastAPI 的 @asynccontextmanager async def lifespan(app) 来确保所有后台任务（OSC 连接、Bilibili 连接）在接受 API 请求之前正确启动，并在关闭时干净地终止。
- **数据库 (database.py)**: 使用 SQLModel 与 SQLite (rcosc_bilibili_v3.db) 提供防崩溃的持久化存储。包含 AppConfig、Rule 和 AuthProfile 的数据表结构。
- **身份验证 (uth/bili_auth.py)**: 使用 rowser-cookie3 跨多个浏览器提取用户的登录会话，实现无缝登录体验，无需手动获取 token。
- **规则引擎 (engine/rule_engine.py)**: 根据数据库中的规则评估传入的 B站事件，并决定触发哪些 OSC 消息。
- **Bilibili 客户端 (ili_client.py)**: 使用 ilibili-api-python 库连接到 B 站直播弹幕 WebSocket。它将原始事件（弹幕、礼物、醒目留言等）转换为结构化的内部事件发送给规则引擎。
- **OSC 管理器 (engine/osc_manager.py)**: 封装 python-osc。
  - **单例客户端 (Singleton Client)**: 提前启动一个 OSC 发送客户端，避免了 v1/v2 中多个并发事件同时触发时产生多个客户端的竞态条件。
  - **OSC 服务端 (OSC Server)**: 运行一个异步 UDP 服务器监听 VRChat 参数的本地变化。通过对比 VRChat 的状态和内部记录的状态，实现 **双向同步 (Bi-Directional Sync)** 逻辑（Overwrite 覆盖 或 Respect 尊重）。

### 2. 前端 (React + Vite + Tailwind)
- 前端位于 rontend/ 目录中。它是一个使用 React 构建并使用 Tailwind CSS 设置样式的单页应用程序 (SPA)。
- **Unity 风格 UI**: UI 分为三个主要组件：Sidebar (层级/Hierarchy)、Inspector (检查器) 和 Console (控制台)，在视觉与交互上贴近 Unity 编辑器，让 VRChat 模型作者感到熟悉。
- **构建集成**: 使用 uild.py 构建项目时，React 应用将被编译，静态的 dist/ 文件夹会被复制到后端目录中。FastAPI 会挂载此静态目录，直接从 Python 后端提供 UI 服务。

### 3. 启动器 (Start.bat & Launcher.ps1)
- 对于终端用户来说，命令行被完全隐藏。Start.bat 调用 VBScript 隐藏终端，然后触发 Launcher.ps1。
- Launcher.ps1 构建了一个轻量级的 WinForms UI 来显示加载进度，自动管理 Python 的 .venv 虚拟环境，自动安装依赖项，然后静默执行 main.py。

## 🛠️ 开发环境设置

1. **前置条件**: 需安装 Python 3.10+ 和 Node.js。
2. **后端设置**:
   ``bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python backend/main.py
   ``
3. **前端设置**:
   ``bash
   cd frontend
   npm install
   npm run dev
   ``
   *注意：在开发期间，前端运行在 localhost:5173，而后端运行在 localhost:8000。前端使用 Axios 的全局默认设置将请求指向 8000 端口。*

## 📦 打包发布版本

打包独立的 .exe 程序：
``bash
.venv\Scripts\activate
python build.py
``
此脚本将执行：
1. 编译 React 前端。
2. 将构建好的资源移动到 ackend/static/。
3. 调用 PyInstaller 将后端和静态资源打包到 ackend/dist/VRCOSC-Bilibili/VRCOSC-Bilibili.exe 中。
