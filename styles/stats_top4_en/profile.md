# Style profile: Statistics top-4 journals, English (stats_top4_en)

Status: trained (6 papers) | Language: en, with a Chinese-rendering table for writing in Chinese
Corpus: Chen & Qin (AoS 2010); Chen & Peng (AoS); Athey, Tibshirani & Wager (AoS); Candès, Fan, Janson & Lv (JRSSB); Yu, Li, Xue & Li (JASA 2022); Jiang, Wang, Wen, Jiang & Zhang (JASA 2022).

## 1. Measured profile (from features.json, 66.7k words, 2,647 sentences)
- Sentence length: mean 25 words, median 22, middle half 14 to 32. Short sentences carry interpretation, long ones carry definitions and conditions.
- Commas per sentence: 1.79; semicolons rare (9.4 per 100 sentences).
- First-person plural ("we"): 13.07 per 1000 words, "our": 3.79 per 1000 words.
- Connectives: Hence/Thus/Therefore (1.2/1k), Moreover/Furthermore/In addition (0.7/1k), However (1.08/1k), Specifically/In particular (0.3/1k).

## 2. Move structure
- **Abstract**: Setup -> We propose X -> Properties & Conditions -> Theoretical guarantee -> Empirical validation.
- **Introduction**: Broad setting -> Formal setup -> Chain of literature -> The gap ("However...") -> Departure from classical setting -> Novelty claim ("To the best of our knowledge") -> Paper roadmap.
- **Method & Theory**: Notation setup ("With a slight abuse of notation...") -> Heuristic illustration -> Formal theorem -> Step-by-step conditions -> Remarks.
- **Simulation & Empirical**: Flat parameter description -> Baseline models -> "The results can be summarized as follows:" -> Numbered findings -> Honest caveats.
- **Conclusion**: Retrospective summary -> Unaddressed limitations -> Understated future extensions.

## 3. High-Tier Native Verbs & Transitions
- **Verbs**: harness, employ, invoke, eschew, circumvent, preclude, elucidate, tease apart.
- **Heuristic Signposts**: "To gain insight into condition (3.4)...", "To heuristically illustrate the impact of...", "To appreciate this point, let us consider...".
- **Balanced Critique**: "Although [X] remains a standard benchmark, it relies on [restriction] which fails when...".
- **Concessions**: "Despite meaningful progress, further research is warranted.", "Admittedly, this paper poses more problems than it solves...".

## 4. Anti-AI Checklist
- No stacked adjectives ("novel, robust and scalable").
- No corporate buzzwords: pivotal, comprehensive, landscape, delve into, seamlessly, game-changer.
- No unqualified superiority claims; every guarantee must state its asymptotic regime (e.g., "as n, p -> infinity under Assumptions 1-3").