# AI Writing Patterns

This file is part of the `manuscript:humanizer` skill, adapted from [blader/humanizer](https://github.com/blader/humanizer) (MIT, Siqi Chen); see the skill's `SKILL.md` for attribution and `LICENSE` for terms.

National Institutes of Health (NIH), Institute of Electrical and Electronics Engineers (IEEE), American Psychological Association (APA), and American Chemical Society (ACS) are referenced below by their standard abbreviations.

Patterns 1 to 29 come from upstream; patterns 30 to 45, the quick scan, and the per-pattern "Research writing note" callouts are research-skills additions.

## CONTENT PATTERNS

### 1. Undue Emphasis on Significance, Legacy, and Broader Trends

**Words to watch:** stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance/significance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted

**Problem:** Large language model (LLM) writing puffs up importance by adding statements about how arbitrary aspects represent or contribute to a broader topic.

**Before:**
> The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics in Spain. This initiative was part of a broader movement across Spain to decentralize administrative functions and enhance regional governance.

**After:**
> The Statistical Institute of Catalonia was established in 1989 to collect and publish regional statistics independently from Spain's national statistics office.

**Research writing note:** Grant Significance sections legitimately make importance claims; strip the filler ("pivotal moment", "evolving landscape") but keep substantive significance backed by evidence ("affects 1.2M patients annually", "no validated biomarker exists").


### 2. Undue Emphasis on Notability and Media Coverage

**Words to watch:** independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence

**Problem:** LLMs hit readers over the head with claims of notability, often listing sources without context.

**Before:**
> Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu. She maintains an active social media presence with over 500,000 followers.

**After:**
> In a 2024 New York Times interview, she argued that AI regulation should focus on outcomes rather than methods.


### 3. Superficial Analyses with -ing Endings

**Words to watch:** highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing...

**Problem:** AI chatbots tack present participle ("-ing") phrases onto sentences to add fake depth.

**Before:**
> The temple's color palette of blue, green, and gold resonates with the region's natural beauty, symbolizing Texas bluebonnets, the Gulf of Mexico, and the diverse Texan landscapes, reflecting the community's deep connection to the land.

**After:**
> The temple uses blue, green, and gold colors. The architect said these were chosen to reference local bluebonnets and the Gulf coast.


### 4. Promotional and Advertisement-like Language

**Words to watch:** boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning

**Problem:** LLMs have serious problems keeping a neutral tone, especially for "cultural heritage" topics, and especially in grant Innovation sections.

**Before:**
> Nestled within the breathtaking region of Gonder in Ethiopia, Alamata Raya Kobo stands as a vibrant town with a rich cultural heritage and stunning natural beauty.

**After:**
> Alamata Raya Kobo is a town in the Gonder region of Ethiopia, known for its weekly market and 18th-century church.

**Research writing note:** Grant Innovation sections are particularly prone to this. "Groundbreaking", "transformative", "paradigm-shifting" land as red flags to reviewers. Let the methods speak.


### 5. Vague Attributions and Weasel Words

**Words to watch:** Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications (when few cited)

**Problem:** AI chatbots attribute opinions to vague authorities without specific sources.

**Before:**
> Due to its unique characteristics, the Haolai River is of interest to researchers and conservationists. Experts believe it plays a crucial role in the regional ecosystem.

**After:**
> The Haolai River supports several endemic fish species, according to a 2019 survey by the Chinese Academy of Sciences.

**Research writing note:** Always cite. "Recent work has shown" without a citation is a peer-review red flag.


### 6. Outline-like "Challenges and Future Prospects" Sections

**Words to watch:** Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook

**Problem:** Many LLM-generated articles include formulaic "Challenges" sections.

**Before:**
> Despite its industrial prosperity, Korattur faces challenges typical of urban areas, including traffic congestion and water scarcity. Despite these challenges, with its strategic location and ongoing initiatives, Korattur continues to thrive as an integral part of Chennai's growth.

**After:**
> Traffic congestion increased after 2015 when three new IT parks opened. The municipal corporation began a stormwater drainage project in 2022 to address recurring floods.

**Research writing note:** Discussion sections often need "Limitations" and "Future directions". That is fine; just write specifics ("our sample excluded subjects under 18") instead of generic templates ("Despite these limitations, this work opens exciting avenues").


## LANGUAGE AND GRAMMAR PATTERNS

### 7. Overused "AI Vocabulary" Words

**High-frequency AI words:** Actually, additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adjective), landscape (abstract noun), pivotal, showcase, tapestry (abstract noun), testament, underscore (verb), valuable, vibrant

