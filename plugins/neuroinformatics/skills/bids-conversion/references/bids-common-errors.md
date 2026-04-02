# Common BIDS Validation Errors and Fixes

## Errors (Must Fix)

### DATASET_DESCRIPTION_JSON_MISSING
**Error:** `dataset_description.json` not found at dataset root.
**Fix:** Create the file:
```json
{
  "Name": "Dataset Name",
  "BIDSVersion": "1.9.0",
  "DatasetType": "raw",
  "License": "CC0",
  "Authors": ["Last, First"]
}
```

### INVALID_JSON_ENCODING
**Error:** JSON file contains non-UTF-8 characters.
**Fix:** Re-encode the file: `iconv -f ISO-8859-1 -t UTF-8 file.json > file_fixed.json`

### TSV_MISSING_HEADER
**Error:** TSV file missing required header row.
**Fix:** Add header as first line (tab-separated).

### PARTICIPANT_ID_PATTERN
**Error:** Subject directory name does not match `sub-<label>` pattern.
**Fix:** Rename to use only alphanumeric characters: `sub-01`, not `sub-01_john`.

### EVENTS_TSV_MISSING
**Error:** Functional data file has no corresponding `_events.tsv`.
**Fix:** Extract events from the data file or create manually with `onset`, `duration`, `trial_type` columns.

### SIDECAR_KEY_REQUIRED
**Error:** Required field missing from JSON sidecar.
**Fix:** Add the field. Common missing fields:
- `TaskName` (must match filename)
- `PowerLineFrequency` (50 or 60)
- `SamplingFrequency` (read from data file header)

### CHANNEL_COUNT_MISMATCH
**Error:** Channel count in sidecar does not match data file.
**Fix:** Count channels in the actual data file and update sidecar.

## Warnings (Should Fix)

### MISSING_RECOMMENDED
**Warning:** Recommended sidecar field missing.
**Fix:** Add recommended fields. Priority:
1. `InstitutionName`
2. `Manufacturer`
3. `ManufacturersModelName`
4. `EEGReference` / `EMGReference`
5. `RecordingDuration`

### NO_README
**Warning:** No README file at dataset root.
**Fix:** Create `README` (no extension) with a brief dataset description.

### NO_PARTICIPANTS_TSV
**Warning:** No `participants.tsv` at dataset root.
**Fix:**
```tsv
participant_id	age	sex	hand
sub-01	25	M	R
sub-02	30	F	R
```

### EMPTY_CELL
**Warning:** TSV file contains empty cells.
**Fix:** Replace empty cells with `n/a`.

## Tips

- Run `bids-validator` after each fix to confirm resolution
- Fix errors before warnings (errors block submission)
- Use `--json` flag for machine-readable output
- The `--ignoreNiftiHeaders` flag skips NIfTI header validation (useful during development)
- OpenNeuro requires zero errors; warnings are acceptable
