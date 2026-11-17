#!/usr/bin/env python3
"""Run scoped release instruments and retain source/asset identities and output."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inputs():
    paths = [ROOT / n for n in ('pyproject.toml', 'run.sh', 'run.bat', 'run_mathlab.py', 'run_mathlab_mcp.py',
                                'web/index.html', 'web/app.js', 'web/static-api.js', 'web/style.css',
                                'web/vendor/x_ite/ORIGIN.json', 'vendor/x3d_mcp/ORIGIN.json')]
    for folder in ('mathlab', 'src/manim_mcp', 'tests', 'tools', 'schemas'):
        paths += [p for p in (ROOT / folder).rglob('*')
                  if p.suffix in ('.py', '.mjs', '.json', '.txt') and '__pycache__' not in p.parts]
    return {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted(set(paths))}


def verify_assets():
    results = []
    for directory, key in [('web/vendor/x_ite', 'files'), ('vendor/x3d_mcp', 'files_sha256')]:
        root = ROOT / directory
        origin = json.loads((root / 'ORIGIN.json').read_text())
        entries = origin[key]
        for name, row in entries.items():
            expected = row['sha256'] if isinstance(row, dict) else row
            if sha((root / name).read_bytes()) != expected:
                raise ValueError('Vendored input changed: ' + directory + '/' + name)
        results.append({'directory': directory, 'files': len(entries), 'status': 'pass'})
    build = json.loads((ROOT / 'receipts/example-build.json').read_text())
    for row in build['examples']:
        for name, expected in row['files'].items():
            data = (ROOT / name).read_bytes()
            if sha(data) != expected['sha256'] or len(data) != expected['bytes']:
                raise ValueError('Generated example changed: ' + name)
    if sha((ROOT / 'schemas/lesson-card.schema.json').read_bytes()) != build['card_schema_sha256']:
        raise ValueError('Generated lesson-card schema changed.')
    for name, expected in build['source_sha256'].items():
        if sha((ROOT / 'mathlab' / name).read_bytes()) != expected:
            raise ValueError('Examples need regeneration after source change: ' + name)
    return results


def main():
    identity = inputs()
    report = {'schema': 'mathlab.release-checks/1', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'environment': {'python': platform.python_version(), 'platform': platform.platform()},
              'source_sha256': identity, 'tests': [], 'status': 'not_run',
              'scope': 'Scoped development evidence, not a formal Loom acceptance or learning-outcome study.',
              'limitations': ['Manim renderer tests use explicit registration/subprocess adapters and fake media, plus one owned real child reap.',
                              'UI concurrency tests use actual functions with explicit DOM/X_ITE adapters; browser observations are separate.',
                              'No Manim video, hardware-GPU benchmark or cross-host comparison ran in this command.']}
    failed = False
    try:
        report['assets'] = verify_assets()
        commands = [[sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                    ['node', 'tests/ui_state.test.mjs'],
                    ['node', 'tests/learning_ui.test.mjs'],
                    ['node', 'tests/connections_ui.test.mjs'],
                    [sys.executable, 'tools/independent_probe.py'],
                    [sys.executable, 'tools/probe_aha.py'],
                    [sys.executable, 'tools/probe_expeditions.py'],
                    [sys.executable, 'tools/probe_math_mcp.py'],
                    [sys.executable, 'tools/validate_x3d.py']]
        for command in commands:
            started = time.perf_counter()
            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
            output = process.stdout + process.stderr
            row = {'command': command[1:], 'exit_code': process.returncode,
                   'duration_seconds': round(time.perf_counter() - started, 4),
                   'stdout': process.stdout, 'stderr': process.stderr}
            if command[1:3] == ['-m', 'unittest']:
                match = re.search(r'Ran (\d+) tests?', output)
                row['tests_run'] = int(match.group(1)) if match else 0
                row['skipped'] = int(re.search(r'skipped=(\d+)', output).group(1)) if re.search(r'skipped=(\d+)', output) else 0
                if not match or row['skipped']:
                    failed = True
            if process.returncode:
                failed = True
            report['tests'].append(row)
            print(('PASS ' if process.returncode == 0 else 'FAIL ') + ' '.join(command[1:]), flush=True)
        for name in ('independent-math.json', 'aha-independent.json', 'expeditions-independent.json',
                     'math-mcp.json', 'x3d-validation.json'):
            evidence = json.loads((ROOT / 'receipts' / name).read_text())
            if evidence.get('status') != 'pass':
                failed = True
        report['source_drift'] = 'none' if inputs() == identity else 'changed'
        if report['source_drift'] != 'none':
            failed = True
        report['status'] = 'fail' if failed else 'pass'
    except Exception as error:
        report['status'] = 'instrument_error'
        report['instrument_error'] = type(error).__name__ + ': ' + str(error)
        failed = True
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    report['report_sha256'] = sha(json.dumps(report, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode())
    (ROOT / 'receipts/release-checks.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps({'status': report['status'], 'instruments': len(report['tests']),
                      'python_tests': report['tests'][0].get('tests_run') if report['tests'] else None,
                      'source_drift': report.get('source_drift')}))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
