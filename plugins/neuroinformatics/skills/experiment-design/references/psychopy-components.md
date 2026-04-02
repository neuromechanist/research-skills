# PsychoPy Components Reference

## Visual Stimuli

### TextStim
```python
text = visual.TextStim(win, text="Hello", font="Arial", height=2, color="white")
text.draw()
win.flip()
```

### ImageStim
```python
img = visual.ImageStim(win, image="stimulus.png", size=[10, 10], units="deg")
img.draw()
win.flip()
```

### GratingStim
```python
grating = visual.GratingStim(win, tex="sin", mask="gauss", sf=3, size=5, ori=45)
grating.draw()
win.flip()
```

### ShapeStim / Circle / Rect
```python
circle = visual.Circle(win, radius=2, fillColor="red", lineColor="white")
rect = visual.Rect(win, width=4, height=2, fillColor="blue")
```

### RatingScale
```python
scale = visual.RatingScale(win, low=1, high=7, labels=["Low", "High"])
while scale.noResponse:
    scale.draw()
    win.flip()
rating = scale.getRating()
rt = scale.getRT()
```

## Audio Stimuli

### Sound
```python
from psychopy import sound

tone = sound.Sound(value=440, secs=0.5)  # 440 Hz for 500 ms
tone.play()

wav = sound.Sound(value="beep.wav")
wav.play()
```

## Response Collection

### Keyboard
```python
from psychopy import event

# Wait for specific keys
keys = event.waitKeys(keyList=["left", "right", "escape"], timeStamped=clock)

# Check without waiting
keys = event.getKeys(keyList=["space"])
```

### Mouse
```python
mouse = event.Mouse(win=win)

# Get position
x, y = mouse.getPos()

# Check clicks
buttons = mouse.getPressed()  # [left, middle, right]

# Wait for click
while not any(mouse.getPressed()):
    stimulus.draw()
    win.flip()
```

### Parallel Port (for EEG triggers)
```python
from psychopy import parallel

port = parallel.ParallelPort(address=0x0378)

# Send trigger
port.setData(1)   # Set trigger value
core.wait(0.01)    # Hold for 10 ms
port.setData(0)    # Reset
```

## Data Handling

### TrialHandler
```python
from psychopy import data

conditions = data.importConditions("conditions.xlsx")
trials = data.TrialHandler(
    conditions,
    nReps=2,
    method="random",  # "sequential", "fullRandom"
)

for trial in trials:
    # trial is a dict with condition values
    stimulus.image = trial["image"]
    trials.addData("response", resp)
    trials.addData("rt", rt)

# Save
trials.saveAsWideText("output.csv")
trials.saveAsExcel("output.xlsx")
```

### ExperimentHandler
```python
exp = data.ExperimentHandler(
    name="myExp",
    extraInfo=exp_info,
    dataFileName=f"data/sub-{exp_info['participant']}",
)
exp.addLoop(trials)
```

## Timing Utilities

### Clock
```python
clock = core.Clock()
clock.reset()
elapsed = clock.getTime()
```

### CountdownTimer
```python
timer = core.CountdownTimer(5.0)  # 5 second countdown
while timer.getTime() > 0:
    stimulus.draw()
    win.flip()
```

### Frame-based Timing (preferred)
```python
# Show stimulus for exactly 30 frames (500 ms at 60 Hz)
for frame in range(30):
    stimulus.draw()
    win.flip()
```

## Monitor Setup

```python
from psychopy import monitors

mon = monitors.Monitor("testMonitor")
mon.setDistance(57)       # cm from screen
mon.setWidth(53)         # cm screen width
mon.setSizePix([1920, 1080])
mon.save()

win = visual.Window(monitor="testMonitor", units="deg")
```
