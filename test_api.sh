#!/bin/bash
# Test script for PKI-Based 2FA Microservice

echo "=== Testing PKI-Based 2FA Microservice ==="
echo

# 1. Decrypt seed
echo "1. Testing decrypt-seed endpoint..."
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"
echo -e "\n"

# 2. Generate 2FA code
echo "2. Testing generate-2fa endpoint..."
curl http://localhost:8080/generate-2fa
echo -e "\n"

# 3. Verify valid code
echo "3. Testing verify-2fa with valid code..."
RESPONSE=$(curl -s http://localhost:8080/generate-2fa)
echo "Generated: $RESPONSE"
CODE=$(echo $RESPONSE | grep -oP '"code":"\K[^"]+')
echo "Extracted code: $CODE"
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"$CODE\"}"
echo -e "\n"

# 4. Verify invalid code
echo "4. Testing verify-2fa with invalid code..."
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "000000"}'
echo -e "\n"

# 5. Check cron output (wait 70+ seconds)
echo "5. Checking cron job output (waiting 70 seconds)..."
sleep 70
docker exec 2fa_microservice cat /cron/last_code.txt
echo -e "\n"

echo "=== Tests completed ==="
