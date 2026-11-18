#!/usr/bin/env python3
"""Find 2025-2026 papers that cite our reading list (_paper/), using the free OpenAlex API.

Step 1: find each seed paper in OpenAlex (title search).  Step 2: list every work that cites it, published 2025-2026.
Writes _paper/citing_2025_2026/all_citing.json (raw: title, year, venue, DOI, open-access PDF, abstract, which seeds it cites).
Usage: python3 _SCRIPT/2026-11-19_script/find_citing_papers.py
"""
import json, os, subprocess, time, urllib.parse

SEEDS = {
    "Coulter1992": "Implementation of the Pure Pursuit Path Tracking Algorithm",
    "Snider2009": "Automatic Steering Methods for Autonomous Automobile Path Tracking",
    "Hoffmann2007": "Autonomous Automobile Trajectory Tracking for Off-Road Driving: Controller Design, Experimental Validation and Racing",
    "LippBoyd2014": "Minimum-time speed optimisation over a fixed path",
    "Kong2015": "Kinematic and dynamic vehicle models for autonomous driving control design",
    "Kapania2015": "Design of a feedback-feedforward steering controller for accurate path tracking and stability at the limits of handling",
    "Paden2016": "A Survey of Motion Planning and Control Techniques for Self-driving Urban Vehicles",
    "Kabzan2020": "AMZ Driverless: The Full Autonomous Racing System",
    "OKelly2020": "F1TENTH: An Open-source Evaluation Environment for Continuous Control and Reinforcement Learning",
    "Betz2022": "Autonomous Vehicles on the Edge: A Survey on Autonomous Vehicle Racing",
    "Becker2023": "Model- and Acceleration-based Pursuit Controller for High-Performance Autonomous Racing",
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_paper", "citing_2025_2026")
API = "https://api.openalex.org/works"


def get(url):
    for _ in range(5):
        r = subprocess.run(["curl", "-s", "-m", "60", url], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            if "results" in d or "id" in d:
                return d
        except json.JSONDecodeError:
            pass
        time.sleep(3)
    raise RuntimeError(f"OpenAlex failed: {url}\n{r.stdout[:300]}")


def abstract(inv):
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


seeds, works = {}, {}
for key, title in SEEDS.items():
    d = get(f"{API}?search={urllib.parse.quote(title)}&per-page=5&select=id,display_name,publication_year,cited_by_count")
    norm = lambda s: "".join(c for c in s.lower() if c.isalnum())
    hit = next((r for r in d["results"] if norm(r["display_name"])[:40] == norm(title)[:40]), None)
    if hit is None:
        print(f"{key}: NOT FOUND in OpenAlex"); continue
    wid = hit["id"].split("/")[-1]
    seeds[key] = {"openalex": wid, "title": hit["display_name"], "year": hit["publication_year"], "cited_by": hit["cited_by_count"]}
    page_no, n = 1, 0
    while True:
        sel = "id,display_name,publication_year,doi,primary_location,open_access,best_oa_location,abstract_inverted_index,cited_by_count"
        page = get(f"{API}?filter=cites:{wid},publication_year:2025-2026&per-page=200&page={page_no}&select={sel}")
        for w in page["results"]:
            e = works.setdefault(w["id"].split("/")[-1], {
                "title": w["display_name"], "year": w["publication_year"], "doi": w.get("doi"),
                "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
                "oa_pdf": (w.get("best_oa_location") or {}).get("pdf_url"),
                "is_oa": (w.get("open_access") or {}).get("is_oa"),
                "cited_by": w.get("cited_by_count", 0),
                "abstract": abstract(w.get("abstract_inverted_index")), "cites": []})
            e["cites"].append(key)
            n += 1
        if len(page["results"]) < 200 or page_no * 200 >= 10000:
            break
        page_no += 1
    seeds[key]["citing_2025_2026"] = n
    print(f"{key:13s} {wid:12s} cited_by {hit['cited_by_count']:5d} | 2025-2026 citing: {n}")

os.makedirs(OUT, exist_ok=True)
json.dump({"seeds": seeds, "works": works}, open(os.path.join(OUT, "all_citing.json"), "w"), indent=1)
print(f"{len(works)} unique 2025-2026 citing works -> {OUT}/all_citing.json")
