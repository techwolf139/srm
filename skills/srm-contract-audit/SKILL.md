---
name: contract-auditing
description: Use when reviewing enterprise contracts, service agreements, procurement documents, or NDAs for risks, ambiguities, or unfavorable clauses
---

# Contract Auditing

## Overview

**Professional contract review requires systematic analysis of risk, clarity, and enforceability.**

This skill provides a structured approach to auditing contracts with precise location identification for high-risk content.

## When to Use

**Use when presented with:**
- Service agreements (SaaS, outsourcing, consulting)
- Procurement contracts
- Non-disclosure agreements (NDAs)
- Employment or contractor agreements
- Partnership or joint venture contracts
- License agreements
- Any legally binding document requiring risk assessment

**Particularly critical when:**
- Contract value exceeds threshold
- Unfamiliar counterparty
- Non-standard terms offered
- Compressed review timeline
- Industry-specific regulatory requirements apply

## The Audit Framework

### Phase 1: Document Structure Analysis

```
1. Identify all parties and their legal entities
2. Map contract hierarchy: main agreement → exhibits → amendments → appendices
3. Note effective dates, renewal terms, termination triggers
4. Identify governing law and jurisdiction
```

### Phase 2: Risk Classification

**Classify each clause by risk level:**

| Level | Classification | Action |
|-------|---------------|--------|
| 🔴 CRITICAL | One-sided obligations, unlimited liability, automatic renewal | Requires immediate renegotiation |
| 🟠 HIGH | Ambiguous terms, asymmetric rights, broad indemnification | Negotiation recommended |
| 🟡 MEDIUM | Missing protections, unclear definitions | Clarification needed |
| 🟢 LOW | Standard industry terms, balanced provisions | Acceptable as-is |

### Phase 3: Clause-by-Clause Analysis

**For each section, identify:**

1. **Who** - Which party bears the obligation/right
2. **What** - Exact obligation or right being granted
3. **When** - Timing, deadlines, notice periods
4. **How** - Conditions, exceptions, carve-outs
5. **What If** - Consequences of breach, termination scenarios

### Phase 4: High-Risk Content Detection

**Flag these specific patterns:**

#### 🔴 Critical Red Flags

```
- "Unlimited liability" or liability without cap
- "Auto-renewal" with inadequate notice period (<30 days)
- "Exclusive" rights without reciprocal obligation
- "Best efforts" / "reasonable efforts" without definition
- One-sided termination rights
- Assignment rights without consent
- Governing law in counterparty's jurisdiction
- Waiver of jury trial
- Class action waiver
```

#### 🟠 High-Risk Patterns

```
- Ambiguous definitions ("material", "reasonable", "timely")
- Broad indemnification scope
- Non-compete without geographic/scope limits
- IP assignment without compensation
- Non-solicitation of employees
- Most-favored-nation without exceptions
- Price escalation without caps
- Performance guarantees without cure periods
```

### Phase 5: Report Generation

**Output structure:**

```markdown
## Contract Audit Report

**Document:** [Contract Name]
**Parties:** [All identified parties]
**Risk Rating:** [Overall assessment]

### CRITICAL Issues (Require Immediate Attention)
| # | Location | Clause | Risk | Recommendation |
|---|----------|--------|------|----------------|
| C1 | Section 4.2, Line 15 | "unlimited liability" | ... | ... |

### HIGH Issues (Negotiation Recommended)
| # | Location | Clause | Risk | Recommendation |
|---|----------|--------|------|----------------|
| H1 | Section 7.1 | "best efforts" undefined | ... | ... |

### MEDIUM Issues (Clarification Needed)
| # | Location | Clause | Risk | Recommendation |
|---|----------|--------|------|----------------|
| M1 | Exhibit A | Scope undefined | ... | ... |

### Summary
- Total CRITICAL: X
- Total HIGH: X  
- Total MEDIUM: X
- Overall Recommendation: [Approve/Renegotiate/Reject]
```

## Location Identification Protocol

**CRITICAL: Always cite specific locations for findings.**

```
Format: [Section Number], [Paragraph/Sentence], [Line/Page if applicable]

Examples:
- "Section 5.2, paragraph 2"
- "Article III, clause (b)"
- "Exhibit B, page 2, lines 8-12"
- "Definitions section, 'Confidential Information'"
```

**Never say:** "The contract has a problematic clause about liability"
**Always say:** "Section 12.3, lines 4-7, states party A assumes ALL liability..."

## Common Mistakes

| Mistake | Why It's Bad | Correction |
|---------|--------------|------------|
| Reviewing only obvious sections | Risks hide in definitions, exhibits | Review entire document including headers |
| Ignoring defined terms | Definitions control interpretation | Cross-reference all defined terms |
| Missing amendments | Original + amendments = actual agreement | Read as unified document |
| Assuming standard language | "Standard" ≠ "Favorable" | Evaluate each clause independently |
| Not citing locations | Findings are unverifiable | Always cite section, paragraph, line |

## Quick Reference

**Audit Checklist:**

- [ ] All parties correctly identified
- [ ] Contract hierarchy mapped (main + exhibits + amendments)
- [ ] Governing law and jurisdiction noted
- [ ] Renewal and termination terms catalogued
- [ ] Liability provisions identified and capped?
- [ ] Indemnification scope assessed
- [ ] IP ownership clearly defined
- [ ] Termination rights bilateral?
- [ ] Notice provisions adequate?
- [ ] Dispute resolution mechanisms specified
- [ ] Force majeure examined
- [ ] Assignment rights evaluated
- [ ] Confidential information properly defined
- [ ] All undefined terms flagged

**Risk Magnifiers (Escalate Review):**
- Counterparty is sole-source
- Contract value >$100K
- Multi-year commitment
- Involves personal data
- Cross-border elements
- Novel or complex subject matter
