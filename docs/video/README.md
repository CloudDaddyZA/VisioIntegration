# Instruction Video Assets

Materials for producing a short instructional video covering the **Azure Visio AI**
Streamlit app and the **VS Code extension** (`@azureVisio`).

| File | Purpose |
|------|---------|
| [walkthrough.html](walkthrough.html) | A **self-playing, dependency-free** visual walkthrough (12 slides, ~80s). Open in any browser. Auto-advances; use ← → to navigate, Space to pause, **F** for fullscreen. |
| [walkthrough-script.md](walkthrough-script.md) | A **shot-by-shot recording script** with narration, on-screen actions, and timings (~3 min) for capturing the live UI. |

## Turn it into an MP4 (two options)

### Option A — Record the self-playing HTML (fastest, no live app needed)
1. Open [walkthrough.html](walkthrough.html) in your browser and press **F** for fullscreen.
2. Start a screen recorder (Windows: `Win+Alt+R` for Game Bar, or [OBS Studio](https://obsproject.com)).
3. Press **Space** to restart at slide 1 if needed; let it play through (~80s).
4. Optionally record narration from [walkthrough-script.md](walkthrough-script.md) and overlay it.

### Option B — Record the live product (most authentic)
1. Start the app: `streamlit run app/streamlit_app.py`.
2. Open VS Code with the extension installed for the second segment.
3. Follow [walkthrough-script.md](walkthrough-script.md) shot by shot in OBS / Clipchamp.
4. Capture at 1080p / 30fps, 100% display scaling for crisp icons.

> Tip: Collapse the **AI Configuration** panel before recording so no API keys/tokens appear on screen.
