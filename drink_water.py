"""Drink water reminder - shows a Windows notification every 2 hours.

Usage:
    python drink_water.py                 (runs forever, alert every 2 hours)
    python drink_water.py --test          (shows one alert now)
    python drink_water.py --hours 1.5     (custom interval)
    pythonw drink_water.py                (runs in background, no window)
"""

import argparse
import subprocess
import time
from datetime import datetime

APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"

TOAST_XML = """
<toast scenario="reminder">
  <visual>
    <binding template="ToastGeneric">
      <text>Drink water</text>
      <text>It's {time} - time for a glass of water.</text>
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
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{app_id}').Show($toast)
"""


def show_drink_water_alert():
    xml = TOAST_XML.format(time=datetime.now().strftime("%H:%M"))
    script = PS_SCRIPT.replace("{xml}", xml).replace("{app_id}", APP_ID)
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(description="Drink water reminder")
    parser.add_argument("--hours", type=float, default=2, help="interval in hours (default 2)")
    parser.add_argument("--test", action="store_true", help="show one alert now and exit")
    args = parser.parse_args()

    if args.test:
        show_drink_water_alert()
        return

    while True:
        time.sleep(args.hours * 3600)
        show_drink_water_alert()


if __name__ == "__main__":
    main()
