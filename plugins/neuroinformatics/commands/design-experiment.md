---
description: Design and scaffold a PsychoPy neuroscience experiment
argument-hint: <experiment-description>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Experiment Design

Design and generate a PsychoPy experiment script. Load the `neuroinformatics:experiment-design` skill for reference.

## Process

### 1. Gather Requirements
From `$ARGUMENTS` and user input, determine:
- Experiment type (block, event-related, resting state)
- Stimuli types (visual, auditory, somatosensory)
- Number of conditions
- Trial structure and timing
- Response collection method
- Recording modality (EEG, EMG, fMRI, behavioral only)
- LSL marker requirements

### 2. Design Trial Structure
Present the trial structure with timing diagram for user approval.

### 3. Generate Code
Create:
- PsychoPy experiment script
- Conditions file (CSV/Excel)
- Stimuli directory structure
- LSL marker integration (if needed)
- BIDS-compatible output format

### 4. Validate Timing
Check for timing issues:
- Frame-based vs time-based durations
- Minimum stimulus duration
- Jitter distribution
- Total experiment duration
