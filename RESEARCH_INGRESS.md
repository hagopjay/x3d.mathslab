# Research Ingress Guide — manim-mcp
## How to feed external knowledge into this animation system

This document explains how to pipe questions, mathematical concepts, and
external research from Wolfram Alpha, LLM agents, and other sources into
the manim-mcp rendering pipeline.

---

## Architecture Overview

```
External Sources                Claude Code Session (this project)
────────────────                ──────────────────────────────────
Wolfram Alpha API    ──┐
GPT-4 / Gemini       ──┤──► Prompt with math concept ──► Claude writes Manim ──► render_manim ──► MP4
Perplexity           ──┤
Papers / Wikipedia   ──┘
```

---

## Method 1: Wolfram Alpha (direct API)

### Setup
```bash
# Install wolframalpha Python client
.venv/bin/pip install wolframalpha

# Get a free App ID at: https://developer.wolframalpha.com/
export WOLFRAM_APP_ID="YOUR-APP-ID-HERE"
```

### Query pattern
```python
import wolframalpha, os
client = wolframalpha.Client(os.environ["WOLFRAM_APP_ID"])

# Ask Wolfram a mathematical question
res = client.query("plot sin(x) + sin(2x) + sin(3x)")

# Extract the plaintext result
for pod in res.pods:
    print(pod.title, "→", pod.text)
```

### Then paste the result into Claude:
```
"Wolfram says the Fourier series of a square wave is:
 (4/π) * Σ sin((2k-1)x)/(2k-1)

Can you animate this as a Manim scene showing the first 7 terms?"
```

---

## Method 2: Ask an LLM agent for the math, then animate

### Template prompt for GPT-4 / Claude API / Gemini:

```
You are a math explainer. Describe [CONCEPT] with:
1. The key equation (in plain text, no LaTeX)
2. What changes over time (for animation)
3. What the visual should show at t=0, t=middle, t=end
4. What text labels are most important
5. Any surprising or counterintuitive facts to highlight

Be specific and numerical. Output format: JSON.
```

Then take the JSON output and say to Claude Code:
```
"Here's the math description from GPT-4:
 [paste JSON]

Please write a Manim scene that animates this. Use medium quality.
Follow the existing patterns in src/manim_mcp/server.py."
```

---

## Method 3: Perplexity / Web Research → Animation

Use the `/fetch` skill in Claude Code to pull live web content:
```
/fetch https://en.wikipedia.org/wiki/Riemann_hypothesis
```

Then:
```
"Based on what we just fetched about the Riemann Hypothesis,
animate the critical strip (0 < Re(s) < 1) on the complex plane
and show the first few non-trivial zeros."
```

---

## Method 4: Python script as research preprocessor

Create a script that queries multiple sources and outputs a Manim-ready prompt:

```python
# research_to_manim.py
import requests, json

def wolfram_query(question, app_id):
    url = "http://api.wolframalpha.com/v2/query"
    params = {"input": question, "format": "plaintext",
              "output": "JSON", "appid": app_id}
    r = requests.get(url, params=params).json()
    pods = r.get("queryresult", {}).get("pods", [])
    return {p["title"]: p.get("subpods",[{}])[0].get("plaintext","")
            for p in pods}

def build_animation_prompt(concept, wolfram_result):
    return f"""
Animate this mathematical concept as a Manim scene:

CONCEPT: {concept}

WOLFRAM DATA:
{json.dumps(wolfram_result, indent=2)}

REQUIREMENTS:
- Scene class name: {concept.replace(' ','').replace('-','')}Scene
- Background: #08081a
- No MathTex (LaTeX not installed) — use Text() only
- Quality: medium for draft, high for final
- Duration: 30-60 seconds
- Show the key equation as Text at bottom
- Animate the core idea visually with Axes + plot

Please write the complete Manim code.
"""

if __name__ == "__main__":
    import os
    APP_ID = os.environ.get("WOLFRAM_APP_ID", "DEMO")
    concept = "Gaussian distribution"
    data = wolfram_query(f"formula for {concept}", APP_ID)
    print(build_animation_prompt(concept, data))
```

