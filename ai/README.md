# AI Interpretation Layer

This directory contains the AI engineering component of the Mystery Gene Decoder.

## Purpose

The AI layer translates structured bioinformatics findings into an accessible, evidence-grounded explanation for the user.

The AI does **not** infer gene function directly from raw DNA. Computational analysis and database evidence should produce the findings; the AI explains and contextualizes those findings.

## MVP Output

The interpretation should answer:

1. **What am I seeing?**
2. **Why might this matter?**
3. **What should I investigate next?**
4. **Evidence**
5. **Limitations**

## Development Approach

The AI layer can initially be developed against mock structured findings while the backend bioinformatics pipeline is being implemented.

The mock contract should later be replaced by the backend's real output without changing the interpretation interface.

## Guardrails

- Never fabricate evidence, annotations, citations, or database results.
- Do not equate sequence similarity with demonstrated biological function.
- Distinguish observed findings from hypotheses or interpretations.
- Communicate uncertainty explicitly.
- Do not make diagnostic or pathogenicity claims unless the supplied evidence supports them.
