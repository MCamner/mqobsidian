---
type: reference
system: mq-ums
status: active
tags: [reference, commands, system]
updated: 2026-06-17
links_to: [index]
---

# mq-ums Commands v2

Token-snål kommandoreferens för `mq-ums`.

> Källbas: verifierad mot `README.md` och `docs/COMMANDS.md` i `mq-ums`.

## 1. Install / Start

### `git clone https://github.com/MCamner/mq-ums.git C:\mq-ums`
**Vad det gör**
Klonar `mq-ums` till en lokal Windows-path.

**När det används**
Första gången du sätter upp projektet.

**1 exempel**
```powershell
git clone https://github.com/MCamner/mq-ums.git C:\mq-ums
```

### `cd C:\mq-ums`
**Vad det gör**
Byter till repo-roten.

**När det används**
Efter kloning eller innan install/scripts.

**1 exempel**
```powershell
cd C:\mq-ums
```

### `.\scripts\install-windows.ps1`
**Vad det gör**
Kör Windows-installationsflödet för `mq-ums`.

**När det används**
Vid första lokal installation på management host.

**1 exempel**
```powershell
.\scripts\install-windows.ps1
```

### `.\scripts\New-UmsCredential.ps1 -Path C:\mq-ums\ums.cred.xml`
**Vad det gör**
Skapar credential-fil för UMS.

**När det används**
När du behöver lagra credential säkert.

**1 exempel**
```powershell
.\scripts\New-UmsCredential.ps1 -Path C:\mq-ums\ums.cred.xml
```

### `copy .env.example .env`
**Vad det gör**
Skapar lokal `.env` från exempelmall.

**När det används**
Innan du startar appen första gången.

**1 exempel**
```powershell
copy .env.example .env
```

### `notepad .env`
**Vad det gör**
Öppnar `.env` för redigering.

**När det används**
När du behöver sätta `MQ_UMS_HOST` och `MQ_UMS_CRED_PATH`.

**1 exempel**
```powershell
notepad .env
```

### `npm start`
**Vad det gör**
Startar den lokala web UI/API-ytan.

**När det används**
När du vill använda `mq-ums` i browsern.

**1 exempel**
```powershell
npm start
```

## 2. Validation / Connectivity

### `npm run validate`
**Vad det gör**
Validerar config och setup.

**När det används**
Efter ändringar i commands/config eller inför demo/release.

**1 exempel**
```powershell
npm run validate
```

### `.\scripts\Test-PSIGEL.ps1 -UmsHost ums.example.com -CredPath C:\mq-ums\ums.cred.xml`
**Vad det gör**
Testar PSIGEL/UMS-konnektivitet.

**När det används**
När du vill verifiera att host och credentials fungerar.

**1 exempel**
```powershell
.\scripts\Test-PSIGEL.ps1 -UmsHost ums.example.com -CredPath C:\mq-ums\ums.cred.xml
```

### `.\scripts\Test-LiveUmsValidation.ps1`
**Vad det gör**
Kör live validation-flödet för de första read-only UMS-kommandona.

**När det används**
När du vill verifiera live-läge på en Windows management host.

**1 exempel**
```powershell
.\scripts\Test-LiveUmsValidation.ps1
```

### `./release-check.sh`
**Vad det gör**
Gatar release på config validation, tests och versionssynk.

**När det används**
Inför release eller PR där release readiness måste säkras.

**1 exempel**
```bash
./release-check.sh
```

## 3. Web UI Usage

### `Get-UMSStatus`
**Vad det gör**
Hämtar UMS serverstatus, version och buildinfo.

**När det används**
För att verifiera connectivity först.

**1 exempel**
```text
Command: Get-UMSStatus
Args:    {}
Confirm: not required
```

### `Get-UMSFirmware`
**Vad det gör**
Listar firmware-versioner registrerade i UMS.

**När det används**
När du vill se tillgängliga firmwareversioner eller slå upp en specifik.

**1 exempel**
```text
Command: Get-UMSFirmware
Args:    {}
Confirm: not required
```

