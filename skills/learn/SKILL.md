---
name: learn
description: Deep, explicit learning sessions that probe the learner's current knowledge, clarify a concrete goal, build a dependency graph from solid foundations, teach through motivated discovery, verify understanding, and use research and minimal diagrams when useful. Use ONLY when the user explicitly invokes `learn`, `$learn`, says `usa la skill learn`, `usa la skill de aprendizaje`, or asks for a deep study session. Do not use for ordinary questions, quick explanations, summaries, or casual tutoring unless the user explicitly requests this skill.
---

# Learn

Run a deliberate learning session whose goal is understanding, not memorization. Keep a graph of concepts in which each new node connects to foundations the learner has already accepted. Make the learner able to reconstruct the result, not only repeat it.

## Activation boundary

Use this skill only after an explicit request such as `$learn`, `usa la skill learn`, `quiero aprender X usando learn`, or `enséñame X con la skill de aprendizaje`. Do not activate it for a normal question such as "¿qué es OSPF?" or "explícame esta función". Answer those directly with the normal response style.

When the user invokes the skill without a topic, ask for the topic before starting. Keep the session in the user's language unless they request another one.

## Session loop

Follow this sequence. Scale the number of questions and concepts to the topic, but do not skip a phase without stating why.

`probe → goal → plan → teach → verify`

### 1. Probe current understanding

Find the learner's current level before teaching.

- Identify the prerequisite strands the requested goal depends on.
- Ask short, gradable questions for those strands. Use Markdown options labelled A, B, C, or D, and do not reveal the answer until the learner responds.
- Start with an accessible question, then jump difficulty when the learner is correct. After an error, ask a nearby question to distinguish a careless slip from a gap or misconception.
- Bracket every relevant strand with a floor the learner can handle and a ceiling where understanding stops. An all-correct round is not enough. A single wrong answer is not a reason to start teaching.
- Keep each round small, normally two to six questions. Continue only where the result changes the plan.

Treat the original `quiz` extension as a behaviour, not as a required tool. In a text-only interface, show the question, wait for the answer, then give the result and a short explanation. Never make the learner hunt for an answer hidden in the same message.

### 2. Clarify the goal

Ask what the learner wants to be able to do or explain at the end. Resolve scope, intended depth, practical context, and constraints. Use a normal conversational question, one at a time, for choices that have no right answer. This is the portable equivalent of `ask-user-question`; do not require a popup extension.

Turn a vague request such as "learn OSPF" into an observable target, for example: "explain why OSPF selects a path, predict the effect of a link-cost change, and diagnose a simple adjacency problem".

### 3. Research and plan

Before teaching facts that may be current, niche, disputed, or easy to misremember, verify them. Research first when the lesson depends on documentation, standards, APIs, library behaviour, versions, dates, or external data.

Use the available web-search or research capability. If the environment supports a read-only research agent, delegate a narrow research brief. If it does not, do the research in the current session. Never assume a particular runtime, extension, or project tool exists.

Prefer sources in this order:

1. Official documentation from the owner of the system or project.
2. Standards, specifications, source code, and first-party APIs.
3. Recognised technical documentation.
4. Other sources only when the first three do not cover the point.

Record source links near claims that depend on them. Separate verified facts from explanations and inferences. If research changes a claim, say what was corrected. If the research capability is unavailable, narrow the claim and say that it could not be verified instead of presenting uncertain memory as fact.

Then design the lesson for this learner:

- Start from the smallest unconditional truths or real definitions the learner can accept without caveats. Do not call a fact an axiom merely because it sounds foundational.
- Build a dependency graph from those roots to the stated goal. Include only concepts the goal needs.
- Choose Socratic discovery when the learner can plausibly derive the next move. Choose a short motivated explanation when the step is beyond cold reasoning or the learner asks for a direct explanation.
- Plan checks at every important node and identify likely misconceptions.

Present the plan before teaching. Explain the order and its reason, then include a small Mermaid dependency graph only if the relationships themselves help. Keep the graph to a few nodes. Ask the learner to approve or change the plan, and wait before entering the teaching phase.

