import math
import random

global_verbose = True
global_super_verbose = False

 
private_set_cache = {}
def num_possible_sets(n_items, set_size):
    if n_items == 1:
        return 1
    elif set_size == 1:
        return n_items
    else:
        cache_key = '{}_{}'.format(n_items, set_size)
        if cache_key not in private_set_cache.keys():
            private_set_cache[cache_key] = sum( [num_possible_sets(n_items - 1, i) for i in range(0, set_size + 1)] )
        return(private_set_cache[cache_key])
      
 
def gen_random_set(items, set_size):
    if len(items) == 1:
        return(items * set_size)
    elif set_size == 0:
        return([])
    else:
        # figure out how many copies of the first item to include:
        possibilities = num_possible_sets(len(items), set_size)
        rng = random.random() * possibilities
      
        i = -1
        while rng > 0:
            i = i + 1
            # calculate num of possibilities with i copies of the first item:
            num_possibilities = num_possible_sets(len(items) - 1, set_size - i)
            rng = rng - num_possibilities
          
 
        first_item_set = [items[0]] * i
        remainder_set = gen_random_set(items[1:], set_size - i)
        return(first_item_set + remainder_set)

class Card:
    def __init__(self, full_name, cost, points, alignment):
        self.full_name = full_name
        self.name = full_name[0]
        self.cost = cost
        self.points = points
        self.alignment = alignment
        self.empower = 1 if self.full_name == 'Lilac Lotus' else 0
        self.save = 1 if self.full_name == 'Adamant Angel' else 0

class Deck:
    def __init__(self, cards):
        self.cards = cards
        self.deck = cards

    def prep_and_shuffle(self):
        self.deck = self.cards
        self.in_play = []
        self.pending_play = []
        random.shuffle(self.deck)

    def print_self(self):
        names = [c.name for c in self.cards]
        names.sort()
        print('{}'.format(' '.join(names)))

    def get_score(self):
        return(sum([c.points(self.in_play) for c in self.in_play]))

    def get_empower(self):
        return(sum([c.empower for c in self.in_play]))

    def has_save(self):
        #return(False)
        return(sum([c.save for c in self.in_play]))
  
    def execute_play(self):
        assert( len( self.pending_play ) <= 1 )
        self.in_play = self.in_play + self.pending_play
        self.pending_play = []

    def select_play(self, round_number):
       
        max_cost = round_number + self.get_empower()
 
        # look for angel redraws
        valid_draw = False
        while valid_draw == False:
            draws = self.deck[0:2]
            if max_cost >= 5:
                valid_draw = True
            angels_drawn = len([c for c in draws if c.name == 'A'])
            non_angels_in_deck = len([c for c in self.deck if c.name != 'A'])
            if angels_drawn == 0:
                valid_draw = True
            if (2 - angels_drawn) == non_angels_in_deck:
                valid_draw = True
            if valid_draw == False:
                random.shuffle(self.deck)
 
           
        if global_super_verbose:
            print('Drew {} and {}'.format(draws[0].name, draws[1].name))
        self.deck = self.deck[2:]
        valid_plays = [c for c in draws if c.cost <= max_cost]
        if len(valid_plays):  
            valid_plays.sort(key=lambda card : card.cost)
            card_to_play = valid_plays[-1]
            if global_super_verbose:
                print('Played {}'.format(card_to_play.name))
            self.pending_play.append(card_to_play)
        else:
            if global_super_verbose:
                print('Played nothing')

