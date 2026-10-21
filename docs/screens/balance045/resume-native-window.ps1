$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class Balance045Window {
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd,int nCmdShow);
 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd,IntPtr hWndInsertAfter,int X,int Y,int cx,int cy,uint uFlags);
}
'@
$p=Get-Process -Id 24736
if($p.Path -ne 'C:\Users\momoy\Projects\Catchline-ui041-sim\Builds\Tier033\Catchline.exe'){throw 'Wrong process'}
[Balance045Window]::ShowWindow($p.MainWindowHandle,4) | Out-Null
[Balance045Window]::SetWindowPos($p.MainWindowHandle,[IntPtr]1,0,0,0,0,0x13) | Out-Null
Write-Output 'Resumed own capture window without activation, behind other windows.'