**Problem:** These words appear far more frequently in post-2023 text. They often co-occur.

**Before:**
> Additionally, a distinctive feature of Somali cuisine is the incorporation of camel meat. An enduring testament to Italian colonial influence is the widespread adoption of pasta in the local culinary landscape, showcasing how these dishes have integrated into the traditional diet.

**After:**
> Somali cuisine also includes camel meat, which is considered a delicacy. Pasta dishes, introduced during Italian colonization, remain common, especially in the south.


### 8. Avoidance of "is"/"are" (Copula Avoidance)

**Words to watch:** serves as/stands as/marks/represents [a], boasts/features/offers [a]

**Problem:** LLMs substitute elaborate constructions for simple copulas.

**Before:**
> Gallery 825 serves as LAAA's exhibition space for contemporary art. The gallery features four separate spaces and boasts over 3,000 square feet.

**After:**
> Gallery 825 is LAAA's exhibition space for contemporary art. The gallery has four rooms totaling 3,000 square feet.


### 9. Negative Parallelisms and Tailing Negations

**Problem:** Constructions like "Not only...but..." or "It is not just about..., it is..." are overused. So are clipped tailing-negation fragments such as "no guessing" or "no wasted motion" tacked onto the end of a sentence instead of written as a real clause.

**Before:**
> It is not just about the beat riding under the vocals; it is part of the aggression and atmosphere. It is not merely a song, it is a statement.

**After:**
> The heavy beat adds to the aggressive tone.

**Before (tailing negation):**
> The options come from the selected item, no guessing.

**After:**
> The options come from the selected item without forcing the user to guess.


### 10. Rule of Three Overuse

**Problem:** LLMs force ideas into groups of three to appear comprehensive.

**Before:**
> The event features keynote sessions, panel discussions, and networking opportunities. Attendees can expect innovation, inspiration, and industry insights.

**After:**
> The event includes talks and panels. There is also time for informal networking between sessions.


### 11. Elegant Variation (Synonym Cycling)

**Problem:** AI has repetition-penalty code causing excessive synonym substitution.

**Before:**
> The protagonist faces many challenges. The main character must overcome obstacles. The central figure eventually triumphs. The hero returns home.

**After:**
> The protagonist faces many challenges but eventually triumphs and returns home.

**Research writing note:** In scientific writing, *repeat the same technical term* rather than cycling synonyms. Reviewers should not have to figure out whether "the cohort", "the sample", and "the participants" refer to the same group.


### 12. False Ranges

**Problem:** LLMs use "from X to Y" constructions where X and Y are not on a meaningful scale.

**Before:**
> Our journey through the universe has taken us from the singularity of the Big Bang to the grand cosmic web, from the birth and death of stars to the enigmatic dance of dark matter.

**After:**
> The book covers the Big Bang, star formation, and current theories about dark matter.


### 13. Passive Voice and Subjectless Fragments

**Problem:** LLMs often hide the actor or drop the subject entirely with lines like "No configuration file needed" or "The results are preserved automatically." Rewrite these when active voice makes the sentence clearer and more direct.

**Before:**
> No configuration file needed. The results are preserved automatically.

**After:**
> You do not need a configuration file. The system preserves the results automatically.

**Research writing note:** Methods sections in many journals use passive intentionally ("Samples were collected and processed within 4 h"). Apply this pattern to Introduction, Results interpretation, Discussion, and grant Approach narrative. In Methods, only fix passives that genuinely obscure who did what. Pattern 44 covers the research-prose form, including aims and hypotheses written as the actor.


## STYLE PATTERNS

### 14. Em Dash Overuse

**Problem:** LLMs use em dashes (—) more than humans, mimicking "punchy" sales writing. In practice, most of these can be rewritten more cleanly with commas, periods, or parentheses.

**Before:**
> The term is primarily promoted by Dutch institutions—not by the people themselves. You do not say "Netherlands, Europe" as an address—yet this mislabeling continues—even in official documents.

**After:**
> The term is primarily promoted by Dutch institutions, not by the people themselves. You do not say "Netherlands, Europe" as an address, yet this mislabeling continues in official documents.

**Research writing note:** Research-skills project rule: no em-dashes anywhere. Use commas or semicolons.


### 15. Overuse of Boldface

**Problem:** AI chatbots emphasize phrases in boldface mechanically.