class World:
    def __init__(self, card_details):
        self.cards = []
        self.deck_size = 12
        self.instant_win_threshold = 2000
        for entry in card_details:
            self.cards.append(Card(entry['full_name'], entry['cost'], entry['points'], entry['alignment']))

    def build_deck_from_names(self, names):
        cards = []
        for n in names:
            matches = [ c for c in self.cards if c.name == n ]
            assert(len(matches) == 1)
            cards.append(matches[0])
        return(Deck(cards))

    def build_random_deck(self):
        cards = gen_random_set(self.cards, self.deck_size)
        return(Deck(cards))

    def eval_deck_str_vs_random(self, deck, games_to_play=10000):
        games_played = 0
        wins = 0
        losses = 0
        draws = 0
        while games_played < games_to_play:
            res = self.play_game(deck, self.build_random_deck())[0]
            if res == 1:
                wins = wins + 1
            elif res == -1:
                losses = losses + 1
            elif res == 0:
                draws = draws + 1
            else:
                assert(False)
            games_played = games_played + 1
        strength_val = 100*(wins)/games_played
        print('Out of {} games had {} wins, {} losses.  Win rate is {:.2f}.'.format(games_played, wins, losses, strength_val))
        return(strength_val)

    def eval_deck_str_comparison(self, deck_a, deck_b, games_to_play=10000, force_seed=None):
        if force_seed is not None:
            random.seed(force_seed)
        games_played = 0
        wins = 0
        losses = 0
        draws = 0
        while games_played < games_to_play:
            res = self.play_game(deck_a, deck_b)[0]
            if res == 1:
                wins = wins + 1
            elif res == -1:
                losses = losses + 1
            elif res == 0:
                draws = draws + 1
            else:
                assert(False)
            games_played = games_played + 1
        strength_val = 100*(wins)/games_played
        if global_verbose:
            print('Out of {} games Deck A had {} wins, {} losses.  Win rate is {:.2f}%.'.format(games_played, wins, losses, strength_val))
        return(strength_val)

    def play_game(self, deck_a, deck_b):
        round_no = 1
        deck_a.prep_and_shuffle()
        deck_b.prep_and_shuffle()
        round_no = 1
        while round_no <= 6:
            if global_super_verbose:
                print('Round {}'.format(round_no))
            deck_a.select_play(round_no)
            deck_b.select_play(round_no)
            deck_a.execute_play()
            deck_b.execute_play()
            if global_super_verbose:
                print('Score is {} - {}'.format(deck_a.get_score(), deck_b.get_score()))
            point_diff = deck_a.get_score() - deck_b.get_score()
           
            if abs(point_diff) >= self.instant_win_threshold:
                if point_diff > 0 and deck_b.has_save() == 0:
                    break
                elif point_diff < 0 and deck_a.has_save() == 0:
                    break
            round_no = round_no + 1

        point_diff = deck_a.get_score() - deck_b.get_score()

        #actually prevent draws
        if point_diff == 0:
            point_diff = random.random() - 0.5
          
        if point_diff > 0:
            if global_super_verbose:
                print('Deck A Wins!')
            return([1, round_no])
        elif point_diff < 0:
            if global_super_verbose:
                print('Deck B Wins!')
            return([-1, round_no])
        else:
            if global_super_verbose:
                print('Draw')
            return([0, round_no])

    def eval_card_quality(self, runs_to_make = 10000):
        win_loss_struct = {}
        early_wins = 0
      
        for c in self.cards:
            win_loss_struct[c] = {'wins' : 0, 'losses' : 0, 'draws' : 0}
        runs = 0
        exp_card_count = self.deck_size / len(self.cards)
      
        while runs < runs_to_make:
            runs = runs + 1
            deck_a = myWorld.build_random_deck()
            deck_b = myWorld.build_random_deck()
            [out_result, out_round] = myWorld.play_game(deck_a, deck_b)
            if out_round < 6:
                early_wins = early_wins + 1
            if out_result == 0:
                continue
            a_result = 'wins' if out_result >0 else 'losses'
            b_result = 'wins' if out_result <0 else 'losses'
            for c in deck_a.cards:
                win_loss_struct[c][a_result] = win_loss_struct[c][a_result] + 1
            for c in deck_b.cards:
                win_loss_struct[c][b_result] = win_loss_struct[c][b_result] + 1
            for c in self.cards:
                win_loss_struct[c]['wins'] = win_loss_struct[c]['wins'] - exp_card_count
                win_loss_struct[c]['losses'] = win_loss_struct[c]['losses'] - exp_card_count

        if global_verbose:
            print('{:.2f}% of games({}/{}) ended early'.format(early_wins * 100 / runs, early_wins, runs))

        for c in self.cards:
            card_res = win_loss_struct[c]
            if global_verbose:
                print('{} overweight is involved in {:.1f} wins and {:.1f} losses'.format(c.full_name, card_res['wins'], card_res['losses']))
        return(win_loss_struct)
   
    def log(self, log_row, mode='a'):
        log_string = ','.join([str(e) for e in log_row])+"\n"
        f = open('mtg_output.csv', mode)
        f.write(log_string)

    def setup_logs(self):
        log_row = ['Game ID']
        for c in self.cards:
            log_row.append(c.full_name.replace(',', '').replace(' ', '_') + '_Deck_A_Count')
        for c in self.cards:
            log_row.append(c.full_name.replace(',', '').replace(' ', '_') + '_Deck_B_Count')
        log_row.append('Deck_A_Win?')
        log_row.append('Deck_B_Win?')
        self.log(log_row, mode='w')

    def write_logs(self, rows_to_write=342395):
        runs = 0
        while runs <= rows_to_write:
            d1 = self.build_random_deck()
            d2 = self.build_random_deck()
            result = self.play_game(d1, d2)[0]
            log_row = [runs]
            for c in self.cards:
                log_row.append(len([x for x in d1.cards if x == c]))
            for c in self.cards:
                log_row.append(len([x for x in d2.cards if x == c]))
            log_row.append(1 if result == 1 else 0)
            log_row.append(1 if result == -1 else 0)
            self.log(log_row)
            runs = runs + 1
 
    def list_possible_replacements(self, card_names, valid_cards=None):
 
        if valid_cards is None:
            valid_cards = [c.name for c in self.cards]
           
        possibilities = []
       
        uniq_cards = []
        for c in card_names:
            if c not in uniq_cards:
                uniq_cards.append(c)
       
        for card_to_remove in uniq_cards:
            for card_to_add in valid_cards:
                if card_to_add != card_to_remove:
                    new_cards = card_names + [card_to_add]
                    new_cards.remove(card_to_remove)
                    new_cards.sort()
                    possibilities.append(new_cards)
 
        return(possibilities)
                   
    def optimize_versus(self, base_deck, opponent_deck, valid_cards=None, seed='yugioh'):
        card_names = [c.name for c in base_deck.cards]
        card_names.sort()
        print('Evaluating deck:')
        print(card_names)      
        best_perf = self.eval_deck_str_comparison(base_deck, opponent_deck, force_seed=seed)
        best_deck = base_deck
 
       
        while True:
            improvement_made = False
 
            possible_changes = self.list_possible_replacements(card_names, valid_cards)
            random.shuffle(possible_changes)
            for possible_new_cards in possible_changes:
                possible_new_deck = self.build_deck_from_names(possible_new_cards)
                new_perf = self.eval_deck_str_comparison(possible_new_deck, opponent_deck, force_seed=seed)
                if new_perf > best_perf:
                    print('Improved from {:.2f} to {:.2f} with deck:'.format(best_perf, new_perf))
                    print(possible_new_cards)
                    best_perf = new_perf
                    card_names = possible_new_cards
                    best_deck = possible_new_deck
                    improvement_made=True
                    break
                   
 
            if improvement_made == False:
                break
 
        return(card_names)
   
 
 
