"""The three FitFindr tools (EXAMPLE KEY)."""

import json
import re

import config
from generate import generate
from utils.data_loader import load_listings

_FILLER = {"a", "an", "the", "for", "in", "and", "or", "with", "of", "to",
           "looking", "want", "need", "find", "me", "some", "something", "i"}
_SIZE_WORDS = {"small": "s", "medium": "m", "large": "l", "xlarge": "xl"}


def _tokens(text):
    return re.findall(r"[a-z0-9]+", str(text or "").lower())


def _stem(word):
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


def _size_matches(wanted, have):
    """Whole-token match: 'M' matches 'S/M' but 's' does not match 'US 9'."""
    if not wanted:
        return True
    want = {_SIZE_WORDS.get(t, t) for t in _tokens(wanted)}
    return bool(want & set(_tokens(have)))


def search_listings(description, size=None, max_price=None):
    """Return matching listing dicts, best first. [] when nothing matches."""
    keywords = {_stem(t) for t in _tokens(description) if t not in _FILLER}
    scored = []
    for item in load_listings():
        price = item.get("price")
        if max_price is not None and (price is None or price > max_price):
            continue
        if not _size_matches(size, item.get("size")):
            continue
        haystack = " ".join([
            str(item.get("title", "")), str(item.get("description", "")),
            str(item.get("category", "")), " ".join(item.get("style_tags") or []),
            " ".join(item.get("colors") or []), str(item.get("brand") or ""),
        ])
        words = {_stem(t) for t in _tokens(haystack)}
        score = len(keywords & words)
        if score > 0:
            scored.append((score, price or 0, item))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [s[2] for s in scored][: config.SEARCH_RESULT_LIMIT]


def _describe(item):
    return (f"{item.get('title')} (${item.get('price')}, size {item.get('size')}, "
            f"{item.get('condition')}, on {item.get('platform')})")


def suggest_outfit(new_item, wardrobe):
    """One or two outfit ideas. Never returns an empty string."""
    items = (wardrobe or {}).get("items") or []
    if not items:
        prompt = (f"Someone is considering this thrifted item: {_describe(new_item)}. "
                  f"Tags: {new_item.get('style_tags')}. They have not told me what "
                  f"they own. Give one or two general outfit ideas in under 90 words.")
    else:
        owned = "\n".join(f"- {json.dumps(i)[:160]}" for i in items)
        prompt = (f"A person is considering this thrifted item: {_describe(new_item)}. "
                  f"Their wardrobe:\n{owned}\n\nSuggest one or two outfits that name "
                  f"specific pieces they already own. Under 120 words.")
    text = generate(prompt)
    return text or f"Pair the {new_item.get('title')} with simple basics and clean shoes."


def create_fit_card(outfit, new_item):
    """A 2-4 sentence caption. Returns a message if there is no outfit."""
    if not outfit or not outfit.strip():
        return "No outfit was provided, so there is no fit card to write."
    prompt = (
        f"Write a 2-4 sentence social post about a thrift find. Item: "
        f"{new_item.get('title')}. Price: ${new_item.get('price')}. Platform: "
        f"{new_item.get('platform')}. Outfit idea: {outfit}\n"
        f"Mention the price and the platform once each, be specific about the "
        f"vibe, and sound like a real person, not a product listing."
    )
    return generate(prompt) or "Couldn't write a caption this time."