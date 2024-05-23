import streamlit as st
import pandas as pd
import random
import replicate
import os

def get_card_state():
    '''
    get the current cards in the deck, hand and play pile
    '''    
    # if this is the first run through, create a new deck
    if 'deck' not in st.session_state:
        st.session_state.deck = [
            '♣️ A','♣️ 2','♣️ 3','♣️ 4','♣️ 5','♣️ 6','♣️ 7','♣️ 8','♣️ 9','♣️ 10','♣️ J','♣️ Q','♣️ K',
            '♠️ A','♠️ 2','♠️ 3','♠️ 4','♠️ 5','♠️ 6','♠️ 7','♠️ 8','♠️ 9','♠️ 10','♠️ J','♠️ Q','♠️ K',
            '♦️ A','♦️ 2','♦️ 3','♦️ 4','♦️ 5','♦️ 6','♦️ 7','♦️ 8','♦️ 9','♦️ 10','♦️ J','♦️ Q','♦️ K',
            '♥️ A','♥️ 2','♥️ 3','♥️ 4','♥️ 5','♥️ 6','♥️ 7','♥️ 8','♥️ 9','♥️ 10','♥️ J','♥️ Q','♥️ K'
            ]
    
    # if this is the first run through, create a new hand
    if 'cards_in_hand' not in st.session_state:
        st.session_state.cards_in_hand = []

    if 'cards_in_opp_hand' not in st.session_state:
        st.session_state.cards_in_opp_hand = []

    # if this is the first run through, create a new play pile
    if 'play_pile' not in st.session_state:
        st.session_state.play_pile = []
    
    if 'selected_cards' not in st.session_state:
        st.session_state.selected_cards = []

def set_style():

    st.markdown(
    """
    <style>
    button {
        width: 65px !important;
        height: 80px !important;
        --background-color: white !important;
        --color: "white" !important;
        --opacity: 1.0 !important;
        border: 1px solid black !important;

    }
    button[kind="primary"] {
    background-color: grey;
    }

    button[kind="secondary"] {
        background-color: white;
    }
    table {
        background-color: #E4E4E4 !important;
        border-radius: 0.5rem !important;
    }
    div[role="dialog"] {
        background-color: #E4E4E4 !important;
    }
    button[aria-label="Close"] {
        border: none !important;
    }
    /*
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 2px solid white;
    }
    */
    </style>
    """,
        unsafe_allow_html=True,
    )
    # container for the table
    playpile_container = st.container(border = True, height = 180)
    playpile_container.markdown('<p style="color:white;">Table</p>', unsafe_allow_html=True)

    pc1, pc2, pc3 = playpile_container.columns(3)
    st.session_state.table_cols = [pc1, pc2, pc3]
    st.divider()
    # container for the hand
    hand_container = st.container(border = True, height = 180)
    hand_container.markdown('<p style="color:white;">Hand</p>', unsafe_allow_html=True)
    # hc1,hc2,hc3 = hand_container.columns(3)
    # st.session_state.cols = [hc1,hc2,hc3]
    st.session_state.cols = hand_container.columns(6)

    return playpile_container

@st.experimental_dialog("Welcome To Suit Yourself")
def initial_inputs():
    st.write('''
             Play against [Snowflake's Arctic AI](https://www.snowflake.com/blog/arctic-open-efficient-foundation-language-models-snowflake/) in a card game that you make up
             ''')
    starting_num = st.select_slider(
        "How many cards does each player start with?",
        options = list(range(0,26))
    )
    draw_num = st.select_slider(
        "How many cards does each player draw each turn?",
        options = list(range(0,26))
    )
    rules = st.text_input(
        label = "What are the rules of the game?",
        placeholder = 'E.g. the first person to play a 2 wins\n'
    )
    if st.button("Play"):
        st.session_state.starting_num = starting_num
        st.session_state.draw_num = draw_num = draw_num
        st.session_state.rules = rules
        st.rerun()

def get_clicked_cards():
    
    # cards in the hand have the notation __.hand, get all the session state
    # entires with this notation
    cards_in_hand = {
        x: st.session_state[x] for x in st.session_state if '.hand' in x
    }

    # get the card that was played
    clicked_card_id = [
        x for x in cards_in_hand if cards_in_hand[x]
    ][0]
    clicked_card = clicked_card_id.split('.')[0]
    
    return clicked_card_id, clicked_card

