"""Parse google-research/meena conversation files into JSONL.

Usage: python load_meena.py <dir containing meena.txt/human.txt/mitsuku.txt/xiaoice.txt> <out.jsonl>
Source: https://github.com/google-research/google-research/tree/master/meena (Apache-2.0)
"""
import json
import re
import sys
from pathlib import Path

HEADER = re.compile(r"^(?P<bot>\w+) Conversation (?P<id>\d+)\s*$")
TURN = re.compile(r"^(?P<speaker>Human(?: \d)?|Meena|Mitsuku|XiaoIce): ?(?P<text>.*)$")


def parse(path):
    conv = None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = HEADER.match(line)
        if m:
            if conv:
                yield conv
            conv = {"source": m["bot"], "id": int(m["id"]), "turns": []}
            continue
        m = TURN.match(line)
        if m and conv is not None:
            conv["turns"].append({"speaker": m["speaker"], "text": m["text"]})
        elif line.strip() and conv and conv["turns"]:
            conv["turns"][-1]["text"] += "\n" + line  # multi-line utterance
    if conv:
        yield conv


if __name__ == "__main__":
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for name in ["meena", "human", "mitsuku", "xiaoice"]:
            for c in parse(src / f"{name}.txt"):
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
                n += 1
    print("wrote", n, "conversations to", out)
