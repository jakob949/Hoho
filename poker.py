# -*- coding: utf-8 -*-
import numpy as np
import random, time
from operator import itemgetter

start = time.time()
# es = 14
OG_deck = np.array(['14H','02H','03H','04H','05H','06H','07H','08H','09H','10H','11H','12H','13H',
                '14D','02D','03D','04D','05D','06D','07D','08D','09D','10D','11D','12D','13D',
                '14S','02S','03S','04S','05S','06S','07S','08S','09S','10S','11S','12S','13S',
                '14C','02C','03C','04C','05C','06C','07C','08C','09C','10C','11C','12C','13C'])


out = list()

def random_card(num_deck, num_of_players, deck):
    """
    The function returns random cards for both the deck and players
    return [0] = [deck cards]
    return[1] = [[cards_p1],[cards_p2]....]
    """
    deck_cards = list()
    player_cards = list()
    cards = list()
    
    for i in range(num_deck):
        temp = random.choice(range(0,len(deck)))
        deck_cards.append(deck[temp])
        
        deck = np.delete(deck,temp)
    for i in range(num_of_players):
        player_cards.append([])
        for j in range (2):
            temp = random.choice(range(0,len(deck)))
            player_cards[i].append(deck[temp])
            
            deck = np.delete(deck,temp)
    
    return (deck_cards, player_cards)    


########### Sorting function / keys
def last_letter(last):
    """ sorting-key
    (For sorting by last char in string)
    """
    return last[::-1]

def sort_by_number(x):
    """ sorting-key
    (For sorting by two first chars in string)
    """
    return x[0:2]

############ functions for evalution result of hand+table

def flush(evaluting_hand):
    if len(evaluting_hand) < 5:
        return False
    # sorting by the last letter of each item in list
    evaluting_hand = sorted(evaluting_hand, key=sort_by_number, reverse = True)
    evaluting_hand = sorted(evaluting_hand, key=last_letter)
    
    multiply_flushs = list()
    for i in range (len(evaluting_hand)):
        temp = (evaluting_hand[i:i+5])
        
        if len(temp) < 5:
            break
        if temp[0][-1] == temp[4][-1]: 
            # hands evaluted to flush
            multiply_flushs.append(temp)
    
    for hands in multiply_flushs:
        if straight(hands) != False:
            hand = sorted(hands, key=sort_by_number, reverse = True)
            return (True, hand)
        elif straight(hands) == False:
            hand = sorted(hands, key=sort_by_number, reverse = True)
            return (True, hand)            
    return (False)



def straight(evaluting_hand):

    """
    To account for 14/es both as to be apple to make a straight with 02 and 13
    This if/else thing is included 
    """
    if len(evaluting_hand) < 5:
        return False
    if "14C" or "14D" or "14S" or "14H" in evaluting_hand:
        # Replace 14s with 01, (list comprehension)
        evaluting_hand = ['01{0}'.format(i[2]) if i[0:2] =='14' else i for i in evaluting_hand]

        evaluting_hand = sorted(evaluting_hand, key=sort_by_number)
        for i in range (len(evaluting_hand)-4):
            temp = (evaluting_hand[i:i+5])
     
            if int(temp[0][0:2].lstrip('0')) + 4  == int(temp[1][0:2].lstrip('0')) + 3 == int(temp[2][0:2].lstrip('0')) + 2 == int(temp[3][0:2].lstrip('0')) + 1 == int(temp[4][0:2].lstrip('0')): 
                # Cards evaluted to straigh. thus returns true
                temp = sorted(temp, key=sort_by_number, reverse=True)
                # What to show for the es in this case? 
                # - 14 or 01?
              
                
                return (True, temp)
    else:
        evaluting_hand = sorted(evaluting_hand, key=sort_by_number)
        for i in range (len(evaluting_hand)-4):
            temp = (evaluting_hand[i:i+5])
     
            if int(temp[0][0:2].lstrip('0')) + 4  == int(temp[1][0:2].lstrip('0')) + 3 == int(temp[2][0:2].lstrip('0')) + 2 == int(temp[3][0:2].lstrip('0')) + 1 == int(temp[4][0:2].lstrip('0')): 
                # Cards evaluted to straigh. thus returns true
                return (True, sorted(temp, key=sort_by_number, reverse=True))     
    return (False)


def four(evaluting_hand):
    if len(evaluting_hand) < 4:
        return False
    evaluting_hand = sorted(evaluting_hand, key=sort_by_number)
    
    for i in range (len(evaluting_hand)-3):
        temp = (evaluting_hand[i:i+4])

        if int(temp[0][0:2].lstrip('0')) == int(temp[1][0:2].lstrip('0')) == int(temp[2][0:2].lstrip('0')) == int(temp[3][0:2].lstrip('0')): 
            # Cards evaluted to straigh. thus returns true
            return (True, temp)     
    return (False)

