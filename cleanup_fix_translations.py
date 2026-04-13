from pathlib import Path

root = Path('.chainlit/translations')
if not root.exists():
    raise SystemExit('No translations folder')

for path in sorted(root.glob('*.json')):
    text = path.read_text(encoding='utf-8')
    out_lines = []
    in_conflict = False
    keep = False
    changed = False
    for line in text.splitlines():
        if line.startswith('<<<<<<< HEAD'):
            in_conflict = True
            keep = True
            changed = True
            continue
        if in_conflict and line.startswith('======='):
            keep = False
            continue
        if in_conflict and line.startswith('>>>>>>>'):
            in_conflict = False
            continue
        if not in_conflict or keep:
            out_lines.append(line)
    if changed:
        path.write_text('\n'.join(out_lines) + ('\n' if text.endswith('\n') else ''), encoding='utf-8')
        print('Cleaned', path)
