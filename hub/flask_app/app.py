from collections import OrderedDict
from flask import Flask, current_app
from flask import render_template
import os
import re

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

REG = re.compile(r'CARD_([\d]+)_')

@app.route("/")
def home():
    # Read environment variables to create info cards.
    # For each card you can provide the following:
    # CARD_<nr>_TITLE --> Card title
    # CARD_<nr>_DESCRIPTION --> Description in card
    # CARD_<nr>_HREF --> Comma separated key-value pairs
    # of link button text and link. Multiple pairs are separated by semicolon.
    # CARD_<nr>_CONNECTIONINFO --> Comma separated key-value pairs
    # connection information. Multiple pairs are separated by semicolon.

    cards = {}
    # Iterate over all env variables and process those matching CARD_<nr>...
    for k, v in os.environ.items():
        matched = REG.search(k)
        if matched is not None:
            # Extract card number and part (TITLE, DESCRIPTION, HREF, CONNECTIONINFO)
            card_nr = matched[1]
            if card_nr not in cards:
                cards[card_nr] = {}
            card_part = k.rsplit('_')[-1]
            # For CONNECTIONINFO or HREF do extra processing to split pairs
            if card_part == 'CONNECTIONINFO' or card_part == 'HREF':
                v = [p.split(',') for p in v.split(';')]
            cards[card_nr][card_part] = v
    # Order by increasing card nr
    cards = OrderedDict(sorted(cards.items(), key=lambda x: x[0]))
    return render_template('home.html', cards=cards)