random.seed("yugioh")
cards = [
    { 'full_name' : 'Alessin, Adamant Angel', 'cost' : 5, 'points' : lambda board: 1800, 'alignment' : 'Good' },
    { 'full_name' : 'Bold Battalion', 'cost' : 4, 'points' : lambda board : 600 * len([c for c in board if c.alignment == 'Good']), 'alignment' : 'Good' },
    { 'full_name' : 'Dreadwing, Darkfire Dragon', 'cost' : 5, 'points' : lambda board: 2500, 'alignment' : 'Evil' },
    { 'full_name' : 'Evil Emperor Eschatonus, Empyreal Envoy of Entropic End', 'cost' : 6, 'points' : lambda board: 4500, 'alignment' : 'Evil' },
    { 'full_name' : 'Gentle Guard', 'cost' : 1, 'points' : lambda board: 700, 'alignment' : 'Good' },
    { 'full_name' : 'Horrible Hooligan', 'cost' : 2, 'points' : lambda board: 900, 'alignment' : 'Evil' },
    { 'full_name' : 'Kindly Knight', 'cost' : 2, 'points' : lambda board: 900, 'alignment' : 'Good' },
    { 'full_name' : 'Lilac Lotus', 'cost' : 1, 'points' : lambda board: 200, 'alignment' : 'Artifact' },
    { 'full_name' : 'Murderous Minotaur', 'cost' : 4, 'points' : lambda board: 1700, 'alignment' : 'Evil' },
    { 'full_name' : 'Patchy Pirate', 'cost' : 1, 'points' : lambda board: 700, 'alignment' : 'Evil' },
    { 'full_name' : 'Sword of Shadows', 'cost' : 3, 'points' : lambda board: 2000 if len([c for c in board if c.alignment == 'Evil']) else 0, 'alignment' : 'Artifact' },
    { 'full_name' : 'Virtuous Vigilante', 'cost' : 3, 'points' : lambda board: 1300, 'alignment' : 'Good' },
    ]
