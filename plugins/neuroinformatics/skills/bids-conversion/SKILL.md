---
name: bids-conversion
description: "Use this skill for \"convert to BIDS\", \"BIDS format\", \"create BIDS dataset\", \"BIDS sidecar\", \"participants.tsv\", \"events.tsv\", \"EEG BIDS\", \"EMG BIDS\", \"MEG BIDS\", \"fMRI BIDS\", \"BIDS validator\", \"channel locations\", \"electrode positions\", \"BIDS metadata\", or when the user wants to convert neuroscience data to Brain Imaging Data Structure (BIDS) format or validate BIDS compliance."
version: 0.1.0
---

# BIDS Conversion

Convert neuroscience datasets to Brain Imaging Data Structure (BIDS) format. Supports EEG, EMG, MEG, fMRI, and behavioral data with proper file naming, JSON sidecars, and metadata.

## When to Use

- Converting raw data files to BIDS format
- Creating or fixing BIDS metadata (JSON sidecars, TSV files)
- Validating BIDS compliance
- Setting up a new BIDS dataset from scratch
- Converting between data formats (e.g., .set to .edf, .vhdr to .bdf)

## BIDS Directory Structure

```
dataset/
  dataset_description.json
  participants.tsv
  participants.json
  README
  CHANGES
  sub-01/
    sub-01_scans.tsv
    eeg/
      sub-01_task-rest_eeg.set
      sub-01_task-rest_eeg.json
      sub-01_task-rest_channels.tsv
      sub-01_task-rest_electrodes.tsv
      sub-01_task-rest_coordsystem.json
      sub-01_task-rest_events.tsv
    emg/
      sub-01_task-grasp_emg.edf
      sub-01_task-grasp_emg.json
      sub-01_task-grasp_channels.tsv
      sub-01_task-grasp_events.tsv
    anat/
      sub-01_T1w.nii.gz
      sub-01_T1w.json
  derivatives/
    pipeline-name/
      sub-01/
```

## File Naming Convention

```
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_<suffix>.<extension>
```

- **sub**: subject identifier (required, alphanumeric, no special chars)
- **ses**: session (optional, for longitudinal studies)
- **task**: task name (required for functional data)
- **acq**: acquisition parameters (optional)
- **run**: run index (optional, for repeated acquisitions)
- **suffix**: data type (eeg, emg, meg, bold, T1w, events, channels, electrodes)

## Conversion Workflow

### Step 1: Inventory Source Data

Identify:
- Data format (BrainVision .vhdr, EEGLAB .set, EDF .edf, BDF .bdf, NIfTI .nii.gz)
- Number of subjects and sessions
- Task names and conditions
- Channel types (EEG, EMG, EOG, ECG, misc)
- Events/markers in the data
- Coordinate system for electrode positions

### Step 2: Create Dataset Scaffold

```python
import json
from pathlib import Path

def create_bids_scaffold(root: str, subjects: list[str], tasks: list[str], modality: str = "eeg"):
    root = Path(root)
    root.mkdir(exist_ok=True)

    # dataset_description.json
    desc = {
        "Name": "Dataset Name",
        "BIDSVersion": "1.9.0",
        "DatasetType": "raw",
        "License": "CC0",
        "Authors": ["Last, First"],
        "DatasetDOI": "",
        "GeneratedBy": [{"Name": "Manual conversion"}]
    }
    (root / "dataset_description.json").write_text(json.dumps(desc, indent=2))

    # participants.tsv
    with open(root / "participants.tsv", "w") as f:
        f.write("participant_id\tage\tsex\thand\n")
        for sub in subjects:
            f.write(f"sub-{sub}\tn/a\tn/a\tn/a\n")

    # Create subject directories
    for sub in subjects:
        for task in tasks:
            (root / f"sub-{sub}" / modality).mkdir(parents=True, exist_ok=True)
```

### Step 3: Convert Data Files

#### EEG (EEGLAB .set)

EEGLAB .set files are BIDS-compatible as-is. Copy and rename:
```bash
cp source.set sub-01/eeg/sub-01_task-rest_eeg.set
cp source.fdt sub-01/eeg/sub-01_task-rest_eeg.fdt  # if separate .fdt file
```

