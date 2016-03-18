!ifndef VERSION
  !define VERSION 'DEV'
!endif
!addplugindir "nsisPlugins"

; The name of the installer
Name "Horus ${VERSION}"

; The file to write
OutFile "Horus_${VERSION}.exe"

; The default installation directory
InstallDir $PROGRAMFILES\Horus

; Registry key to check for directory (so if you install again, it will
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\Horus" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

; Set the LZMA compressor to reduce size.
SetCompressor /SOLID lzma
;--------------------------------

!include "MUI2.nsh"
!include Library.nsh

!define MUI_ICON "dist/res/horus.ico"
!define MUI_BGCOLOR FFFFFF

; Directory page defines
!define MUI_DIRECTORYPAGE_VERIFYONLEAVE

; Header
#!define MUI_HEADERIMAGE
#!define MUI_HEADERIMAGE_RIGHT
#!define MUI_HEADERIMAGE_BITMAP "header.bmp"
#!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH
; Don't show the component description box
!define MUI_COMPONENTSPAGE_NODESC

;Do not leave (Un)Installer page automaticly
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_UNFINISHPAGE_NOAUTOCLOSE

;Run Horus after installing
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Start Horus ${VERSION}"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"

; Pages
;!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Reserve Files
!insertmacro MUI_RESERVEFILE_LANGDLL
ReserveFile '${NSISDIR}\Plugins\InstallOptions.dll'
#ReserveFile "header.bmp"

;--------------------------------

Function .onInit

  ReadRegStr $R0 HKLM \
  "Software\Microsoft\Windows\CurrentVersion\Uninstall\Horus" \
  "UninstallString"
  StrCmp $R0 "" done

  ClearErrors
  ExecWait '$R0 _?=$INSTDIR' ;Do not copy the uninstaller to a temp file

  IfErrors no_remove_uninstaller done
    ;You can either use Delete /REBOOTOK in the uninstaller or add some code
    ;here to remove the uninstaller. Use a registry key to check
    ;whether the user has chosen to uninstall. If you are using an uninstaller
    ;components page, make sure all sections are uninstalled.
  no_remove_uninstaller:

done:

FunctionEnd

;--------------------------------

; The stuff to install
Section "Horus ${VERSION}"

  SectionIn RO

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR

  ; Put file there
  File /r "dist\"

  ; Remove ini files version
  Delete "$INSTDIR\src\horus\*.ini"

  ; Write the installation path into the registry
  WriteRegStr HKLM "SOFTWARE\Horus" "Install_Dir" "$INSTDIR"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Horus" "DisplayName" "Horus"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Horus" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Horus" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Horus" "NoRepair" 1
  WriteUninstaller "uninstall.exe"

  ; Write start menu entries for all users
  SetShellVarContext all

  CreateDirectory "$SMPROGRAMS\Horus"
  CreateShortCut "$SMPROGRAMS\Horus\Uninstall Horus.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\Horus\Horus.lnk" "$INSTDIR\python\pythonw.exe" '-m "horus"' "$INSTDIR\res\horus.ico" 0

  ; Give all users write permissions in the install directory, so they can read/write profile and preferences files.
  AccessControl::GrantOnFile "$INSTDIR" "(S-1-5-32-545)" "FullAccess"

SectionEnd

Function LaunchLink
  ; Write start menu entries for all users
  SetShellVarContext all
  ExecShell "" "$SMPROGRAMS\Horus\Horus.lnk"
FunctionEnd

Section "Install FTDI Drivers"
  ; Set output path to the driver directory.
  SetOutPath "$INSTDIR\drivers\"
  File /r "drivers\"

  ExecWait '"$INSTDIR\drivers\CDM v2.10.00 WHQL Certified.exe" /lm'
SectionEnd

Section "Install Arduino Drivers"
  ; Set output path to the driver directory.
  SetOutPath "$INSTDIR\drivers\"
  File /r "drivers\"

  ${If} ${RunningX64}
    ExecWait '"$INSTDIR\drivers\dpinst64.exe" /lm'
  ${Else}
    ExecWait '"$INSTDIR\drivers\dpinst32.exe" /lm'
  ${EndIf}
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Horus"
  DeleteRegKey HKLM "SOFTWARE\Horus"

  ; Write start menu entries for all users
  SetShellVarContext all

  ; Remove directories used
  RMDir /r "$SMPROGRAMS\Horus"
  RMDir /r "$INSTDIR"

SectionEnd
