;NSIS Modern User Interface
;Basic Example Script
;Written by Joost Verburg

;--------------------------------
;Include Modern UI

    !include "MUI2.nsh"
    !include LogicLib.nsh
;--------------------------------
;General

    ;Name and file
    Name "PLANHEAT"
    OutFile "planheat-1.0-installer-win64.exe"

    ;Default installation folder
    InstallDir "$LOCALAPPDATA\Modern UI Test"

    !define MUI_ICON "planheat_icon.ico"
    !define MUI_HEADERIMAGE
    !define MUI_HEADERIMAGE_BITMAP "..\ui\icon.png"
    !define MUI_HEADERIMAGE_RIGHT
  
    ;Get installation folder from registry if available
    ;InstallDirRegKey HKCU "Software\Modern UI Test" ""

    ;Request application privileges for Windows Vista
    RequestExecutionLevel admin ;Require admin rights on NT6+ (When UAC is turned on)

;--------------------------------
;Interface Settings

    !define MUI_ABORTWARNING

;--------------------------------
;Variables

Var QGISDIR
Var QGIS_PLUGIN_DIR
Var QGIS_PLUGIN_DIR_2
Var QGIS_PLUGIN_DIR_REL_PATH
Var QGIS_PLUGIN_DIR_REL_PATH_2

Function .onInit
	; Check admin rights
	UserInfo::GetAccountType
	pop $0
	${If} $0 != "admin" ;Require admin rights on NT4+
		MessageBox mb_iconstop "Administrator rights required!"
		SetErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
		Quit
	${EndIf}
	; Set default QGIS path
	StrCpy $QGIS_PLUGIN_DIR_REL_PATH "apps\qgis\python\plugins"
	StrCpy $QGIS_PLUGIN_DIR_REL_PATH_2 "apps\qgis-ltr\python\plugins"
	; Try QGIS 3.4
	StrCpy $QGISDIR "C:\Program Files\QGIS 3.4"
	StrCpy $QGIS_PLUGIN_DIR "$QGISDIR\$QGIS_PLUGIN_DIR_REL_PATH"
	StrCpy $QGIS_PLUGIN_DIR_2 "$QGISDIR\$QGIS_PLUGIN_DIR_REL_PATH_2"
	${IfNot} ${FileExists} "$QGIS_PLUGIN_DIR\*"
	${AndIfNot} ${FileExists} "$QGIS_PLUGIN_DIR_2\*"
		; Try QGIS 3.6
		StrCpy $QGISDIR "C:\Program Files\QGIS 3.6"
		StrCpy $QGIS_PLUGIN_DIR "$QGISDIR\$QGIS_PLUGIN_DIR_REL_PATH"
		${IfNot} ${FileExists} "$QGIS_PLUGIN_DIR\*"
			; Try QGIS 3.2
			StrCpy $QGISDIR "C:\Program Files\QGIS 3.2"
			StrCpy $QGIS_PLUGIN_DIR "$QGISDIR\$QGIS_PLUGIN_DIR_REL_PATH"
			${IfNot} ${FileExists} "$QGIS_PLUGIN_DIR\*"
				StrCpy $QGISDIR ""
				StrCpy $QGIS_PLUGIN_DIR "$QGISDIR\$QGIS_PLUGIN_DIR_REL_PATH"
			${EndIf}
		${EndIf}
	${EndIf}
	
FunctionEnd

Function LeaveDirectory
	StrCpy $QGIS_PLUGIN_DIR "$QGISDIR\$QGIS_PLUGIN_DIR_REL_PATH"
	StrCpy $QGIS_PLUGIN_DIR_2 "$QGISDIR\$QGIS_PLUGIN_DIR_REL_PATH_2"
	${IfNot} ${FileExists} "$QGIS_PLUGIN_DIR\*"
	${AndIfNot} ${FileExists} "$QGIS_PLUGIN_DIR_2\*"
		MessageBox MB_OK '"$QGISDIR" is not a correct QGIS installation directory (impossible to find the plugin directory), please set a valid one. If you do not have QGIS installed, you can download it here: https://www.qgis.org'
		Abort
	${EndIf}

    ${If} ${FileExists} "$QGIS_PLUGIN_DIR_2\*"
        StrCpy $QGIS_PLUGIN_DIR "$QGIS_PLUGIN_DIR_2"
    ${EndIf}
