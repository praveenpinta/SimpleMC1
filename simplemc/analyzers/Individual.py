import numpy as np
import random
import warnings


class Individual:
    def __init__(self, n_variables, lower_bounds=None, upper_bounds=None):
        """
        This class generates the individuals within the bounds of the parameter space.

        Parameters
        -----------
        n_variables : int
            Number of variables or free parameters

        lower_bounds : list
            List with the lower bounds
        """
        self.n_variables = n_variables
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
        self.value_variables = np.repeat(None, n_variables)
        self.fitness = None
        self.function_value = None

        if self.lower_bounds is not None and not isinstance(self.lower_bounds, np.ndarray):
            self.lower_bounds = np.array(self.lower_bounds)

        if self.upper_bounds is not None \
                and not isinstance(self.upper_bounds, np.ndarray):
            self.upper_bounds = np.array(self.upper_bounds)

        if self.lower_bounds is not None and len(self.lower_bounds) != self.n_variables:
            raise Exception(
                "lower_bounds must have a value for each variable." +
                "If you do not want to limit any variable, use None." +
                "Ex: lower_bounds = [10, None, 5]"
            )
        elif self.upper_bounds is not None \
                and len(self.upper_bounds) != self.n_variables:
            raise Exception(
                "upper_bounds must have a value for each variable." +
                "If you do not want to limit any variable, use None." +
                "Ex: lower_bounds = [10, None, 5]"
            )
        elif (self.lower_bounds is None) or (self.upper_bounds is None):
            warnings.warn(
                "It is highly recommended to indicate" +
                " the bounds within which the solution of each variable." +
                "By default: [-10^3, 10^3]."
            )
        elif any(np.concatenate((self.lower_bounds, self.upper_bounds)) == None):
            warnings.warn(
                "By default the bounds are: [-10^3, 10^3]."
            )

        if self.lower_bounds is None:
            self.lower_bounds = np.repeat(-10 ** 3, self.n_variables)

        if self.upper_bounds is None:
            self.upper_bounds = np.repeat(+10 ** 3, self.n_variables)

        if self.lower_bounds is not None:
            self.lower_bounds[self.lower_bounds == None] = -10 ** 3

        if self.upper_bounds is not None:
            self.upper_bounds[self.upper_bounds == None] = +10 ** 3

        for i in np.arange(self.n_variables):
            self.value_variables[i] = random.uniform(
                self.lower_bounds[i],
                self.upper_bounds[i]
            )

    def calculate_fitness(self, target_function, optimization):
        if not optimization in ["maximize", "minimize"]:
            raise Exception(
                "Arg should be: 'maximize' or 'minimize'"
            )

        self.function_value = target_function(*self.value_variables)
        if optimization == "maximize":
            self.fitness = self.function_value
        elif optimization == "minimize":
            self.fitness = -self.function_value

    def mutate(self, prob_mut=0.01, distribution="uniform", media_distribution=1,
              sd_distribution=1, min_distribution=-1, max_distribution=1):
        if not distribution in ["normal", "uniform", "random"]:
            raise Exception(
                "Arg should be: 'normal', 'uniform' or 'random'"
            )

        pos_mutated = np.random.uniform(
            low=0,
            high=1,
            size=self.n_variables
        )
        pos_mutated = pos_mutated < prob_mut

        if distribution in ["normal", "uniform"]:
            if distribution == "normal":
                factor_mut = np.random.normal(
                    loc=media_distribution,
                    scale=sd_distribution,
                    size=np.sum(pos_mutated)
                )
            if distribution == "uniform":
                factor_mut = np.random.uniform(
                    low=min_distribution,
                    high=max_distribution,
                    size=np.sum(pos_mutated)
                )
            self.value_variables[pos_mutated] = \
                self.value_variables[pos_mutated] + factor_mut

            for i in np.flatnonzero(pos_mutated):
                if self.value_variables[i] < self.lower_bounds[i]:
                    self.value_variables[i] = self.lower_bounds[i]
                if self.value_variables[i] > self.upper_bounds[i]:
                    self.value_variables[i] = self.upper_bounds[i]

        if distribution == "random":
            for i in np.flatnonzero(pos_mutated):
                self.value_variables[i] = random.uniform(
                    self.lower_bounds[i],
                    self.upper_bounds[i]
                )

        self.fitness = None
        self.function_value = None

