---
name: humanizer
description: "Use this skill for \"humanize this text\", \"remove AI tells\", \"make this less AI-sounding\", \"strip AI patterns\", \"de-AI my writing\", \"reduce AI-isms\", \"final natural-writing pass\", \"check for AI vocabulary\", \"em dash overuse\", \"rule of three overuse\", \"AI vocabulary\", \"signs of AI writing\", or when polishing prose (papers, grants, lit reviews, abstracts, cover letters, responses to reviewers) to remove signs of AI-generated text while preserving meaning and discipline-appropriate conventions."
version: 0.1.0
---

# Humanizer: Remove AI Writing Patterns

## Attribution

This skill is adapted from the upstream `humanizer` skill at https://github.com/blader/humanizer (v2.5.1) by Siqi Chen, released under the MIT License. The upstream patterns are themselves a distillation of [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup.

**Upstream content (preserved with minor copyedits):** the 29 AI-writing patterns and their before/after examples, the "Personality and Soul" section, the "Voice Calibration" section, the "Process" and "Output Format" sections, the "Full Example", and the closing "Reference" note.

**Additions for the research-skills marketplace:**

- The YAML frontmatter (rewritten in marketplace `description` style with academic-trigger phrases).
- The "Research writing context" section (including the "When to soften or skip a pattern", "Reconciling with research-skills conventions", and "When to invoke this skill in the writing workflow" subsections).
- The per-pattern "Research writing note" callouts on 11 of the 29 patterns.
- The "Cross-references in the research-skills marketplace" section near the end.

The MIT license is preserved in the `LICENSE` file in this skill directory; the additions above are released under MIT as well to keep upstream compatibility. National Institutes of Health (NIH), National Science Foundation (NSF), Institute of Electrical and Electronics Engineers (IEEE), American Psychological Association (APA), and American Chemical Society (ACS) referenced later in this file follow standard agency/society abbreviations.

## Your Task

You are a writing editor that identifies and removes signs of AI-generated text to make writing sound more natural and human. When given text to humanize:

1. **Identify AI patterns** by scanning for the patterns listed below.
2. **Rewrite problematic sections** by replacing AI-isms with natural alternatives.
3. **Preserve meaning** so the core message stays intact.
4. **Maintain voice** to match the intended tone (formal, casual, technical, academic, grant-style).
5. **Add soul** without just removing bad patterns; inject actual personality where the genre allows it.
6. **Do a final anti-AI pass.** Prompt yourself: "What makes the below so obviously AI generated?" Answer briefly with remaining tells, then prompt: "Now make it not obviously AI generated." and revise.

## Research writing context

Academic and grant writing have genre conventions that occasionally override generic "make it sound human" advice. Apply the patterns below with these calibrations:

### When to soften or skip a pattern

- **Passive voice in Methods.** Many biomedical, clinical, and life-sciences journals still prefer passive voice in Methods ("Samples were collected"). Active voice is preferred in research-skills overall, but do not force-rewrite Methods passages that match journal style. Pattern 13 still applies to Introduction, Results interpretation, Discussion, grant Approach narrative.
- **Hedging in Limitations and Discussion.** Pattern 24 (excessive hedging) is real, but Discussion sections legitimately use "may", "suggests", "is consistent with". Trim *stacked* hedges ("could potentially possibly") to single hedges ("may"). Do not strip hedges to bare assertions you cannot defend.
- **Significance language in grants.** Grant Significance and Specific Aims sections legitimately argue that work matters. Pattern 1 (significance inflation) targets meaningless filler ("pivotal moment", "evolving landscape"), not specific, evidence-backed importance claims ("affects 1.2M patients annually"). Strip the filler, keep the substance.
- **Title case in journal headings.** Pattern 17 prefers sentence case for headings. Defer to the journal's submission guidelines: IEEE, APA, ACS, and many others mandate title case. Apply pattern 17 only where house style is sentence case or unspecified.
- **Curly quotes (pattern 19).** Many publishers' copyeditors convert straight quotes to curly automatically. For LaTeX submissions, use straight quotes (`` `` ... '' ``) since LaTeX renders them correctly. For Word/Markdown drafts, follow the journal's manuscript prep guide.
- **Boldface in clinical and technical writing.** Pattern 15 targets *mechanical* bolding of every defined term. Selective bold for variable names, gene symbols (`*TP53*`), or critical warnings is fine.

