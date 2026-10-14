# Task 2: extend second.py to the dictionary's new measures

You wrote second.py earlier from TASK.md (read it again; its rules still hold). docs/dictionary.json now has 10 more
measures: rate_credit_card, rate_new_auto, rate_used_auto, rate_mortgage, rate_unsecured (offered loan rates) and
free_checking, bilingual, credit_builder, payday_alternative, surcharge_free_atm (yes/no profile answers). Work
only from docs/ (dictionary.json, the call report instructions and the Profile form 4501A instructions) and the
zips. Don't look anywhere else.

Rules for the new measures:
- Rates: the files store the percent times 100. Output the percent, 2 decimals, halves up. A stored 0 means not
  offered or not reported: output null (empty), never 0. A rate under 1% or over 30% after scaling is
  implausible: output null and add a row to withheld.csv (quarter, cu_number, measure, computed_value).
- Yes/no: output true or false (lowercase), null when the account is missing or blank.
- These measures get no peers rows.

Keep everything else exactly as it is. Run the script, check the 15 FPR figures still pass, update NOTES.md with the
judgment calls for the new measures, and print a one-line summary.
