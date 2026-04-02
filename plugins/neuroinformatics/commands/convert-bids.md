---
description: Convert a neuroscience dataset to BIDS format
argument-hint: <source-directory> [--modality eeg|emg|meg|anat] [--task task-name]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# BIDS Conversion

Convert a raw neuroscience dataset to BIDS format. Load the `neuroinformatics:bids-conversion` skill for reference.

## Process

### 1. Analyze Source Data
!echo "Source: $ARGUMENTS"
!ls -la

Identify data files, format, number of subjects, task, and modality.

### 2. Plan Conversion
Present the conversion plan:
- Source format detected
- Number of subjects/sessions
- Target BIDS structure
- Required metadata to collect

### 3. Execute
Follow the bids-conversion skill workflow:
- Create BIDS scaffold
- Copy and rename data files
- Generate JSON sidecars
- Create TSV files (participants, channels, events, electrodes)

### 4. Validate
Run the bids-validator agent to check compliance.
