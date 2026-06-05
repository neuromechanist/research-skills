<!--
Synthetic NIH R01 Specific Aims page. Fictional content for testing the grant-review
reviewer end to end. Not a real proposal; investigators, data, and citations are invented.
Mechanism: NIH R01. It contains deliberate, reviewable strengths and weaknesses so the
reviewer has something to score.
-->

# Specific Aims

## Decoding Motor Intent from Non-Invasive EEG for At-Home Stroke Rehabilitation

Upper-limb impairment after stroke affects more than 60% of survivors, and access to intensive supervised rehabilitation is limited by clinician time and travel burden. Brain-computer interfaces (BCIs) that decode movement intent and drive functional feedback can deliver high-dose practice, but most decoders rely on invasive recordings or laboratory-grade EEG systems that do not translate to the home. The central problem is that consumer-grade EEG is noisy, non-stationary across sessions, and poorly characterized in the lesioned brain, so existing decoders degrade rapidly outside the lab.

Our long-term goal is a self-calibrating, non-invasive BCI that sustains accurate motor-intent decoding across months of unsupervised home use. The **central hypothesis** is that subject-specific cortical source features, combined with session-adaptive transfer learning, yield decoding that is robust to the day-to-day non-stationarity of consumer EEG in stroke survivors. We base this hypothesis on our preliminary data showing that source-space features reduced cross-session accuracy loss from 18% to 6% in 8 chronic stroke participants. We will test the hypothesis through three aims.

**Aim 1. Characterize the cross-session stability of motor-intent features in consumer EEG after stroke.** We will record weekly 32-channel EEG during a cued reach-and-grasp task in 40 chronic stroke survivors over 12 weeks. We will quantify drift in sensor- and source-space features and relate drift to lesion location from structural MRI. *Working hypothesis:* source-space features drift less than sensor-space features, and drift magnitude scales with peri-lesional involvement of sensorimotor cortex.

**Aim 2. Develop and validate a session-adaptive transfer-learning decoder.** We will build a decoder that updates a subject-specific prior with a short (<2 min) recalibration each session. We will benchmark it against a fixed decoder and a full-retrain decoder on the Aim 1 data using nested cross-validation. *Success criterion:* the adaptive decoder maintains >=75% four-class accuracy with no more than 5% loss across sessions.

**Aim 3. Evaluate feasibility and decoding accuracy during 4 weeks of unsupervised home use.** Twenty participants will take a packaged BCI home and complete daily sessions. We will measure adherence, accuracy over time, and usability, and we will collect feedback for design iteration. *Success criterion:* >=70% adherence and accuracy within 8% of in-lab performance.

**Impact.** Establishing which EEG features survive home deployment, and a decoder that adapts to them, will remove a central barrier to scalable at-home BCI rehabilitation and provide an openly released dataset and decoding pipeline for the field.
