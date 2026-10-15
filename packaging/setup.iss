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
en.AskInstallHwinfo=HWiNFO64 was not found on this PC.%n%nHWiNFO (free) gives HWiNFO Panel the most data: CPU / GPU temperatures, fans, voltages, FPS. Without it the panel uses its built-in data source (usage, clocks, RAM, network, disk, NVIDIA GPU; no CPU temperatures or fans).%n%nInstall HWiNFO64 now?
en.InstallingHwinfo=Installing HWiNFO64 (winget)...
en.HwinfoInstallFailed=HWiNFO64 could not be installed automatically. The download page will open; install it and run this Setup again so the panel can start / stop HWiNFO.
en.AskEnableSM=HWiNFO64 is installed, but its "Shared Memory Support" is off, so HWiNFO Panel cannot read its sensors.%n%nTurn it on now? (If HWiNFO is running, restart it afterwards.)
en.TasksFailed=The scheduled tasks for HWiNFO control could not be created. The panel still works in read-only mode.%n%nDetails: C:\ProgramData\HWiNFO Panel\install_tasks.log
tr.AutoStart=Windows'ta oturum açtığımda HWiNFO Panel başlasın
tr.AskInstallHwinfo=Bu bilgisayarda HWiNFO64 bulunamadı.%n%nHWiNFO (ücretsiz), HWiNFO Panel'e en fazla veriyi sağlar: CPU / GPU sıcaklıkları, fanlar, voltajlar, FPS. HWiNFO olmadan panel dahili veri kaynağını kullanır (kullanım, saat hızları, RAM, ağ, disk, NVIDIA GPU; CPU sıcaklığı ve fanlar olmaz).%n%nHWiNFO64 şimdi kurulsun mu?
tr.InstallingHwinfo=HWiNFO64 kuruluyor (winget)...
tr.HwinfoInstallFailed=HWiNFO64 otomatik kurulamadı. İndirme sayfası açılacak; HWiNFO'yu kurup bu kurulumu yeniden çalıştırırsanız panel HWiNFO'yu açıp kapatabilir.
tr.AskEnableSM=HWiNFO64 kurulu ama "Shared Memory Support" (paylaşılan bellek) ayarı kapalı, bu yüzden HWiNFO Panel sensörleri okuyamaz.%n%nŞimdi açılsın mı? (HWiNFO açıksa sonrasında yeniden başlatın.)
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

function FindHwinfo(): String;
var
  s: String;
begin
  Result := '';
  if RegQueryStringValue(HKLM64, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\HWiNFO64_is1', 'InstallLocation', s) and
     FileExists(AddBackslash(s) + 'HWiNFO64.EXE') then
  begin
    Result := AddBackslash(s) + 'HWiNFO64.EXE';
    Exit;
  end;
  s := ExpandConstant('{commonpf64}\HWiNFO64\HWiNFO64.EXE');
  if FileExists(s) then begin Result := s; Exit; end;
  s := ExpandConstant('{commonpf32}\HWiNFO64\HWiNFO64.EXE');
  if FileExists(s) then begin Result := s; Exit; end;
end;

function InstallHwinfoWinget(): Boolean;
var
  winget: String;
  rc: Integer;
begin
  Result := False;
  winget := ExpandConstant('{localappdata}\Microsoft\WindowsApps\winget.exe');
  if not FileExists(winget) then
    winget := 'winget.exe';
  WizardForm.StatusLabel.Caption := CustomMessage('InstallingHwinfo');
  WizardForm.ProgressGauge.Style := npbstMarquee;
  try
    if Exec(winget, 'install --id REALiX.HWiNFO -e --silent --accept-package-agreements --accept-source-agreements --disable-interactivity',
            '', SW_HIDE, ewWaitUntilTerminated, rc) then
      Result := FindHwinfo() <> '';
  finally
    WizardForm.ProgressGauge.Style := npbstNormal;
  end;
end;

// HWiNFO Panel reads HWiNFO's sensor shared memory: make sure it is enabled
procedure EnsureSharedMemory(const exe: String; ask: Boolean);
var
  ini: String;
begin
  ini := ExtractFilePath(exe) + 'HWiNFO64.INI';
  if GetIniString('Settings', 'SensorsSM', '0', ini) = '1' then
    Exit;
  if ask and (SuppressibleMsgBox(CustomMessage('AskEnableSM'), mbConfirmation, MB_YESNO, IDYES) <> IDYES) then
    Exit;
  SetIniString('Settings', 'SensorsSM', '1', ini);
  if not ask then
  begin
    // fresh HWiNFO install: start straight in sensors-only mode without the welcome dialog
    SetIniString('Settings', 'SensorsOnly', '1', ini);
    SetIniString('Settings', 'ShowWelcomeAndProgress', '0', ini);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Params, hw: String;
  rc: Integer;
begin
  if CurStep <> ssPostInstall then
    Exit;
  hw := FindHwinfo();
  if hw = '' then
  begin
    if SuppressibleMsgBox(CustomMessage('AskInstallHwinfo'), mbConfirmation, MB_YESNO, IDYES) = IDYES then
    begin
      if InstallHwinfoWinget() then
        EnsureSharedMemory(FindHwinfo(), False)
      else
      begin
        SuppressibleMsgBox(CustomMessage('HwinfoInstallFailed'), mbInformation, MB_OK, IDOK);
        ShellExec('open', 'https://www.hwinfo.com/download/', '', '', SW_SHOWNORMAL, ewNoWait, rc);
      end;
    end;
  end
  else
    EnsureSharedMemory(hw, True);
  Params := '-NoProfile -ExecutionPolicy Bypass -File "' + ExpandConstant('{app}\tasks\register_tasks.ps1') + '"' +
            ' -User "' + GetEnv('USERDOMAIN') + '\' + ExpandConstant('{username}') + '"' +
            ' -AppExe "' + ExpandConstant('{app}\{#AppExe}') + '"';
  if WizardIsTaskSelected('autostart') then
    Params := Params + ' -Autostart';
  if not Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), Params, '', SW_HIDE, ewWaitUntilTerminated, rc) then
    rc := 1;
  // rc = 3: HWiNFO64.EXE not found -> no tasks; the panel falls back to its built-in data source
  if (rc <> 0) and (rc <> 3) then
    SuppressibleMsgBox(CustomMessage('TasksFailed'), mbError, MB_OK, IDOK);
end;
