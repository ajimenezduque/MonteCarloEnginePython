from abc import ABC, abstractmethod
import math
import MonteCarlo

class Option(ABC):
    """
    Option Interface
    """

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def add(self, component):
        pass

    def remove(self, component):
        pass

    def is_composite(self):

        return False

    @abstractmethod
    def evaluate(self):
        """
        """

        pass

    @abstractmethod
    def getExpiry(self):
        pass


class Call(Option):
    """
    Option Call
    """

    def __init__(self, signo, interest, strike, spot, vol, tau):
        self.signo = signo
        self.interest = interest
        self.strike = strike
        self.spot = spot
        self.vol = vol
        self.tau = tau
        self.discount_factor = math.exp(-interest * tau)
        self.forward = spot / self.discount_factor

    def evaluate(self, values, criteria):
        idx = self.tau * criteria
        prices = {self.tau: self.signo * max(values[int(idx)] - self.strike, 0.0)}
        return prices

    def getExpiry(self):
        return self.tau


class Composite(Option):
    """
    The Composite class it represents a portfolio of options
    """

    def __init__(self):
        # List of Options
        self._children = []

    def add(self, component):
        self._children.append(component)
        component.parent = self

    def remove(self, component):
        self._children.remove(component)
        component.parent = None

    def is_composite(self):
        return True

    def evaluate(self, values, criteria):
        """
        The Composite iterative evaluate
        """

        valuation = {}
        for child in self._children:
            result_element = child.evaluate(values, criteria)
            for key, value in result_element.items():
                if valuation.get(key) is None:
                    valuation[key] = value
                else:
                    suma = valuation[key] + value
                    valuation[key] = suma
        return valuation

    def getExpiry(self):
        maxExpiry = 0.0
        for child in self._children:
            maxExpiry = max(maxExpiry, child.getExpiry())
        return maxExpiry



if __name__ == "__main__":
    spot = 305.0
    optionCall = Call(signo=1, interest=0.08, spot=305.0, strike=300.0, vol=0.25, tau=4.0 / 12.0)
    vol = 0.25
    volatility_map = {}
    volatility_map[0.1] = 0.25;
    volatility_map[0.2] = 0.30;
    volatility_map[0.3] = 0.33;
    volatility_map[0.4] = 0.35;
    composite = Composite()
    composite.add(optionCall)

    valuation = MonteCarlo.MonteCarloEngine.pricing(composite,
                                                    spot=spot,
                                                    volatility_map=volatility_map,
                                                    interest=0.08,
                                                    paths=10000, samples=365)

    print("Valuation ", valuation)


    optionCall2 = Call(signo=1, interest=0.08, spot=305, strike=309, vol=0.25, tau=6.0 / 12.0)
    valuation = MonteCarlo.MonteCarloEngine.pricing(optionCall2, spot=305, volatility_map=volatility_map, interest=0.08,
                                                    paths=10000, samples=365)
    print("Call2 ", valuation)
    composite = Composite()
    composite.add(optionCall)
    composite.add(optionCall2)

    valuation = MonteCarlo.MonteCarloEngine.pricing(composite, spot=305, volatility_map=volatility_map, interest=0.08,
                                                    paths=10000, samples=365)

    print("Composite ", valuation)