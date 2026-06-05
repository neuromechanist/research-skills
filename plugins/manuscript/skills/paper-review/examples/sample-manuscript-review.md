<!--
Worked example review of examples/sample-manuscript-excerpt.md. Synthetic, for
calibration of tone, depth, severity, and format. Demonstrates the PARTIAL REVIEW
banner (the input is a methods+results excerpt) and the Synopsis / Critical / Major /
Minor / References / Editor Note structure from references/review-output-template.md.
-->

**PARTIAL REVIEW.** Sections provided: Methods and Results (excerpt). Missing: Abstract, Introduction, Discussion, Conclusion, the figures themselves, supplementary materials, and references. The assessment below is based solely on the provided excerpt and is not a complete peer review.

## Synopsis

This excerpt reports an EEG motor-imagery decoding study in eight healthy adults, using a 64-channel system at 256 Hz, ICA artifact rejection, and a linear classifier evaluated with 10-fold cross-validation; group accuracy was 71.2%, reported as above chance. The research question is legitimate and cross-validation is appropriate in principle. However, the analysis contains a publication-blocking double-dipping flaw, a Nyquist violation in the filtering description, uncorrected multiple comparisons, and an interpretive claim ("left hemisphere dominance") with no methodological basis. The work requires major revision at minimum.

## Critical Issues

1. **Double-dipping invalidates the decoding result (Methods, Decoding Analysis).** Channels were selected by largest condition difference across the full dataset, then the classifier was trained and evaluated on those channels by cross-validation on the same data. Feature selection uses the labels of the full set, so the cross-validation no longer estimates generalization and the 71.2% accuracy is optimistically biased. Fix: perform channel selection inside each training fold only, with the test fold unseen; or use all channels with regularization (L2-LDA, CSP). See Kriegeskorte et al. 2009, Nat Neurosci 12:535-540.

2. **Nyquist violation: 200 Hz low-pass at 256 Hz sampling (Methods, EEG Acquisition).** The Nyquist frequency at 256 Hz is 128 Hz; a 200 Hz cutoff is not representable and signals the filter or the reported sampling rate is wrong, with possible aliasing. Report the actual cutoff (<= 128 Hz) and confirm the sampling rate; raise the sampling rate if higher frequencies are required.

## Major Concerns

1. **Uncorrected multiple comparisons (Statistics; Results).** Three pairwise t-tests are run with no omnibus test and no correction. The left-vs-right result (p = 0.048) does not survive Bonferroni (threshold 0.0167). Add a repeated-measures ANOVA or non-parametric equivalent before post-hoc tests, apply a named correction (Holm-Bonferroni or FDR), and report adjusted values.

2. **N = 8 with no power analysis (Participants; Results).** Availability-driven recruitment with no power analysis; condition-level subgroup claims are underpowered. Acknowledge the limitation and report effect sizes (Cohen's d, partial eta-squared) for all comparisons.

3. **Unsupported "left hemisphere dominance" claim (Results, final sentence).** No spatial analysis, classifier-weight mapping, source localization, or laterality index is described, so the lateralization claim is unsupported. Remove it or support it with an appropriate spatial analysis.

4. **ICA and classifier underspecified (Methods).** Number of components removed and the rejection criterion are absent; "linear classifier" is ambiguous (LDA vs linear SVM vs logistic regression differ at N = 8), and fold construction (temporal independence between adjacent epochs) is unstated. Provide these for reproducibility.

## Minor Concerns

1. **Bar chart for N = 8 (Figure 2, described).** Bar plots with error bars for small N hide the distribution; show individual participant points, connected across paired conditions. (Figure not included in the excerpt; assessed from its text description.)
2. **Sex/gender, ethics approval, and informed consent not reported (Participants).** Add per standard human-subjects reporting.
3. **Significance inflation in the closing sentence.** "Robustly decodes ... left hemisphere is dominant" overstates the evidence; see manuscript:humanizer (significance inflation). Quantify or remove "robustly."

## References

1. Kriegeskorte N, Simmons WK, Bellgowan PS, Baker CI. 2009. "Circular analysis in systems neuroscience: the dangers of double dipping." Nature Neuroscience 12(5):535-540. doi:10.1038/nn.2303

## Editor Note

Dear Editor, this excerpt reports an EEG motor-imagery decoding study in eight participants. The question is valid, but a publication-blocking double-dipping flaw biases the headline accuracy, a Nyquist violation undermines the preprocessing description, multiple comparisons are uncorrected, and the central interpretive claim is unsupported. Recommendation: major revision, contingent on within-fold feature selection (or regularization), corrected filter parameters, and removal or proper support of the hemispheric claim.
