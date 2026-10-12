; installer.iss - Script Inno Setup cho PhotoAI Studio
; Dong goi ung dung da build bang PyInstaller (dist\PhotoAI Studio\) thanh mot trinh
; cai dat duy nhat, va tu dong tai + cai dat digiCamControl (silent) neu may chua co -
; de nguoi dung KHONG can thuc hien buoc setup trung gian nao.

#define MyAppName "PhotoAI Studio"
; MyAppVersion duoc workflow CI truyen vao qua "ISCC.exe /DMyAppVersion=<version doc tu config.py>"
; de luon dong bo voi APP_VERSION trong app (xem .github/workflows/release.yml). #ifndef cho phep
; build thu cong (khong truyen /D) van chay duoc voi gia tri mac dinh ben duoi.
#ifndef MyAppVersion
  #define MyAppVersion "dev"
#endif
#define MyAppPublisher "Giang Bao Nguyen"
#define MyAppExeName "PhotoAI Studio.exe"
#define DigiCamUrl "https://github.com/dukus/digiCamControl/releases/download/2.0.0/digiCamControlsetup_2.0.0.0.msi"
#define DigiCamInstallPath "{commonpf32}\digiCamControl\CameraControlCmd.exe"

[Setup]
AppId={{2C69A035-7E11-4E44-8F28-44F85FD98151}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\PhotoAI Studio
DefaultGroupName=PhotoAI Studio
OutputBaseFilename=PhotoAIStudio-Setup-{#MyAppVersion}
OutputDir=Output
Compression=lzma2
SolidCompression=yes
SetupIconFile=assets\icon.ico
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "installdigicam"; Description: "Tự động tải và cài digiCamControl (bắt buộc để chụp ảnh qua USB)"; GroupDescription: "Phụ thuộc:"; Flags: checkedonce

[Files]
Source: "dist\PhotoAI Studio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PhotoAI Studio"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\PhotoAI Studio"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\digiCamControlSetup.msi"" /quiet /norestart"; \
    StatusMsg: "Đang cài digiCamControl (giúp ứng dụng chụp ảnh qua USB)..."; \
    Flags: skipifdoesntexist waituntilterminated; Check: ShouldInstallDigiCam; AfterInstall: CleanupDigiCamInstaller
Filename: "{app}\{#MyAppExeName}"; Description: "Chạy PhotoAI Studio"; Flags: nowait postinstall skipifsilent

[Code]
var
  DigiCamDownloaded: Boolean;

function IsDigiCamInstalled(): Boolean;
begin
  Result := FileExists(ExpandConstant('{#DigiCamInstallPath}'));
end;

function ShouldInstallDigiCam(): Boolean;
begin
  Result := WizardIsTaskSelected('installdigicam') and (not IsDigiCamInstalled()) and DigiCamDownloaded;
end;

procedure CleanupDigiCamInstaller();
begin
  DeleteFile(ExpandConstant('{tmp}\digiCamControlSetup.msi'));
end;

function DownloadDigiCam(): Boolean;
var
  ResultCode: Integer;
  Cmd: String;
begin
  Result := False;
  if IsDigiCamInstalled() then
  begin
    Result := True;
    Exit;
  end;
  // Dung PowerShell de tai file msi digiCamControl ve thu muc tam
  Cmd := '-NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri ''' +
    '{#DigiCamUrl}' + ''' -OutFile ''' + ExpandConstant('{tmp}\digiCamControlSetup.msi') + ''' -UseBasicParsing"';
  if Exec('powershell.exe', Cmd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0) and FileExists(ExpandConstant('{tmp}\digiCamControlSetup.msi'));
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssInstall) and WizardIsTaskSelected('installdigicam') then
  begin
    DigiCamDownloaded := DownloadDigiCam();
    if not DigiCamDownloaded then
      MsgBox('Không thể tải digiCamControl tự động (có thể do mạng). Bạn có thể cài thủ công sau tại digicamcontrol.com.', mbInformation, MB_OK);
  end;
end;
