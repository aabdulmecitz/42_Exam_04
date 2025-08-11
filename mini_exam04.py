#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_TESTS = {
    'ft_popen': {
        'tester': ROOT / 'ft_popen' / 'test_ft_popen.c',
        'binary': 'test_ft_popen',
        'compile': lambda src: ['cc', '-Wall', '-Wextra', str(src), str(ROOT / 'ft_popen' / 'test_ft_popen.c'), '-o', 'test_ft_popen']
    },
    'picoshell': {
        'tester': ROOT / 'picoshell' / 'test_picoshell.c',
        'binary': 'test_picoshell',
        'compile': lambda src: ['cc', '-Wall', '-Wextra', str(src), str(ROOT / 'picoshell' / 'test_picoshell.c'), '-o', 'test_picoshell']
    },
    'vbc': {
        'binary': 'vbc',
        'compile': lambda src: ['cc', '-Wall', '-Wextra', str(src), '-o', 'vbc']
    }
}

# Colors
RST = "\033[0m"; BOLD = "\033[1m"; GRN = "\033[32m"; RED = "\033[31m"; CYN = "\033[36m"; YLW = "\033[33m"

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

# --- VBC cases (same as Makefile) ---
VBC_VALID = [
    ('1', '1'),
    ('2+3', '5'),
    ('3*4+5', '17'),
    ('3+4*5', '23'),
    ('(3+4)*5', '35'),
    ('(((((2+2)*2+2)*2+2)*2+2)*2+2)*2', '188'),
    ('1+2+3+4+5', '15'),
    ('(1)', '1'),
    ('(((((((3)))))))', '3'),
    ('(1+2)*3', '9'),
    ('2*4+9+3+2*1+5+1+6+6*1*1+8*0+0+5+0*4*9*5*8+9*7+5*1+3+1+4*5*7*3+0*3+4*8+8+8+4*0*5*3+5+4+5*7+9+6*6+7+9*2*6*9+2+1*3*7*1*1*5+1+2+7+4+3*4*2+0+4*4*2*2+6+7*5+9+0+8*4+6*7+5+4*4+2+5*5+1+6+3*5*9*9+7*4*3+7+4*9+3+0+1*8+1+2*9*4*5*1+0*1*9+5*3*5+9*6+5*4+5+5*8*6*4*9*2+0+0+1*5*3+6*8*0+0+2*3+7*5*6+8+6*6+9+3+7+0*0+5+2*8+2*7*2+3+9*1*4*8*7*9+2*0+1*6*4*2+8*8*3*1+8+2*4+8*3+8*3+9*5+2*3+9*5*6*4+3*6*6+7+4*8+0+2+9*8*0*6*8*1*2*7+0*5+6*5+0*2+7+2+3+8*7+6+1*3+5+4*5*4*6*1+4*7+9*0+4+9*8+7+5+6+2+6+1+1+1*6*0*9+7+6*2+4*4+1*6*2*9+3+0+0*1*8+4+6*2+6+2*7+7+0*9+6+2*1+6*5*2*3*5*2*6*4+2*9*2*4*5*2*2*3+8+8*3*2*3+0*5+9*6+8+3*1+6*9+8+9*2*0+2', '94305'),
]
VBC_ERRORS = [
    ('1+', 'Unexpected end of input'),
    ("1+2)", "Unexpected token ')'"),
    ("((1+3)*12+(3*(2+6))", "Unexpected token '2'"),
]

def test_vbc_binary(bin_path: Path):
    print(f"\n{BOLD}[vbc Tests]{RST} {CYN}(many cases){RST}")
    passed = 0; total = 0
    def run_case(expr, expect, is_err):
        nonlocal passed, total
        total += 1
        r = run([str(bin_path), expr])
        out = (r.stdout or '').rstrip('\n')
        ok = False
        if is_err:
            ok = (r.returncode != 0 and out == expect)
            label = expr
        else:
            ok = (r.returncode == 0 and out == expect)
            label = f"{expr} = {expect}"
        print(f"  {GRN}[PASS]{RST} {label}" if ok else f"  {RED}[FAIL]{RST} {label}")
        passed += 1 if ok else 0
    for expr, expect in VBC_VALID:
        run_case(expr, expect, False)
    for expr, expect in VBC_ERRORS:
        run_case(expr, expect, True)
    print((f"{GRN}All tests passed{RST} ({passed}/{total})" if passed == total else f"{RED}Some tests failed{RST} ({passed}/{total})"))
    return passed == total

# --- Core workflow ---

def build_and_run(assignment: str, src_path: Path) -> bool:
    if assignment not in REPO_TESTS:
        print(f"Unknown assignment: {assignment}")
        return False
    build_dir = ROOT / '.mini_build' / assignment
    ensure_dir(build_dir)

    if assignment in ('ft_popen', 'picoshell'):
        spec = REPO_TESTS[assignment]
        cmd = spec['compile'](src_path)
        r = run(cmd, cwd=build_dir)
        if r.returncode != 0:
            print(r.stdout)
            return False
        exe = build_dir / spec['binary']
        # The C tester prints summary with colors; just forward output
        rr = run([str(exe)], cwd=build_dir)
        sys.stdout.write(rr.stdout)
        return rr.returncode == 0
    else:  # vbc
        spec = REPO_TESTS['vbc']
        cmd = spec['compile'](src_path)
        r = run(cmd, cwd=build_dir)
        if r.returncode != 0:
            print(r.stdout)
            return False
        exe = build_dir / spec['binary']
        return test_vbc_binary(exe)


