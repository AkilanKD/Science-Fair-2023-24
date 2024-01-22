# Science-Fair-2023-24
This project is the source code for my science fair project. It creates 8 poker bots which follow different preflop strategies. Each strategy has two bots each. These bots then play Hold'Em games against each other in as many rounds as specified rounds. The results of each game is storied in RESULTS.csv.
Each row represents a single bot. The first column holds its strategy, the second row holds its net profit or loss, the third row holds whether it won, represented as a decimal (1 = win, 0.5 = split win with another AI, 0 = loss), and the fourth row holds its position (0 = small blind, 1 = big blind, 2 = under the gun, and so on).

Thanks to @HenryRLee for the library PH Evaluator. Source code can be found here: https://github.com/HenryRLee/PokerHandEvaluator. It is licensed under the Apache License, a copy of which is attached to this project.

Thanks to @elleklinton for the library Pied Poker. Source code can be found here: https://github.com/elleklinton/PiedPoker.

Thanks to John La Rooy from Stack Overflow for his line of code to sort 2D arrays based on a specific column: https://stackoverflow.com/a/4174955.

Thanks to Match Poker Online for their preflop hand cart, which PREFLOP-RANGES.csv is based on: https://matchpoker.com/learn/strategy-guides/pre-flop-ranges-8-max.
