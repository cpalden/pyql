import  unittest

from quantlib.settings import Settings
from quantlib.quotes import SimpleQuote
from quantlib.termstructures.yields.api import FlatForward
from quantlib.termstructures.credit.api import FlatHazardRate
from quantlib.pricingengines.credit.api import MidPointCdsEngine
from quantlib.instruments.api import CreditDefaultSwap, Side
from quantlib.time.api import ( TARGET, today, Years, Schedule,
    Following, Quarterly, Rule, Actual360, Period )
import math


class CreditDefaultSwapTest(unittest.TestCase):
    calendar = TARGET()
    today_date = today()

    Settings().evaluation_date = today_date

    hazard_rate = SimpleQuote(0.01234)
    probability_curve = FlatHazardRate(0, calendar, hazard_rate, Actual360())
    discount_curve = FlatForward(today_date, 0.06, Actual360())
    issue_date  = today_date
    #calendar.advance(today_date, -1, Years)
    maturity = calendar.advance(issue_date, 10, Years)
    convention = Following
    schedule = Schedule(issue_date, maturity, Period("3M"), calendar, convention,
                            convention, Rule.TwentiethIMM)
    recovery_rate = 0.4
    engine = MidPointCdsEngine(probability_curve, recovery_rate, discount_curve, True)

    def test_fair_spread(self):
        fixed_rate = 0.001
        day_count = Actual360()
        notional = 10000

        cds = CreditDefaultSwap(Side.Seller, notional, fixed_rate, self.schedule,
                                self.convention, day_count, True, True)
        cds.set_pricing_engine(self.engine)

        fair_rate = cds.fair_spread
        fair_cds = CreditDefaultSwap(Side.Seller, notional, fair_rate, self.schedule,
                                     self.convention, day_count, True, True)
        fair_cds.set_pricing_engine(self.engine)

        self.assertAlmostEqual(fair_cds.npv, 0.)

    def test_fair_upfront(self):
        fixed_rate = 0.05
        upfront = 0.001
        day_count = Actual360()
        notional = 10000

        cds = CreditDefaultSwap.from_upfront(Side.Seller, notional, upfront, fixed_rate,
                                             self.schedule,
                                             self.convention, day_count, True, True)
        cds.set_pricing_engine(self.engine)

        fair_upfront = cds.fair_upfront
        fair_cds = CreditDefaultSwap.from_upfront(Side.Seller, notional, fair_upfront,
                                                  fixed_rate, self.schedule,
                                                  self.convention, day_count, True, True)
        fair_cds.set_pricing_engine(self.engine)

        self.assertAlmostEqual(fair_cds.npv, 0.)

        # same with null upfront
        upfront = 0.
        cds2 = CreditDefaultSwap.from_upfront(Side.Seller, notional, upfront,
                                              fixed_rate, self.schedule,
                                              self.convention, day_count, True, True)
        cds2.set_pricing_engine(self.engine)
        fair_upfront2 = cds.fair_upfront
        fair_cds2 = CreditDefaultSwap.from_upfront(Side.Seller, notional, fair_upfront,
                                                   fixed_rate, self.schedule,
                                                   self.convention, day_count, True, True)
        fair_cds2.set_pricing_engine(self.engine)
        self.assertAlmostEqual(fair_cds2.npv, 0.)

if __name__ == "__main__":
    unittest.main()
