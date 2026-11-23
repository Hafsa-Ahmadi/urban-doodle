# Composio 100-App Integration Research

An evidence-first research project for assessing how easily applications can become agent-callable toolkits.

## Current state (honest handoff)
- Exact assignment scope: **100 applications across 10 categories**.
- **36 applications** have source-reviewed research records.
- **64 applications** remain pending; their fields should stay Unknown / Unverified.
- Automated live research and agent accuracy evaluation have not yet been run.
- The 36-app findings are a purposive review subset, not a random sample of all 100.

## Run locally on Windows
Open PowerShell in the repository folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and add your API credentials:
- `OPENAI_API_KEY` — required for structured extraction and verification.
- `TAVILY_API_KEY` — required for search/retrieval.
- `OPENAI_MODEL` — optional; default is `gpt-4.1-mini`.
- `COMPOSIO_API_KEY` — reserved for optional Composio SDK/MCP experimentation; not required by the current research runner.

Start with a small test:
```powershell
python agent/research_agent.py --limit 2 --verify-sample 1
``

Then run all 100:
```powershell
python agent/research_agent.py --limit 100 --verify-sample 15
``

Resume an interrupted run:
```powershell
python agent/research_agent.py --limit 100 --verify-sample 15 --resume
``

Calculate measured verification results after the run:
```powershell
python verification/evaluate.py
``

Run input tests:
```powershell
python -m pytest -q
``

## Project structure
- `data/apps.json`: the authoritative 100 applications and the supplied website/documentation hints.
- `agent/research_agent.py`: Pass 1 discovery/extraction and Pass 2 fresh-search verification.
- `outputs/`: generated agent results and verification reports. These are created by the run.
- `verification/evaluate.py`: counts Correct / Partially Correct / Incorrect / Unverifiable claims and calculates strict accuracy only for binary-resolvable claims.
- `dashboard/index.html`: static GitHub Pages research overview.
- `.env.example`: names of environment variables; never put real secrets here in a public commit.
- `.gitignore`: prevents `.env`, virtual environments, caches, and generated secrets from being committed.

## How to interpret the reviewed subset
For the 36 source-reviewed apps only: REST is documented for 32/36 (88.9%); OAuth appears in 24/36 (66.7%); official MCP is confirmed for 6/36 (16.7%); credential/scope complexity was tagged as a blocker in 22/36 (61.1%). Authentication and blockers are multi-label and overlap. These statistics must not be generalized to the other 64 apps.

## Evidence discipline
- Prefer official developer documentation, authentication guides, API references, access/pricing pages, and official MCP repositories.
- API existence does not prove self-serve credentials.
- A free account does not prove unrestricted API access.
- Official, third-party, community and unverified MCP are different statuses.
- Unknown is not No.
- Never claim the agent ran unless you executed it and the generated output confirms it.
- Never commit API keys, OAuth secrets, MCP session headers, or `.env`.

## Publish with Git
```powershell
git add .
git commit -m "Add Composio integration research project"
git push origin main
```

## Enable GitHub Pages
In the GitHub repository, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and folder `/docs` only if a `docs` folder exists. The included dashboard is under `dashboard/`, so the simplest option is either move/copy it to `docs/index.html`, or select GitHub Actions and add a workflow. Ask the owner to enable Pages; a repository push alone does not publish a live website.