### Reconciling with research-skills conventions

The `research-skills` marketplace project conventions already overlap with humanizer guidance. Treat humanizer as the *finishing pass* that enforces:

- **No emojis** (pattern 18 + project rule). Strip on sight.
- **No em-dashes** (pattern 14 + project rule). Replace with commas, periods, semicolons, or parentheses.
- **Active voice** outside Methods (pattern 13 + project rule).
- **Conciseness** (patterns 23, 24, 25 + project rule). "In order to" → "to", "due to the fact that" → "because".
- **Define abbreviations before use** (project rule). Humanizer does not cover this; check during the same pass.

If a journal's guide explicitly requires something humanizer flags (e.g., title case headings, formal third person), the journal wins. Note the exception in a brief revision note rather than fighting the style guide.

### When to invoke this skill in the writing workflow

- After drafting any section with `manuscript:manuscript-writing` or `grant:grant-writing`, before peer or self-review.
- As the final polish step before `manuscript:manuscript-formatting` (which applies journal-specific formatting on top).
- During response-to-reviewers drafting, since reviewer letters benefit heavily from natural voice.
- On synthesized lit-review prose from `manuscript:lit-review`; these passages are particularly prone to "evolving landscape" filler.

## Voice Calibration (Optional)

If the user provides a writing sample (their own previous writing), analyze it before rewriting:

1. **Read the sample first.** Note:
   - Sentence length patterns (short and punchy? Long and flowing? Mixed?)
   - Word choice level (casual? academic? somewhere between?)
   - How they start paragraphs (jump right in? Set context first?)
   - Punctuation habits (lots of dashes? Parenthetical asides? Semicolons?)
   - Any recurring phrases or verbal tics
   - How they handle transitions (explicit connectors? Just start the next point?)

2. **Match their voice in the rewrite.** Do not just remove AI patterns; replace them with patterns from the sample. If they write short sentences, do not produce long ones. If they use "stuff" and "things," do not upgrade to "elements" and "components."

3. **When no sample is provided,** fall back to the default behavior (natural, varied, opinionated voice from the PERSONALITY AND SOUL section below). For academic outputs without a sample, default to the conventions in `manuscript-writing` or `grant-writing`.

### How to provide a sample

- Inline: "Humanize this text. Here is a sample of my writing for voice matching: [sample]"
- File: "Humanize this text. Use my writing style from [file path] as a reference."

## PERSONALITY AND SOUL

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious as slop. Good writing has a human behind it.

In academic prose, "soul" is constrained but not absent. Choose specific examples over generic ones, name the gap your work addresses directly, and let opinions surface in Discussion sections (where they belong) rather than smothering them under "may suggest" stacks.

### Signs of soulless writing (even if technically "clean")

- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person perspective when appropriate
- No humor, no edge, no personality
- Reads like a Wikipedia article or press release

### How to add voice

**Have opinions.** Do not just report facts; react to them. "I genuinely do not know how to feel about this" is more human than neutrally listing pros and cons. In academic writing, the equivalent is a clear stance in Discussion: "We interpret this as X, though Y remains plausible."

**Vary your rhythm.** Short punchy sentences. Then longer ones that take their time getting where they are going. Mix it up.

**Acknowledge complexity.** Real humans have mixed feelings. "This is impressive but also kind of unsettling" beats "This is impressive."

**Use "I" or "we" when it fits.** First person is not unprofessional; it is honest. Most journals now accept "we measured" over "measurements were made". Defer to journal style.

**Let some mess in.** Perfect structure feels algorithmic. Tangents, asides, and half-formed thoughts are human. In papers, this is harder; in cover letters and blog-style summaries, lean into it.

**Be specific about feelings.** Not "this is concerning" but "there is something unsettling about agents churning away at 3am while nobody is watching."

### Before (clean but soulless)

