; Inno Setup 6 script for HWiNFO Panel.  Compile with:  ISCC /DAppVersion=1.0.0 packaging\setup.iss
; (build.ps1 -Installer does that after building dist\HWiNFO Panel). Output: packaging\Output\HWiNFO-Panel-Setup-<version>.exe
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
#define AppName "HWiNFO Panel"
#define AppExe "HWiNFO Panel.exe"
#define AppId "HWiNFOPanel.App"

[Setup]
; fixed GUID: identifies the app for upgrades / uninstall, never change it
AppId={{DD4FA703-DC9E-475A-9631-EBD77AE96BA9}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=AcarPlus
VersionInfoVersion={#AppVersion}
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableDirPage=auto
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
SetupIconFile=..\panel.ico
LicenseFile=..\LICENSE
OutputDir=Output
OutputBaseFilename=HWiNFO-Panel-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; close a running panel (Restart Manager); StopPanel below is the fallback
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "tr"; MessagesFile: "compiler:Languages\Turkish.isl"

[CustomMessages]
en.AutoStart=Start HWiNFO Panel when I sign in to Windows
en.NoHwinfo=HWiNFO64 was not found on this PC.%n%nHWiNFO Panel is installed, but without the scheduled tasks it runs in read-only mode (you start HWiNFO yourself). To let the panel start / stop HWiNFO without a UAC prompt, install HWiNFO64 and run this Setup again.%n%nDownload: https://www.hwinfo.com/download/%n%nOpen the download page now?
en.TasksFailed=The scheduled tasks for HWiNFO control could not be created. The panel still works in read-only mode.%n%nDetails: C:\ProgramData\HWiNFO Panel\install_tasks.log
tr.AutoStart=Windows'ta oturum açtığımda HWiNFO Panel başlasın
tr.NoHwinfo=Bu bilgisayarda HWiNFO64 bulunamadı.%n%nHWiNFO Panel kuruldu, ancak zamanlanmış görevler olmadan salt okunur modda çalışır (HWiNFO'yu siz başlatırsınız). Panelin HWiNFO'yu UAC sormadan açıp kapatabilmesi için HWiNFO64'ü kurup bu kurulumu yeniden çalıştırın.%n%nİndirme: https://www.hwinfo.com/download/%n%nİndirme sayfası şimdi açılsın mı?
tr.TasksFailed=HWiNFO denetimi için zamanlanmış görevler oluşturulamadı. Panel yine de salt okunur modda çalışır.%n%nAyrıntı: C:\ProgramData\HWiNFO Panel\install_tasks.log

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "{cm:AutoStart}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "..\dist\HWiNFO Panel\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; what the scheduled tasks run: lives under Program Files (writable by administrators only)
Source: "..\hidden.vbs"; DestDir: "{app}\tasks"; Flags: ignoreversion
Source: "..\set_interval.ps1"; DestDir: "{app}\tasks"; Flags: ignoreversion
Source: "register_tasks.ps1"; DestDir: "{app}\tasks"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"; AppUserModelID: "{#AppId}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon; AppUserModelID: "{#AppId}"

[Run]
; started as the original (non-elevated) user
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent runasoriginaluser

[UninstallRun]
; removes the scheduled tasks, %ProgramData%\HWiNFO Panel and the autostart entry; user data in %LOCALAPPDATA% is kept
Filename: "{sys}\WindowsPowerShell\v1.0\powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""{app}\tasks\register_tasks.ps1"" -Remove"; Flags: runhidden waituntilterminated; RunOnceId: "RemoveHwinfoPanelTasks"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{commonappdata}\{#AppName}"

[Code]
procedure StopPanel();
var
  rc: Integer;
begin
  // polite first (WM_CLOSE), then forced
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/im "{#AppExe}"', '', SW_HIDE, ewWaitUntilTerminated, rc);
  Sleep(1500);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/f /im "{#AppExe}"', '', SW_HIDE, ewWaitUntilTerminated, rc);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  StopPanel();
  Result := '';
end;

function InitializeUninstall(): Boolean;
begin
  StopPanel();
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Params: String;
  rc: Integer;
begin
  if CurStep <> ssPostInstall then
    Exit;
  Params := '-NoProfile -ExecutionPolicy Bypass -File "' + ExpandConstant('{app}\tasks\register_tasks.ps1') + '"' +
            ' -User "' + GetEnv('USERDOMAIN') + '\' + ExpandConstant('{username}') + '"' +
            ' -AppExe "' + ExpandConstant('{app}\{#AppExe}') + '"';
  if WizardIsTaskSelected('autostart') then
    Params := Params + ' -Autostart';
  if not Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), Params, '', SW_HIDE, ewWaitUntilTerminated, rc) then
    rc := 1;
  if rc = 3 then
  begin
    // HWiNFO64.EXE not found
    if SuppressibleMsgBox(CustomMessage('NoHwinfo'), mbInformation, MB_YESNO, IDNO) = IDYES then
      ShellExec('open', 'https://www.hwinfo.com/download/', '', '', SW_SHOWNORMAL, ewNoWait, rc);
  end
  else if rc <> 0 then
    SuppressibleMsgBox(CustomMessage('TasksFailed'), mbError, MB_OK, IDOK);
end;
