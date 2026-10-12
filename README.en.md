<div align="center">

# 📸 PhotoAI Studio

**Tether your camera over USB and auto-edit photos with AI — a mobile-style photo-editing UI, touch-friendly**

![Version](https://img.shields.io/badge/version-alpha--003-orange)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt&logoColor=white)
![AI](https://img.shields.io/badge/AI-Gemini-8E44AD?logo=google)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-red)

[**⬇️ Download the latest installer**](../../releases/latest) · [Report an issue](../../issues) · [Overview](#-overview)

[🇻🇳 Tiếng Việt](README.md) | **🇬🇧 English**

</div>

---

## 📖 Overview

**PhotoAI Studio** is a Windows desktop app that shortens the shoot-and-edit workflow for
photographers: connect your camera via USB, capture directly from the app, pick a photo and a
style, and let AI edit it automatically in that style — instead of manually retouching every
photo in Lightroom/Photoshop. The UI is inspired by popular mobile photo-editing apps (in the
style of Xingtu/Meitu): a bottom navigation bar, a carousel of style chips, a before/after
compare slider, and buttons/tap targets large enough to work well on touchscreens too.

> ⚠️ **Currently in `alpha-003`** — the core features work but haven't been tested widely
> across camera models yet. Feedback and issues are always welcome.
>
> Starting with `alpha-003`, several features are inspired by the mobile photo-editing app
> **醒图 (XingTu/retouchpics.com)**: one-tap tools, AI object removal, custom presets, and
> batch processing — details below.

## ✨ Features

**Library** 🖼️ — newly captured photos appear automatically; pick one with a single tap. Switch
to **multi-select mode** to pick several photos at once and batch-process them.

**AI Edit** ✨
- 📷 USB tethered capture via [digiCamControl](https://www.digicamcontrol.com) (most Canon/Nikon/Sony/Pentax cameras)
- 🎨 A carousel of 6 built-in styles:

  | Style | Description |
  |---|---|
  | Portrait | Natural skin smoothing, eyes stand out, soft background blur |
  | Outdoor | Natural light/shadow balance, natural outdoor colors |
  | Landscape | Increased dynamic range, sky and detail stand out |
  | People / Candid | Consistent skin tones, even lighting for multiple people |
  | Graduation | Bright, consistent tones, smiles stand out |
  | 🧹 Remove Object | Removes distracting people/objects from the background with natural AI inpainting |
- ⭐ **Custom presets** — save a style + intensity + note combo as a named preset that shows up
  in the carousel for quick reuse (right-click / long-press to delete)
- 🧵 **Batch processing** — select multiple photos in the Library and apply one style/preset to
  all of them, with a progress bar and automatic saving
- 🎚️ An **effect intensity** slider (0–100%) to blend the AI result with the original
- 🖱️ A **before/after compare slider** right on the photo (drag to reveal the AI result)
- 🤖 Generative AI editing via the [Gemini API](https://ai.google.dev) (`gemini-2.5-flash-image`), with an optional custom note

**Manual Edit** 🎚️ — brightness, contrast, saturation, sharpness (live preview) + 90° rotation,
plus 2 **local one-tap tools** (no AI needed, instant): 🌈 White Balance (gray-world) and
✨ Smart Auto (brightness/color/contrast).

**Settings** ⚙️ — switch AI model, digiCamControl path, output folders, and app language (Vietnamese/English).

## 🏗️ Architecture

```
photoai_app/
├── main.py                 # App entry point
├── config.py                # Configuration management (API key, paths, version)
├── requirements.txt
├── installer.iss            # Inno Setup script (auto-downloads & installs digiCamControl)
├── assets/icon.ico           # App icon
├── i18n.py                   # Lightweight VI/EN translation system
├── camera/
│   └── digicam.py            # Wrapper around digiCamControl (CameraControlCmd.exe)
├── ai/
│   ├── styles.py              # 6 styles + bilingual prompts for Gemini
│   ├── gemini_editor.py       # Calls the Gemini API to edit photos
│   ├── manual_edit.py         # Manual edit (brightness/contrast/saturation/sharpness/rotate) + AI blend
│   └── one_tap.py             # Local one-tap tools: white balance, smart auto adjust (no AI needed)
└── ui/
    ├── theme.py                # Color palette & QSS (dark theme, pink/purple accent)
    ├── widgets.py               # Bottom nav bar, style chips, compare slider
    ├── pages.py                 # 4 pages: Library / AI Edit / Manual / Settings
    └── main_window.py           # Main window, coordinates the pages
```

| Component | Technology |
|---|---|
| UI | [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python) |
| Camera tethering | [digiCamControl](https://www.digicamcontrol.com) (open source) |
| AI photo editing | [Google Gemini API](https://ai.google.dev) (`google-genai`) |
| Image processing | [Pillow](https://python-pillow.org) |
| Packaging | PyInstaller + Inno Setup, built automatically via GitHub Actions |

## ⬇️ Quick install (recommended)

1. Go to [**Releases**](../../releases/latest) and download `PhotoAIStudio-Setup-*.exe`.
2. Run it, leave the "Automatically download and install digiCamControl" option checked →
   the installer downloads and installs digiCamControl for you, with no extra steps needed.
3. Open **PhotoAI Studio** → go to **Settings** and enter your Gemini API key (get a free one
   at [Google AI Studio](https://ai.google.dev)) — this is the only step you need to do
   yourself, since the API key is private/billed to your own account and can't be bundled.

## 📋 System requirements

- Windows 10/11
- A Gemini API key ([get one free at Google AI Studio](https://ai.google.dev))
- A camera supported by digiCamControl ([camera list](https://www.digicamcontrol.com/cameras))

## 🧑‍💻 Run from source (for developers)

```bash
git clone https://github.com/ngiangbao/photoai-studio.git
cd photoai-studio
pip install -r requirements.txt
python main.py
```

> ⚠️ Don't keep digiCamControl's main window open while using this app —
> `CameraControlCmd.exe` only works while the digiCamControl GUI is *not* running.

## 🖱️ Usage

1. Plug in your camera via USB and turn it on.
2. **Library** tab → **"New Capture"** → select the photo you just took.
3. **AI Edit** tab → pick a style from the carousel → adjust intensity if you like →
   **"Apply AI"** → drag the compare slider to see before/after → **"Save Photo"**.
4. Or the **Manual** tab → tap **"White Balance"** / **"Smart Auto"** for a quick fix, then
   fine-tune with the sliders → **"Save Photo"**.
5. Want to reuse a favorite combo? Pick a style + intensity + note on the **AI Edit** tab →
   **"Save as Preset"** → give it a name. It shows up in the carousel; right-click to delete it.
6. Got several photos that need the same style? On the **Library** tab, tap **"Select
   Multiple"** → check the photos → **"Batch Process"** (uses the style/preset currently
   selected on the AI Edit tab).
7. Change the app's language anytime in **Settings** → **Language** (takes effect immediately,
   no restart needed).

## 📦 Build the installer from source

Whenever a `v*` tag is pushed to GitHub, the **Build & Release Windows Installer** workflow
(`.github/workflows/release.yml`) automatically: builds with PyInstaller → packages with Inno
Setup → publishes `PhotoAIStudio-Setup-*.exe` to **Releases**. To build manually:

```bash
pip install pyinstaller
pyinstaller --name "PhotoAI Studio" --windowed --onedir --icon assets/icon.ico main.py
# Then open installer.iss in Inno Setup and Build
```

## 📱 Android version

In progress under [`android/`](android/) — built with Kotlin + Jetpack Compose, sharing the
same 5 styles and Gemini-calling logic as the Windows app, but capturing with the phone's own
camera (via CameraX) instead of digiCamControl (which only runs on Windows). See
[`android/README.md`](android/README.md) for architecture details and how to try it.

## 🗺️ Roadmap

- [ ] Direct tethering via vendor SDKs (Canon EDSDK, Nikon SDK) in addition to digiCamControl
- [x] Batch processing of multiple photos at once
- [x] Custom/saveable user-defined styles (presets)
- [ ] Landmark-based face reshape/lift — needs a face-landmark library; face effects currently
      go through generative AI (the Portrait style) rather than a precise mesh warp
- [ ] A stackable library of 1,200+ filters, matching the original 醒图 app
- [ ] A dedicated SVG icon set instead of emoji, with dark/light theme switching
- [ ] Android: import from gallery, USB-OTG tethering, signed release builds (see its own roadmap in `android/README.md`)

## 🤝 Contributing

Contributions, bug reports and feature requests are all welcome — please open an
[Issue](../../issues) or send a Pull Request.

## ☕ Support the project

If you find **PhotoAI Studio** useful, you're welcome to buy me a coffee to help keep the
project going 🙏

<div align="center">
<table>
<tr>
<td align="center" width="50%">
<b>MoMo</b><br/><br/>
<img src="assets/donate-momo.jpg" width="220" alt="MoMo QR code to support PhotoAI Studio"/>
</td>
<td align="center" width="50%">
<b>Bank (VietQR)</b><br/><br/>
<img src="assets/donate-bank.jpg" width="220" alt="VietQR bank QR code to support PhotoAI Studio"/>
</td>
</tr>
</table>

Nguyễn Giang Bảo

</div>

## 📄 License

Released under the [MIT](LICENSE) license.

---

<div align="center">

Made with ☕ by [ngiangbao](https://github.com/ngiangbao)

</div>
