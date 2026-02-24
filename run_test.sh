#!/bin/bash
# Disable exit on error so we can capture the failing test output
set +e

cd /a0/usr/projects/salon_flow

# Ensure the test points to the local development server
sed -i "s|const BASE_URL = 'https://salon-flow-owner-rgvcleapsa-el.a.run.app';|const BASE_URL = 'http://localhost:3000';|g" tests/e2e/owner.spec.ts

# Start Vite server in the background
cd apps/owner
npm run dev > /tmp/vite.log 2>&1 &
VITE_PID=$!
cd ../..

echo "Waiting for Vite server on port 3000..."
for i in {1..30}; do
  if curl -s http://localhost:3000 > /dev/null; then
    echo "Vite is up!"
    break
  fi
  sleep 1
done

echo "Running Playwright CLI..."
npx playwright test tests/e2e/owner.spec.ts -g "should load login page" --project=chromium > /tmp/pw.log 2>&1

echo "\n--- PLAYWRIGHT OUTPUT ---"
cat /tmp/pw.log

# Cleanup
kill $VITE_PID
