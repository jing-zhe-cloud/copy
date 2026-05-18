[Setup]
AppName=键盘打字助手
AppVersion=1.0.0
AppPublisher=TypeSimulator
AppPublisherURL=https://github.com
AppContact=
DefaultDirName={autopf}\键盘打字助手
DefaultGroupName=键盘打字助手
UninstallDisplayIcon={app}\TypeSimulator.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=键盘打字助手_Setup
;SetupIconFile=TypeSimulator.ico
PrivilegesRequired=admin
AllowNoIcons=yes
LanguageDetectionMethod=uilanguage
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce

[Files]
Source: "dist\TypeSimulator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "TypeSimulator.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\键盘打字助手"; Filename: "{app}\TypeSimulator.exe"; IconFilename: "{app}\TypeSimulator.ico"
Name: "{commondesktop}\键盘打字助手"; Filename: "{app}\TypeSimulator.exe"; IconFilename: "{app}\TypeSimulator.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\TypeSimulator.exe"; Description: "立即运行 键盘打字助手"; Flags: postinstall nowait skipifsilent unchecked

[UninstallRun]
Filename: "{cmd}"; Parameters: "/c taskkill /f /im TypeSimulator.exe 2>nul"; Flags: runhidden
