# Analysis

The R pipeline and data for The AI Label Paradox. Every input the Rmd
reads sits in this folder, because it loads its files by bare filename.

## Files

- study_analysis.Rmd                 the full pipeline
- prolific_192_anon.csv              anonymised data, N = 201 analytical sample
- oshea_function_words_277.csv       function-word list for the stylometry
- suspicion_coding_sheet_coded.csv   manual suspicion coding input
- suspicion_coding_sheet.csv         uncoded template, regenerated if absent
- coding_review.txt

## Run

From this folder, with R and the packages BayesFactor, specr, psych,
lavaan, car, lme4, performance, parameters, emmeans, effectsize, tidytext
and tidyverse:

    rmarkdown::render("Study_Analysis.Rmd")

It regenerates the dissertation results to the decimal: confirmatory
tests, equivalence bounds, Bayes factors, the measurement model and the
round-level mixed model.