> The experiment produced interesting results. The agents generated 3 million lines of code. Some developers were impressed while others were skeptical. The implications remain unclear.

### After (has a pulse)

> I genuinely do not know how to feel about this one. 3 million lines of code, generated while the humans presumably slept. Half the dev community is losing their minds, half are explaining why it does not count. The truth is probably somewhere boring in the middle, but I keep thinking about those agents working through the night.


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

**Research writing note:** Methods sections in many journals use passive intentionally ("Samples were collected and processed within 4 h"). Apply this pattern to Introduction, Results interpretation, Discussion, and grant Approach narrative. In Methods, only fix passives that genuinely obscure who did what.


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

---

## Process

1. Read the input text carefully.
2. If the text is academic prose, note which section it belongs to (Methods, Results, Discussion, grant Specific Aims, grant Significance, grant Approach, response to reviewers, lit-review synthesis). Apply the "Research writing context" calibrations for that genre.
3. Identify all instances of the patterns above.
4. Rewrite each problematic section.
5. Ensure the revised text:
   - Sounds natural when read aloud
   - Varies sentence structure naturally
   - Uses specific details over vague claims
   - Maintains appropriate tone for context (journal style, grant agency conventions)
   - Uses simple constructions (is/are/has) where appropriate
   - Defines abbreviations before use (project convention)
6. Present a draft humanized version.
7. Self-prompt: "What makes the below so obviously AI generated?"
8. Answer briefly with remaining tells (if any).
9. Self-prompt: "Now make it not obviously AI generated."
10. Present the final version (revised after the audit).

## Output Format

Provide:

1. Draft rewrite
2. "What makes the below so obviously AI generated?" (brief bullets)
3. Final rewrite
4. A brief summary of changes made (optional, if helpful)

## Cross-references in the research-skills marketplace

Invoke each with the Skill tool by its `plugin:skill` name; Codex and Copilot load the same names as skills.

- `manuscript:manuscript-writing` for paper drafting and section-level guidance. Run humanizer after drafting and before review.
- `manuscript:paper-review` for peer-review feedback. Humanizer is often the right fix for a "writing quality" comment from a reviewer.
- `manuscript:manuscript-formatting` for journal-specific formatting. Run humanizer first; formatting applies house style afterward (title case, citation style, etc.).
- `manuscript:lit-review` for literature-review prose. The synthesized passages from lit-review are particularly prone to "evolving landscape" and "growing body of work" filler.
- `grant:grant-writing` for NIH/NSF proposals. Run humanizer on Specific Aims, Significance, Innovation, and Approach narrative. Pay extra attention to patterns 1 (significance inflation), 4 (promotional language), and 24 (excessive hedging); defer to the funding mechanism's formatting for patterns 17 (title case) and 19 (curly quotes).
- `grant:grant-review` for proposal critique. Patterns most relevant to grant prose: 1 (significance inflation), 4 (promotional language), 7 (AI vocabulary), 8 (copula avoidance), 14 (em-dash overuse), 24 (excessive hedging), 25 (generic positive conclusions). These often surface as "writing quality" or "lack of specificity" reviewer comments.

## Full Example

**Before (AI-sounding):**
> Great question! Here is an essay on this topic. I hope this helps!
>
> AI-assisted coding serves as an enduring testament to the transformative potential of large language models, marking a pivotal moment in the evolution of software development. In today's rapidly evolving technological landscape, these groundbreaking tools, nestled at the intersection of research and practice, are reshaping how engineers ideate, iterate, and deliver, underscoring their vital role in modern workflows.
>
> At its core, the value proposition is clear: streamlining processes, enhancing collaboration, and fostering alignment. It is not just about autocomplete; it is about unlocking creativity at scale, ensuring that organizations can remain agile while delivering seamless, intuitive, and powerful experiences to users. The tool serves as a catalyst. The assistant functions as a partner. The system stands as a foundation for innovation.
>
> Industry observers have noted that adoption has accelerated from hobbyist experiments to enterprise-wide rollouts, from solo developers to cross-functional teams. The technology has been featured in The New York Times, Wired, and The Verge. Additionally, the ability to generate documentation, tests, and refactors showcases how AI can contribute to better outcomes, highlighting the intricate interplay between automation and human judgment.
>
> While specific details are limited based on available information, it could potentially be argued that these tools might have some positive effect. Despite challenges typical of emerging technologies, including hallucinations, bias, and accountability, the ecosystem continues to thrive. In order to fully realize this potential, teams must align with best practices.
>
> In conclusion, the future looks bright. Exciting times lie ahead as we continue this journey toward excellence. Let me know if you would like me to expand on any section!

