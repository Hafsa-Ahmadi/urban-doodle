# Composio 100-App Integration Research

An evidence-first research project for assessing how easily applications can become agent-callable toolkits.

## Current research status
- Exact assignment scope: **100 applications across 10 categories**.
- **36 applications** have source-reviewed records across all categories.
- **64 applications** remain pending; their fields are Unknown / Unverified, not negative findings.
- The automated research run and measured agent-accuracy evaluation have **not yet been executed**.
- The 36-app findings are a purposive sample, not a random sample of the full 100.

## Quick start — Windows 10 / PowerShell

1. Install Python 3.10+ and Git. Verify:
   ```powershell
   py --version
   git --version
   ```
2. Clone the repo and enter the folder:
   ```powershell
   git clone https://github.com/Hafsa-Ahmadi/urban-doodle.git
   cd urban-doodle
   ```
3. Create and activate an isolated Python environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again.
4. Install dependencies and create your private environment file:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```
5. Open `.env` in VS Code or Notepad and set:
   - `OPENAI_API_KEY` — required for structured extraction and verification.
   - `TAVILY_API_KEY` — required for web retrieval.
   - `OPENAI_MODEL` — optional; default: `gpt-4.1-mini`.
   - `REQUEST_TIMEOUT` — optional; default: 25 seconds.
   - `COMPOSIO_API_KEY` — optional placeholder only; the current runner does not call Composio SDK/MCP.

6. Run a small smoke test first:
   ```powershell
   python agent/research_agent.py --limit 2 --verify-sample 1
   ```
7. Run the full set:
   ```powershell
   python agent/research_agent.py --limit 100 --verify-sample 15
   ```
   Resume if interrupted:
   ```powershell
   python agent/research_agent.py --limit 100 --verify-sample 15 --resume
   ```
8. Evaluate the verification sample and run tests:
   ```powershell
   python verification/evaluate.py
   python -m pytest -q
   ```

The agent writes `outputs/automated_results.json` after pass 1 and `outputs/automated_verification.json` after pass 2. The verification sample is risk-prioritized (low-confidence records first), not random. Report Correct, Partially Correct, Incorrect and Unverifiable separately.

## WSL2 Ubuntu alternative

If working in Ubuntu via WSL:
```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
git clone https://github.com/Hafsa-Ahmadi/urban-doodle.git
cd urban-doodle
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```
Edit `.env` with a text editor, then use the same `python agent/research_agent.py ...` commands shown above.

## File-by-file guide

| Path | Purpose |
|---|---|
| `data/apps.json` | The exact 100 application names, categories and official-site/documentation hints. This is the input dataset. |
| `data/reviewed_findings.json` | The 36 source-reviewed seed records used by the dashboard. The remaining 64 are pending. |
| `agent/research_agent.py` | Main Python research agent. Pass 1 searches API/auth, credential/access and MCP information; pass 2 re-searches a sample and compares claims. |
| `requirements.txt` | Third-party Python packages required by the agent and tests. |
| `.env.example` | Names of environment variables. Copy it to `.env` and add your own keys; never commit `.env`. |
| `.gitignore` | Prevents secrets, virtual environments and cache files from being pushed. |
| `verification/evaluate.py` | Calculates strict accuracy from claim-level pass-2 outputs while reporting partial/unverifiable claims separately. |
| `verification/README.md` | Explains how the verification sample is selected and interpreted. |
| `analysis/metrics.py` | Prints descriptive research distributions from the local merged `outputs/results.json` file. |
| `research_sources.txt` | Official documentation URLs inspected for the 36 reviewed seed records. |
| `docs/index.html` | GitHub Pages dashboard: summary findings, patterns and a searchable 100-app matrix. |
| `outputs/` | Runtime output directory. Agent JSON files are generated here when you run it. |

## What the agent actually does

1. Loads each app from `data/apps.json`.
2. Runs three Tavily searches: API/authentication, developer credentials/access, and MCP.
3. Deduplicates results and sends source snippets to OpenAI for JSON extraction.
4. Writes the first-pass finding immediately, so progress survives interruptions.
5. For the verification sample, conducts fresh searches and asks the model to compare the new evidence against the initial record.
6. Saves claim-level checks. Human review is still needed for ambiguous plan gates, partner approval, access scopes and final integration priority.

The current code uses Tavily + OpenAI; it does **not** create or use a Composio MCP session. Do not say Composio SDK dogfooding was performed unless you add and run that part yourself.

## Deploy the dashboard with GitHub Pages

1. Push the repository to `main`.
2. Open the repository on GitHub → **Settings** → **Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select branch `main` and folder `/docs`, then click **Save**.
5. Wait for the Pages workflow/build to finish. Open the site at:
   `https://hafsa-ahmadi.github.io/urban-doodle/`

The dashboard loads its two data files from `data/apps.json` and `data/reviewed_findings.json`. Keep these paths in place when editing the page.

## Push your local changes

```powershell
git add .
git status
git commit -m "Update Composio research"
git push origin main
```

## Evidence and quality rules

- Prefer official developer docs, API references, authentication guides, credential/pricing pages and official MCP repositories.
- API existence does not prove self-serve credential access.
- A free account does not prove unrestricted API access.
- Official, third-party, community and unverified MCP are different statuses.
- Unknown is not No.
- Never report an accuracy improvement unless pass 1 and pass 2 were actually run on a frozen claim set and evaluated.
- Never commit API keys, OAuth secrets, MCP session headers or `.env`.

## Known limitation at this handoff

The dashboard and seed dataset are ready to view, but the automated 100-app run and accuracy scoring still require your API keys and local execution. The current 36-app statistics are descriptive of the source-reviewed subset only.
