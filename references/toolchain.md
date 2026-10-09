# Toolchain traps (cadquery / OCCT / playwright / CI)

## CadQuery / OCCT
- Fillets on fused prisms fail silently or explode → move the feature
  into the 2D profile (chamfers/tapers print better anyway).
- `Workplane.rect()` CENTERS on its origin — build rects from the center.
- Cylinder/capsule direction must be `end − start`; a reversed cylinder
  once produced phantom 200 mm³ intersections.
- OCP/OpenCascade segfaults (exit 139) on constrained CI runners when its
  thread pool races: pin `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1` in
  every CI job. Healthy build boxes may run unpinned.
- STEP exports embed timestamps → never byte-compare STEP files; the
  determinism gate hashes STLs.

## Rendering
- VTK offscreen needs a GL stack on CI (apt: libegl1 libgl1 libosmesa6
  …), else exit 139.
- three.js-in-chromium render loops: every `loader.load()` needs an
  error callback; a single 404 otherwise hangs `wait_for_function` for
  the full timeout. Fail fast by setting `document.title = 'LOAD_ERROR'`
  in the error handler and checking it after each wait.
- Placeholder meshes (battery, glass) load from the directory the
  builder writes them to — keep the URL contract in ONE place.
- WebGL pages: fresh page per heavy scene if context loss appears.

## CI / deploy
- Cache dirs must be created before a no-download cache path writes into
  them.
- Generated renders deploy to Pages as an ORPHAN branch, force-pushed
  from a job dir (git init inside the rendered output dir) — never
  orphan-branch from the working repo.
- Frozen requirements are the contract between local and CI.

## Remote build boxes (rsync + terminal multiplexer)
- rsync excludes PROTECT from `--delete`: `--exclude=__pycache__` will
  keep remote pycache dirs alive and block directory removal — clean
  explicitly.
- Drive long jobs in visible panes with anchored markers:
  `cmd; echo DONE_$?` and match `^DONE_[0-9]+$` (a bare marker
  false-matches the echoed command line).
- Heavy env setup once per box: uv venv + frozen requirements + (renders)
  `playwright install --with-deps chromium`.

## Local vs remote loop
Validation that takes minutes locally can take seconds on a 20-core box —
sync, validate remotely, rsync artifacts back, and byte-diff what should
be deterministic before trusting either side.
