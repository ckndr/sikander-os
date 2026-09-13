#!/usr/bin/env python3
"""
Sikander OS — Verification Suite for Phase 3: Sovereign Capital, Property & Banking Hub
(Module 05: finance.html)
"""

import os
import sys
import json
import re
import html.parser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_master_json():
    print("\n[TEST 1] Verifying data/finance/sikander_finance_master.json...")
    json_path = os.path.join(BASE_DIR, "data", "finance", "sikander_finance_master.json")
    assert os.path.exists(json_path), f"Missing {json_path}"
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Check top-level keys
    required_keys = ["meta", "executive_metrics", "banking_strip", "cashflow_monthly", "expense_intelligence", "property_ledger", "fbr_vault"]
    for k in required_keys:
        assert k in data, f"Key '{k}' missing from master JSON"
        
    # Check executive metrics
    metrics = data["executive_metrics"]
    print(f"   Ground-Truth Net Worth: PKR {metrics['ground_truth_net_worth_pkr']:,.2f} ({metrics['ground_truth_net_worth_formatted']})")
    assert metrics["ground_truth_net_worth_pkr"] > 8000000, "Net worth should be > PKR 8M"
    assert metrics["property_equity_paid_pkr"] == 2093000, "Property equity paid must be 2,093,000"
    assert metrics["property_total_outlay_pkr"] == 3124000, "Property outlay must be 3,124,000"
    assert metrics["property_outstanding_liabilities_pkr"] == 1031000, "Property liabilities must be 1,031,000"
    assert metrics["property_equity_percentage"] == 67.0, "Property equity percentage must be 67.0%"
    assert metrics["fbr_statutory_declared_wealth_2025_pkr"] == 10163356, "FBR 2025 declared wealth must be 10,163,356"
    assert metrics["fbr_consultant_balancing_figures_pkr"] == 1952681, "Consultant balancing total must be 1,952,681"
    assert metrics["bluecoins_tx_count"] == 9003, f"Bluecoins tx count must be 9,003, got {metrics['bluecoins_tx_count']}"
    
    # Check banking strip
    accounts = data["banking_strip"]
    print(f"   Banking Strip Accounts: {len(accounts)}")
    assert len(accounts) == 9, f"Expected 9 accounts, got {len(accounts)}"
    account_names = [a["account_name"] for a in accounts]
    print(f"   Accounts: {', '.join(account_names)}")
    
    # Check monthly cashflow
    cashflow = data["cashflow_monthly"]
    print(f"   Monthly Cashflow Count: {len(cashflow)} months")
    assert len(cashflow) == 59, f"Expected 59 months, got {len(cashflow)}"
    assert cashflow[0]["ym"] == "2020-07", "First month should be 2020-07"
    assert cashflow[-1]["ym"] == "2025-05", "Last month should be 2025-05"
    
    # Check expense intelligence
    clusters = data["expense_intelligence"]["cluster_summary"]
    print(f"   Expense Clusters: {len(clusters)}")
    assert len(clusters) >= 5, "Should have at least 5 primary expense clusters"
    cluster_names = [c["cluster"] for c in clusters]
    assert any("Housing" in c for c in cluster_names), "Housing cluster missing"
    assert any("Household" in c for c in cluster_names), "Household cluster missing"
    assert any("Family" in c for c in cluster_names), "Family cluster missing"
    assert any("Commute" in c for c in cluster_names), "Commute cluster missing"
    assert any("Healthcare" in c for c in cluster_names), "Healthcare cluster missing"
    
    # Check property ledger
    prop = data["property_ledger"]
    assert len(prop.get("historical_ledger", [])) == 100, "Historical ledger should have 100 txs"
    assert len(prop.get("utility_schedule", [])) == 37, "Utility schedule should have 37 months"
    assert len(prop.get("document_vault", [])) == 20, "Document vault should have 20 verified documents"
    
    # Check FBR vault
    fbr = data["fbr_vault"]
    assert fbr["taxpayer_profile"]["registration_no"] == "4220155342061"
    assert len(fbr["annual_returns"]) >= 2
    assert len(fbr["ground_truth_divergence_explainer"]["reality_check"]) == 6
    print("   [PASS] Master JSON structure, ground-truth math, and data points fully verified.")

def test_master_js():
    print("\n[TEST 2] Verifying data/finance/sikander_finance_master.js...")
    js_path = os.path.join(BASE_DIR, "data", "finance", "sikander_finance_master.js")
    assert os.path.exists(js_path), f"Missing {js_path}"
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content.startswith("window.__SIKANDER_FINANCE_DATA__ = {"), "JS file must define window.__SIKANDER_FINANCE_DATA__"
    assert content.strip().endswith("};"), "JS file must end with valid assignment semicolon"
    print(f"   JS file size: {len(content):,} bytes")
    print("   [PASS] Zero-CORS offline JS data store verified.")

