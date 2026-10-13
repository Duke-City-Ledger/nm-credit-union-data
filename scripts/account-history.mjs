#!/usr/bin/env node
/**
 * Account history: how every account the page uses has been described and
 * carried, quarter by quarter, in NCUA's call report data.
 *
 * NCUA renumbers, adds and rewords accounts between form revisions, and its
 * dictionary (AcctDesc.txt) ships fresh in every quarter's zip. This reads the
 * dictionary and the table headers from each quarter since 2017-12 and writes:
 *
 *   data/account-history.json   per account: the quarters it exists in, the
 *                               table that carries it, and each distinct
 *                               description with the quarters it was used
 *   docs/account-history.md     the same, for a person to read, with every
 *                               description change called out
 *
 * A person reads every change and decides whether the meaning changed. This
 * script only finds them.
 *
 * Usage: node scripts/account-history.mjs [--from 2017-12] [--to 2026-06]
 * Zips are cached in .cache/ (gitignored), about 8 MB each.
 */

import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CACHE = join(ROOT, '.cache');
const URL_BASE = 'https://ncua.gov/files/publications/analysis/call-report-data-';

/** The accounts the page uses, plus their neighbors worth watching. */
export const ACCOUNTS = [
  'ACCT_010', 'ACCT_025B', 'ACCT_997', 'ACCT_998', 'ACCT_041B', 'ACCT_550', 'ACCT_551',
  'ACCT_400T1', 'ACCT_718A3', 'ACCT_718A4', 'ACCT_CM0099', 'ACCT_RL0047', 'ACCT_RL0050',
  'ACCT_691P1', 'ACCT_691P2', 'ACCT_691C1', 'ACCT_691C2', 'ACCT_712', 'ACCT_083',
];

function arg(name, fallback) {
  const i = process.argv.indexOf(name);
  return i > -1 ? process.argv[i + 1] : fallback;
}

export function quarters(from, to) {
  const out = [];
  let [y, m] = from.split('-').map(Number);
  for (;;) {
    const q = `${y}-${String(m).padStart(2, '0')}`;
    if (q > to) break;
    out.push(q);
    m += 3;
    if (m > 12) { m -= 12; y += 1; }
  }
  return out;
}

function zipFor(q) {
  mkdirSync(CACHE, { recursive: true });
  const path = join(CACHE, `call-report-data-${q}.zip`);
  if (!existsSync(path)) {
    execFileSync('curl', ['-sSfL', '--retry', '3', '-o', path, `${URL_BASE}${q}.zip`]);
  }
  return path;
}

function listZip(path) {
  return execFileSync('unzip', ['-Z1', path], { encoding: 'utf8' }).split('\n').filter(Boolean);
}

function readFromZip(path, name) {
  return execFileSync('unzip', ['-p', path, name], { encoding: 'latin1', maxBuffer: 1 << 30 });
}

/** Minimal CSV line parser: NCUA quotes every field and doubles embedded quotes. */
export function parseLine(line) {
  const out = [];
  let cur = '';
  let quoted = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (quoted) {
      if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (c === '"') quoted = false;
      else cur += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { out.push(cur); cur = ''; }
    else cur += c;
  }
  out.push(cur);
  return out;
}

const norm = (s) => s.replace(/\s+/g, ' ').trim();

