# 🛡️ Cerber Security System

**Paranoidyczny system bezpieczeństwa mobilnego z hardware kill-switch**

> ⚠️ **STATUS: MVP Development** - System w fazie rozwojowej. Nie używaj do danych produkcyjnych.

## 🎯 Filozofia

- **Offline-First**: Core działa lokalnie bez internetu
- **Zero Trust**: Wobec operatorów, baseband, cloud providers
- **Device-Bound Keys**: Klucze NIGDY nie opuszczają Secure Element
- **Hardware Kill-Switch**: Fizyczna kontrola nad radio/modem
- **Honeypot Cloud**: Aktywne łowienie intruzów

## 📦 Komponenty

### 1. Mobile App (Kivy/Python)
- Zaszyfrowany vault (AES-256-GCM)
- Daily Password Challenge (cognitive unlock)
- Medical Journal + PHQ-9 Forms
- Sleep Audio Recording (apnea detection)
- Biometric + Voice Authentication

**Lokalizacja**: `mobile-app/`

### 2. Guardian Agent (Python)
- Heartbeat monitoring (5min intervals)
- IMSI/Baseband anomaly detection
- Quick Purge (20s hold)
- Full Purge (biometric + token)
- Forensic snapshot collection

**Lokalizacja**: `guardian-agent/`

### 3. Server (FastAPI)
- Device registration with attestation
- Heartbeat status (ACTIVE/REVOKED)
- Emergency purge reporting
- Token rotation + revocation

**Lokalizacja**: `server/`

### 4. Hardware Killbox (ESP32)
- Physical relay cutting antenna/modem power
- Mechanical bypass switch
- USB-Serial command interface
- Tamper detection (optional)

**Lokalizacja**: `hardware/`

## 🚀 Quick Start

### Mobile App (S24 Ultra)

```bash
cd mobile-app/
pip install buildozer cython==0.29.33
buildozer android debug
adb install bin/*.apk
```

### Guardian Agent (Termux/Linux)

```bash
cd guardian-agent/
pip install -r requirements.txt
export CERBER_DEVICE_ID="cerber-001"
export CERBER_SERVER_URL="https://your-server.com"
python guardian_agent.py
```

### Server (Cloud/VPS)

```bash
cd server/
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Hardware Killbox (ESP32)

```bash
cd hardware/firmware/
# Użyj Arduino IDE lub PlatformIO
# Upload killbox.ino do ESP32
# Podłącz relay do GPIO14, button do GPIO12
```

## 📋 Testing Checklist (S24 Ultra)

- [ ] APK instaluje się bez błędów
- [ ] Vault tworzy się lokalnie
- [ ] Daily Password generuje wyzwania
- [ ] Journal zapisuje wpisy
- [ ] PHQ-9 form oblicza wyniki
- [ ] Biometria działa (fingerprint/face)
- [ ] Audio recording permissions OK
- [ ] Brak crashów przy obracaniu ekranu

## 🔐 Security Architecture

```
Device (S24U)
    ├── Secure Element (Knox)
    │   └── Private Keys (Ed25519)
    ├── Local Vault (AES-256-GCM)
    ├── Guardian Agent
    └── Hardware Killbox (USB-C)
         ↓
    Gateway (Edge Router)
         ├─→ Real Cloud (auth OK)
         └─→ Fake Cloud (honeypot, no egress)
```

Więcej: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 🛠️ Development Roadmap

### Phase 1: MVP (Current)
- [x] Offline vault with encryption
- [x] Daily password system
- [x] Guardian agent skeleton
- [x] FastAPI server endpoints
- [ ] **S24 Ultra APK validation** ← YOU ARE HERE
- [ ] **SE/Knox integration proof-of-concept**

### Phase 2: Hardening
- [ ] Real destroy_key() with Knox SDK
- [ ] Hardware killbox prototype
- [ ] Attestation verification
- [ ] IMSI monitoring
- [ ] Emergency purge flow

### Phase 3: Production
- [ ] Fake cloud honeypot deployment
- [ ] Forensics pipeline
- [ ] Factory reset integration
- [ ] Penetration testing
- [ ] GDPR/HIPAA compliance

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Security Model](docs/SECURITY.md)
- [Testing Guide](docs/TESTING.md)
- [Hardware BOM](hardware/schematics/)

## 🤝 Contributing

Ten projekt jest rozwijany przez Karen Tonoyan w ramach Projekt ALFA.

**Aktualny focus**: Walidacja MVP na Samsung S24 Ultra + Knox integration R&D.

## ⚖️ License

Proprietary - Projekt ALFA © 2025

## 🆘 Support

- GitHub Issues: [Create Issue](../../issues)
- Email: contact@alfafoundation.org
- Status: Experimental - Active Development

---

**Built with paranoia. Tested with purpose. 🐕🔥**

