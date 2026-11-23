"""Evidence-first 100-app API integration research agent.

Pass 1 retrieves official-first search evidence and extracts a structured record.
Pass 2 independently re-searches a sample and compares key claims. Human review
is still required for ambiguous entitlement/partner gates and product priority.
"""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '25'))
MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')

FIELDS = [
    'description','official_website','developer_docs_url','api_availability',
    'api_coverage','authentication','credential_acquisition','access_model_bucket',
    'mcp_status','agent_compatibility','integration_blockers','buildability',
    'priority','evidence','research_confidence','notes'
]

EXTRACT_SYSTEM = '''You are a product-operations API researcher. Extract only what is
supported by the supplied search results. Prefer official docs and official product
pages. Never infer credential self-service from API existence. Distinguish API key,
OAuth, token and Basic auth; distinguish official MCP from third-party/community;
state Unverified if no reliable evidence. Use Unknown for missing claims. Return JSON
with keys: description, official_website, developer_docs_url, api_availability
(REST/GraphQL/Both/SDK-only/CLI/None/Unknown), api_coverage (Broad/Moderate/Narrow/
Unavailable/Unknown), authentication (array), credential_acquisition (Self-serve/
Free trial/Paid subscription/Admin approval/Enterprise-only/Partner-gated/
Contact-sales/Unavailable/Unknown), access_model_bucket (Self-serve/Gated/Mixed/
Unknown), mcp_status (Official/Third-party/Community/Unavailable/Unverified),
agent_compatibility (High/Medium/Low/Unknown), integration_blockers (array),
buildability (Easy/Medium/Hard/Not currently feasible/Unknown), priority (P0/P1/P2/P3/
Unassigned), evidence (array of {claim,url,source_type}), research_confidence
(High/Medium/Low), notes. Do not assign high confidence without official-source support.
Do not manufacture evidence URLs.'''

VERIFY_SYSTEM = '''Independently verify the initial record. Treat it as untrusted. Use only the
fresh results supplied. Return JSON with verified_record (same keys as the initial
record) and claim_checks. Each claim_check must include claim, initial_value,
verified_value, outcome (Correct/Partially Correct/Incorrect/Unverifiable),
discrepancy, error_class (retrieval/extraction/classification/stale_documentation/none).
An absent result is Unverifiable, not Correct. Do not exaggerate accuracy.'''

def search_tavily(query: str, max_results: int = 6) -> list[dict]:
    key = os.getenv('TAVILY_API_KEY')
    if not key:
        raise RuntimeError('TAVILY_API_KEY missing')
    resp = requests.post('https://api.tavily.com/search', json={
        'api_key': key, 'query': query, 'search_depth': 'advanced',
        'max_results': max_results, 'include_answer': False,
        'include_raw_content': True,
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json().get('results', [])

def source_pack(items: list[dict]) -> list[dict]:
    output, seen = [], set()
    for item in items:
        url = item.get('url')
        if not url or url in seen:
            continue
        seen.add(url)
        output.append({'title': item.get('title'), 'url': url,
                       'content': (item.get('raw_content') or item.get('content') or '')[:5000]})
    return output

def llm_json(client: OpenAI, system: str, payload: dict) -> dict:
    res = client.chat.completions.create(
        model=MODEL, temperature=0, response_format={'type':'json_object'},
        messages=[{'role':'system','content':system},
                  {'role':'user','content':json.dumps(payload, ensure_ascii=False)}])
    return json.loads(res.choices[0].message.content)

def run_pass1(client: OpenAI, app: dict) -> dict:
    queries = [
        f'{app["name"]} official developer API documentation authentication',
        f'{app["name"]} official developer credential access pricing plan API',
        f'{app["name"]} official MCP server documentation'
    ]
    found=[]
    for query in queries:
        found.extend(search_tavily(query))
    checked=datetime.now(timezone.utc).isoformat()
    extraction=llm_json(client, EXTRACT_SYSTEM, {
        'application':app, 'search_results':source_pack(found), 'checked_at':checked})
    return {**app, **extraction, 'research_status':'Automated pass 1',
            'pass1_checked_at':checked, 'pass1_source_count':len(source_pack(found)),
            'human_review_required':True}

def run_pass2(client: OpenAI, row: dict) -> dict:
    queries = [
        f'{row["name"]} official API reference authentication developer access',
        f'{row["name"]} official MCP documentation pricing API availability'
    ]
    found=[]
    for query in queries:
        found.extend(search_tavily(query))
    return llm_json(client, VERIFY_SYSTEM, {
        'application': {'id':row['id'],'name':row['name'],'category':row['category'],
                        'official_website_hint':row['official_website_hint'],
                        'docs_hint':row['docs_hint']},
        'initial_record':row, 'fresh_search_results':source_pack(found),
        'checked_at':datetime.now(timezone.utc).isoformat()})

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int,default=100)
    parser.add_argument('--verify-sample',type=int,default=15)
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    if not os.getenv('OPENAI_API_KEY') or not os.getenv('TAVILY_API_KEY'):
        raise SystemExit('Set OPENAI_API_KEY and TAVILY_API_KEY in .env')
    apps=json.loads((ROOT/'data/apps.json').read_text())['applications']
    out=ROOT/'outputs'; out.mkdir(exist_ok=True)
    result_file=out/'automated_results.json'
    current={}
    if args.resume and result_file.exists():
        current={r['id']:r for r in json.loads(result_file.read_text()).get('applications',[])}
    client=OpenAI()
    for app in apps[:args.limit]:
        if app['id'] in current: continue
        try:
            current[app['id']]=run_pass1(client, app)
            print(f"PASS1 {app['id']:03d}/100 {app['name']} — {current[app['id']].get('research_confidence','Low')}")
        except Exception as exc:
            current[app['id']]={**app,'research_status':'Automated pass 1 failed',
                'research_confidence':'Low','buildability':'Unknown','priority':'Unassigned',
                'authentication':['Unknown'],'credential_acquisition':'Unknown',
                'mcp_status':'Unverified','api_availability':'Unknown','evidence':[],
                'notes':f'{type(exc).__name__}: {exc}','human_review_required':True}
            print(f"ERROR {app['name']}: {exc}")
        result_file.write_text(json.dumps({'applications':sorted(current.values(),key=lambda x:x['id'])},indent=2))
        time.sleep(.25)
    records=sorted(current.values(), key=lambda r:({'Low':0,'Medium':1,'High':2}.get(r.get('research_confidence'),0)))
    sample=records[:args.verify_sample]
    verified=[]
    for row in sample:
        try:
            result=run_pass2(client,row)
            verified.append({'id':row['id'],'name':row['name'],**result})
            print(f"PASS2 {row['name']}: complete")
        except Exception as exc:
            verified.append({'id':row['id'],'name':row['name'],'overall_result':'Unverifiable',
                             'claim_checks':[],'error':f'{type(exc).__name__}: {exc}'})
    (out/'automated_verification.json').write_text(json.dumps({'verification':verified},indent=2))
    print(f'Saved {len(current)} automated application records and {len(verified)} verification records.')

if __name__ == '__main__':
    main()
