---
name: bids-validator
description: "Use this agent to autonomously validate a BIDS dataset, interpret validation errors, and suggest fixes. Triggers on \"validate BIDS\", \"check BIDS compliance\", \"BIDS errors\", \"fix BIDS warnings\", or when preparing a dataset for OpenNeuro/NEMAR submission."
version: 0.1.0
model: sonnet
tools: Bash, Read, Write, Edit, Glob, Grep
color: purple
---

# BIDS Validator Agent

Autonomously validate a BIDS dataset, interpret validation results, categorize errors by severity, and provide specific fixes for each issue.

## Procedure

### 1. Locate Dataset

Find the BIDS dataset root (contains `dataset_description.json`):
```bash
find . -name "dataset_description.json" -maxdepth 2
```

### 2. Run BIDS Validator

```bash
# Try the CLI validator first
bids-validator /path/to/dataset --json 2>/dev/null

# Fallback: Python validator
python3 -c "from bids_validator import BIDSValidator; print('available')" 2>/dev/null
```

### 3. Parse Results

Categorize findings:
- **Errors** (must fix): Missing required files, invalid naming, schema violations
- **Warnings** (should fix): Missing recommended fields, deprecated practices
- **Info** (optional): Suggestions for improvement

### 4. Diagnose Common Issues

For each error, provide the specific fix:

**MISSING_REQUIRED_FILE:**
- Check which file is missing (dataset_description.json, participants.tsv, etc.)
- Generate the file with required fields

**INVALID_FILE_NAME:**
- Show correct naming pattern
- Provide rename command

**SIDECAR_INVALID:**
- Read the JSON sidecar
- Identify missing required fields
- Add them with appropriate values

**EVENTS_TSV_MISSING:**
- Check if events are in the data file
- Extract and create events.tsv

**CHANNELS_TSV_MISSING:**
- Read channel info from data file header
- Generate channels.tsv

### 5. Apply Fixes (with confirmation)

For each fixable issue:
1. Show what will be changed
2. Apply the fix
3. Re-validate to confirm

### 6. Generate Report

```
## BIDS Validation Report

Dataset: {path}
BIDS Version: {version from dataset_description.json}

### Summary
- Subjects: N
- Sessions: N
- Modalities: eeg, emg, anat
- Total errors: N
- Total warnings: N

### Errors Fixed
1. [FIXED] Missing dataset_description.json - created with required fields
2. [FIXED] sub-01_task-rest_eeg.json missing PowerLineFrequency - added 60

### Remaining Issues
1. [WARNING] Recommended field "InstitutionName" missing in 12 sidecars
2. [INFO] Consider adding a README file

### Ready for Submission: YES/NO
```
