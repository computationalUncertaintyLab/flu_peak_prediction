#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.integrate import solve_ivp as solve

if __name__ == "__main__":

    #--sim and tim params
    sim_number = 1000
    T          = 32

    #--This is the mean function over time (We can call this m(t) )
    
    #--epi parameters
    R0         = 2.0
    gamma      = 1.0/2
    beta       = gamma*R0

    #--initial conditions
    s0 = 0.99
    i0 = 0.01
    r0 = 0.

    def sir(t,y,beta,gamma):
        s,i,r,c = y #<--assuming that these are proportions
        
        ds_dt = -beta*s*i
        di_dt = i*(beta*s - gamma)
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
    m_t           = c
    
    #--stochastic noise
    #--We could assume that an observation of the proportion of incident cases, y(t), is y(t) = m(t) + N(0,sigma**2).
    #--Potentially more complicated would be a covariance structure like y~GP( m(t), C(t,t') ) where GP is a Gaussian process with mean function m(t) and covariance function C(t,t')
    #--For now i'll structure this as Indpednent Gaussian in a wat that makes the GP implementation easy 

    sigma = 0.0125
    R     = np.eye( T ) #<--correlation function is sometimes easier to think about
    D     = np.eye( T )
    C     = (sigma*D) @ R @ (sigma*D) #<--Covariance function

    #--simulations of the same exact mean with varying noise according to above Covariance function C
    simulations = m_t[None,:] + np.random.multivariate_normal( mean = np.zeros(len(C)) , cov = C, size=sim_number)
    
    #--im expanding this into a for loop just in case we need to run a more complicated simualtion down the road.
    sim_data = { "sim_number":[], "time":[], "incident_cases":[] }
    for sim_number in range(sim_number):

        sim_data["sim_number"].extend( [sim_number]*T )
        sim_data["time"].extend(np.arange(T))

        simulated_values = simulations[sim_number]
        sim_data["incident_cases"].extend(simulated_values)
    sim_data = pd.DataFrame(sim_data)

    #--drag along paramters just in case
    sim_data["R0"]    = R0
    sim_data["gamma"] = gamma
    sim_data["init"]  = "{:.2f}_{:.2f}_{:.2f}".format(s0,i0,r0)

    sim_data.to_csv("./theoretrical_component/sim_data/simulated_sir_plus_white_noise.csv",index=False)
