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

At this stage the framework does not use data for training. However, we decided to test it on a sample of statutory code provisions sampled from the Swiss civil code, in all languages included in the SwissGov-RSD dataset. Therefore we built records paired in IT-EN, DE-EN, FR-EN. Dataset pairs are split as follows: 

| Destination language    | Sample |
|-------------------------|--------|
| de                      |        |
| fr                      |        |
| en                      |        |
| it                      |        |

We stress that the sampled articles are not an official publication. Only the publication issued by the Federal Chancellery is authoritative.
Assuming that the text in the two languages is identical in meaning. The objective is to generate candidate words (or word sets) conditioned on a target text and to determine whether each generated candidate corresponds to the aligned word in the source text. Every generated word by Apertus is accompanied by a score that quantifies the degree of fit (i.e., the quality of the correspondence or alignment).

## 5. Evaluation

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
