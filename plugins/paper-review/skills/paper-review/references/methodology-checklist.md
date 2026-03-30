# Methodology Assessment Checklist

Systematic checklist for evaluating the methodological soundness of a manuscript. Not all items apply to every paper; use the relevant sections.

## Experimental Design

- [ ] Research question or hypothesis is clearly stated
- [ ] Study design is appropriate for the research question
- [ ] Controls or comparison conditions are adequate
- [ ] Sample size is justified (power analysis, prior work, or acknowledged as a limitation)
- [ ] Inclusion/exclusion criteria are clearly stated and justified
- [ ] Participant demographics are reported (age, sex/gender, relevant clinical characteristics)
- [ ] If only one sex/gender was studied, this limitation is acknowledged
- [ ] Randomization or counterbalancing is described (if applicable)
- [ ] Potential confounds are identified and addressed or acknowledged

## Data Collection

- [ ] Equipment and software versions are specified
- [ ] Acquisition parameters (sampling rates, resolution, calibration) are reported
- [ ] Data collection protocol is described in sufficient detail to replicate
- [ ] For human subjects: IRB/ethics approval and informed consent are reported
- [ ] For clinical populations: diagnostic criteria and staging are specified

## Signal Processing (EEG/EMG/physiological data)

- [ ] Filtering parameters are appropriate (check Nyquist: analysis bandwidth must not exceed half the cutoff frequency)
- [ ] Artifact rejection/correction method is described and validated for the data type
- [ ] For movement data: movement-specific artifact handling is addressed
- [ ] Re-referencing scheme is stated (if applicable)
- [ ] Epoch/trial selection criteria are stated
- [ ] Number of trials/epochs retained per condition is reported
- [ ] Baseline correction method and period are specified
- [ ] For source estimation: number of electrodes is adequate (>64 for high-density claims)
- [ ] No "double-dipping": features used for clustering/selection are independent of analysis targets

## Statistical Analysis

- [ ] Statistical tests are named and justified
- [ ] Assumptions are tested (normality, homogeneity of variance)
- [ ] Correct test variant is used (paired vs. unpaired, parametric vs. non-parametric)
- [ ] Main effects are tested before post-hoc comparisons
- [ ] Multiple comparison correction is applied (and named: Bonferroni, FDR, etc.)
- [ ] Effect sizes are reported alongside p-values
- [ ] Degrees of freedom are reported
- [ ] For regression: independence of predictors is assessed (multicollinearity, VIF)
- [ ] For correlation: the type is appropriate (Pearson for linear, Spearman for monotonic)
- [ ] Lack of significant correlation is not equated with lack of association
- [ ] PCA components are not interpreted as independent factors (PCA gives orthogonal, not independent)
- [ ] Sample sizes per group are adequate for the statistical test used
- [ ] Confidence intervals are reported where appropriate
- [ ] Statistical software and version are specified

## Figures and Visualizations

- [ ] Axes are labeled with units
- [ ] Legends are present and complete
- [ ] Error bars are defined (standard deviation, standard error, confidence interval)
- [ ] For small N (<5): individual data points are shown (not just bar plots)
- [ ] Color maps are defined with scale bars
- [ ] Time/frequency scales are appropriate (not in milliseconds when showing minutes)
- [ ] Spectral plots show baseline-corrected data (not biased by average activity)
- [ ] Figures match what is described in the text
- [ ] No figure duplicates information already in another figure or table

## Reproducibility

- [ ] Methods are detailed enough for independent replication
- [ ] Custom code is shared or code availability is addressed
- [ ] Data are shared or data availability is addressed
- [ ] For hardware papers: schematics, block diagrams, or component lists are provided
- [ ] Software versions and key parameters are specified
- [ ] Any custom tools or pipelines are described or referenced

## Conflicts of Interest and Transparency

- [ ] Author affiliations are consistent with the work presented
- [ ] Funding sources are disclosed
- [ ] Conflicts of interest are declared (or explicitly stated as none)
- [ ] If authors are evaluating their own tool/product, this relationship is transparent
- [ ] Patents related to the work are disclosed

## Literature and Context

- [ ] Literature review includes recent work (last 2-3 years)
- [ ] Competing methods or interpretations are cited
- [ ] Cited papers actually support the claims they are attached to
- [ ] The paper positions itself relative to existing work (novelty claim is supported)
- [ ] Limitations are discussed honestly

Use opencite to search for relevant literature when verifying whether key references are missing:
```bash
uvx opencite search "topic keywords" --max 10 --sort citations
uvx opencite canonical "field or method" --max 5
```
