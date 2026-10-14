# Offered loan rates against posted rates

The call report's loan rates (`ACCT_521`, `522`, `523`, `524`, `563A`) have no FPR equivalent, so they're checked
two ways: a separate plain read of the raw zip for five credit unions (the tests, `tests/test_measures.py`), and a
comparison with what the credit unions post on their own sites. The posted rate is from a later date than the
quarter end, so this is a plausibility check, not a match.

Checked 2026-10-14:

| Credit union | Call report, 2026-06 | Posted, 2026-10-14 | Reading |
|---|---|---|---|
| U.S. Eagle (808) | New and used vehicle, both 5.24% | Vehicles model year 2022-2027, 37 to 66 months, "as low as 5.24%" (https://www.useagle.org/rates/vehicle-loan-rates) | Same figure; U.S. Eagle prices by model year, not new versus used, which is why its new and used rates are equal |

Nusenda's rates page (https://www.nusenda.org/news-resources/rates-fees) fills its figures in with JavaScript and
didn't render for this check. Artesia, Deming Schools and Four Corners didn't turn up a rates page in search.
The scale (stored times 100) and the column (offered rate, most common) are confirmed by the instructions (p. 50)
and by the U.S. Eagle match.
