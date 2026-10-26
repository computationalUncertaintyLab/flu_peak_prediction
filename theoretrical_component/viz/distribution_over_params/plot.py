#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":

    fitted_data = pd.read_csv("./theoretrical_component/fitted_MLEs/fitted_data__for_simulated_sir_plus_white_noise.csv")

    fig, ax = plt.subplots()
    
    sns.kdeplot( x="R0_fit", y= "gamma_fit", data = fitted_data, ax=ax )
    sns.scatterplot(x="R0_fit", y= "gamma_fit", data = fitted_data, ax=ax, color="black",s=3 )
    
    ax.axvline(2.0 ,color="black")
    ax.axhline(1./2,color="black")

    ax.set_xlim(1,3)
    ax.set_ylim(1./5,9/10)
    
    plt.savefig("./theoretrical_component/viz/distribution_over_params/validation.pdf")
