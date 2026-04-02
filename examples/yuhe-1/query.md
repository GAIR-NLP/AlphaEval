> **Note:** This is a fictional task for demonstration purposes only. All product names, specifications, and prices are synthetic.

# BOM Board Card Procurement Optimization

## Task
You are a procurement optimization specialist. Given a catalog of 2,000 board cards with specifications and pricing, find the lowest-cost combination that satisfies all functional requirements.

## Input Files
- `files/board_cards_2000_price_correlated.xlsx` — Catalog of 2,000 board cards with specs and prices
- `files/requirements.md` — Functional requirements (constraints that must be satisfied)

## Requirements
1. **All functional requirements must be met** — every constraint in `requirements.md` must be satisfied
2. **Minimize total procurement cost** — among all valid combinations, choose the cheapest
3. **Tie-breaking**: If costs are equal, minimize the number of board cards. If still tied, prefer the combination with ascending board card IDs.

## Output
Save your answer to `results/ans.md` in this format:

```
Total Cost: $XXXXX

Selected Board Cards:
| Card ID | Quantity | Unit Price | Subtotal |
|---------|----------|------------|----------|
| XXX     | X        | $XXX       | $XXX     |
| ...     | ...      | ...        | ...      |
```

Show your reasoning for why this combination satisfies all constraints.
