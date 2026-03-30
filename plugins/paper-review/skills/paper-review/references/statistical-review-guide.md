# Statistical Review Guide

Common statistical issues encountered in manuscript review and how to identify them.

## Test Selection Errors

### Parametric vs. Non-parametric
- **Issue:** Using parametric tests (t-test, ANOVA) on data that violates normality assumptions.
- **How to identify:** Check if normality was tested (Shapiro-Wilk, Kolmogorov-Smirnov). For small samples (N<30), non-parametric tests are often more appropriate.
- **What to recommend:** Suggest appropriate non-parametric alternatives (Mann-Whitney U, Kruskal-Wallis, Friedman) and request normality testing.

### Paired vs. Unpaired
- **Issue:** Using paired tests for independent samples or unpaired tests for repeated measures.
- **How to identify:** Paired tests (paired t-test, Wilcoxon signed-rank) are for repeated measures on the same subjects. Unpaired tests (independent t-test, Wilcoxon rank-sum/Mann-Whitney U) are for comparing different groups. Check if the comparison involves the same subjects measured twice or different subjects.
- **What to recommend:** Name the correct test variant and explain the distinction.

### Missing Main Effects
- **Issue:** Running post-hoc pairwise comparisons without first testing for a main effect.
- **How to identify:** Multiple t-tests or Wilcoxon tests between groups without a preceding ANOVA or Kruskal-Wallis test.
- **What to recommend:** Suggest testing for the main effect first, then using post-hoc tests with appropriate correction.

## Multiple Comparisons

- **Issue:** Running many statistical tests without correcting for the increased false positive rate.
- **How to identify:** Count the number of tests performed. If >3 comparisons are made on the same dataset, correction is needed.
- **What to recommend:** Bonferroni (conservative), Holm-Bonferroni (less conservative), or FDR/Benjamini-Hochberg (for many comparisons). State the correction method and adjusted significance threshold.

## Sample Size Issues

### Small N with Bar Plots
- **Issue:** Using bar plots with error bars for groups of N<5. The mean and error bars create an illusion of a distribution that does not exist with 2-4 data points.
- **How to identify:** Check figure legends for N. If N<5, bar plots are inappropriate.
- **What to recommend:** Show individual data points connected with lines (for paired data) or as a strip/jitter plot. The reader can then judge the actual data distribution.

### Subgroup Analysis with Insufficient Power
- **Issue:** Splitting an already small sample into subgroups and drawing statistical conclusions from groups of N=2 or N=3.
- **How to identify:** Check the subgroup sizes in the methods or results. If any group has fewer than 5 participants, conclusions about group differences are questionable.
- **What to recommend:** Acknowledge as a limitation, or use non-parametric tests that do not assume a distribution. Consider whether the subgroup analysis is essential or if the data should be analyzed as a whole.

## Correlation and Regression Pitfalls

### Linear Correlation Does Not Imply Association (or Lack Thereof)
- **Issue:** Reporting no significant Pearson correlation and concluding "no association."
- **How to identify:** Look at scatter plots. If the relationship appears non-linear, a linear correlation test will miss it.
- **What to recommend:** Use Spearman's rank correlation for monotonic relationships, or distance correlation / mutual information for non-linear associations. State clearly that "no significant linear correlation" does not mean "no association."

### PCA Does Not Imply Independence
- **Issue:** Interpreting PCA components as independent factors.
- **How to identify:** PCA produces orthogonal (uncorrelated) components, but orthogonality does not imply statistical independence. Authors who run PCA and then treat components as independent factors for regression are making an unsupported assumption.
- **What to recommend:** Clarify that PCA provides orthogonal decomposition, not independence. If independence is needed, consider Independent Component Analysis (ICA) or explicit independence testing.

### Correlation Driven by Outliers
- **Issue:** A few extreme data points driving the apparent correlation.
- **How to identify:** In scatter plots, check if removing 1-2 points would eliminate the correlation. Look for data clustered in two groups with the correlation driven by the gap between groups.
- **What to recommend:** Report the correlation with and without the suspected outliers. Use robust correlation methods. Show the scatter plot so readers can judge.

## Signal Processing Statistics

### Nyquist Constraint
- **Issue:** Analyzing frequency content above the Nyquist frequency (half the sampling rate) or above half the filter cutoff.
- **How to identify:** If data is filtered at X Hz, the maximum analyzable frequency is X/2 Hz. If the analysis extends above this, the results above that frequency are invalid.
- **What to recommend:** Either increase the filter cutoff (if the sampling rate allows) or restrict the analysis to below the Nyquist limit.

### Baseline Correction in Spectral Analysis
- **Issue:** Event-related spectral perturbation (ERSP) or coherence plots shown without baseline removal.
- **How to identify:** If the spectral plots show absolute power rather than change from baseline, the interpretation is biased by the average spectral activity.
- **What to recommend:** Apply baseline correction (subtraction or division) and show the change relative to a pre-event baseline period.

### Double-Dipping
- **Issue:** Using the same data features for both selection (e.g., clustering, ROI definition) and analysis.
- **How to identify:** If ICA components are clustered using ERSP features, and then ERSP is analyzed for those clusters, the analysis is circular. Similarly, if electrodes are selected based on activity patterns and then those patterns are reported as findings.
- **What to recommend:** Use independent criteria for selection and analysis. For clustering, use features orthogonal to the analysis target (e.g., cluster by dipole location, analyze by ERSP).

## Reporting Checklist

For each statistical test reported, verify:
- [ ] Test name and variant (paired/unpaired, parametric/non-parametric)
- [ ] Test statistic value
- [ ] Degrees of freedom
- [ ] p-value (exact, not just < 0.05)
- [ ] Effect size (Cohen's d, eta-squared, r, etc.)
- [ ] Correction for multiple comparisons (if applicable)
- [ ] Software and version used
