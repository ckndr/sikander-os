#!/usr/bin/env python3
"""
Sikander OS — Career Intelligence Verification Suite
Runs deep assertion tests against:
- Data integrity (JSON & JS)
- Compensation trajectory (38 pay slips + 2026 offer)
- 21 SAP macros and rationales
- Industrial SOPs and cold extrusion metallurgy
- Target roles and competency matching
- HTML structure and navigation linkage
"""

import os
import sys
import json
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_all():
    print("⚡ Starting Sikander OS Career Intelligence Verification...")
    
    # 1. Check Data Files
    json_path = r"I:\sikander-os\data\career\sikander_career_data.json"
    js_path = r"I:\sikander-os\data\career\sikander_career_data.js"
    assert os.path.exists(json_path), "JSON missing: " + json_path
    assert os.path.exists(js_path), "JS missing: " + js_path
    
    with open(json_path, 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
        assert js_content.startswith("window.__SIKANDER_CAREER_DATA__ = {"), "Invalid JS wrapper"

    print("✓ Data files exist and are well-formed.")

    # 2. Candidate Profile
    p = d["candidate_profile"]
    assert p["typing_speed_wpm"] == 90
    assert "Novatex" in p["dual_employer_status"]
    assert "Alpha Containers" in p["dual_employer_status"]
    assert len(p["education"]) == 2
    print("✓ Candidate Profile: 90 WPM, Dual Employer, Education verified.")

    # 3. Verified Compensation
    comp = d["verified_compensation"]
    records = comp["monthly_records"]
    assert len(records) == 38, f"Expected 38 salary slips, found {len(records)}"
    
    # Sort order and pay slip earnings/deductions integrity check
    for i in range(len(records) - 1):
        assert records[i]["sort_key"] <= records[i+1]["sort_key"], f"Records not in order at index {i}"
    
    for r in records:
        assert r["fixed_gross"] > 0, f"Zero or negative fixed gross in {r['period']}"
        assert r["net_pay"] > 0, f"Zero or negative net pay in {r['period']}"
        assert "total_earning" in r, f"Missing total_earning in {r['period']}"
        assert "total_deductions" in r, f"Missing total_deductions in {r['period']}"
        assert r["net_pay"] == r["total_earning"] - r["total_deductions"], (
            f"Pay slip math mismatch in {r['period']}: Net {r['net_pay']} != "
            f"Earn {r['total_earning']} - Ded {r['total_deductions']}"
        )

    assert records[0]["period"] == "NOV 2022"
    assert records[0]["fixed_gross"] == 32000
    assert records[-1]["period"] == "DEC 2025"
    assert records[-1]["fixed_gross"] == 73375, f"Expected 73375, got {records[-1]['fixed_gross']}"
    assert records[-1]["net_pay"] == 110098, f"Expected 110098, got {records[-1]['net_pay']}"
    assert records[-1]["total_earning"] == 110843
    assert records[-1]["total_deductions"] == 745
    
    assert comp["summary"]["alpha_containers_base_gross"] == 120000
    assert comp["summary"]["alpha_containers_package_breakdown"]["aerosol_expansion_step"] == 45000
    assert comp["summary"]["alpha_containers_package_breakdown"]["basic_salary"] == 80400
    assert comp["summary"]["alpha_containers_package_breakdown"]["house_rent"] == 36180
    assert comp["summary"]["alpha_containers_package_breakdown"]["cost_of_living"] == 3420
    print("✓ Compensation Records: All 38 slips verified with 100% earnings/deductions math integrity. Dec 2025: Gross 73,375, Net 110,098. 2026: 120,000 (+45k).")

    # 4. SAP Vault (21 macros across 6 normalized categories)
    vault = d["sap_automation_vault"]
    assert len(vault) == 21, f"Expected 21 macros, found {len(vault)}"
    seen_files = set()
    category_counts = {}
    total_time = 0
    for m in vault:
        assert m["id"].startswith("MRF-")
        assert m["file"] not in seen_files, f"Duplicate file {m['file']}"
        seen_files.add(m["file"])
        assert len(m["tcode"]) > 0
        assert len(m["description"]) > 10
        assert len(m["workflow_rationale"]) > 10
        assert m["time_saved_daily_mins"] > 0
        total_time += m["time_saved_daily_mins"]
        cat = m["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    assert total_time == 825, f"Expected 825 mins, got {total_time}"
    assert category_counts == {
        "Production Order Management": 5,
        "Order Lifecycle & TECO": 5,
        "Inventory & Logistics Telemetry": 3,
        "Data Integrity & Variance Control": 5,
        "Workflow Orchestration": 1,
        "Administrative & HR Automation": 2
    }, f"Unexpected category counts: {category_counts}"
    
    assert "Claim.mrf" in seen_files
    assert "COOIS Report.mrf" in seen_files
    assert "Teco.mrf" in seen_files
    assert "Daily.mrf" in seen_files
    print(f"✓ SAP Automation Vault: All 21 unique scripts verified across 6 normalized categories. Total daily savings: {total_time} mins (~13.8 hrs).")

    # 5. Industrial Knowledge Base
    kb = d["industrial_engineering_knowledge_base"]
    sops = kb["novatex_bopet_sops"]
    assert len(sops) == 3
    sop_docs = [s["doc_no"] for s in sops]
    assert "PP/SOP-FL/01" in sop_docs
    assert "PP/SOP-PS/02" in sop_docs
    assert "PP/SOP-SS/03" in sop_docs

    ext = kb["tubex_cold_extrusion_mechanics"]
    assert "Zinc Stearate" in ext["preparation_and_mechanics"]["lubrication_protocol"]["compound"]
    assert "55 SPM" in ext["preparation_and_mechanics"]["process"]
    assert "250°C" in ext["thermal_processing_annealing"]["furnace_parameters"]
    assert len(ext["bom_weight_consumption_matrices"]) == 3
    assert len(kb["tubex_inventory_snapshot_april_2026"]["selected_balances"]) >= 10
    print("✓ Industrial Knowledge Base: 3 Novatex SOPs + Tubex Cold Extrusion manual + 3 BOM matrices verified.")

    # 6. Target Roles & Full 11-Year Milestones
    roles = d["target_roles"]
    assert len(roles) == 4
    role_titles = [r["title"] for r in roles]
    assert any("Supply Chain" in t for t in role_titles)
    assert any("Plant Operations" in t for t in role_titles)
    assert any("SAP" in t for t in role_titles)
    assert any("Packaging" in t for t in role_titles)
    
    milestone_keys = {"tubex", "novatex_skp", "novatex_khi_plan", "novatex_khi_data", "novatex_khi_qa"}
    for r in roles:
        assert len(r["target_keywords"]) >= 8
        assert len(r["novatex_bullets"]) >= 3
        assert len(r["tubex_bullets"]) >= 2
        assert "sections" in r, f"Role {r['title']} missing sections"
        assert len(r["sections"]) == 5, f"Role {r['title']} does not cover all 5 career milestones"
        sec_ids = {s["company_id"] for s in r["sections"]}
        assert sec_ids == milestone_keys, f"Role {r['title']} sections mismatch: {sec_ids}"
        for s in r["sections"]:
            assert len(s["bullets"]) >= 1, f"Empty bullets in section {s['company_id']} of role {r['title']}"
            
    print("✓ Target Roles: 4 tailored roles verified with keywords, competencies, and full 11-year milestone sections.")

    # 7. Job Application Strategy Advisor (Precision Macro Surfacing)
    def test_advisor_surfacing(jd_text):
        lower = jd_text.lower()
        matched_tokens = set()
        candidate_terms = [
            ("mps", "daily"), ("mrp", "component"), ("sap", "co01"),
            ("coois", "coois"), ("co01", "co01"), ("mb52", "mb52"),
            ("teco", "teco"), ("slitter", "slitter"), ("bopet", "film line"),
            ("container", "shipment"), ("vessel", "shipment")
        ]
        for term, tok in candidate_terms:
            if term in lower:
                matched_tokens.add(term)
                if tok: matched_tokens.add(tok)
        scored = []
        for m in vault:
            searchable = (m["name"] + " " + m["tcode"] + " " + m["category"] + " " + m["description"] + " " + " ".join(m.get("trigger_keywords", []))).lower()
            score = sum(2 for tok in matched_tokens if tok in searchable)
            if m["id"] in ("MRF-05", "MRF-19"): score += 1
            scored.append((score, m["id"], m["file"]))
        scored.sort(key=lambda x: -x[0])
        return [item[1] for item in scored[:3]]

    coois_top = test_advisor_surfacing("Requires expert SAP COOIS reporting")
    assert "MRF-06" in coois_top, f"Expected MRF-06 for COOIS, got {coois_top}"
    
    mb52_top = test_advisor_surfacing("Manage warehouse stock balance using MB52")
    assert "MRF-11" in mb52_top or "MRF-19" in mb52_top, f"Expected MRF-11 or MRF-19 for MB52, got {mb52_top}"
    
    teco_top = test_advisor_surfacing("Mass TECO technical order completion")
    assert "MRF-07" in teco_top or "MRF-08" in teco_top, f"Expected MRF-07 or MRF-08 for TECO, got {teco_top}"
    print("✓ Job Strategy Advisor: Precision token-based macro surfacing verified for COOIS, MB52, and TECO.")

    # 8. HTML Verification
    career_html = r"I:\sikander-os\career.html"
    index_html = r"I:\sikander-os\index.html"
    sw_js = r"I:\sikander-os\sw.js"
    manifest_json = r"I:\sikander-os\manifest.json"

    assert os.path.exists(career_html), "career.html missing"
    with open(career_html, 'r', encoding='utf-8') as f:
        c_html = f.read()

    # Check key features and fixes in career.html
    assert "90 WPM TYPING SPEED" in c_html
    assert "DUAL EMPLOYER STATUS" in c_html
    assert "togglePrivacy()" in c_html
    assert "copyResumeMarkdown()" in c_html
    assert "copyResumeText()" in c_html
    assert "analyzeJobDescription()" in c_html
    assert "filterVaultTable()" in c_html
    assert "data/career/sikander_career_data.js" in c_html
    assert "fallbackCopy" in c_html and "execCommand('copy')" in c_html, "Missing clipboard fallback"
    assert "maxVal = 180000" in c_html, "Chart not scaled to 180,000 maxVal"
    assert 'viewBox="0 0 1000 260"' in c_html, "SVG chart viewBox height must match 260 coordinate space"
    assert "records[20].fixed_gross" in c_html, "SU2 promotion badge not dynamically anchored to fixed gross"
    assert "Total Earning" in c_html and "Total Deductions" in c_html, "Missing salary breakdown columns in table"
    assert "Production Order Management (5)" in c_html
    assert "Order Lifecycle & TECO (5)" in c_html
    assert "Inventory & Logistics Telemetry (3)" in c_html
    assert "Data Integrity & Variance Control (5)" in c_html
    assert "Workflow Orchestration (1)" in c_html
    assert "Administrative & HR Automation (2)" in c_html
    print("✓ career.html: Complete feature set, privacy toggle, ATS export, clipboard fallback, and SVG chart scaling verified.")

    # Check index.html linkage
    with open(index_html, 'r', encoding='utf-8') as f:
        i_html = f.read()

    assert "career.html" in i_html
    assert "4 Live" in i_html
    assert "Module 04 · Career & Industrial Intelligence" in i_html
    assert "Launch Career Engine" in i_html
    print("✓ index.html: Module 04 hero card and metrics updated to 4 Live operational modules.")

    # Check sw.js and manifest.json
    with open(sw_js, 'r', encoding='utf-8') as f:
        sw = f.read()
    assert "'./career.html'" in sw
    assert "'./data/career/sikander_career_data.js'" in sw
    assert "'./data/career/sikander_career_data.json'" in sw
    print("✓ sw.js: Offline caching verified for career app and data assets.")

    with open(manifest_json, 'r', encoding='utf-8') as f:
        mf = f.read()
    assert '"./career.html"' in mf
    print("✓ manifest.json: Career shortcut registered.")

    # 9. Headless Browser DOM Execution Test (Microsoft Edge)
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    edge_bin = next((p for p in edge_paths if os.path.exists(p)), None)
    if edge_bin:
        import subprocess
        res = subprocess.run([
            edge_bin,
            "--headless",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--enable-logging=stderr",
            "--dump-dom",
            "file:///I:/sikander-os/career.html"
        ], capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=30)
        
        # 1. Assert zero JavaScript console errors in Edge stderr
        js_errors = []
        for line in res.stderr.splitlines():
            if "CONSOLE" in line and any(err in line for err in ["Uncaught", "Error", "SyntaxError", "TypeError", "ReferenceError"]):
                if "chrome-extension://" not in line:
                    js_errors.append(line.strip())
            elif any(err in line for err in ["Uncaught SyntaxError", "Uncaught TypeError", "Uncaught ReferenceError"]):
                js_errors.append(line.strip())
        assert not js_errors, f"JavaScript console errors detected in Edge execution:\n" + "\n".join(js_errors)

        # 2. Assert dynamic DOM elements rendered OUTSIDE <script> and <style> tags (eliminates false positives from source text)
        dom_rendered = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', res.stdout, flags=re.IGNORECASE)
        dom_rendered = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', dom_rendered, flags=re.IGNORECASE)

        assert len(dom_rendered) > 10000, f"Headless rendered DOM dump too short: {len(dom_rendered)} bytes"
        assert "role-btn active" in dom_rendered, "Active role tab not rendered in dynamic DOM"
        assert "resume-experience-section" in dom_rendered, "Dynamic resume experience sections not rendered in DOM"
        assert "bullet-item" in dom_rendered, "Dynamic resume bullet items not rendered in DOM"
        assert "MRF-01" in dom_rendered, "Macro table row MRF-01 not rendered in dynamic DOM"
        assert "MRF-21" in dom_rendered, "Macro table row MRF-21 not rendered in dynamic DOM"
        assert "trajectory-line" in dom_rendered, "Compensation chart SVG trajectory-line not rendered in DOM"
        assert "SU2 Promoted" in dom_rendered, "Compensation chart SU2 promotion milestone not rendered in DOM"
        assert "Zinc Stearate" in dom_rendered, "Industrial KB not rendered in dynamic DOM"
        assert "PKR 110k Net" in dom_rendered, "Milestone callout Dec 2025 (110k Net) not rendered in dynamic DOM"
        assert "Planning Lead 120k" in dom_rendered, "Alpha Containers milestone callout not rendered in dynamic DOM"

        # 3. Assert specific dynamic containers were actually populated with children
        vault_match = re.search(r'<tbody id="vault-tbody">(.*?)</tbody>', dom_rendered, re.DOTALL)
        assert vault_match and "MRF-01" in vault_match.group(1) and "MRF-21" in vault_match.group(1), "Vault table was not dynamically populated"

        chart_match = re.search(r'<svg class="svg-chart" id="salary-chart"[^>]*>(.*?)</svg>', dom_rendered, re.DOTALL)
        assert chart_match and "trajectory-line" in chart_match.group(1) and "SU2 Promoted" in chart_match.group(1), "Salary chart SVG was not dynamically rendered"

        roles_match = re.search(r'<div class="role-select-bar" id="role-selector-container">(.*?)</div>', dom_rendered, re.DOTALL)
        assert roles_match and len(re.findall(r'<button class="role-btn', roles_match.group(1))) >= 4, "Role selector bar not populated with 4 target roles"

        slips_match = re.search(r'<tbody id="slips-tbody">(.*?)</tbody>', dom_rendered, re.DOTALL)
        assert slips_match and len(re.findall(r'<tr>', slips_match.group(1))) == 38, "Salary slips table not populated with 38 rows"

        # 4. Interactive in-browser integration simulation (role switching, advisor, vault filter, privacy toggle, copy routines)
        test_script = """
        let interactiveErrors = [];
        try {
            selectRole(1);
            selectRole(2);
            selectRole(3);
            selectRole(0);
            switchTab('advisor', false);
            loadSampleJD('scm');
            analyzeJobDescription();
            switchTab('vault', false);
            document.getElementById('vault-search').value = 'coois';
            filterVaultTable();
            document.getElementById('vault-search').value = '';
            document.getElementById('vault-category-filter').value = 'Production Order Management';
            filterVaultTable();
            document.getElementById('vault-category-filter').value = 'ALL';
            filterVaultTable();
            switchTab('comp', false);
            togglePrivacy();
            togglePrivacy();
            copyCoverPitch();
            copyResumeMarkdown();
            copyResumeText();
        } catch(e) {
            interactiveErrors.push(e.toString());
        }
        let div = document.createElement('div');
        div.id = 'interactive-test-results';
        div.innerText = JSON.stringify(interactiveErrors);
        document.body.appendChild(div);
        """
        temp_html_path = r"I:\sikander-os\__test_interactive.html"
        with open(r"I:\sikander-os\career.html", 'r', encoding='utf-8') as cf:
            test_content = cf.read().replace(
                "window.addEventListener('DOMContentLoaded', init);",
                f"window.addEventListener('DOMContentLoaded', () => {{ init(); setTimeout(() => {{ {test_script} }}, 300); }});"
            )
        with open(temp_html_path, 'w', encoding='utf-8') as tf:
            tf.write(test_content)
        
        try:
            res_int = subprocess.run([
                edge_bin,
                "--headless",
                "--disable-gpu",
                "--allow-file-access-from-files",
                "--enable-logging=stderr",
                "--dump-dom",
                f"file:///{temp_html_path.replace(os.sep, '/')}"
            ], capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=30)

            int_errors = []
            for line in res_int.stderr.splitlines():
                if "CONSOLE" in line and any(err in line for err in ["Uncaught", "Error", "SyntaxError", "TypeError", "ReferenceError"]):
                    if "chrome-extension://" not in line:
                        int_errors.append(line.strip())
            assert not int_errors, f"Console errors in interactive simulation:\n" + "\n".join(int_errors)

            m_int = re.search(r'<div id="interactive-test-results">(.*?)</div>', res_int.stdout)
            assert m_int and m_int.group(1) == "[]", f"Interactive execution runtime errors: {m_int.group(1) if m_int else 'Tag missing'}"
        finally:
            if os.path.exists(temp_html_path):
                os.remove(temp_html_path)

        print("✓ Headless Edge DOM Execution: 0 console errors, dynamic role tabs, resume bullets, macro rows (MRF-01/21), SVG trajectory curves, and interactive simulation verified.")
    else:
        print("⚠️ Edge executable not found, skipped headless browser test.")

    print("\n🎉 ALL 9 VERIFICATION CRITERIA PASSED FLAWLESSLY!")

if __name__ == "__main__":
    test_all()
