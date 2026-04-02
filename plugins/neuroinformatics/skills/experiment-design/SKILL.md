---
name: experiment-design
description: "Use this skill for \"design experiment\", \"create PsychoPy experiment\", \"stimulus presentation\", \"experiment protocol\", \"timing validation\", \"trial structure\", \"block design\", \"event-related design\", \"PsychoPy builder\", \"create stimuli\", \"LSL markers\", \"Lab Streaming Layer\", \"event markers\", \"trigger codes\", or when the user wants to design or implement a neuroscience experiment."
version: 0.1.0
---

# Experiment Design

Design and implement neuroscience experiments with PsychoPy, including stimulus presentation, timing validation, event markers, and Lab Streaming Layer (LSL) integration.

## When to Use

- Designing a new behavioral or neuroimaging experiment
- Creating PsychoPy scripts for stimulus presentation
- Setting up event markers via LSL or parallel port
- Validating timing accuracy
- Converting an experiment protocol to code

## Experiment Design Principles

### Trial Structure

Every trial consists of:

```
[Fixation] -> [Stimulus] -> [Response Window] -> [Inter-trial Interval]
   |              |               |                    |
  marker       marker          marker              marker
```

### Design Types

| Design | Best For | Example |
|--------|----------|---------|
| **Block** | fMRI, sustained attention | 30s blocks of condition A, B |
| **Event-related** | ERP/EEG, rapid events | Randomized single trials |
| **Mixed** | Both sustained and transient | Blocks with jittered events |
| **Resting state** | Baseline/connectivity | Eyes open/closed periods |

### Timing Considerations

- **Frame-based timing** (preferred): Specify durations in frames, not seconds
- **Monitor refresh rate**: 60 Hz = 16.67 ms/frame; 120 Hz = 8.33 ms/frame
- **Stimulus onset**: Sync to vertical blank for precise timing
- **Jitter**: Add random ITI variation for event-related designs (avoid expectation effects)
- **Minimum stimulus duration**: 1 frame (16.67 ms at 60 Hz)

## PsychoPy Experiment Template

### Basic Structure

```python
from psychopy import visual, core, event, data, gui
import numpy as np

# Experiment parameters
exp_info = {
    "participant": "",
    "session": "01",
    "task": "experiment_name",
}

# GUI dialog
dlg = gui.DlgFromDict(exp_info, title="Experiment")
if not dlg.OK:
    core.quit()

# Window setup
win = visual.Window(
    size=[1920, 1080],
    fullscr=True,
    monitor="testMonitor",
    units="deg",
    color=[0, 0, 0],
)

# Stimuli
fixation = visual.TextStim(win, text="+", height=2)
stimulus = visual.ImageStim(win, image=None, size=[10, 10])
feedback = visual.TextStim(win, text="", height=1.5)

# Trial handler
conditions = data.importConditions("conditions.xlsx")
trials = data.TrialHandler(
    conditions,
    nReps=1,
    method="random",
)

# Clock
clock = core.Clock()

# Main experiment loop
for trial in trials:
    # Fixation
    fixation.draw()
    win.flip()
    core.wait(0.5)  # 500 ms fixation

    # Stimulus
    stimulus.image = trial["stimulus_file"]
    stimulus.draw()
    win.flip()
    # Send marker here

    # Response
    clock.reset()
    keys = event.waitKeys(
        maxWait=2.0,
        keyList=["left", "right", "escape"],
        timeStamped=clock,
    )

    if keys:
        if keys[0][0] == "escape":
            core.quit()
        trials.addData("response", keys[0][0])
        trials.addData("rt", keys[0][1])

    # ITI (jittered)
    iti = np.random.uniform(0.8, 1.2)
    core.wait(iti)

# Save data
trials.saveAsWideText(f"data/sub-{exp_info['participant']}_task-{exp_info['task']}.csv")
win.close()
core.quit()
```

### Conditions File Format

```
# conditions.xlsx or conditions.csv
stimulus_file,condition,correct_response
stimuli/face01.png,face,left
stimuli/house01.png,house,right
stimuli/face02.png,face,left
```

## Lab Streaming Layer (LSL) Integration

### Sending Markers

```python
from pylsl import StreamInfo, StreamOutlet

# Create marker stream
info = StreamInfo(
    name="ExperimentMarkers",
    type="Markers",
    channel_count=1,
    nominal_srate=0,  # irregular rate
    channel_format="string",
    source_id="psychopy_markers",
)
outlet = StreamOutlet(info)

# Send marker at stimulus onset
stimulus.draw()
win.flip()
outlet.push_sample(["stimulus_onset"])  # Send immediately after flip
```

### Common Marker Scheme

| Marker | Code | Description |
|--------|------|-------------|
| stimulus_onset | S1-S99 | Stimulus presentation |
| response | R1-R4 | Participant response |
| feedback | F1-F2 | Correct/incorrect feedback |
| block_start | B1-B10 | Block onset |
| block_end | BE | Block offset |
| trial_start | T | Trial onset |
| experiment_start | EXP_START | First trial |
| experiment_end | EXP_END | Last trial |

### HED Annotation for Markers

Annotate events with Hierarchical Event Descriptors (HED) for standardized event description:

```tsv
onset	duration	trial_type	value	HED
0.0	0.0	stimulus	S1	Sensory-event, Visual-presentation, (Image, Face)
1.5	0.0	response	R1	Agent-action, (Press, Key/Left)
```

## Timing Validation

### Photodiode Check

```python
# Add a small white square in the corner that flashes with stimulus
photodiode = visual.Rect(win, width=50, height=50, pos=[900, -500], units="pix")

# During stimulus presentation
stimulus.draw()
photodiode.fillColor = [1, 1, 1]  # White
photodiode.draw()
win.flip()
# Photodiode sensor on screen corner measures actual onset time
```

### Frame Timing Check

```python
# Check for dropped frames
win.recordFrameIntervals = True
# After experiment:
frame_intervals = win.frameIntervals
dropped = sum(1 for fi in frame_intervals if fi > 1.5 * (1.0 / 60.0))
print(f"Dropped frames: {dropped}/{len(frame_intervals)}")
```

## Output for BIDS

Structure experiment output to be BIDS-compatible:

```
data/
  sub-01/
    sub-01_task-name_events.tsv    # onset, duration, trial_type, response, rt
    sub-01_task-name_beh.tsv       # behavioral data
    sub-01_task-name_beh.json      # metadata
```

## Additional Resources

- Reference: [references/psychopy-components.md](references/psychopy-components.md) - Visual, audio, and response components
- Reference: [references/lsl-integration.md](references/lsl-integration.md) - LSL setup, synchronization, and troubleshooting
