import re
import os
import argparse
from collections import Counter

# for chess stuff
import chess
import chess.pgn

# for building graphs
import json
import networkx as nx
from networkx.readwrite import json_graph

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='store_true', help='print messages')

subparsers = parser.add_subparsers(help='commands', dest='command')

# find a player
find_parser = subparsers.add_parser('find', help='find a player')
find_parser.add_argument('player',
                    help='name of the player')

find_parser.add_argument('-input', action='store',
                    dest='input_dir', default='pgn',
                    help='directory where PGN files are located (default=pgn)')

# create profile file of a player
create_parser = subparsers.add_parser('create', help='create a players profile')
create_parser.add_argument('player',
                    help='name of the player')
create_parser.add_argument('-graph', action='store_false',
                    dest='tree',
                    help='select graph or tree (default=tree)')
create_parser.add_argument('-input', action='store',
                    dest='input_dir', default='pgn',
                    help='directory where PGN files are located (default=pgn)')
create_parser.add_argument('-profile', action='store',
                    dest='profile_dir', default='profile',
                    help='directory where profile files are written (default=profile)')

# play against the player's profile
play_parser = subparsers.add_parser('play', help='play against the players profile')
play_parser.add_argument('player',
                    help='name of the player')
play_parser.add_argument('colour', choices = ['white', 'black'],
                    help='colour of the player')
play_parser.add_argument('moves', 
                    nargs='*',
                    help='moves played so far')
play_parser.add_argument('-graph', action='store_false',
                    dest='tree',
                    help='select graph or tree (default=tree)')
play_parser.add_argument('-profile', action='store', 
                    dest='profile_dir', default='profile',
                    help='directory where profile files are located (default=profile)')

def open_pgn(file_name, args):
    '''
    Open a pgn file so that games can be read from it

    Input: file name of pgn file
 
    Output: pgn_file_descriptor
    ''' 
    if args.v:
        print('reading pgn file:', file_name)

    return open(file_name, 'r', encoding='utf-8-sig', errors='surrogateescape')

def read_pgn(f):
    '''
    Read the next game from an open pgn file

    Input: pgn_file_descriptor

    Output: game which is of class 'chess.pgn.Game'
    ''' 
    return chess.pgn.read_game(f)


def close_pgn(f):
    '''
    Close the pgn file

    Input: pgn_file_descriptor

    Output: None
    '''
    f.close()

def root_name(args):
    '''
    Create the name for the root node of the tree
    '''
    if args.tree:
        name = 'root'
    else:
        name = chess.STARTING_FEN
    return name

def profile_file_name(args):
    if args.tree:
        graph_type = '_T'
    else:
        graph_type = '_G'
    file_name = ''.join([args.profile_dir, 
        '/', args.player, 
        ' (', args.colour, ')',
        graph_type,
        '.json'])
    return file_name

def init_profile(args):
    '''
    Creates the trees to capture the moves from games. Two separate trees are created:
    one for white and one for black
    '''
    Tree = []
    for c in range(len(args.colours)):
        name = ''.join([args.player, ' (', args.colours[c], ')'])
        Tree += [nx.DiGraph(name=name)]
        # Add root node to tree
        setattr (args, 'root', root_name(args))
        Tree[c].add_node(args.root, games=0, score=0, move=name)
    return Tree

