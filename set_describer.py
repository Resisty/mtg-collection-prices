#!/usr/bin/env python
""" Try to get prices for your wishlist from scryfall
"""
import os
import csv
import json
import logging
import argparse
from decimal import Decimal

import urllib3

API = 'https://api.scryfall.com'
SETS = f'{API}/sets/'
BULK = f'{API}/bulk-data'
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)
def chunks(lst, num):
    """ Divide list 'lst' into num-sized chunks
    """
    for i in range(0, len(lst), num):
        yield lst[i: i+num]

def get_bulk(args):  # pylint: disable=unused-argument
    """ Script command function; wraps bulk data handler
    """
    return bulk_file()

def bulk_file():
    """ Download most recent bulk data
    """
    http = urllib3.PoolManager()
    request = http.request('GET', BULK)
    req_json = json.loads(request.data.decode('utf-8'))
    all_cards = [i['download_uri'] for i in req_json['data'] if i['type'] == 'all_cards'][0]
    filename = all_cards.split('/')[-1]
    if not os.path.isfile(f'./{filename}'):
        LOGGER.info('Most recent bulk data "%s" not found; downloading...', filename)
        bulk_req = http.request('GET', all_cards)
        with open(filename, 'wb') as out:
            out.write(bulk_req.data)
    return filename

def prepare_card_data(code, price=2):
    """ Obtain, read, and correct card data from bulk json

        :param code: 3-letter MTG set code to look up
    """
    bulk_data = bulk_file()
    with open(bulk_data) as fhandle:
        LOGGER.info('Loading card data for set "%s" from bulk data...', code)
        data = json.loads(fhandle.read())
        set_cards = [i for i in data if i['set'] == code]
    cards = []
    LOGGER.info('Fixing price data for set "%s"...', code)
    for card in set_cards:
        unknown_usd = True if not card['prices']['usd'] and card['lang'] == 'en' else False
        card['prices']['usd'] = Decimal(card['prices']['usd']) if card['prices']['usd'] else 0
        card['prices']['usd_foil'] = Decimal(card['prices']['usd_foil']) if card['prices']['usd_foil'] else 0
        if card['prices']['usd'] > price or unknown_usd:
            cards.append(card)
        elif card['prices']['usd_foil'] > price:
            cards.append(card)
    return cards

def visual(args):
    """ Main entry point
    """
    cards = sorted(prepare_card_data(args.set_code, price=args.price), key=lambda x: x['prices']['usd'], reverse=True)
    with open(f'{args.set_code}.csv', 'w') as fhandle:
        LOGGER.info('Writing visual CSV for set "%s"...', args.set_code)
        writer = csv.writer(fhandle)
        writer.writerow(['Card/Price', 'Qty'] * 10)
        for chunk in chunks(cards, 10):
            name_row = []
            card_row = []
            price_row = []
            for card in chunk:
                name_row.append(card['name'])
                name_row.append('')
                card_row.append(f'=IMAGE("{card["image_uris"]["small"]}")')
                card_row.append('')
                price_row.append(f'{card["prices"]["usd"]} / {card["prices"]["usd_foil"]}')
                price_row.append('')
            writer.writerow(name_row)
            writer.writerow(card_row)
            writer.writerow(price_row)
def text(args):
    """ Main entry point
    """
    cards = sorted(prepare_card_data(args.set_code, price=args.price), key=lambda x: x['name'])
    with open(f'{args.set_code}.csv', 'w') as fhandle:
        LOGGER.info('Writing visual CSV for set "%s"...', args.set_code)
        writer = csv.writer(fhandle)
        writer.writerow(['Rarity', 'Name', 'Price', 'Qty', 'FoilPrice', 'Qty', 'Notes'])
        for rarity in ['Mythic', 'Rare', 'Uncommon', 'Common']:
            writer.writerow([rarity, '', '', '', '', '', ''])
            for card in cards:
                if card['rarity'] == rarity.lower():
                    clean_name = card["name"].replace('"', '\\"')
                    writer.writerow(
                        [
                            '',
                            f'=HYPERLINK("{card["scryfall_uri"]}","{clean_name}")',
                            f'{card["prices"]["usd"]}',
                            '',
                            f'{card["prices"]["usd_foil"]}',
                            '',
                            ''
                        ]
                    )

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        '-p', '--price',
        help='The lowest price to allow',
        default=2,
        type=Decimal
    )
    PARSER.add_argument(
        '-v', '--verbose',
        help='Verbosity',
        action='count',
        default=1
    )
    SUBPARSERS = PARSER.add_subparsers()
    VISUAL_PARSE = SUBPARSERS.add_parser('visual', help='Generate list with card images, sorted by price')
    VISUAL_PARSE.set_defaults(func=visual)
    VISUAL_PARSE.add_argument(
        'set_code',
        help='Set code to tabulate by rarity'
    )
    TEXT_PARSE = SUBPARSERS.add_parser('text', help='Generate list with text only, sorted by name')
    TEXT_PARSE.set_defaults(func=text)
    TEXT_PARSE.add_argument(
        'set_code',
        help='Set code to tabulate by rarity'
    )
    BULK_PARSE = SUBPARSERS.add_parser('bulk', help='Download most recent bulk data for testing purposes.')
    BULK_PARSE.set_defaults(func=get_bulk)
    ARGS = PARSER.parse_args()
    LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]
    LEVEL = LEVELS[min(len(LEVELS)-1, ARGS.verbose)]
    LOGGER.setLevel(LEVEL)
    ARGS.func(ARGS)
