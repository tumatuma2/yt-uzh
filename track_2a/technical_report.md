# Technical report — YT-APERTUS-RSD

A deeper write-up than the README: what you built, how it works, and what the
numbers say. Also check the specific submission requirements for your Academia
challenge and add required information here.

- **Track:** Track 2A - SwissGov-RSD: Detecting Cross-Lingual Semantic Differences in Swiss Government Websites
- **Event:** Online
- **Team:** YT - Dario Fagotto, Eleni Gkovedarou, Marco Tumaini

## 1. Summary

Given the RSD research challenge introduced as "Given two related documents in different languages, predict for each token how strongly its meaning differs from the corresponding content in the other document. Systems should identify both symmetric differences and asymmetric ones such as additions and omissions.".

Given the system constraint the usage of Apertus model, limited availability of GPU for training operations, and our previous limited knowledge of the aforementioned challenge.

We decided to tackle the problem by using a deterministic set of rules for token mapping and a pretrained Apertus forecast model.

We tested our framework at a custom dataset of statutory code provisions. Due to time constraints, we could not test it on the SwissGov-RSD data set. 

## 1.5 Idea and compromises

The idea at base of this project is to approach the problem as a very constrained translation attempt filling text trying to autocomplete small snippets of a text using its translation.

This solution frames the problem as a *FIM (fill in the middle)* task providing the text in both languages and hiding only small semantic parts of it to be reconstructed, then reading from the internal probabilities of the model what is the accuracy of the translation.

This would require a model that is aware of *FIM* tasks; unfortunately Apertus is not trained for these tasks as stock and we didn't have access until very late to infrastructure that would allow for the finetuning required; from an efficiency point of view moreover a diffusion style model would be probably more approriate; becasue while KV cache definitely helps with the huge prefixes shared for the small completions, the access of this through APIs and reversing the problem (for simmetry) incur in very high number of requests via API.

We proceeded with Apertus 70B since the initial tests showed that the task was not understood well by the 8B model without training; but with fine tuning we think 8B will probably work as well.

## 2. Architecture

The pipeline for the task consists in multiple steps:

