"""The FitFindr planning loop (EXAMPLE KEY)."""

import re

import config  # noqa: F401
import trace
from generate import ModelUnavailable
from tools import search_listings, suggest_outfit, create_fit_card


def new_session(query, wardrobe):
    return {
        "query": query, "parsed": {}, "search_results": [],
        "selected_item": None, "wardrobe": wardrobe,
        "outfit_suggestion": None, "fit_card": None, "error": None,
    }


def parse_query(query):
    """Regex parse: price ceiling, size, and what's left is the description."""
    text, max_price, size = query, None, None
    m = re.search(r"(?:under|below|less than|max|up to|<=?)\s*\$?\s*(\d+(?:\.\d+)?)"
                  r"|\$\s*(\d+(?:\.\d+)?)", text, re.I)
    if m:
        max_price = float(m.group(1) or m.group(2))
        text = text.replace(m.group(0), " ")
    m = re.search(r"\bsize\s*:?\s*([A-Za-z0-9/]+)", text, re.I)
    if m:
        size = m.group(1)
        text = text.replace(m.group(0), " ")
    description = re.sub(r"[,.]", " ", text)
    description = re.sub(r"\s+", " ", description).strip()
    return {"description": description, "size": size, "max_price": max_price}


def _empty_message(parsed):
    tips = []
    if parsed.get("size"):
        tips.append(f"drop or change the size (you asked for {parsed['size']})")
    if parsed.get("max_price") is not None:
        tips.append(f"raise your budget above ${parsed['max_price']:g}")
    tips.append("use fewer or broader keywords, like 'tee' instead of a long phrase")
    return (f"No listings matched '{parsed.get('description')}'. Try to "
            + ", or ".join(tips) + ".")


def run_agent(query, wardrobe):
    """Branch rule: if search_listings returns [], set session['error'] with what
    to change and return before suggest_outfit. Otherwise take the first result."""
    session = new_session(query, wardrobe)
    step, count = "parse", 0
    try:
        while step != "done":
            count += 1
            trace.check_iterations(count)
            if step == "parse":
                session["parsed"] = parse_query(session["query"])
                step = "search"
            elif step == "search":
                p = session["parsed"]
                session["search_results"] = search_listings(
                    p["description"], p["size"], p["max_price"])
                if not session["search_results"]:          # <-- THE BRANCH
                    session["error"] = _empty_message(p)
                    return session
                step = "select"
            elif step == "select":
                session["selected_item"] = session["search_results"][0]
                step = "outfit"
            elif step == "outfit":
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"], session["wardrobe"])
                step = "card"
            elif step == "card":
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"], session["selected_item"])
                step = "done"
    except ModelUnavailable as exc:
        session["error"] = str(exc)
    return session


def _show(session):
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return
    item = session["selected_item"] or {}
    print(f"  found: {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit: {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe
    print("=== A query the data can match ===")
    _show(run_agent("looking for a vintage graphic tee under $30", get_example_wardrobe()))
    print("\n=== A query it can't ===")
    _show(run_agent("designer ballgown size XXS under $5", get_example_wardrobe()))