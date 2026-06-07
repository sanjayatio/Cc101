/**
 * Minimal .env loader for Node.js tooling (no npm required).
 *
 * Usage:
 *   const { loadEnv } = require('./env');
 *   const env = loadEnv();          // reads <project-root>/.env
 *   const key = env.GOOGLE_API_KEY;
 *
 * Rules:
 *   - Lines starting with # (after trimming) are ignored.
 *   - Blank lines are ignored.
 *   - KEY=VALUE — value is everything after the first '=', trimmed.
 *   - No quote stripping; values are returned as plain strings.
 */

'use strict';

const fs   = require('fs');
const path = require('path');

/**
 * Load the .env file relative to this script's directory.
 * @param {string} [envPath] - Optional explicit path to the .env file.
 * @returns {{ [key: string]: string }}
 */
function loadEnv(envPath) {
  const target = envPath || path.join(__dirname, '..', '.env');

  if (!fs.existsSync(target)) {
    throw new Error(`.env file not found at ${target}`);
  }

  const env = {};
  for (const raw of fs.readFileSync(target, 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    const val = line.slice(eq + 1).trim();
    env[key] = val;
  }
  return env;
}

module.exports = { loadEnv };