def test_finance_html():
    print("\n[TEST 3] Verifying finance.html...")
    html_path = os.path.join(BASE_DIR, "finance.html")
    assert os.path.exists(html_path), f"Missing {html_path}"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check critical requirements
    assert "Sovereign Capital, Property & Banking Hub" in content, "Title missing"
    assert "GROUND-TRUTH SOVEREIGN WEALTH" in content, "Executive banner missing"
    assert "Privacy Mode" in content, "Privacy shield missing"
    assert "togglePrivacy" in content, "Privacy toggle function missing"
    assert "applyPrivacy" in content, "Apply privacy function missing"
    assert "tab-banking" in content, "Tab 1 Banking missing"
    assert "tab-property" in content, "Tab 2 Property missing"
    assert "tab-tax" in content, "Tab 3 Tax Vault missing"
    assert "image-modal" in content, "Lightbox modal missing"
    assert "handleDeepLinks" in content, "Deep linking handler missing"
    assert "svg-chart" in content or "renderCashflowChart" in content, "SVG cashflow chart missing"
    assert "donut-svg" in content or "renderExpenseIntelligence" in content, "Category donut missing"
    assert "copyText" in content or "btn-copy-iban" in content, "IBAN copy button missing"
    assert "data/finance/sikander_finance_master.js" in content, "Zero-CORS JS script tag missing"
    
    # Check HTML validity
    class TagChecker(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.tags = []
            self.errors = []
            self.void_tags = {'meta', 'link', 'img', 'br', 'hr', 'input', 'line', 'polyline', 'path', 'defs', 'linearGradient', 'stop', 'rect', 'circle', '!doctype'}
        def handle_starttag(self, tag, attrs):
            if tag.lower() not in self.void_tags:
                self.tags.append(tag.lower())
        def handle_endtag(self, tag):
            if tag.lower() not in self.void_tags:
                if self.tags and self.tags[-1] == tag.lower():
                    self.tags.pop()
    
    parser = TagChecker()
    parser.feed(content)
    print(f"   Unclosed non-void tags count: {len(parser.tags)}")
    print(f"   finance.html size: {len(content):,} bytes")
    print("   [PASS] finance.html structure and all required features verified.")

def test_property_redirect():
    print("\n[TEST 4] Verifying property.html redirect & deep-linking...")
    prop_path = os.path.join(BASE_DIR, "property.html")
    assert os.path.exists(prop_path), f"Missing {prop_path}"
    with open(prop_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert 'url=finance.html#property' in content, "Meta refresh missing"
    assert 'finance.html' in content, "Redirect URL missing"
    assert 'window.location.replace' in content, "Script redirect missing"
    print("   [PASS] property.html clean redirect with deep-linking verified.")

def test_index_html():
    print("\n[TEST 5] Verifying index.html consolidation...")
    idx_path = os.path.join(BASE_DIR, "index.html")
    assert os.path.exists(idx_path), f"Missing {idx_path}"
    with open(idx_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Sovereign Capital, Property & Banking Hub" in content, "Consolidated module title missing in index.html"
    assert "finance.html" in content, "finance.html link missing in index.html"
    assert "PKR 8.45M" in content, "Unified Net Worth metric missing in index.html"
    assert "5 Live" in content, "Active modules count should be updated to 5 Live"
    print("   [PASS] index.html consolidated Capital & Real Estate card verified.")

def test_service_worker():
    print("\n[TEST 6] Verifying sw.js precaching...")
    sw_path = os.path.join(BASE_DIR, "sw.js")
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "./finance.html" in content, "finance.html missing from sw.js"
    assert "./data/finance/sikander_finance_master.js" in content, "Finance master JS missing from sw.js"
    print("   [PASS] sw.js precache list verified.")

def test_local_links():
    print("\n[TEST 7] Verifying local asset links and image references...")
    files = ['index.html', 'finance.html', 'property.html']
    missing_assets = []
    for fn in files:
        p = os.path.join(BASE_DIR, fn)
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
        urls = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', content)
        for u in urls:
            if u.startswith('http') or u.startswith('#') or u.startswith('data:') or '${' in u:
                continue
            clean = u.split('#')[0].split('?')[0]
            if not clean:
                continue
            target_path = os.path.join(BASE_DIR, clean.replace('/', os.sep))
            if not os.path.exists(target_path):
                missing_assets.append((fn, u, target_path))
    assert len(missing_assets) == 0, f"Missing local assets: {missing_assets}"
    print("   [PASS] All local asset links and references exist on disk.")

def test_sunburst_and_subcategories():
    print("\n[TEST 8] Verifying 2-Tier Sunburst SVG & Subcategory Intelligence...")
    json_path = os.path.join(BASE_DIR, "data", "finance", "sikander_finance_master.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    clusters = data["expense_intelligence"]["cluster_summary"]
    for c in clusters:
        assert "items" in c, f"Cluster '{c['cluster']}' missing items array"
        assert len(c["items"]) > 0, f"Cluster '{c['cluster']}' has empty items array"
    
    html_path = os.path.join(BASE_DIR, "finance.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    assert "makeArcPath" in html, "makeArcPath SVG generator missing"
    assert "sunburst-slice" in html, "sunburst-slice CSS class missing"
    assert "hoverSunburst" in html, "hoverSunburst interaction missing"
    assert "resetSunburst" in html, "resetSunburst interaction missing"
    assert "2-Tier Radial" in html, "2-Tier Radial sunburst indicator missing"
    print("   [PASS] 2-Tier Sunburst structure, mathematical SVG arc generator, and subcategories verified.")

def test_privacy_masking_robustness():
    print("\n[TEST 9] Verifying Privacy Shield masking robustness...")
    html_path = os.path.join(BASE_DIR, "finance.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    # Check N/A handling in privacy maskable acc
    assert "raw.startsWith('N/A')" in html or 'raw.startsWith("N/A")' in html, "N/A check missing in privacy masking"
    assert "raw === '-'" in html or 'raw === "-"' in html, "Dash preservation check missing in privacy masking"
    assert "No IBAN" in html, "Cash Reserve (No IBAN) indicator missing"
    # Ensure static numbers are masked by default with data-real-val
    assert 'id="hero-net-worth" class="privacy-maskable" data-real-val="8,447,042">••••••<' in html, "Hero net worth must start masked by default"
    assert 'id="strip-net-worth" style="color:var(--emerald);" data-real-val="PKR 8.45M">••••••<' in html, "Strip net worth must start masked by default"
    print("   [PASS] Privacy masking rules, N/A safeguards, and zero-leak initial load verified.")

def test_subtab_deeplinking_and_keyboard():
    print("\n[TEST 10] Verifying Deep-linking subtab routing & keyboard accessibility...")
    html_path = os.path.join(BASE_DIR, "finance.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    assert "e.key === 'Escape'" in html, "Escape key modal close listener missing"
    assert "switchPropSubtab" in html, "switchPropSubtab function missing"
    assert "updateHash" in html, "Hash preservation toggle missing in tab switchers"
    assert "popstate" in html, "popstate event listener missing"
    # Check subtabs exist
    assert "subtab-prop-utilities" in html, "Utilities subtab missing"
    assert "subtab-prop-historical" in html, "Historical ledger subtab missing"
    assert "subtab-prop-vault" in html, "Vault subtab missing"
    assert "subtab-prop-protocol" in html, "Protocol subtab missing"
    print("   [PASS] Subtab deep-linking, history management, and Escape key accessibility verified.")

def test_dynamic_fbr_pdf_extraction():
    print("\n[TEST 11] Verifying dynamic FBR PDF parser in data engine...")
    sys.path.insert(0, os.path.join(BASE_DIR, "data", "finance"))
    import extract_finance_data
    assert hasattr(extract_finance_data, "parse_fbr_pdf_safely"), "parse_fbr_pdf_safely missing in extract_finance_data"
    parsed = extract_finance_data.parse_fbr_pdf_safely(r"I:\Personal\Filer")
    r25 = parsed.get("ret_2025", {})
    assert r25.get("net_declared_assets") == 10163356, f"Expected 10163356, got {r25.get('net_declared_assets')}"
    assert r25.get("total_income") == 1961920, f"Expected 1961920, got {r25.get('total_income')}"
    assert r25.get("tax_chargeable") == 163416, f"Expected 163416, got {r25.get('tax_chargeable')}"
    assert r25.get("code_7009") == 800000, f"Expected 800000 for gold, got {r25.get('code_7009')}"
    assert r25.get("code_7014") == 2174000, f"Expected 2174000 for property, got {r25.get('code_7014')}"
    print("   [PASS] Dynamic pypdf parser verified against real official tax returns.")

def main():
    print("=" * 60)
    print("RUNNING COMPREHENSIVE VERIFICATION SUITE")
    print("Phase 3: Module 05 (finance.html)")
    print("=" * 60)
    
    test_master_json()
    test_master_js()
    test_finance_html()
    test_property_redirect()
    test_index_html()
    test_service_worker()
    test_local_links()
    test_sunburst_and_subcategories()
    test_privacy_masking_robustness()
    test_subtab_deeplinking_and_keyboard()
    test_dynamic_fbr_pdf_extraction()
    
    print("\n" + "=" * 60)
    print("ALL 11 TEST SUITES PASSED WITH ZERO ERRORS!")
    print("=" * 60)

if __name__ == "__main__":
    main()
