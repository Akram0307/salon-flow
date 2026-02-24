#!/bin/bash
./node_modules/.bin/playwright test tests/e2e/owner.spec.ts -g "should load login page" --project=chromium > /tmp/pw_out.txt 2>&1
echo "Playwright Exit Code: $?" >> /tmp/pw_out.txt
