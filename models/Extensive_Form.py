# # Model
# '''Put the model into the model folder later'''
# m = Model("2SP_ExtForma")
#
# # set variables
# # first stage variables
# x = m.addVars(Bset, vtype=GRB.INTEGER, name='x')
#
# # second stage variables
# beta_ijs = m.addVars(Bset, Bset, Sset, vtype=GRB.INTEGER, name='beta_ijs')
# I_is_surplus = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='I_ijs_surplus')
# I_ijs_shortage = m.addVars(Bset, Bset, Sset, vtype=GRB.INTEGER, name='I_ijs_shortage')
# rho_ijs = m.addVars(Bset, Bset, Sset, vtype=GRB.INTEGER, name='rho_ijs')
# O_is_resCap = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='O_is_resCap')
# O_is_overF = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='O_is_overF')
# tau_ijs = m.addVars(Bset, Bset, Sset, vtype=GRB.INTEGER, name='tau_ijs')
# T_is_excess = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='T_is_excess')
# T_is_lack = m.addVars(Bset, Sset, vtype=GRB.INTEGER, name='T_is_lack')
#
# ## Set objective
# m.setObjective(c * quicksum(x[i] for i in Bset) \
#                + quicksum(p_s[s] * quicksum(v_i * I_ijs_shortage.sum(i, '*', s) \
#                                             + w_i * O_is_overF[(i, s)] \
#                                             + t_ij * tau_ijs.sum(i, '*', s) for i in Bset) for s in Sset))
# ## Set model sense
# m.modelSense = GRB.MINIMIZE
#
# ## Set constraints
# m.addConstrs((x[i] <= capacity_i[i] for i in Bset), name='assignment_capacity');
# m.addConstrs(
#     (beta_ijs[i, j, s] == demScens[i, j, s] - I_ijs_shortage[i, j, s] for i in Bset for j in Bset for s in Sset),
#     name='actual_rental');
# m.addConstrs(
#     (I_is_surplus[i, s] - I_ijs_shortage.sum(i, '*', s) == x[i] - sum(demScens[i, j, s] for j in Bset) for i in Bset for
#      s in Sset), \
#     name='realized_surplus_shortage');
# m.addConstrs((O_is_resCap[i, s] - O_is_overF[i, s] \
#               == capacity_i[i] - x[i] + beta_ijs.sum(i, '*', s) - beta_ijs.sum('*', i, s) for i in Bset for s in Sset),
#              name='residual_overflow_after_rental');
# m.addConstrs((rho_ijs.sum(i, '*', s) == O_is_overF[i, s] for i in Bset for s in Sset),
#              name='redirecting_overflow');
# m.addConstrs((rho_ijs.sum('*', i, s) <= O_is_resCap[i, s] for i in Bset for s in Sset),
#              name='successful_redictions');
# m.addConstrs((T_is_excess[i, s] - T_is_lack[i, s] \
#               == capacity_i[i] - O_is_resCap[i, s] + rho_ijs.sum('*', i, s) - x[i] for i in Bset for s in Sset),
#              name='successful_redictions');
# m.addConstrs((tau_ijs.sum(i, '*', s) == T_is_excess[i, s] for i in Bset for s in Sset),
#              name='transshipment_excessive_bike');
# m.addConstrs((tau_ijs.sum('*', i, s) == T_is_lack[i, s] for i in Bset for s in Sset),
#              name='transshipment_fulfillment');
# m.optimize()