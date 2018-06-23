from datetime import timedelta
from unittest import TestCase

from dateutil.tz import gettz

from ruminati.models import Breakout
from ruminati.picker import quantize
from ruminati.utils import parse_aware_datetime, parse_to_utc

NY = gettz("America/New_York")

BRKBEG = parse_aware_datetime("08:00 AM", NY)
BRKEND = parse_aware_datetime("05:00 PM", NY)
SUBDIV = 2


class TestLayout(TestCase):
    data = [Breakout(start_at=parse_aware_datetime("09:00 AM", NY), duration=timedelta(hours=1)),
            Breakout(start_at=parse_aware_datetime("11:00 AM", NY), duration=timedelta(hours=1)),
            Breakout(start_at=parse_aware_datetime("01:00 PM", NY), duration=timedelta(hours=1))]

    def test_correct_number_of_rows(self):
        """
        A conference running from 8 to 5 is nine hours long. Each hour has
        two subdivisions, so there should be 18 rows in the result.
        """
        rows = quantize(BRKBEG, BRKEND, SUBDIV, self.data)
        self.assertEqual(len(rows), 18)

    def test_correct_number_of_breakouts(self):
        rows = quantize(BRKBEG, BRKEND, SUBDIV, self.data)
        self.assertEqual(sum(1 if breakout.is_some() else 0
                             for dt, breakout, repeat in rows), 6)

    def test_all_rows_nothing(self):
        """
        When there are no breakouts, all rows should be Nothing.
        """
        rows = quantize(BRKBEG, BRKEND, SUBDIV, [])
        for dt, breakout, repeat in rows:
            self.assertTrue(breakout.is_none())