### `Get-UMSDevice`
**Vad det gör**
Listar devices i UMS eller hämtar en specifik device.

**När det används**
När du vill slå upp device-ID eller läsa device-detaljer.

**1 exempel**
```text
Command: Get-UMSDevice
Args:    { "Id": "12345" }
Confirm: not required
```

### `Restart-UMSDevice`
**Vad det gör**
Startar om en device.

**När det används**
När du medvetet vill göra device restart.

**1 exempel**
```text
Command: Restart-UMSDevice
Args:    { "Id": "12345" }
Confirm: RUN
```

## 4. Device Commands

### `Start-UMSDevice`
**Vad det gör**
Skickar Wake-on-LAN till en device.

**När det används**
När du vill starta en device på distans.

**1 exempel**
```text
Command: Start-UMSDevice
Args:    { "Id": "12345" }
Confirm: RUN
```

### `Stop-UMSDevice`
**Vad det gör**
Stänger av en device.

**När det används**
När du behöver shutdown.

**1 exempel**
```text
Command: Stop-UMSDevice
Args:    { "Id": "12345" }
Confirm: RUN
```

### `Send-UMSDeviceSetting`
**Vad det gör**
Pushar nuvarande profilinställningar till en device direkt.

**När det används**
När en device behöver få senaste settings omedelbart.

**1 exempel**
```text
Command: Send-UMSDeviceSetting
Args:    { "Id": "12345" }
Confirm: RUN
```

### `Update-UMSDevice`
**Vad det gör**
Uppdaterar device-metadata som namn, site eller comment.

**När det används**
När du behöver ändra registrerad device-information.

**1 exempel**
```text
Command: Update-UMSDevice
Args:    { "Id": "12345", "Name": "New Name" }
Confirm: RUN
```

### `Move-UMSDevice`
**Vad det gör**
Flyttar en device till annan directory.

**När det används**
När du behöver omorganisera devices i UMS.

**1 exempel**
```text
Command: Move-UMSDevice
Args:    { "Id": "12345", "DestId": "987" }
Confirm: RUN
```

### `Remove-UMSDevice`
**Vad det gör**
Tar bort en device från UMS.

**När det används**
Bara när du medvetet vill radera en device-post.

**1 exempel**
```text
Command: Remove-UMSDevice
Args:    { "Id": "12345" }
Confirm: RUN
```

### `Reset-UMSDevice`
**Vad det gör**
Återställer en device till factory defaults.

**När det används**
Endast för avsiktlig reset.

**1 exempel**
```text
Command: Reset-UMSDevice
Args:    { "Id": "12345" }
Confirm: RUN
```

## 5. Device Directories

### `Get-UMSDeviceDirectory`
**Vad det gör**
Listar device directories.

**När det används**
När du behöver directory-ID eller struktur.

**1 exempel**
```text
Command: Get-UMSDeviceDirectory
Args:    {}
Confirm: not required
```

### `New-UMSDeviceDirectory`
**Vad det gör**
Skapar en ny device directory.

**När det används**
När du behöver lägga till struktur i UMS.

**1 exempel**
```text
Command: New-UMSDeviceDirectory
Args:    { "Name": "New Devices" }
Confirm: RUN
```

### `Update-UMSDeviceDirectory`
**Vad det gör**
Byter namn på en device directory.

**När det används**
När du vill döpa om en directory.

**1 exempel**
```text
Command: Update-UMSDeviceDirectory
Args:    { "Id": "55", "Name": "Renamed" }
Confirm: RUN
```

### `Move-UMSDeviceDirectory`
**Vad det gör**
Flyttar en device directory till annan parent.

**När det används**
När du omstrukturerar katalogträdet.

**1 exempel**
```text
Command: Move-UMSDeviceDirectory
Args:    { "Id": "55", "DestId": "10" }
Confirm: RUN
```

### `Remove-UMSDeviceDirectory`
**Vad det gör**
Tar bort en device directory.

**När det används**
Bara när directoryn är tom och ska bort.

**1 exempel**
```text
Command: Remove-UMSDeviceDirectory
Args:    { "Id": "55" }
Confirm: RUN
```

