# ECE-050 – Component Tolerance Check and Batch Acceptance Engine — Sample Data Pack
Prepared by 10 SECONDS for Team E018.

This pack is the input for an incoming-inspection engine for resistors and capacitors: 15 part specs, 6 suppliers, 40 lots received in October 2026 and their sampled measurements.

Pack conventions where the brief is silent: suffixes are case-sensitive (M = 10^6, m = 10^-3, k = 10^3, u = 10^-6, n = 10^-9, p = 10^-12); a value has no unit symbol and no spaces. Anything else (two dots, letters other than one suffix, commas, text) is unparseable. If more samples than required are supplied, use the lowest sample_no values up to the required size. Decision order: HELD (too few samples) first, then WRONG_VALUE_SUSPECTED (more than half of the OUT samples deviate by more than 3 x tolerance from nominal; unparseable samples are OUT but are not 'beyond 3x'), then the count rule. Supplier score = ACCEPTED lots / all lots of that supplier in the period (HELD and SCREEN_100 count as not accepted).

## Files
| File | What it holds | Rows |
|---|---|---|
| part_specs.csv | 15 resistor / capacitor specs | 15 |
| suppliers.csv | 6 suppliers | 6 |
| lots.csv | 40 incoming lots | 40 |
| measurements.csv | Sampled measured values per lot | 1818 |
| commands.txt | Load, evaluate and scorecard commands | 6 |

## Column reference
Conventions: dates `YYYY-MM-DD`; timestamps `YYYY-MM-DD HH:MM:SS` (24h, IST, no timezone suffix); money in Rs as plain decimals (no commas, no symbol); percentages as plain numbers (12.5 = 12.5%); booleans `true`/`false`; IDs uppercase with a fixed prefix.

### part_specs.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| part_no | string | PN-Rnnn / PN-Cnnn |  | Primary key |
| part_type | string | - | R, C |  |
| nominal_value | string | number + optional suffix | e.g. 4.7k, 100n | Same notation as measurements |
| unit | string | - | ohm, F |  |
| tolerance_pct | integer | % | 1, 5, 10, 20 |  |
| description | string | - |  |  |

### suppliers.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| supplier_id | string | SUP-nn | SUP-01 … SUP-06 | Primary key |
| supplier_name | string | - |  |  |
| city | string | - |  |  |

### lots.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| lot_id | string | LOT-nnnn | unique | Numbered in received_date order |
| part_no | string | - | must exist in part_specs.csv |  |
| supplier_id | string | - | must exist in suppliers.csv |  |
| lot_size | integer | pieces |  | Decides sample size |
| received_date | date | YYYY-MM-DD | Oct 2026 |  |

### measurements.csv
| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| lot_id | string | LOT-nnnn | must exist in lots.csv |  |
| sample_no | integer | - | 1, 2, 3 … |  |
| measured_value | string | number + optional suffix | k, M, m, u, n, p | May be unparseable on purpose |

## Command file format
`commands.txt` holds one command per line as `COMMAND_NAME|arg1|arg2|...`. Commands must be processed in file order, top to bottom. Lines starting with `#` are comments and blank lines are ignored.

| Command | Arguments (in order) | Meaning |
|---|---|---|
| LOAD_SPECS | file | Load part_specs.csv |
| LOAD_SUPPLIERS | file | Load suppliers.csv |
| LOAD_LOTS | file | Load lots.csv |
| LOAD_MEASUREMENTS | file | Load measurements.csv |
| EVALUATE | (none) | Decide every lot in lot_id order |
| SCORECARD | from_date \| to_date | Supplier scorecard for lots received in the period (inclusive) |

reason is OK, COUNT, WRONG_VALUE_SUSPECTED or INSUFFICIENT_SAMPLE. flag is OK or PROBATION. score_pct has 1 decimal.

## Planted scenarios
Line numbers count the header row as line 1, so the first data row of a CSV is line 2. For commands.txt the line number is the physical line in the file (comment lines included).

