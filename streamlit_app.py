from pathlib import Path
import json

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "evidence.json").read_text(encoding="utf-8"))
R = DATA["report"]
FIN = R["q11"]
BLUE = "#215D76"
GOLD = "#D4963B"

st.set_page_config(page_title="OWND! | FY28 rollout decision", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1250px; padding-top: 2.6rem;}
.decision {background: #14283B; color: #fff; border-radius: 18px;
padding: 26px 34px; margin-bottom: 20px; border-left: 5px solid #D4963B;}
.decision strong {font-size: clamp(1.55rem, 4vw, 2.5rem); display: block; margin: 5px 0;}
.decision small {color: #F5D195; font-weight: 700; letter-spacing: .09em;}
.decision p {margin: 8px 0 0; color: #E8EFF6;}
div[data-testid="stMetric"] {background: #EDF3F7; color: #14283B; padding: 12px 16px;
border-radius: 12px; min-height: 100px;}
div[data-testid="stMetricValue"] {color: #14283B;}
div[data-testid="stMetricLabel"] {color: #14283B;}
</style>
""", unsafe_allow_html=True)

def table(name):
    return pd.DataFrame(DATA[name])

def bar(frame, category, measure, *, percent=False, signed=False):
    axis = alt.Axis(format=".0%" if percent else "~g")
    values = alt.X(f"{measure}:Q", axis=axis)
    colors = (alt.condition(alt.datum[measure] < 0, alt.value(GOLD), alt.value(BLUE))
              if signed else alt.value(BLUE))
    return (alt.Chart(frame).mark_bar(cornerRadiusEnd=4).encode(
        x=values,
        y=alt.Y(f"{category}:N", sort=None, title=None),
        color=colors,
        tooltip=[alt.Tooltip(f"{category}:N"),
                 alt.Tooltip(f"{measure}:Q", format=".1%" if percent else ",.1f")],
    ).properties(height=max(170, min(400, 37 * len(frame)))))

def show_chart(chart):
    st.altair_chart(chart, width="stretch")

def show_table(frame, *, formats=None):
    st.dataframe(frame, hide_index=True, width="stretch", column_config={
        name: st.column_config.NumberColumn(format=fmt)
        for name, fmt in (formats or {}).items()
    })

def margin_chart():
    trend = table("margin").tail(4)
    trend = trend[["Quarter", "Margin YoY stated (pp)"]].rename(
        columns={"Margin YoY stated (pp)": "YoY margin change (pp)"})
    show_chart(bar(trend, "Quarter", "YoY margin change (pp)", signed=True))
    st.caption("Reported segment margins, Q2 FY26–Q1 FY27. H2 FY26 pooled change "
               f"was {R['q10']['h2_yoy_pp']:+.1f} pp after combining the festive quarters.")

def executive():
    st.markdown("""
    <div class="decision"><small>FY28 CAPITAL DECISION</small>
    <strong>Hold the rollout behind two gates.</strong>
    <p>Approve a conditional first tranche of up to 20 stores. Split it between
    10 metro in-fill openings and 10 Tier 2 test openings. Release about 40 more
    only if the November 2027 review passes.</p></div>
    """, unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("Best-sellers at ₹500 or less", f"{table('price').iloc[2]['share_le_500']:.0%}",
             help="OWND! online best-seller collection. Zudio's historical published benchmark was 50%.")
    b.metric("Inside Pantaloons’ price band", f"{R['q7']['inside_share_of_covered']:.0%}",
             help="Share of OWND! products with a comparable Pantaloons best-seller band.")
    c.metric("Segment EBITDA margin change", f"{R['q10']['yoy_pp_stated']['Q1 FY27']:+.1f} pp",
             help="Q1 FY27 versus Q1 FY26.")
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Margin pressure persisted")
        margin_chart()
    with right:
        st.subheader("What management needs to decide")
        st.markdown("""
        **March 2027 · Gate 1**  
        Sign off on an OWND! store P&L and shared-cost allocation before releasing tranche 1.

        **November 2027 · Gate 2**  
        Use Q2 FY28 results to assess mature-store EBITDA, the segment margin gap,
        and Pantaloons’ catchment LTL gap. If the tests fail, slow openings and reposition.
        """)
        st.metric("Four-quarter EBITDA shortfall vs prior-year margins",
                  f"₹{R['q10']['shortfall_4q']:.1f} cr",
                  help="Segment counterfactual. Includes effects such as Pantaloons marketing spend.")

def commercial():
    st.header("Price positioning and overlap")
    a, b = st.columns(2)
    with a:
        cohort = st.selectbox("OWND! catalogue cohort",
                              ["OWND! bestsellers", "OWND! all items", "OWND! apparel bestsellers",
                               "OWND! apparel only"])
        p = table("price")
        p = p[p["Set"].isin([cohort, "Zudio (published)", "Pantaloons own label"])]
        threshold = st.radio("MRP threshold", ["₹500 or less", "₹999 or less"], horizontal=True)
        column = "share_le_500" if threshold == "₹500 or less" else "share_le_999"
        show_chart(bar(p[["Set", column]].rename(columns={column: "Share of products"}),
                       "Set", "Share of products", percent=True))
        st.caption("OWND! and Pantaloons use October 2026 online MRP. Zudio uses published "
                   "2020–24 summaries with a different price basis and no item-level catalogue.")
    with b:
        overlap = table("overlap")
        gender = st.selectbox("Product group", ["All", "Men", "Women", "Boys", "Girls"])
        if gender != "All":
            overlap = overlap[overlap["Key"].str.startswith(gender + " | ")]
        category = st.selectbox("Comparable category", overlap["Key"].tolist())
        row = overlap.set_index("Key").loc[category]
        st.metric("OWND! products inside the band", f"{row['share_inside']:.1%}")
        st.write(f"Pantaloons band ₹{row['Pant_top10_Q1']:,.0f}–₹{row['Pant_top10_Q3']:,.0f}"
                 f" · OWND! median ₹{row['OWND_median']:,.0f}"
                 f" · {row['OWND_items']:,.0f} OWND! products")
        st.caption("Band = middle 50% of MRPs among comparable Pantaloons own-label best-sellers "
                   "from the top 10% by orders, with at least 10 styles per group.")
    st.subheader("Price guardrails by category")
    display = overlap[["Key", "OWND_items", "OWND_median", "Pant_top10_Q1", "Pant_top10_Q3",
                       "share_inside", "share_below"]].rename(columns={
        "Key": "Group", "OWND_items": "OWND! items", "OWND_median": "OWND! median (₹)",
        "Pant_top10_Q1": "Band floor (₹)", "Pant_top10_Q3": "Band ceiling (₹)",
        "share_inside": "Inside band", "share_below": "Below band",
    })
    show_table(display, formats={"Inside band": "percent", "Below band": "percent"})
    st.caption("Men’s and boys’ T-shirts are the priority exceptions. Price bands and national "
               "like-for-like sales are indirect measures of cannibalisation.")

def economics():
    st.header("Store economics")
    a, b, c = st.columns(3)
    a.metric("Q1 FY27 segment EBITDA", f"₹{table('margin').iloc[-1]['Segment EBITDA (₹ cr)']:.0f} cr")
    b.metric("Q1 FY27 OWND! revenue estimate", f"₹{FIN['O1']:.1f} cr")
    c.metric("Estimated quarterly revenue per store", f"₹{FIN['ownd_rev_per_store_qtr']:.2f} cr")
    st.caption(f"OWND! revenue sensitivity ₹{FIN['O1_min']:.0f}–{FIN['O1_max']:.0f} cr. "
               "The estimate uses segment revenue and reported format growth rates varied by ±0.5 pp.")
    st.subheader("What does OWND! earn at different Pantaloons margins?")
    assumed = st.slider("Assumed Pantaloons-format EBITDA margin (%)",
                        16.0, 21.0, 18.0, 0.1, key="implied")
    segment = table("margin").iloc[-1]["Segment EBITDA (₹ cr)"]
    implied = segment - FIN["P1"] * assumed / 100
    a, b, c = st.columns(3)
    a.metric("Implied OWND! quarterly EBITDA", f"₹{implied:+.1f} cr")
    b.metric("Implied OWND! margin", f"{implied / FIN['O1']:+.1%}")
    c.metric("Pantaloons margin at OWND! break-even", f"{segment / FIN['P1']:.1%}")
    st.caption("Implied OWND! EBITDA equals reported segment EBITDA minus estimated Pantaloons "
               "revenue times assumed Pantaloons margin. The four-wall store gate requires actual store P&Ls.")
    with st.expander("Quarterly margin evidence"):
        margin_chart()
        show_table(table("margin")[["Quarter", "Segment revenue (₹ cr)", "Segment EBITDA (₹ cr)",
                                   "Segment EBITDA margin (stated)", "Margin YoY stated (pp)",
                                   "EBITDA shortfall vs LY margin (₹ cr)"]],
                   formats={"Segment EBITDA margin (stated)": "percent",
                            "Margin YoY stated (pp)": "%.1f",
                            "EBITDA shortfall vs LY margin (₹ cr)": "%.1f"})

def scenarios():
    st.header("FY28 exit scenarios")
    a, b, c = st.columns(3)
    ownd = a.slider("OWND! EBITDA margin (%)", -25, 15, -5)
    pant = b.slider("Pantaloons EBITDA margin (%)", 15.0, 22.0, 18.0, 0.1)
    rps = c.number_input("OWND! revenue per store / quarter (₹ cr)",
                         min_value=0.1, max_value=5.0,
                         value=FIN["ownd_rev_per_store_qtr"], step=0.05, format="%.4f")
    options = {"Slow down": 95, "Gated hold": 120, "Status quo": 150,
               "Gated hold + release": 160, "Accelerate": 210}
    rows = []
    for name, stores in options.items():
        revenue = stores * rps
        profit = revenue * ownd / 100
        segment = profit + FIN["P1"] * pant / 100
        rows.append({"Rollout option": name, "Exit stores": stores,
                     "OWND! EBITDA / quarter (₹ cr)": profit,
                     "Segment EBITDA / quarter (₹ cr)": segment,
                     "Segment margin": segment / (FIN["P1"] + revenue)})
    frame = pd.DataFrame(rows)
    gap = (options["Accelerate"] - options["Gated hold"]) * rps * ownd / 100
    a, b = st.columns(2)
    a.metric("Accelerate vs gated hold · quarterly EBITDA", f"₹{gap:+.1f} cr")
    b.metric("Annualised difference at exit run rate", f"₹{4 * gap:+.1f} cr")
    show_chart(bar(frame, "Rollout option", "OWND! EBITDA / quarter (₹ cr)", signed=True))
    show_table(frame, formats={"OWND! EBITDA / quarter (₹ cr)": "%.1f",
                               "Segment EBITDA / quarter (₹ cr)": "%.1f",
                               "Segment margin": "percent"})
    st.caption("Illustrative exit run rate from report §§10–11. The exit counts are approximate "
               "network assumptions from the report. The 20-store cap applies to FY28 tranche 1. "
               "Quarterly Pantaloons revenue is fixed at the Q1 FY27 estimate. "
               "The calculation assumes equal store productivity and excludes capex, ramp-up and inflation.")

def markets():
    st.header("Where the next 20 stores could go")
    tier = st.radio("Test cell", ["Metro", "Tier 2"], horizontal=True)
    shortlist = table("markets")
    if tier:
        shortlist = shortlist[shortlist["Tier"] == tier]
    column = "Zudio pincodes with no OWND! or Pantaloons store"
    shortlist = shortlist.sort_values(column, ascending=False)
    show_chart(bar(shortlist, "Market", column))
    show_table(shortlist.drop(columns="Role"))
    st.caption("Shortlisted markets from report §12. Validate site economics, footfall, leases and "
               "store-level overlap before approving a location.")
    with st.expander("Tier mix and co-location evidence"):
        mix = table("tiers")
        show_table(mix, formats={name: "percent" for name in mix if name.endswith("share")})
        co = table("colocation")[["Test", "Actual", "Baseline: city-weighted", "OWND! stores"]]
        show_table(co, formats={"Actual": "percent", "Baseline: city-weighted": "percent"})
        st.caption("Co-location compares 77 OWND! stores in the 28 markets with all three brands. "
                   "City-weighted peer rates account for the concentration of OWND! stores.")
    with st.expander("Pantaloons like-for-like growth"):
        ltl = table("ltl")
        show_table(ltl, formats={name: "percent" for name in ltl if "LTL" in name or name.endswith("growth")})
        st.caption("Q3 FY26 reported LTL is unavailable. The management-adjusted figure and the "
                   "annual-reconciliation estimate use different bases.")

def governance():
    st.header("Stage gates and owners")
    st.markdown("""
    | Review | Evidence required | Action |
    |---|---|---|
    | **Gate 1 · March 2027** | Finance signs off on store-level P&Ls and shared-cost allocation. | Release up to 20 stores in the two test cells. |
    | **Gate 2 · November 2027** | All three tests below pass on the Q2 FY28 review. | Release about 40 more. If the tests fail, slow openings and reposition. |
    """)
    st.subheader("Gate 2 tests")
    st.markdown("""
    | Measure | Report threshold | Latest evidence in the case |
    |---|---|---|
    | Four-wall EBITDA for stores open at least 12 months | Break-even or better | Store-cohort P&L unavailable |
    | Segment margin versus prior year | Within 0.5 pp for two consecutive quarters | −1.2 pp in Q1 FY27 |
    | Pantaloons LTL in OWND! catchments versus other stores | Within 2 pp | Catchment-level LTL unavailable |
    """)
    st.caption("Uses the three tests in §§13–14 of the detailed report. The executive summary "
               "refers to two. Finance and Strategy prepare the pack for the CEO’s decision.")
    st.subheader("Actions before the FY28 review")
    st.markdown("""
    - **Finance and FP&A** agree shared costs and build the monthly store P&L by age cohort.
    - **Strategy and Analytics** track catchment LTL and prepare the monthly CEO pack.
    - **Real Estate and Expansion** screen pincodes and compare metro in-fill with Tier 2 economics.
    - **Merchandising** reviews men’s and boys’ T-shirt pricing and maintains the ≥50% best-seller value guardrail.
    """)
    with st.expander("Sources and definitions"):
        st.markdown("""
        - **Decision and roadmap** · *OWND! Rollout Decision*, Bhinit Rout, 20 October 2026, §§10–14.
        - **Segment financials and LTL** · `Pantaloons_Quarterly_Data.xlsx`, Quarterly data sheet.
        - **MRP and overlap** · `OWND_Prices_18Oct2026.xlsx`, Products sheet and
          `pantaloons_products_18Oct2026.csv`, own-label apparel comparison set.
        - **Competitor price reference** · `Zudio_Price_Benchmarks.xlsx`, Zudio benchmarks sheet.
        - **Footprint** · OWND!, Zudio and Pantaloons store locator snapshots, 18–19 October 2026.
        - **Packaging** · `evidence.json` contains the report’s prepared aggregate tables and model inputs.
          MRP is maximum retail price, LTL is like-for-like sales growth, pp is percentage points and cr is crore.
        """)

st.title("OWND! rollout decision")
st.caption("Aditya Birla Fashion and Retail · FY28 planning case · Report dated 20 October 2026")
views = {"Decision": executive, "Pricing": commercial, "Economics": economics,
         "Scenarios": scenarios, "Markets": markets, "Stage gates": governance}
view = st.radio("Dashboard section", list(views), horizontal=True,
                label_visibility="collapsed")
views[view]()