**Before:**
> It blends **OKRs (Objectives and Key Results)**, **KPIs (Key Performance Indicators)**, and visual strategy tools such as the **Business Model Canvas (BMC)** and **Balanced Scorecard (BSC)**.

**After:**
> It blends OKRs, KPIs, and visual strategy tools like the Business Model Canvas and Balanced Scorecard.

**Research writing note:** Selective bold for gene symbols, variable names, or NIH Specific Aims headers is fine. Mechanical bolding of every defined term is not.


### 16. Inline-Header Vertical Lists

**Problem:** AI outputs lists where items start with bolded headers followed by colons.

**Before:**
> - **User Experience:** The user experience has been significantly improved with a new interface.
> - **Performance:** Performance has been enhanced through optimized algorithms.
> - **Security:** Security has been strengthened with end-to-end encryption.

**After:**
> The update improves the interface, speeds up load times through optimized algorithms, and adds end-to-end encryption.


### 17. Title Case in Headings

**Problem:** AI chatbots capitalize all main words in headings.

**Before:**
> ## Strategic Negotiations And Global Partnerships

**After:**
> ## Strategic negotiations and global partnerships

**Research writing note:** Many journals (IEEE, APA, ACS) require title case. Defer to the journal's submission guide. Apply this pattern only where house style is sentence case or unspecified.


### 18. Emojis

**Problem:** AI chatbots often decorate headings or bullet points with emojis.

**Before:**
> 🚀 **Launch Phase:** The product launches in Q3
> 💡 **Key Insight:** Users prefer simplicity
> ✅ **Next Steps:** Schedule follow-up meeting

**After:**
> The product launches in Q3. User research showed a preference for simplicity. Next step: schedule a follow-up meeting.

**Research writing note:** Research-skills project rule: no emojis in commits, PRs, code, or prose. Strip on sight.


### 19. Curly Quotation Marks

**Problem:** ChatGPT uses curly quotes ("...") instead of straight quotes ("...").

**Before:**
> He said "the project is on track" but others disagreed.

**After:**
> He said "the project is on track" but others disagreed.

**Research writing note:** For LaTeX manuscripts use `` `` ... '' `` (LaTeX renders straight). For Word/Markdown, follow the publisher's manuscript prep guide.


## COMMUNICATION PATTERNS

### 20. Collaborative Communication Artifacts

**Words to watch:** I hope this helps, Of course!, Certainly!, You are absolutely right!, Would you like..., let me know, here is a...

**Problem:** Text meant as chatbot correspondence gets pasted as content.

**Before:**
> Here is an overview of the French Revolution. I hope this helps! Let me know if you would like me to expand on any section.

**After:**
> The French Revolution began in 1789 when financial crisis and food shortages led to widespread unrest.


### 21. Knowledge-Cutoff Disclaimers

**Words to watch:** as of [date], Up to my last training update, While specific details are limited/scarce..., based on available information...

**Problem:** AI disclaimers about incomplete information get left in text.

**Before:**
> While specific details about the company's founding are not extensively documented in readily available sources, it appears to have been established sometime in the 1990s.

**After:**
> The company was founded in 1994, according to its registration documents.


### 22. Sycophantic/Servile Tone

**Problem:** Overly positive, people-pleasing language.

**Before:**
> Great question! You are absolutely right that this is a complex topic. That is an excellent point about the economic factors.

**After:**
> The economic factors you mentioned are relevant here.

**Research writing note:** Response-to-reviewer letters are a frequent home for this. "We thank the reviewer for this excellent and insightful comment" can be tightened to "We thank the reviewer for this comment" or simply addressed directly.


## FILLER AND HEDGING

### 23. Filler Phrases

**Before → After:**
- "In order to achieve this goal" → "To achieve this"
- "Due to the fact that it was raining" → "Because it was raining"
- "At this point in time" → "Now"
- "In the event that you need help" → "If you need help"
- "The system has the ability to process" → "The system can process"
- "It is important to note that the data shows" → "The data shows"


### 24. Excessive Hedging

**Problem:** Over-qualifying statements.

**Before:**
> It could potentially possibly be argued that the policy might have some effect on outcomes.

**After:**
> The policy may affect outcomes.

**Research writing note:** Single hedges in Discussion are fine and often required. Strip stacked hedges ("could potentially possibly") to a single appropriate hedge ("may" or "suggests"). Do not strip to bare assertions you cannot defend with evidence.