def copy_to_rendu(assignment: str, src: Path) -> Path:
    dest_dir = ROOT / 'rendu' / assignment
    ensure_dir(dest_dir)
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    print(f"Copied to {dest}")
    return dest


def archive_submission(assignment: str) -> Path:
    ts = time.strftime('%Y%m%d_%H%M%S')
    subs_dir = ROOT / 'submissions'
    ensure_dir(subs_dir)
    src_dir = ROOT / 'rendu' / assignment
    if not src_dir.exists():
        raise SystemExit(f"rendu/{assignment} is empty. Nothing to push.")
    archive_base = subs_dir / f"{assignment}_{ts}"
    archive_path = shutil.make_archive(str(archive_base), 'gztar', root_dir=src_dir)
    print(f"Submission archived: {archive_path}")
    return Path(archive_path)


def find_available_assignments():
    """Find assignments that have files in rendu/ directory"""
    rendu_dir = ROOT / 'rendu'
    if not rendu_dir.exists():
        return []
    
    available = []
    all_assignments = ['ft_popen', 'picoshell', 'vbc']
    
    for assignment in all_assignments:
        assign_dir = rendu_dir / assignment
        if assign_dir.exists():
            c_files = list(assign_dir.glob('*.c'))
            if c_files:
                available.append((assignment, c_files[0]))
    
    return available

def interactive_start():
    print(f"{BOLD}MiniExam04 Tester{RST}")
    
    # Check what's available in rendu/
    available = find_available_assignments()
    
    if not available:
        print(f"{YLW}No assignments found in rendu/ directory.{RST}")
        print("Available assignments:")
        choices = ['ft_popen', 'picoshell', 'vbc']
        for i, name in enumerate(choices, 1):
            print(f"  {i}. {name}")
        sel = input('Select assignment [1-3]: ').strip()
        try:
            idx = int(sel) - 1
            assignment = choices[idx]
        except Exception:
            raise SystemExit('Invalid selection')
        src_in = input("Path to your file (directory/file.c): ").strip()
        if not src_in:
            raise SystemExit('No file provided')
        src_path = (ROOT / src_in).resolve()
        if not src_path.exists():
            raise SystemExit(f"File not found: {src_path}")
        dest = copy_to_rendu(assignment, src_path)
        ok = build_and_run(assignment, dest)
        sys.exit(0 if ok else 1)
    else:
        print(f"{GRN}Found assignments in rendu/:{RST}")
        for i, (assignment, file_path) in enumerate(available, 1):
            print(f"  {i}. {assignment} ({file_path.name})")
        
        sel = input(f'Select assignment [1-{len(available)}]: ').strip()
        try:
            idx = int(sel) - 1
            if idx < 0 or idx >= len(available):
                raise ValueError()
            assignment, src_path = available[idx]
        except Exception:
            raise SystemExit('Invalid selection')
        
        print(f"Testing {assignment} with {src_path}")
        ok = build_and_run(assignment, src_path)
        sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(description='MiniExam04 tester shell')
    sub = ap.add_subparsers(dest='cmd')

    sp_start = sub.add_parser('start', help='Interactive start (select, copy, test)')

    sp_test = sub.add_parser('test', help='Test a specific assignment with a given file or from rendu')
    sp_test.add_argument('assignment', choices=['ft_popen', 'picoshell', 'vbc'])
    sp_test.add_argument('path', nargs='?', help='Path to directory/file.c (if omitted, uses rendu/<assignment>/*.c)')

    sp_push = sub.add_parser('push', help='Archive submission from rendu and re-test')
    sp_push.add_argument('assignment', choices=['ft_popen', 'picoshell', 'vbc'])

    args = ap.parse_args()
    if args.cmd == 'start' or args.cmd is None:
        interactive_start()
    elif args.cmd == 'test':
        if args.path:
            src_path = (ROOT / args.path).resolve()
        else:
            # pick first .c in rendu/assignment
            cand = list((ROOT / 'rendu' / args.assignment).glob('*.c'))
            if not cand:
                raise SystemExit(f"No file in rendu/{args.assignment}. Provide path explicitly.")
            src_path = cand[0]
        if not src_path.exists():
            raise SystemExit(f"File not found: {src_path}")
        ok = build_and_run(args.assignment, src_path)
        sys.exit(0 if ok else 1)
    elif args.cmd == 'push':
        # archive and then test from rendu
        archive_submission(args.assignment)
        cand = list((ROOT / 'rendu' / args.assignment).glob('*.c'))
        if not cand:
            raise SystemExit(f"No file in rendu/{args.assignment} to test after push.")
        ok = build_and_run(args.assignment, cand[0])
        sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
