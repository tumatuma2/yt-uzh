# Technical report — `project name`

A deeper write-up than the README: what you built, how it works, and what the
numbers say. Also check the specific submission requirements for your Academia
challenge and add required information here.

- **Track:** Track 2A - SwissGov-RSD: Detecting Cross-Lingual Semantic Differences in Swiss Government Websites
- **Event:** Online
- **Team:** YT - Dario Fagotto, Eleni Gkovedarou, Marco Tumaini
- **Demo:** `link to video, deployment, or notebook`

## 1. Summary

Given the RSD research challenge introduced as "Given two related documents in different languages, predict for each token how strongly its meaning differs from the corresponding content in the other document. Systems should identify both symmetric differences and asymmetric ones such as additions and omissions.". Given as system constraint the usage of Apertus model, limited availability of GPU for training operations, and our previous limited knowledge of the aforementioned challenge. We decided to tackle the problem by using a deterministic set of rules for token mapping and a  pretrained Apertus forecast model. We tested our framework at a custom dataset of statutory code provisions and the provided SwissGov-RSD dataset. Preliminary results show that...

## 2. Architecture

Components, data flow, and where each one runs. Put diagrams in `docs/` and
reference them here.

## 3. Use of Apertus

- **Model:** `e.g. swiss-ai/Apertus-v1.5-8B`
- **How it is used:** inference | fine-tuning | evaluation | red-teaming | agents / tool use
- **Where it runs:** `local weights, hosted endpoint, ...`

Prompts, adapters, quantisation, serving stack — whatever a reader needs to
rebuild your setup.

## 4. Data

What you used, where it came from, and its licence. Flag anything personal or
non-redistributable, and keep it out of the repository (see `.gitignore`).
If data comes from human subjects or contains personal information, describe
how consent was obtained.

At this stage the framework does not use data for training. However, we decided to test it on a sample of statutory code provisions sampled from the Swiss civil code, in all languages included in the SwissGov-RSD dataset. Therefore we built records paired in IT-EN, DE-EN, FR-EN. Then we generated four tables, obtained from the articles sample, that per each record have a text in a language, and the correspondent in another language pair, splitted as prefix, middle (the text Apertus will generate), and a suffix. The generation is based on a seed id that we share in the following table: 

| Destination language           | Seed   |
|--------------------------------|--------|
| Table 1                        |        |
| Table 2                        |        |
| Table 3                        |        |
| Table 4                        |        |

Assuming that the text in the two languages is identical in meaning. The objective is to generate candidate words (or word sets) conditioned on a target text and to determine whether each generated candidate corresponds to the aligned word in the source text. Every generated word by Apertus is accompanied by a score that quantifies the degree of fit (i.e., the quality of the correspondence or alignment).

## 5. Evaluation

A. Fedlex data set

We ran four independent Monte-Carlo simulations that randomly sampled same-meaning text pairs and estimated, for each source language, the average probability that a given token is the closest match when English is the target. Because the simulations are independent draws from the same distribution, we simply averaged these per-simulation probability estimates; the resulting mean probability for each source language (German, French, Italian) provides a stable ranking of which language pairs most strongly with English, with French emerging as the strongest on average.

On the same four tables we run Monte-Carlo simulations, investigating the following: Does log-probability vary depending on how far into the text the missing token appears? This analysis investigates whether the Apertus generated log-probability changes according to the relative position of the missing token within the target text. The position is normalized by the total text length, allowing comparisons across texts of different lengths. Results show an increasing trend in mean log-probability from Q1 (-11.93) to Q4 (-8.80), suggesting that Apertus assigns higher probabilities to its predicted tokens when the missing span occurs later in the text.

B. SwissGov-RSD

How you measured success: task, metric, baseline.

| Setup    | Metric | Result |
|----------|--------|--------|
| Baseline |        |        |
| Ours     |        |        |

## 6. Limitations

Where it breaks, what you did not test, and known failure modes.

## 7. Reproducibility

What a judge needs to get your numbers back: hardware, runtime, seeds, and the
exact commit. `make run` should do the rest.

## 8. Next steps

What you would build with another month.

## License

Creative Commons Attribution 4.0 (CC-BY-4.0). All HackApertus projects are open-sourced.

## References
