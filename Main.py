#!/usr/bin/env python3
"""
PyMOL Agent for Windsurf
- Generates PyMOL commands with OpenAI Chat Completions
- Saves to .pml and (optionally) executes via pymol2
Usage examples (after installing deps and setting OPENAI_API_KEY):
  python pymol_agent.py --pdb 6HRE --obj tau --copies 10 --step 15 --axis x --out tau_stack.pml
  python pymol_agent.py --pdb 6HRE --execute
"""
from __future__ import annotations
import argparse, os, sys, shutil
from typing import List
from openai import OpenAI

# ---- Safety: whitelist allowed PyMOL commands
ALLOWED = {
  "fetch","load","set_name","hide","show","as","color","spectrum","bg_color",
  "create","translate","rotate","zoom","orient","center","set","select","sele","save"
}
BLOCKED_TOKENS = {"python","cmd.","run ","@","import","exec","eval","system","delete","remove"}

SYSTEM_PROMPT = """You are a PyMOL command generator.
RULES:
- Output ONLY PyMOL commands, one per line. No prose, no code fences.
- Assume a clean session.
- If the requested object is not loaded, fetch the given PDB id then rename to the requested object name.
- Default style: hide everything; show cartoon; color by secondary structure (H=red, S=yellow, L=white); bg_color white.
- For aggregation: create explicit copies and translate each copy by the given step along the chosen axis.
- Finish with: zoom all
- Never output comments or explanations.
"""

def build_user_prompt(obj: str, pdb_id: str|None, copies: int|None, step: float|None, axis: str|None, extra: str|None) -> str:
    parts = []
    if obj:    parts.append(f"Object name: {obj}")
    if pdb_id: parts.append(f"PDB id to fetch if missing: {pdb_id}")
    if copies and step and axis:
        parts.append(f"Aggregation: make {copies} total units, shift {step} Å per copy along {axis}.")
    parts.append("Tasks:")
    parts.append("1) Load/fetch structure.")
    parts.append("2) Hide everything; show cartoon; color by secondary structure; bg_color white.")
    if copies and step and axis:
        parts.append(f"3) Create {copies-1} copies and translate each by {step} Å along {axis}, keeping the first at origin.")
    parts.append("4) Finish with zoom all.")
    parts.append("IMPORTANT: One PyMOL command per line, no prose.")
    if extra:
        parts.append(f"Extra request: {extra}")
    return "\n".join(parts)

def validate_lines(lines: List[str]) -> List[str]:
    out = []
    for raw in lines:
        line = raw.strip()
        if not line: 
            continue
        l = line.lower()
        if any(tok in l for tok in BLOCKED_TOKENS):
            continue
        first = l.split()[0]
        if first.endswith(","):  # e.g., "as"
            first = first[:-1]
        if first not in ALLOWED:
            # allow "as" alias and common forms already in ALLOWED
            continue
        out.append(line)
    return out

def ask_model(prompt: str, model: str="gpt-5") -> str:
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system", "content": SYSTEM_PROMPT},
            {"role":"user",   "content": prompt}
        ],
    )
    return resp.choices[0].message.content.strip()

def write_pml(path: str, commands: List[str]) -> None:
    with open(path, "w") as f:
        for c in commands:
            f.write(c.rstrip() + "\n")

def maybe_execute_with_pymol2(commands: List[str]) -> None:
    try:
        import pymol2  # requires open-source PyMOL installed
    except Exception as e:
        print("! Skipping execution (pymol2 not available):", e, file=sys.stderr)
        print("Open the .pml in PyMOL: File → Run…", file=sys.stderr)
        return
    with pymol2.PyMOL() as pm:
        for c in commands:
            pm.cmd.do(c)

def main():
    ap = argparse.ArgumentParser(description="Generate and (optionally) execute PyMOL commands with OpenAI.")
    ap.add_argument("--pdb", help="PDB id to fetch if missing (e.g. 6HRE)")
    ap.add_argument("--obj", default="obj", help="Object name inside PyMOL (default: obj)")
    ap.add_argument("--copies", type=int, help="Total number of units for aggregation")
    ap.add_argument("--step", type=float, help="Translation per copy in Å")
    ap.add_argument("--axis", choices=["x","y","z"], help="Axis for translation")
    ap.add_argument("--extra", help="Freeform extra instruction (e.g. 'color chain A green')")
    ap.add_argument("--model", default="gpt-4o", help="OpenAI chat model (default gpt-4o)")
    ap.add_argument("--out", default="script.pml", help="Output .pml path (default script.pml)")
    ap.add_argument("--execute", action="store_true", help="Execute now via pymol2 (if available)")
    args = ap.parse_args()

    # sanity checks
    if args.copies or args.step or args.axis:
        if not (args.copies and args.step and args.axis):
            ap.error("--copies, --step and --axis must be provided together")

    # build & call
    user_prompt = build_user_prompt(args.obj, args.pdb, args.copies, args.step, args.axis, args.extra)
    raw = ask_model(user_prompt, model=args.model)
    lines = [ln for ln in raw.splitlines()]
    validated = validate_lines(lines)

    if not validated:
        print("No valid PyMOL commands produced. Raw output:\n", raw, file=sys.stderr)
        sys.exit(2)

    write_pml(args.out, validated)
    print(f"✅ Wrote {args.out} with {len(validated)} commands.")
    print("Preview:")
    for ln in validated[:8]:
        print("  ", ln)
    if args.execute:
        print("→ Executing via pymol2…")
        maybe_execute_with_pymol2(validated)
    else:
        # helpful tip if GUI available
        hint = "pymol -cq " + args.out if shutil.which("pymol") else "Open PyMOL → File → Run… → " + args.out
        print("Run in PyMOL:", hint)

if __name__ == "__main__":
    # Require env var (don’t hardcode keys)
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY in your shell before running.", file=sys.stderr)
        sys.exit(1)
    main()
