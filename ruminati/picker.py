from datetime import timedelta

from flask import Blueprint, render_template, current_app, request
from pymaybe import maybe, Nothing

from ruminati.models import Breakout, Lapse

blueprint = Blueprint("picker", __name__)


def quantize(begin, end, subdiv, breakouts):
    lapse = Lapse(begin, timedelta(hours=1) / subdiv)
    results = []
    iterator = iter(breakouts)
    repeat = 0
    try:
        breakout = next(iterator)
        while lapse.precedes(end):
            if lapse.precedes(breakout.start_at):
                repeat = 0
                results.append((lapse.start_at, Nothing(), repeat))
            elif breakout.lapse.contains(lapse):
                results.append((lapse.start_at, maybe(breakout), repeat))
                repeat += 1
            else:
                repeat = 0
                breakout = next(iterator)
                continue
            lapse.increment()
    except StopIteration:
        while lapse.precedes(end):
            results.append((lapse.start_at, Nothing(), repeat))
            lapse.increment()
    finally:
        return results


def occurrences(this_breakout, schedule):
    if this_breakout.is_none():
        return 1
    count = 0
    for dt, that_breakout, repeat in schedule:
        if that_breakout.is_some():
            if this_breakout.get() is that_breakout.get():
                count += 1
    return count


def calculate_runs(schedule):
    results = []
    for dt, breakout, repeat in schedule:
        results.append((dt, breakout, repeat, occurrences(breakout, schedule)))
    return results


@blueprint.route("/picker")
def display_picker():
    config = current_app.config
    breakouts = (request.db_sess.query(Breakout)
                 .order_by(Breakout.start_at).all())
    schedule = quantize(config["BRKBEG"], config["BRKEND"], config["SUBDIV"],
                        breakouts)
    schedule_with_runs = calculate_runs(schedule)
    return render_template("picker.html", schedule=schedule_with_runs)
