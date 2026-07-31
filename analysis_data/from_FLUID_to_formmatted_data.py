#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":


    d = pd.read_csv("./data/who_viw_fid_epi.csv")
    d = d[ ["WHOREGION", "COUNTRY_CODE","COUNTRY_AREA_TERRITORY","HEMISPHERE"
            ,"MMWR_WEEKSTARTDATE","MMWR_YEAR","MMWR_WEEK","MMWRYW"
            ,"ILI_CASE","ILI_OUTPATIENTS","ILI_POP_COV","ARI_CASE","SARI_CASE","SARI_INPATIENTS","SARI_POP_COV"] ]

    def assign_season(x):
        hem    = str(x.HEMISPHERE)
        MMWRYW = str(x.MMWRYW)
        yr,wk  = int(MMWRYW[:4]), int(MMWRYW[-2:])

        if hem == "NH":
            if wk>=40 and wk<=53:
                season=yr
            elif wk>=1 and wk<=22:
                season=yr-1
            else:
                season=-1
                
        elif hem == "SH":
            if wk>=15 and wk<46: #<--typical range for the flu season in SH (32 weeks)
                season=yr
            else:
                season=-1
        else:
            season = -1
        return season
    
    d["SEASON"] = d.apply(assign_season, 1)

    d = d.loc[d.SEASON!=-1]
    
    def add(x):
        covs = ["ILI_CASE","ILI_OUTPATIENTS","ILI_POP_COV","ARI_CASE","SARI_CASE","SARI_INPATIENTS","SARI_POP_COV"]
        dct = {}
        for name in covs:
            dct[name] = np.nansum(x[name])
        return pd.Series(dct)
        
    summary = d.groupby(["WHOREGION","COUNTRY_CODE","COUNTRY_AREA_TERRITORY","HEMISPHERE","SEASON"]).apply(add)
    summary = summary.reset_index()
    summary = summary.sort_values(["COUNTRY_CODE","SEASON"])

    summary["pILI"] = summary.ILI_CASE/(summary.ILI_OUTPATIENTS + summary.ILI_CASE)
    
 
    summary.to_csv("./analysis_data/summarized_fluid.csv",index=False)

    
    





    

