#!/usr/bin/env python3
"""
Sikander OS — Module 06: Health, Fitness & Family Vitality Hub Verification Suite
Rigorous assertion tests verifying:
1. Data store integrity (sikander_health_data.json & sikander_health_data.js)
2. Sample workout CSV file structure and parsing (sample_workout_sheet.csv)
3. Walking Telemetry: 10k target, 10,420 steps, exact 19-day 10k streak, and triple-intake math
4. Gym Workouts: 4 splits, 24 exercises, 8 PRs with Epley formula, and zero-CORS CSV specs
5. Family Biomarkers: 5 panels, 4 profiles, demographic-aware clinical reference ranges (HDL, Ferritin, Uric Acid, HGB, HCT)
6. Circadian Routines: 9 schedule slots, 6 trackable habits, and 3.0L hydration protocol
7. Corporate Health Insurance: Novatex Jubilee CTP, 20 outpatient tests, 45 daycare surgeries, 7 panel hospitals
8. health.html features: Real CSV parser, sample CSV loader, URL hash routing, demographic-aware evaluation, Takeout parser, and 6 LocalStorage keys
9. index.html navigation and Module 06 linkage
"""

import os
import sys
import json
import csv
import re

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def evaluate_biomarker_py(b, val, gender="Male", age=30):
    """Python reference implementation of the client-side demographic-aware biomarker evaluator."""
    target_range = b
    target_text = b.get("target_text", "")

    if "gender_ranges" in b:
        gr = b["gender_ranges"]
        if age is not None and age < 12 and "Pediatric" in gr:
            target_range = gr["Pediatric"]
            target_text = target_range.get("target_text", target_text)
        elif gender == "Female" and "Female" in gr:
            target_range = gr["Female"]
            target_text = target_range.get("target_text", target_text)
        elif gender == "Male" and "Male" in gr:
            target_range = gr["Male"]
            target_text = target_range.get("target_text", target_text)

    opt = target_range.get("optimal") or target_range.get("optimal_range")
    border = target_range.get("borderline") or target_range.get("borderline_range")

    if opt and opt[0] <= val <= opt[1]:
        return "Optimal", target_text
    elif border and border[0] <= val <= border[1]:
        return "Borderline", target_text
    else:
        return "Attention", target_text


