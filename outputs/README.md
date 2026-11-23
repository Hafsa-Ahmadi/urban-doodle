# Generated outputs

The research runner creates files here when it executes:
- `automated_results.json`: pass-1 structured findings for each processed app. It is saved after every app, so `--resume` can continue.
- `automated_verification.json`: fresh-search verification results and claim-level outcomes for the selected sample.

After running the agent locally:
1. Run `python verification/evaluate.py` to print Correct / Partially Correct / Incorrect / Unverifiable counts and strict binary-resolvable accuracy.
2. Run `python analysis/metrics.py` to calculate distributions from the automated result set.
3. To update the GitHub Pages dashboard, commit the generated JSON files to this `outputs/` directory. The page automatically merges automated findings over the 36-record manual seed.
4. Never place API keys or credentials in these files.
