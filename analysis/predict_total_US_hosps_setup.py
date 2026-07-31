#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":

    d = pd.read_csv("./analysis_data/ILI_signal_by_season.csv")

    US  = d.loc[d.COUNTRY_CODE=="USA"]
    US["season"] = [ int(x.split("/")[0]) for x in US.season.values]

    US = US[ ["season","ili_proportion"] ]

    #--group by hemisphere
    SH = d.loc[d.HEMISPHERE=="SH"]
    SH["season"] = [ x.split("/")[-1] for x in SH.season.values]

    
    SH_wide         = pd.pivot_table(index="season",columns=["COUNTRY_CODE"],values=["ili_proportion"],data=SH)
    
    SH_wide.columns   = [y for x,y in SH_wide.columns]
    SH_wide           = SH_wide.reset_index()
    SH_wide           = SH_wide.interpolate()
    SH_wide["season"] = SH_wide.season.astype(int)
    SH_wide           = SH_wide.loc[SH_wide.season>=2022]
    
    US_plus_SH = US.merge( SH_wide, on = ["season"], how="right" )

    #--Need to add in NHSN hospitalizations
    us_hosps = pd.read_csv("./data/target-data/target-hospital-admissions.csv")
    us_hosps = us_hosps.loc[us_hosps.location=="US"]
    
    #--add season
    def assign_season(row):
        from datetime import datetime, timedelta
        from epiweeks import Week
        
        dt = datetime.strptime(row.date,"%Y-%m-%d")
        w = Week.fromdate(dt)

        year,week = w.year,w.week

        if week >= 35:
            return f"{year}/{year + 1}"
        else:
            return f"{year - 1}/{year}"

    us_hosps["season"] = us_hosps.apply(assign_season, 1)
    us_hosps["season"] = [ int(x.split("/")[0]) for x in us_hosps.season.values]

    def addup(d):
        return pd.Series({"ttl_hosps": np.nansum(d["value"].values)})
    ttl_hosps = us_hosps.groupby(["season"]).apply(addup)
    ttl_hosps = ttl_hosps.reset_index()

    
    US_plus_SH = ttl_hosps.merge( US_plus_SH, on = ["season"], how = "right" )

    #--this doesnt need to be output. Just for help looking at the data
    US_plus_SH.to_csv("./analysis/US_plus_SH_data.csv", index=False)
