#!/usr/bin/env python3
"""Read-only OOOD H.264 SDR gate: check coded headers and every decoded frame."""
import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import re
import struct
import subprocess

EXPECTED_FRAME = ('tv', 'bt709', 'bt709', 'bt709')
HEADER_FIELDS = ('video_signal_type_present_flag', 'video_full_range_flag',
                 'colour_description_present_flag', 'colour_primaries',
                 'transfer_characteristics', 'matrix_coefficients')
EXPECTED_HEADER = (1, 0, 1, 1, 1, 1)


def container_audit(path):
    """Inspect MP4 structure without scanning or loading the picture payload."""
    edits, sample_entries, colors = [], [], []
    containers = {'moov', 'trak', 'mdia', 'minf', 'stbl', 'edts'}
    with path.open('rb') as media:
        def walk(start, end, parent=''):
            pos = start
            while pos + 8 <= end:
                media.seek(pos)
                size, kind = struct.unpack('>I4s', media.read(8))
                header = 8
                if size == 1:
                    size = struct.unpack('>Q', media.read(8))[0]
                    header = 16
                if size == 0:
                    size = end - pos
                if size < header or pos + size > end:
                    raise ValueError('Malformed MP4 box')
                kind = kind.decode('ascii', errors='replace')
                name = parent + '/' + kind
                if kind == 'elst':
                    edits.append(name)
                if kind in containers:
                    walk(pos + header, pos + size, name)
                if kind == 'stsd':
                    media.seek(pos + header + 4)
                    count = struct.unpack('>I', media.read(4))[0]
                    sample_entries.append({'path': name, 'count': count})
                    entry = pos + header + 8
                    for _ in range(count):
                        media.seek(entry)
                        length, codec = struct.unpack('>I4s', media.read(8))
                        if length < 8 or entry + length > pos + size:
                            raise ValueError('Malformed MP4 sample entry')
                        if codec in (b'avc1', b'avc3'):
                            walk(entry + 86, entry + length, name + '/' + codec.decode())
                        entry += length
                if kind == 'colr':
                    media.seek(pos + header)
                    data = media.read(size - header)
                    if data[:4] in (b'nclx', b'nclc') and len(data) >= 10:
                        values = list(struct.unpack('>HHH', data[4:10]))
                        full_range = (data[10] >> 7) if data[:4] == b'nclx' and len(data) > 10 else 0
                        colors.append({'path': name, 'values': values, 'full_range': full_range})
                pos += size
        walk(0, path.stat().st_size)
    passed = not edits and bool(sample_entries) and all(s['count'] == 1 for s in sample_entries)
    passed = passed and bool(colors) and all(c['values'] == [1, 1, 1] and c['full_range'] == 0 for c in colors)
    return {'edit_lists': edits, 'sample_entries': sample_entries, 'color_boxes': colors, 'passed': passed}


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stderr[-2000:]}')
    return result