### 25. Generic Positive Conclusions

**Problem:** Vague upbeat endings.

**Before:**
> The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence. This represents a major step in the right direction.

**After:**
> The company plans to open two more locations next year.

**Research writing note:** "This work opens exciting new avenues" is the classic Discussion-section AI tell. Replace with specific next steps: "Future work will test this in subjects with X."


### 26. Hyphenated Word Pair Overuse

**Words to watch:** third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end

**Problem:** AI hyphenates common word pairs with perfect consistency. Humans rarely hyphenate these uniformly, and when they do, it is inconsistent. Less common or technical compound modifiers are fine to hyphenate.

**Before:**
> The cross-functional team delivered a high-quality, data-driven report on our client-facing tools. Their decision-making process was well-known for being thorough and detail-oriented.

**After:**
> The cross functional team delivered a high quality, data driven report on our client facing tools. Their decision making process was known for being thorough and detail oriented.

**Research writing note:** Established compound modifiers used as adjectives before a noun ("high-throughput sequencing", "single-cell RNA-seq") stay hyphenated per scientific style. Strip only the generic management-speak hyphens.


### 27. Persuasive Authority Tropes

**Phrases to watch:** The real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter

**Problem:** LLMs use these phrases to pretend they are cutting through noise to some deeper truth, when the sentence that follows usually just restates an ordinary point with extra ceremony.

**Before:**
> The real question is whether teams can adapt. At its core, what really matters is organizational readiness.

**After:**
> The question is whether teams can adapt. That mostly depends on whether the organization is ready to change its habits.


### 28. Signposting and Announcements

**Phrases to watch:** Let us dive in, let us explore, let us break this down, here is what you need to know, now let us look at, without further ado

**Problem:** LLMs announce what they are about to do instead of doing it. This meta-commentary slows the writing down and gives it a tutorial-script feel.

**Before:**
> Let us dive into how caching works in Next.js. Here is what you need to know.

**After:**
> Next.js caches data at multiple layers, including request memoization, the data cache, and the router cache.


### 29. Fragmented Headers

**Signs to watch:** A heading followed by a one-line paragraph that simply restates the heading before the real content begins.

**Problem:** LLMs often add a generic sentence after a heading as a rhetorical warm-up. It usually adds nothing and makes the prose feel padded.

**Before:**
> ## Performance
>
> Speed matters.
>
> When users hit a slow page, they leave.

**After:**
> ## Performance
>
> When users hit a slow page, they leave.


## RESEARCH AND GRANT PROSE PATTERNS

These patterns come from revising AI-assisted grant and paper drafts that had already passed patterns 1 to 29 (no promotional words, em dashes, or filler).
The tells that remain are in sentence shape.
Each shape is normal in human writing once or twice a page; what gives a draft away is density, when most sentences on a page share the same shape.
Count them with the quick scan below and rewrite until no shape repeats more than once or twice per 500 words.
Patterns 44 and 45 are about who acts and what each pronoun refers to; their counts measure density, and single hits are often fine.
Every After below keeps the facts of its Before.
Purpose clauses, restatements, and freshness markers may go; a rewrite that adds, drops, or softens a fact, a caveat, or a registration label is wrong, however natural it sounds, except that pattern 33 removes disclosures that add nothing a reader needs to interpret a result or make a decision, never a caveat that changes how a result is read.

What the patterns share matters more than their wording.
The quoted phrases are examples, and a sentence that does the same job in other words is the same pattern.
Four ideas cover them:

- **Show, do not announce.** The text states the result or the limitation and lets it stand; it does not certify its own honesty, rigor, or timeliness, and it does not volunteer limitations for their own sake (patterns 33, 42).
- **Say it once.** Each sentence adds a fact; tails, kickers, repeated glosses, and repeated absolutes restate one already given (patterns 30, 35, 37, 39).
- **Literal over clever.** Claims use plain verbs and plain comparisons, not slogans, contests, reveals, scripted answers, or verbs of standing (patterns 31, 32, 36, 38, 41, 43).
- **The reader never guesses.** Who acted, what each word points to, and which qualification belongs to which result are on the page (patterns 40, 44, 45); an objection is answered where it arises (pattern 34).

### 30. Purpose Tails ("so" Payoffs)

**Words to watch:** ", so a", ", so only", ", so the", ", so that", ", which means", "; this ensures", "; the X matters because"