FunctionEnd
  
;--------------------------------
;Pages

    ;!insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\Modern UI\License.txt"
    !insertmacro MUI_PAGE_LICENSE "..\LICENCE"
    ;!insertmacro MUI_PAGE_COMPONENTS

  
	; Get QGIS directory path
	!define MUI_PAGE_HEADER_SUBTEXT "Choose the folder in which QGIS is installed (e.g. 'C:\Program Files\QGIS 3.4'). Supported versions are 3.2, 3.4, 3.6 and 3.8."
	!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "QGIS installation directory."
	!define MUI_DIRECTORYPAGE_TEXT_TOP "The installer will install the Planheat plugin for the specified QGIS version. To install in a different folder, click Browse and select another folder."
	!define MUI_DIRECTORYPAGE_VARIABLE $QGISDIR ; <= the other directory will be stored into that variable
	!define MUI_PAGE_CUSTOMFUNCTION_LEAVE LeaveDirectory
	;!define MUI_DIRECTORYPAGE_VERIFYONLEAVE
	!insertmacro MUI_PAGE_DIRECTORY
	# TODO validate that there is minimal directories in the QGIS dir (bin, apps, python, etc)
  
    !insertmacro MUI_PAGE_INSTFILES
  
    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES
  
  
  
;--------------------------------
;Languages
 
    !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections
Section "Paths settings" SEC_PATHS

    StrCpy $INSTDIR "$QGIS_PLUGIN_DIR\planheat"

    SetOutPath "$INSTDIR"
  
    ;Store installation folder
    ;WriteRegStr HKCU "C:\Program Files\QGIS 3.2" "" $INSTDIR

    ;MessageBox MB_OK 'INSTDIR = $INSTDIR is some value'

SectionEnd


Section "Files extraction" SEC_FILE_EXTRACT

    SetOutPath "$INSTDIR"
    SetOverwrite ifnewer
    File /r "..\..\planheat\*"
 
SectionEnd


Section "Installation script run" SEC_BAT_SCRIPT
    ;MessageBox MB_OK 'Launching batch setup script'
    nsExec::ExecToLog '"$INSTDIR\install\setup.bat"'
SectionEnd

Section "Create uninstaller" SEC_UNINSTALLER
    ;Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd
  

;--------------------------------
;Descriptions

    ;Language strings
    LangString DESC_SEC_PATHS ${LANG_ENGLISH} "Paths settings"
    LangString DESC_SEC_FILE_EXTRACT ${LANG_ENGLISH} "Paths settings"
    LangString DESC_SEC_BAT_SCRIPT ${LANG_ENGLISH} "Paths settings"

    ;Assign language strings to sections
    !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_PATHS} $(DESC_SEC_PATHS)
	!insertmacro MUI_DESCRIPTION_TEXT ${SEC_FILE_EXTRACT} $(DESC_SEC_FILE_EXTRACT)
	!insertmacro MUI_DESCRIPTION_TEXT ${SEC_BAT_SCRIPT} $(DESC_SEC_BAT_SCRIPT)
    !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

    ;ADD YOUR OWN FILES HERE...

    Delete "$INSTDIR\Uninstall.exe"

    RMDir "$INSTDIR"

    ${If} ${FileExists} "$%LOCALAPPDATA%\QGIS\QGIS3\planheat_data\*"
        RMDir "$%LOCALAPPDATA%\QGIS\QGIS3\planheat_data"
    ${EndIf}


    DeleteRegKey /ifempty HKCU "Software\Modern UI Test"

SectionEnd