## 6. Profiles and Assignments

### `Get-UMSProfile`
**Vad det gör**
Listar profiler i UMS.

**När det används**
När du behöver profile-ID eller vill se profiler.

**1 exempel**
```text
Command: Get-UMSProfile
Args:    {}
Confirm: not required
```

### `Update-UMSProfile`
**Vad det gör**
Byter namn på en profil.

**När det används**
När du behöver rename på en profil.

**1 exempel**
```text
Command: Update-UMSProfile
Args:    { "Id": "200", "Name": "Kiosk Base" }
Confirm: RUN
```

### `Move-UMSProfile`
**Vad det gör**
Flyttar en profil till en annan profile directory.

**När det används**
När profiler ska omorganiseras.

**1 exempel**
```text
Command: Move-UMSProfile
Args:    { "Id": "200", "DestId": "12" }
Confirm: RUN
```

### `Remove-UMSProfile`
**Vad det gör**
Tar bort en profil från UMS.

**När det används**
Bara när en profil ska raderas medvetet.

**1 exempel**
```text
Command: Remove-UMSProfile
Args:    { "Id": "200" }
Confirm: RUN
```

### `Get-UMSProfileDirectory`
**Vad det gör**
Listar profile directories.

**När det används**
När du behöver katalogstruktur för profiler.

**1 exempel**
```text
Command: Get-UMSProfileDirectory
Args:    {}
Confirm: not required
```

### `New-UMSProfileAssignment`
**Vad det gör**
Tilldelar en profil till en device eller device directory.

**När det används**
När du vill applicera en profil.

**1 exempel**
```text
Command: New-UMSProfileAssignment
Args:    { "Id": "200", "ReceiverId": "12345", "ReceiverType": "tc" }
Confirm: RUN
```

### `Remove-UMSProfileAssignment`
**Vad det gör**
Tar bort en profiltilldelning från device eller directory.

**När det används**
När en profil inte längre ska vara tilldelad.

**1 exempel**
```text
Command: Remove-UMSProfileAssignment
Args:    { "Id": "200", "ReceiverId": "12345", "ReceiverType": "tc" }
Confirm: RUN
```

## 7. Environment

### `MQ_UMS_HOST`
**Vad det gör**
Sätter UMS-host.

**När det används**
Alltid för live-koppling.

**1 exempel**
```env
MQ_UMS_HOST=ums.example.com
```

### `MQ_UMS_PORT`
**Vad det gör**
Sätter UMS TCP-port.

**När det används**
När du inte kör default eller vill vara explicit.

**1 exempel**
```env
MQ_UMS_PORT=8443
```

### `MQ_UMS_CRED_PATH`
**Vad det gör**
Pekar till credential XML-filen.

**När det används**
När appen ska autentisera mot UMS.

**1 exempel**
```env
MQ_UMS_CRED_PATH=C:\mq-ums\ums.cred.xml
```

### `MQ_UMS_BIND`
**Vad det gör**
Sätter bind-adress för web UI/API.

**När det används**
När du behöver ändra från default bind.

**1 exempel**
```env
MQ_UMS_BIND=127.0.0.1
```

### `MQ_UMS_HTTP_PORT`
**Vad det gör**
Sätter HTTP-port för UI/API.

**När det används**
När du behöver annan lokal port än default.

**1 exempel**
```env
MQ_UMS_HTTP_PORT=8787
```

## 8. Fast Path

### Install
```powershell
.\scripts\install-windows.ps1
.\scripts\New-UmsCredential.ps1 -Path C:\mq-ums\ums.cred.xml
copy .env.example .env
notepad .env
```

### Start
```powershell
npm start
```

### Validate
```powershell
npm run validate
.\scripts\Test-PSIGEL.ps1 -UmsHost ums.example.com -CredPath C:\mq-ums\ums.cred.xml
```

### Read-only first
```text
Get-UMSStatus
Get-UMSFirmware
Get-UMSDevice
```

### Dangerous commands require
```text
RUN
```