def deselect_cards():
    
    cards_in_hand = st.session_state.cards_in_hand
    selected_cards = st.session_state.selected_cards
    play_pile = st.session_state.play_pile
    table_cols = st.session_state.table_cols
    cols = st.session_state.cols

    clicked_card_id, clicked_card = get_clicked_cards()

    #remove the clicked card from the selected car list
    selected_cards = [
        c for c in selected_cards if c not in clicked_card
    ]
    unselected_cards = [
        c for c in cards_in_hand if c not in selected_cards
    ]
    st.session_state.selected_cards = selected_cards

    # generate a button for each card in the hand
    col_count = 0
    for card in selected_cards:
        if '♦️' in card or '♥️' in card:
            card_label = f':red[{card}]'
        else:
            card_label = card
        col = cols[col_count]
        col.button(
            label = card_label, key = f'{card}.hand', on_click = deselect_cards,
            type = 'primary'
            )
        col_count = (col_count + 1) % len(cols)
    for card in unselected_cards:
        if '♦️' in card or '♥️' in card:
            card_label = f':red[{card}]'
        else:
            card_label = card
        col = cols[col_count]
        col.button(
            label = card_label, key = f'{card}.hand', on_click = select_cards)
        col_count = (col_count + 1) % len(cols)

        # display what has been played on the table
    if len(play_pile) > 0:
        top_card = play_pile[len(play_pile)-1]
        #st.write(top_card)
        table_cols[1].button(
            label = top_card,
            key = f'{top_card}.table'
        )
        with table_cols[2].expander("See played cards"):
            st.write('\n\r'.join(play_pile))

def select_cards():
    '''
    displays the cards that are ready to be played
    '''
    cards_in_hand = st.session_state.cards_in_hand
    cols = st.session_state.cols
    table_cols = st.session_state.table_cols
    play_pile = st.session_state.play_pile

    clicked_card_id, clicked_card = get_clicked_cards()
    # store a list of selected cards
    st.session_state.selected_cards.append(clicked_card)

    selected_cards = st.session_state.selected_cards
    unselected_cards = [
        c for c in cards_in_hand if c not in selected_cards
    ]

    # generate a button for each card in the hand
    col_count = 0
    for card in selected_cards:
        col = cols[col_count]
        if '♦️' in card or '♥️' in card:
            card_label = f':red[{card}]'
        else:
            card_label = card
        col.button(
            label = card_label, key = f'{card}.hand', on_click = deselect_cards,
            type = 'primary'
            )
        col_count = (col_count + 1) % len(cols)
    for card in unselected_cards:
        col = cols[col_count]
        if '♦️' in card or '♥️' in card:
            card_label = f':red[{card}]'
        else:
            card_label = card        
        col.button(
            label = card_label, key = f'{card}.hand', on_click = select_cards)
        col_count = (col_count + 1) % len(cols)

    # display what has been played on the table
    if len(play_pile) > 0:
        top_card = play_pile[len(play_pile)-1]
        #st.write(top_card)
        table_cols[1].button(
            label = top_card,
            key = f'{top_card}.table'
        )
        with table_cols[2].expander("See played cards"):
            st.write('\n\r'.join(play_pile))


def opponent_determine_card():
    pass

def opponents_turn():

    cards_in_hand = st.session_state.cards_in_hand
    cols = st.session_state.cols

    opponent_draw()
    opponent_playcard()
    player_draw()

def opponent_playcard():

    cards_in_opp_hand = st.session_state.cards_in_opp_hand
    command_cols = st.session_state.command_cols  
    table_cols = st.session_state.table_cols

    cards_to_play = cards_in_opp_hand[0:2]

    st.session_state.play_pile.extend(cards_to_play)
    play_pile = st.session_state.play_pile

    # remove these cards from the opponents hand
    cards_in_opp_hand = [
        c for c in cards_in_opp_hand if c not in cards_to_play
    ]
    st.session_state.cards_in_opp_hand = cards_in_opp_hand
    command_cols[0].write(f'Opponent plays {str(cards_to_play)}')

