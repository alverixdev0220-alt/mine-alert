"""Reminders - shows Windows notifications on a schedule.

    Drink water  -> every 2 hours
    Do exercise  -> every 1 hour

Usage:
    python reminders.py            (runs forever)
    pythonw reminders.py           (runs in background, no window)
    python reminders.py --test     (shows every alert once now)

To add or change a reminder, edit the REMINDERS list below.
"""

import argparse
import subprocess
import time
from datetime import datetime

REMINDERS = [
    {"title": "Drink water", "message": "time for a glass of water.", "hours": 2},
    {"title": "Do exercise", "message": "stand up and move for a few minutes.", "hours": 1},
]

CHECK_EVERY_SECONDS = 30

# How long an alert stays on screen if you don't click "Done".
DISPLAY_SECONDS = 3

APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"

TOAST_XML = """
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>{title}</text>
      <text>It's {time} - {message}</text>
    </binding>
  </visual>
  <actions>
    <action content="Done" arguments="dismiss" activationType="system"/>
  </actions>
  <audio src="ms-winsoundevent:Notification.Reminder"/>
</toast>
"""

# Windows toast notifications are shown through PowerShell's WinRT bridge,
# so no extra Python packages are needed.
PS_SCRIPT = """
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
$doc.LoadXml(@'
{xml}
'@)
$toast = New-Object Windows.UI.Notifications.ToastNotification $doc
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{app_id}')
$notifier.Show($toast)
Start-Sleep -Seconds {seconds}
try { $notifier.Hide($toast) } catch {}
"""


def show_alert(title, message):
    """Show an alert and hide it after DISPLAY_SECONDS. Returns without waiting."""
    xml = TOAST_XML.format(title=title, message=message, time=datetime.now().strftime("%H:%M"))
    script = (
        PS_SCRIPT.replace("{xml}", xml)
        .replace("{app_id}", APP_ID)
        .replace("{seconds}", str(DISPLAY_SECONDS))
    )
    return subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def main():
    parser = argparse.ArgumentParser(description="Reminders")
    parser.add_argument("--test", action="store_true", help="show every alert once now and exit")
    args = parser.parse_args()

    if args.test:
        alerts = [show_alert(r["title"], r["message"]) for r in REMINDERS]
        for a in alerts:
            a.wait()
        return

    # Wall-clock times, so reminders still fire correctly after the PC wakes from sleep.
    now = time.time()
    next_due = [now + r["hours"] * 3600 for r in REMINDERS]

    while True:
        time.sleep(CHECK_EVERY_SECONDS)
        now = time.time()
        for i, r in enumerate(REMINDERS):
            if now >= next_due[i]:
                show_alert(r["title"], r["message"])
                next_due[i] = now + r["hours"] * 3600


if __name__ == "__main__":
    main()