def expand_profile(Tree, game, args):
    '''
    Process the moves of a game and store them into the tree
    The game is already verified to be played by the intended player
    '''
    
    def get_score(score_string, colour):
        '''
        Simple function to extract the score for the player from the Result string
        Result = ['1-0', '1/2-1/2','0-1']
        Colour = { 0:'white', 1:'black'}
        '''
        value = {'0':0, '1/2':0.5, '1':1}
        return value[score_string.split('-')[colour]]

    plies = 0
    colour = args.colour
    if args.v:
        print(game.headers['White'],'-',game.headers['Black'],' ',game.headers['Result'])
    board = chess.Board()   # board with starting position
    node_name = args.root
    position = chess.STARTING_FEN
    Tree[colour].node[node_name]['games'] += 1
    Tree[colour].node[node_name]['score'] += get_score(game.headers['Result'], colour)
    move = game
    while (not move.is_end()) and (plies < args.max_plies):
        plies += 1
        next_move = move.variation(0)
        san_move = move.board().san(next_move.move)
        board.push(next_move.move)   # execute the move on board
        next_position = board.fen()
        if args.tree:
            # we combine the move and the position to avoid not having a tree
            # remember: in chess you can get the same position through different move order
            #next_position = '&'.join([san_move, next_position])
            next_node_name = '-'.join([node_name, san_move])
        else:
            next_node_name = next_position

        if not(next_node_name in Tree[colour]):
            # add a new node
            Tree[colour].add_node(next_node_name, games=0, score=0, move=san_move)

        # keep track of how many times this node was visited and the score
        Tree[colour].node[next_node_name]['games'] += 1
        Tree[colour].node[next_node_name]['score'] += get_score(game.headers['Result'], colour)
        # add edge between this node and previous node
        Tree[colour].add_edge(node_name, next_node_name, move=san_move)

        #print(san_move)
        #print(next_position)
        move = next_move
        position = next_position
        node_name = next_node_name


def aggregate_profile(Tree, args):
    '''
    After all games have been read some aggregation is done:
    > calculate the overall score per node
    > prune the tree to delete all branches with only 1 game, only keep the first moves
    '''
    for c in range(len(Tree)):
        for node, attr in Tree[c].nodes(data=True):
            Tree[c].node[node]['rate'] = attr['score']/attr['games']
    
    if args.prune == 0:     # no pruning wanted
        return

    # prune
    for c in range(len(Tree)):
        outdeg = Tree[c].out_degree()
        leaves = [n for n in outdeg if outdeg[n] == 0]
        for leave in leaves:
            to_prune = [leave]
            # find the first node with outdeg > 1
            distance_to_leaf = 0
            n = leave
            p = Tree[c].predecessors(n)[0]
            while outdeg[p] == 1:
                n = p
                p = Tree[c].predecessors(n)[0]
                distance_to_leaf += 1
            
            # now keep args.prune nodes (n is the first to keep)
            if distance_to_leaf >= args.prune:
                s = Tree[c].successors(n)[0]
                for i in range(args.prune-1):
                    n = s
                    s = Tree[c].successors(n)[0]

                # now s is the first to be pruned
                Tree[c].remove_nodes_from(nx.descendants(Tree[c], n))

def save_profile(Tree, args):
    '''
    Save the profile, after aggregation, to files. One for white and one for black.
    '''
    for c in range(len(Tree)):
        setattr(args, 'colour', args.colours[c])
        if args.v:
            print('The',args.colour,'tree has', Tree[c].number_of_nodes(), 'nodes.')
            print('The',args.colour,'tree has', Tree[c].number_of_edges(), 'edges.')

        if args.tree:
            # for a tree format and the graph needs to be created with DiGraph
            data = json_graph.tree_data(Tree[c], root=args.root)
        else:
            Tree[c] = nx.convert_node_labels_to_integers(Tree[c], first_label=0, label_attribute='fen')
            # name is changed to: "(Carlsen (black))_with_int_labels"
            Tree[c].name = ''.join([args.player, ' (', args.colour, ')'])     # above convert also converts the name
            # for a Force directed graph
            data = json_graph.node_link_data(Tree[c])
        s = json.dumps(data)
        js = open(profile_file_name(args), 'w')
        js.write(s)
        js.close()

def create_profile (args):
    '''
    Opens all pgn files in the input_dir and find games from a particular player.
    These games are stored in the Graph structure. It keeps games from the player
    where he played with white separate from those with black.
    It starts by storing all moves from all games as a node but at the end it
    removes all child nodes with moves that have been played only once.

    Input: args.player, args.input_dir args.profile_dir, ....
 
    Output: profile file with player name as filename in json format
    '''

    games = 0        # total nr of games
    Tree = init_profile(args)
    for f in os.scandir(args.input_dir):
        if f.is_file() and ('.pgn' in f.name):
            pgn_file = args.input_dir+'/'+f.name
            fh = open_pgn(pgn_file, args)
            game = read_pgn(fh)
            while game and (games < args.max_games):
                colour = -1
                if re.search(args.player, game.headers['White']):
                    colour = 0
                if re.search(args.player, game.headers['Black']):
                    colour = 1
                if colour in range(len(args.colours)):      # so player was found
                    setattr (args, 'colour', colour)
                    expand_profile (Tree, game, args)
                    games += 1
                game = read_pgn(fh)
            close_pgn(fh)
    aggregate_profile (Tree, args)
    save_profile (Tree, args)

