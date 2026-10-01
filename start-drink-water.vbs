' Starts the reminders (drink water + exercise) in the background (no console window).
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
CreateObject("WScript.Shell").Run "pythonw.exe """ & scriptDir & "\reminders.py""", 0, False
