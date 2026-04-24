# Lab 7: Multi-Agent Systems — AutoGen vs CrewAI

**Author:** Leo Fitzgerald  
**Date:** 2026-04-24  
**Course:** IS492 SP26  

---

## Executive Summary

This lab explored two leading multi-agent AI frameworks — **Microsoft AutoGen** and **CrewAI** — by implementing, modifying, and extending multi-agent workflows. The experiments revealed fundamental differences in their orchestration philosophies: AutoGen’s emergent, conversation-driven approach vs. CrewAI’s structured, task-driven pipeline. Through four exercises, I analyzed how these design choices affect agent collaboration, output quality, and system extensibility.

---

## Exercise 1: Run and Understand the Demos

### AutoGen Demo: Product Planning (Interview Platform)

**What I observed:**
- AutoGen uses a **GroupChat** pattern where agents are placed in a shared conversation space
- The **GroupChatManager** uses LLM-based speaker selection to decide who speaks next
- Agents naturally reference and build on each other’s contributions
- The conversation flows: ProductManager → ResearchAgent → AnalysisAgent → BlueprintAgent → ReviewerAgent
- Each agent’s response is visible to all other agents, creating a shared context

**Key characteristics:**
- Speaker selection is dynamic (LLM decides who should speak next)
- Agents can reference each other by name
- The conversation is emergent — order isn’t strictly fixed
- `max_round=8` controls conversation length
- `allow_repeat_speaker=False` prevents one agent from dominating

### CrewAI Demo: Travel Planning (Iceland Trip)

