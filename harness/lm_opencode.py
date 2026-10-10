"""OpenCodeLM — a dspy.LM that literally pipes through `opencode run`.

No API key exists in this environment; the only sanctioned inference
path is the opencode coding agent itself. Each LM call spawns:

    opencode run [-m provider/model] "<flattened messages>"

Sync-only engine (dspy retries/eval defaults are sync in our usage).
Latency ~60 s/call: fine for stage execution (4-5 calls/board); a full
optimizer compile through this pipe is demo-scale. Swap in a real
dspy.LM when a key exists — nothing else in the harness changes.
"""

from __future__ import annotations

import re
import subprocess

import dspy

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _flatten(messages: list[dict]) -> str:
    out = []
    for m in messages:
        role = str(m.get("role", "user")).upper()
        out.append(f"{role}:\n{m.get('content', '')}")
    return "\n\n".join(out)


def _run_opencode(text: str, model: str | None, timeout: int) -> str:
    cmd = ["opencode", "run"]
    if model:
        cmd += ["-m", model]
    cmd += [text]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    lines = [ANSI.sub("", ln).rstrip() for ln in r.stdout.splitlines()]
    keep = [ln for ln in lines
            if ln.strip() and not ln.startswith("> ") and not ln.startswith("•")]
    out = "\n".join(keep).strip()
    if not out:
        raise RuntimeError(
            f"opencode run empty (rc={r.returncode}): {r.stderr.strip()[:200]}")
    return out


class OpenCodeEngine:
    def __init__(self, owner):
        self.owner = owner

    def complete(self, request):
        from dspy.lm15 import Message, Response, TextPart, Usage
        messages = []
        if request.system is not None:
            system = request.system if isinstance(request.system, str) else \
                "".join(p.text for p in request.system)
            messages.append({"role": "system", "content": system})
        messages.extend({"role": m.role, "content": m.text or ""}
                        for m in request.messages)
        text = _flatten(messages)
        last = None
        for _ in range(self.owner._tries):
            try:
                out = _run_opencode(text, self.owner._oc_model,
                                    self.owner._timeout)
                return Response(
                    id=None,
                    model="opencode/pipe",
                    message=Message(role="assistant",
                                    parts=(TextPart(text=out),)),
                    finish_reason="stop",
                    usage=Usage())
            except Exception as exc:  # noqa: BLE001 - pipe is flaky by nature
                last = exc
        raise last


class OpenCodeLM(dspy.LM):
    def __init__(self, model: str | None = None, timeout: int = 300,
                 tries: int = 2):
        self._oc_model = model          # None = opencode default agent/model
        self._timeout = timeout
        self._tries = tries
        super().__init__(model or "opencode/pipe", "chat")
        self._engine_spec = OpenCodeEngine(self)

    def copy(self, **kwargs):
        copied = OpenCodeLM(model=self._oc_model, timeout=self._timeout,
                            tries=self._tries)
        copied._engine_spec = OpenCodeEngine(copied)
        return copied
