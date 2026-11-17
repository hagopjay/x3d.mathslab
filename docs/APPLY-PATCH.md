# Run or apply Insight Expeditions

The complete ZIP contains the eighteen-lesson source tree and vendored X_ITE.
Unzip it, enter `X3D-MathLab-Insight-Expeditions/`, then run:

```sh
python3 run_mathlab.py --open
```

On Windows, `python run_mathlab.py --open` or `run.bat` starts the same lab.
WSL/Linux can use `bash run.sh`. Open http://127.0.0.1:8850/.
No dependencies are needed for the local interactive lab. The **Insight atlas**
button opens six worked investigations. Try “A rare tag surprises”, “Erase one
direction”, or “Ripples gone, broad shape remains”.

## Choose the correct patch

| Patch | Apply to |
|---|---|
| `X3D-MathLab-Insight-Expeditions.patch` | The previous twelve-lesson Aha Atlas edition, after applying its patch |
| `X3D-MathLab-Insight-Complete.patch` | Clean upstream commit `24c9bbd8ad92e477c56f239476cd3dff7c05ecb2` |

The incremental patch's exact prior content is Git tree
`9b653b4070c69181bf6c59a0211a7fa5db34d550`, captured from the delivered v0.2.0
source. It is a content identity, not a remote commit to check out. The
cumulative patch includes both expansions from the public upstream baseline.
Choose one applicable patch and first check it:

```sh
git switch -c feat/insight-expeditions
git apply --check /path/to/selected.patch
git apply /path/to/selected.patch
```

Both patches are checked on clean copies of their named baselines. If your
checkout contains other changes, inspect and reconcile them before applying.
The upstream repository is https://github.com/hagopjay/x3d.mathslab.

For optional development verification, install MCP, SciPy, lxml and jsonschema
in a development environment, ensure Node is available, then run:

```sh
python3 tools/check_release.py
```

Matplotlib is needed only to reproduce `docs/Insight-Preview.png` with
`python3 tools/render_expedition_preview.py`. Native browser continuation is
explained in `EXPEDITIONS-VALIDATION.md`. This delivery does not publish to
GitHub or Pages.