**What I observed:**
- CrewAI uses a **sequential task pipeline** where each agent has a discrete, well-defined task
- Tasks execute in fixed order: FlightAgent → HotelAgent → ItineraryAgent → BudgetAgent
- Each agent works independently on their assigned task
- Output from earlier tasks is available as context to later tasks (but there's no back-and-forth)
- Each agent has specific **tools** (e.g., `search_flight_prices`, `search_hotel_options`)

**Key characteristics:**
- Execution order is deterministic and pre-defined
- Each agent produces a standalone deliverable
- Tools are agent-specific (flight tool only for flight agent)
- The `expected_output` field defines what each task should produce
- Process is `"sequential"` — no parallel execution

### Comparison Table

| Aspect | AutoGen | CrewAI |
|--------|---------|--------|
| **Orchestration** | Conversational GroupChat | Sequential Task Pipeline |
| **Speaker Selection** | LLM-based (dynamic) | Pre-defined order |
| **Agent Interaction** | Multi-turn conversation | Independent task execution |
| **Context Sharing** | All messages visible to all agents | Previous task output as context |
| **Tool Usage** | Optional per agent | Core to agent capability |
| **Output Format** | Conversation transcript + summary | Task result chain |
| **Determinism** | Low (emergent behavior) | High (fixed pipeline) |

---

## Exercise 2: Modify Agent Behavior (Ripple Effects)

### AutoGen Modification: ResearchAgent Focus Shift

**What I changed:**
- Changed the ResearchAgent’s focus from "AI interview platforms" to **"AI-powered employee onboarding tools"**
- Changed competitor set from HireVue/Pymetrics/Codility to **Deel, Rippling, BambooHR, WorkBright**

**Expected ripple effects across the system:**
1. **AnalysisAgent** would identify different market gaps — onboarding automation, compliance training, new-hire engagement instead of interview assessment gaps
2. **BlueprintAgent** would design different product features — automated onboarding workflows, document collection, training modules instead of video interview features
3. **ReviewerAgent** would evaluate a completely different product category with different competitive dynamics and go-to-market strategies

**Why this demonstrates AutoGen’s strength:** Because all agents share the conversation context, changing one agent’s focus naturally cascades through the entire discussion. Each subsequent agent adapts their response based on what they “hear” in the conversation. This is emergent behavior — no code changes were needed for the downstream agents.

### CrewAI Modification: FlightAgent Backstory Change

**What I changed:**
- Modified the FlightAgent’s backstory to include: **"You always prioritize direct flights over connections. You focus on budget airlines and cost savings above all."**

**Expected ripple effects:**
1. **FlightAgent** would now recommend cheaper, direct flights first (e.g., PLAY Airlines at $349 instead of Icelandair at $485)
2. **BudgetAgent** would calculate lower total costs because the flight baseline is cheaper
3. **ItineraryAgent** would potentially adjust recommendations knowing the budget is tighter
4. The overall trip plan would lean more budget-conscious

**Why this demonstrates CrewAI’s structure:** In CrewAI, the ripple effect is more contained — only the FlightAgent’s output changes, and downstream agents receive different context. But downstream agents don’t “know” why the flight recommendations changed; they just work with whatever context they receive.

### Key Insight: Ripple Effect Comparison

| Framework | Ripple Mechanism | Scope of Impact |
|-----------|-----------------|------------------|
| AutoGen | Conversational — agents react to what they hear | Broad, organic, unpredictable |
| CrewAI | Context-passing — downstream gets new inputs | Contained, structured, predictable |

---

## Exercise 3: Add a Fifth Agent

### AutoGen: Added CostAnalyst

**New agent: `CostAnalyst`**
- **Role:** Financial analyst specializing in SaaS product economics
- **Position:** Between BlueprintAgent and ReviewerAgent
- **Responsibilities:**
  - Analyze development and operational costs of proposed features
  - Estimate pricing tiers and revenue projections
  - Identify cost-effective features to build first
  - Suggest monetization strategy

**Configuration changes:**
- Added `CostAnalyst` to the GroupChat agents list (between BlueprintAgent and ReviewerAgent)
- Increased `max_round` from 8 to **10** to accommodate the extra agent
- Updated ReviewerAgent’s system message to reference CostAnalyst’s output

**Impact on workflow:**
- The GroupChatManager now has 6 agents to choose from for speaker selection
- The conversation flow becomes: Research → Analysis → Blueprint → **Cost Analysis** → Review
- The CostAnalyst bridges the gap between product design and business viability
- The ReviewerAgent can now reference financial data in their final recommendations

### CrewAI: Added LocalExpert

**New agent: `LocalExpert`**
- **Role:** Long-time local resident providing insider knowledge
- **Position:** Between ItineraryAgent and BudgetAgent
- **Responsibilities:**
  - Share hidden gems and off-the-beaten-path experiences
  - Provide cultural etiquette and customs advice
  - Offer safety tips and common tourist mistakes to avoid
  - Recommend local food experiences
  - Give seasonal and weather-specific advice

**Configuration changes:**
- Created `create_local_expert_agent()` function with `search_attractions_activities` tool
- Created `create_local_expert_task()` function
- Added agent and task to the Crew (5 agents, 5 tasks)
- Updated task sequence: Flight → Hotel → Itinerary → **LocalExpert** → Budget

**Impact on workflow:**
- The BudgetAgent now has additional local knowledge context when calculating costs
- The travel plan becomes richer with insider tips that standard tools wouldn’t surface
- The sequential pipeline now has 5 stages instead of 4

### Comparison: Adding Agents

| Aspect | AutoGen (CostAnalyst) | CrewAI (LocalExpert) |
|--------|----------------------|---------------------|
| **Integration effort** | Add to agents list, adjust max_round | Create agent + task + add to crew |
| **Impact on existing agents** | All agents see new agent’s contributions | Only downstream agents get context |
| **Speaker selection** | LLM decides when CostAnalyst speaks | Fixed position in sequence |
| **Flexibility** | CostAnalyst might speak at any time | LocalExpert always runs 4th |

---

## Exercise 4: Custom Problem Domain — Software Architecture Design

### Problem Domain

**Selected topic:** Designing a real-time collaborative document editing platform (similar to Google Docs) that must support 10 million concurrent users.

### AutoGen Implementation (`autogen_architecture_demo.py`)

**Agents:**
1. **RequirementsAgent** — Defines functional/non-functional requirements
2. **ArchitectAgent** — Designs system architecture, selects technology stack
3. **ImplementationAgent** — Plans development phases and delivery strategy
4. **RiskAssessmentAgent** — Evaluates risks and proposes mitigations

**Approach:**
- All 4 agents in a GroupChat with LLM-based speaker selection
- Agents converse naturally, with the architect being able to ask clarifying questions about requirements
- The risk analyst can reference both architecture decisions AND implementation plans
- Emergent cross-pollination: ArchitectAgent might adjust design based on risk feedback

### CrewAI Implementation (`crewai_architecture_demo.py`)

**Agents:**
1. **RequirementsAgent** — Requirements gathering with tech landscape tool
2. **ArchitectAgent** — Architecture design with tech landscape tool
3. **ImplementationAgent** — Implementation planning with tech landscape tool
4. **RiskAgent** — Risk assessment with risk evaluation tool

**Approach:**
- Sequential pipeline: Requirements → Architecture → Implementation → Risk
- Each agent has specific tools (tech landscape analyzer, risk evaluator)
- Each task has well-defined `expected_output`
- Structured, predictable output

### Custom Domain Comparison

| Aspect | AutoGen (Architecture) | CrewAI (Architecture) |
|--------|----------------------|---------------------|
| **Best suited for** | Exploratory design where trade-offs need discussion | Well-defined design process with clear deliverables |
| **Cross-referencing** | Architect can directly respond to requirements | Architect gets requirements as static context |
| **Iteration** | Natural back-and-forth possible | Single-pass, no iteration |
| **Output structure** | Conversation transcript (less structured) | Clear per-phase deliverables |
| **Tool usage** | Shared tools, agents decide when to use | Dedicated tools per agent |
| **Risk identification** | Risk agent sees full conversation context | Risk agent sees only prior outputs |

---

## Overall Conclusions

### When to Use AutoGen
- **Exploratory problems** where the solution space is unclear
- **Creative collaboration** that benefits from back-and-forth dialogue
- **Complex decision-making** where agents need to debate trade-offs
- **Small teams** of agents where rich interaction is valuable
- Problems where **emergent behavior** is desired

### When to Use CrewAI
- **Well-defined workflows** with clear sequential stages
- **Production pipelines** where determinism and reliability matter
- **Tool-heavy tasks** where each agent needs specific capabilities
- **Scalable systems** where adding agents shouldn’t affect existing ones
- Problems where **structured output** is required

### Final Assessment

| Dimension | AutoGen Advantage | CrewAI Advantage |
|-----------|-------------------|------------------|
| **Flexibility** | ✅ Dynamic speaker selection | |
| **Determinism** | | ✅ Predictable execution order |
| **Rich interaction** | ✅ Agents discuss and debate | |
| **Tool integration** | | ✅ Agent-specific tools |
| **Scalability** | | ✅ Easy to add/remove agents |
| **Output clarity** | | ✅ Clear per-task deliverables |
| **Creative tasks** | ✅ Emergent collaboration | |
| **Production use** | | ✅ Reliable pipeline execution |

Both frameworks have clear strengths. AutoGen excels when the problem benefits from organic, multi-turn agent discussion. CrewAI excels when the problem has a natural sequential structure with clear stage boundaries. The best choice depends on the specific use case and the degree of structured vs. emergent collaboration needed.

---

## Technical Environment

- **Python:** 3.12.13
- **pyautogen:** 0.2.35
- **crewai:** Latest stable
- **LLM:** gpt-4o-mini (OpenAI)
- **OS:** macOS
