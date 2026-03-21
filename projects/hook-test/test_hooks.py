#!/usr/bin/env python3
"""
Hook verification test suite.
Tests that safety hooks correctly BLOCK dangerous operations.
Run from the claudeProjects root directory.

Tests are based on READING the actual hook code, not assumptions.
"""

import subprocess
import sys
import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
HOOKS_DIR = os.path.join(REPO_ROOT, ".claude/hooks")

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

passed = 0
failed = 0
errors = []


def test_hook(hook_script, tool_name, tool_input, expect_decision, description):
    """
    Test a PreToolUse hook.
    expect_decision: "block" (exit != 0), "allow" (exit 0, no output or decision=allow),
                     "ask" (decision=ask), "deny" (decision=deny)
    """
    global passed, failed, errors

    hook_path = os.path.join(HOOKS_DIR, hook_script)
    if not os.path.exists(hook_path):
        print(f"  {YELLOW}SKIP{RESET} {description} -- hook not found: {hook_script}")
        return

    hook_input_data = {
        "tool_name": tool_name,
        "tool_input": tool_input,
    }

    try:
        result = subprocess.run(
            [sys.executable, hook_path],
            input=json.dumps(hook_input_data),
            capture_output=True,
            text=True,
            timeout=10,
            cwd=REPO_ROOT,
        )

        output = result.stdout.strip()
        actual_decision = "allow"  # default

        if result.returncode != 0:
            actual_decision = "block"
        elif output:
            try:
                parsed = json.loads(output)
                d = parsed.get("hookSpecificOutput", {}).get("permissionDecision")
                if d:
                    actual_decision = d
            except json.JSONDecodeError:
                pass

        if actual_decision == expect_decision:
            print(f"  {GREEN}PASS{RESET} {description} (got {actual_decision})")
            passed += 1
        else:
            msg = f"  {RED}FAIL{RESET} {description} -- expected {expect_decision}, got {actual_decision} (exit={result.returncode})"
            print(msg)
            if result.stderr.strip():
                print(f"        stderr: {result.stderr.strip()[:120]}")
            failed += 1
            errors.append(msg)

    except subprocess.TimeoutExpired:
        print(f"  {RED}FAIL{RESET} {description} -- hook timed out")
        failed += 1
        errors.append(f"TIMEOUT: {description}")
    except Exception as e:
        print(f"  {RED}FAIL{RESET} {description} -- error: {e}")
        failed += 1
        errors.append(f"ERROR: {description}: {e}")


