#!/usr/bin/env python3
"""Refresh portable context snapshots and create individual Claude upload ZIPs."""
from pathlib import Path
import hashlib
import json
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
SOURCES={'show-context.md':ROOT/'00_CONTEXT/PROJECT_BRIEF.md','editorial-direction.md':ROOT/'00_CONTEXT/editorial-direction.md','brand-guide.md':ROOT/'03_ASSETS/brand-guidelines.md'}

def main():
    out=ROOT/'exports/skills';out.mkdir(parents=True,exist_ok=True)
    records=[]
    for skill in sorted((ROOT/'skills').glob('oood-*')):
        if not (skill/'SKILL.md').is_file():continue
        refs=skill/'references';refs.mkdir(exist_ok=True)
        for name,source in SOURCES.items():
            header='<!-- Generated portable snapshot. Live OOOD repository files take precedence. -->\n\n'
            text=source.read_text().replace('](../03_ASSETS/brand-guidelines.md)','](brand-guide.md)').replace('](brand-tokens.json)','](../assets/brand-tokens.json)')
            (refs/name).write_text(header+text)
        assets=skill/'assets';assets.mkdir(exist_ok=True)
        shutil.copy2(ROOT/'03_ASSETS/brand-tokens.json',assets/'brand-tokens.json')
        dest=out/(skill.name+'.zip')
        with ZipFile(dest,'w',ZIP_DEFLATED) as z:
            for p in sorted(skill.rglob('*')):
                if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
                    z.write(p,str(Path(skill.name)/p.relative_to(skill)))
            if skill.name=='oood-brand-visuals':
                for p in sorted((ROOT/'03_ASSETS/brand-fonts').iterdir()):
                    if p.is_file():z.write(p,str(Path(skill.name)/'assets/fonts'/p.name))
        records.append({'skill':skill.name,'zip':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    (out/'package-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()
