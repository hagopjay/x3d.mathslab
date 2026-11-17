/* Static (GitHub Pages) transport for x3d.mathlab.
 *
 * The lab's kernels are pure standard-library Python. On a static host there is no
 * local server, so this adapter loads pinned Pyodide (CPython compiled to WebAssembly) and
 * runs the SAME mathlab/*.py files that the loopback server runs, behind the SAME request
 * gate (decode_request) and the SAME response budget. It evaluates enumerated lessons and
 * generates Manim *source text* only; it never imports Manim and never executes supplied code.
 */
(() => {
  const PYODIDE = "0.27.7";
  const BASE = "https://cdn.jsdelivr.net/pyodide/v" + PYODIDE + "/full/";
  // SHA-384 of pyodide.js@0.27.7 as served by jsDelivr; the browser refuses a changed file.
  const SRI = "sha384-90so5tCKvl0xs9agU29IMKlAVzhfzFX7QO//YxQkRhJG58bBZrFN+2ZTRB026X5X";
  const MODULES = ["__init__", "schema", "catalog", "kernel", "lessons_analysis", "lessons_structures", "lessons_inference", "lessons_science", "x3d", "manim_bridge", "cards", "server"];
  const root = new URL("../", document.baseURI);
  let booting = null;
  const status = (t) => window.dispatchEvent(new CustomEvent("mathlab-static", { detail: t }));

  function script(src, integrity) {
    return new Promise((ok, bad) => {
      const s = document.createElement("script");
      s.src = src;
      if (integrity) { s.integrity = integrity; }
      s.crossOrigin = "anonymous";
      s.onload = ok;
      s.onerror = () => bad(new Error("Could not load the in-browser Python runtime (" + src + ")."));
      document.head.append(s);
    });
  }

  const RUNNER = `
import json
from mathlab.server import decode_request, evaluate_request, canonical, MAX_RESPONSE, ModelSourceChanged
from mathlab.catalog import catalog
def run(path, raw):
    try:
        if path == "/api/catalog":
            return 200, canonical({"lessons": catalog()}).decode("utf-8")
        if path not in ("/api/evaluate", "/api/manim"):
            return 404, '{"error":"Unknown endpoint."}'
        request = decode_request(raw.encode("utf-8"))
        result = evaluate_request(request)
        if path == "/api/manim":
            from mathlab.manim_bridge import generate_manim
            result = {"source": generate_manim(result["sample"]), "identity": result["identity"],
                      "scope": "Baked scene source only. This endpoint does not execute Python or render a video."}
        data = canonical(result)
        if len(data) > MAX_RESPONSE:
            return 413, '{"error":"Generated response exceeds the declared 4 MiB budget."}'
        return 200, data.decode("utf-8")
    except ModelSourceChanged as e:
        return 409, json.dumps({"error": str(e)})
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as e:
        return 400, json.dumps({"error": str(e)[:300]})
`;

  async function boot() {
    status("Loading in-browser Python (Pyodide " + PYODIDE + ", ~10 MB, cached after first visit)");
    await script(BASE + "pyodide.js", SRI);
    const py = await window.loadPyodide({ indexURL: BASE });
    status("Preparing the mathematical experiments");
    py.FS.mkdirTree("/app/mathlab");
    for (const name of MODULES) {
      const r = await fetch(new URL("mathlab/" + name + ".py", root));
      if (!r.ok) throw new Error("Missing mathlab/" + name + ".py (" + r.status + ").");
      py.FS.writeFile("/app/mathlab/" + name + ".py", new Uint8Array(await r.arrayBuffer()));
    }
    py.runPython("import sys; sys.path.insert(0, '/app')");
    py.runPython(RUNNER);
    const run = py.globals.get("run");
    status("");
    return {
      version: py.runPython("import sys; sys.version.split()[0]"),
      call(path, raw) {
        const [code, text] = run(path, raw).toJs();
        return { code, text };
      },
    };
  }

  window.MathLabStatic = {
    pyodide: PYODIDE,
    async fetch(url, options = {}) {
      booting = booting || boot();
      let runtime;
      try { runtime = await booting; } catch (e) { booting = null; throw e; }
      // The runtime is single-threaded; calls are short and synchronous, so ordering is preserved.
      const path = new URL(url, location.href).pathname.replace(/^.*?(\/api\/)/, "/api/");
      const { code, text } = runtime.call(path, typeof options.body === "string" ? options.body : "");
      return new Response(text, { status: code, headers: { "Content-Type": "application/json" } });
    },
    async runtimeVersion() { booting = booting || boot(); return (await booting).version; },
  };
})();
