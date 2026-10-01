"""simpleC - a tiny CCleaner-style cleaner for Windows.

===============================  QUICK START  ===============================

1) Install the one dependency (only needed once):
       pip install -r requirements.txt

2) Run this file (only needed once):
       python cleaner.py

   This single run will:
     - create hotkeys.txt next to this file, with defaults:
           clean=ctrl+r
           stop=ctrl+q
     - show ONE Windows admin (UAC) prompt - click Yes. This registers a
       Scheduled Task ("SimpleCCleaner") so the listener auto-starts at
       every future logon/boot.
     - immediately start listening in this same window, right now.

3) Use it:
       Ctrl+R   -> cleans temp/cache files + empties Recycle Bin, right now
       Ctrl+Q   -> stops this listener window

   Restart your PC any time after step 2 and it is already running again
   automatically - no need to open or click anything.

To change the hotkeys: edit hotkeys.txt, save, then log off/on (or re-run
"python cleaner.py") for the new keys to take effect.

Other commands, if you ever need them:
    python cleaner.py --dry-run       # show what WOULD be deleted, deletes nothing
    python cleaner.py --status        # check whether auto-start is installed
    python cleaner.py --uninstall     # remove the automatic auto-start entirely
    python cleaner.py --install       # (re)install the auto-start task manually

What it actually cleans: user/Windows temp folders, Prefetch, the Recent
files list, thumbnail cache, Windows error reports, and Chrome/Edge/Firefox
browser caches - see TARGETS below. It also empties the Recycle Bin and
flushes the DNS cache. It never touches passwords, cookies, browsing
history or your documents, and it silently skips any file that is in use.
================================================================================
"""
import argparse
import ctypes
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

TASK_NAME = "SimpleCCleaner"
LOG_FILE = Path(os.environ.get("LOCALAPPDATA", ".")) / "simpleC" / "cleaner.log"
HOTKEY_FILE = Path(__file__).resolve().with_name("hotkeys.txt")
DEFAULT_HOTKEYS = {"clean": "ctrl+r", "stop": "ctrl+q"}

LOCAL = Path(os.environ.get("LOCALAPPDATA", ""))
ROAMING = Path(os.environ.get("APPDATA", ""))
WINDIR = Path(os.environ.get("SystemRoot", r"C:\Windows"))

# Each target: name -> list of folders whose CONTENTS are deleted.
# Only caches / temp / traces. No passwords, cookies, history or documents.
TARGETS = {
    "User temp": [Path(os.environ.get("TEMP", ""))],
    "Windows temp": [WINDIR / "Temp"],
    "Prefetch": [WINDIR / "Prefetch"],
    "Recent files list": [ROAMING / "Microsoft/Windows/Recent"],
    "Thumbnail cache": [LOCAL / "Microsoft/Windows/Explorer"],
    "Windows error reports": [LOCAL / "Microsoft/Windows/WER",
                              Path(os.environ.get("ProgramData", "")) / "Microsoft/Windows/WER"],
    "Chrome cache": [LOCAL / "Google/Chrome/User Data/Default/Cache",
                     LOCAL / "Google/Chrome/User Data/Default/Code Cache"],
    "Edge cache": [LOCAL / "Microsoft/Edge/User Data/Default/Cache",
                   LOCAL / "Microsoft/Edge/User Data/Default/Code Cache"],
    "Firefox cache": [p / "cache2" for p in (LOCAL / "Mozilla/Firefox/Profiles").glob("*")],
}


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def clean_folder(folder: Path, dry_run: bool) -> int:
    """Delete everything inside folder (not the folder itself). Returns bytes freed."""
    freed = 0
    if not folder.is_dir():
        return 0
    for item in folder.iterdir():
        try:
            if item.is_symlink() or item.is_file():
                size = item.lstat().st_size
                if not dry_run:
                    item.unlink()
                freed += size
            elif item.is_dir():
                size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                if not dry_run:
                    shutil.rmtree(item)
                freed += size
        except (PermissionError, OSError):
            pass  # file in use or protected: skip it
    return freed


def empty_recycle_bin(dry_run: bool) -> None:
    if dry_run:
        return
    # flags: no confirmation, no progress UI, no sound
    ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x1 | 0x2 | 0x4)


def flush_dns(dry_run: bool) -> None:
    if not dry_run:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)


def run_clean(dry_run: bool) -> None:
    total = 0
    for name, folders in TARGETS.items():
        freed = sum(clean_folder(f, dry_run) for f in folders)
        total += freed
        logging.info("%-22s %8.1f MB", name, freed / 1024 / 1024)
    empty_recycle_bin(dry_run)
    flush_dns(dry_run)
    verb = "Would free" if dry_run else "Freed"
    logging.info("%s %.1f MB total%s", verb, total / 1024 / 1024,
                 "" if is_admin() else "  (not admin: system folders skipped)")


