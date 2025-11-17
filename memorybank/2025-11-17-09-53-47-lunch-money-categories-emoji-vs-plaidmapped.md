---
filename: 2025-11-17-09-53-47-lunch-money-categories-emoji-vs-plaidmapped
timestamp: '2025-11-17T09:53:47.790031+00:00'
title: 'Lunch Money categories: emoji vs Plaid-mapped'
---

In Lunch Money, Howard's categories appear to come from two distinct bulk-creation events:

- Emoji-based category groups and children (e.g. "🍔 Food and Drinks", "🎉 Entertainment", etc.)
  - All created within a very tight window around 2025-11-15T19:23:31–19:23:32Z
  - Represent the main, human-friendly budget structure (groups + subcategories).

- Plain-text categories without emojis (e.g. "Online marketplaces", "Tv and movies", "Other general merchandise")
  - All created within another tight window around 2025-11-15T19:31:44–19:31:45Z
  - Names closely mirror Plaid personal_finance_category.detailed values (for example,
    "Tv and movies" ↔ ENTIRETTAINMENT_TV_AND_MOVIES, "Online marketplaces" ↔ GENERAL_MERCHANDISE_ONLINE_MARKETPLACES,
    "Other general services" ↔ GENERAL_SERVICES_OTHER_GENERAL_SERVICES, etc.).
  - These plain categories are very likely auto-mapped / auto-generated from Plaid’s enriched categories.

The category objects themselves do not expose an explicit flag for origin (no `source` or `plaid_mapped` field),
so this conclusion is based on:

1. Bulk creation timestamps for each set.
2. Name alignment between plain-text categories and Plaid personal_finance_category.detailed codes.

Practical takeaway: emoji categories are the primary LM-defined structure; the non-emoji, plain categories form
an auto-generated layer that mirrors Plaid’s categorization, even though the API does not explicitly label them as such.
