### Overview

This is the player profiler for the k9 chess playing robot dog. It finds the weakest spots in the openings repertoire of human players and exploits them remorselessly. The stronger the player, the bigger the effect.

It achieves this in the following way:
* it scans through historical games of the human player
* it builds up a tree structure capturing all opening moves
* it performs statistics on the player's result to find the opening where the player has, historically seen, the worst results.


### Using the profiler
The profiler can be used by the k9-profiler.py script. It offers options via the commandline. Use 'k9-profiler.py -h' to find out the different options.
The usual flow of using the profiler is:
1. Select a player and find out if the pgn files contains games of this player. This is done via the 'find' option of the profiler.
2. Create the player profile with the 'create' option of the profiler.
3. If wanted, inspect the profile in a visual way with the 'show_tree.html' command. You can have a look at the profile in an interactive way. Another way is to use the 'show_tree_force.html' command which delivers even nicer output.
4. Play against the profile with the 'play' option of the profiler. The profiler outputs a list of found moves and the results of the player against these moves. Select the move with the lowest score by the player. But of course, the player may have found an improvement already....

### Some details
Collections of chess games do not form a tree (where each node should have only 1 predecessor) because of the phenomenon of move-exchange where different move sequences can lead to the same position. Example: 1. e4 e6 2. d4 d6 and 1. d4 d6 2. e4 e6 both lead to the same position. The games can be forced to fit a tree structure, however, by not capturing the position but the sequence of moves and ignoring that this could be the same position. Trees can be visualised with the 'show_tree.html' viewer or the 'show_tree_force.html' viewer.
A viewer for the non-tree graph has to be developed.
Profiles that are trees have names ending on "_T.json" while the more general graph type has "\_G.json" name

### Setup

## Load packages
The python code requires 2 packages:
* python-chess
* networkx

## Setup directory structure
The files can be placed in any sub directory, but the following subdirectories are used:
* pgn       directory to place all pgn files (put as many as you like)
* profile   directory where the created profiles from players are stored.

### To do
There are still many 'loose ends' to tidy up or put in more / improved functionality.
Some examples left for next sprints.
* take into account rating difference with opponent
* take the date of the game into account
* build a viewer for graph type profiles

### Terms of use

