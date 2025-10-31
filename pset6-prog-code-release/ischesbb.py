#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index

class Ischesbb:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = list(map(compute, list(range(len(clicks)))))
#        sys.stdout.write("slot info: %s\n" % info)
        return info


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        last_round = history.round(t-1)
        utilities = [0] * len(last_round.slot_payments)  
        if t > 0:
            if last_round.bids[0][1] < reserve:
                utilities = [0.0001] # util.py has a bug -- if no max, throws exception
                return utilities
            try:
                my_slot = last_round.occupants.index(self.id)
            except ValueError: 
                my_slot = -1
            if my_slot >= 0:
                my_id, my_bid = last_round.bids[my_slot]
            else:
                my_bid = 0
            for i in range(len(last_round.slot_payments)):
            
                # BIDS IS SORTED ALREADY!!!
            
                    # occupant = last_round.occupants[i]-1 # assume agent's name from 1,..,N
                agentid, next_highest_bid = last_round.bids[i] # = original first price
                if my_bid >= next_highest_bid: # I won, pay original
                    next_highest_bid = last_round.per_click_payments[i]
                
                #print(f"my value: {self.value}, clicks for slot {i}: {last_round.clicks[i]}, winning bid: {next_highest_bid}")
                utilities[i] =  last_round.clicks[i]*(self.value - max(reserve, next_highest_bid))
                #print(f"utility computed: {utilities[i]}")
        # else: 
        #     utilities = [reserve] * len(last_round.slot_payments)  
        
        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)
       
        # TODO: Fill this in.
        bid = 0
        if slot == 0 or min_bid > self.value:
            bid = self.value 
        else: # b_i^t* = v_i - (pos_j*/pos_j*-1)(v_i - price_j*)
            pos_estimate_j = prev_round.clicks[slot] / prev_round.clicks[0] 
            # pos_j*-1
            pos_estimate_before_j =  prev_round.clicks[slot-1] / prev_round.clicks[0]
            bid = self.value - ((pos_estimate_j/pos_estimate_before_j) * (self.value - min_bid))
        
        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


