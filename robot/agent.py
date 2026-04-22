import random
from config import ALPHA

def make_bid(robot):
    return robot.load + ALPHA * random.random()

def run_auction(robots):
    bids = {}

    for r in robots:
        if r.status != "FAILED":
            bids[r.id] = make_bid(r)

    if not bids:
        return None, bids

    winner = min(bids, key=lambda x: (bids[x], x))
    return winner, bids