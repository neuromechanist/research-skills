# EMG-BIDS Reference (BEP 038)

BIDS Extension Proposal 038 defines the standard for electromyography data in BIDS.

## Directory Structure

```
sub-01/
  emg/
    sub-01_task-grasp_emg.edf
    sub-01_task-grasp_emg.json
    sub-01_task-grasp_channels.tsv
    sub-01_task-grasp_events.tsv
```

## Required Sidecar Fields

| Field | Type | Description |
|-------|------|-------------|
| TaskName | string | Name of the task |
| SamplingFrequency | number | Sampling rate (typically 1000-5000 Hz) |
| PowerLineFrequency | number | 50 or 60 Hz |
| EMGChannelCount | integer | Number of EMG channels |
| EMGPlacementScheme | string | "bipolar", "monopolar", or description |

## Recommended Fields

| Field | Description |
|-------|-------------|
| Manufacturer | Device manufacturer (e.g., "Delsys", "Noraxon", "OT Bioelettronica") |
| ManufacturersModelName | Device model |
| EMGReference | Reference electrode type/location |
| MuscleNames | List of recorded muscles |
| ElectrodeType | "surface", "intramuscular", "needle" |
| InterElectrodeDistance | For bipolar recordings (mm) |
| SkinPreparation | Skin preparation procedure |

## Channel Types for EMG

| Type | Description |
|------|-------------|
| EMG | Electromyography |
| EEG | Concurrent EEG (if recorded) |
| ACC | Accelerometer |
| GYRO | Gyroscope |
| MISC | Force sensors, goniometers |
| TRIG | Trigger channels |

## channels.tsv for EMG

```tsv
name	type	units	sampling_frequency	description
EMG1	EMG	uV	2000	First dorsal interosseous - proximal
EMG2	EMG	uV	2000	First dorsal interosseous - distal
EMG3	EMG	uV	2000	Abductor pollicis brevis - proximal
EMG4	EMG	uV	2000	Abductor pollicis brevis - distal
ACC1_X	ACC	m/s^2	148	Wrist accelerometer X
ACC1_Y	ACC	m/s^2	148	Wrist accelerometer Y
ACC1_Z	ACC	m/s^2	148	Wrist accelerometer Z
Force	MISC	N	2000	Grip force transducer
```

## Common EMG Muscle Naming Convention

Use standardized muscle abbreviations:
- FDI: First Dorsal Interosseous
- APB: Abductor Pollicis Brevis
- FCR: Flexor Carpi Radialis
- ECR: Extensor Carpi Radialis
- BB: Biceps Brachii
- TB: Triceps Brachii
- TA: Tibialis Anterior
- SOL: Soleus
- GM: Gastrocnemius Medialis
- GL: Gastrocnemius Lateralis

## Conversion from Common Systems

### Delsys Trigno
- Native format: .csv or proprietary
- Channels include EMG + accelerometer
- Typical sampling: EMG at 2000 Hz, ACC at 148.15 Hz
- Convert to EDF: resample ACC to match EMG or store separately

### Noraxon
- Native format: .csv
- Multiple sensor types possible
- Convert to EDF with channel type metadata

### OT Bioelettronica
- High-density EMG (HD-EMG)
- Multiple channels per grid
- Store as single file with grid layout in channels.tsv
