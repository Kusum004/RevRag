You are building a complete, end-to-end working system for PS-002: RevRag In-App Agent — Zero-Touch App Understanding. Implement this fully — every layer, wired together, actually runnable — not a partial demo or a proof-of-concept for one piece. Follow a proper SDLC: design before code, build layer by layer with a passing checkpoint after each, write tests as you go, and produce a README written for a judge evaluating the finished product.

GOAL
Build an AI system that autonomously explores an unfamiliar Android app (no scripted/human-recorded flows), understands each screen's purpose/elements/form fields even without accessibility labels, extracts the app's brand & design language from screenshots + UI tree, and produces a compact, structured, stable "App Knowledge Pack" (JSON) usable by another AI. Include a viewer UI showing the screen graph next to each screen's profile, and a rebuild test that regenerates 2-3 screens from the pack alone to prove fidelity.

HARD CONSTRAINTS
- Exploration must be fully autonomous: an agent decides what to tap/scroll/fill next; no hand-authored flow scripts.
- Must get past login/OTP/KYC using provided test credentials during exploration.
- Output must be stable: two scans of the same app must converge on the same screen graph (dedupe by structural fingerprint, not by path taken).
- Raw UI trees can exceed 1.5MB — the knowledge pack must be a compact, summarized derivative, never raw XML/tree dumps.
- Target platform: Android, Kotlin-first tooling (UIAutomator2/Appium for device control is acceptable). Use any on-device or API-based LLM/VLM.

BUILD IN THIS ORDER — implement one layer fully, show me it working (or write the test that proves it), THEN move to the next. Do not jump ahead.

LAYER 1 — Instrumentation Layer
- Wrap device control (UIAutomator2/Appium) behind a clean interface: getScreenState(), performAction(action), getUiTree(), takeScreenshot().
- Unit-test this against a running emulator with a trivial sample app before touching anything else.

LAYER 2 — Perception Layer
- On each visited screen, capture: screenshot (compressed), full UI hierarchy (bounds, class, resource-id even if unlabeled), and compute a structural fingerprint hash (based on view hierarchy shape + resource-ids, NOT pixels) so the same screen is recognized on repeat visits regardless of dynamic content.
- Write a test proving two screenshots of the "same" screen with different dynamic content (e.g. different list items) hash identically.

LAYER 3 — Exploration Agent
- Implement a policy loop: given the current screen + the graph of screens/edges discovered so far, pick the next action from an unexplored-elements frontier per screen.
- Include: cycle detection via fingerprint, a login/OTP/KYC handler using supplied test data, a step budget/coverage stop condition, and back-navigation recovery when stuck.
- Log every (screen_fingerprint, action, resulting_screen_fingerprint) triple — this becomes your journey graph.

LAYER 4 — Screen Understanding Layer
- For each captured screen, send screenshot + UI tree together to a VLM/LLM. Prompt it to output: screen purpose (1 sentence), per-element type/role/plain-language description, and form-field semantics — grounded in the screenshot even when the tree has no labels.
- Validate output against a strict JSON schema; reject and retry on malformed output.

LAYER 5 — Design Extraction Layer
- Separately extract: dominant color palette, typography signal, spacing rhythm, light/dark mode, tone of voice from visible copy, recurring component patterns — from the batch of screenshots + trees.

LAYER 6 — Journey Graph Builder
- Merge per-fingerprint screen understanding + all transition edges into a single deduplicated graph. Prove stability: run exploration twice on the same app, diff the two resulting graphs, and report near-zero divergence.

LAYER 7 — Knowledge Pack Compiler
- Compile everything into the compact JSON schema (define it explicitly before writing this layer). Enforce a size ceiling and verify well below 1.5MB even for a large app.

LAYER 8 — Viewer
- Minimal web frontend: graph/list of screens on one side; clicking a screen shows its screenshot next to its extracted profile (purpose, elements, design tokens).

LAYER 9 — Rebuild Test Harness
- Given only the knowledge pack (no original screenshots), generate a rough visual reconstruction of 2-3 screens (can be simple HTML/CSS using the extracted design tokens + element list). Show it side-by-side with the real screenshot as your fidelity proof.

DELIVERABLES
1. Clean, modular codebase — one directory per layer above, clear interfaces between them, no god-files.
2. Automated tests for the fingerprinting/dedup logic and the JSON schema validation at minimum.
3. A single command (script or Makefile target) that runs the full pipeline end-to-end against a target app package name.
4. A README.md containing:
   - One-paragraph problem statement in your own words and why manual flow recording breaks
   - Architecture diagram (mermaid, layers as above) and a flow diagram of one exploration cycle
   - Setup/run instructions (emulator setup, dependencies, how to point it at a new app)
   - The knowledge pack JSON schema, documented field by field
   - Your stability test result (before/after diff) and rebuild test screenshots
   - Known limitations and what you'd build next with more time
5. Keep everything reproducible — pin dependency versions, no hardcoded absolute paths, no secrets committed (use .env / test-data config file for login credentials).

Work incrementally: after each layer, show me it passing its own test/checkpoint before moving to the next layer. Do not stop at a partial system — carry every layer through to a fully working, integrated pipeline, end to end, from pointing at an app package name to producing the final knowledge pack, viewer, and rebuild test output. If any design decision forces a simplification, note it explicitly in the README's limitations section rather than hiding it.