**Problem:** The sentence states a method or a fact, then appends a clause that restates its purpose in simpler words, as if the reader might miss it.
When most methods sentences end this way, the text keeps explaining itself.
Related: pattern 3 (-ing tails such as "ensuring") and pattern 9 (tailing negations).

**Before:**
> The null shuffles which tags each image has but keeps how many it has, so a gain must come from what the tags say. Folds hold out whole subjects, so the results generalize across people. The code is on GitHub, so others can reuse it.

**After:**
> To separate the content of the tags from their number, the null shuffles which tags each image has and keeps how many. Folds hold out whole subjects. The code is on GitHub.

**Research writing note:** Keep a purpose clause where a reviewer would otherwise ask "why?", and lead with it ("To separate X from Y, ..."), as in the first sentence above.
Drop it where the purpose is obvious to the field, as in the other two.
"So that" and "which means" are ordinary connectors and become a problem only in bulk.


### 31. Talking Data

**Words to watch:** data, results, tags, curves, models, or tests that "say", "tell", "show us", "know", "carry", "name", or "decide"; "what the X says"

**Problem:** Evidence and objects are cast as speakers and agents.
It sounds friendly and explanatory, and it hides the quantity that was measured.

**Before:**
> What the annotations say matters more than how much they say. The curve tells laboratories where to stop, and the permutation test decides each result.

**After:**
> The content of the annotations predicts more than their length. Laboratories can stop annotating at the level where the curve saturates. Each result is judged against a permutation null.


### 32. Mirrored Aphorisms

**Problem:** Two clauses with matching syntax land a neat contrast or symmetry: "fMRI shows where, EEG shows when"; "the participant is the same, and here so is the moment"; "readable but coarse, rich but opaque".
One, placed where the idea matters most, can be memorable.
Several read as composed by formula and turn the argument into slogans.
Related: pattern 9 (negative parallelisms) and pattern 10 (rule of three).

**Before:**
> Labels are readable but coarse; model features are rich but opaque. fMRI shows which features a region weights, and EEG shows when.

**After:**
> Labels are readable but coarse, and model features are rich but opaque. We map the feature weights of each region with fMRI and time them with EEG.

The After keeps one contrast, the one the paragraph is about, and states the second idea plainly.


### 33. Self-Certifying Candor and Gratuitous Disclosure

**Words to watch:** "and we say so", "we say it first", "we say this up front", "we state plainly", "to be clear", "to be honest", "honestly", "candidly", "frankly", "we flag this openly", "we report this honestly", "to be transparent", "in fairness", "we do not hide", "we claim X only for Y", "we do not trust X", "not an oracle", "we are careful to"

**Problem:** The text announces its own honesty or rigor instead of showing it.
Reviewers read it as defensive, and it is a common residue of prompting a model to "be honest about limitations".
The same prompting leaves a second habit: limitations volunteered for their own sake.
A sentence that admits what the work did not set out to do, or that some other approach exists, often adds nothing a reader needs to interpret a result or make a decision.
Related: pattern 24 (excessive hedging), pattern 27 (persuasive authority tropes), and pattern 34 (pre-emptive objection packaging).
If the caveat answers a real objection, move it to where the objection arises and answer it once (pattern 34); cut it only when it informs no one.

**Before:**
> The tool is preliminary, weak on actions, and we say so. We do not trust it; we treat it as an instrument, not an oracle. Aim 3 validates each tag against trained annotators.

**After:**
> The tool is preliminary and weak on actions. Aim 3 validates each tag against trained annotators.

**Before (gratuitous disclosure in Specific Aims):**
> We compare three architectures in two cohorts. To be clear, we did not test every possible architecture, and other approaches to this question exist.

**After:**
> We compare three architectures in two cohorts.

The scope is already on the page, so the disclaimers add nothing a reader needs.
A caveat that would change how the comparison is read stays: an exclusion that depended on the outcome, a possible leak of test labels into training, or a confound the design cannot remove.

**Research writing note:** Be truthful, not exhaustive.
A proposal or a paper makes a case, and open questions are often what the work sets out to answer; frame them that way when that is true, and never state or imply anything false.
Never cut a disclosure that an institution, journal, or funder requires: conflicts of interest, overlap with other support, prior or duplicate publication, deviations from a registered plan, data exclusions, and ethics statements.
Keep every limitation, scope statement, and caveat that rigor sections, reporting guidelines, a Limitations section, a Potential Problems and Alternatives section, or a reviewer's question require, and any caveat that changes how a result should be read.
Elsewhere, and above all in persuasive sections (Specific Aims, Significance, abstracts, cover letters, funding requests), cut a disclosure that adds nothing a reader needs to interpret a result or make a decision, and remove the self-congratulation around the caveats that stay.
Pattern 24 still applies to what remains: keep the single hedge a claim needs.