cards.sort(key = lambda c: c['full_name'])
 
myWorld = World(cards)
 
 
__name__ = "__test__"
 
if __name__ == "__main__" :
    myWorld.setup_logs()
    myWorld.write_logs()

if __name__ == "score_pve":
    player_decks = [ 
        { 'player' : 'Sword Aggro', 'deck' : myWorld.build_deck_from_names(['P'] * 3 + ['S'] * 5 + ['A'] * 4)},
        { 'player' : 'Lotus Ramp', 'deck' : myWorld.build_deck_from_names(['L'] * 5 + ['A'] * 3 + ['E'] * 4)},   
        { 'player' : 'Good Tribal', 'deck' : myWorld.build_deck_from_names(['G'] * 6 + ['B'] * 6)},
        { 'player' : 'abstractapplic', 'deck' : myWorld.build_deck_from_names(['A'] * 2 + ['H'] * 3 + ['P'] * 3 + ['S'] * 4)},   
        { 'player' : 'gammagurke', 'deck' : myWorld.build_deck_from_names(['A'] * 3 + ['E'] * 2 + ['L'] * 5 + ['P'] * 2)},
        { 'player' : 'GuySrinivasan', 'deck' : myWorld.build_deck_from_names(['D'] * 4 + ['E'] * 2 + ['L'] * 6)},
        { 'player' : 'jsevillamol', 'deck' : myWorld.build_deck_from_names(['B'] * 1 + ['E'] * 1 + ['K'] * 9 + ['P'] * 1)},
        { 'player' : 'Maxwell Peterson', 'deck' : myWorld.build_deck_from_names(['A'] * 3 + ['M'] * 1 + ['P'] * 6 + ['S'] * 2)},
        { 'player' : 'Measure', 'deck' : myWorld.build_deck_from_names(['A', 'A', 'D', 'E', 'E', 'L', 'L', 'L', 'P', 'P', 'S', 'V'])},
        { 'player' : 'Pablo Repetto', 'deck' : myWorld.build_deck_from_names(['A'] * 4 + ['L'] * 3 + ['P'] * 3 + ['S'] * 2)},
        { 'player' : 'Yonge', 'deck' : myWorld.build_deck_from_names(['A', 'A', 'D', 'E', 'E', 'H', 'L', 'L', 'M', 'P', 'V', 'V'])},  
        
    ]
    npc_deck =  myWorld.build_deck_from_names([c['full_name'][0] for c in cards])
    for submission in player_decks:
        random.seed('yugioh') # avoid ordering issues...
        print('Evaluating submission of {}:'.format(submission['player']))
        deck = submission['deck']
        deck.print_self()
        myWorld.eval_deck_str_comparison(deck, npc_deck)