def verify(path):
    path = Path(path).resolve()
    metadata = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_streams', '-of', 'json', str(path)]).stdout)['streams'][0]
    if metadata['codec_name'] != 'h264':
        raise ValueError('This gate supports H.264 SDR exports; use a codec-specific header audit for others.')
    time_base = float(Fraction(metadata['time_base']))
    # Decode views may inherit earlier tags and mask unspecified SPS values.
    # Filter to SPS units before tracing so output excludes picture-slice headers.
    traced = run(['ffmpeg', '-nostdin', '-hide_banner', '-v', 'info', '-i', str(path),
        '-map', '0:v:0', '-c:v', 'copy', '-bsf:v',
        'filter_units=pass_types=7-8,trace_headers', '-f', 'null', '-'])
    headers = []
    parameter_sets = {'sps': [], 'pps': []}
    current = None
    complete = None
    kind = None
    packet_time = None
    for line in traced.stderr.splitlines():
        new_kind = ('sps' if 'Sequence Parameter Set' in line else
                    'pps' if 'Picture Parameter Set' in line else None)
        if new_kind or 'Packet:' in line:
            if complete is not None:
                parameter_sets[kind].append({'time': packet_time, 'fields': complete})
            complete = None
            kind = None
        if 'Packet:' in line:
            match = re.search(r'\bpts (-?\d+)', line)
            packet_time = int(match[1]) * time_base if match else None
        if 'Sequence Parameter Set' in line:
            if current is not None:
                headers.append(current)
            current = {'time': packet_time}
        if new_kind:
            kind = new_kind
            complete = {}
        field = re.search(r'\]\s+\d+\s+(\S+)\s+[01]+\s+=\s+(-?\d+)', line)
        if field and complete is not None:
            complete[field[1]] = int(field[2])
        match = re.search(r'\s(' + '|'.join(HEADER_FIELDS) + r')\s+[01]+\s+=\s+(\d+)', line)
        if match and current is not None:
            current[match[1]] = int(match[2])
    if current is not None:
        headers.append(current)
    if complete is not None:
        parameter_sets[kind].append({'time': packet_time, 'fields': complete})
    configurations = {}
    for kind, entries in parameter_sets.items():
        variants = {}
        for entry in entries:
            signature = json.dumps(entry['fields'], sort_keys=True)
            if signature not in variants:
                variants[signature] = {'first_time': entry['time'], 'fields': entry['fields'], 'count': 0}
            variants[signature]['count'] += 1
        configurations[kind] = {'count': len(entries), 'variants': list(variants.values())}
    configuration_ok = all(len(c['variants']) == 1 for c in configurations.values())
    container = container_audit(path)
    header_counts = Counter(tuple(h.get(k) for k in HEADER_FIELDS) for h in headers)
    changes = []
    previous = None
    for header in headers:
        color = tuple(header.get(k) for k in HEADER_FIELDS)
        if color != previous:
            changes.append(header)
            previous = color
    stream_color = tuple(metadata.get(k) for k in
        ('color_range', 'color_space', 'color_primaries', 'color_transfer'))
    header_ok = bool(headers) and set(header_counts) == {EXPECTED_HEADER}
    report = {'path': str(path), 'passed': False,
        'stream_color': dict(zip(('range', 'space', 'primaries', 'transfer'), stream_color)),
        'h264_header_audit': {'sps_count': len(headers), 'field_order': HEADER_FIELDS,
            'combinations': {str(k): v for k, v in header_counts.items()},
            'changes': changes, 'passed': header_ok},
        'encoding_configuration_audit': {'parameter_sets': configurations, 'passed': configuration_ok},
        'container_audit': container, 'frame_audit': None}
    # Reject bad coded headers immediately; do not accept inherited decoder tags.
    if not header_ok or stream_color != EXPECTED_FRAME or not configuration_ok or not container['passed']:
        return report
    decoded = run(['ffprobe', '-v', 'error', '-threads', '4', '-select_streams', 'v:0',
        '-show_frames', '-show_entries',
        'frame=best_effort_timestamp_time,width,height,pix_fmt,sample_aspect_ratio,interlaced_frame,color_range,color_space,color_primaries,color_transfer',
        '-of', 'compact=p=0', str(path)])
    counts = Counter()
    properties = Counter()
    last = -float('inf')
    increasing = True
    for line in decoded.stdout.splitlines():
        values = dict(item.split('=', 1) for item in line.split('|') if '=' in item)
        try:
            seconds = float(values['best_effort_timestamp_time'])
        except (KeyError, ValueError):
            continue
        increasing = increasing and seconds > last
        last = seconds
        counts[tuple(values.get(k) for k in ('color_range','color_space','color_primaries','color_transfer'))] += 1
        properties[tuple(values.get(k) for k in ('width','height','pix_fmt','sample_aspect_ratio','interlaced_frame'))] += 1
    frames = sum(counts.values())
    expected = metadata.get('nb_frames')
    count_ok = expected in (None, 'N/A') or frames == int(expected)
    properties_ok = len(properties) == 1 and all(p[2] == 'yuv420p' and p[4] == '0' for p in properties)
    frame_ok = frames > 0 and set(counts) == {EXPECTED_FRAME} and properties_ok and increasing and count_ok and not decoded.stderr.strip()
    report['frame_audit'] = {'frames': frames, 'expected_frames': expected,
        'combinations': {str(k): v for k, v in counts.items()},
        'picture_properties': {str(k): v for k, v in properties.items()},
        'strictly_increasing_frame_times': increasing, 'last_frame_time': last,
        'errors': decoded.stderr, 'passed': frame_ok}
    report['passed'] = frame_ok
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.report and args.report.exists():
        raise FileExistsError(args.report)
    report = verify(args.video)
    if args.report:
        with args.report.open('x') as output:
            json.dump(report, output, indent=2)
            output.write('\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 2)


if __name__ == '__main__':
    main()
