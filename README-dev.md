# VRCOSC-Bilibili (v3) - Developer Guide

[English (User Guide)](README.md) | [中文 (用户指南)](README-zh-CN.md) | [English (Developer Guide)](README-dev.md) | [中文 (开发者指南)](README-dev-zh-CN.md)

Welcome to the Developer Guide for **VRCOSC-Bilibili**. This document outlines the technical architecture, design patterns, and instructions for contributing or modifying the codebase.

## 🏗️ Architecture Overview

The v3 rewrite uses a modern, lightweight, and robust architecture based on a **Python FastAPI Backend** and a **React + Vite Frontend**. It is bundled into a standalone Windows executable via PyInstaller.

### 1. Backend (FastAPI + SQLModel)
- **API & WebSockets (main.py)**: The entry point for the backend. It hosts REST endpoints for UI configuration and a WebSocket endpoint for real-time log streaming. It utilizes FastAPI's @asynccontextmanager async def lifespan(app) to ensure all background tasks (OSC connections, Bilibili connections) are properly started before accepting API requests and cleanly terminated upon shutdown.
- **Database (database.py)**: Uses SQLModel with SQLite (`vrcosc_bilibili_v3.db`) for crash-resistant persistence. Contains schemas for AppConfig, Rule, and AuthProfile. It implements automated schema migration (`migrate_db()`) to alter SQLite tables and safely inject missing configuration columns at startup without data loss.
- **Authentication (auth/bili_auth.py)**: Uses browser-cookie3 to extract user login sessions across multiple browsers, enabling a seamless login experience without manual token fetching.
- **Rule Engine (engine/rule_engine.py)**: Evaluates incoming Bilibili events against database rules and determines what OSC messages to fire. It also handles dynamic camera command keyword parsing (retrieved from `AppConfig` in DB) and projects local step translations (6 Degrees of Freedom) into world-space coordinates via ZXY Euler rotation matrices relative to the current tracked camera viewpoint.
- **Bilibili Client (bili_client.py)**: Connects to the Bilibili Live Websocket using the bilibili-api-python library. It translates raw events (Danmaku, Gift, SuperChat) into structured internal events sent to the Rule Engine.
- **OSC Manager (engine/osc_manager.py)**: Wraps python-osc. 
  - **Singleton Client**: Starts an OSC client upfront, avoiding race conditions that existed in v1/v2 where multiple simultaneous events spawned multiple clients.
  - **OSC Server**: Runs an async UDP server to listen for VRChat parameters changing locally. It implements the **Bi-Directional Sync** logic (Overwrite vs Respect) by comparing VRChat's state to the internal tracked state.

### 2. Frontend (React + Vite + Tailwind)
- The frontend is located in the rontend/ directory. It is a single-page application built with React and styled using Tailwind CSS.
- **Unity-Style UI**: The UI is split into three main components: Sidebar (Hierarchy), Inspector, and Console, closely resembling the Unity editor to feel familiar to VRChat avatar creators.
- **Build Integration**: When building the project using uild.py, the React app is compiled and the static dist/ folder is copied into the backend. FastAPI mounts this static directory, serving the UI directly from the Python backend.

### 3. Launcher (Start.bat & Launcher.ps1)
- For end-users, command lines are hidden. Start.bat invokes a VBScript to hide the terminal, which then triggers Launcher.ps1.
- Launcher.ps1 builds a lightweight WinForms UI indicating loading progress, manages the Python .venv, installs requirements automatically, and then silently executes main.py.

## 🛠️ Development Setup

1. **Prerequisites**: Python 3.10+ and Node.js.
2. **Backend Setup**:
   ``bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python backend/main.py
   ``
3. **Frontend Setup**:
   ``bash
   cd frontend
   npm install
   npm run dev
   ``
   *Note: During development, the frontend runs on localhost:5173 while the backend runs on localhost:8000. The frontend uses Axios defaults to target port 8000.*

## 📦 Building for Production

To build the standalone .exe:
``bash
.venv\Scripts\activate
python build.py
``
This script will:
1. Compile the React frontend.
2. Move the built assets into ackend/static/.
3. Invoke PyInstaller to bundle the backend and static assets into ackend/dist/VRCOSC-Bilibili/VRCOSC-Bilibili.exe.
