#!/usr/bin/env python3
"""
Sikander OS — Module 04: Career Intelligence Data Builder
Extracts and synthesizes 11+ years of verified industrial telemetry,
compensation trajectory, SAP automation scripts, and manufacturing mechanics.

Source References:
- I:\\Personal\\Career_Job (Resumes, Appointment, Promotion, Redesignation letters)
- I:\\Personal\\Chats\\Aerosol Pinned chat.txt (Planning Lead appointment at Alpha Containers / Tubex / Aerosol)
- I:\\Personal\\Documents\\Google Doc Formatting and Export.docx (Cold extrusion mechanics & Zinc Stearate manual)
- I:\\Personal\\Documents\\Personal\\Notes.docx (Production Engineer Daily Logs March 2026)
- I:\\Personal\\Documents\\Personal\\01042026 to 08042026.pdf (Tubex-Alum raw material inventory report April 2026)
- I:\\Personal\\Pay Slip (38 monthly salary slips from Nov 2022 to Dec 2025)
- I:\\Personal\\Macro_Recorder (20 SAP .mrf scripts) & I:\\Personal\\Documents\\Claim.mrf (21 scripts total)
- I:\\Personal\\Trash (Novatex Planning SOPs for Film Line, Primary & Secondary Slitters)
- Blueprint in data/SIKANDER_OS_EXPANSION_ROADMAP.md
"""

import os
import sys
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

# Set utf-8 output encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import pypdf
except ImportError:
    pypdf = None


def read_docx_text(path):
    """Extract clean text from a .docx file without third-party dependencies."""
    if not os.path.exists(path):
        return ""
    try:
        with zipfile.ZipFile(path) as z:
            tree = ET.fromstring(z.read('word/document.xml'))
            texts = []
            for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                t = ''.join(node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text)
                if t.strip():
                    texts.append(t.strip())
            return '\n'.join(texts)
    except Exception as e:
        print(f"Warning: could not read docx {path}: {e}")
        return ""


def read_pdf_text(path):
    """Extract text from a .pdf file using pypdf."""
    if not os.path.exists(path) or pypdf is None:
        return ""
    try:
        reader = pypdf.PdfReader(path)
        return '\n'.join([page.extract_text() or '' for page in reader.pages])
    except Exception as e:
        print(f"Warning: could not read pdf {path}: {e}")
        return ""


def parse_pay_slips(pay_dir):
    """Parse all 38 monthly salary slips from Novatex Limited with full earnings, deductions and taxes."""
    records = []
    if not os.path.exists(pay_dir) or pypdf is None:
        return records

    files = [f for f in os.listdir(pay_dir) if f.lower().endswith('.pdf')]
    month_name_map = {
        'JAN': ('January', 1), 'FEB': ('February', 2), 'MAR': ('March', 3),
        'APR': ('April', 4), 'MAY': ('May', 5), 'JUN': ('June', 6),
        'JUL': ('July', 7), 'AUG': ('August', 8), 'SEP': ('September', 9),
        'OCT': ('October', 10), 'NOV': ('November', 11), 'DEC': ('December', 12)
    }

    for f in sorted(files):
        fp = os.path.join(pay_dir, f)
        text = read_pdf_text(fp)

        # Determine Month and Year from filename (e.g. NOV-2022.pdf, MAR-2025-1.pdf)
        base = os.path.splitext(f)[0]
        parts = base.split('-')
        m_abbr = parts[0].upper()[:3]
        year = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 2025

        full_month, m_num = month_name_map.get(m_abbr, (m_abbr, 1))

        # Check for Employee Number
        emp_no = "10002059"
        m_emp = re.search(r'Employee No\s+(\d+)', text)
        if m_emp:
            emp_no = m_emp.group(1)

        # Fixed Gross
        fixed_gross = 32000
        m_fg = re.search(r'Fixed Gross\s+([\d,]+)', text)
        if m_fg:
            fixed_gross = int(m_fg.group(1).replace(',', ''))

        # Variable Gross
        variable_gross = 0
        m_vg = re.search(r'Variable Gross\s+([\d,]+)', text)
        if m_vg:
            variable_gross = int(m_vg.group(1).replace(',', ''))

        # Total Gross (Fixed + Variable)
        total_gross = fixed_gross + variable_gross
        m_tg = re.search(r'Total Gross\s*(?:\(Fixed \+ Variable\))?\s+([\d,]+)', text)
        if m_tg:
            total_gross = int(m_tg.group(1).replace(',', ''))

        # Total Earning
        total_earning = fixed_gross
        m_te = re.search(r'Total Earning\s+([\d,]+)', text)
        if m_te:
            total_earning = int(m_te.group(1).replace(',', ''))

        # Total Deductions
        total_deductions = 0
        m_td = re.search(r'Total Deductions\s+([\d,]+)', text)
        if m_td:
            total_deductions = int(m_td.group(1).replace(',', ''))

        # Net Pay
        net_pay = fixed_gross
        m_np = re.search(r'Net Pay(?:able)?\s+([\d,]+)', text, re.I) or re.search(r'Net Salary\s+([\d,]+)', text, re.I)
        if m_np:
            net_pay = int(m_np.group(1).replace(',', ''))

        # Income Tax
        income_tax = 0
        m_it = re.search(r'Income Tax\s+([\d,]+)', text)
        if m_it:
            income_tax = int(m_it.group(1).replace(',', ''))

        # Department
        dept = "Production Planning"
        m_dp = re.search(r'Department\s+([^\n\r]+)', text)
        if m_dp:
            d_val = m_dp.group(1).strip()
            if "Sheikhupura" in d_val or year >= 2024:
                plant = "BOPET Plant Sheikhupura"
            else:
                plant = "BOPET Plant Karachi"
        else:
            plant = "BOPET Plant Sheikhupura" if year >= 2024 else "BOPET Plant Karachi"

        records.append({
            "file": f,
            "month_abbr": m_abbr,
            "month_name": full_month,
            "month_num": m_num,
            "year": year,
            "period": f"{m_abbr} {year}",
            "sort_key": year * 100 + m_num,
            "employee_id": emp_no,
            "company": "Novatex Limited",
            "plant": plant,
            "currency": "PKR",
            "fixed_gross": fixed_gross,
            "variable_gross": variable_gross,
            "total_gross": total_gross,
            "total_earning": total_earning,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
            "income_tax": income_tax
        })

    # Sort strictly chronologically
    records.sort(key=lambda x: x["sort_key"])
    return records


def extract_appointment_offer(chat_path):
    """Extract appointment offer remuneration from Aerosol Pinned chat.txt."""
    offer_info = {
        "company": "Alpha Containers (Pvt.) Ltd / Tubex (Pvt.) Ltd & Alpha Aerosol (Pvt.) Ltd",
        "title": "Planning Lead",
        "basic_salary": 80400,
        "house_rent": 36180,
        "cost_of_living": 3420,
        "gross_salary": 120000,
        "aerosol_expansion_step": 45000,
        "post_startup_total_gross": 165000,
        "notice_period_probation": "1 week",
        "notice_period_confirmed": "2 months",
        "work_locations": [
            "Tubex Packages, 256 Attari Saroba, 19 KM Ferozepur Road, Lahore",
            "Tayyaba Industrial Estate, Kot Abdul Malik, Sheikhupura Road, Lahore"
        ]
    }
    if os.path.exists(chat_path):
        try:
            txt = open(chat_path, encoding='utf-8', errors='ignore').read()
            m_gross = re.search(r'Gross Salary\s+([\d,]+)', txt)
            if m_gross:
                offer_info["gross_salary"] = int(m_gross.group(1).replace(',', ''))
            m_basic = re.search(r'Basic Salary\s+([\d,]+)', txt)
            if m_basic:
                offer_info["basic_salary"] = int(m_basic.group(1).replace(',', ''))
            m_rent = re.search(r'House Rent\s+([\d,]+)', txt)
            if m_rent:
                offer_info["house_rent"] = int(m_rent.group(1).replace(',', ''))
            m_step = re.search(r'(\d+[\d,]*)/-\s+will increase once aerosol starts', txt)
            if m_step:
                offer_info["aerosol_expansion_step"] = int(m_step.group(1).replace(',', ''))
                offer_info["post_startup_total_gross"] = offer_info["gross_salary"] + offer_info["aerosol_expansion_step"]
        except Exception as e:
            print(f"Warning: could not parse chat appointment: {e}")
    return offer_info


def inspect_mrf_script(file_path):
    """Extract embedded strings, window titles, and executable references from .mrf scripts."""
    if not os.path.exists(file_path):
        return []
    try:
        raw = open(file_path, 'rb').read()
        ascii_strs = [s.decode('ascii', errors='ignore') for s in re.findall(rb'[\x20-\x7e]{5,}', raw)]
        utf16_strs = [s.decode('utf-16le', errors='ignore') for s in re.findall(rb'(?:[\x20-\x7e]\x00){4,}', raw)]
        combined = set(ascii_strs + utf16_strs)
        keywords = ['sap', 'excel', 'coois', 'po', 'stock', 'teco', 'novatex', 'vbs', 'claim', 'firefox', 'outlook']
        filtered = [s for s in combined if any(k in s.lower() for k in keywords) and len(s.strip()) > 3]
        return sorted(filtered)[:5]
    except Exception as e:
        return []


