# English Banned Phrases

> 本文件是解释、示例与操作细则；行为合同的单源是 `SKILL.md`，两处表述不一致时以 `SKILL.md` 为准。

> 以下例句是合成编辑材料，数字、机构、功能与命令不代表真实测量或本 skill 能力；只能在例句给出的范围内改写，不能套入用户材料。

> Sources: humanizer, stop-slop, avoid-ai-writing. Historical references and withdrawn material are recorded in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

本表默认列代表项，不追求穷举同义变体。**这份清单是举例，不是边界。** 这里管的是修辞动作，不是字面：把一个命中的说法换一套词继续做同一件事——同样的 significance inflation、同样的 sycophantic opener、同样的空 hedging——仍然算命中。判断一个新说法要不要处理，看它在做什么动作，不看它在不在下面的列表里。反过来也成立：出现在列表里但在当前句子里承担实义的词，按误杀防护放行。

## Tier 1: Replace by default

These are candidates for editing in context, not statistical evidence of authorship. Preserve meaningful uses under the [misfire protection rules](./severity.md).

### Throat-clearing openers
- Here's the thing
- The uncomfortable truth is
- Can we talk about
- Let's be honest
- I'll be frank
- It's worth noting that
- At the end of the day

### Emphasis crutches
- Full stop.
- Let that sink in.
- Make no mistake.
- Mark my words.
- I promise.
- Read that again.
- Period.

### Business jargon
- leverage → use
- navigate → handle, deal with
- unpack → explain
- lean into → accept, try
- deep dive → detailed look
- game-changer → important change
- circle back → revisit
- synergy → cooperation
- ecosystem → system, community
- streamline → simplify
- empower → let, enable
- actionable → practical
- learnings → lessons
- thought leader → expert
- best practices → good practices
- holistic → complete, whole

Keep literal technical uses in graph, network, routing, or pathfinding contexts. Example: `The system navigates the network topology using Dijkstra's algorithm.`

### Inflated verbs (use simpler alternatives)
- utilize → use
- commence → start
- endeavor → try
- ascertain → find out
- facilitate → help
- cultivate → build, grow
- elucidate → explain
- ameliorate → improve
- galvanize → motivate
- bolster → support
- spearhead → lead
- catalyze → trigger
- reimagine → rethink

### Significance inflation
- testament to → shows
- serves as → is
- stands as → is
- showcases → shows
- underscores → shows
- highlights → shows
- pivotal → important
- groundbreaking → new
- cutting-edge → new, latest
- watershed moment → turning point
- indelible mark → lasting effect
- paradigm shift → major change

### Copula avoidance (just use "is/are/has")
- serves as a → is a
- stands as a → is a
- represents a → is a
- functions as a → is a
- boasts a → has a
- features a → has a
- presents a → has a

### Filler phrases
- In order to → To
- Due to the fact that → Because
- At this point in time → Now
- It is important to note that → (delete)
- The system has the ability to → The system can
- It goes without saying → (delete)

### Sycophantic / meta
- Great question!
- You're absolutely right!
- Certainly!
- Of course!
- I hope this helps!
- Let me know if you'd like me to expand
- In this essay we will explore
- As we'll see
- Here is a/an

## Tier 2: Inspect clustering in context

Use the shared [inspection thresholds](./severity.md#检查阈值). Counts prompt a functional check; preserve meaningful uses regardless of their number.

- harness, navigate, foster, elevate, unleash
- resonate, revolutionize, underpin, nuanced, crucial
- multifaceted, myriad, plethora, encompass
- transformative, cornerstone, paramount, poised
- burgeoning, nascent, quintessential, overarching

## Tier 3: Flag at high density only

Common words are not problems by themselves. Use the shared [inspection thresholds](./severity.md#检查阈值), then check whether repetition serves a purpose.

- significant, innovative, effective, dynamic
- scalable, compelling, unprecedented, exceptional
- remarkable, sophisticated, instrumental
- comprehensive, robust, seamless

## Adverbs (-ly words)

Check whether an adverb adds meaning before deleting it. Preserve uncertainty, degree, timing, and technical meanings such as statistical significance. Examples to inspect:

- really, just, literally, genuinely, honestly
- deeply, truly, fundamentally, essentially
- incredibly, remarkably, significantly
- interestingly, importantly, notably
- ultimately, arguably, undeniably
