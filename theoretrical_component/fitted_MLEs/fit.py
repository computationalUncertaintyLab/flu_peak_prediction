#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.integrate import solve_ivp as solve
from scipy.stats import qmc
from scipy.optimize import minimize

from joblib import delayed,Parallel

if __name__ == "__main__":

    sim_data = pd.read_csv("./theoretrical_component/sim_data/simulated_sir_plus_white_noise.csv")

    def find_optimal_parmeters(data):
        def fit(params,data):
            import scipy.stats

            R0, gamma, sigma = params
            beta = R0*gamma
            T = len(data)

            #--assume initial conditions are known (best case)
            s0 = 0.99
            i0 = 0.01
            r0 = 0.

            def sir(t,y,beta,gamma):
                s,i,r,c = y #<--assuming that these are proportions

                ds_dt = -beta*s*i
                di_dt = beta*s*i - gamma*i
                dr_dt = gamma*i
                dc_dt = beta*s*i

                return [ds_dt,di_dt,dr_dt,dc_dt]

            results = solve( sir
                             , y0     = [s0,i0,r0,i0]
                             , t_span = (0,T)
                             , t_eval = np.arange(0,T,1)
                             , args   = (beta, gamma)
                             )
            s_i_r_c = results.y
            times   = results.t

            s,i,r, cumu_c = s_i_r_c
            c             = np.append( i0,  np.diff(cumu_c) ) #<--in other words we assume all the i0 are incident at once

            return np.sum( scipy.stats.norm( c, sigma).logpdf( data ) )

        #--find a good starting point by Latin Hypercube over the parameter space
        sampler = qmc.LatinHypercube(d=3)
        sample  = sampler.random(n=1000)

        param_ranges = {  "R0":[1,10], "gamma":[1./10,10], "sigma":[10**-3,0.5] }

        param_samples = np.array([ param_ranges["R0"][0], param_ranges["gamma"][0], param_ranges["sigma"][0]  ]) + sample*np.array([ param_ranges["R0"][1] - param_ranges["R0"][0], param_ranges["gamma"][1] - param_ranges["gamma"][0], param_ranges["sigma"][1] - param_ranges["sigma"][0]  ])

        score      = -np.inf
        best_param = 0
        for params in param_samples:
            score_attempt = fit(params, data)
            if score_attempt > score:
                best_param = params
                score      = score_attempt

        results  = minimize( lambda params: -fit(params,data)
                             , x0=best_param
                             ,method="L-BFGS-B",
                             bounds=[
                                 (1, 10),     # R0
                                 (1./10, 10),    # gamma
                                 (10**-3, 0.5)]
                             ,options={"maxiter": 1000})
        best_fit = results.x

        return best_fit

    def process_data(sim,data):
        fit_data = {"sim_number":[], "R0_fit":[], "gamma_fit":[], "sigma_fit":[]}

        optimal_params = find_optimal_parmeters(data["incident_cases"].values)

        fit_data["sim_number"].append(sim)
        fit_data["R0_fit"].append(optimal_params[0])
        fit_data["gamma_fit"].append(optimal_params[1])
        fit_data["sigma_fit"].append(optimal_params[2])

        fit_data = pd.DataFrame(fit_data)
        return fit_data

    params = Parallel(n_jobs=20)( delayed(process_data)(sim,data) for (sim, data) in sim_data.groupby("sim_number") )

    fit_data = pd.concat(params)
    fit_data.to_csv("./theoretrical_component/fitted_MLEs/fitted_data__for_simulated_sir_plus_white_noise.csv", index=False)
