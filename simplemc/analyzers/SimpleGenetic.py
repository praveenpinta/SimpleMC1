from .Population import Population
from simplemc import logger
import sys

class SimpleGenetic:
    def __init__(self, target_function, n_variables, bounds, **kwargs):
        """
        SimpleGenetic use the optimization method from Population class and execute it.

        Parameters
        ----------
        target_function : method
            Usually the likelihood function.

        n_variables : int
            Number of variables or free parameters

        bounds : list
            List with upper and lower bounds for each free parameter

        n_individuals : int
            Number of initial individuals

        optimization : str
            Options {"maximize", "minimize"}. Default is "maximize"

        n_generations : int
            Number of generations to evolve the original population

        method_selection : str
            Type of selection method {"tournament", "rank", "roulette"}.
            Default: "tournament"

        elitism : float
            Value of elitism.
            Default: 0.01.

        prob_mut : float
            Probability of mutation.
            Default: 0.4

        distribution : str
            {"uniform", "gaussian", "random"}
            Default: uniform

        media_distribution : float

        sd_distribution : float

        min_distribution :

        max_distribution :

        stopping_early : bool


        rounds_stopping : int

        tolerance_stopping : float

        outputname : str
        """
        n_individuals = kwargs.pop("n_individuals", 50)
        optimization = kwargs.pop("optimization", "maximize")
        n_generations = kwargs.pop("n_generations", 250)
        method_selection = kwargs.pop("method_selection","tournament")
        elitism = kwargs.pop("elitism", 0.01)
        prob_mut = kwargs.pop("prob_mut", 0.4)
        distribution = kwargs.pop("distribution", "uniform")
        media_distribution = kwargs.pop("media_distribution", 1)
        sd_distribution = kwargs.pop("sd_distribution", 1)
        min_distribution = kwargs.pop("min_distribution", -1)
        max_distribution = kwargs.pop("max_distribution", 1)
        stopping_early = kwargs.pop("stopping_early", True)
        rounds_stopping = kwargs.pop("rounds_stopping", 500)
        tolerance_stopping = kwargs.pop("tolerance_stopping", 0.1)
        outputname = kwargs.pop("outputname", "geneticOutput")
        if kwargs:
            logger.critical('Unexpected **kwargs for SimpleGenetic: {}'.format(kwargs))
            sys.exit(1)
        self.target_function = target_function
        # These bounds are a list where every input is the limit of a param
        bounds = bounds

        self.lower_bounds = []
        self.upper_bounds = []

        for bound in bounds:
            self.lower_bounds.append(bound[0])
            self.upper_bounds.append(bound[1])

        self.n_individuals = n_individuals
        self.n_variables = n_variables
        
        self.distribution = distribution
        self.elitism = elitism
        self.max_distribution = max_distribution
        self.media_distribution = media_distribution
        self.method_selection = method_selection
        self.min_distribution = min_distribution
        self.n_generations = n_generations
        self.optimization = optimization
        self.stopping_early = stopping_early
        self.prob_mut = prob_mut
        self.rounds_stopping = rounds_stopping
        self.sd_distribution = sd_distribution
        self.tolerance_stopping  = tolerance_stopping
        self.outputname = outputname

        self.optimize()

    def optimize(self):
        population = Population(n_individuals=self.n_individuals,
                n_variables=self.n_variables,
                lower_bounds=self.lower_bounds,
                upper_bounds=self.upper_bounds)

        o = population.optimize(target_function=self.target_function,
                            optimization=self.optimization,
                            n_generations=self.n_generations,
                            method_selection=self.method_selection,
                            elitism=self.elitism,
                            prob_mut=self.prob_mut,
                            distribution=self.distribution,
                            media_distribution=self.media_distribution,
                            sd_distribution=self.sd_distribution,
                            min_distribution=self.min_distribution,
                            max_distribution=self.max_distribution,
                            stopping_early=self.stopping_early,
                            rounds_stopping=self.rounds_stopping,
                            outputname=self.outputname)
        return o