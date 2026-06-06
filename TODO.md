# TODO / Next Steps

This document outlines the final polishing steps and information you need to provide before shipping the v3 rewrite of **VRCOSC-Bilibili**.

## 1. Application Icon
To give the standalone .exe a professional look, you need to provide an icon file.

- **Action:** Create an .ico file and place it at <path_to_icon>/<icon_name>.ico (e.g., ackend/assets/icon.ico).
- **Format Requirement:** PyInstaller on Windows requires the icon to be strictly in .ico format (not .png or .svg). You can use free online converters to change your logo into an .ico file.
- **Update Build Script:** Once you have the file, update line 11 in uild.py to include the icon flag:
  \\\python
  "--icon", "assets/icon.ico",
  \\\

## 2. GitHub Release Strategy
- **Action:** Since all launch scripts (Start.bat) were removed in favor of a single executable, ensure that when you create a GitHub Release, you *only* attach the pre-compiled VRCOSC-Bilibili.exe file. Do not instruct users to download the source code zip.

## 3. UI/UX Final Polish
- **Action:** Confirm the dark-mode aesthetic for the React frontend. Currently, it uses a generic Unity-like dark gray palette. If you have specific Bilibili Pink/Blue branding colors you want integrated, provide the HEX codes.
- **Action:** Double-check the wording of the "Sync Mode" toggles. Are "Overwrite" and "Respect" intuitive enough for your Chinese audience, or would you prefer alternative phrasing in the UI?

## 4. Documentation Links
- **Action:** In both README.md and README-zh-CN.md, the download links currently point to https://github.com/TZFC/VRCOSC-Bilibili/releases. Confirm that TZFC is still the correct GitHub organization/user account.