### 34. Pre-emptive Objection Packaging

**Words to watch:** "X also limits ..., but ...", "X is not the only ...", "admittedly", "while X predicts as well, ...", "although X, Y"

**Problem:** Paragraph after paragraph concedes an imagined objection and rebuts it in the same sentence.
Answering a real objection once, with evidence, is good argument; doing it everywhere reads like a defensive essay.
Related: pattern 24 (excessive hedging).

**Before:**
> Sample size is not the only limit on these datasets, but it has mature tools, and the stimulus description has none. A pretrained model predicts as well, but its features cannot be read. Richer annotation costs more, but it pays off.

**After:**
> Sample size has mature tools. The description of the stimulus has none.

The other two objections move to the paragraphs that report the model comparison and the cost of annotation, and are answered there, once.

**Research writing note:** "Although" and "but" are ordinary connectors, and a grant must answer the objections its reviewers raised.
What to remove is a concession in every paragraph.


### 35. Repeated Inline Glosses

**Problem:** A technical term carries an appositive definition every time it appears ("annotation tuning, the weight a region gives each tag, ...").
Writers define a term once and then trust the reader.
Related: pattern 11 (keep the same term once it is defined).

**Before:**
> Annotation tuning, the weight a region gives each tag, agreed at two sites. We will test whether annotation tuning, the weight a region gives each tag, peaks at matched locations.

**After:**
> Annotation tuning (the weight a region gives each tag) agreed at two sites. We will test whether annotation tuning peaks at matched locations.

**Research writing note:** In a grant, define a term once in each separately read document (Specific Aims, Introduction, Research Strategy), not again within one.


### 36. Colon Reveals

**Words to watch:** "The answer is simple:", "The premise is now narrower:", "X is preliminary:", "The key is this:", and any sentence whose colon introduces the actual claim

**Problem:** A setup clause, a colon, then the point.
Once or twice a page is fine; more creates a drumbeat of reveals.
A colon that introduces a list or a definition is not a reveal.
Related: pattern 16 (inline headers) and pattern 28 (signposting).

**Before:**
> The premise is now narrower: the field has a standard but lacks the tools to use it.

**After:**
> The field has a standard but lacks the tools to use it.


### 37. Absolute Guards

**Words to watch:** "never", "only", "always", "every", "no ... at all", "at no point"

**Problem:** Absolutes repeated as reassurance.
Where a rule is real, state it once, in the methods or rigor section; elsewhere describe what is done.

**Before:**
> We never pool signals across cohorts. The three tests are never combined, and models never see the test images. We compare the modalities only through the tags.

**After (rigor section, once):**
> Signals from different cohorts are not pooled, the three tests are not combined, and test images are held out of training.

**After (methods):**
> We compare the modalities only through the tags.

**Research writing note:** "Only" and "never" often state a real constraint ("only the registered analysis is confirmatory"); keep those, once.


### 38. Answering the Heading

**Problem:** In responses to reviewers and other question-headed text, the answer starts with "Then", "Exactly", or a restated question.
The exchange then reads as scripted.
Related: pattern 29 (fragmented headers).

**Before:**
> **What if richer is not better?** Then the curve flattens, and that tells laboratories where to stop.

**After:**
> **What if richer is not better?** A flat annotation-response curve marks the level where laboratories can stop annotating.

**Research writing note:** In a response to reviewers, a direct "Yes." or "No." followed by the evidence is conventional and good; only the scripted "Then" should go.


### 39. Kicker Sentences

**Problem:** A short last sentence restates the paragraph as a takeaway.
Delete it; the evidence sentence before it is the ending.
Related to pattern 25 (generic positive conclusions), at paragraph scale.

**Before:**
> The category contrast predicted 0.12 of the variance and the annotations 0.62. The gain comes from the tags the classic contrast leaves out.

**After:**
> The category contrast predicted 0.12 of the variance and the annotations 0.62.

**Research writing note:** A closing sentence that links a paragraph to an aim, or states the gap the paragraph exposes, is expected in grants; delete only a pure restatement.


### 40. Stacked Coordination

