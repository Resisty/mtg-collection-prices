---
Python script for generating CSVs of cards and prices/foil prices.

Intended to be used with Scryfall bulk data.

# How

```
python set_describer.py ${set_code}
```

## Example

```
python set_describer.py ulg
```

Generates CSV of cards worth more than $2 (both foil and non-foil) from Urza's Legacy, sorted by non-foil price.

