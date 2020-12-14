# Stochastic_optimization_models_BSP
 
This repository contains the work for solving and implementing Stochastic Optimization Bike Sharing Systems (BSS) problem. 
Models include:
* Two-stage extensive form
* Benders multiple & single cut model
* Multi-stage model 

<b>Data Generation:</b>
Data generation was performed using project_data.ipynb. For each station pair (A-V), four possible distributions were used for the stochastic demands inlcuding Normal distribution, log-normal distribution, exponential distribution, and uniform distribution. Scenario numbers being used were 100,300,500,700,900,and 1000. 

<b>Extensive Form results:</b>
The results for all different use cases using different scenario number, probabilistic distributions and capacity range were computed using main.py. Default arguments were set inside the main script. 