def main():
    print("=" * 60)
    print("HOOK VERIFICATION TEST SUITE")
    print("These tests verify hooks BLOCK what they should.")
    print("If Bash(*) is added, these hooks are the safety net.")
    print("=" * 60)

    # == main_branch_guard.py: DESTRUCTIVE OPERATIONS (all branches) ==
    print("\n== main_branch_guard.py: destructive operations ==")

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git reset --hard"},
        "block",
        "BLOCK: git reset --hard (no args)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git reset --hard HEAD~1"},
        "block",
        "BLOCK: git reset --hard HEAD~1",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git reset --hard origin/main"},
        "block",
        "BLOCK: git reset --hard origin/main",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git checkout ."},
        "block",
        "BLOCK: git checkout . (discard all changes)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git checkout -- ."},
        "block",
        "BLOCK: git checkout -- . (discard all changes)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git restore ."},
        "block",
        "BLOCK: git restore . (discard all changes)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git clean -fd"},
        "block",
        "BLOCK: git clean -fd (delete untracked files)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git clean -fxd"},
        "block",
        "BLOCK: git clean -fxd (delete untracked+ignored)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "rm -rf projects/stock-analyzer"},
        "block",
        "BLOCK: rm -rf on project directory",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "rm -rf src/"},
        "block",
        "BLOCK: rm -rf on src/",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "rm -rf /tmp/some-random-dir"},
        "block",
        "BLOCK: rm -rf on ANY directory",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "rm -rf ."},
        "block",
        "BLOCK: rm -rf . (current directory)",
    )

    # Windows equivalents
    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "rd /s /q some-folder"},
        "block",
        "BLOCK: rd /s (Windows rm -rf)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "powershell.exe -Command \"Remove-Item -Recurse -Force some-folder\""},
        "block",
        "BLOCK: Remove-Item -Recurse (PowerShell)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "del /s /q *.cs"},
        "block",
        "BLOCK: del /s (recursive Windows delete)",
    )

    # Force push on any branch
    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git push --force origin develop"},
        "block",
        "BLOCK: git push --force on develop",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git push --force origin feature/whatever"},
        "block",
        "BLOCK: git push --force on feature branch",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git push origin develop"},
        "allow",
        "ALLOW: git push (no --force)",
    )

    # SQL destructive
    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "sqlcmd -Q \"DROP TABLE data.Prices\""},
        "block",
        "BLOCK: DROP TABLE",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "sqlcmd -Q \"TRUNCATE TABLE roadtrip.Photos\""},
        "block",
        "BLOCK: TRUNCATE TABLE",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "sqlcmd -Q \"DELETE FROM data.Prices\""},
        "block",
        "BLOCK: DELETE FROM without WHERE",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "sqlcmd -Q \"DELETE FROM data.Prices WHERE SecurityAlias = 'AAPL'\""},
        "allow",
        "ALLOW: DELETE FROM with WHERE clause",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "sqlcmd -Q \"DROP DATABASE StockAnalyzer\""},
        "block",
        "BLOCK: DROP DATABASE",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git reset --soft HEAD~1"},
        "allow",
        "ALLOW: git reset --soft (not destructive)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git checkout -b feature/new-thing"},
        "allow",
        "ALLOW: git checkout -b (creating branch, not discarding)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git stash"},
        "allow",
        "ALLOW: git stash (saves work, not destructive)",
    )

    # == main_branch_guard.py: BRANCH PROTECTIONS ==
    # Blocks: commit on main, merge main (on develop), pull main,
    #         gh pr merge, push --force main, rebase main
    print("\n== main_branch_guard.py: branch protections ==")

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git merge main"},
        "block",
        "BLOCK: git merge main (reverse merge into develop)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git pull origin main"},
        "block",
        "BLOCK: git pull origin main (reverse merge)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git push --force origin main"},
        "block",
        "BLOCK: git push --force to main",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "gh pr merge 42"},
        "block",
        "BLOCK: gh pr merge (CLI merge forbidden)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git rebase main"},
        "block",
        "BLOCK: git rebase main (on develop)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git status"},
        "allow",
        "ALLOW: git status",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "git add ."},
        "allow",
        "ALLOW: git add",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "dotnet build"},
        "allow",
        "ALLOW: dotnet build (not git)",
    )

    test_hook(
        "main_branch_guard.py", "Bash",
        {"command": "ls -la"},
        "allow",
        "ALLOW: ls -la (not git)",
    )

    # == deploy_guard.py ==
    # HARD DENY: gh workflow run
    # SOFT ASK: az webapp deploy, az container create
    # ALLOW: everything else
    print("\n== deploy_guard.py ==")

    test_hook(
        "deploy_guard.py", "Bash",
        {"command": "gh workflow run deploy.yml"},
        "deny",
        "DENY: gh workflow run (hard block)",
    )

    test_hook(
        "deploy_guard.py", "Bash",
        {"command": "gh run workflow deploy"},
        "deny",
        "DENY: gh run workflow (alternate order)",
    )

    test_hook(
        "deploy_guard.py", "Bash",
        {"command": "az webapp deploy --name app-stockanalyzer"},
        "ask",
        "ASK: az webapp deploy (prompts, doesn't hard block)",
    )

    test_hook(
        "deploy_guard.py", "Bash",
        {"command": "dotnet test"},
        "allow",
        "ALLOW: dotnet test (not deployment)",
    )

    test_hook(
        "deploy_guard.py", "Bash",
        {"command": "git push origin develop"},
        "allow",
        "ALLOW: git push (not deployment)",
    )

    # == git_commit_guard.py ==
    # On feature branches: ALLOW (auto-approve)
    # On develop/main: ASK (prompt for approval)
    # Current branch is develop, so should ASK
    print("\n== git_commit_guard.py ==")

    test_hook(
        "git_commit_guard.py", "Bash",
        {"command": "git commit -m 'test message'"},
        "ask",
        "ASK: git commit on develop (requires approval)",
    )

    test_hook(
        "git_commit_guard.py", "Bash",
        {"command": "dotnet build"},
        "allow",
        "ALLOW: dotnet build (not a commit)",
    )

    test_hook(
        "git_commit_guard.py", "Bash",
        {"command": "git status"},
        "allow",
        "ALLOW: git status (not a commit)",
    )

    # == prices_scan_guard.py ==
    # Only fires on git commit commands (checks staged diff)
    # Does NOT scan arbitrary SQL commands
    print("\n== prices_scan_guard.py ==")

    test_hook(
        "prices_scan_guard.py", "Bash",
        {"command": "dotnet build"},
        "allow",
        "ALLOW: dotnet build (not a commit, hook ignores)",
    )

    test_hook(
        "prices_scan_guard.py", "Bash",
        {"command": "git commit -m 'test'"},
        "allow",
        "ALLOW: git commit with no staged Prices changes",
    )

    # == Non-Bash commands ==
    print("\n== Non-Bash commands (all hooks should ignore) ==")

    test_hook(
        "main_branch_guard.py", "Read",
        {"file_path": "/some/file"},
        "allow",
        "ALLOW: Read tool (not Bash)",
    )

    test_hook(
        "deploy_guard.py", "Edit",
        {"file_path": "/some/file", "old_string": "a", "new_string": "b"},
        "allow",
        "ALLOW: Edit tool (not Bash)",
    )

    # == Summary ==
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"RESULTS: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET} out of {total}")
    if errors:
        print(f"\n{RED}FAILURES:{RESET}")
        for e in errors:
            print(f"  {e}")
    else:
        print(f"\n{GREEN}ALL HOOKS WORKING CORRECTLY{RESET}")
        print("Safety net is solid. Bash(*) permission is safe to add.")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
