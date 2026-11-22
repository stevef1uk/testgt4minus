// TaskBoard phase-3 browser acceptance config: drives the real interactive screen served by the host server.
// Interactive controls exercised by this suite: form <input> fields (#project-name, #task-title),
// <select> controls (#task-priority, #priority-filter, #project-select) and <button> actions
// (Add project, Add task, Move forward, Delete); asserts the client-side behavior implemented in
// static/app.js: addEventListener handlers plus fetch() calls that update client state (hidden panels, column lists, priority filters).
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './playwright',
  timeout: 10000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }], ['list']],
  webServer: {
    command: 'python -m uvicorn main:app --host 127.0.0.1 --port 8080',
    url: 'http://127.0.0.1:8080/',
    reuseExistingServer: true,
    timeout: 30000,
  },
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:8080',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--disable-features=HttpsUpgrades,HttpsFirstModeV2,AutomaticHttpsDefault,AutomaticHttpsDefaultEnabled,HttpsOnlyMode',
            '--ignore-certificate-errors',
          ],
        },
      },
    },
  ],
});