def find_player (args):
    '''
    Opens all pgn files in the input_dir to look for a particular player.
    It does not use a pgn function because direct file reads are much faster.

    Input: args.player, args.input_dir
 
    Output: list of found players and played games.
    ''' 
    games=0        # total nr of games
    players =[]    # list of matched names
    for f in os.scandir(args.input_dir):
        if f.is_file() and ('.pgn' in f.name):
            pgn_file = args.input_dir+'/'+f.name
            fh = open(pgn_file)
            line = fh.readline()
            while line:
                line = line.rstrip()
                if re.search('White ', line):
                    games += 1
                if re.search(args.player, line):
                    players += [line]
                line = fh.readline()
            fh.close()
    print("Total games:", games)

    names_counted = Counter(players)
    for name in sorted(names_counted.keys()):
        print(name, names_counted[name])

def read_profile(args):
    '''
    Read a profile from a player.

    Input: args.player, args.profile_dir, ....
 
    Output: tree of the profile
    
    Globals: sets args.root, args.file_OK
    '''
    tree = []
    file_name = profile_file_name(args)
    try:
        js = open(file_name, 'r')
    except IOError:
        print("Unable to open file", file_name)
        setattr(args, 'file_OK', False)
        return tree

    setattr(args, 'file_OK', True)
    data = json.load(js)
    js.close()
    tree = json_graph.tree_graph (data)
    setattr (args, "root", root_name(args))

    if args.v:
        print('The tree has', tree.number_of_nodes(), 'nodes.')
        print('The tree has', tree.number_of_edges(), 'edges.')

    return tree

def process_moves(Tree, args):
    '''
    Plays the moves from args against the opening board.
    There are no checks on move validity

    Input: args.player,  ....
 
    Output: json / dict of the next moves in the profile after playing the args moves
    '''
    board = chess.Board()   # board with starting position
    node_name = args.root
    position = chess.STARTING_FEN
    if args.v:
        print('root:', Tree.node[node_name])
    for move in args.moves:
        try:
            board.push_san(move)   # execute the move on board
        except ValueError:
            print("invalid move", move)
            return []

        next_position = board.fen()
        if args.tree:
            next_node_name = '-'.join([node_name, move])
        else:
            next_node_name = next_position
        position = next_position
        node_name = next_node_name

    # make a simple dict
    moves =[]
    if node_name not in Tree.nodes():
        # positon is not found in tree
        return moves

    for d in Tree.successors(node_name):
        moves += [Tree.node[d]]

    if args.v:
        print ('move'.rjust(7),'rate'.rjust(7), 'score'.rjust(7), 'games'.rjust(7))
        for d in moves:
            print (d['move'].rjust(7),"%7.3f" % d['rate'],
            "%7.1f" % d['score'], "%7d" % d['games'])

    return json.dumps(moves)

def play_profile(args):
    # also receive the colour
    # do a separate init (based on action?)
    # load the profile into a networkx tree
    Tree = read_profile(args)
    # execute the moves on a chess board & check if OK
    if args.file_OK:
        moves = process_moves(Tree, args)
        print(moves)
    # read from the tree available descendants and their score
    # print in reverse order (so worst for player on top)
    return 0

# process the command line arguments and set globals
def init():    
    # if you want to use arguments as a dict:
    # settings = vars(parser.parse_args()) and then
    # use the settings as settings['max_plies']
    settings = parser.parse_args()
    if settings.command == 'create':
        setattr(settings, 'colours', ['white', 'black'])      # we play chess
        setattr(settings, 'max_plies', 20)    # max plies to put in the profile tree
        setattr(settings, 'max_games', 300)    # max games to read for a player
        setattr(settings, 'prune', 3)         # 0->no, values: how many are kept
    
    if settings.v:
        print(settings)
    return settings

# start the main program
settings = init()
# and kick off the right command:
if settings.command == 'find':
    find_player(settings)
elif settings.command == 'create':
    create_profile(settings)
elif settings.command == 'play':
    play_profile(settings)
else:
    print('unknown command')
