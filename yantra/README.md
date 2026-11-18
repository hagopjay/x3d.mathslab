# Sri Yantra · Resonance Loom (live editions)

A measured Sri Yantra in native X3D with a harmonic instrument. Nine canonical triangles make 43 chambers. Edition 2.0, the **Chamber Harp**, makes every chamber playable: touch one to strike it. Its mathematics (the Huet/Chiodo concentric construction, coverage depth and the numerical witness) makes it a geometry lesson as much as an artwork.

- Play: https://hagopjay.github.io/x3d.mathslab/yantra/ (opens 2.0.0)
- Source, tests and validation receipts: `hagopjay/x3d.loom`, folder `x3d.mandala/` ([CHAMBER-HARP.md](https://github.com/hagopjay/x3d.loom/blob/main/x3d.mandala/docs/CHAMBER-HARP.md), [HARP-GAPS.md](https://github.com/hagopjay/x3d.loom/blob/main/x3d.mandala/docs/HARP-GAPS.md))

Each release folder is a frozen, self-contained standalone (pinned X_ITE 16.8.0 embedded, no network requests) plus the authored X3D scene. **Never overwrite a release.** A new edition gets a new folder, and `index.html` here moves to it.

| Edition | File | Bytes | SHA-256 |
|---|---|---|---|
| 1.0.0 | `index.html` | 2,172,698 | `52c6caf22eb77074d8ae0d43f62c38fe2f4eaea752764283575c57d0560fd828` |
| 1.0.0 | `Sri-Yantra-Resonance-Loom.x3d` | 3,712,579 | `10ef65a2258fa1b66072ab90778c67e66aa7de2d445a5855db4ba255dad91e55` |
| 2.0.0 | `index.html` | 2,201,910 | `d378552d0845c4d281a85c6a32210f13f337a929e687d420d58366097b608afc` |
| 2.0.0 | `Sri-Yantra-Resonance-Loom.x3d` | 3,753,964 | `7f31eb449108a2fbe5e0dca7066869deed2a4b1034466b2f28246f91b9e42406` |

1.0.0 is the uploaded standalone byte for byte; a clean build of the delivered source reproduces it. 2.0.0 is built with `node tools/build.mjs` from the x3d.loom commit "x3d.mandala 2.0: the Chamber Harp".

This folder is outside the Math Lab release manifest and `tools/check_release.py` inputs, so it does not change Math Lab's checks.