Run it, then paste the output into a Claude Code session in this directory.

---

## Method 5: Batch animation from a research list

Create a file `animation_queue.json`:
```json
[
  {
    "concept": "Gaussian Distribution",
    "equation": "f(x) = (1/sqrt(2*pi*sigma^2)) * exp(-(x-mu)^2 / (2*sigma^2))",
    "visual": "Bell curve with mu and sigma sliders",
    "duration": 40
  },
  {
    "concept": "Mandelbrot Set",
    "equation": "z_{n+1} = z_n^2 + c",
    "visual": "Complex plane iteration coloring",
    "duration": 60
  },
  {
    "concept": "Lorenz Attractor",
    "equation": "dx/dt = sigma*(y-x), dy/dt = x*(rho-z)-y, dz/dt = x*y - beta*z",
    "visual": "3D trajectory ThreeDScene",
    "duration": 60
  }
]
```

Then tell Claude Code:
```
"Read animation_queue.json and render all three scenes as a batch
using render_manim_batch. Use medium quality for speed."
```

---

## Method 6: MCP-to-MCP chaining (advanced)

If you have Wolfram's official MCP server or a custom research MCP, you can
chain them with manim-mcp in a single Claude session:

1. Add the research MCP to `.mcp.json`:
```json
{
  "mcpServers": {
    "manim": { ... },
    "wolfram": {
      "command": "uvx",
      "args": ["wolfram-mcp"],
      "env": { "WOLFRAM_APP_ID": "YOUR-ID" }
    }
  }
}
```

2. Claude will then have BOTH tool sets. You can say:
```
"Query Wolfram for the formula of [X], then animate it with Manim."
```
Claude will call `wolfram.query(...)` → get result → call `manim.render_manim(...)`.

---

## Prompting Tips for Best Results

### DO:
- Be specific about what should MOVE vs what should be STATIC
- Specify time durations ("spend 5 seconds on this, then transition")
- Name the scene class explicitly
- Say "use Text() not MathTex" until LaTeX is installed
- Ask for `validate_manim_code` first, then render

### DON'T:
- Ask for MathTex/Tex without LaTeX installed (install: `brew install --cask basictex`)
- Request 3D scenes without mentioning `ThreeDScene` + `renderer="opengl"`
- Ask for images/audio in the scene without providing the file paths

### Magic phrases that work well:
- "Animate this concept in the style of 3Blue1Brown"
- "Show this building up from first principles"
- "Start simple, reveal complexity gradually"
- "Add a live counter/tracker that updates as the animation plays"
- "Use always_redraw for anything that changes over time"

---

## Current System Capabilities

| Capability | Status |
|---|---|
| Manim 0.20.0 | ✅ Installed |
| ffmpeg | ✅ Installed |
| LaTeX / MathTex | ❌ Not installed (`brew install --cask basictex`) |
| 3D rendering (OpenGL) | ⚠️ Available but slow without GPU |
| Audio in animations | ⚠️ Needs audio file path |
| Max render timeout | 900s (15 min) |
| Output location | `~/.manim-mcp/renders/` |

---

## Quick Reference: Useful Manim Patterns

```python
# Live-updating value
tracker = ValueTracker(0)
label = always_redraw(lambda:
    Text(f"x = {tracker.get_value():.2f}", color=GOLD).to_corner(DR))
self.play(tracker.animate.set_value(10), run_time=3)

# Plot a function
axes = Axes(x_range=[-5,5,1], y_range=[-2,2,1],
            axis_config={"include_numbers": False})
curve = axes.plot(np.sin, color=YELLOW, stroke_width=3)

# Zoom in/out (requires MovingCameraScene)
self.play(self.camera.frame.animate.scale(0.5), run_time=2)

# Color gradient on text
text = Text("Hello").set_color_by_gradient(BLUE, PURPLE, GOLD)

# Riemann rectangles (built-in)
rects = axes.get_riemann_rectangles(curve, x_range=[0,3], dx=0.5)

# Area under curve (built-in)
area = axes.get_area(curve, x_range=[0, PI], color=[BLUE, GREEN])
```
