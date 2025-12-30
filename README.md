# PKI-Based 2FA Microservice

A secure, containerized microservice implementing enterprise-grade authentication using **Public Key Infrastructure (PKI)** and **Time-based One-Time Passwords (TOTP)**. This project demonstrates cryptographic operations, REST API development, Docker containerization, and secure data persistence.

## 🔐 Overview

This microservice provides a complete 2FA authentication system that:
- Uses **RSA 4096-bit encryption** for secure seed transmission
- Implements **TOTP-based 2FA** (RFC 6238) for user verification
- Runs as a **containerized application** with automated cron jobs
- Ensures **data persistence** across container restarts
- Provides **three REST API endpoints** for authentication workflows

## 🚀 Features

- **RSA Cryptography**: 4096-bit key generation, RSA-OAEP decryption, RSA-PSS signatures
- **TOTP Authentication**: SHA-1 based, 6-digit codes, 30-second intervals, ±30s tolerance
- **REST API**: FastAPI-based endpoints for seed decryption, code generation, and verification
- **Docker Containerization**: Multi-stage builds, volume persistence, cron scheduling
- **Security Best Practices**: Encrypted seed transmission, secure key management, audit logging

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development/testing)
- Git
- Bash/PowerShell (for running scripts)

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│              PKI-Based 2FA Microservice                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐         ┌──────────────────┐      │
│  │ FastAPI Server  │         │  Cron Daemon     │      │
│  │ (Port 8080)     │         │  (Every Minute)  │      │
│  └────────┬────────┘         └────────┬─────────┘      │
│           │                           │                 │
│  ┌────────▼──────────────────────────▼────────┐        │
│  │   Persistent Storage (/data volume)        │        │
│  │   seed.txt (64-char hex seed)              │        │
│  └────────────────────────────────────────────┘        │
│           │                           │                 │
│  ┌────────▼────────┐         ┌───────▼──────────┐      │
│  │ API Endpoints   │         │  Audit Logs      │      │
│  │ - /decrypt-seed │         │  /cron/output    │      │
│  │ - /generate-2fa │         │  last_code.txt   │      │
│  │ - /verify-2fa   │         └──────────────────┘      │
│  └─────────────────┘                                    │
└──────────────────────────────────────────────────────────┘
```

## 🔧 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AkhileshMalthi/PKI-Based-2FA-Microservice.git
cd PKI-Based-2FA-Microservice
```

### 2. Generate RSA Key Pair

```bash
python scripts/generate_rsa_keypair.py
```

This creates:
- `student_private.pem` (4096-bit private key)
- `student_public.pem` (public key)

### 3. Request Encrypted Seed

```bash
python scripts/request_seed.py
```

This calls the instructor API with your public key and saves `encrypted_seed.txt`.

### 4. Build and Run with Docker

```bash
docker-compose up --build
```

The service will be available at `http://localhost:8080`

## 📡 API Endpoints

### 1. Decrypt Seed
```http
POST /decrypt-seed
Content-Type: application/json

{
  "encrypted_seed": "BASE64_ENCODED_SEED"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### 2. Generate 2FA Code
```http
GET /generate-2fa
```

**Response:**
```json
{
  "code": "123456",
  "valid_for": 25
}
```

### 3. Verify 2FA Code
```http
POST /verify-2fa
Content-Type: application/json

{
  "code": "123456"
}
```

**Response:**
```json
{
  "valid": true
}
```

## 🧪 Testing

### Run API Tests

```bash
bash test_api.sh
```

### Test Individual Endpoints

```bash
# Decrypt seed
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"

# Generate 2FA code
curl http://localhost:8080/generate-2fa

# Verify code
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code":"123456"}'
```

### Verify Cron Job

```bash
# Wait 70+ seconds after container start, then check logs
docker exec 2fa_microservice cat /cron/last_code.txt
```

## 🔒 Security Features

- **RSA-OAEP Encryption**: 4096-bit keys with SHA-256 hash algorithm and MGF1
- **RSA-PSS Signatures**: Digital signatures with SHA-256 and maximum salt length
- **TOTP Standard**: RFC 6238 compliant with SHA-1, 30-second periods, 6 digits
- **Secure Storage**: Persistent Docker volumes for seed and audit logs
- **UTC Timezone**: All timestamps in UTC to prevent time-based attacks
- **Time Window Tolerance**: ±30 second tolerance for clock skew

## 📁 Project Structure

```
PKI-Based-2FA-Microservice/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── crypto_utils.py      # RSA encryption/decryption
│   └── totp_utils.py        # TOTP generation/verification
├── scripts/
│   ├── generate_rsa_keypair.py   # Generate RSA keys
│   ├── request_seed.py           # Request encrypted seed
│   ├── log_2fa_cron.py           # Cron job script
│   └── generate_proof.py         # Generate commit proof
├── cron/
│   └── 2fa_cron             # Cron configuration
├── tests/
│   ├── test_decrypt.py      # Decryption tests
│   └── test_totp.py         # TOTP tests
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Container orchestration
├── requirements.txt         # Python dependencies
├── .gitattributes          # Line ending configuration
├── .gitignore              # Git exclusions
└── README.md               # This file
```

## 🛠️ Technology Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Cryptography**: PyCA cryptography library
- **TOTP**: pyotp library
- **Containerization**: Docker & Docker Compose
- **Scheduler**: Cron (system)
- **Server**: Uvicorn (ASGI)

## 📊 Key Technical Concepts

### TOTP Algorithm
```
seed (hex) → bytes → base32 → TOTP object
current_time → time_period (time // 30)
HMAC-SHA1(base32_seed, time_period) → 6-digit code
```

### RSA Encryption Flow
```
1. Instructor encrypts seed with student_public.pem
2. Student receives encrypted_seed.txt
3. API decrypts with student_private.pem
4. Seed stored at /data/seed.txt
```

### Authentication Flow
```
1. User requests code: GET /generate-2fa
2. Service generates TOTP from seed + current time
3. User submits code: POST /verify-2fa
4. Service verifies with ±1 period tolerance
5. Returns authentication result
```

## 🔄 Cron Job

The automated cron job runs every minute and logs:
```
2025-12-09 14:32:00 - 2FA Code: 123456
2025-12-09 14:33:00 - 2FA Code: 456789
```

Location: `/cron/last_code.txt`

## 📝 Environment Variables

Create a `.env` file (see `.env.example`):
```env
STUDENT_ID=your_student_id
GITHUB_REPO_URL=https://github.com/yourusername/your-repo
INSTRUCTOR_URL=https://instructor-api-url
DATA_DIR=/data
SEED_FILE=/data/seed.txt
PRIVATE_KEY_FILE=student_private.pem
```

## 🚢 Deployment

### Build Docker Image
```bash
docker-compose build
```

### Run Container
```bash
docker-compose up -d
```

### Check Container Status
```bash
docker ps
docker logs 2fa_microservice
```

### Stop Container
```bash
docker-compose down
```

## 🧩 Use Cases

1. **API Authentication**: Add 2FA to existing APIs
2. **User Login**: Enhance web application security
3. **Transaction Verification**: Confirm sensitive operations
4. **Access Control**: Secure internal systems

## 🎓 Learning Outcomes

This project demonstrates:
- Asymmetric encryption (RSA/OAEP, RSA/PSS)
- Digital signatures and PKI concepts
- TOTP authentication protocols
- Docker containerization best practices
- REST API design with FastAPI
- Cron job scheduling in containers
- Persistent storage with Docker volumes
- Secure key management
- Production deployment patterns

---

**⚠️ Security Notice**: The RSA keys in this repository are for educational purposes only. Never reuse these keys in production environments.

