# Verification protocol

The current handoff contains 36 manually source-reviewed records selected purposively across all ten categories. This is not a random accuracy sample.

The automated research runner performs:
1. Pass 1: three search queries per application (API/auth, credential/access, MCP), then structured extraction.
2. Pass 2: fresh independent searches on a risk-prioritized sample (lowest confidence first) and claim-level comparison.
3. Evaluation: Correct / Partially Correct / Incorrect / Unverifiable claims are counted separately. Strict accuracy is Correct divided by Correct + Incorrect; partial and unverifiable claims remain separately disclosed.

Do not interpret this risk-targeted sample as a population-representative accuracy estimate. A formal overall estimate needs a separately selected random/stratified verification sample.

Human review remains necessary for credential gates, plan tiers, app review, partner programs, MCP production readiness and prioritization.
