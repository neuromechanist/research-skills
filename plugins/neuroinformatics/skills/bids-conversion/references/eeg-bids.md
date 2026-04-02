# EEG-BIDS Reference

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| BrainVision | .vhdr, .vmrk, .eeg | Triplet files, must rename all three |
| EEGLAB | .set, .fdt | BIDS-compatible as-is |
| European Data Format | .edf | Standard format |
| BioSemi Data Format | .bdf | 24-bit variant of EDF |
| Neuroscan | .cnt | Convert to EDF first |

## Required Sidecar Fields

| Field | Type | Description |
|-------|------|-------------|
| TaskName | string | Name of the task |
| SamplingFrequency | number | Sampling rate in Hz |
| PowerLineFrequency | number | 50 or 60 Hz |
| EEGReference | string | Reference electrode (e.g., "Cz", "average", "CMS/DRL") |
| EEGChannelCount | integer | Number of EEG channels |
| EOGChannelCount | integer | Number of EOG channels |
| ECGChannelCount | integer | Number of ECG channels |
| EMGChannelCount | integer | Number of EMG channels |
| MiscChannelCount | integer | Number of misc channels |
| TriggerChannelCount | integer | Number of trigger channels |

## Recommended Sidecar Fields

| Field | Description |
|-------|-------------|
| InstitutionName | Name of institution |
| Manufacturer | Device manufacturer |
| ManufacturersModelName | Device model |
| EEGPlacementScheme | "10-20", "10-10", "10-5", "custom" |
| EEGGround | Ground electrode location |
| SoftwareFilters | Online filters applied during recording |
| HardwareFilters | Hardware filter settings |
| RecordingType | "continuous" or "epoched" |
| RecordingDuration | Total duration in seconds |
| SubjectArtefactDescription | Free text description of artifacts |

## Channel Types

| BIDS Type | Description |
|-----------|-------------|
| EEG | Electroencephalography |
| EOG | Electrooculography |
| ECG | Electrocardiography |
| EMG | Electromyography |
| MISC | Miscellaneous (accelerometer, temperature, etc.) |
| TRIG | Trigger/event channel |
| STIM | Stimulus channel |
| REF | Reference electrode |

## Common Coordinate Systems

| System | Description | Use Case |
|--------|-------------|----------|
| CapTrak | Digitized cap coordinates | Standard EEG caps |
| EEGLAB | EEGLAB channel location format | EEGLAB datasets |
| CTF | CTF MEG coordinates | CTF systems |
| Other | Custom or non-standard | Document thoroughly |

## BrainVision Header Update

When renaming BrainVision files, update internal references:

```python
def update_brainvision_header(vhdr_path: str, new_basename: str):
    """Update internal file references in .vhdr and .vmrk files."""
    import re

    # Update .vhdr
    with open(vhdr_path) as f:
        content = f.read()

    content = re.sub(
        r'DataFile=.*',
        f'DataFile={new_basename}.eeg',
        content,
    )
    content = re.sub(
        r'MarkerFile=.*',
        f'MarkerFile={new_basename}.vmrk',
        content,
    )

    with open(vhdr_path, 'w') as f:
        f.write(content)

    # Update .vmrk
    vmrk_path = vhdr_path.replace('.vhdr', '.vmrk')
    with open(vmrk_path) as f:
        content = f.read()

    content = re.sub(
        r'DataFile=.*',
        f'DataFile={new_basename}.eeg',
        content,
    )

    with open(vmrk_path, 'w') as f:
        f.write(content)
```