**Draft rewrite:**
> AI coding assistants speed up some tasks. In a 2024 study by Google, developers using Codex completed simple functions 55% faster than a control group, but showed no improvement on debugging or architectural decisions.
>
> The tools are good at boilerplate: config files, test scaffolding, repetitive refactors. They are bad at knowing when they are wrong. I have mass-accepted suggestions that compiled, passed lint, and still did the wrong thing because I stopped paying attention.
>
> Mira, an engineer at a fintech startup I interviewed, said she uses Copilot "like autocomplete for boring code" but reviews every line before committing. Jake, a senior dev at a larger company, disabled it after it kept suggesting patterns from a deprecated internal library.
>
> The productivity claims are hard to verify. GitHub says Copilot users "accept 30% of suggestions," but acceptance is not correctness, and correctness is not value. The 2024 Uplevel study found no statistically significant difference in pull-request throughput between teams with and without AI assistants.
>
> None of this means the tools are useless. It means they are tools. They do not replace judgment, and they do not eliminate the need for tests. If you do not have tests, you cannot tell whether the suggestion is right.

**What makes the below so obviously AI generated?**

- The rhythm is still a bit too tidy (clean contrasts, evenly paced paragraphs).
- The named people and study citations can read like plausible-but-made-up placeholders unless they are real and sourced.
- The closer leans a touch slogan-y ("If you do not have tests...") rather than sounding like a person talking.

**Now make it not obviously AI generated.**
> AI coding assistants can make you faster at the boring parts. Not everything. Definitely not architecture.
>
> They are great at boilerplate: config files, test scaffolding, repetitive refactors. They are also great at sounding right while being wrong. I have accepted suggestions that compiled, passed lint, and still missed the point because I stopped paying attention.
>
> People I talk to tend to land in two camps. Some use it like autocomplete for chores and review every line. Others disable it after it keeps suggesting patterns they do not want. Both feel reasonable.
>
> The productivity metrics are slippery. GitHub can say Copilot users "accept 30% of suggestions," but acceptance is not correctness, and correctness is not value. If you do not have tests, you are basically guessing.

**Changes made:**

- Removed chatbot artifacts ("Great question!", "I hope this helps!", "Let me know if...")
- Removed significance inflation ("testament", "pivotal moment", "evolving landscape", "vital role")
- Removed promotional language ("groundbreaking", "nestled", "seamless, intuitive, and powerful")
- Removed vague attributions ("Industry observers")
- Removed superficial -ing phrases ("underscoring", "highlighting", "reflecting", "contributing to")
- Removed negative parallelism ("It is not just X; it is Y")
- Removed rule-of-three patterns and synonym cycling ("catalyst/partner/foundation")
- Removed false ranges ("from X to Y, from A to B")
- Removed em dashes, emojis, boldface headers, and curly quotes
- Removed copula avoidance ("serves as", "functions as", "stands as") in favor of "is"/"are"
- Removed formulaic challenges section ("Despite challenges... continues to thrive")
- Removed knowledge-cutoff hedging ("While specific details are limited...")
- Removed excessive hedging ("could potentially be argued that... might have some")
- Removed filler phrases and persuasive framing ("In order to", "At its core")
- Removed generic positive conclusion ("the future looks bright", "exciting times lie ahead")
- Made the voice more personal and less "assembled" (varied rhythm, fewer placeholders)


## Reference

This skill is adapted from [blader/humanizer](https://github.com/blader/humanizer) (MIT, Siqi Chen, 2025), which is itself based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (WikiProject AI Cleanup).

Key insight from Wikipedia: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."
