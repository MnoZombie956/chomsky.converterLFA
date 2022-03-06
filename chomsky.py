import sys # for main args 
import json
import itertools # combinations

class Cfg: # context free grammar
    def __init__(self, init_path=''):
        self.variables = []
        self.simbols = []
        self.rules = dict()
        self.start_rule = '' 
        if init_path:
            with open(init_path) as json_file:
                data = json.load(json_file)
            ##print("Json form:\n", data)
            self.variables = data['glc'][0]
            self.simbols = data['glc'][1]
            for rule in data['glc'][2]:
                value = []
                for simbol in rule[1:]:
                    list_of_simbols = []
                    gen = (char for char in simbol)
                    for ele in gen:
                        list_of_simbols.append(ele)
                    value.append(list_of_simbols)
                if rule[0] in self.rules.keys():
                    self.rules[rule[0]].extend(value)
                else:
                    self.rules[rule[0]] = value
            self.start_rule = data['glc'][3]
        ## print("Cng object form:")
        ## print(self.variables)
        ## print(self.simbols)
        ## print(self.rules)
        ## print(self.start_rule)

    def get_nullable_variables(self):
        N = set(self.rules.keys())
        nullable_vars = ['#']

        while True:
            oldN = N
            for rule in list(self.rules.keys()):
                for var in list(self.rules[rule]):
                    if (len(set(var) - set(nullable_vars))) == 0 and rule not in nullable_vars: # if n belongs to kleenstar(nullvars) 
                        nullable_vars.append(rule)
            N = N - set(nullable_vars)
            if oldN == N:
                break

        nullable_vars.remove('#') # bc lambda -> lambda is always nullable
        #print("Nullable Vars: ", nullable_vars)
        return nullable_vars

    def lists_all_combinations_of_removal(self, l, removal, existent, rule): # if comb doest exist, add it
        combinations = existent.copy()
        indexlist = []
        bin_size = 0

        for i, ele in enumerate(l):
            if ele in removal:
                indexlist.append([None, 1, ele])
                bin_size += 1
            else:
                indexlist.append([None, 0, ele])

        if bin_size == 0:
            return combinations

        bin_list = list(itertools.product([0, 1], repeat=bin_size))

        for b in bin_list:
            #print(f"b:{b}")
            new_combo = []

            bindigit = 0
            #print("two indexlist", indexlist)
            for i, listele in enumerate(indexlist):
                if listele[1] == 1:
                    indexlist[i][0] = b[bindigit]
                    bindigit+=1
                else:
                    indexlist[i][0] = 0
            #print("three indexlist", indexlist)
            for listele in indexlist:
                #print("listele:",listele)
                if listele[0] == 0:
                    new_combo.append(listele[2])
                    #print("added listele[2]:",listele[2])
                    #print(f"now, new_combo:{new_combo}")


            #print(f"new_combo:{new_combo}")

            if new_combo not in combinations and new_combo!=[] and not (len(new_combo)==1 and new_combo[0] == rule):
                combinations.append(new_combo)

            #print(f"allcombos:{combinations}")

        return combinations

    def find_if_rule_gens_lambda(self, init_rule, nullable_vars, visited=None):
        for var in self.rules[init_rule]:
            #print("var:",var)
            for simbol in var:
                #print("simbol:",var)
                if simbol == '#':
                    return True
            if len(var) == 1 and var[0].isupper() and var[0] in self.rules.keys() and var not in visited:
                visited.append(var)
                return self.find_if_rule_gens_lambda(var[0], nullable_vars, visited)
        return False


    def remove_lambda_rules(self, nullable_vars, cfg=None): # has also a cfg return if parameters where given, otherwise self is updated
        if not cfg:
            cfg = self

        start_rule_gens_lambda = cfg.start_rule in nullable_vars# self.find_if_rule_gens_lambda(cfg.start_rule, nullable_vars)# P is nullable important but case not covered in Gjson 

        combinations = []
        # remove nullable variables from rules
        for rule in list(cfg.rules.keys()):
            #print(f"rule:{rule}")
            for var in list(cfg.rules[rule]):
                #print(f"var:{var}")

                if len(var) == 1 and var[0] == "#" and len(cfg.rules[rule]) == 1:
                    cfg.rules[rule] = [""]
                    #print("# removed, now X -> []")
                elif len(var) == 1 and var[0] == "#" and len(cfg.rules[rule]) > 1:
                    cfg.rules[rule].remove(var)
                    #print("# removed, now X -> (V, S)*-#")  
                else:
                    combinations = self.lists_all_combinations_of_removal(var, nullable_vars, cfg.rules[rule], rule)
                    #print(f"new combinations:{combinations}")

                    cfg.rules[rule] = combinations.copy()

        if start_rule_gens_lambda:
            cfg.rules[cfg.start_rule].append("#")
            #print("Start rule orginally gens lambda, # added")

        if cfg:
            return cfg
        self = cfg

    def remove_unit_rules(self, cfg=None):
        if not cfg:
            cfg = self

        chaining = dict()

        for key in list(cfg.rules.keys()):
            chaining[key] = list(key)

        #print("chaining with only keys:",chaining)

        for rule in chaining.keys():
            for var in cfg.rules[rule]:
                if len(var) == 1 and var[0] in chaining.keys():
                    chaining[rule].extend(var)

        #print("chaining with basic:",chaining)

        for key in chaining.keys():
            lookfor = list(chaining[key])[1:]
            #print("lookfor:",lookfor)
            if lookfor != []:
                for look in lookfor:
                    for var in cfg.rules[look]:
                        #print(f"\tlook:{look} var:{var} chaining[key]:{chaining[key]}")

                        if len(var) == 1 and var[0] not in chaining[key] and var[0] in chaining.keys():
                            chaining[key].extend(var)
            #print("deep chaining:",chaining)

        rules_wo_unit_vars = dict()

        for key in chaining.keys():
            for gen in chaining[key]:
                for var in cfg.rules[gen]:
                    #print(f"key:{key} gen:{gen} var:{var}")
                    if len(var) != 1 or (len(var) == 1 and (not var[0].isupper())):
                        #print(f"\tput var:{var} in key:{key} gen")
                        if key not in rules_wo_unit_vars.keys():
                            rules_wo_unit_vars[key] = []
                        if var not in rules_wo_unit_vars[key] and var:
                            rules_wo_unit_vars[key].append(var)

        #print(rules_wo_unit_vars)

        cfg.rules = rules_wo_unit_vars

        #print("remove_unit_rules END")

        if cfg:
            return cfg
        self = cfg

    def remove_useless_variables(self, cfg):
        if not cfg:
            cfg = self
        # algo pt 1: pick all rules that either generate straight way a simbol or a rule that produces a simbol somehow
        v1 = []
        for rule in cfg.rules.keys(): # var that gen simbols
            for var in cfg.rules[rule]:
                if len(var) == 1 and var[0] in cfg.simbols:
                    v1.append(rule)
        #print("pre v1:",v1)
        for rule in list(set(cfg.variables)-set(v1)): # var that gen X -> w in simbols*
            for var in cfg.rules[rule]:
                if not False in ((simbol in cfg.simbols or simbol in v1) for simbol in var):
                    if rule not in v1 and not('' in var):
                        v1.append(rule)

        r1 = dict()
        for rule in v1:
            new_var_for_rule = []
            for var in cfg.rules[rule]:
                if (False in ((x in v1 or x in cfg.simbols and x not in new_var_for_rule) for x in var))==False: # omg, luv py
                    new_var_for_rule.append(var)
                else:
                    pass
            r1[rule] = new_var_for_rule.copy()

        #print('algo pt1, v1:',v1,'\nr1:',r1)

        #algo pt 2: include P and pick all the rules X that, from, generate a format uXv where u,v are either from v1 or simbols

        n = [cfg.start_rule]
        i2 = []

        while True:
            i2 = list(set().union(i2,n))
            y = list(set(v1)-set(i2)) 
            #print(f"ite> i2 U n:{n} is {i2}, y:{y}")
            n2 = []
            for x in n:
                for var in r1[x]:
                    #print(f"x:{x}->var:{var} of r1[x]:{r1[x]}")
                    if True in ((somey in var) for somey in y):
                        #print("There is in var some simbol of y")
                        for simbol in var:
                            if simbol in y:
                                index = var.index(simbol) 
                                u = var[:index]
                                v = var[index:]
                                #print(f"{simbol} is in var but does uXv:{u}{simbol}{v} exist where uv satisfy")
                                if not False in ((eleu in list(set().union(v1,cfg.simbols,['']))) for eleu in u)\
                                and not False in ((elev in list(set().union(v1,cfg.simbols,['']))) for elev in v)\
                                and simbol not in n2:
                                    #print(f"\tit does")
                                    n2.append(simbol)
            n = n2.copy()
            if n2 == []:
                break
        v2 = i2.copy()
        r2 = dict()
        for rule in r1.keys():
            if rule in v2:
                r2[rule] = r1[rule].copy()

        #print('algo tp2, v2:',v2,'r2:',r2)

        cfg.variables = v2
        cfg.rules = r2

        if cfg:
            return cfg
        self = cfg

    def check_variables_only_rules(self, cfg):
        if not cfg:
            cfg = self

        nv = []
        nr = dict() 
        for rule in cfg.rules.keys():
            for var in cfg.rules[rule]:
                #print(f"only_lowers_in_var for var:{var} in rule:{rule}:", (len(var) > 1 and not False in list((x in cfg.simbols for x in var))))
                if (len(var) > 1 and True in list((x in cfg.simbols) for x in var) and True in list((x in cfg.rules.keys()) for x in var))\
                or (len(var) > 1 and not False in list((x in cfg.simbols for x in var))):
                    #print(f"There still the var:{var} in rule:{rule}")
                    return True
        return False

    def enforce_variables_only_rules(self, cfg):
        if not cfg:
            cfg = self

        new_rules_qnt = 0
        rule_for_simbol = dict()
        while self.check_variables_only_rules(cfg):
            cfg2 = Cfg() 
            for key, value in cfg.rules.items():
                cfg2.rules[key] = value
            cfg2.simbols = cfg.simbols.copy()
            cfg2.variables = cfg.variables.copy()
            cfg2.start_rule = cfg.start_rule

            done = False
            for rule in cfg.rules.keys():
                for i, var in enumerate(cfg2.rules[rule]):
                    only_lowers_in_var = (len(var) > 1 and not False in list((x in cfg.simbols for x in var)))
                    for j, simbol in enumerate(var):
                        if (simbol in cfg2.simbols and len(var) > 1) or only_lowers_in_var:
                            #print(f"simbol:{simbol} found in var:{var} at j:{j}")
                            if simbol not in rule_for_simbol.keys():
                                while('_X' + str(new_rules_qnt) + '_' in cfg.rules.keys()): # we must garantee there isn't conflict to an already existent rule RN for R 
                                    new_rules_qnt += 1
                                new_rule_name = '_X' + str(new_rules_qnt) + '_'
                                rule_for_simbol[simbol] = new_rule_name
                                cfg2.rules[new_rule_name] = [[simbol]]
                                
                                if simbol in rule_for_simbol.keys():
                                    cfg2.rules[rule][i] = var[:j] + [rule_for_simbol[simbol]] + var[j+1:]
                                else:
                                    cfg2.rules[rule][i] = [new_rule_name] + var[j+1:] # 000000000000000
                            else:
                                cfg2.rules[rule][i] = var[:j] + [rule_for_simbol[simbol]] + var[j+1:] # 000000000000000
                            done = True
                            #cfg2.print()
                        if done:
                            break
                    if done:
                        break
                if done:
                    break
            for key, value in rule_for_simbol.items():# since the while loop for new_rule_name won't generate an existent rule
                cfg2.variables = list(set().union([value], cfg2.variables))

            for key, value in cfg2.rules.items():
                cfg.rules[key] = value
            cfg.simbols = cfg2.simbols.copy()
            cfg.variables = cfg2.variables.copy()
            cfg.start_rule = cfg2.start_rule

            #cfg.print()
        if cfg:
            return cfg
        self = cfg

    def check_dual_variable_rules(self, cfg):
        for rule in cfg.rules.keys():
            for var in  cfg.rules[rule]:
                if len(var) > 2:
                    #print(f"var:{var} is len:{len(var)}")
                    return True
        return False

    def enforce_dual_variable_rules(self, cfg):
        if not cfg:
            cfg = self

        new_rules_qnt = 0
        rule_for_dualVarRule = dict()
        while self.check_dual_variable_rules(cfg):
            cfg2 = Cfg() 
            for key, value in cfg.rules.items():
                cfg2.rules[key] = value
            cfg2.simbols = cfg.simbols.copy()
            cfg2.variables = cfg.variables.copy()
            cfg2.start_rule = cfg.start_rule

            done = False
            for rule in list(cfg.rules.keys()):
                for i, var in enumerate(cfg2.rules[rule]):
                    if not False in list(((x in cfg.variables) for x in var)) and len(var) > 2:
                        u = var[:-2]
                        v = var[-2:]

                        #print(f"var:{var} in rule:{rule} shall be enforced, btw is v:{v} in rule_for_dualVarRuleK:{list(rule_for_dualVarRule.keys())}? ans:{str(v) in list(rule_for_dualVarRule.keys())}")

                        if str(v) in list(rule_for_dualVarRule.keys()):
                            cfg2.rules[rule][i] = u + rule_for_dualVarRule[str(v)]
                        else:
                            while ('_Y' + str(new_rules_qnt) + '_' in cfg.rules.keys()):
                                new_rules_qnt += 1
                            new_rule_name = '_Y' + str(new_rules_qnt) + '_'
                            rule_for_dualVarRule[str(v)] = [new_rule_name]
                            cfg2.rules[rule][i] = u + [new_rule_name]
                            cfg2.rules[new_rule_name] = [v]

                        done = True
                        #cfg2.print()
                    if done:
                        break
                if done:
                    break
            for key, value in rule_for_dualVarRule.items():# since the while loop for new_rule_name won't generate an existent rule
                cfg2.variables = list(set().union(value, cfg2.variables))

            for key, value in cfg2.rules.items():
                cfg.rules[key] = value
            cfg.simbols = cfg2.simbols.copy()
            cfg.variables = cfg2.variables.copy()
            cfg.start_rule = cfg2.start_rule

            #cfg.print()

        if cfg:
            return cfg
        self = cfg

    def to_Cnf(self): # to chomsky normal form
        # order must preserve consistency
        cnf = self # copies cfg

        nullable_vars = self.get_nullable_variables()
        cnf = self.remove_lambda_rules(nullable_vars, cnf)
        #print("- P1 done")
        cnf = self.remove_unit_rules(cnf)
        #print("- P2 done")
        cnf = self.remove_useless_variables(cnf)
        #print("- P3 done")
        cnf = self.enforce_variables_only_rules(cnf)
        #print("- P4 done")
        cnf = self.enforce_dual_variable_rules(cnf)
        #print("- P5 done")
        #cnf.print()

        #cnf.print_formated()

        return cnf

    def print(self):
        cfg_dict = dict()
        cfg_dict['glc'] = list()
        cfg_dict['glc'].append(self.variables)
        cfg_dict['glc'].append(self.simbols)
        cfg_dict['glc'].append(self.rules)
        cfg_dict['glc'].append(self.start_rule)

        #print(cfg_json)

    def print_formated(self):
        #print("\nFormated>")
        cfg_dict = dict()
        cfg_dict["glc"] = list()
        cfg_dict["glc"].append(str(self.variables))
        cfg_dict["glc"].append(str(self.simbols))
        cfg_dict["glc"].append(list([]))
        l = list(self.rules.keys())
        for key in l:
            for value in self.rules[key]:
                v = str()
                for digit in value:
                    v = v + digit
                cfg_dict['glc'][2].append(str([key]+[v]))


        cfg_dict['glc'].append(str(self.start_rule))

        cfg_json = json.dumps(cfg_dict, indent = 4)
        print(cfg_json)
        #print(cfg_dict)



def main(init_path) -> int:
    #print(f"Given:{init_path}")
    cfg = Cfg(init_path)
    cfg.to_Cnf()
    cfg.print_formated()
    return 0

if __name__ == '__main__':
    main(sys.argv[1])



