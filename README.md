# FitFindr (EXAMPLE KEY)

## What This Does

FitFindr is an agent for thrift shopping. A user types what they want, such as "vintage graphic tee under $30", and the agent searches the listings file, picks the best match, suggests outfits using pieces from the user's wardrobe, and writes a short caption they could post. If nothing matches, it stops and tells the user what to change.

---

## Tool Inventory

### `search_listings`

- **What it does:** Searches the 40 listings for keyword matches, filtered by size and price.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None).
- **Returns:** A list of listing dicts (id, title, description, category, style_tags, size, condition, price, colors, brand, platform), best match first (most matching keywords, then lowest price), at most `config.SEARCH_RESULT_LIMIT` items. Size matching is whole-token, so "M" matches "S/M" but "S" does not match "US 9".
- **When it has nothing:** an empty list `[]`, never None and never an exception.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits using the item and the user's wardrobe.
- **Inputs:** `new_item` (dict, a listing), `wardrobe` (dict with an `items` list, which may be empty).
- **Returns:** A non-empty string of outfit suggestions that name wardrobe pieces by id.
- **When it has nothing:** With an empty wardrobe it returns general styling advice. If the model returns nothing, it returns a default one-line suggestion. It never returns "".

### `create_fit_card`

- **What it does:** Writes a 2 to 4 sentence social caption about the find.
- **Inputs:** `outfit` (str), `new_item` (dict).
- **Returns:** A caption string that mentions the price and platform.
- **When it has nothing:** If `outfit` is empty or whitespace, it returns a message string saying no outfit was provided.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what the user could change (size, budget, keywords) and return the session without calling `suggest_outfit` or `create_fit_card`. Otherwise take the first result and go on.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::parse_query`. It pulls out a price ceiling ("under $30", "$30"), a size ("size M"), and treats the rest as the description.

**What moves through the session:** `parsed`, then `search_results`, then `selected_item` (the first result), then `outfit_suggestion`, then `fit_card`. Each tool reads its input back from the session.

---

## Sample Run

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear**
Pair the butterfly baby tee with your **baggy straight-leg dark wash jeans (w_001)** for that classic contrast of fitted top and loose bottoms. Finish with **chunky white sneakers (w_007)** and the **black crossbody bag (w_010)**.

**Outfit 2: Edge & Contrast**
Layer the baby tee under your **black cropped zip hoodie (w_005)** paired with the **wide-leg khaki trousers (w_002)** for an earth-toned, early-2000s look. Ground the outfit with **black combat boots (w_008)**.

  Fit card: Obsessed with this Y2K butterfly baby tee I just scored—it literally screams 2003 in the best way possible. Pair it with baggy dark wash jeans and chunky sneakers for the ultimate fitted-top-loose-bottoms streetwear vibe, or layer it under a cropped zip hoodie with combat boots if you're leaning into that grungy earth-toned look. Grabbed it on Depop for just $18, so act fast before I change my mind and keep it for myself! 🦋✨
```

**The empty case**

```
$ python agent.py   (second query)
  stopped: No listings matched 'designer ballgown'. Try to drop or change the size (you asked for XXS), or raise your budget above $5, or use fewer or broader keywords, like 'tee' instead of a long phrase.
  fit_card is None — it should still be None here
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; r=search_listings('graphic tee', max_price=30); print(len(r), [(x['title'], x['price'], x['size']) for x in r])"
7 [('Mesh Long-Sleeve Top — Black', 15.0, 'S/M'), ('Y2K Baby Tee — Butterfly Print', 18.0, 'S/M'), ('Vintage Band Tee — Faded Grey', 19.0, 'L'), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L'), ('Oversized Crewneck Sweatshirt — Vintage Navy', 20.0, 'XL (fits oversized)'), ('Vintage Graphic Hoodie — Faded Black', 26.0, 'L'), ('Low-Rise Cargo Pants — Khaki', 27.0, 'W29')]
```

```
$ python -c "from tools import suggest_outfit; ..."
**Outfit 1: Casual Streetwear**
Pair the vintage Levi's with the **white ribbed tank top** (w_003) tucked in, layered under the **vintage black denim jacket** (w_006). Finish with **chunky white sneakers** (w_007) and the **black crossbody bag** (w_010) for an effortless, everyday look.

**Outfit 2: Cozy & Classic**
Wear the medium wash jeans with the **oversized grey crewneck sweatshirt** (w_004). Cinch the waist with the **brown leather belt** (w_009) and style with **black combat boots** (w_008) for a cool, textural contrast between vintage denim and grunge footwear.
```

```
$ python -c "from tools import create_fit_card; ..."
Scored the holy grail of denim today—a perfectly worn-in pair of vintage Levi's 501s in the ideal medium wash. They've got that effortless, effortlessly slouchy 90s vibe that's impossible to fake. Just listed these on Depop for $38 and I'm already obsessed with styling them with crisp white sneakers and a beat-up tee.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* An implementation of the three tools, with a size filter that avoids the `"s" in "us 9"` trap in the starter's notes.
- *What came back:* Whole-token size matching, a keyword-overlap score for search, and an empty-wardrobe branch in `suggest_outfit`.
- *What I changed:* I ran each tool from the terminal and read the output before wiring anything together.

**Moment 2**

- *What I asked for:* The planning loop in `agent.py`, with the empty-search branch.
- *What came back:* A step loop (parse, search, select, outfit, card) that returns early when search is empty, with an error message built from the parsed size and price.
- *What I changed:* I ran both example queries and checked that the second stopped with `fit_card` still None.

---

## Run Log — Before

(Filled in next unit.)

## Verdicts and Diagnoses

(Filled in next unit.)

## Loop Trace

(Filled in next unit.)

## The Improvement

(Filled in next unit.)

## What's Still Broken

(Filled in next unit.)