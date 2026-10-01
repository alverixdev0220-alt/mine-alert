# Drink water reminder - shows a Windows notification every 2 hours.
# Usage:
#   powershell -ExecutionPolicy Bypass -File drink-water.ps1          (runs forever)
#   powershell -ExecutionPolicy Bypass -File drink-water.ps1 -Test    (shows one alert now)

param(
    [double]$IntervalHours = 2,
    [switch]$Test
)

function Show-DrinkWaterAlert {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $time = Get-Date -Format "HH:mm"
    # scenario="reminder" keeps the toast on screen until you dismiss it
    $xml = @"
<toast scenario="reminder">
  <visual>
    <binding template="ToastGeneric">
      <text>Drink water</text>
      <text>It's $time - time for a glass of water.</text>
    </binding>
  </visual>
  <actions>
    <action content="Done" arguments="dismiss" activationType="system"/>
  </actions>
  <audio src="ms-winsoundevent:Notification.Reminder"/>
</toast>
"@

    $doc = New-Object Windows.Data.Xml.Dom.XmlDocument
    $doc.LoadXml($xml)
    $toast = New-Object Windows.UI.Notifications.ToastNotification $doc
    $appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
}

if ($Test) {
    Show-DrinkWaterAlert
    return
}

while ($true) {
    Start-Sleep -Seconds ([int]($IntervalHours * 3600))
    Show-DrinkWaterAlert
}
