3. [20 Points] Experimental Analysis
To answer the following questions, run the simulation with 5 agents. By default
the budget is $5000, which is not binding. Leave it this way!
(a) [10 Points] What is the average utility of a population of truthful agents? What is the
average utility of a population of balanced bidding agents? Compare the two cases and
explain your findings.
Make use of the --perms, --seed, and --iters commands, e.g. --perms 1 --seed 2
--iters 200 would be a good starting point.

3a: 
Over 500 iterations, seed=2, default settings
Mean utility for each of five truthful agents: $334.652$, std: $12.625$
Mean Utility for each of five BB Agents:  571.12, std: 28.136

Balanced bidding agents are more successful than truthful agents, which aligns with the textbook’s description and proof that balanced bidding is an envy-free Nash equilibrium while truthful bidding is not. Put differently, a truthful agent can profitably shave its bid and keep the same slot, but a balanced bidder already sits at a point where any deviation invites retaliation. The empirical gap in total costs mirrors that logic: balanced bidders pay far less for the same clicks.


3(b) [10 Points] In addition, what is the average utility of one balanced-bidding agent against
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

These runs suggest a balanced bidder dominates truthful play in a population of naive agents, while a truthful bidder can still do well when everyone else is balanced. The tension with the theoretical envy-free equilibrium hints that our implementation may deviate from the textbook construction.

4 (b)
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

---

#### 4(d) Switching midstream  
`python auction.py --loglevel WARNING --perms 1 --iters 200 --seed 199 --mech switch Ischesbb,5`

Keeping all agents balanced, average daily revenue drops from \$4468.76 under pure GSP (reserve 0) to \$4052.16 when the platform switches to VCG at round 24. Once VCG kicks in, bids fall to truthful levels and the higher slots stop paying second-price premiums, so the short-run revenue dip is immediate even though allocation efficiency rises

A simple reserve can substantially increase GSP revenue, but only up to the point where it begins to exclude too many bidders from the market; beyond that the revenue falls as slots go unsold. VCG tolerates more aggressive reserves because truthful bidding prevents the strategic underbidding that GSP invites, though the platform may collect slightly lower payments when the reserve is low. Balanced bidding emerges as a robust best‑response heuristic: it raises individual agent utility while tightening competition around the marginal slot and thus boosting GSP revenue. Finally, mechanism changes matter in the short run since switching from GSP to VCG without retuning reserves can reduce platform income immediately even if overall welfare improves.  


### 5. Budget Constraints
#### (a) Competition agent (`ischesbudget.py`)
Our `Ischesbudget` client starts from the balanced bidding playbook and adds pacing. It reads historical clicks and bid ranges to compute the balanced best response for each slot, compares the cumulative spend stored in `history.agents_spent` with the remaining budget, and divides by the periods left in the 48-step day to derive an allowable spend per round. Whenever the projected cost of a slot exceeds that allowance, the utility estimate is dampened so the agent drifts toward cheaper slots. The final bid scales the balanced bid toward the reserve, ensuring that expected spend tracks the pacing target without ever exceeding the per-click value. This keeps the agent aggressive early on and automatically throttles bids once the budget becomes binding, avoiding the catastrophic zero bids that strike a pure balanced bidder after it exhausts the budget mid-day.