def run_command() -> str:
    """Command line the scheduled task executes (no console window)."""
    exe = Path(sys.executable)
    pythonw = exe.with_name("pythonw.exe")
    interpreter = pythonw if pythonw.exists() else exe
    return f'"{interpreter}" "{Path(__file__).resolve()}" --hotkey'


def install(exit_after: bool = True) -> None:
    # Starts the hotkey listener at every logon (= after every boot/restart),
    # with highest privileges so it can also clean Windows\Temp and Prefetch,
    # and so it can see keystrokes typed in elevated windows.
    if not is_admin():
        # Re-launch this same command elevated (triggers the UAC prompt once),
        # then let the elevated copy do the actual schtasks /Create.
        params = " ".join(f'"{a}"' for a in sys.argv[1:]) or "--install"
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{Path(__file__).resolve()}" {params}', None, 1)
        if exit_after:
            sys.exit(0)
        return
    result = subprocess.run(
        ["schtasks", "/Create", "/F", "/TN", TASK_NAME, "/TR", run_command(),
         "/SC", "ONLOGON", "/RL", "HIGHEST"],
        capture_output=True, text=True)
    print(result.stdout or result.stderr)
    if exit_after:
        sys.exit(result.returncode)


def uninstall() -> None:
    result = subprocess.run(["schtasks", "/Delete", "/F", "/TN", TASK_NAME],
                            capture_output=True, text=True)
    print(result.stdout or result.stderr)
    sys.exit(result.returncode)


def status() -> None:
    result = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME],
                            capture_output=True, text=True)
    print(result.stdout if result.returncode == 0 else "Auto-run is NOT installed.")


def is_installed() -> bool:
    result = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME],
                            capture_output=True, text=True)
    return result.returncode == 0


def load_hotkeys() -> dict:
    """Read hotkeys.txt (key=value lines). Created with defaults if missing."""
    if not HOTKEY_FILE.exists():
        HOTKEY_FILE.write_text(
            "# simpleC hotkeys - edit and save, then restart for changes to apply\n"
            f"clean={DEFAULT_HOTKEYS['clean']}\n"
            f"stop={DEFAULT_HOTKEYS['stop']}\n",
            encoding="utf-8")
    keys = dict(DEFAULT_HOTKEYS)
    for line in HOTKEY_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        name, value = name.strip().lower(), value.strip().lower()
        if name in keys and value:
            keys[name] = value
    return keys


def setup_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    handlers = [logging.FileHandler(LOG_FILE, encoding="utf-8")]
    if sys.stdout:  # pythonw has no stdout
        handlers.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", handlers=handlers)


def run_hotkey_listener() -> None:
    import keyboard  # pip install keyboard

    keys = load_hotkeys()
    logging.info("Hotkey listener started. %s = clean, %s = stop listener.",
                 keys["clean"], keys["stop"])
    keyboard.add_hotkey(keys["clean"], lambda: run_clean(dry_run=False))
    keyboard.add_hotkey(keys["stop"], lambda: os._exit(0))
    keyboard.wait()  # blocks until the stop hotkey calls os._exit


def main() -> None:
    ap = argparse.ArgumentParser(description="Simple Windows cleaner")
    ap.add_argument("--dry-run", action="store_true", help="only report, delete nothing")
    ap.add_argument("--install", action="store_true", help="(re)install the auto-run task")
    ap.add_argument("--uninstall", action="store_true", help="remove auto-run entirely")
    ap.add_argument("--status", action="store_true", help="show auto-run state")
    ap.add_argument("--hotkey", action="store_true", help="internal: used by the scheduled task")
    args = ap.parse_args()

    if args.uninstall:
        uninstall()
    elif args.status:
        status()
        return
    elif args.install:
        install()
    elif args.dry_run:
        setup_logging()
        run_clean(dry_run=True)
    elif args.hotkey:
        # Launched by the scheduled task at logon.
        setup_logging()
        run_hotkey_listener()
    else:
        # Plain "python cleaner.py": install once if needed, then start
        # listening right away - no restart required to begin using it.
        setup_logging()
        if not is_installed():
            print("First run: installing auto-start (admin prompt may appear)...")
            install(exit_after=False)
        print(f"Running. {load_hotkeys()['clean']} = clean now, "
              f"{load_hotkeys()['stop']} = stop this window.")
        run_hotkey_listener()


if __name__ == "__main__":
    main()