**Problem:** Two "and"s in one phrase with no comma ("in A and B (...) and in C"), or long sentences assembled from qualifications glued with "and".
Use the series comma and one "and", split long sentences, and give each qualification its own sentence.
When the items are results, list the strongest first and keep each result's label with it.

**Before:**
> They improved prediction in 4 of 5 lobes and all 6 regions (a test registered after a first look at those data) and in 7 of 11 parcels (registered before any parcel value was seen).

**After:**
> They improved prediction in all 6 regions, 4 of 5 lobes, and 7 of 11 parcels. The region and lobe test was registered after a first look at those data. The parcel test was registered before any parcel value was seen.


### 41. Contest Metaphors for Statistics

**Words to watch:** "beat the null", "clear the bar", "set the bar", "the bar is low", "wins", "outperforms" (when nothing competes)

**Problem:** Statistical comparisons framed as contests.

**Before:**
> The tags beat the null in six regions, clearing a low bar set by the low-level features.

**After:**
> The tags exceeded the null in six regions. The low-level features alone predicted little.


### 42. Freshness Markers

**Words to watch:** "now", "today", "currently", "increasingly", "no longer", "for the first time"

**Problem:** Sprinkled to make claims feel timely.
Related: pattern 1 (significance inflation).

**Before:**
> Shared datasets now record the brain in three modalities, and every test now includes a matched null.

**After:**
> Shared datasets record the brain in three modalities, and every test includes a matched null.

**Research writing note:** Keep a marker where the text contrasts with a stated earlier time, as in a resubmission's list of changes ("The A1 now includes ..."), or where it is literal ("currently recruiting").


### 43. Abstract Verbs of Standing

**Words to watch:** "rests on", "reads as", "counts as", "sits between", "lies at", "holds", "speaks to", "points to"

**Problem:** Relations stated with positional verbs instead of is, has, uses, or a concrete verb.
Overlaps pattern 8.

**Before:**
> The innovation rests on two methods, and a gain reads as unique variance when the calibration allows it.

**After:**
> The innovation is in two methods. A gain is interpreted as unique variance when the calibration allows it.

**Research writing note:** These verbs are literal in anatomy and statistics ("the lesion lies at", "the assumption holds"); leave those.


### 44. Hidden Actors

**Words to watch:** "is/are/was/were" plus a past participle in narrative prose ("was registered", "is rebuilt", "were chosen"); an aim, hypothesis, goal, or analysis as the one doing a person's work ("Aim 3 tests", "Hypothesis 1B tests", "the analysis asks")

**Problem:** The sentence hides who did the work, behind a passive verb or behind a part of the document.
Readers must infer the actor, and statements about what the team did and when (registering a test, choosing units after seeing data, excluding participants) read as evasive.
Grant and paper readers expect "we" for the team's actions.
Related: pattern 13 (passive voice) and pattern 31 (talking data).

**Before:**
> Aim 3 is rebuilt on recordings that share the participant and the stimulus. The test was registered after a first look at the EEG data, before any fMRI value was seen. Hypothesis 1B tests location specificity directly.

**After:**
> We rebuilt Aim 3 on recordings that share the participant and the stimulus. We registered the test after a first look at the EEG data, before seeing any fMRI value. We test location specificity directly in Hypothesis 1B.

**Research writing note:** Passives in Methods that match journal style stay (pattern 13).
A part of the document can stay the subject when it is the topic rather than an actor ("Aim 2 has two hypotheses", "Figure 3 shows the three tests"); rewrite the ones that perform a person's act, such as registering, choosing, excluding, testing, or rebuilding.
Keep every timing and registration detail: "we registered X before seeing Y" must say exactly what "X was registered before Y was seen" said.
Confirm who acted before writing "we"; if another group recorded, registered, or chose something, name that group.
On single-investigator mechanisms (K, F, DP2), "I" is the actor for the applicant's own work.


### 45. Unanchored Pronouns

**Words to watch:** a sentence that opens with "It", "Its", "They", "This", or "These" and points back across a sentence; "it" or "its" twice in one sentence; "this level", "this test", or "this approach" when that noun did not appear just before

**Problem:** The draft chains sentences with pronouns; the reader must hold the referent in mind or search back for the noun.
When two nouns could fit, the sentence turns ambiguous, and in research prose the ambiguity often falls on the claim, such as whose prediction a model recovered or which test was registered.
Repeating the technical noun costs the reader less than a pronoun and keeps the terms consistent (pattern 11).

