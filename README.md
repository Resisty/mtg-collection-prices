---
Python script for generating CSVs of cards and prices/foil prices.

Intended to be used with Scryfall bulk data.

# How

```
usage: set_describer.py [-h] [-v] {visual,text,bulk} ...

positional arguments:
  {visual,text,bulk}
    visual            Generate list with card images, sorted by price
    text              Generate list with text only, sorted by name
    bulk              Download most recent bulk data for testing purposes.

optional arguments:
  -h, --help          show this help message and exit
  -v, --verbose       Verbosity
```

## Example

```
python set_describer.py visual ulg
```

Generates CSV of card images worth more than $2 (both foil and non-foil) from Urza's Legacy, sorted by non-foil price.

