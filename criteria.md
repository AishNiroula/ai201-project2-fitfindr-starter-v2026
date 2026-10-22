# Acceptance criteria — FitFindr (EXAMPLE KEY)

Written before testing. Criteria 1 and 2 were given; 3 to 5 are mine.

---

## 1.

Given a query that matches at least one listing, the agent completes all three tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** My search is a plain keyword match, so some phrasings will miss. 4 of 5 allows one miss without calling it working.

---

## 2.

Given a query that matches no listings, the agent stops before calling suggest_outfit and returns a message naming what to change — 5 of 5 tries.

**Why this target:** This is plain code with no model involved, so it should never fail.

---

## 3. (state)

In 5 of 5 tries on a matching query, `session["selected_item"]["id"]` equals `session["search_results"][0]["id"]`, and the fit card mentions that item's price.

**Why this target:** If the id matches and the price in the caption matches the listing, the same item flowed through all three tools without the user retyping it. Plain code, so 5 of 5.

---

## 4. (fit card)

Across 5 runs of the same query with the cache off, every fit card is 2 to 4 sentences and names the price and platform, and at least 3 of the 5 are not word-for-word identical.

**Why this target:** The caption calls a model, so wording will vary. I don't need every run different, but 5 identical runs would mean caching or zero temperature.

---

## 5. (filters)

For 5 queries that include a size and a price limit, every result has price at or below the limit and a size that matches as a whole token (so "S" never returns "US 9") — 100% of results in 5 of 5 queries.

**Why this target:** The starter warns that a loose size test returns shoes for a small top. One wrong result makes the search look broken.