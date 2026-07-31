# flu_peak_prediction

Scripts for assembling ILI and hospitalization data used to explore flu-peak prediction.

## Python scripts

### `data/download_FluID_dataset.py`

Downloads the WHO FluMart `VIW_FID_EPI` dataset.

| | |
|---|---|
| **Inputs** | Optional CLI args: `--output` (default `./data/who_viw_fid_epi.csv`), `--chunk-size-mb` |
| **Output** | `./data/who_viw_fid_epi.csv` |
| **Description** | Raw WHO FluID epidemiology CSV (ILI/ARI/SARI cases and denominators by country and week). |

---

### `analysis_data/create_WWHO_ILI_Signal.py`

Builds a seasonal ILI signal from WHO FluID data.

| | |
|---|---|
| **Inputs** | `./data/who_viw_fid_epi.csv` |
| **Output** | `./analysis_data/ILI_signal_by_season.csv` |
| **Description** | Country–season summary with outpatient ILI proportion (`ili_proportion` / `ili_percent`) and population-based ILI rate per 100k person-weeks. Seasons run week 35 through week 20. |

---

### `analysis_data/from_FLUID_to_formmatted_data.py`

Alternative FluID seasonal summarizer (older / parallel path).

| | |
|---|---|
| **Inputs** | `./data/who_viw_fid_epi.csv` |
| **Output** | `./analysis_data/summarized_fluid.csv` |
| **Description** | Country–season aggregates of ILI/ARI/SARI counts and a crude outpatient ILI proportion (`pILI`). Season windows differ by hemisphere (NH vs SH). |

---

### `analysis_data/build_ili_data.py`

Pulls US ILINet data from the Delphi Epidata API.

| | |
|---|---|
| **Inputs** | None (queries Epidata FluView for all states, 2021–present) |
| **Output** | `./analysis_data/ili_data_all_states_2021_present.csv` |
| **Description** | Weekly state-level ILI metrics (`wili`, `ili`, case/patient counts, age groups) with epiweek and season labels. |

---

### `analysis_data/format_ili_data.py`

Formats the Epidata ILI extract and adds a national series.

| | |
|---|---|
| **Inputs** | `./analysis_data/ili_data_all_states_2021_present.csv` |
| **Output** | `./analysis_data/ili_data_all_states_2021_present__formatted.csv` |
| **Description** | State abbreviations, zero-padded FIPS codes, and a national (`nat`) row per epiweek computed from pooled ILI counts. |

---

### `analysis/predict_total_US_hosps_setup.py`

Assembles a modeling table linking US hosps, US ILI, and Southern Hemisphere ILI.

| | |
|---|---|
| **Inputs** | `./analysis_data/ILI_signal_by_season.csv`, `./data/target-data/target-hospital-admissions.csv` |
| **Output** | `./analysis/US_plus_SH_data.csv` |
| **Description** | Season-level table with total US hospitalizations, US ILI proportion, and Southern Hemisphere country ILI proportions (from 2022 onward). Helper dataset for exploring peak prediction. |