if __name__ == "score_pvp":
    player_decks = [
        { 'player' : 'abstractapplic', 'deck' : myWorld.build_deck_from_names(['A'] * 2 + ['H'] * 3 + ['P'] * 3 + ['S'] * 4)},
        { 'player' : 'gammagurke', 'deck' : myWorld.build_deck_from_names(['A'] * 2 + ['E'] * 4 + ['L'] * 6)}, 
        { 'player' : 'GuySrinivasan', 'deck' : myWorld.build_deck_from_names(['M'] * 1 + ['D'] * 5 + ['L'] * 6)},
        { 'player' : 'jsevillamol', 'deck' : myWorld.build_deck_from_names(['B'] * 1 + ['E'] * 1 + ['K'] * 9 + ['P'] * 1)},
        { 'player' : 'Maxwell Peterson', 'deck' : myWorld.build_deck_from_names(['A'] * 4 + ['H'] * 4 + ['P'] * 2 + ['S'] * 2)},
        { 'player' : 'Measure', 'deck' : myWorld.build_deck_from_names(['V'] * 1 + ['E'] * 3 + ['P'] * 4 + ['S'] * 4)},
        { 'player' : 'Pablo Repetto', 'deck' : myWorld.build_deck_from_names(['A'] * 4 + ['L'] * 3 + ['P'] * 3 + ['S'] * 2)},
        { 'player' : 'Yonge', 'deck' : myWorld.build_deck_from_names(['A', 'A', 'D', 'E', 'E', 'H', 'L', 'L', 'M', 'P', 'V', 'V'])},
    ]
    for d in player_decks:
        d['matchups'] = {}
        d['matchups'][d['player']] = 50
    for i1 in range(0, len(player_decks)):
        for i2 in range(i1 + 1, len(player_decks)):
            p1 = player_decks[i1]
            p2 = player_decks[i2]
            print('Evaluating {} vs {}:'.format(p1['player'], p2['player']))
            res = myWorld.eval_deck_str_comparison(p1['deck'], p2['deck'])
            p1['matchups'][p2['player']] = res
            p2['matchups'][p1['player']] = 100 - res
    for d in player_decks:
        d['total_score'] = sum(d['matchups'].values())/100
    player_decks.sort(key=lambda entry : -1 * entry['total_score'])
    names = [d['player'] for d in player_decks]

    log_string = 'Player,' + ','.join(names)+",Total Score\n"
    f = open('mtg_pvp_output.csv', 'w')
    f.write(log_string)

    for d in player_decks:
        log_row = [d['player']]
        for o in names:
            log_row.append(str(d['matchups'][o]) + '%')
        log_row.append('{:.2f}'.format(d['total_score']))
        log_string = ','.join([str(x) for x in log_row]) + '\n'
        print(log_string)
        f.write(log_string)

    f.close()
        
    
    
    
    
if __name__ == "__test__" :
    #myWorld.eval_card_quality()
   
    test_decks = [
        myWorld.build_deck_from_names([c['full_name'][0] for c in cards]),
        myWorld.build_deck_from_names(['P'] * 3 + ['S'] * 5 + ['A'] * 4),
        myWorld.build_deck_from_names(['G'] * 6 + ['B'] * 6),
        myWorld.build_deck_from_names(['L'] * 5 + ['E'] * 4 + ['A'] * 3),
        ]
    for deck in test_decks:
        myWorld.eval_deck_str_vs_random(deck)
    #res1 = myWorld.optimize_versus(test_decks[1], test_decks[0])
    #res2 = myWorld.optimize_versus(test_decks[2], test_decks[0])
    #res3 = myWorld.optimize_versus(test_decks[3], test_decks[0])
    #res4 = myWorld.optimize_versus(test_decks[4], test_decks[0])
 
    for i1 in range(0,len(test_decks)):
        for i2 in range(i1 + 1,len(test_decks)):
            d1 = test_decks[i1]
            d2 = test_decks[i2]
            d1.print_self()
            print( 'VS' )
            d2.print_self()
            myWorld.eval_deck_str_comparison(d1, d2)
   
    #myWorld.optimize_versus(test_decks[1], test_decks[0], valid_cards=['P', 'S', 'A', 'H', 'D'])
    #myWorld.optimize_versus(test_decks[2], test_decks[0], valid_cards=['G', 'B', 'E', 'K', 'V', 'A'])
    #myWorld.optimize_versus(test_decks[3], test_decks[0], valid_cards=['L', 'E', 'A', 'V'])
