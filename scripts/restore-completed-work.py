#!/usr/bin/env python3
"""List or restore completed launch records without overwriting working files."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / '99_ARCHIVE/2026-09-30-completed-launch-work.zip'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prefix', nargs='?', default='01_EPISODES/')
    parser.add_argument('--restore', action='store_true')
    parser.add_argument('--into', type=Path, default=ROOT / '99_ARCHIVE/restored-launch-work')
    args = parser.parse_args()
    with ZipFile(ARCHIVE) as archive:
        manifest = json.loads(archive.read('archive-content-manifest.json'))
        selected = [e for e in manifest['entries'] if e['path'].startswith(args.prefix)]
        if not selected:
            parser.error('No matching archived paths')
        if not args.restore:
            for entry in selected:
                print(entry['path'])
            return
        destination = args.into.resolve()
        for entry in selected:
            path = (destination / entry['path']).resolve()
            if not path.is_relative_to(destination):
                parser.error('Unsafe archived path')
            if path.exists():
                parser.error('Use an empty destination; file exists: ' + str(path))
            if hashlib.sha256(archive.read(entry['path'])).hexdigest() != entry['sha256']:
                parser.error('Archived file checksum mismatch: ' + entry['path'])
        for entry in selected:
            path = destination / entry['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as output:
                output.write(archive.read(entry['path']))
        print(f'Restored {len(selected)} files under {destination}')

if __name__ == '__main__':
    main()
