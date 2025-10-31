# EconCS Pset6 Programming Writeup

## 3. Experimental Analysis
To answer the following questions, run the simulation with 5 agents. By default the budget is \$5000, which is not binding. Leave it this way!

### 3(a) Truthful vs. Balanced Bidding Populations
Over 500 iterations, seed = 2, default settings  
Mean utility for each of five truthful agents: \$334.652, std: \$12.625  
Mean utility for each of five balanced-bidding (BB) agents: \$571.12, std: \$28.136  

Balanced bidding agents are more successful than truthful agents, which aligns with the textbook’s description and proof that balanced bidding is an envy-free Nash equilibrium while truthful bidding is not. Put differently, a truthful agent can profitably shave its bid and keep the same slot, but a balanced bidder already sits at a point where any deviation invites retaliation. The empirical gap in total costs mirrors that logic: balanced bidders pay far less for the same clicks.

### 3(b) Mixed Populations
Command template: `python auction.py --perms 10 --iters 200 Truthful,4 abxybb,1`

Over 500 iterations, seed = 2, default settings, 4 truthful + 1 balanced bidder  
Mean for truthful bidders: \$370.690, std: \$20.700  
Mean for balanced bidder: \$465.08  

Over 500 iterations, seed = 2, default settings, 1 truthful + 4 balanced bidders  
Mean for truthful bidder: \$651.77  
Mean for balanced bidders: \$566.2625, std: \$17.622  

These runs suggest a balanced bidder dominates truthful play in a population of naive agents, while a truthful bidder can still do well when everyone else is balanced. The tension with the theoretical envy-free equilibrium hints that our implementation may deviate from the textbook construction.

## 4. Experiments with Revenue: GSP vs. VCG

### 4(b) GSP Revenue with Balanced Bidders
What is the auctioneer’s revenue under GSP with no reserve price when all the agents use the balanced-bidding strategy? What happens as the reserve price increases? What is the revenue-optimal reserve price?

> Budget default was 5000.00

$$ b_i^{t*} = v_i - \frac{\text{pos}_{j^*}}{\text{pos}_{j^*-1}}\left(v_i - \text{price}_{j^*}\right) $$

Default settings: Budget = 500000 (not limiting)  
500 iterations, seed = 199, 5 BB agents  
No reserve price: Average daily revenue \$4978.88 (std \$1309.84)  
Reserve 10: \$4978.88 (std \$1309.84) — bids all above the reserve  
Reserve 15: \$5030.50 (std \$1316.45)  
Reserve 20: \$4952.17 (std \$1322.60)  
Reserve 30: \$5098.51 (std \$1273.24)  
Reserve 35: \$5136.70 (std \$1404.82)  
Reserve 40: \$5236.85 (std \$1379.90)  
Reserve 50: \$5289.07 (std \$1268.18)  
**Reserve 70: \$5446.51 (std \$1469.04)**  
Reserve 80: \$5440.12 (std \$1645.94)  
Reserve 90: \$5278.75 (std \$1781.30)  
Reserve 100: \$5227.75 (std \$1955.07)  
Reserve 113: \$5015.08 (std \$2265.56)  
Reserve 125: \$4226.97 (std \$2374.59)  
Reserve 150: \$2953.42 (std \$2490.68)  

Revenue rises with the reserve up to roughly 70 cents and then falls as the reserve excludes too many bidders. This makes sense because valuations are drawn uniformly from [25, 175]; a 70-cent reserve trims the lowest 30% of bids while still selling the available slots most days.

### 4(c) VCG Revenue with Truthful Agents
Command template: `python auction.py --seed 199 --iters 500 --perms 1 --reserve <value> --mech VCG Ischesbb,5`

No reserve: \$4062.71 (std \$1289.80)  
Reserve 20: \$4031.61 (std \$1277.60)  
Reserve 40: \$4260.62 (std \$1257.72)  
Reserve 70: \$4714.31 (std \$1213.85)  
Reserve 90: \$4792.52 (std \$1513.66)  
Reserve 95: \$4772.53 (std \$1500.13)  
**Reserve 100: \$4840.97 (std \$1716.15)**  
Reserve 105: \$4828.93 (std \$1878.53)  
Reserve 110: \$4600.44 (std \$2070.89)  
Reserve 120: \$4393.43 (std \$2076.87)  
Reserve 150: \$2927.09 (std \$2449.50)  

VCG yields slightly lower revenue than GSP at low reserves because payments match the precise externality, but it tolerates higher reserves without destabilizing bidding. The revenue peak shifts upward (about 110 cents) since truthful bids allow the platform to push the reserve until only high-value clicks remain.

### 4(d) Switching Midstream
Command: `python auction.py --loglevel WARNING --perms 1 --iters 200 --seed 199 --mech switch Ischesbb,5`

Keeping all agents balanced, average daily revenue drops from \$4468.76 under pure GSP (reserve 0) to \$4052.16 when the platform switches to VCG at round 24. Once VCG kicks in, bids fall to truthful levels and the higher slots stop paying second-price premiums, so the short-run revenue dip is immediate even though allocation efficiency rises.

### 4(e) Takeaways
A simple reserve can substantially increase GSP revenue, but only up to the point where it begins to exclude too many bidders; beyond that the revenue drops as slots go unsold. VCG handles more aggressive reserves because truthful bidding curbs strategic underbidding, yet the platform receives slightly lower payments when the reserve is low. Balanced bidding emerges as a robust best-response heuristic: it raises individual agent utility while tightening competition around the marginal slot and thus boosting GSP revenue. Finally, mechanism changes matter in the short run since switching from GSP to VCG without retuning reserves can reduce platform income immediately even if overall welfare improves.

## 5. Budget Constraints

### 5(a) Competition Agent (`ischesbudget.py`)
Our `Ischesbudget` client starts from the balanced bidding playbook and adds pacing. It reads historical clicks and bid ranges to compute the balanced best response for each slot, compares the cumulative spend stored in `history.agents_spent` with the remaining budget, and divides by the periods left in the 48-step day to derive an allowable spend per round. Whenever the projected cost of a slot exceeds that allowance, the utility estimate is dampened so the agent drifts toward cheaper slots. The final bid scales the balanced bid toward the reserve, ensuring that expected spend tracks the pacing target without ever exceeding the per-click value. This keeps the agent aggressive early on and automatically throttles bids once the budget becomes binding, avoiding the catastrophic zero bids that strike a pure balanced bidder after it exhausts the budget mid-day.
