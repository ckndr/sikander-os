import json
from collections import Counter

def load_js(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        return json.loads(content.split('=', 1)[1].strip().rstrip(';'))

cinema = load_js('data/sikander_unified_cinema.js')
prop = load_js('data/property/alghafoor_property_ledger.js')
music = load_js('data/music/sikander_music_library.js')
career = load_js('data/career/sikander_career_data.js')
finance = load_js('data/finance/sikander_finance_master.js')
health = load_js('data/health/sikander_health_data.js')

items = []

# 1. Cinema
for m in cinema.get('watchlist', []):
    items.append(('Cinema', m.get('title'), f"⭐ {m.get('sikander_score', m.get('imdb_rating'))} · Watchlist", 'cinema.html'))
for m in cinema.get('history', []):
    items.append(('Cinema', m.get('title'), f"⭐ {m.get('user_rating', 'Watched')} · History", 'cinema.html'))

# 2. Property
items.append(('Property', 'Al Ghafoor Grande City — Unit 206', '67% Equity Paid (PKR 2.093M)', 'finance.html#property'))
for tx in prop.get('historical_ledger', []):
    items.append(('Property', f"{tx.get('description', '')} ({tx.get('date', '')})", f"PKR {tx.get('amount_pkr', '')}", 'finance.html#historical'))
for doc in prop.get('document_vault', []):
    items.append(('Property', f"Receipt #{doc.get('doc_id')}: {doc.get('document_type', '')}", f"PKR {doc.get('amount', '')}", 'finance.html#vault'))
for u in prop.get('utility_schedule', []):
    items.append(('Property', f"Utility: {u.get('inst_label', '')} ({u.get('status', '')})", f"PKR {u.get('scheduled_dues', '')}", 'finance.html#utilities'))

# 3. Music
for t in music.get('tracks', []):
    items.append(('Music', t.get('title'), f"{t.get('artist', 'Artist')} · {t.get('mood', 'Music')}", 'music.html'))

# 4. Career
prof = career.get('candidate_profile', {})
items.append(('Career', f"{prof.get('full_name')} — {prof.get('professional_title')}", prof.get('dual_employer_status', ''), 'career.html#resume'))
for r in career.get('target_roles', []):
    items.append(('Career', f"Target Role: {r.get('title')}", r.get('level', ''), 'career.html#advisor'))
for m in career.get('career_milestones', []):
    items.append(('Career', f"{m.get('role')} @ {m.get('company')}", m.get('period', ''), 'career.html#timeline'))
for s in career.get('sap_automation_vault', []):
    items.append(('Career', f"SAP Macro: {s.get('name')} [{s.get('tcode', 'MRF')}]", s.get('description', ''), 'career.html#vault'))
skills = career.get('skills_inventory', {})
for cat, sk_list in skills.items():
    if isinstance(sk_list, list):
        for sk in sk_list:
            items.append(('Career', f"Competency: {sk}", cat.replace('_', ' ').title(), 'career.html#resume'))

# 5. Finance
exec_m = finance.get('executive_metrics', {})
items.append(('Finance', f"True Net Worth: {exec_m.get('ground_truth_net_worth_formatted')}", 'Liquid + Equity - Liabilities', 'finance.html#banking'))
for b in finance.get('banking_strip', []):
    items.append(('Finance', f"{b.get('account_name')} ({b.get('institution')})", f"PKR {b.get('verified_statement_balance', '')}", 'finance.html#banking'))
fbr = finance.get('fbr_vault', {})
for ar in fbr.get('annual_returns', []):
    items.append(('Finance', f"FBR Tax Return Tax Year {ar.get('tax_year')}", f"Declared: PKR {ar.get('net_declared_assets', '')}", 'finance.html#tax'))
exp = finance.get('expense_intelligence', {})
for c in exp.get('cluster_summary', []):
    items.append(('Finance', f"Expense Cluster: {c.get('cluster')}", f"PKR {c.get('total_pkr', '')}", 'finance.html#banking'))

# 6. Health
wt = health.get('walking_telemetry', {})
today = wt.get('today', {})
items.append(('Health', f"Walking Telemetry: {today.get('steps_formatted', '10,420')} Steps", f"Goal: 10,000 · {today.get('distance_km', '8.13')} km", 'health.html#walking'))
gym = health.get('gym_workouts', {})
for sp in gym.get('splits', []):
    items.append(('Health', f"Gym Split: {sp.get('name')}", f"Target: {sp.get('target_muscles', '')}", 'health.html#gym'))
    for ex in sp.get('exercises', []):
        items.append(('Health', f"Exercise: {ex.get('name')}", f"PR: {ex.get('pr_weight_kg', ex.get('current_weight_kg'))}kg", 'health.html#gym'))
bio = health.get('family_biomarkers', {})
panels = bio.get('reference_panels', {})
if isinstance(panels, dict):
    for p_key, p_val in panels.items():
        items.append(('Health', f"Biomarker Panel: {p_val.get('name', p_key)}", p_val.get('description', ''), 'health.html#biomarkers'))
        for bm in p_val.get('biomarkers', []):
            items.append(('Health', f"Biomarker: {bm.get('name')} ({bm.get('code')})", f"Target: {bm.get('target_text', '')}", 'health.html#biomarkers'))
profiles = bio.get('profiles', [])
if isinstance(profiles, list):
    for pr in profiles:
        items.append(('Health', f"Health Profile: {pr.get('name')}", f"Blood: {pr.get('blood_group', 'N/A')}", 'health.html#biomarkers'))
circ = health.get('circadian_routines', {})
for sl in circ.get('schedule_slots', []):
    items.append(('Health', f"Routine: {sl.get('time')} — {sl.get('title')}", sl.get('target_metric', ''), 'health.html#routine'))
ins = health.get('insurance_emergency', {})
items.append(('Health', f"Insurance: {ins.get('policy_provider')} CTP ({ins.get('policy_number')})", f"Sponsor: {ins.get('corporate_sponsor')}", 'health.html#insurance'))
for sug in ins.get('daycare_surgeries', []):
    items.append(('Health', f"Daycare Surgery: {sug.get('procedure')}", sug.get('category', ''), 'health.html#insurance'))
for inv in ins.get('specialized_investigations', []):
    items.append(('Health', f"Outpatient Test: {inv.get('name')}", inv.get('coverage', ''), 'health.html#insurance'))
for h in ins.get('panel_hospitals', []):
    items.append(('Health', f"Panel Hospital: {h.get('name')}", f"{h.get('city')} · Emergency: {h.get('emergency')}", 'health.html#insurance'))

print(f"Total indexed items: {len(items)}")
counts = Counter([x[0] for x in items])
for k in sorted(counts.keys()):
    print(f"  {k}: {counts[k]}")
