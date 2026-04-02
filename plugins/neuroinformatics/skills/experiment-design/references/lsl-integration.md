# Lab Streaming Layer (LSL) Integration

## Overview

Lab Streaming Layer (LSL) provides a unified system for streaming time-series data and event markers across devices and applications on a local network.

## Installation

```bash
# Python bindings
uv add pylsl

# Or system-wide
pip install pylsl
```

## Sending Markers from PsychoPy

### Setup

```python
from pylsl import StreamInfo, StreamOutlet

# Create marker stream
marker_info = StreamInfo(
    name="PsychoPyMarkers",
    type="Markers",
    channel_count=1,
    nominal_srate=0,  # Irregular rate (event-based)
    channel_format="string",
    source_id="psychopy_experiment_001",
)

# Add metadata
desc = marker_info.desc()
desc.append_child_value("experiment", "task_name")
desc.append_child_value("version", "1.0")

marker_outlet = StreamOutlet(marker_info)
```

### Sending Markers

```python
# String markers
marker_outlet.push_sample(["stimulus_onset"])
marker_outlet.push_sample(["response_left"])

# With timestamp (for precise timing)
from pylsl import local_clock
timestamp = local_clock()
marker_outlet.push_sample(["stimulus_onset"], timestamp)
```

### Marker Timing

Send markers immediately after `win.flip()` for best timing:
```python
stimulus.draw()
flip_time = win.flip()  # Returns time of flip
marker_outlet.push_sample(["stimulus_onset"])
# The LSL timestamp is captured at push_sample() call time
```

## Sending Continuous Data

```python
# Example: streaming force sensor data
data_info = StreamInfo(
    name="ForceSensor",
    type="Force",
    channel_count=1,
    nominal_srate=100,  # 100 Hz
    channel_format="float32",
    source_id="force_001",
)

data_outlet = StreamOutlet(data_info)

# In your loop:
force_value = read_force_sensor()
data_outlet.push_sample([force_value])
```

## Receiving Streams (for Feedback)

```python
from pylsl import StreamInlet, resolve_stream

# Find EEG stream
streams = resolve_stream("type", "EEG")
inlet = StreamInlet(streams[0])

# Read samples
sample, timestamp = inlet.pull_sample(timeout=1.0)
if sample:
    eeg_data = sample  # List of channel values
```

## Synchronization

### Clock Synchronization
LSL automatically synchronizes clocks across devices on the same network. Use `local_clock()` for timestamps.

### Sync with External Systems

```python
# Send sync pulse at experiment start
marker_outlet.push_sample(["SYNC_START"])

# Send periodic sync pulses
import threading
def sync_pulse():
    while experiment_running:
        marker_outlet.push_sample(["SYNC_PULSE"])
        time.sleep(60)  # Every 60 seconds

sync_thread = threading.Thread(target=sync_pulse, daemon=True)
sync_thread.start()
```

## Recording with LabRecorder

LabRecorder captures all LSL streams into XDF files:

```bash
# CLI usage
LabRecorder --filename recording.xdf
```

XDF files can be loaded in Python:
```python
import pyxdf

streams, header = pyxdf.load_xdf("recording.xdf")
for stream in streams:
    name = stream["info"]["name"][0]
    data = stream["time_series"]
    timestamps = stream["time_stamps"]
```

## Common Issues

### Stream Not Found
- Check network: all devices must be on the same subnet
- Check firewall: LSL uses UDP for discovery (port 16571)
- Verify stream is created before resolving

### Timing Jitter
- Use `local_clock()` for timestamps, not Python `time.time()`
- Send markers in the main thread, not from a callback
- Minimize processing between event and `push_sample()`

### Buffer Overflow
- For continuous streams, ensure consumer reads fast enough
- Set appropriate buffer sizes: `StreamOutlet(info, chunk_size=0, max_buffered=360)`

## secureLSL Integration

For secure streaming over untrusted networks, use secureLSL:
- Encrypts LSL streams with TLS
- Authenticates stream sources
- Compatible with standard LSL receivers after decryption