function readQuarter(q) {
  const zip = zipFor(q);
  const names = listZip(zip);
  // Not Acct-DescGrants.txt or Acct-DescTradeNames.txt, which ship alongside it.
  const dictName = names.find((n) => /^acctdesc\.txt$/i.test(n));
  if (!dictName) throw new Error(`${q}: no AcctDesc file in zip (${names.join(', ')})`);

  const dict = new Map();
  const lines = readFromZip(zip, dictName).split(/\r?\n/).filter(Boolean);
  const head = parseLine(lines[0]).map((h) => h.toLowerCase());
  const iCode = head.findIndex((h) => h.includes('account'));
  const iName = head.findIndex((h) => h.includes('name'));
  const iDesc = head.findIndex((h) => h.includes('desc'));
  const iTable = head.findIndex((h) => h.includes('table'));
  for (const line of lines.slice(1)) {
    const f = parseLine(line);
    const code = f[iCode >= 0 ? iCode : 0]?.toUpperCase();
    if (!code) continue;
    dict.set(code, {
      name: norm(f[iName >= 0 ? iName : 1] ?? ''),
      description: norm(f[iDesc >= 0 ? iDesc : 2] ?? ''),
      table: f[iTable >= 0 ? iTable : 3] ?? '',
    });
  }

  // Which data file actually carries each account this quarter.
  const carriedBy = new Map();
  for (const n of names.filter((n) => /\.txt$/i.test(n) && !/acct-?desc/i.test(n))) {
    const first = readFromZip(zip, n).split(/\r?\n/, 1)[0];
    for (const col of parseLine(first)) carriedBy.set(col.toUpperCase(), n);
  }
  return { dict, carriedBy };
}

function main() {
  const from = arg('--from', '2017-12');
  const to = arg('--to', '2026-06');
  const qs = quarters(from, to);
  const history = Object.fromEntries(ACCOUNTS.map((a) => [a, { quarters: [], tables: {}, descriptions: [] }]));

  for (const q of qs) {
    process.stderr.write(`${q} `);
    const { dict, carriedBy } = readQuarter(q);
    for (const a of ACCOUNTS) {
      const h = history[a];
      const d = dict.get(a);
      const file = carriedBy.get(a);
      if (!d && !file) continue;
      h.quarters.push(q);
      if (file) (h.tables[file] ??= []).push(q);
      const text = d ? `${d.name} | ${d.description}` : '(in data, not in dictionary)';
      const last = h.descriptions.at(-1);
      if (last && last.text === text) last.to = q;
      else h.descriptions.push({ text, from: q, to: q, inDictionary: Boolean(d), inData: Boolean(file) });
    }
  }
  process.stderr.write('\n');

  mkdirSync(join(ROOT, 'data'), { recursive: true });
  writeFileSync(join(ROOT, 'data/account-history.json'), `${JSON.stringify({ from, to, accounts: history }, null, 2)}\n`);

  const md = [`# Account history, ${from} to ${to}`, '',
    'Generated by `scripts/account-history.mjs`. Every description change below needs a person to say whether the',
    'meaning changed (a break in the series) or only the wording.', ''];
  for (const [a, h] of Object.entries(history)) {
    const missing = qs.filter((q) => !h.quarters.includes(q));
    md.push(`## ${a}`, '');
    md.push(`- In ${h.quarters.length} of ${qs.length} quarters${missing.length ? `; missing ${summarize(missing)}` : ''}.`);
    for (const [file, list] of Object.entries(h.tables)) md.push(`- Carried in \`${file}\`: ${summarize(list)}.`);
    md.push(`- ${h.descriptions.length === 1 ? 'One description throughout' : `**${h.descriptions.length} descriptions**`}:`);
    for (const d of h.descriptions) md.push(`  - ${d.from} to ${d.to}: ${d.text}`);
    md.push('');
  }
  mkdirSync(join(ROOT, 'docs'), { recursive: true });
  writeFileSync(join(ROOT, 'docs/account-history.md'), `${md.join('\n')}\n`);
}

/** "2017-12 to 2019-06, 2020-03" from a sorted list of quarters. */
function summarize(list) {
  if (!list.length) return 'none';
  const runs = [];
  let start = list[0];
  let prev = list[0];
  for (const q of list.slice(1)) {
    if (quarters(prev, q).length === 2) { prev = q; continue; }
    runs.push(start === prev ? start : `${start} to ${prev}`);
    start = prev = q;
  }
  runs.push(start === prev ? start : `${start} to ${prev}`);
  return runs.join(', ');
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main();