- **(A)** Splitting the text in semantic blocks that (while being granular) are long and meaningful enough to make sense for the LLM as concepts
- **(B)** For each of these blocks (in both texts) frame the problem as an autocompletion task (with some regards to have the longest possible shared prefix) aware of the original text
- **(C)** Feed the model the task AND the answer while recording log probabilities of the assistent tokens (including EOS)
- **(D)** Compute the total probability of that answer adding the logprobs together (possibly in the future also adjusting the value depending on how the attention in the LLM distributed over the original/translated text to make sure it's using the base text and not inventing).
- **(E)** Distribute the results from those probabilities in the sematic blocks back into the standard tokenization provided by the dataset

*@TODO*
(Components, data flow, and where each one runs. Put diagrams in `docs/` and
reference them here.)

### A. Semantic-unit segmentation

As a preprocessing step, we segmented each document into short, linguistically motivated units to support the subsequent cross-lingual comparison. We used a separate, languagespecific spaCy pipeline for each language. Each pipeline uses the corresponding language model and adapted tokenization, part-of-speech tagging, dependency parsing, named-entity recognition, fixed-expression lists, and other rules specific to the linguistic properties of that language. The segmentation identifies expressions that are best treated as a unit, including multiword expressions, named entities, dates and numerical expressions, proper names, noun compounds, determiner-noun groups, auxiliary-verb constructions, infinitives, verb-particle constructions, and selected prepositional constructions. Domain-specific fixed expressions, such as “in accordance with”, “federal law”, “come into force” in the English pipeline, were explicitly preserved as single units. The pipelines follow the same general principles, but
their rules and expression lists are adapted to the linguistic characteristics of each language. The segmentation also accounts for the semantic importance of individual words. Negation and modal verbs are kept separate from surrounding phrase units because they can substantially change the interpretation of a proposition. Negation changes its polarity, while modal verbs encode obligation, permission, possibility, or necessity. These distinctions are especially important in legal and administrative texts, where small linguistic differences can have significant consequences for meaning. Adjectives and adverbs are generally kept separate as well, to make their individual contributions easier to identify, unless they form
part of a predefined fixed expression. To obtain a consistent segmentation, the pipeline identifies candidate spans and selects them in order of priority, preventing overlaps between units. Any tokens not assigned to a multiword unit remain as individual units. The resulting sequence preserves important linguistic expressions while allowing potentially meaningful differences to be localized more precisely than with sentence-level comparison alone.

## 3. Use of Apertus

*@TODO*

- **Model:** `swiss-ai/Apertus-v1.5-70B`
- **How it is used:** forced inference logprobs *(vllm `prompt_logprobs`)*
- **Where it runs:** hosted endpoint

For the evaluation itself the only requirement is a `.env` file that points to a `vllm` server, that has the 70B chat model.

```sh
LLM_NAME=<served-model-name>
LLM_BASE_URL=<openai-endpoint-url>
LLM_API_KEY=<key>
```

## 4. Data

At this stage the framework does not use data for training. However, we decided to test it on a sample of statutory code provisions sampled from the Swiss civil code, in all languages included in the SwissGov-RSD dataset. Therefore we built records paired in IT-EN, DE-EN, FR-EN. Then we generated four tables, obtained from the articles sample, that per each record have a text in a language, and the correspondent in another language pair, splitted as prefix, middle (the text Apertus will generate), and a suffix. The generation is based on a seed id that we share in the following table:

| Table ID                       | Seed                  |
|--------------------------------|-----------------------|
| Table 1                        | 1B3C5D7E9FA1B2C3      |
| Table 2                        | DEADBEEFCAFEBABE      |
| Table 3                        | 0123456789ABCDEF      |
| Table 4                        | F0E1D2C3B4A59687      |

Assuming that the text in the two languages is identical in meaning. The objective is to generate candidate words (or word sets) conditioned on a target text and to determine whether each generated candidate corresponds to the aligned word in the source text. Every generated word by Apertus is accompanied by a score that quantifies the degree of fit (i.e., the quality of the correspondence or alignment). Each table can be generated by running `make run_on_fedlex_sample SEED=...`

## 5. Evaluation

**A. Fedlex data set**

We ran four independent Monte-Carlo simulations that randomly sampled same-meaning text pairs and estimated, for each source language, the average probability that a given token is the closest match when English is the target. Because the simulations are independent draws from the same distribution, we simply averaged these per-simulation probability estimates; the resulting mean probability for each source language (German, French, Italian) provides a stable ranking of which language pairs most strongly with English, with French emerging as the strongest on average.

| Source Language                | T1     | T2     | T3     | T4     |
|--------------------------------|--------|--------|--------|--------|
| FR                             | 2      |2       | 1      | 1      |
| DE                             | 1      |3       | 2      | 3      |
| IT                             | 3      |1       | 3      | 2      |

On the same four tables we run Monte-Carlo simulations, investigating the following: Does log-probability vary depending on how far into the text the missing token appears? This analysis investigates whether the Apertus generated log-probability changes according to the relative position of the missing token within the target text. The position is normalized by the total text length, allowing comparisons across texts of different lengths. Results show an increasing trend in mean log-probability from Q1 (-11.93) to Q4 (-8.80), suggesting that Apertus assigns higher probabilities to its predicted tokens when the missing span occurs later in the text.

| Position Quartile              | Average Logprob                   |
|--------------------------------|-----------------------------------|
| Q1                             | -11.93                            |
| Q2                             | -10.60                            |
| Q3                             | -10.13                            |
| Q4                             | -8.80                             |

**B. SwissGov-RSD**

*@TODO*

How you measured success: task, metric, baseline.

| Setup    | Metric | Result |
|----------|--------|--------|
| Baseline |        |        |
| Ours     |        |        |

## 6. Limitations

At this stage we could not test the framework on SwissGov-RSD.

## 7. Reproducibility

*@TODO*
What a judge needs to get your numbers back: hardware, runtime, seeds, and the
exact commit. `make run` should do the rest.

## 8. Next steps

1. Test the framework on SwissGov-RSD;
2. Performance comparison with the next Apertus model release. 

## License

Creative Commons Attribution 4.0 (CC-BY-4.0). All HackApertus projects are open-sourced.

## References
