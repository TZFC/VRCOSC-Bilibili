# VRCOSC-Bilibili (v3)

Welcome to **VRCOSC-Bilibili**, the easiest way to bridge Bilibili live streams with VRChat! 
This application seamlessly connects your Bilibili live room to VRChat's OSC system, allowing you to trigger avatar animations, move your character, control your camera, or type in the chatbox using livestream events like Danmaku, Gifts, or Super Chats.

## 🚀 Getting Started

1. **Launch the App**
   Simply double-click `Start.bat`. A loading screen will appear to automatically set up the Python environment and download dependencies (this may take a minute on your very first run). Once finished, a web browser will automatically open with the Unity-style user interface. You will never need to touch the command line!

2. **Authenticate with Bilibili**
   In the main setup screen, click **Auto-Scan Browsers for Login**. The app will securely search your installed browsers (Chrome, Firefox, Edge, etc.) for an active Bilibili login and present your profile card. Alternatively, you can use the manual fallback if you're an advanced user.

3. **Configure Connection**
   Enter your **Bilibili Room ID**. The OSC ports are already set up for default VRChat usage (9000 for sending to VRChat, 9001 for receiving), so you usually won't need to change them. Click **Save & Apply Config**.

4. **Create Your First Rule!**
   Click the + button in the left **Hierarchy** panel to add a new rule.

## 🎛️ How to Make Rules (Unity-Style Inspector)

When you select a rule, the right panel (the **Inspector**) lets you configure it:

### Triggers (The 'If')
Choose what Bilibili event triggers the rule:
- **Event Type:** Pick between Danmaku, Gift, Super Chat (SC), Guard, or Enter (when someone joins the stream).
- **Keyword:** Want to trigger an animation when someone types "jump"? Type "jump" here (works for Danmaku).
- **Min Value:** For Gifts or Super Chats, you can specify the minimum price (in RMB) needed to trigger the action.

### Action (The 'Then')
Choose what happens in VRChat:
- **Endpoint:** The VRChat OSC address to hit. Examples:
  - /avatar/parameters/Dance (Triggers an avatar parameter)
  - /chatbox/input (Types in the chatbox)
  - /input/Jump (Makes you jump)
  - /usercamera/Capture (Takes a picture with your camera)
- **Action Type:** Set (force a specific value), Toggle (flip between true/false), or Add (increase a number).
- **Value:** The value to send (e.g., 	rue, alse, 1.5, or text for the chatbox).

### Sync Mode (Bi-Directional Sync)
VRChat avatars are interactive. If a user manually changes an Avatar Parameter (e.g., via their Action Menu in VR):
- **Overwrite:** The app will be stubborn and immediately overwrite the user's manual change back to the rule's state.
- **Respect:** The app will listen to VRChat and accept the user's manual change, staying in sync.

## 📦 Sharing Configs

Want to share your complex avatar setup with friends? 
Use the **Exp** (Export) button in the Hierarchy to download your rules as a .json file, and the **Imp** (Import) button to load someone else's!

---
*Note: Make sure OSC is enabled in your VRChat Action Menu (Action Menu > Options > OSC > Enabled).*
