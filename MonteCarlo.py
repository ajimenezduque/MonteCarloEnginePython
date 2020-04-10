import numpy as np
import math
from math import *
import random
from numpy.random import Generator, MT19937, SeedSequence
from numpy import random


def normpdf(x, mean, sd):
    var = float(sd) ** 2
    denom = (2 * math.pi * var) ** .5
    num = math.exp(-(float(x) - float(mean)) ** 2 / (2 * var))
    return num / denom


def phi(x):
    #'Cumulative distribution function for the standard normal distribution'
    return (1.0 + erf(x / sqrt(2.0))) / 2.0


class MonteCarloEngine:
    @staticmethod
    def pricing(portfolio, spot, volatility_map, interest, paths, samples):

        maxExpiry = portfolio.getExpiry()
        dt = maxExpiry / samples
        underlying_values = np.full(samples + 1, spot)
        running_sum = {}
        random.seed(1234)
        for i in range(paths):
            for j in range(1, len(underlying_values)):
                init_idx = dt * j
                keys = list(volatility_map.keys())
                if init_idx > keys[-1]:
                    init_idx = keys[-1]

                idx_volatility = np.searchsorted(keys, init_idx)
                vol = volatility_map[keys[idx_volatility]]
                variance = vol ** 2
                rootVariance = math.sqrt(variance * dt)
                movedSpotFactor = math.exp((interest - (0.5 * variance)) * dt)
                gaussian = random.normal(0, 1, 1)
                diffusion = math.exp(rootVariance * gaussian)
                # TODO shift array
                drift = underlying_values[j - 1] * movedSpotFactor
                underlying_values[j] = drift * diffusion

            payOff = portfolio.evaluate(underlying_values, samples / maxExpiry)
            for key, value in payOff.items():
                if running_sum.get(key) is None:
                    running_sum[key] = (math.exp(-interest * key) * value)
                else:
                    running_sum[key] += (math.exp(-interest * key) * value)
        value = 0.0
        for it in list(running_sum.values()):
            value += it

        return value / paths