def playcard():
    '''
    play selected cards
    '''
    selected_cards = st.session_state.selected_cards
    cards_in_hand = st.session_state.cards_in_hand
    cols = st.session_state.cols
    table_cols = st.session_state.table_cols

    unselected_cards = [
        c for c in cards_in_hand if c not in selected_cards
    ]

    #leave the unselected cards in the hand
    st.session_state.cards_in_hand = unselected_cards

    # add the selected cards to the play pile
    st.session_state.play_pile.extend(selected_cards)
    play_pile = st.session_state.play_pile

    # reset the selected cards
    st.session_state.selected_cards = []

    col_count = 0
    for card in unselected_cards:
        if '♦️' in card or '♥️' in card:
            card_label = f':red[{card}]'
        else:
            card_label = card
        col = cols[col_count]
        col.button(
            label = card_label, key = f'{card}.hand', on_click = select_cards
            )
        col_count = (col_count + 1) % len(cols)

    
    top_card = play_pile[len(play_pile)-1]
    table_cols[1].button(
        label = top_card,
        key = f'{top_card}.table'
    )
    with table_cols[2].expander("See played cards"):
        st.write('\n\r'.join(play_pile))

def opponent_draw(
    draw_num_flag = 'Regular'
    ):
    if draw_num_flag == 'Regular':
        draw_num = st.session_state.draw_num
    else:
        draw_num = st.session_state.starting_num

    cards_in_opp_hand = st.session_state.cards_in_opp_hand
    
    deck = st.session_state.deck
    cards = random.sample(deck, draw_num)

    # add cards to the opponents hand
    cards_in_opp_hand.extend(cards)
    st.session_state.cards_in_opp_hand = cards_in_opp_hand

    # remove those cards from the deck
    # remember this deck in the session state
    deck = [c for c in deck if c not in cards]
    st.session_state.deck = deck

    
    #st.write(f'Opponent plays {cards_to_play}')

def player_draw(
    draw_num_flag = 'Regular'
    ):
    if draw_num_flag == 'Regular':
        draw_num = st.session_state.draw_num
    else:
        draw_num = st.session_state.starting_num

    deck = st.session_state.deck
    cards_in_hand = st.session_state.cards_in_hand
    cols = st.session_state.cols
    play_pile = st.session_state.play_pile
    table_cols = st.session_state.table_cols

    cards = random.sample(deck, draw_num)
    
    # add those cards to your hand
    # remember this hand in the session state
    cards_in_hand.extend(cards)
    st.session_state.cards_in_hand = cards_in_hand

    # remove those cards from the deck
    # remember this deck in the session state
    deck = [c for c in deck if c not in cards]
    st.session_state.deck = deck

    # generate a button for each card in the hand
    if draw_num_flag == 'Regular':
        col_count = 0
        for card in cards_in_hand:
            col = cols[col_count]
            if '♦️' in card or '♥️' in card:
                card_label = f':red[{card}]'
            else:
                card_label = card
            col.button(
                label = card_label, key = f'{card}.hand', on_click = select_cards
                )        
            col_count = (col_count + 1) % len(cols)

        if len(play_pile) > 0:
            top_card = play_pile[len(play_pile)-1]
            #st.write(top_card)
            table_cols[1].button(
                label = top_card,
                key = f'{top_card}.table'
            )
            with table_cols[2].expander("See played cards"):
                st.write('\n\r'.join(play_pile))

def determine_win():
    pass

# set app layout
# width
st.set_page_config(layout="wide")# get initial card state

get_card_state()
# get style parameters
playpile_container = set_style()

# container for user options
command_container = st.container()
cc1, cc2, cc3, cc4, cc5, cc6, cc7 = command_container.columns(7)
cols = [cc1, cc2, cc3, cc4, cc5, cc6, cc7]
st.session_state.command_cols = cols

cc4.button(
    label = 'Play Cards', on_click = playcard
    )
cc5.button(
    label = 'End Turn', on_click = opponents_turn
)

if 'starting_num' not in st.session_state:
    initial_inputs()

# if no cards have been drawn yet
if 'starting_num' in st.session_state and len(st.session_state.deck) == 52:
    player_draw(draw_num_flag = 'First')
    opponent_draw(draw_num_flag = 'First')
    player_draw()