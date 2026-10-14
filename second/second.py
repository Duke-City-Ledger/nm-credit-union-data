#!/usr/bin/env python3
"""Independent NCUA calculation. Python 3.11+, standard library only."""
import csv
import io
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent
D = Decimal
PEERS = ('net_worth_ratio', 'delinquency', 'net_charge_offs_12m',
         'commercial_share', 'cre_reset_5y', 'home_reset_5y')
SHARES = set(PEERS) - {'net_worth_ratio', 'net_charge_offs_12m'}
DIRECT = {'total_assets': '010', 'total_loans': '025B', 'members': '083'}
PARTS = {'other_gov_guaranteed': ('691P1', '691P2'), 'sba': ('691C1', '691C2')}
RATES = {'rate_credit_card': '521', 'rate_new_auto': '523', 'rate_used_auto': '524',
         'rate_mortgage': '563A', 'rate_unsecured': '522'}
YES_NO = {'free_checking': '879A4', 'bilingual': '879C1', 'credit_builder': '879D1',
          'payday_alternative': '879D9', 'surcharge_free_atm': 'PP0034'}


def rounded(value, places='0.01'):
    if value is None:
        return None
    result = value.quantize(D(places), rounding=ROUND_HALF_UP)
    return abs(result) if result == 0 else result


def ratio(numerator, denominator):
    return None if numerator is None or denominator in (None, 0) else numerator / denominator * 100


def add(*values):
    return None if None in values else sum(values, D(0))


def read_quarter(quarter, accounts):
    """Discover account locations from headers, never the dictionary's table hints."""
    roster, records = {}, {}
    with ZipFile(ROOT.parent / '.cache' / f'call-report-data-{quarter}.zip') as archive:
        names = {Path(n).name.upper(): n for n in archive.namelist()}
        def reader(name):
            # Windows-1252 retains all roster text; account cells are ASCII.
            return csv.reader(io.TextIOWrapper(archive.open(name), encoding='cp1252', newline=''))
        rows = reader(names['FOICU.TXT'])
        header = [s.strip().upper() for s in next(rows)]
        seen = set()
        for cells in rows:
            row = dict(zip(header, cells))
            cu = str(int(row['CU_NUMBER']))
            if cu in seen:
                raise ValueError(f'Duplicate roster charter: {quarter} {cu}')
            seen.add(cu)
            if row['STATE'].strip().upper() == 'NM' and row['CU_TYPE'].strip() in {'1', '2'}:
                roster[cu] = int(row['PEER_GROUP']) if row['PEER_GROUP'].strip() else None
            # Keep national history: a charter can move into NM in a later year.
            records[cu] = {}
        locations = {}
        for basename, name in sorted(names.items()):
            if not (basename.startswith('FS220') and basename.endswith('.TXT')):
                continue
            rows = reader(name)
            header = [s.strip().upper() for s in next(rows)]
            selected = [(i, key) for i, key in enumerate(header) if key in accounts]
            if not selected:
                continue
            for _, key in selected:
                if key in locations:
                    raise ValueError(f'Duplicate account column: {quarter} {key}')
                locations[key] = name
            cu_index = header.index('CU_NUMBER')
            seen = set()
            for cells in rows:
                cu = str(int(cells[cu_index]))
                if cu in seen:
                    raise ValueError(f'Duplicate table charter: {quarter} {name} {cu}')
                seen.add(cu)
                if cu not in records:
                    continue
                for i, key in selected:
                    cell = cells[i].strip()
                    value = D(cell) if cell else None
                    if value is not None and not value.is_finite():
                        raise ValueError(f'Nonfinite value: {quarter} {cu} {key}')
                    records[cu][key] = value
    return roster, records


