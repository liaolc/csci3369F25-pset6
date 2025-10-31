3. [20 Points] Experimental Analysis
To answer the following questions, run the simulation with 5 agents. By default
the budget is $5000, which is not binding. Leave it this way!
(a) [10 Points] What is the average utility of a population of truthful agents? What is the
average utility of a population of balanced bidding agents? Compare the two cases and
explain your findings.
Make use of the --perms, --seed, and --iters commands, e.g. --perms 1 --seed 2
--iters 200 would be a good starting point.

A: 
Over 500 iterations, seed=2, default settings
Mean utility for each of five truthful agents: $334.652$, std: $12.625$
Mean Utility for each of five BB Agents:  571.12, std: 28.136

Balanced Bidding agents are more successful than truthful agents, which aligns with the textbook's description and proof that Balanced Bidding is an Envy Free Nash Equilibrium, while Truthful bidding is not. A quick way to see this is that in truthful bidding, an agent could deviate to bid lower than their true value while still retaining the same position. In Balanced Bidding, agents already bid the lowest possible such that no other agent can deviate (retaliate). This is also shown empirically by BB Agents having much lower total costs than Truthful agents.


(b) [10 Points] In addition, what is the average utility of one balanced-bidding agent against
4 truthful agents, and one truthful agent against 4 balanced-bidding agents? For the
new experiment, make use of the --seed, and --iters commands, but you will now
want to run multiple permutations. Note that you can add multiple agents types using:
> python auction.py --perms 10 --iters 200 Truthful,4 abxybb,1
What does this suggest about the incentives to follow the truthful vs. the balanced bidding
strategy?

Over 500 iterations, seed=2, default settings, 4 Truthful + 1 Balanced Bidder
Mean for truthful bidders:  370.690, std:  20.700
Mean for Balanced bidder: 465.08

Over 500 iterations, seed=2, default settings, 1 Truthful + 4 Balanced Bidder
Mean for truthful bidder:  651.77
Mean for Balanced bidders:  566.2625, std: 17.622

This shows being a balanced bidder is better when there are many truthful bidders, but being a truthful bidder is better when there are many balanced bidders. This seems to contradict Balanced Bidding being an Envy Free Nash Equilibrium, which likely means our implementation of balanced bidding doesn't match the theoretical EFNE.

2 (b)
What is the auctioneer’s revenue under GSP with no reserve price when
all the agents use the balanced-bidding strategy? What happens as the reserve price
increases? What is the revenue-optimal reserve price?

> Budget default was 5000.00

$$
b_i^{t*} = v_i - (pos_{j*}/pos_{j*}-1)(v_i - price_{j*})
$$

Default settings: Budget = 500000 (not limiting)
500 iters, default settings, 5 BBAgents, seed=199
No reserve price Average daily revenue (stddev): $4978.88 ($1309.84)
reserve price: 10, Average daily revenue (stddev): $4978.88 ($1309.84) -- I think all bids > reserve price, so it didn't affect it
Resreve price: 15, Average daily revenue (stddev): $5030.50 ($1316.45)
Reserve price: 20, Average daily revenue (stddev): $4952.17 ($1322.60)
Reserve price: 30, Average daily revenue (stddev): $5098.51 ($1273.24)
Reserve price: 35, Average daily revenue (stddev): $5136.70 ($1404.82)
Reserve price: 40, Average daily revenue (stddev): $5236.85 ($1379.90)
Reserve price: 50, Average daily revenue (stddev): $5289.07 ($1268.18)
**Reserve price: 70, Average daily revenue (stddev): $5446.51 ($1469.04)**
Reserve price: 80, Average daily revenue (stddev): $5440.12 ($1645.94)
Reserve price: 90, Average daily revenue (stddev): $5278.75 ($1781.30)
Reserve price: 100, Average daily revenue (stddev): $5227.75 ($1955.07)
Reserve price: 113, Average daily revenue (stddev): $5015.08 ($2265.56)
Reserve price: 125, Average daily revenue (stddev): $4226.97 ($2374.59)
Reserve price: 150, Average daily revenue (stddev): $2953.42 ($2490.68)

It seems reserve prices cause an increase in revenue up to an optimal point of about 70, then revenue falls off after that when agents have no budget. This reflects the fact that values are drawn from \[25, 175\] uniformly each day, so we expect 70 to remove the bottom 30% of bids, which is just enough to still preserve all slots being sold on most bids. 

---

4 (c)

VCG
python auction.py --seed 199 --iters 500 --perms 1  --reserve 100 --mech VCG Ischesbb,5
No RP: Average daily revenue (stddev): $4062.71 ($1289.80)
RP 20: Average daily revenue (stddev): $4031.61 ($1277.60)
RP 40: Average daily revenue (stddev): $4260.62 ($1257.72)
RP 70: age daily revenue (stddev): $4714.31 ($1213.85)
RP 90: Average daily revenue (stddev): $4792.52 ($1513.66)
RP 95: Average daily revenue (stddev): $4772.53 ($1500.13)
**RP 100: Average daily revenue (stddev): $4840.97 ($1716.15)**
RP 105: Average daily revenue (stddev): $4828.93 ($1878.53)
RP 110: Average daily revenue (stddev): $4600.44 ($2070.89)
RP 120: Average daily revenue (stddev): $4393.43 ($2076.87)
RP 150: Average daily revenue (stddev): $2927.09 ($2449.50)

