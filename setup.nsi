!define APP_NAME "Sector Eight"
!define APP_VERSION "1.0.0-Beta"
!define PUBLISHER "Arjunpride15"
!define WIKI_URL "https://github.com/Arjunpride15/sector-eight/wiki"

Name "${APP_NAME}"
OutFile "SectorEight_Setup.exe"
InstallDir "$LOCALAPPDATA\SectorEight"
RequestExecutionLevel admin
Icon "images\sector_eight.ico"

Var CurrentStep

Page custom ShowInstallerUI

Function .onInit
  StrCpy $CurrentStep "welcome"
FunctionEnd

Function ShowInstallerUI
  nsLUI::Init /headerless /width 400 /height 400 "$PLUGINSDIR\ui.html"
  
  ; Bind Javascript calls to NSIS functions
  nsLUI::Bind "OnNext" OnNextPressed
  nsLUI::Bind "OnCancel" OnCancelPressed
  nsLUI::Bind "OnFinish" OnFinishPressed
  nsLUI::Bind "OpenWiki" OpenWikiPressed

  nsLUI::Show
FunctionEnd

Function OnNextPressed
  ${If} $CurrentStep == "welcome"
    StrCpy $CurrentStep "progress"
    nsLUI::CallJS "showStep('step-progress')"
    
    ; Execute background installation routine
    Call RunInstallation
  ${ElseIf} $CurrentStep == "progress"
    StrCpy $CurrentStep "complete"
    nsLUI::CallJS "showStep('step-complete')"
  ${EndIf}
FunctionEnd

Function OnCancelPressed
  nsLUI::Close
  Quit
FunctionEnd

Function OnFinishPressed
  nsLUI::Close
  Quit
FunctionEnd

Function OpenWikiPressed
  ExecShell "open" "${WIKI_URL}"
FunctionEnd

Function RunInstallation
  ; Stage 1: Python 3.14 Check & Install (20%)
  nsLUI::CallJS "setProgress(10)"
  nsExec::ExecToStack 'winget install -e --id Python.Python.3.14 --accept-package-agreements --accept-source-agreements'
  nsLUI::CallJS "setProgress(20)"

  ; Stage 2: Git Check & Install (40%)
  nsExec::ExecToStack 'winget install --id Git.Git -e --source winget --silent --override "/VERYSILENT /NORESTART"'
  nsLUI::CallJS "setProgress(40)"

  ; Stage 3: Clone Repository (60%)
  SetOutPath "$INSTDIR"
  nsExec::ExecToStack 'git clone https://github.com/Arjunpride15/sector-eight.git "$INSTDIR"'
  nsLUI::CallJS "setProgress(60)"

  ; Stage 4: Set up Virtual Environment & Requirements (85%)
  nsExec::ExecToStack 'python -m venv "$INSTDIR\se_env"'
  nsLUI::CallJS "setProgress(75)"
  nsExec::ExecToStack '"$INSTDIR\se_env\Scripts\pip.exe" install -r "$INSTDIR\requirements.txt"'
  nsLUI::CallJS "setProgress(85)"

  ; Stage 5: Register Executables in Windows Registry (100%)
  Call RegisterApps
  nsLUI::CallJS "setProgress(100)"
FunctionEnd

Function RegisterApps
  ; Register AppUserModelIDs and Registry App Paths for Home Launcher
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\home_launcher.exe" "" "$INSTDIR\home_launcher.exe"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\home_launcher.exe" "Path" "$INSTDIR"

  ; Register AppUserModelIDs and Registry App Paths for Auth Launcher
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\auth_launcher.exe" "" "$INSTDIR\auth_launcher.exe"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\auth_launcher.exe" "Path" "$INSTDIR"

  ; Add Uninstaller details to Windows Installed Apps
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SectorEight" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SectorEight" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SectorEight" "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SectorEight" "DisplayIcon" "$INSTDIR\images\sector_eight.ico"
FunctionEnd