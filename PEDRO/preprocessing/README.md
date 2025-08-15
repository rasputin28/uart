Test Distance Unit	Diameter inches	Cruise	# Imanes o % velocidad	Bateria Volts	Gear	Status
1	Mi	8	No	30	48	2	Accelerating
2	Mi	8	No	30	48	1	Accelerating
3	Mi	10	Si	15	36	2	Idle
4	Mi	8	No	30	48	3	Accelerating
5	Km	8	Si	30	36	3	Idle
6	Km	10	No	15	48	1	Accelerating
7	Km	8	Si	30	36	2	Idle
8	Km	10	No	15	48	3	Accelerating
9	Km	8	Si	30	36	1	Idle
10	Km	10	No	15	48	2	Accelerating

We have run each test for 5 minutes to gather enough data

The baud rate selected is 16250, which is the most stable baud rate we found, close to 97% stability in non corrupted byte transmissions.

These are the 10 tests we ran for the pairwise analysis.

From here we can deduct the relevant bytes for each action.

Here are some preliminary assumptions (may be wrong):

Each packet starts with a 02

.....

On test number 8, speed oscillated mcuh between 56 and 57 km/h due to instability.