def calculate(measure, quarter, cu, history):
    def get(q, account):
        return history.get(q, {}).get(cu, {}).get('ACCT_' + account)
    def current(account):
        return get(quarter, account)
    if measure in DIRECT:
        return current(DIRECT[measure])
    if measure in RATES:
        value = current(RATES[measure])
        if value is None or value == 0:
            return None
        return value / D(100)
    if measure in YES_NO:
        value = current(YES_NO[measure])
        if value is None:
            return None
        if value == 1:
            return 'true'
        if value == 0:
            return 'false'
        raise ValueError(f'Unexpected yes/no value: {quarter} {cu} {measure} {value}')
    if measure == 'net_worth_ratio':
        value = current('998')
        return None if value is None else value / 100
    if measure == 'delinquency':
        return ratio(current('041B'), current('025B'))
    if measure == 'commercial_share':
        return ratio(current('400T1'), current('010'))
    if measure == 'cre_reset_5y':
        return ratio(current('CM0099'), add(current('718A3'), current('718A4')))
    if measure == 'home_reset_5y':
        return ratio(current('RL0050'), current('RL0047'))
    if measure == 'net_charge_offs_12m':
        year, month = quarter.split('-')
        prior = f'{int(year)-1}-{month}'
        december = f'{int(year)-1}-12'
        def net(q):
            charge, recovery = get(q, '550'), get(q, '551')
            return None if charge is None or recovery is None else charge - recovery
        numerator = net(quarter)
        if month != '12':
            a, b = net(december), net(prior)
            numerator = None if None in (numerator, a, b) else numerator + a - b
        loans = add(current('025B'), get(prior, '025B'))
        return ratio(numerator, None if loans is None else loans / 2)
    raise ValueError(f'Unimplemented dictionary measure: {measure}')


def quantile(values, fraction):
    index = (len(values) - 1) * D(fraction)
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    return rounded(values[lower] + (values[upper] - values[lower]) * (index - lower))


def main():
    dictionary = json.loads((ROOT.parent / 'data/dictionary.json').read_text())
    measures = dictionary['measures']
    accounts = {a['account'].upper() for m in measures for a in m['accounts']}
    quarters = [f'{y}-{m:02}' for y in range(2018, 2027) for m in (3, 6, 9, 12)
                if f'{y}-{m:02}' <= '2026-06']
    history, rosters = {}, {}
    for q in ['2017-12'] + quarters:
        needed = {'ACCT_025B', 'ACCT_550', 'ACCT_551'} if q == '2017-12' else accounts
        rosters[q], history[q] = read_quarter(q, needed)
    output, withheld, peer_rows, values = [], [], [], {}
    for q in quarters:
        for cu in sorted(rosters[q], key=int):
            for definition in measures:
                measure = definition['id']
                if measure in PARTS:
                    for part, account in zip(('balance', 'guaranteed'), PARTS[measure]):
                        value = history[q][cu].get('ACCT_' + account)
                        output.append((q, cu, measure, part, rounded(value, '1')))
                    continue
                value = calculate(measure, q, cu, history)
                # Check before rounding, so 100.001 cannot silently become 100.00.
                if measure in SHARES and value is not None and not 0 <= value <= 100:
                    withheld.append((q, cu, measure, value))
                    value = None
                if measure in RATES and value is not None and not 1 <= value <= 30:
                    withheld.append((q, cu, measure, value))
                    value = None
                if definition['units'] != 'yes/no':
                    value = rounded(value, '0.01' if definition['units'] == 'percent' else '1')
                values[q, cu, measure] = value
                output.append((q, cu, measure, '', value))
        for cu in sorted(rosters[q], key=int):
            group = rosters[q][cu]
            for measure in PEERS:
                others = sorted(values[q, other, measure] for other, peer in rosters[q].items()
                                if group in range(1, 7) and peer == group and other != cu
                                and values[q, other, measure] is not None)
                stats = [quantile(others, p) for p in ('0.5', '0.25', '0.75')] if len(others) >= 5 else [None]*3
                peer_rows.append((q, cu, measure, len(others), *stats))
    expected = {'808': ('7.80', '6.91', '0.96'), '61559': ('24.76', '0.11', '0.70'),
                '66143': ('20.88', '0.00', '0.00'), '9566': ('18.34', '0.00', '0.92'),
                '62783': ('16.12', '1.08', '0.27')}
    for cu, wanted in expected.items():
        actual = tuple(str(values['2026-06', cu, m]) for m in PEERS[:3])
        if actual != wanted:
            raise AssertionError(f'2026-06 {cu}: {actual} != {wanted}')
        print(f'2026-06 {cu}: {", ".join(actual)} — PASS')
    out = ROOT / 'out'
    out.mkdir(exist_ok=True)
    for name, header, rows in [
        ('measures', 'quarter,cu_number,measure,part,value', output),
        ('peers', 'quarter,cu_number,measure,n_others,median,p25,p75', peer_rows),
        ('withheld', 'quarter,cu_number,measure,computed_value', withheld),
    ]:
        with (out / f'{name}.csv').open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(header.split(','))
            writer.writerows(rows)
    print(f'Wrote {len(output)} measure rows, {len(peer_rows)} peer rows, and {len(withheld)} withheld rows across {len(quarters)} quarters.')


if __name__ == '__main__':
    main()