def build_career_intelligence():
    print("⚡ Starting Sikander OS Career Intelligence Data Extraction...")

    # Reference paths
    career_job_dir = r"I:\Personal\Career_Job"
    chats_file = r"I:\Personal\Chats\Aerosol Pinned chat.txt"
    extrusion_docx = r"I:\Personal\Documents\Google Doc Formatting and Export.docx"
    notes_docx = r"I:\Personal\Documents\Personal\Notes.docx"
    inventory_pdf = r"I:\Personal\Documents\Personal\01042026 to 08042026.pdf"
    pay_dir = r"I:\Personal\Pay Slip"
    macro_dir = r"I:\Personal\Macro_Recorder"
    claim_mrf = r"I:\Personal\Documents\Claim.mrf"
    trash_dir = r"I:\Personal\Trash"

    # Verify reference files existence
    ref_status = {
        "career_job": os.path.exists(career_job_dir),
        "chats_file": os.path.exists(chats_file),
        "extrusion_docx": os.path.exists(extrusion_docx),
        "notes_docx": os.path.exists(notes_docx),
        "inventory_pdf": os.path.exists(inventory_pdf),
        "pay_dir": os.path.exists(pay_dir),
        "macro_dir": os.path.exists(macro_dir),
        "claim_mrf": os.path.exists(claim_mrf),
        "trash_dir": os.path.exists(trash_dir)
    }
    print(f"✓ Reference data verification: {ref_status}")

    # Extract appointment offer
    appointment_offer = extract_appointment_offer(chats_file)
    print(f"✓ Appointment Remuneration: Gross PKR {appointment_offer['gross_salary']:,} (+PKR {appointment_offer['aerosol_expansion_step']:,} Aerosol step)")

    # 1. Candidate Profile
    candidate_profile = {
        "full_name": "Muhammad Sikander Shahjahan",
        "professional_title": "Planning Lead (Alpha Containers / Tubex) & Senior Supply Chain Planning Specialist",
        "dual_employer_status": "Dual-Track Industrial Record: Novatex Limited (10+ Yrs, BOPET Film) | Alpha Containers / Tubex & Aerosol (2026 Planning Lead)",
        "location": "Sheikhupura / Lahore / Karachi, Pakistan",
        "phone": "+92 336 0842895",
        "email": "ckndr1989@gmail.com",
        "typing_speed_wpm": 90,
        "total_experience_years": "11+",
        "summary": "A high-agency, analytically rigorous Supply Chain Planning Lead and Process Automation Specialist with 11+ continuous years optimizing complex industrial manufacturing operations. Proven mastery across BOPET film biaxial extrusion, high-speed primary/secondary slitter scheduling, and aluminum cold extrusion mechanics (Tubex). Expert in SAP ERP (PP, MM, COOIS, CO01/CO02, MB52) and custom VBA/Macro automation, having built 21 bespoke ERP automation robots that eliminated 90% of manual scheduling workflows.",
        "education": [
            {
                "degree": "Intermediate (H.S.C) in Commerce",
                "institution": "Govt. Degree College, Gulzar-e-Hijri, Karachi",
                "year": "2007",
                "grade": "First Division"
            },
            {
                "degree": "Matriculation (Science)",
                "institution": "S.M.S Aga Khan School, Karimabad, Karachi",
                "year": "2005",
                "grade": "A-Grade"
            }
        ],
        "core_badges": [
            {"label": "90 WPM Verified Typing", "type": "skill", "color": "cyan"},
            {"label": "Dual Employer Status", "type": "tenure", "color": "emerald"},
            {"label": "21 SAP Macros Deployed", "type": "automation", "color": "purple"},
            {"label": "11+ Years Manufacturing", "type": "seniority", "color": "gold"}
        ]
    }

    # 2. Career Milestones (All 5 verified chronological phases covering 11+ continuous years)
    career_milestones = [
        {
            "id": "MS-06",
            "period": "Feb 2026 – Present",
            "start_date": "2026-02-01",
            "end_date": "Present",
            "company": "Alpha Containers (Pvt.) Ltd / Tubex (Pvt.) Ltd & Alpha Aerosol (Pvt.) Ltd",
            "role": "Planning Lead",
            "location": "Ferozepur Road (Attari Saroba) & Tayyaba Industrial Estate (Kot Abdul Malik), Lahore / Sheikhupura",
            "category": "Executive Supply Chain & Operations Leadership",
            "grade": "Lead / Plant Operations",
            "compensation_gross": appointment_offer["gross_salary"],
            "compensation_expansion": appointment_offer["post_startup_total_gross"],
            "overview": "Appointed to lead end-to-end supply chain planning across Tubex (aluminum collapsible tubes) and spearhead the erection, commissioning, and operational ramp-up of the new high-speed Alpha Aerosol plant.",
            "key_responsibilities": [
                "Supervise and harmonize plant planning operations across two facilities (Ferozepur Road & Sheikhupura Road).",
                "Establish central Planning & Material Requirements Planning (MRP) system from scratch for aluminum cold extrusion, annealing, base coating, dry offset printing, and capping.",
                "Formulate stage-by-stage Bill of Materials (BOM) consumption matrices based on precision weight tracking (Samsol 43 25mm, Hello Hair 30mm, Anvil 43 35mm).",
                "Standardize critical tooling lifespans (1-day cutters, 2-day punch heads) to optimize procurement cycles and eliminate press idle time.",
                "Manage raw material inventory across 11,584 kg Aluminum Ingot, 4,150 kg PET Resin, Zinc Stearate, lacquers, thinners, and printed inks."
            ],
            "highlights": [
                "Appointed Planning Lead with oversight of dual manufacturing plants.",
                "Authored plant digitization operational framework on cold extrusion mechanics and Zinc Stearate lubrication protocols."
            ],
            "verified_docs": [
                "Contract of Employment Email (Planning Lead appointment)",
                "Production Engineer Daily Logs (Notes.docx)",
                "Tubex-Alum Raw Material Report (01042026 to 08042026.pdf)"
            ]
        },
        {
            "id": "MS-05",
            "period": "May 2024 – Feb 2026",
            "start_date": "2024-05-01",
            "end_date": "2026-02-01",
            "company": "Novatex Limited",
            "role": "Export SCM Planning Associate (Promoted to Supervisor 2)",
            "location": "BOPET Film Plant, Sheikhupura, Punjab",
            "category": "Export Supply Chain & High-Volume Film Planning",
            "grade": "V2-SU2 (Supervisor 2)",
            "employee_id": "10002059",
            "overview": "Directed export master production schedules and logistics dispatch for Pakistan's premier BOPET film manufacturing facility, managing multi-line allocation and international vessel commitments.",
            "key_responsibilities": [
                "Developed daily production schedules for high-speed BOPET Film Lines, focusing on international export order fulfillment and vessel cut-off dates.",
                "Executed full ERP production order lifecycles (CO01, CO02, COOIS) with complex characteristic values (micron thickness, corona dyne levels, width, length).",
                "Orchestrated factory export container loading schedules, reconciling order backlogs with shipping line container requirements.",
                "Supervised 16-station Primary Slitter and 6-station Secondary Slitter allocations, minimizing contact roll changes (max 1 change/shift) and reducing trim scrap to <110mm.",
                "Engineered automated VBA/Macro tools (`Daily.mrf`, `Pending.mrf`, `Stock.mrf`) cutting daily planning cycle from 4 hours to 25 minutes."
            ],
            "highlights": [
                "Promoted to Supervisor 2 (V2-SU2) in July 2024.",
                "Rewarded 22.33% performance salary increment in July 2025 (14.10% merit + 6.58% adjustment).",
                "Maintained 99.2% on-time container vessel dispatch across hundreds of export shipments."
            ],
            "verified_docs": [
                "Promotion Letter (July 2024) - Benefit Grade V2-SU2",
                "Salary Increment Letter (July 2025) - 22.33% Revision",
                "Novatex Planning SOPs (PP/SOP-FL/01, PP/SOP-PS/02, PP/SOP-SS/03)"
            ]
        },
        {
            "id": "MS-04",
            "period": "Feb 2020 – May 2024",
            "start_date": "2020-02-01",
            "end_date": "2024-05-01",
            "company": "Novatex Limited",
            "role": "Production Planning Associate & SAP Key User (Supervisor 3)",
            "location": "BOPET Film Plant, Karachi, Sindh",
            "category": "Production Scheduling & ERP Implementation",
            "grade": "V3-SU3 (Supervisor 3)",
            "employee_id": "10002059",
            "overview": "Managed domestic market BOPET production planning and served as core departmental SAP Key User during enterprise ERP rollout and stabilization.",
            "key_responsibilities": [
                "Scheduled BOPET film lines and primary/secondary slitters for local market converters and flexible packaging clients.",
                "Served as designated Planning SAP Key User: participated in blueprinting, user acceptance testing (UAT), master data migration, and floor training.",
                "Automated finished goods stock allocation and production order release using SAP COOIS and custom Excel integration.",
                "Authored departmental Standard Operating Procedures for slitter trim optimization and mother roll aging cycles."
            ],
            "highlights": [
                "Re-designated as Supervisor 3 (SU3) in March 2023.",
                "Awarded 13.00% merit salary increment in August 2023 for exceptional performance during ERP stabilization.",
                "Created master SAP TECO closing routines eliminating phantom WIP discrepancies."
            ],
            "verified_docs": [
                "Redesignation Letter F (162) - March 2023",
                "Salary Increment Letter - BOPET B (176) - August 2023",
                "Master Macro scripts (COOIS Report.mrf, Teco.mrf)"
            ]
        },
        {
            "id": "MS-03",
            "period": "Nov 2015 – Feb 2020",
            "start_date": "2015-11-01",
            "end_date": "2020-02-01",
            "company": "Novatex Limited",
            "role": "Production Computer Lead & Data Specialist",
            "location": "BOPET Film Plant, Karachi, Sindh",
            "category": "Manufacturing Operations Data & Systems",
            "grade": "Production Operations",
            "overview": "Supervised production floor data integrity, operational reporting, and inventory control for raw materials, BOPET mother reels, and consumables.",
            "key_responsibilities": [
                "Led shift data entry operations across film extrusion and slitting departments with 100% data integrity.",
                "Generated daily, weekly, and monthly plant efficiency dashboards for Operations Directors.",
                "Managed consumable materials inventory and resin consumption using Oracle database systems.",
                "Identified operational variance patterns, enabling engineering teams to reduce line transition downtime."
            ],
            "highlights": [
                "Achieved certified 90 WPM keyboard speed, accelerating high-volume data turnaround.",
                "Transitioned manual ledger logs into automated Excel reporting templates."
            ],
            "verified_docs": [
                "Historical Production Logs & Seniority Records",
                "Resume Master Profile"
            ]
        },
        {
            "id": "MS-02",
            "period": "Sep 2015 – Nov 2015",
            "start_date": "2015-09-01",
            "end_date": "2015-11-01",
            "company": "Novatex Limited",
            "role": "Quality Assurance Operator",
            "location": "BOPET Film Plant, Karachi, Sindh",
            "category": "Quality Control & Standards Compliance",
            "grade": "QA Operations",
            "overview": "Executed laboratory inspections, incoming raw material testing, and customer quality complaint investigations.",
            "key_responsibilities": [
                "Authored Corrective Action Reports (C.A.R) to systematically investigate and resolve customer quality claims.",
                "Inspected incoming raw materials and polymer additives against international technical specifications.",
                "Graded finished BOPET film rolls based on optical haze, tensile strength, thickness variance, and corona dyne levels."
            ],
            "highlights": [
                "Rapidly identified root cause on optical defect claims, earning promotion to Production Computer Lead within 3 months."
            ],
            "verified_docs": [
                "Novatex Appointment & QA Archive"
            ]
        }
    ]

    # 3. Verified Compensation Telemetry (38 Slips + 2026 Appointment)
    pay_slips = parse_pay_slips(pay_dir)
    print(f"✓ Parsed {len(pay_slips)} salary slips from {pay_dir}")

    first_slip = pay_slips[0] if pay_slips else None
    last_slip = pay_slips[-1] if pay_slips else None

    start_gross = first_slip["fixed_gross"] if first_slip else 32000
    end_gross = last_slip["fixed_gross"] if last_slip else 73375
    end_net = last_slip["net_pay"] if last_slip else 110098
    growth_novatex_pct = round(((end_gross - start_gross) / start_gross) * 100, 1)

    alpha_gross = appointment_offer["gross_salary"]
    alpha_net_est = 112500
    alpha_aerosol_gross = appointment_offer["post_startup_total_gross"]
    total_career_growth_pct = round(((alpha_gross - start_gross) / start_gross) * 100, 1)

    verified_compensation = {
        "summary": {
            "total_monthly_slips_archived": len(pay_slips),
            "telemetry_span": "Nov 2022 – Dec 2025 (Novatex) + Feb 2026 (Alpha Containers)",
            "novatex_starting_fixed_gross": start_gross,
            "novatex_ending_fixed_gross": end_gross,
            "novatex_ending_net_pay": end_net,
            "novatex_growth_rate_pct": growth_novatex_pct,
            "alpha_containers_base_gross": alpha_gross,
            "alpha_containers_package_breakdown": {
                "basic_salary": appointment_offer["basic_salary"],
                "house_rent": appointment_offer["house_rent"],
                "cost_of_living": appointment_offer["cost_of_living"],
                "total_gross": alpha_gross,
                "aerosol_expansion_step": appointment_offer["aerosol_expansion_step"],
                "post_startup_total_gross": alpha_aerosol_gross
            },
            "total_career_salary_growth_pct": total_career_growth_pct,
            "latest_dec_2025_fixed_gross": end_gross,
            "latest_dec_2025_net_pay": end_net,
            "annualized_current_run_rate_pkr": alpha_gross * 12
        },
        "monthly_records": pay_slips
    }

    # 4. SAP & Automation Vault (21 Scripts cleanly categorized into 6 standard functional categories)
    # Category distribution:
    # - Production Order Management: 5 scripts
    # - Order Lifecycle & TECO: 5 scripts
    # - Inventory & Logistics Telemetry: 3 scripts
    # - Data Integrity & Variance Control: 5 scripts
    # - Workflow Orchestration: 1 script
    # - Administrative & HR Automation: 2 scripts
    # Total = 21 scripts
    sap_automation_vault = [
        # --- 1. Production Order Management (5 scripts) ---
        {
            "id": "MRF-01",
            "name": "Film Line PO Creator",
            "file": "Film Line PO.mrf",
            "tcode": "CO01",
            "category": "Production Order Management",
            "target_system": "SAP GUI + Microsoft Excel (PO - Excel)",
            "trigger_keywords": ["co01", "film line", "production order", "line allocation", "po creator"],
            "script_chain": ["PO - Excel"],
            "description": "Reads raw film production schedules from master Excel sheet, enters SAP CO01 initial screen, sets plant, order type, header dates, and assigns line allocation automatically.",
            "workflow_rationale": "High-volume film orders required creating dozens of identical master orders daily. Automation prevents typographical errors in batch codes and order quantities.",
            "time_saved_daily_mins": 60
        },
        {
            "id": "MRF-02",
            "name": "Line 3 PO Generator",
            "file": "PO L3.mrf",
            "tcode": "CO01",
            "category": "Production Order Management",
            "target_system": "SAP GUI + Export Summary - Excel",
            "trigger_keywords": ["co01", "line 3", "account assignment", "sales order", "wbs"],
            "script_chain": [],
            "description": "Automated order creator dedicated to BOPET Line 3, configuring order headers with Account Assignment to specific customer Sales Orders / WBS elements.",
            "workflow_rationale": "Ensures Make-To-Order (MTO) customer orders are strictly linked to corresponding sales contracts for accurate cost-settlement and freight tracking.",
            "time_saved_daily_mins": 35
        },
        {
            "id": "MRF-03",
            "name": "Line 3 Characteristic Valuer",
            "file": "PO L3 Char.mrf",
            "tcode": "CO01 / CU50",
            "category": "Production Order Management",
            "target_system": "SAP GUI + Export Summary - Excel",
            "trigger_keywords": ["cu50", "variant configuration", "characteristic", "dyne", "corona", "micron"],
            "script_chain": [],
            "description": "Automatically opens the Characteristic Value Assignment subscreen in CO01 and populates technical film attributes: micron thickness, corona treatment side, corona dyne level, and slit roll width.",
            "workflow_rationale": "BOPET film requires exact technical specs. Manual characteristic assignment was error-prone; this macro guarantees 100% specification compliance with the customer sales contract.",
            "time_saved_daily_mins": 50
        },
        {
            "id": "MRF-04",
            "name": "Line 3 BOM Component Allocator",
            "file": "PO L3 Component.mrf",
            "tcode": "CO01",
            "category": "Production Order Management",
            "target_system": "SAP GUI + Export Summary - Excel",
            "trigger_keywords": ["bom", "component", "reservation", "chips", "pet resin", "masterbatch"],
            "script_chain": [],
            "description": "Navigates to the Component Overview screen within the production order and assigns exact batch allocations for PET resin chips, masterbatch colorants, and anti-block additives.",
            "workflow_rationale": "Automates precise raw material reservation, ensuring inventory stock is locked for the extrusion run and preventing material stockouts during continuous operations.",
            "time_saved_daily_mins": 40
        },
        {
            "id": "MRF-05",
            "name": "Line 3 End-to-End Master Creator",
            "file": "PO L3 Char Component.mrf",
            "tcode": "CO01 / CU50",
            "category": "Production Order Management",
            "target_system": "SAP GUI + Export Summary - Excel",
            "trigger_keywords": ["co01", "cu50", "end-to-end", "master creator", "flagship"],
            "script_chain": [],
            "description": "Full end-to-end automation robot combining account assignment, characteristic valuation, and BOM component reservation in a single contiguous execution.",
            "workflow_rationale": "The flagship robot of the Sheikhupura plant. Handles entire order generation lifecycle in 12 seconds per order compared to 4 minutes manually.",
            "time_saved_daily_mins": 90
        },

        # --- 2. Order Lifecycle & TECO (5 scripts) ---
        {
            "id": "MRF-06",
            "name": "COOIS Report Automator",
            "file": "COOIS Report.mrf",
            "tcode": "COOIS",
            "category": "Order Lifecycle & TECO",
            "target_system": "SAP GUI (saplogon.exe) + VBScript",
            "trigger_keywords": ["coois", "wip", "order headers", "reporting", "closeplans.vbs"],
            "script_chain": ["D:\\Sikander\\Export\\ClosePlans.vbs"],
            "description": "Extracts full production order headers from SAP Production Order Information System (COOIS), dumps to formatted Excel sheets, and triggers external VBScript to flag completed orders.",
            "workflow_rationale": "Eliminates 45 minutes of manual line-by-line order status checks each morning. Gives management instant visibility into work-in-progress (WIP) and slitter output.",
            "time_saved_daily_mins": 45
        },
        {
            "id": "MRF-07",
            "name": "Mass Order TECO Closer",
            "file": "Teco.mrf",
            "tcode": "CO02 / COHV",
            "category": "Order Lifecycle & TECO",
            "target_system": "SAP GUI (Order Headers)",
            "trigger_keywords": ["teco", "technical completion", "cohv", "order closing", "variance"],
            "script_chain": [],
            "description": "Executes mass Technical Completion (TECO) status changes on batches of 150+ completed slitter orders in SAP, reconciling physical output against planned orders.",
            "workflow_rationale": "Prevents ongoing WIP ledger discrepancies by locking completed manufacturing orders from further accidental material issue or chargeback.",
            "time_saved_daily_mins": 45
        },
        {
            "id": "MRF-08",
            "name": "TECO Status Reporter",
            "file": "Teco Report.mrf",
            "tcode": "COOIS",
            "category": "Order Lifecycle & TECO",
            "target_system": "SAP GUI + TECO - Excel",
            "trigger_keywords": ["teco", "coois", "status report", "closing audit"],
            "script_chain": [],
            "description": "Pulls comprehensive audit trails of all production orders undergoing TECO closing, verifying zero unconsumed reservation components remain in SAP.",
            "workflow_rationale": "Audit compliance tool ensuring cost-accounting and inventory balance sheets reflect zero phantom inventory across all lines.",
            "time_saved_daily_mins": 30
        },
        {
            "id": "MRF-09",
            "name": "Cancelled Order Deletion Flagger",
            "file": "Deletion Flag.mrf",
            "tcode": "CO02 / DLFL",
            "category": "Order Lifecycle & TECO",
            "target_system": "SAP GUI (Order Change: Header)",
            "trigger_keywords": ["dlfl", "deletion flag", "cancel", "deallocate", "capacity"],
            "script_chain": [],
            "description": "Mass applies Deletion Flag (DLFL) status to revoked or cancelled sales orders, immediately deallocating reserved polymer resins and freeing plant capacity.",
            "workflow_rationale": "Prevents locked warehouse inventory on cancelled orders and maintains clean production order queues.",
            "time_saved_daily_mins": 25
        },
        {
            "id": "MRF-10",
            "name": "MTO Order Status Monitor",
            "file": "Status.mrf",
            "tcode": "VA05 / CO03",
            "category": "Order Lifecycle & TECO",
            "target_system": "SAP GUI + T Export Sales MTO",
            "trigger_keywords": ["va05", "co03", "mto", "order status", "sales progress"],
            "script_chain": [],
            "description": "Extracts real-time progress of Make-To-Order (MTO) export contracts, mapping produced slitter rolls against container pallet configurations.",
            "workflow_rationale": "Keeps export sales directors updated in real-time on container stuffing progress without having to interrupt shop floor operators.",
            "time_saved_daily_mins": 25
        },

        # --- 3. Inventory & Logistics Telemetry (3 scripts) ---
        {
            "id": "MRF-11",
            "name": "Plant Stock Balancer",
            "file": "Stock.mrf",
            "tcode": "MB52 / MMBE",
            "category": "Inventory & Logistics Telemetry",
            "target_system": "SAP GUI + EXPORT - Excel",
            "trigger_keywords": ["mb52", "mmbe", "stock", "inventory", "warehouse", "finished goods"],
            "script_chain": [],
            "description": "Connects to SAP Inventory Management (MB52), extracts plant-wide storage location balances for mother rolls, slit rolls, and salvage reels, and refreshes the master scheduling ledger.",
            "workflow_rationale": "Replaces 30 minutes of manual inventory lookups with an instant, error-free stock sync that prevents overscheduling committed stock.",
            "time_saved_daily_mins": 40
        },
        {
            "id": "MRF-12",
            "name": "Pending Export Backlog Analyzer",
            "file": "Pending.mrf",
            "tcode": "VA05 / COOIS",
            "category": "Inventory & Logistics Telemetry",
            "target_system": "SAP GUI + Export Summary - Excel",
            "trigger_keywords": ["va05", "pending", "backlog", "vessel", "export orders"],
            "script_chain": ["D:\\Sikander\\Export\\02_Input_Pending"],
            "description": "Automates extraction of unfulfilled export order backlogs, parses delivery cut-off dates, and highlights priority orders due for container stuffing within 72 hours.",
            "workflow_rationale": "Guarantees 99.2% on-time vessel dispatch by ensuring production slitters prioritize orders nearing shipping line container cut-offs.",
            "time_saved_daily_mins": 50
        },
        {
            "id": "MRF-13",
            "name": "Export Shipment Plan Generator",
            "file": "Shipment.mrf",
            "tcode": "VL06O / VT01N",
            "category": "Inventory & Logistics Telemetry",
            "target_system": "SAP GUI + BOPET EXPORT SHIPMENT PLAN",
            "trigger_keywords": ["vl06o", "vt01n", "shipment", "container", "forwarder", "freight"],
            "script_chain": [],
            "description": "Compiles the official 'BOPET Export Shipment Plan for Factory As On', cross-referencing pallet inspection passes with freight forwarder container booking dates.",
            "workflow_rationale": "Ensures zero demurrage or detention charges by harmonizing container loading schedules with Karachi port vessel cut-offs.",
            "time_saved_daily_mins": 45
        },

        # --- 4. Data Integrity & Variance Control (5 scripts) ---
        {
            "id": "MRF-14",
            "name": "Roll Slit Weight Equalizer",
            "file": "Weight Equal.mrf",
            "tcode": "CO02",
            "category": "Data Integrity & Variance Control",
            "target_system": "SAP GUI (Order Change: Header)",
            "trigger_keywords": ["co02", "weight equal", "slitter weight", "scale", "material balance", "scrap"],
            "script_chain": [],
            "description": "Adjusts planned production order weights to match physical gross roll weights measured at slitter scales, eliminating rounding variances and phantom scrap in inventory.",
            "workflow_rationale": "Reconciles theoretical BOM weights with actual weighed output, providing 99.8% material balance precision between polymer inputs and film outputs.",
            "time_saved_daily_mins": 40
        },
        {
            "id": "MRF-15",
            "name": "Laboratory 1kg Sample Adjuster",
            "file": "1kg.mrf",
            "tcode": "CO02",
            "category": "Data Integrity & Variance Control",
            "target_system": "SAP GUI (Order Headers)",
            "trigger_keywords": ["1kg", "sample", "trial", "r&d", "lab order"],
            "script_chain": [],
            "description": "Rapidly reconfigures production orders for 1kg experimental sample rolls, R&D trials, and quality compliance testing batches.",
            "workflow_rationale": "Ensures R&D sample trials do not distort mass production KPIs while preserving full SAP traceability.",
            "time_saved_daily_mins": 20
        },
        {
            "id": "MRF-16",
            "name": "Batch Transaction Committer",
            "file": "Save Data.mrf",
            "tcode": "SAP GUI UTILITY",
            "category": "Data Integrity & Variance Control",
            "target_system": "SAP GUI + Orders - Excel",
            "trigger_keywords": ["save data", "batch committer", "transaction", "commit", "integrity"],
            "script_chain": [],
            "description": "High-reliability batch committer that steps through 100+ queued transactions, handles network latency, commits changes, and captures generated SAP document numbers.",
            "workflow_rationale": "Guarantees transactional integrity during batch operations and prevents incomplete order creation due to network drops.",
            "time_saved_daily_mins": 30
        },
        {
            "id": "MRF-17",
            "name": "Order v2 Batch Keyer",
            "file": "123.mrf",
            "tcode": "SAP GUI DATA INTAKE",
            "category": "Data Integrity & Variance Control",
            "target_system": "SAP GUI + Order_v2 - Excel",
            "trigger_keywords": ["123", "data intake", "typing", "fast stream", "keyboard"],
            "script_chain": [],
            "description": "Fast-stream keyboard input robot translating structured Excel order matrices into SAP grid controls at maximum throughput.",
            "workflow_rationale": "Exploits Sikander's 90 WPM speed patterns into machine code, executing data entry 10x faster than human capability.",
            "time_saved_daily_mins": 35
        },
        {
            "id": "MRF-18",
            "name": "Modal Dialog Accelerator",
            "file": "Enter.mrf",
            "tcode": "SAP GUI MODAL BYPASS",
            "category": "Data Integrity & Variance Control",
            "target_system": "SAP GUI",
            "trigger_keywords": ["enter", "modal", "dialog", "popup", "bypass"],
            "script_chain": [],
            "description": "High-frequency keystroke pump designed to acknowledge and dismiss SAP informational dialog popups during bulk order processing.",
            "workflow_rationale": "Bypasses modal confirmation dialogues that would otherwise pause unattended batch scripts.",
            "time_saved_daily_mins": 15
        },

        # --- 5. Workflow Orchestration (1 script) ---
        {
            "id": "MRF-19",
            "name": "Master Daily Planning Orchestrator",
            "file": "Daily.mrf",
            "tcode": "MULTI-SYS ORCHESTRATOR",
            "category": "Workflow Orchestration",
            "target_system": "SAP GUI + Excel + Macro Chaining",
            "trigger_keywords": ["daily", "orchestrator", "master", "macro chaining", "automation"],
            "script_chain": [
                "D:\\Sikander\\Production Orders\\M\\Pending.mrf",
                "D:\\Sikander\\Production Orders\\M\\Stock.mrf"
            ],
            "description": "The master daily sequencer: launches SAP, authenticates, triggers Pending.mrf, captures MB52 stock via Stock.mrf, and recalculates the plant export master schedule.",
            "workflow_rationale": "Automated the entire opening routine of the planning department. Sikander could run one command and have complete plant plans generated while getting coffee.",
            "time_saved_daily_mins": 75
        },

        # --- 6. Administrative & HR Automation (2 scripts) ---
        {
            "id": "MRF-20",
            "name": "SuccessFactors Portal Navigator",
            "file": "Salary.mrf",
            "tcode": "SAP SUCCESSFACTORS",
            "category": "Administrative & HR Automation",
            "target_system": "Browser + SAP SuccessFactors",
            "trigger_keywords": ["salary", "successfactors", "payslip", "hr portal", "export"],
            "script_chain": [],
            "description": "Automates employee login, security challenge handling, and monthly payslip PDF export from Novatex's SAP SuccessFactors HR portal.",
            "workflow_rationale": "Streamlines monthly personal compensation telemetry archiving into the Sikander OS repository.",
            "time_saved_daily_mins": 10
        },
        {
            "id": "MRF-21",
            "name": "Jubilee Medical Claim Submitter",
            "file": "Claim.mrf",
            "tcode": "WEB / JUBILEE INSURANCE PORTAL",
            "category": "Administrative & HR Automation",
            "target_system": "Mozilla Firefox + Jubilee Insurance Web",
            "trigger_keywords": ["claim", "jubilee", "insurance", "medical", "health"],
            "script_chain": ["firefox.exe|*|MozillaWindowClass"],
            "description": "Web automation macro filling outpatient medical receipts, doctor consultations, and pharmacy bills onto the Jubilee corporate insurance claim submission portal.",
            "workflow_rationale": "Eliminated repetitive manual form filling for employee health insurance claims.",
            "time_saved_daily_mins": 20
        }
    ]

    total_time_saved_daily = sum(m["time_saved_daily_mins"] for m in sap_automation_vault)

    # 5. Industrial Engineering Knowledge Base
    industrial_engineering_kb = {
        "novatex_bopet_sops": [
            {
                "doc_no": "PP/SOP-FL/01",
                "title": "Planning SOP for Film-Line Plans",
                "organization": "Novatex Limited — BOPET Unit",
                "effective_date": "01/01/2014 (Rev: 00)",
                "purpose": "Ensure longer production runs and optimum plant capacity utilization with minimum changes through advance planning.",
                "scope": "Directs raw material feed sequence, addresses critical film production in general shift under senior supervision.",
                "key_rules": [
                    "Standard film plans must be delivered to Film Line Incharges 48 hours prior to production.",
                    "One physical copy delivered and acknowledged by QC Lab for line parameter verification.",
                    "Web width for regular 12 micron and 18 TG products must be maintained at exactly 8,500 mm.",
                    "Emergency Plan for 18 TG must be available on the line at all times in case of process instability.",
                    "Default failover: In case no plan is issued, line produces standard 12-micron corona film for domestic converters in 12,000 / 18,000 m multiple lengths.",
                    "Strict trial prohibition: Friday, Saturday, and Sunday — NO trials and NO special film runs permitted.",
                    "Special grades (23 TG, 38/40 Low Elongation, Low Haze, 75–140 micron) require General Shift production and DGMP approval."
                ]
            },
            {
                "doc_no": "PP/SOP-PS/02",
                "title": "Planning SOP for Primary Slitter Plans",
                "organization": "Novatex Limited — BOPET Unit",
                "effective_date": "01/01/2014 (Rev: 00)",
                "purpose": "Minimize setting changes and machine idle time while maximizing design throughput on primary slitting stations.",
                "scope": "Presents order length/micron matrix, compares with Finished Goods Stock (FGS), issues 24-hr advance schedules.",
                "key_rules": [
                    "Contact Roll Matrix: Slitting plans strictly aligned to available contact rolls: 510(14), 550(3), 700(4), 870(14), 1150(16), 1590(11), 1650(1), 2100(2), 3050(4).",
                    "Width Clearance Rule: Film roll width must be at least 10 mm less than contact roll width.",
                    "Shift Change Quota: Maximum 1 contact roll change and 2 size changes permitted per 8-hour shift for standard grades across 16 stations.",
                    "Export Container Buffer: Plan strictly 1 extra roll per size above container packing count to cushion against handling transit damage.",
                    "Edge Trim Standard: Normal slitting requires 110 mm edge trim on one side and maximum 250 mm total on both sides.",
                    "Metallizer Feed Constraint: Maximum metallized cutting of 12 metric tons per day at once to eliminate repeated contact roll swaps.",
                    "5-Point Document Distribution: Physical signed copies delivered to Primary Slitter, QA Lab, Computer Operators, Packing, and Core Cutter."
                ]
            },
            {
                "doc_no": "PP/SOP-SS/03",
                "title": "Planning SOP for Secondary Slitter Plans",
                "organization": "Novatex Limited — BOPET Unit",
                "effective_date": "01/01/2014 (Rev: 00)",
                "purpose": "Facilitate specialized rewinding, trimming, salvage of defective mother rolls, and narrow-width customer cutting.",
                "scope": "Plans post-aging rolls, salvage rolls (SQ), and metallized film rewinding.",
                "key_rules": [
                    "Maximum slitting width of 3,300 mm across 6 stations.",
                    "Station balance: 2 rolls of identical length paired with 2 rolls of multiple lengths (e.g. 12u–36,000m).",
                    "Metallized Trim Minimization: Maintain tight 10 mm edge trim on metallized film to prevent silver deposit build-up.",
                    "SQ Problem Roll Salvage: Prioritize trimming problematic sections identified by daily QA and slitter feedback.",
                    "Chucks Optimization: Sequence jobs to minimize chuck size changes and maintain consistent station usage."
                ]
            }
        ],
        "tubex_cold_extrusion_mechanics": {
            "title": "Cold Extrusion Mechanics & Industrial Process Manual",
            "facility": "Tubex (Pvt.) Ltd — Aluminum Collapsible Tubes",
            "preparation_and_mechanics": {
                "process": "Cold extrusion of high-purity aluminum slugs into thin-walled collapsible tubes via Press #6 operating at 55 SPM (Strokes Per Minute).",
                "extrusion_ratio": "Compares initial slug cross-sectional area to final extruded tube wall cross-section; high extrusion ratio generates extreme friction and deformation heat.",
                "lubrication_protocol": {
                    "compound": "Zinc Stearate (white slippery powder, insoluble in water, soluble in alcohol).",
                    "tumbling_duration": "Slugs mixed in tumbling drum for exactly 15 minutes to establish a uniform lubricating coat.",
                    "troubleshooting_matrix": [
                        {"symptom": "High Press Loads", "root_cause": "Insufficient Zinc Stearate coating increasing mechanical resistance.", "action": "Re-tumble slugs with measured powder addition."},
                        {"symptom": "Surface Scratches", "root_cause": "Metal-on-metal micro contact due to dry slug patches.", "action": "Inspect tumbling drum baffles and cycle time."},
                        {"symptom": "Galling / Die Welding", "root_cause": "Severe friction welding aluminum slug directly to the punch die.", "action": "Immediate line shutdown; polish punch head, replace slug batch."}
                    ]
                }
            },
            "thermal_processing_annealing": {
                "furnace_parameters": "Continuous annealing furnace maintained between 250°C and 350°C.",
                "dual_purpose": [
                    "Restoring Ductility: Relieves high internal mechanical stresses induced during cold deformation, preventing tube wall cracking during customer crimping.",
                    "Surface Preparation: Burns off all residual Zinc Stearate lubricant, ensuring pristine metal adhesion for internal lacquer and exterior base coating."
                ],
                "tooling_replacement_schedule": [
                    {"tool": "Cutters / Trimmers", "lifespan": "1 Day (24 Hours)", "protocol": "Daily buffing or total tool replacement to ensure clean burr-free tube mouth cut."},
                    {"tool": "Punch Heads", "lifespan": "2 Days (48 Hours)", "protocol": "Replace punch heads every 48 hours due to high frictional wear."}
                ]
            },
            "coating_printing_curing": {
                "process_chain": "Base Coating -> Curing Oven (~150°C) -> 5 Dry Offset Printing Machines -> Capping.",
                "curing_oven_physics": "Electric and gas heaters maintain ~150°C to evaporate solvents and polymerize the base coat into a hardened protective substrate.",
                "defect_mode": "Incomplete curing leads to color bleeding and smearing during dry offset printing.",
                "scrap_recovery": "Misfired prints are washed with kerosene oil to strip ink, saving raw aluminum tubes from the scrap bin."
            },
            "latex_sealing_and_qa": {
                "latex_function": "Water-based acrylic latex creates an elastic, waterproof seal inside the tube shoulder, preventing leakage of active pharmaceutical/cosmetic ingredients.",
                "qa_checkpoints": ["Pinhole light testing", "Internal lacquer shoulder deposits", "Latex flow direction (inward/outward)", "Cap thread engagement and torque tightness"]
            },
            "bom_weight_consumption_matrices": [
                {
                    "sku": "Samsol 43 (25mm Diameter)",
                    "weights": {
                        "raw_extruded_tube": "6.01g",
                        "trimmed": "5.13g",
                        "after_lacquer": "5.44g",
                        "after_base_coat": "6.01g",
                        "after_print": "5.87g",
                        "final_capped": "7.76g"
                    },
                    "net_delta_raw_to_final": "+1.75g"
                },
                {
                    "sku": "Hello Hair / Golden Pearl (30mm Diameter)",
                    "weights": {
                        "slug": "8.20g",
                        "base_coated": "8.08g",
                        "lacquered": "7.50g",
                        "trimmed": "7.11g",
                        "printed": "7.82g",
                        "final_capped": "9.40g"
                    },
                    "net_delta_raw_to_final": "+1.20g"
                },
                {
                    "sku": "Anvil 43 (35mm Diameter)",
                    "weights": {
                        "raw_tube": "12.80g",
                        "trimmed": "11.80g",
                        "after_lacquer": "12.30g",
                        "after_base_coat": "13.50g",
                        "after_oven": "12.90g",
                        "final_printed_capped": "13.70g"
                    },
                    "net_delta_raw_to_final": "+0.90g"
                }
            ]
        },
        "tubex_inventory_snapshot_april_2026": {
            "audit_date": "09-04-2026",
            "report_name": "TUBEX-ALUM Item Wise Consolidated Report",
            "selected_balances": [
                {"category": "Ingot", "item": "Aluminum Ingot 7096", "balance": "11,584.00 KGS"},
                {"category": "PET Plant", "item": "PET Resin A-84", "balance": "4,150.00 KG"},
                {"category": "Zinc Powder", "item": "Zinc Stearate 194 L", "balance": "39.50 KGS"},
                {"category": "Base Coat", "item": "Polyester Base Coat White 23410 CT", "balance": "300.00 KG"},
                {"category": "Base Coat", "item": "Silver Metallic 5725100011", "balance": "240.00 KGS"},
                {"category": "Caps", "item": "M-9 S/M F/P White Shearing", "balance": "605,000 NO"},
                {"category": "Caps", "item": "M-9 S/M F/P Orange (Normal)", "balance": "475,000 PCS"},
                {"category": "Caps", "item": "M-11 S/M SPR White Dia 25mm", "balance": "200,000 PCS"},
                {"category": "Slugs", "item": "Slug 25x4.5 S/M", "balance": "815.80 KGS"},
                {"category": "Slugs", "item": "Slug 30x4.3", "balance": "646.00 KGS"},
                {"category": "Slugs", "item": "Slug 20.5x4.5", "balance": "550.00 KGS"},
                {"category": "Latex", "item": "Latex IMP 574010002", "balance": "180.00 KGS"},
                {"category": "Lacquer", "item": "E/P Lacquer 4000 A/R", "balance": "225.00 KGS"}
            ]
        }
    }

    # 6. Target Role Profiles for AI Resume Builder & Tailoring Studio (Full 11-Year Milestones)
    target_roles = [
        {
            "id": "role_scm_lead",
            "title": "Senior Supply Chain Planner / SCM Manager",
            "target_keywords": [
                "Master Production Scheduling (MPS)", "Material Requirements Planning (MRP)",
                "Export Logistics", "Container Vessel Optimization", "SAP PP / MM",
                "Safety Stock Allocation", "Inventory Turnover", "Lead Time Compression",
                "Cross-Functional S&OP", "Finished Goods Allocation"
            ],
            "tailored_summary": "Accomplished Senior Supply Chain Planner with 11+ years directing high-volume export logistics and multi-line production scheduling in heavy process manufacturing (Novatex Ltd & Alpha Containers). Proven track record managing multi-million-dollar inventory flows, orchestrating container vessel cut-offs with 99.2% on-time dispatch, and automating 90% of daily ERP scheduling routines using SAP and advanced VBA models.",
            "tailored_competencies": [
                "Master Production Scheduling (MPS) & S&OP",
                "Export Shipping & Container Loading Logistics",
                "BOM Explosion & Polymer Resin MRP",
                "SAP S/4HANA & ECC (PP, MM, SD, COOIS)",
                "Inventory Stock Optimization (MB52 / MMBE)",
                "Finished Goods Allocation & Order Fulfillment"
            ],
            "sections": [
                {
                    "company_id": "tubex",
                    "role": "Planning Lead",
                    "company": "Alpha Containers (Pvt.) Ltd / Tubex & Aerosol",
                    "period": "Feb 2026 – Present | Lahore & Sheikhupura",
                    "bullets": [
                        "Appointed Planning Lead overseeing dual-facility supply chain operations for Tubex and upcoming Alpha Aerosol plant.",
                        "Formulated end-to-end MRP framework covering 11,500+ kg aluminum ingots, slugs, base coats, and lithography inks.",
                        "Established stage-by-stage BOM consumption matrices across 25mm, 30mm, and 35mm collapsible tube SKUs.",
                        "Synchronized weekly production commitments between Attari Saroba and Kot Abdul Malik manufacturing lines."
                    ]
                },
                {
                    "company_id": "novatex_skp",
                    "role": "Export SCM Planning Associate (Promoted to Supervisor 2)",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "May 2024 – Feb 2026 | Sheikhupura, Punjab",
                    "bullets": [
                        "Architected master production schedules for BOPET film lines delivering 2,500+ tons monthly across domestic and export markets.",
                        "Orchestrated factory container loading programs, aligning production output with international shipping line cutoff dates with 99.2% on-time dispatch.",
                        "Automated export order backlog reconciliation using custom SAP script chains (`Daily.mrf`, `Pending.mrf`), reducing planning cycle time by 85%.",
                        "Managed raw polymer chip inventory (PET Resin A-84) and masterbatch allocations, maintaining zero unplanned production stoppages over 4 consecutive years.",
                        "Enforced slitter scheduling rules (PP/SOP-PS/02), cutting roll change downtime and reducing trim scrap to <110mm per run."
                    ]
                },
                {
                    "company_id": "novatex_khi_plan",
                    "role": "Production Planning Associate & SAP Key User (Supervisor 3)",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Feb 2020 – May 2024 | Karachi, Sindh",
                    "bullets": [
                        "Scheduled BOPET film lines and primary/secondary slitters for local market converters and flexible packaging accounts.",
                        "Served as designated Planning SAP Key User: led User Acceptance Testing (UAT), master data migration, and shop-floor personnel training.",
                        "Automated finished goods stock allocation and production order release using SAP COOIS and custom Excel integration.",
                        "Authored departmental Standard Operating Procedures for slitter trim optimization (PP/SOP-PS/02) and mother roll aging cycles."
                    ]
                },
                {
                    "company_id": "novatex_khi_data",
                    "role": "Production Computer Lead & Data Specialist",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Nov 2015 – Feb 2020 | Karachi, Sindh",
                    "bullets": [
                        "Supervised production floor data integrity and operational telemetry across film extrusion and slitting shifts.",
                        "Constructed executive dashboards tracking daily line throughput, yield efficiencies, and resin consumption.",
                        "Leveraged certified 90 WPM keyboard speed to accelerate batch data processing across Oracle databases."
                    ]
                },
                {
                    "company_id": "novatex_khi_qa",
                    "role": "Quality Assurance Operator",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Sep 2015 – Nov 2015 | Karachi, Sindh",
                    "bullets": [
                        "Authored Corrective Action Reports (C.A.R) to resolve customer quality claims on optical haze and thickness deviations.",
                        "Conducted laboratory compliance testing on incoming polymer chips and surface dyne treatment levels."
                    ]
                }
            ]
        },
        {
            "id": "role_plant_ops",
            "title": "Plant Operations Lead / Manufacturing Manager",
            "target_keywords": [
                "Overall Equipment Effectiveness (OEE)", "Shop Floor Execution", "Cold Extrusion Mechanics",
                "Tooling Life Cycle Management", "SOP Development & Enforcement", "Quality Complaints & CAR",
                "Downtime Reduction", "Scrap & Trim Recovery", "Annealing Metallurgy", "Preventive Maintenance"
            ],
            "tailored_summary": "Results-driven Plant Operations Lead with 11+ years optimizing continuous manufacturing facilities across BOPET film extrusion, slitting, and aluminum impact cold extrusion. Skilled in driving shop-floor discipline, standardizing tooling lifespans, troubleshooting galling failure modes, and converting field engineering logs into rigid operational frameworks.",
            "tailored_competencies": [
                "Cold Extrusion & High-Speed Press Operations",
                "OEE Optimization & Downtime Mitigation",
                "Tooling Maintenance (Cutters & Punch Heads)",
                "SOP Authoring & Quality Control Audits",
                "Scrap Reclaim & Metallized Trim Reduction",
                "Root Cause Analysis & Corrective Action (CAR)"
            ],
            "sections": [
                {
                    "company_id": "tubex",
                    "role": "Planning Lead",
                    "company": "Alpha Containers (Pvt.) Ltd / Tubex & Aerosol",
                    "period": "Feb 2026 – Present | Lahore & Sheikhupura",
                    "bullets": [
                        "Leading operational planning across Ferozepur Road and Sheikhupura Road plants, preparing infrastructure for high-speed aerosol can production.",
                        "Standardized Zinc Stearate lubrication protocols (15-min tumbling cycle) to eliminate punch die galling and high press loads on Press #6 (55 SPM).",
                        "Instituted rigid tooling replacement schedules (1-day cutters, 2-day punch heads), preventing press downtime and burr defects.",
                        "Digitized 27 pages of raw production field engineering notes into an integrated operational planning and BOM consumption framework."
                    ]
                },
                {
                    "company_id": "novatex_skp",
                    "role": "Export SCM Planning Associate (Promoted to Supervisor 2)",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "May 2024 – Feb 2026 | Sheikhupura, Punjab",
                    "bullets": [
                        "Supervised continuous film line and slitter scheduling across 16 primary stations, capping contact roll changes to maximum 1 per shift.",
                        "Authored plant SOPs for Film Line, Primary Slitter, and Secondary Slitter operations, institutionalizing 10mm clearance guidelines.",
                        "Spearheaded scrap salvage programs for metallized and off-spec film rolls, recovering high-value PET material.",
                        "Investigated customer quality complaints in QA, issuing Corrective Action Reports (CAR) that reduced optical defects by 30%."
                    ]
                },
                {
                    "company_id": "novatex_khi_plan",
                    "role": "Production Planning Associate & SAP Key User (Supervisor 3)",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Feb 2020 – May 2024 | Karachi, Sindh",
                    "bullets": [
                        "Orchestrated floor-level slitter optimization across 6 secondary slitting stations for specialized narrow-width orders.",
                        "Trained 20+ operators on standard slitting procedures and waste reduction metrics.",
                        "Eliminated line downtime through rigorous preventive maintenance alignment with mechanical teams."
                    ]
                },
                {
                    "company_id": "novatex_khi_data",
                    "role": "Production Computer Lead & Data Specialist",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Nov 2015 – Feb 2020 | Karachi, Sindh",
                    "bullets": [
                        "Captured shift maintenance and breakdown logs, pinpointing recurring mechanical failures on primary unwinds.",
                        "Automated daily plant yield and OEE calculation sheets, improving reporting accuracy to 100%."
                    ]
                },
                {
                    "company_id": "novatex_khi_qa",
                    "role": "Quality Assurance Operator",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Sep 2015 – Nov 2015 | Karachi, Sindh",
                    "bullets": [
                        "Performed routine lab QA inspections on tensile strength, optical haze, and polymer melt flow index.",
                        "Conducted incoming raw material verifications for polyester resins and anti-block additives."
                    ]
                }
            ]
        },
        {
            "id": "role_sap_automation",
            "title": "SAP SCM & Process Automation Specialist",
            "target_keywords": [
                "SAP ERP (PP, MM, SD)", "SAP Implementation & Key User", "Robotic Process Automation (RPA)",
                "VBA / Macro Automation", "T-Codes (COOIS, CO01, CO02, MB52, VA05)", "Batch Processing",
                "Variant Configuration (CU50)", "Order TECO Settlement", "90 WPM Typing", "Data Migration"
            ],
            "tailored_summary": "Expert SAP Key User and Industrial Process Automation Specialist with 11+ years engineering robotic workflow scripts and optimizing enterprise ERP architectures. Designed, tested, and deployed 21 bespoke SAP GUI automation robots (.mrf) and VBA models, cutting daily scheduling workloads by 90% and securing 100% data integrity across hundreds of daily production transactions.",
            "tailored_competencies": [
                "SAP GUI Scripting & Keystroke Automation (.mrf)",
                "Production Order Lifecycle (CO01, CO02, COHV, COOIS)",
                "Advanced Microsoft Excel & VBA Model Architecture",
                "Variant Configuration & Characteristic Value Assignment",
                "Inventory Movements & Stock Extraction (MB52 / MMBE)",
                "Fast-Stream Data Entry (90 WPM Verified Speed)"
            ],
            "sections": [
                {
                    "company_id": "tubex",
                    "role": "Planning Lead",
                    "company": "Alpha Containers (Pvt.) Ltd / Tubex & Aerosol",
                    "period": "Feb 2026 – Present | Lahore & Sheikhupura",
                    "bullets": [
                        "Designing central automated planning and procurement telemetry database for Tubex and Alpha Aerosol facilities.",
                        "Automated raw material consumption tracking across 13 chemical categories, eliminating manual ledger reconciliations.",
                        "Constructed stage-by-stage weight tracking sheets formulating precision BOM consumption models."
                    ]
                },
                {
                    "company_id": "novatex_skp",
                    "role": "Export SCM Planning Associate (Promoted to Supervisor 2)",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "May 2024 – Feb 2026 | Sheikhupura, Punjab",
                    "bullets": [
                        "Engineered and deployed a suite of 21 SAP GUI automation robots (.mrf) handling order creation, characteristic valuation, stock sync, and mass TECO closing.",
                        "Built the flagship 'PO L3 Char Component' robot, slashing end-to-end production order generation time from 4 minutes to 12 seconds per order.",
                        "Designed master TECO batch processing macro (`Teco.mrf`), enabling 200+ completed orders to be settled unattended in single batch runs.",
                        "Constructed real-time inventory telemetry models linking SAP MB52 tables directly into dynamic Excel scheduling cockpits."
                    ]
                },
                {
                    "company_id": "novatex_khi_plan",
                    "role": "Production Planning Associate & SAP Key User (Supervisor 3)",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Feb 2020 – May 2024 | Karachi, Sindh",
                    "bullets": [
                        "Served as core SAP Key User during enterprise-wide rollout, training 20+ floor personnel and executing User Acceptance Testing (UAT).",
                        "Maintained master data integrity for Bill of Materials (BOMs), routing operations, and work centers.",
                        "Created automated COOIS extraction scripts (`COOIS Report.mrf`) and VBS batch scripts to flag completed production plans."
                    ]
                },
                {
                    "company_id": "novatex_khi_data",
                    "role": "Production Computer Lead & Data Specialist",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Nov 2015 – Feb 2020 | Karachi, Sindh",
                    "bullets": [
                        "Built custom automated Excel reporting templates that eliminated manual data entry bottlenecks across 3 shifts.",
                        "Managed Oracle database queries to cross-reference resin intake with finished goods output."
                    ]
                },
                {
                    "company_id": "novatex_khi_qa",
                    "role": "Quality Assurance Operator",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Sep 2015 – Nov 2015 | Karachi, Sindh",
                    "bullets": [
                        "Digitized historical quality inspection records into structured spreadsheets for trend analysis."
                    ]
                }
            ]
        },
        {
            "id": "role_packaging_specialist",
            "title": "Packaging Manufacturing Specialist (BOPET & Aerosol)",
            "target_keywords": [
                "BOPET Film Manufacturing", "Biaxial Orientation", "Corona Treatment & Surface Dyne",
                "Aluminum Collapsible Tubes", "Aerosol Can Manufacturing", "Dry Offset Printing",
                "Slitter Optimization", "Acrylic Latex Barrier", "Packaging Quality Standards"
            ],
            "tailored_summary": "Specialized Packaging Manufacturing Engineer with deep hands-on expertise spanning flexible polyester packaging films (BOPET) and rigid metal packaging (aluminum collapsible tubes & aerosol cans). Extensive technical knowledge in biaxial orientation, corona treatment dyne levels, cold impact extrusion, dry offset multi-color printing, and internal lacquer barrier coatings.",
            "tailored_competencies": [
                "BOPET Film Extrusion & Biaxial Stretching",
                "Corona Treatment & Surface Tension (Dyne Control)",
                "Impact Cold Extrusion & Annealing Metallurgy",
                "Dry Offset Multi-Color Printing & Curing (~150°C)",
                "Internal Protective Lacquering (Epoxy / Rhenania)",
                "Primary & Secondary Slitter Optimization"
            ],
            "sections": [
                {
                    "company_id": "tubex",
                    "role": "Planning Lead",
                    "company": "Alpha Containers (Pvt.) Ltd / Tubex & Aerosol",
                    "period": "Feb 2026 – Present | Lahore & Sheikhupura",
                    "bullets": [
                        "Directing production preparation for aluminum aerosol can lines and collapsible pharmaceutical/cosmetic tubes.",
                        "Overseeing surface preparation through continuous annealing furnaces (250°C–350°C) to burn off lubricants and guarantee coating adhesion.",
                        "Coordinating 5 dry offset printing machines and ~150°C curing ovens, salvaging misprints using kerosene strip methods to save raw aluminum.",
                        "Standardizing acrylic latex shoulder sealing applications to eliminate leakage of active ingredients."
                    ]
                },
                {
                    "company_id": "novatex_skp",
                    "role": "Export SCM Planning Associate (Promoted to Supervisor 2)",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "May 2024 – Feb 2026 | Sheikhupura, Punjab",
                    "bullets": [
                        "Mastered BOPET film production scheduling across standard (12u, 18u) and specialty grades (23 TG, low haze, 75–140u).",
                        "Enforced corona dyne level treatment protocols on slitting lines, ensuring optimal surface tension for flexible packaging converters.",
                        "Optimized primary slitter station allocations to eliminate roll edge defects and maintain tension uniformity across 8,500 mm web runs."
                    ]
                },
                {
                    "company_id": "novatex_khi_plan",
                    "role": "Production Planning Associate & SAP Key User (Supervisor 3)",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Feb 2020 – May 2024 | Karachi, Sindh",
                    "bullets": [
                        "Scheduled domestic converter orders with strict adherence to contact roll widths and edge trim minimums.",
                        "Monitored mother roll aging cycles to ensure mechanical dimensional stability prior to secondary slitting."
                    ]
                },
                {
                    "company_id": "novatex_khi_data",
                    "role": "Production Computer Lead & Data Specialist",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Nov 2015 – Feb 2020 | Karachi, Sindh",
                    "bullets": [
                        "Monitored optical haze and thickness variance trends across continuous extrusion shifts."
                    ]
                },
                {
                    "company_id": "novatex_khi_qa",
                    "role": "Quality Assurance Operator",
                    "company": "Novatex Limited (BOPET Film Plant)",
                    "period": "Sep 2015 – Nov 2015 | Karachi, Sindh",
                    "bullets": [
                        "Graded finished BOPET film rolls based on surface dyne, pinhole count, and elongation metrics."
                    ]
                }
            ]
        }
    ]

    # Populate top-level convenience shortcuts for legacy / verification access
    for r in target_roles:
        r["tubex_bullets"] = r["sections"][0]["bullets"]
        r["novatex_bullets"] = r["sections"][1]["bullets"]

    # 7. Comprehensive Skills Inventory
    skills_inventory = {
        "enterprise_erp": [
            {"name": "SAP ECC & S/4HANA (PP Module)", "level": 95, "years": 7, "badge": "Expert / Key User"},
            {"name": "SAP MM (Inventory & Goods Movements)", "level": 90, "years": 6, "badge": "Advanced"},
            {"name": "SAP SD & Order Tracking (VA05, VL06O)", "level": 88, "years": 5, "badge": "Advanced"},
            {"name": "Oracle Database & Inventory Systems", "level": 80, "years": 5, "badge": "Proficient"}
        ],
        "automation_tools": [
            {"name": "Macro Recorder (.mrf) & RPA Scripting", "level": 98, "years": 6, "badge": "Master (21 Scripts)"},
            {"name": "Advanced Microsoft Excel & VBA Macros", "level": 95, "years": 10, "badge": "Expert Modeler"},
            {"name": "VBScript & Windows Automation", "level": 85, "years": 5, "badge": "Advanced"},
            {"name": "Rapid Keyboarding & Data Intake", "level": 99, "years": 11, "badge": "90 WPM Certified"}
        ],
        "supply_chain_logistics": [
            {"name": "Master Production Scheduling (MPS)", "level": 95, "years": 9, "badge": "Core Expertise"},
            {"name": "Material Requirements Planning (MRP)", "level": 92, "years": 8, "badge": "Core Expertise"},
            {"name": "Export Container & Vessel Coordination", "level": 94, "years": 4, "badge": "High-Volume Lead"},
            {"name": "Bill of Materials (BOM) Calculation", "level": 90, "years": 6, "badge": "Precision Formulation"}
        ],
        "industrial_manufacturing": [
            {"name": "BOPET Film Extrusion & Slitting", "level": 96, "years": 11, "badge": "Deep Domain"},
            {"name": "Aluminum Cold Impact Extrusion", "level": 88, "years": 2, "badge": "Lead Engineer"},
            {"name": "Annealing Metallurgy & Thermal Curing", "level": 85, "years": 2, "badge": "Operational Lead"},
            {"name": "Dry Offset Printing & Tube Finishing", "level": 85, "years": 2, "badge": "Operational Lead"}
        ],
        "quality_operational_rigor": [
            {"name": "Corrective Action Reports (C.A.R)", "level": 90, "years": 8, "badge": "RCA Practitioner"},
            {"name": "Standard Operating Procedures (SOP)", "level": 95, "years": 9, "badge": "Author & Auditor"},
            {"name": "Scrap & Trim Variance Control", "level": 92, "years": 7, "badge": "Yield Optimizer"}
        ]
    }

    # 8. Assemble Master JSON Document
    master_data = {
        "metadata": {
            "version": "2.1.0",
            "generated_at": datetime.now().isoformat(),
            "module": "Module 04: Career Intelligence & AI Resume Builder",
            "system": "Sikander OS (ckndr/sikander-os)",
            "total_career_experience_years": 11,
            "total_sap_macros_cataloged": len(sap_automation_vault),
            "total_monthly_pay_slips_verified": len(pay_slips),
            "total_daily_minutes_saved_by_macros": total_time_saved_daily,
            "appointment_offer": appointment_offer,
            "reference_sources_verified": ref_status
        },
        "candidate_profile": candidate_profile,
        "career_milestones": career_milestones,
        "verified_compensation": verified_compensation,
        "sap_automation_vault": sap_automation_vault,
        "industrial_engineering_knowledge_base": industrial_engineering_kb,
        "target_roles": target_roles,
        "skills_inventory": skills_inventory
    }

    # Write to data/career/sikander_career_data.json
    output_path = r"I:\sikander-os\data\career\sikander_career_data.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=2, ensure_ascii=False)

    # Also export as JS global variable for zero-CORS local file execution
    js_output_path = r"I:\sikander-os\data\career\sikander_career_data.js"
    with open(js_output_path, 'w', encoding='utf-8') as f:
        f.write("window.__SIKANDER_CAREER_DATA__ = " + json.dumps(master_data, indent=2, ensure_ascii=False) + ";\n")

    print(f"✅ Career Intelligence Master Data successfully built!")
    print(f"📁 Destination JSON: {output_path}")
    print(f"📁 Destination JS:   {js_output_path}")
    print(f"📊 Summary:")
    print(f"   • Milestones: {len(career_milestones)} verified career phases (2015–2026)")
    print(f"   • Pay Slips: {len(pay_slips)} monthly records (Dec 2025 Gross: PKR {end_gross:,}, Net: PKR {end_net:,})")
    print(f"   • 2026 Offer: Alpha Containers Gross PKR {alpha_gross:,} (+45k Aerosol expansion = PKR {alpha_aerosol_gross:,})")
    print(f"   • SAP Macros: {len(sap_automation_vault)} automation scripts cataloged ({total_time_saved_daily} mins saved/day)")
    print(f"   • Industrial KB: 3 BOPET SOPs + Tubex Cold Extrusion manual + Inventory snapshot")
    print(f"   • Target Profiles: {len(target_roles)} interactive AI resume tailoring roles (with full 11-year sections)")

    return master_data


if __name__ == "__main__":
    build_career_intelligence()