def verify_all():
    print("⚡ Starting Sikander OS Health & Vitality Hub Comprehensive Verification...")

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data", "health")
    json_path = os.path.join(data_dir, "sikander_health_data.json")
    js_path = os.path.join(data_dir, "sikander_health_data.js")
    sample_csv_path = os.path.join(data_dir, "sample_workout_sheet.csv")
    health_html_path = os.path.join(base_dir, "health.html")
    index_html_path = os.path.join(base_dir, "index.html")

    # ============================================================
    # 1. VERIFY DATA FILES EXIST & SYNTACTICALLY VALID
    # ============================================================
    assert os.path.exists(json_path), f"JSON file missing: {json_path}"
    assert os.path.exists(js_path), f"JS file missing: {js_path}"
    assert os.path.exists(sample_csv_path), f"Sample CSV missing: {sample_csv_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(js_path, "r", encoding="utf-8") as f:
        js_text = f.read().strip()
        assert js_text.startswith("window.__SIKANDER_HEALTH_DATA__ = {"), "JS file lacks window.__SIKANDER_HEALTH_DATA__ wrapper"
        assert js_text.endswith("};"), "JS file does not end with closing wrapper"

    print("✓ [1/9] Data files exist and are syntactically valid JSON & JS.")

    # ============================================================
    # 2. VERIFY SAMPLE WORKOUT CSV TEMPLATE
    # ============================================================
    with open(sample_csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        headers = [h.strip() for h in reader[0]]
        assert "Split" in headers and any("exercise" in h.lower() for h in headers) and any("working weight" in h.lower() for h in headers)
        assert any("pr weight" in h.lower() for h in headers) and any("1rm" in h.lower() for h in headers)

        csv_splits = set()
        csv_exercises = []
        for row in reader[1:]:
            if len(row) >= 2:
                csv_splits.add(row[0])
                csv_exercises.append(row[1])

        assert len(csv_splits) == 4, f"Expected 4 splits in sample CSV, found {len(csv_splits)}: {csv_splits}"
        assert len(csv_exercises) == 24, f"Expected exactly 24 exercises in sample CSV, found {len(csv_exercises)}"

    print("✓ [2/9] Verified sample workout CSV template (4 splits, 24 exercises, valid CSV schema).")

    # ============================================================
    # 3. VERIFY WALKING TELEMETRY & EXACT 19-DAY STREAK
    # ============================================================
    walk = data.get("walking_telemetry", {})
    assert walk.get("daily_target") == 10000, "Daily target should be 10,000 steps"
    today = walk.get("today", {})
    assert today.get("steps") == 10420, f"Today steps must be exactly 10,420, got {today.get('steps')}"
    assert today.get("distance_km") == 8.13, f"Today distance must be 8.13 km, got {today.get('distance_km')}"
    assert today.get("calories_kcal") == 438, f"Today calories must be 438 kcal, got {today.get('calories_kcal')}"
    assert today.get("target_achieved") is True, "Today target should be achieved"

    # Verify triple intake math: 4250 + 3320 + 2850 == 10420
    sum_intakes = today.get("morning_walk_steps", 0) + today.get("factory_movement_steps", 0) + today.get("evening_walk_steps", 0)
    assert sum_intakes == 10420, f"Triple intake breakdown sum must equal 10,420, got {sum_intakes}"

    # Verify 30-day history records
    history = walk.get("history_30_days", [])
    assert len(history) == 30, f"Expected exactly 30 daily history records, got {len(history)}"

    # Today is index 29 in 30-day history
    assert history[-1]["steps"] == 10420, f"Last history record must be today's 10,420 steps, got {history[-1]['steps']}"

    # Calculate streak backward from today
    backward_streak = 0
    for r in reversed(history):
        if r["steps"] >= 10000:
            backward_streak += 1
        else:
            break

    assert backward_streak == 19, f"Calculated 10k streak must be EXACTLY 19 days, got {backward_streak}!"
    assert history[10]["steps"] == 9450, f"Day 10 (20 days ago) must be 9,450 to terminate streak at 19, got {history[10]['steps']}"
    for i in range(11, 30):
        assert history[i]["steps"] >= 10000, f"History day index {i} ({history[i]['date']}) must be >= 10,000 steps"

    streak = walk.get("streak_summary", {})
    assert streak.get("current_10k_streak_days") == 19, f"Streak summary days must be 19, got {streak.get('current_10k_streak_days')}"
    assert "19-Day 10k Streak 🔥" in streak.get("status_badge", ""), f"Status badge mismatch: {streak.get('status_badge')}"

    print("✓ [3/9] Walking Telemetry: 10,420 steps today, verified triple intake (4250+3320+2850), and exact 19-day 10k streak verified.")

    # ============================================================
    # 4. VERIFY GYM WORKOUTS & ZERO-CORS CONNECTOR
    # ============================================================
    gym = data.get("gym_workouts", {})
    assert gym.get("weekly_frequency_target") == 4, "Weekly workout target should be 4 days"
    assert gym.get("current_consistency_streak_weeks") >= 6, "Consistency streak should be >= 6 weeks"

    splits = gym.get("splits", [])
    assert len(splits) == 4, f"Expected exactly 4 splits, got {len(splits)}"
    split_ids = [s["id"] for s in splits]
    assert split_ids == ["push_a", "pull_a", "legs_abs", "push_b"], f"Unexpected split IDs: {split_ids}"

    total_exercises = 0
    for s in splits:
        ex_list = s.get("exercises", [])
        assert len(ex_list) == 6, f"Split {s['id']} must contain exactly 6 exercises, got {len(ex_list)}"
        total_exercises += len(ex_list)
        for ex in ex_list:
            assert ex["sets"] > 0
            assert ex["current_weight_kg"] >= 0
            assert ex["pr_weight_kg"] >= ex["current_weight_kg"]
            assert ex["estimated_1rm_kg"] >= ex["pr_weight_kg"]

    assert total_exercises == 24, f"Expected 24 exercises total across 4 splits, got {total_exercises}"

    prs = gym.get("personal_records", [])
    assert len(prs) == 8, f"Expected 8 PR records, got {len(prs)}"
    for pr in prs:
        # Verify Epley 1RM formula: weight * (1 + reps / 30.0)
        expected_1rm = round(pr["weight_kg"] * (1 + pr["reps"] / 30.0), 1)
        assert abs(pr["estimated_1rm_kg"] - expected_1rm) < 0.2, f"PR {pr['exercise']} 1RM math mismatch: {pr['estimated_1rm_kg']} vs {expected_1rm}"

    connector = gym.get("google_sheets_connector", {})
    assert "export?format=csv" in connector.get("export_format", "")
    assert connector.get("sample_csv_path") == "data/health/sample_workout_sheet.csv"

    print("✓ [4/9] Gym Workouts: 4 splits, 24 exercises, 8 PRs with Epley 1RM math, and zero-CORS CSV specs verified.")

    # ============================================================
    # 5. VERIFY FAMILY BIOMARKERS & DEMOGRAPHIC-AWARE RANGES
    # ============================================================
    bio = data.get("family_biomarkers", {})
    panels = bio.get("reference_panels", {})
    required_panels = ["lipid_panel", "metabolic_glucose", "vital_micronutrients", "renal_hepatic", "complete_blood_count"]
    for rp in required_panels:
        assert rp in panels, f"Missing clinical reference panel: {rp}"

    # Verify gender_ranges in reference panels
    lipid_bios = {b["code"]: b for b in panels["lipid_panel"]["biomarkers"]}
    assert "gender_ranges" in lipid_bios["HDL"], "HDL must have gender_ranges"
    assert lipid_bios["HDL"]["gender_ranges"]["Male"]["optimal"] == [40.0, 999.0]
    assert lipid_bios["HDL"]["gender_ranges"]["Female"]["optimal"] == [50.0, 999.0]

    cbc_bios = {b["code"]: b for b in panels["complete_blood_count"]["biomarkers"]}
    assert "gender_ranges" in cbc_bios["HGB"], "HGB must have gender_ranges"
    assert cbc_bios["HGB"]["gender_ranges"]["Female"]["optimal"] == [12.0, 15.5]
    assert cbc_bios["HGB"]["gender_ranges"]["Pediatric"]["optimal"] == [11.5, 14.5]

    micro_bios = {b["code"]: b for b in panels["vital_micronutrients"]["biomarkers"]}
    assert "gender_ranges" in micro_bios["FERRITIN"], "FERRITIN must have gender_ranges"

    # TEST DEMOGRAPHIC-AWARE EVALUATION LOGIC
    # Case 1: Spouse HGB 13.2 g/dL (Female, Age 32)
    spouse_status, _ = evaluate_biomarker_py(cbc_bios["HGB"], 13.2, gender="Female", age=32)
    assert spouse_status == "Optimal", f"Spouse HGB 13.2 must evaluate to Optimal, got {spouse_status}"

    # Verify that under Male standard range [13.5, 17.5], 13.2 would have failed (Borderline)
    male_eval, _ = evaluate_biomarker_py(cbc_bios["HGB"], 13.2, gender="Male", age=34)
    assert male_eval == "Borderline", f"13.2 g/dL under male standard must be Borderline, got {male_eval}"

    # Case 2: Khadija Ferritin 28 ng/mL (Pediatric, Age 4)
    khadija_ferr_status, _ = evaluate_biomarker_py(micro_bios["FERRITIN"], 28.0, gender="Female", age=4)
    assert khadija_ferr_status == "Optimal", f"Khadija Ferritin 28 must evaluate to Optimal, got {khadija_ferr_status}"

    # Case 3: HDL 46 mg/dL
    # For Male: Optimal (> 40)
    male_hdl_status, _ = evaluate_biomarker_py(lipid_bios["HDL"], 46.0, gender="Male", age=34)
    assert male_hdl_status == "Optimal", f"Male HDL 46 must evaluate to Optimal, got {male_hdl_status}"
    # For Female: Borderline (40-49.9, since optimal is > 50)
    female_hdl_status, _ = evaluate_biomarker_py(lipid_bios["HDL"], 46.0, gender="Female", age=32)
    assert female_hdl_status == "Borderline", f"Female HDL 46 must evaluate to Borderline, got {female_hdl_status}"

    # Check Profiles
    profiles = bio.get("profiles", [])
    assert len(profiles) == 4, f"Expected 4 profiles, got {len(profiles)}"
    profile_ids = [p["id"] for p in profiles]
    assert profile_ids == ["sikander", "spouse", "khadija", "parents"]

    print("✓ [5/9] Family Biomarkers: 5 clinical panels, 4 profiles, and demographic-aware ranges verified.")

    # ============================================================
    # 6. VERIFY CIRCADIAN ROUTINES & HYDRATION
    # ============================================================
    routines = data.get("circadian_routines", {})
    slots = routines.get("schedule_slots", [])
    assert len(slots) == 9, f"Expected 9 circadian schedule slots, got {len(slots)}"
    assert "05:30" in slots[0]["time"], f"First slot should start at 05:30, got {slots[0]['time']}"
    assert "22:30" in slots[-1]["time"], f"Last slot should start at 22:30, got {slots[-1]['time']}"

    habits = routines.get("habits_checklist", [])
    assert len(habits) == 6, f"Expected 6 daily habits, got {len(habits)}"
    for h in habits:
        assert h["streak"] > 0

    assert routines.get("hydration_target_liters") == 3.0, "Hydration target must be 3.0L"

    print("✓ [6/9] Circadian Routines: 9 schedule slots, 6 daily habits, and 3.0L hydration verified.")

    # ============================================================
    # 7. VERIFY CORPORATE HEALTH COVERAGE (JUBILEE CTP)
    # ============================================================
    ins = data.get("insurance_emergency", {})
    assert ins.get("policy_provider") == "Jubilee Life Insurance Company Ltd"
    assert ins.get("corporate_sponsor") == "Novatex Limited"
    assert ins.get("policy_number") == "JLI-NVX-CTP-2024-8842"
    assert ins.get("emergency_contacts", {}).get("toll_free_24_7") == "021-111-111-545"

    investigations = ins.get("specialized_investigations", [])
    assert len(investigations) == 20, f"Expected 20 outpatient investigations, got {len(investigations)}"

    surgeries = ins.get("daycare_surgeries", [])
    assert len(surgeries) == 45, f"Expected 45 covered daycare surgeries, got {len(surgeries)}"
    for sur in surgeries:
        assert sur["status"] == "Covered"
        assert len(sur["procedure"]) > 3

    hospitals = ins.get("panel_hospitals", [])
    assert len(hospitals) == 7, f"Expected 7 panel hospitals, got {len(hospitals)}"

    print("✓ [7/9] Corporate Coverage: Novatex Jubilee CTP, 20 outpatient tests, 45 daycare surgeries, 7 hospitals verified.")

    # ============================================================
    # 8. VERIFY health.html ARCHITECTURE & SCRIPTS
    # ============================================================
    assert os.path.exists(health_html_path), f"health.html missing: {health_html_path}"
    with open(health_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Verify LocalStorage keys
    ls_keys = [
        "LS_STEPS_KEY",
        "LS_GYM_SETS_KEY",
        "LS_GYM_CSV_KEY",
        "LS_SHEETS_URL_KEY",
        "LS_BIOMARKERS_KEY",
        "LS_WATER_KEY",
        "LS_HABITS_KEY",
    ]
    for key in ls_keys:
        assert key in html, f"health.html missing key definition: {key}"

    # Verify real CSV parser functions
    assert "function parseGymCSV(" in html, "health.html missing parseGymCSV function"
    assert "function splitCSVLine(" in html, "health.html missing splitCSVLine parser"
    assert "loadSampleCSVTemplate" in html, "health.html missing loadSampleCSVTemplate"
    assert "function importPastedCSV()" in html, "health.html missing importPastedCSV"

    # Verify URL hash routing
    assert "function handleHashRouting()" in html, "health.html missing handleHashRouting"
    assert "hashchange" in html, "health.html missing hashchange event listener"

    # Verify demographic-aware biomarker evaluation in JS
    assert "function evaluateBiomarker(b, val, gender, age)" in html, "evaluateBiomarker signature must accept gender and age"
    assert "b.gender_ranges" in html, "evaluateBiomarker must reference b.gender_ranges"
    assert "Pediatric" in html and "Female" in html and "Male" in html

    # Verify real Google Takeout parser
    assert "function applyImportedSteps(count, sourceName)" in html, "health.html missing applyImportedSteps"
    assert "function handleTakeoutFile(e)" in html, "health.html missing handleTakeoutFile"
    assert "intVal" in html or "dataset" in html, "health.html Takeout parser missing Google Fit aggregate parser"

    # Verify UI Modals
    assert 'id="modal-paste-csv"' in html, "health.html missing modal-paste-csv"
    assert 'id="modal-step-logger"' in html, "health.html missing modal-step-logger"
    assert 'id="modal-gym-logger"' in html, "health.html missing modal-gym-logger"
    assert 'id="modal-biomarker"' in html, "health.html missing modal-biomarker"
    assert 'id="modal-takeout"' in html, "health.html missing modal-takeout"

    print("✓ [8/9] health.html: Real CSV parser, URL hash routing, demographic-aware evaluator, Takeout importer, and 5 modals verified.")

    # ============================================================
    # 9. VERIFY index.html INTEGRATION
    # ============================================================
    assert os.path.exists(index_html_path), f"index.html missing: {index_html_path}"
    with open(index_html_path, "r", encoding="utf-8") as f:
        idx = f.read()

    assert "health.html" in idx, "index.html must contain link to health.html"
    assert "health.html#biomarkers" in idx or "Health, Fitness" in idx, "index.html must link to Module 06"

    print("✓ [9/9] index.html links to health.html and integrates Module 06.")

    print("\n🎉 ALL 9 SIKANDER OS HEALTH & VITALITY VERIFICATION SUITES PASSED FLAWLESSLY!")
    return True


if __name__ == "__main__":
    verify_all()
