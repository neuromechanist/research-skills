<!--
Synthetic manuscript excerpt (Methods + Results) for testing the paper-review reviewer
end to end. Fictional content; data, participants, and citations are invented. It
contains deliberate, reviewable methodological and statistical flaws so the reviewer
has substantive material to critique. Not a complete manuscript.
-->

# Methods (excerpt)

## Participants

Eight healthy adults (mean age 24.3 years) were recruited from the laboratory. No formal power analysis was performed; the sample size was chosen based on availability. All participants were right-handed.

## EEG acquisition and preprocessing

EEG was recorded from 64 channels at 256 Hz. Data were band-pass filtered from 1 to 200 Hz. Independent component analysis was used to remove eye-blink artifacts. Epochs were extracted from -200 to 800 ms around stimulus onset.

## Decoding analysis

For each participant, we trained a linear classifier to distinguish left- versus right-hand motor imagery. We first selected the 20 channels showing the largest condition difference across the full dataset, then trained and evaluated the classifier on those channels using 10-fold cross-validation. Classification accuracy was averaged across folds.

## Statistics

Group-level accuracy was compared against chance (50%) using a one-sample t-test. Differences between the three task conditions (rest, left imagery, right imagery) were assessed with multiple pairwise t-tests. Significance was set at p < 0.05.

# Results (excerpt)

Mean decoding accuracy was 71.2% (SD 9.4%), significantly above chance (t(7) = 6.4, p < 0.001). Pairwise comparisons showed that left-imagery accuracy exceeded rest (p = 0.04), right-imagery exceeded rest (p = 0.03), and left exceeded right (p = 0.048). Figure 2 shows mean accuracy per condition as a bar chart with standard-error whiskers. These results demonstrate that our pipeline robustly decodes motor intent and that the left hemisphere is dominant for this task.
