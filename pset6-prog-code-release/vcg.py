#!/usr/bin/env python

import random

from gsp import GSP

class VCG:
    """
    Implements the Vickrey-Clarke-Groves mechanism for ad auctions.
    """
    @staticmethod
    def compute(slot_clicks, reserve, bids):
        """
        Given info about the setting (clicks for each slot, and reserve price),
        and bids (list of (id, bid) tuples), compute the following:
          allocation:  list of the occupant in each slot
              len(allocation) = min(len(bids), len(slot_clicks))
          per_click_payments: list of payments for each slot
              len(per_click_payments) = len(allocation)

        If any bids are below the reserve price, they are ignored.

        Returns a pair of lists (allocation, per_click_payments):
         - allocation is a list of the ids of the bidders in each slot
            (in order)
         - per_click_payments is the corresponding payments.
        """

        # The allocation is the same as GSP, so we filled that in for you...

        valid = lambda a_bid: a_bid[1] >= reserve
        valid_bids = list(filter(valid, bids))

        # shuffle first to make sure we don't have any bias for lower or
        # higher ids
        random.shuffle(valid_bids)
        valid_bids.sort(key=lambda b: b[1], reverse=True)

        num_slots = len(slot_clicks)
        allocated_bids = valid_bids[:num_slots]
        if len(allocated_bids) == 0:
            return ([], [])

        (allocation, just_bids) = list(zip(*allocated_bids))

        num_alloc = len(allocation)

        def next_price(idx):
            """Per-click price driven by the next highest bid or reserve."""
            if idx < num_alloc - 1:
                return max(reserve, just_bids[idx + 1])
            # Last allocated slot looks at the highest losing bid (if any).
            if len(valid_bids) > num_alloc:
                return max(reserve, valid_bids[num_alloc][1])
            return float(reserve)

        # Pre-compute payments recursively following the textbook formula.
        def total_payment(idx):
            if idx == num_alloc - 1:
                return slot_clicks[idx] * next_price(idx)

            payment_next = total_payment(idx + 1)
            price_component = next_price(idx)
            delta_clicks = slot_clicks[idx] - slot_clicks[idx + 1]
            return delta_clicks * price_component + payment_next

        totals = [total_payment(k) for k in range(num_alloc)]

        def norm(totals_list):
            """Normalize total payments by clicks, guarding against zero clicks."""
            result = []
            for total, clicks in zip(totals_list, slot_clicks):
                if clicks == 0:
                    result.append(0.0)
                else:
                    result.append(total / float(clicks))
            return result

        per_click_payments = norm(totals)

        return (list(allocation), per_click_payments)

    @staticmethod
    def bid_range_for_slot(slot, slot_clicks, reserve, bids):
        """
        Compute the range of bids that would result in the bidder ending up
        in slot, given that the other bidders submit bidders.
        Returns a tuple (min_bid, max_bid).
        If slot == 0, returns None for max_bid, since it's not well defined.
        """
        # Conveniently enough, bid ranges are the same for GSP and VCG:
        return GSP.bid_range_for_slot(slot, slot_clicks, reserve, bids)
