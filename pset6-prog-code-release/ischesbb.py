#!/usr/bin/env python

from gsp import GSP
from util import argmax_index

class Ischesbb:
    """Balanced bidding agent following the envy-free best response rule."""

    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2.0

    def slot_info(self, t, history, reserve):
        """Return the (slot, min_bid, max_bid) information for each slot."""
        prev_round = history.round(t - 1)
        other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]

        clicks = prev_round.clicks

        def compute(slot):
            (min_bid, max_bid) = GSP.bid_range_for_slot(slot, clicks, reserve, other_bids)
            if max_bid is None:
                max_bid = 2 * min_bid
            return (slot, min_bid, max_bid)

        return list(map(compute, range(len(clicks))))

    def expected_utils(self, t, history, reserve):
        """Expected utility obtained from targeting each slot."""
        if t <= 0:
            return []

        prev_round = history.round(t - 1)
        clicks = prev_round.clicks
        slot_details = self.slot_info(t, history, reserve)

        utilities = []
        for slot, min_bid, _ in slot_details:
            price = max(reserve, min_bid)
            utilities.append(clicks[slot] * (self.value - price))
        return utilities

    def target_slot(self, t, history, reserve):
        """Return the slot tuple that maximizes expected utility."""
        slot_idx = argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[slot_idx]

    def bid(self, t, history, reserve):
        """
        Balanced bidding update rule:
            clicks_j*(v - price_j) = clicks_{j-1}*(v - bid)
        with the convention that the top slot bids its value.
        """
        if t <= 0:
            return self.initial_bid(reserve)

        prev_round = history.round(t - 1)
        slot, min_bid, _ = self.target_slot(t, history, reserve)
        target_price = max(reserve, min_bid)

        if slot == 0 or target_price >= self.value:
            return float(self.value)

        clicks = prev_round.clicks
        clicks_current = clicks[slot]
        clicks_above = clicks[slot - 1] if slot > 0 else clicks[slot]

        if clicks_above == 0:
            return float(self.value)

        adjustment = (clicks_current / float(clicks_above)) * (self.value - target_price)
        bid = self.value - adjustment
        bid = min(self.value, bid)
        bid = max(reserve, bid)
        return float(bid)

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (self.__class__.__name__, self.id, self.value)


BBAgent = Ischesbb