### 4. Teach one connected node at a time

For each foundation or non-trivial derived concept, run this loop:

1. Motivate it. Name the problem or gap that makes the concept useful now.
2. Establish it. State a foundation plainly. For a derived concept, walk through how the learner could have reached it from established nodes. Every move needs a reason.
3. Connect it. Point to the exact earlier nodes it depends on and what new capability it enables.
4. Check it. Ask one small quiz or a transfer question. Keep the answer hidden until the learner responds.

If the learner misses a fundamental check, stop building on it. Reframe the concept, expose the misconception, and check it again. Do not bury a weak prerequisite under more explanation.

Keep explanations compact. Prefer a useful example, a counterexample, or a small derivation over a long catalogue of facts. Use LaTeX for mathematical notation when it makes the relation clearer.

For quizzes, make every option a bare claim with the same shape and level of detail. Derive distractors from real neighbouring misconceptions. Put explanations after the answer, not in the options. Use an open response when the target is reasoning rather than recognition.

### 5. Verify transfer

End each meaningful segment and the session with a task that is new enough to require the model, not a request to repeat the lesson. Ask the learner to predict, derive, diagnose, compare, or explain the concept in their own words.

Classify the result:

- Solid: the learner reconstructs the idea and uses it in a new case.
- Partial: keep the node, repair the missing edge, and check again.
- Unstable or wrong: return to the last solid foundation and rebuild.

Finish with a short map of what is understood, the remaining gaps, and one useful next exercise. Do not claim mastery from recognition alone.

## Visualizations

Create a visual only when it makes structure, direction, spatial position, or a quantitative relationship easier to understand than prose or a small table. Do not add a decorative diagram.

Choose the representation by the thing the learner must see:

- Relationships, nodes, dependencies, flows, sequences, trees, networks, and state transitions: use Mermaid in the response or save a `.mmd` file when the learner needs an artifact.
- Coordinates, geometry, vectors, number lines, plots, and exact positions: use an SVG file or another geometry-capable renderer available in the environment.
- Architecture or a standalone diagram deliverable: use an installed diagram tool such as `diagram-design` or `drawio` only when available and useful. Do not install a Pi extension or a renderer merely to decorate a lesson.

Before drawing, remove any element that does not carry the idea. Keep the visual to the fewest nodes, labels, and edges that preserve the relation. If a renderer is available, inspect the result for incorrect arrows, clipped labels, overlap, and misleading geometry. If it is not available, return valid source in a fenced block or save the source file, state that it was not rendered, and do not claim visual verification.

Use the current project or the user-specified location for learning artifacts. Do not assume an Obsidian vault, a `viz/` directory, a `md-log` extension, or a special embed syntax. Link a created file using the host application's normal file-link format.

On this computer, `rsvg-convert` and ImageMagick are available for SVG previews, while a standalone Mermaid CLI is not installed. Use the former only when an SVG artifact is useful. Keep Mermaid as source unless an already-installed diagram tool can render it.

## Portable replacements for the original components

Keep these behaviours without importing Pi-specific runtime code:

- `teach`: this file contains the foundations-first, motivated-discovery, connected-knowledge loop.
- `visualize`: the conditional Mermaid/SVG decision above replaces mandatory maker subagents and Obsidian PNG embedding.
- `researcher`: use the available web or research capability with primary-source rules and explicit uncertainty.
- `quiz`: use delayed-answer Markdown checks and adaptive questioning.
- `ask-user-question`: ask in the current conversation and wait; no popup dependency.
- `mermaid-maker` and `svg-maker`: use an available diagram tool or create and inspect source files locally. If no renderer or visual inspection tool exists, degrade to source plus an honest limitation.
- `md-log`: do not mirror every response into a file automatically. Create session notes only when the learner asks for them.

Never reference Pi-only imports, extensions, paths, agents, or commands. Do not install Pi as a prerequisite for this skill.