- **Measured value exactly on the tolerance bound** — LOT-0012 (lots.csv line 13; measurements.csv lines 462–481): PN-R007 is 47k ±5%, bounds 44.65k–49.35k. measurements.csv line 465 = "49.35k" and line 473 = "44.65k" lie exactly on the bounds → IN. Compare with integers or fixed decimals, not floats.
- **Lot size exactly 500 and exactly 3,200** — LOT-0039 (lots.csv line 40) lot size exactly 500 → sample 20, acceptance 1 (it has exactly 1 OUT → ACCEPTED). LOT-0007 (lots.csv line 8) lot size exactly 3200 → sample 50, acceptance 3 (exactly 3 OUT → ACCEPTED).
- **Samples given in mixed forms (4700 vs 4.7k)** — LOT-0023 (lots.csv line 24; measurements.csv lines 948–997): 4.7k nominal; measurements.csv lines 950, 951, 952 give the same value as "4700", "4.7k", "0.0047M"; other rows of the pack also mix forms like 98.2n / 0.0982u.
- **OUT count exactly acceptance number + 2** — LOT-0009 (lots.csv line 10) sample 20 with 3 OUT = acceptance number + 2 → SCREEN_100; LOT-0015 (lots.csv line 16) sample 50 with 5 OUT → SCREEN_100.
- **Supplier with a single lot in the period** — SUP-06 has a single lot LOT-0022 (lots.csv line 23); its score is 0.0% or 100.0% from that one lot.

Extra traps (realistic things your validation should catch):

- **Wrong value suspected** — LOT-0037 (lots.csv line 38; measurements.csv lines 1590–1639): 6 OUT, of which 4 are 10x/100x/0.1x the nominal (beyond 3x tolerance) → more than half → REJECTED with WRONG_VALUE_SUSPECTED.
- **Exactly half beyond 3x tolerance** — LOT-0021 (lots.csv line 22; measurements.csv lines 848–927): 8 OUT, exactly 4 beyond 3x tolerance → NOT more than half, so the normal rule applies (sample 80, 8 OUT > 5 + 2 → REJECTED, reason COUNT).
- **Insufficient sample** — LOT-0014 (lots.csv line 15; measurements.csv lines 532–577): lot size 1500 needs 50 samples but only 46 are given → HELD, reason INSUFFICIENT_SAMPLE.
- **More samples than required** — LOT-0033 (lots.csv line 34; measurements.csv lines 1448–1469): 22 samples for a sample size of 20; use samples 1–20 only (pack convention), so the two OUT values in samples 21–22 do not count.
- **Unparseable strings** — LOT-0038 (lots.csv line 39; measurements.csv lines 1640–1719): line 1643 "--", line 1656 "1O0n" cannot be parsed → counted as OUT and logged (2 OUT in a sample of 80 → still ACCEPTED).
- **Supplier exactly at 80%** — SUP-03 has 5 lots with 4 ACCEPTED = 80.0% → NOT on PROBATION (below 80% is).

## What is NOT in this pack
Expected outputs are not provided for this set. Validate your engine with your own test suite against the rules in your brief (BR-01 … BR-07). A separate hidden input set with the same schema will be used at final evaluation; outputs are compared field-for-field, so follow the column formats above exactly in your own output.

## Output format expected at evaluation
Produce these files (CSV, header row, same conventions as above). Column order matters.

### lot_decisions.csv
One row per lot in lot_id order. decision is ACCEPTED, REJECTED, SCREEN_100 or HELD.

Columns in order: `lot_id`, `part_no`, `supplier_id`, `lot_size`, `sample_size`, `samples_used`, `in_count`, `out_count`, `unparseable_count`, `acceptance_no`, `decision`, `reason`

### supplier_scorecard.csv
One row per supplier in supplier_id order.

Columns in order: `supplier_id`, `lots`, `accepted`, `score_pct`, `flag`

### parse_errors.csv
One row per unparseable measured value.

Columns in order: `lot_id`, `sample_no`, `measured_value`