**Before:**
> We compared HEDit with one human annotator. It agreed best on objects, and against the COCO labels, it was 0.79 to 0.95. CLIP predicts somewhat more than the tags, but the tags recover most of its prediction and add prediction beyond it. A flat curve marks where more annotation adds no prediction. We will build tools that find this level.

**After:**
> We compared HEDit with one human annotator. HEDit agreed with the annotator best on objects, and against the COCO labels, HEDit's agreement was 0.79 to 0.95. CLIP predicts somewhat more than the tags, but the tags recover most of CLIP's prediction and add prediction beyond CLIP. A flat curve marks the level where more annotation adds no prediction. We will build tools that find this level.

**Research writing note:** Do not replace every pronoun.
"HEDit inherits the biases of its models" is clear, because the referent is the subject of the same clause and no other noun competes.
Rewrite when the referent sits in an earlier sentence, when two nouns could fit (HEDit or the annotator above), when the pronoun stands for a noun the text never wrote (the agreement above), or when "this" or "these" has no matching noun just before it; the fix may be to add the noun to the earlier sentence, as in the last pair above.
In documents read in pieces, such as Specific Aims or one section of an Approach, name the subject again at the start of each paragraph.


### Quick scan

The counts run on flattened text, so a pattern split by a semantic line break is still found, and LaTeX comment lines are dropped.
Review every hit by hand: most are fine one at a time, and the count per 500 words is what matters.

```bash
flat()  { grep -v '^[[:space:]]*%' "$1" | tr -s '[:space:]' ' '; }
count() { flat "$1" | grep -oiE "$2" | wc -l; }
count FILE ', so [a-z]+ |, which means|; this ensures|matters because'          # 30 purpose tails
count FILE 'we say (so|it|this)\b|to be (clear|honest|transparent)\b|\b(honestly|candidly|frankly)\b|stat(e|es|ed) (it |this )?plainly|plainly stat(e|es|ed)|in fairness|we do not hide|we are careful to|not an oracle'  # 33 candor markers only; gratuitous disclosures have no marker, so read for them
count FILE '\b(says?|tells?|carr(y|ies)|names?|decides?)\b'                     # 31 talking data
flat FILE | grep -oE ': [a-z]' | wc -l                                          # 36 colons (reveals and lists; case-sensitive)
count FILE '\b(never|only|always)\b'                                            # 37 absolute guards
count FILE ' and [^,;:.]{1,70} and '                                            # 40 stacked coordination
count FILE '\b(beats?|bar|wins?|outperforms?)\b'                                # 41 contest metaphors
count FILE '\b(now|today|currently|increasingly|no longer|for the first time)\b' # 42 freshness markers
count FILE 'rests on|reads as|counts as|sits between|lies at'                   # 43 abstract verbs (holds, speaks to, points to: often literal, check by eye)
count FILE '\b(is|are|was|were|be|been|being) ((not|also|then|[a-z]+ly) )?([a-z]+(ed|en|wn)|(re|un|over|up)?(built|found|made|held|set|kept|run|sent|left|lost|put|done|led|met|paid|read|split|cut|spent|told|brought|taught|thought|bought|won))\b'  # 44 passive verbs (also counts -en words such as open, even, often, between; Methods passives are often fine)
count FILE '\b(aim|hypothesis|goal) [0-9]+[a-z]? (tests?|asks?|measures?|compares?|fits?|uses?|validates?|develops?|repeats?)\b'  # 44 document parts as actors
flat FILE | grep -oE '(^|[.;?!] )([^ ]*[{(*"])?(It|Its|They|Their|This|These) ' | wc -l  # 45 sentence-initial pronouns, also after **, (, ", or \textbf{ (case-sensitive; also counts "This test" and "It is clear")
count FILE '\b(it|its)\b'                                                       # 45 it and its (density; most single hits are fine)
flat FILE | wc -w                                                               # words, for hits per 500 words
```

To find a hit, run the same expression with `grep -niE` on the file; a hit that spans a line break shows only in the count.

Patterns 44 and 45 measure density, not a shape to drive to zero, and the once-or-twice-per-500-words rule above does not apply to them.
As a reference rather than a pass mark: in one NIH Research Strategy of about 10,000 words, a revision for these two patterns took passive verbs from 5.9 to 1.9 per 500 words, aims and hypotheses as actors from 0.9 to 0.5, sentence-initial pronouns from 0.4 to 0.05, and "it" or "its" from 6.4 to 2.7.

---
