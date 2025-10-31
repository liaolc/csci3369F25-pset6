#!/usr/bin/env python

from gsp import GSP
from util import argmax_index


class Ischesbudget:
    """Budget-aware bidding agent based on balanced bidding with pacing."""

    TOTAL_ROUNDS = 48  # Simulator runs 48 periods in a day.
    SPEND_BUFFER = 1.2  # Allow mild overspending relative to even pacing.

    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2.0

    # --- Helper routines mirroring the balanced bidder logic ---
    def slot_info(self, t, history, reserve):
        prev_round = history.round(t - 1)
        other_bids = [bid for bid in prev_round.bids if bid[0] != self.id]
        clicks = prev_round.clicks

        def compute(slot):
            (min_bid, max_bid) = GSP.bid_range_for_slot(slot, clicks, reserve, other_bids)
            if max_bid is None:
                max_bid = 2 * min_bid
            return (slot, min_bid, max_bid)

        return list(map(compute, range(len(clicks))))

    def _baseline_expected_utils(self, t, history, reserve):
        prev_round = history.round(t - 1)
        clicks = prev_round.clicks
        slot_details = self.slot_info(t, history, reserve)
        utilities = []
        for slot, min_bid, _ in slot_details:
            price = max(reserve, min_bid)
            utilities.append(clicks[slot] * (self.value - price))
        return utilities

    def expected_utils(self, t, history, reserve):
        """
        Budget-aware utilities: attenuate slots whose expected spend for the
        coming period would exceed the remaining per-period allowance.
        """
        if t <= 0:
            return []

        remaining_budget = max(0, self.budget - history.agents_spent[self.id])
        remaining_rounds = max(1, self.TOTAL_ROUNDS - t)
        allowance = (remaining_budget / float(remaining_rounds)) * self.SPEND_BUFFER

        prev_round = history.round(t - 1)
        clicks = prev_round.clicks
        slot_details = self.slot_info(t, history, reserve)

        utilities = []
        for slot, min_bid, _ in slot_details:
            price = max(reserve, min_bid)
            raw_util = clicks[slot] * (self.value - price)
            expected_cost = clicks[slot] * price
            if expected_cost <= 0:
                utilities.append(raw_util)
                continue
            pacing = min(1.0, allowance / float(expected_cost))
            utilities.append(raw_util * pacing)
        return utilities

    def target_slot(self, t, history, reserve):
        slot_idx = argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[slot_idx]

    def _balanced_bid(self, t, history, reserve, slot, min_bid):
        if t <= 0:
            return self.initial_bid(reserve)

        target_price = max(reserve, min_bid)
        if slot == 0 or target_price >= self.value:
            return float(self.value)

        prev_round = history.round(t - 1)
        clicks = prev_round.clicks
        clicks_current = clicks[slot]
        clicks_above = clicks[slot - 1] if slot > 0 else clicks_current
        if clicks_above == 0:
            return float(self.value)

        adjustment = (clicks_current / float(clicks_above)) * (self.value - target_price)
        bid = self.value - adjustment
        bid = min(self.value, bid)
        bid = max(reserve, bid)
        return float(bid)

    def bid(self, t, history, reserve):
        if t <= 0:
            return self.initial_bid(reserve)

        (slot, min_bid, _) = self.target_slot(t, history, reserve)
        target_price = max(reserve, min_bid)
        baseline_bid = self._balanced_bid(t, history, reserve, slot, min_bid)

        prev_round = history.round(t - 1)
        clicks = prev_round.clicks
        expected_cost = clicks[slot] * target_price

        spent = history.agents_spent[self.id]
        remaining_budget = max(0, self.budget - spent)
        if remaining_budget <= 0:
            return float(reserve)

        remaining_rounds = max(1, self.TOTAL_ROUNDS - t)
        allowance = (remaining_budget / float(remaining_rounds)) * self.SPEND_BUFFER

        if expected_cost <= 0:
            return baseline_bid

        pacing = min(1.0, allowance / float(expected_cost))
        scaled_bid = reserve + pacing * (baseline_bid - reserve)
        scaled_bid = max(reserve, min(self.value, scaled_bid))
        return float(scaled_bid)

    def __repr__(self):
        return "%s(id=%d, value=%d, budget=%d)" % (
            self.__class__.__name__, self.id, self.value, self.budget)


BudgetAgent = Ischesbudget
