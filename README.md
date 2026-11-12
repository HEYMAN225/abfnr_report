# OWND! rollout decision

An executive dashboard for the FY28 planning case by Bhinit Rout, dated 20 October 2026. Open **Decision** first. Use **Scenarios** to demonstrate the EBITDA impact of a −5% versus +5% OWND! margin. Finish on **Stage gates** to show what evidence unlocks tranche 2.

## Deploy in the browser

1. Extract the ZIP. Open [GitHub New Repository](https://github.com/new), name the repository `ownd-rollout-dashboard` and choose **Private** for controlled sharing.
2. On the new repository page, click **uploading an existing file**. Upload the **four files inside** the extracted folder and commit them to `main`.
3. Open `streamlit_app.py` on GitHub and copy its URL. In [Streamlit Community Cloud](https://share.streamlit.io/), connect GitHub and select **Create app → Yup, I have an app → Paste GitHub URL**. The repository, branch and file can also be entered manually using `main` and `streamlit_app.py`.
4. In **Advanced settings**, choose Python **3.12**, then click **Deploy**. For a private repository, grant Streamlit access under **Settings → Linked accounts** if needed.
5. Share the resulting `.streamlit.app` URL. For a private app, add the presentation viewers by email in Streamlit.

[Deploying an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) · [Managing viewer access](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app)

## Preview locally

With Python 3.10–3.12 installed, open a terminal in this folder and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Data and interpretation

The self-contained JSON uses the supplied analysis project's results and aggregate tables derived from the workbook, catalogue and locator snapshots. The deployment contains aggregate evidence and the candidate-market list. The raw workbooks, raw product catalogue, store addresses and original report PDF are omitted from the package.

The dashboard uses the report's detailed three-test Gate 2 definition in sections 13–14. The scenario model uses section 11's approximate FY28 exit counts and Q1 FY27 run-rate inputs. The 160-store released tranche uses the same calculation as the other options. Actual mature-store P&L and catchment LTL are unavailable in the supplied data.
