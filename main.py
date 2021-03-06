from gurobipy import *
from utils.io import *
import pandas as pd
from datetime import datetime
import argparse


def main(args):
    Bset = pickle_load(args.data_dir + args.Bset_dir)  # 22 Bike Stations
    Bij_set = pickle_load(args.data_dir + args.Bij_set_dir)  # Bike pairs
    deterministic_params = json_load(args.data_dir + args.deterministic_params_dir)  # deterministic parameters
    c = deterministic_params['c']  # unit procurement cost
    v_i = deterministic_params['v_i']  # stock-out cost
    w_i = deterministic_params['w_i']  # time-waste cost
    t_ij = deterministic_params['t_ij']  # unit transshipment cost

    '''Keep in mind that this capacity switcher'''
    capacity_i = json_load(args.data_dir + args.capacity_i_constant_dir)

    scenario_num_set = [100, 300, 500, 700, 900, 1000]
    distributions = ['log-normal', 'normal', 'uniform', 'exponential']
    optimal_table = pd.DataFrame(columns=['Scenario Number', 'Distribution', 'obj', 'duration'] + Bset)

    for scenario_num in scenario_num_set:
        for distribution_choice in distributions:
            print(
                '--------------------%s scenario_number: %d--------------------' % (distribution_choice, scenario_num))
            # scenario number & distribution settings everything below should be inside a for loop
            # will need to load data iteratively
            Sset_dir = args.data_dir + 'Sset_' + str(scenario_num) + '.txt'
            p_s_dir = args.data_dir + 'p_s_' + str(scenario_num) + '.json'
            demScens_dir = args.data_dir + 'demScens_' + distribution_choice + '_' + str(scenario_num) + '.dict'

            # Sets
            Sset = pickle_load(Sset_dir)  # Scenario sets
            p_s = json_load(p_s_dir)
            demScens = pickle_load(demScens_dir)

            ## Settings before running the code
            # for optimal solution in each iteration
            optimal_sol = {'Scenario Number': scenario_num, 'Distribution': distribution_choice}

            ## Model
            '''Put the model into the model folder later'''
            m = Model("2SP_ExtForma")

            # set variables
            # first stage variables
            x = m.addVars(Bset, vtype=GRB.INTEGER, name='x')

            # second stage variables
            beta_ijs = m.addVars(Bset, Bset, Sset, vtype=GRB.INTEGER, name='beta_ijs')
            I_is_surplus = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='I_ijs_surplus')
            I_ijs_shortage = m.addVars(Bset, Bset, Sset, vtype=GRB.INTEGER, name='I_ijs_shortage')
            rho_ijs = m.addVars(Bset, Bset, Sset, vtype=GRB.INTEGER, name='rho_ijs')
            O_is_resCap = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='O_is_resCap')
            O_is_overF = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='O_is_overF')
            tau_ijs = m.addVars(Bset, Bset, Sset, vtype=GRB.INTEGER, name='tau_ijs')
            T_is_excess = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='T_is_excess')
            T_is_lack = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='T_is_lack')

            ## Set objective
            m.setObjective(c * quicksum(x[i] for i in Bset) \
                           + quicksum(p_s[s] * quicksum(v_i * I_ijs_shortage.sum(i, '*', s) \
                                                        + w_i * O_is_overF[(i, s)] \
                                                        + t_ij * tau_ijs.sum(i, '*', s) for i in Bset) for s in Sset))
            ## Set model sense
            m.modelSense = GRB.MINIMIZE

            ## Set constraints
            m.addConstrs((x[i] <= capacity_i[i] for i in Bset), name='assignment_capacity');
            m.addConstrs(
                (beta_ijs[i, j, s] == demScens[i, j, s] - I_ijs_shortage[i, j, s] for i in Bset for j in Bset for s in
                 Sset),
                name='actual_rental');
            m.addConstrs(
                (I_is_surplus[i, s] - I_ijs_shortage.sum(i, '*', s) == x[i] - sum(demScens[i, j, s] for j in Bset) for i
                 in Bset for
                 s in Sset), \
                name='realized_surplus_shortage');
            m.addConstrs((O_is_resCap[i, s] - O_is_overF[i, s] \
                          == capacity_i[i] - x[i] + beta_ijs.sum(i, '*', s) - beta_ijs.sum('*', i, s) for i in Bset for
                          s in Sset),
                         name='residual_overflow_after_rental');
            m.addConstrs((rho_ijs.sum(i, '*', s) == O_is_overF[i, s] for i in Bset for s in Sset),
                         name='redirecting_overflow');
            m.addConstrs((rho_ijs.sum('*', i, s) <= O_is_resCap[i, s] for i in Bset for s in Sset),
                         name='successful_redictions');
            m.addConstrs((T_is_excess[i, s] - T_is_lack[i, s] \
                          == capacity_i[i] - O_is_resCap[i, s] + rho_ijs.sum('*', i, s) - x[i] for i in Bset for s in
                          Sset),
                         name='successful_redictions');
            m.addConstrs((tau_ijs.sum(i, '*', s) == T_is_excess[i, s] for i in Bset for s in Sset),
                         name='transshipment_excessive_bike');
            m.addConstrs((tau_ijs.sum('*', i, s) == T_is_lack[i, s] for i in Bset for s in Sset),
                         name='transshipment_fulfillment');
            m.params.logtoconsole = 0
            start = datetime.now()
            m.optimize()
            duration = (datetime.now() - start).total_seconds()
            optimal_sol['duration'] = duration
            print('duration:', duration)
            ## Get solution into table
            optimal_sol['obj'] = m.ObjVal
            for station in Bset:
                optimal_sol[station] = x[station].x

            optimal_table = optimal_table.append(optimal_sol, ignore_index=True)

        optimal_table.to_csv('results/results_EF_fixedCap.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EF_script")
    parser.add_argument('-d', dest='data_dir', default='./data/')
    parser.add_argument('-Bset_dir', dest='Bset_dir', default='Bset.txt')
    parser.add_argument('-Bij_set_dir', dest='Bij_set_dir', default='Bij_set.txt')
    parser.add_argument('-deterministic_params_dir', dest='deterministic_params_dir',
                        default='deterministic_params.json')
    parser.add_argument('-capacity_i_dir', dest='capacity_i_dir', default='capacity_i.json')
    parser.add_argument('-capacity_i_constant_dir', dest='capacity_i_constant_dir', default='capacity_i_constant.json')
    args = parser.parse_args()

    main(args)
