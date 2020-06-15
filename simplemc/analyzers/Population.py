from .Individual import Individual
import numpy as np
import copy
import pandas as pd
import time
import sys
from datetime import datetime


class Population:
    def __init__(self, n_individuals, n_variables, lower_bounds=None,
                 upper_bounds=None):

        self.n_individuals = n_individuals
        self.n_variables = n_variables
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
        self.individuals = []
        self.optimized = False
        self.iter_optimization = None
        self.best_individual = None
        self.best_fitness = None
        self.best_function_value = None
        self.best_value_variables = None
        self.historical_individuals = []
        self.historical_best_value_variables = []
        self.historical_best_fitness = []
        self.historical_best_function_value = []
        self.difference_abs = []
        self.results_df = None
        self.fitness_optimal = None
        self.value_variables_optimal = None
        self.function_value_optimal = None

        if self.lower_bounds is not None \
        and not isinstance(self.lower_bounds,np.ndarray):
            self.lower_bounds = np.array(self.lower_bounds)

        if self.upper_bounds is not None and not isinstance(self.upper_bounds,np.ndarray):
            self.upper_bounds = np.array(self.upper_bounds)

        for i in np.arange(n_individuals):
            individual_i = Individual(
                            n_variables=self.n_variables,
                            lower_bounds=self.lower_bounds,
                            upper_bounds=self.upper_bounds)
            self.individuals.append(individual_i)

    def show_individuals(self, n=None):
        if n is None:
            n = self.n_individuals
        elif n > self.n_individuals:
            n = self.n_individuals

        for i in np.arange(n):
            print(self.individuals[i])
        return(None)

    def evaluar_population(self, target_function, optimization):
        for i in np.arange(self.n_individuals):
            self.individuals[i].calculate_fitness(
                target_function=target_function,
                optimization=optimization)

        self.best_individual = copy.deepcopy(self.individuals[0])
        for i in np.arange(self.n_individuals):
            if self.individuals[i].fitness > self.best_individual.fitness:
                self.best_individual = copy.deepcopy(self.individuals[i])

        self.best_fitness = self.best_individual.fitness
        self.best_value_variables = self.best_individual.value_variables
        self.best_function_value = self.best_individual.function_value


    def cross_individuals(self, parental_1, parental_2):

        if parental_1 not in np.arange(self.n_individuals):
            raise Exception(
                "index of parental_1 should be between 0 and " 
                "the number of individuals of the population."
                )
        if parental_2 not in np.arange(self.n_individuals):
            raise Exception(
                "index of parental_2 should be between 0 and " 
                "the number of individuals of the population."
                )

        parental_1 = self.individuals[parental_1]
        parental_2 = self.individuals[parental_2]
        
        offspring = copy.deepcopy(parental_1)
        offspring.value_variables = np.repeat(None, offspring.n_variables)
        offspring.fitness = None

        inheritance_parent_1 = np.random.choice(
                                a=[True, False],
                                size=offspring.n_variables,
                                p=[0.5, 0.5],
                                replace=True
                            )
        inheritance_parent_2 = np.logical_not(inheritance_parent_1)

        offspring.value_variables[inheritance_parent_1] \
            = parental_1.value_variables[inheritance_parent_1]

        offspring.value_variables[inheritance_parent_2] \
            = parental_2.value_variables[inheritance_parent_2]
        

        offspring = copy.deepcopy(offspring)


        return(offspring)
    
    def select_individual(self, n, return_indexs=True,
                              method_selection="tournament"):

        if method_selection not in ["roulette", "rank", "tournament"]:
            raise Exception(
                "Selection method should be roulette, rank o tournament"
                )

        array_fitness = np.repeat(None, self.n_individuals)
        for i in np.arange(self.n_individuals):
            array_fitness[i] = copy.copy(self.individuals[i].fitness)
        
        if method_selection == "roulette":
            probabilidad_selection = array_fitness / np.sum(array_fitness)
            ind_selected = np.random.choice(
                                    a       = np.arange(self.n_individuals),
                                    size    = n,
                                    p       = list(probabilidad_selection),
                                    replace = True
                               )
        elif method_selection == "rank":
            order = np.flip(np.argsort(a=array_fitness) + 1)
            ranks = np.argsort(order) + 1
            probabilidad_selection = 1 / ranks
            probabilidad_selection = probabilidad_selection / np.sum(probabilidad_selection)
            ind_selected = np.random.choice(
                                a       = np.arange(self.n_individuals),
                                size    = n,
                                p       = list(probabilidad_selection),
                                replace = True
                            )
        elif method_selection == "tournament":
            ind_selected = np.repeat(None,n)
            for i in np.arange(n):
                # Se selectionan aleatoriamente dos parejas de individuals.
                candidates_a = np.random.choice(
                                a       = np.arange(self.n_individuals),
                                size    = 2,
                                replace = False
                            )
                candidates_b = np.random.choice(
                                a       = np.arange(self.n_individuals),
                                size    = 2,
                                replace = False
                            )
                # Selection best fitness of each pair.
                if array_fitness[candidates_a[0]] > array_fitness[candidates_a[1]]:
                    winner_a = candidates_a[0]
                else:
                    winner_a = candidates_a[1]

                if array_fitness[candidates_b[0]] > array_fitness[candidates_b[1]]:
                    winner_b = candidates_b[0]
                else:
                    winner_b = candidates_b[1]

                # For each couple, comparison of winners
                if array_fitness[winner_a] > array_fitness[winner_b]:
                    ind_final = winner_a
                else:
                    ind_final = winner_b
                
                ind_selected[i] = ind_final

        if(return_indexs):
            return(ind_selected)
        else:
            if n == 1:
                return(copy.deepcopy(self.individuals[int(ind_selected)]))
            if n > 1:
                return(
                    [copy.deepcopy(self.individuals[i]) for i in ind_selected]
                )
            
    def create_new_generation(self, method_selection="tournament",
                               elitism=0.1, prob_mut=0.01,
                               distribution="uniform",
                               media_distribution=1, sd_distribution=1,
                               min_distribution=-1, max_distribution=1):

        news_individuals = []

        if elitism > 0:
            n_elitism = int(np.ceil(self.n_individuals*elitism))
            array_fitness = np.repeat(None, self.n_individuals)
            for i in np.arange(self.n_individuals):
                array_fitness[i] = copy.copy(self.individuals[i].fitness)
            rank = np.flip(np.argsort(array_fitness))
            elite = [copy.deepcopy(self.individuals[i]) for i in rank[:n_elitism]]
            news_individuals = news_individuals + elite
        else:
            n_elitism = 0
            
        for i in np.arange(self.n_individuals-n_elitism):
            # select parents
            index_parents = self.select_individual(
                                    n                = 2,
                                    return_indexs   = True,
                                    method_selection = method_selection)
            
            offspring = self.cross_individuals(
                            parental_1=index_parents[0],
                            parental_2=index_parents[1])
            
            offspring.mutate(
                prob_mut=prob_mut,
                distribution=distribution,
                min_distribution=min_distribution,
                max_distribution=max_distribution)

            news_individuals = news_individuals + [offspring]

        self.individuals = copy.deepcopy(news_individuals)
        self.best_individual = None
        self.best_fitness = None
        self.best_value_variables = None
        self.best_function_value = None
        
        # New generation created! Known number of new individuals.

    def optimize(self, target_function, optimization, n_generations = 50,
                  method_selection="tournament", elitism=0.1, prob_mut=0.01,
                  distribution="uniform", media_distribution=1,
                  sd_distribution=1, min_distribution=-1, max_distribution=1,
                  stopping_early=False, rounds_stopping=3,
                  tolerance_stopping=0.1, outputname="geneticOutput"):


        if stopping_early and (rounds_stopping is None or tolerance_stopping is None):
            raise Exception("To activate Stopping early it is necessary to indicate a",
                            "value of rounds_stopping and tolerance_stopping.")

        start = time.time()

        f = open("{}.txt".format(outputname), "+w")
        f.write("# Generation, best_fitness\n")
        for i in np.arange(n_generations):

            self.evaluar_population(
                target_function=target_function,
                optimization=optimization)

            self.historical_individuals.append(copy.deepcopy(self.individuals))
            self.historical_best_fitness.append(copy.deepcopy(self.best_fitness))
            self.historical_best_value_variables.append(
                                    copy.deepcopy(self.best_value_variables)
                                )
            self.historical_best_function_value.append(
                                    copy.deepcopy(self.best_function_value)
                                )

            if i == 0:
                self.difference_abs.append(None)
            else:
                difference = abs(self.historical_best_fitness[i] \
                                 - self.historical_best_fitness[i-1])
                self.difference_abs.append(difference)
            f.write(" {} {} \n".format(i, self.best_fitness))
            sys.stdout.write("\r{}it | best fitness: {:.4f} | best individual: {}".format(i, self.best_fitness, self.best_value_variables))
            sys.stdout.flush()
            if stopping_early and i > rounds_stopping:
                latest_n = np.array(self.difference_abs[-(rounds_stopping):])
                if all(latest_n < tolerance_stopping):
                    print("Algorithm stopped in the {} generation"
                          "for lack of absolute minimum change of {}"
                          "while {} consecutive generations".format(i, tolerance_stopping,
                                                                    rounds_stopping))

                    break
                   
            self.create_new_generation(
                method_selection=method_selection,
                elitism=elitism,
                prob_mut=prob_mut,
                distribution=distribution)

        f.close()
        end = time.time()
        self.optimized = True
        self.iter_optimization = i
        
        index_value_optimal  = np.argmax(np.array(self.historical_best_fitness))
        self.fitness_optimal  = self.historical_best_fitness[index_value_optimal]
        self.function_value_optimal = self\
                                    .historical_best_function_value[index_value_optimal]
        self.value_variables_optimal = self\
                                      .historical_best_value_variables[index_value_optimal]
        
        self.results_df = pd.DataFrame(
            {
            "best_fitness"        : self.historical_best_fitness,
            "best_function_value"  : self.historical_best_fitness,
            "best_value_variables": self.historical_best_value_variables,
            "difference_abs"       : self.difference_abs
            }
        )
        self.results_df["generation"] = self.results_df.index
        print("\n\nSummary:\n--------")
        print("Optimization duration: {}".format(end - start))
        print("Number of generations: {}".format(self.iter_optimization+1))
        print("Optimal value of variables: {}".format(self.value_variables_optimal))
        print("Target function value: {}".format(self.function_value_optimal))
        file = open("{}_Summary.txt".format(outputname), "+w")
        file.write("Optimization duration: {}\n".format(end - start))
        file.write("Number of generations: {}\n".format(self.iter_optimization+1))
        file.write("Optimal value of variables: {}\n".format(self.value_variables_optimal))
        file.write("Target function value: {}\n".format(self.function_value_optimal))
        file.close()