def tree(evaluting_hand):
    if len(evaluting_hand) < 3:
        return False
    evaluting_hand = sorted(evaluting_hand, key=sort_by_number)
    
    for i in range (len(evaluting_hand)-2):
        temp = (evaluting_hand[i:i+3])
        if int(temp[0][0:2].lstrip('0')) == int(temp[1][0:2].lstrip('0')) == int(temp[2][0:2].lstrip('0')): 
            return (True, temp)     
    return (False)

def pair (evaluting_hand):
    """ Recursion <3
        The function calls itself when it has found the very first pair.
        the pair is added to the out-list.
        If a second pair is found this is also added to the out list.
    """
    if len(evaluting_hand) < 2:
        return False
    evaluting_hand = sorted(evaluting_hand, key=sort_by_number, reverse=True)
    for i in range (len(evaluting_hand)-1):
        temp = (evaluting_hand[i:i+2])
        if int(temp[0][0:2].lstrip('0')) == int(temp[1][0:2].lstrip('0')): 
            # Cards evaluted to straigh. thus returns true
            pair(list(set(evaluting_hand)-set(temp)))
            out.extend(temp)
            
            return (True, out)     
    return (False)
    
def high_cards (evaluting_hand, num_cards):
    evaluting_hand = sorted(evaluting_hand, key=sort_by_number, reverse=True)
    return(evaluting_hand[:num_cards])

########### main functions #######

def best_hand (table_cards, players_hands):
    evaluting_hand = list()
    out.clear()
    
    temp_product = None
    temp = players_hands+table_cards
    evaluting_hand.extend(temp)
    
    temp_product = four(evaluting_hand) 

    if temp_product != False:
        candite_hand = temp_product[1]
        candite_hand.extend(high_cards(list(set(evaluting_hand)-set(temp_product[1])),1))
        return (candite_hand,'four of a kind', 7)
        

    temp_product = tree(evaluting_hand)
    if temp_product != False:
        candite_hand = temp_product[1]
        full_house = pair(list(set(evaluting_hand)-set(candite_hand)))
        if full_house != False:
            candite_hand.extend(full_house[1])
            return(candite_hand, 'full-house', 6)
            
    
    temp_product = flush(evaluting_hand)
    if temp_product != False:
        candite_hand = temp_product[1]
        straight_flush = straight(candite_hand)
        if straight_flush != False:

            return(straight_flush[1], 'Straight flush', 8)
            
        else:
            return(candite_hand,'flush', 5)
            
        
    temp_product = straight(evaluting_hand)
    if temp_product != False:
        candite_hand = temp_product[1]
        return(candite_hand,'straight', 4)
        
    
    temp_product = tree(evaluting_hand)
    if temp_product != False:
        candite_hand = temp_product[1]
        full_house = pair(list(set(evaluting_hand)-set(candite_hand)))
        candite_hand.extend(high_cards(list(set(evaluting_hand)-set(temp_product[1])),2))
        return(candite_hand, 'three of a kind', 3)
        
    
    temp_product = pair(evaluting_hand)
    if temp_product != False:
        candite_hand = temp_product[1]
        if len(candite_hand) == 4:
            candite_hand = sorted(candite_hand, key=sort_by_number, reverse=True)
            candite_hand.extend(high_cards(list(set(evaluting_hand)-set(candite_hand)),1))
            return (candite_hand, 'two-pairs', 2)
            
        elif len(candite_hand) == 2:
            candite_hand.extend(high_cards(list(set(evaluting_hand)-set(candite_hand)),3))
            return (candite_hand, 'Pair' , 1)
                
    
    return(high_cards(evaluting_hand, 5),'High hand', 0)
    



################## probabilities 

def freq (ilteration):
    prob = {}
    for i in range(ilteration):
        out.clear()
        deck = OG_deck
        cards = random_card(5, 1, OG_deck)
        result = best_hand(cards[0], cards[1][0])
        
        # if result[1] == 'Straight flush':
        #     print(result)
        
        if prob.get(result[1]) is None:
            prob[result[1]] = 1
        else:
            prob[result[1]] += 1
    
    for item in prob:
        print(item, 'occs:',prob[item], 'probs:', int(prob[item])/ilteration)





num_of_players = 1
test_hand = ['14C', '02C', '14D', '03D', '09D']
players_hands = ['12D','02S']


def game():
    cards = random_card(5, num_of_players, OG_deck)
    max_value = -1
    high_hand = list()
    results = list()
    for i in range(num_of_players):
        results.append(best_hand(cards[0], cards[1][i]))
    # sort list of list:
    results = sorted(results, key=itemgetter(2))
    
    return results

print(freq(10000000))


end=time.time()
print('\ntime used:',end-start)