#### EEG (BrainVision .vhdr)

BrainVision files come in triplets (.vhdr, .vmrk, .eeg). All three must be renamed consistently:
```bash
cp source.vhdr sub-01/eeg/sub-01_task-rest_eeg.vhdr
cp source.vmrk sub-01/eeg/sub-01_task-rest_eeg.vmrk
cp source.eeg  sub-01/eeg/sub-01_task-rest_eeg.eeg
```
Update internal references in .vhdr and .vmrk to point to renamed files.

#### EEG (EDF/BDF)

Copy and rename:
```bash
cp source.edf sub-01/eeg/sub-01_task-rest_eeg.edf
```

#### EMG

EMG follows the same pattern but uses the `emg` directory and suffix:
```bash
cp source.edf sub-01/emg/sub-01_task-grasp_emg.edf
```

### Step 4: Create JSON Sidecars

#### EEG sidecar (required fields)

```json
{
  "TaskName": "rest",
  "TaskDescription": "Eyes-open resting state recording",
  "InstitutionName": "University Name",
  "InstitutionAddress": "Address",
  "Manufacturer": "BioSemi",
  "ManufacturersModelName": "ActiveTwo",
  "SamplingFrequency": 512,
  "EEGChannelCount": 64,
  "EOGChannelCount": 2,
  "EMGChannelCount": 0,
  "ECGChannelCount": 0,
  "MiscChannelCount": 0,
  "TriggerChannelCount": 1,
  "PowerLineFrequency": 60,
  "EEGPlacementScheme": "10-20",
  "EEGReference": "CMS/DRL",
  "EEGGround": "n/a",
  "SoftwareFilters": "n/a",
  "HardwareFilters": {"Highpass": {"HalfAmplitudeCutoffHz": 0.01}},
  "RecordingType": "continuous",
  "RecordingDuration": 300
}
```

#### EMG sidecar (required fields)

```json
{
  "TaskName": "grasp",
  "TaskDescription": "Grasping task with force measurement",
  "SamplingFrequency": 2000,
  "EMGChannelCount": 8,
  "PowerLineFrequency": 60,
  "EMGPlacementScheme": "bipolar",
  "EMGReference": "differential",
  "Manufacturer": "Delsys",
  "ManufacturersModelName": "Trigno",
  "RecordingType": "continuous"
}
```

### Step 5: Create TSV Files

#### channels.tsv

```tsv
name	type	units	sampling_frequency	status	description
Fp1	EEG	uV	512	good	Frontal pole 1
Fp2	EEG	uV	512	good	Frontal pole 2
HEOG	EOG	uV	512	good	Horizontal EOG
VEOG	EOG	uV	512	good	Vertical EOG
EMG1	EMG	uV	2000	good	First dorsal interosseous
```

#### events.tsv

```tsv
onset	duration	trial_type	value	sample
0.0	0.0	stimulus	1	0
1.5	0.5	response	2	768
3.0	0.0	stimulus	1	1536
```

#### electrodes.tsv (for EEG)

```tsv
name	x	y	z
Fp1	-0.0294	0.0839	-0.0069
Fp2	0.0303	0.0835	-0.0083
```

#### coordsystem.json

```json
{
  "EEGCoordinateSystem": "CapTrak",
  "EEGCoordinateUnits": "m",
  "EEGCoordinateSystemDescription": "Based on 10-20 system with 3D digitization"
}
```

### Step 6: Validate

```bash
# Using the official BIDS validator (Node.js CLI)
bunx bids-validator /path/to/dataset

# Or install globally
bun install -g bids-validator
bids-validator /path/to/dataset
```

## Modality-Specific Notes

Read the detailed references for modality-specific conversion guidance:
- [references/eeg-bids.md](references/eeg-bids.md) - EEG-specific BIDS requirements and common pitfalls
- [references/emg-bids.md](references/emg-bids.md) - EMG-specific BIDS requirements (BEP 038)
- [references/bids-common-errors.md](references/bids-common-errors.md) - Common validation errors and fixes
