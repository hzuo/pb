Scraped using Firecrawl from: https://lunchmoney.dev/

[NAV\\
 ![](https://lunchmoney.dev/images/navbar-cad8cdcb.png)](https://lunchmoney.dev/#)

![](https://lunchmoney.dev/images/logo-9c134457.png)Lunch Money

Developer API

- [Getting Started](https://lunchmoney.dev/#getting-started)  - [Current Status](https://lunchmoney.dev/#current-status)
  - [Connecting to the Lunch Money API](https://lunchmoney.dev/#connecting-to-the-lunch-money-api)
  - [Authentication](https://lunchmoney.dev/#authentication)
  - [What should I build?](https://lunchmoney.dev/#what-should-i-build)
- [Awesome Projects](https://lunchmoney.dev/#awesome-projects)
- [Changelog](https://lunchmoney.dev/#changelog)  - [Feb 6, 2025](https://lunchmoney.dev/#feb-6-2025)
  - [Feb 3, 2025](https://lunchmoney.dev/#feb-3-2025)
  - [Dec 20, 2024](https://lunchmoney.dev/#dec-20-2024)
  - [June 15, 2024](https://lunchmoney.dev/#june-15-2024)
  - [March 27, 2024](https://lunchmoney.dev/#march-27-2024)
  - [January 18, 2024](https://lunchmoney.dev/#january-18-2024)
  - [December 20, 2023](https://lunchmoney.dev/#december-20-2023)
  - [October 8, 2023](https://lunchmoney.dev/#october-8-2023)
  - [June 22, 2022](https://lunchmoney.dev/#june-22-2022)
  - [June 4, 2022](https://lunchmoney.dev/#june-4-2022)
  - [August 31, 2021](https://lunchmoney.dev/#august-31-2021)
  - [June 9, 2021](https://lunchmoney.dev/#june-9-2021)
  - [May 27, 2021](https://lunchmoney.dev/#may-27-2021)
  - [March 28, 2020](https://lunchmoney.dev/#march-28-2020)
- [FAQ](https://lunchmoney.dev/#faq)  - [The endpoint I need is not listed. Can you add it?](https://lunchmoney.dev/#the-endpoint-i-need-is-not-listed-can-you-add-it)
  - [What currencies are supported?](https://lunchmoney.dev/#what-currencies-are-supported)
  - [I’ve built something! Now what?](https://lunchmoney.dev/#i-ve-built-something-now-what)
  - [Where can I get support?](https://lunchmoney.dev/#where-can-i-get-support)
- [User](https://lunchmoney.dev/#user)  - [User Object](https://lunchmoney.dev/#user-object)
  - [Get User](https://lunchmoney.dev/#get-user)
- [Categories](https://lunchmoney.dev/#categories)  - [Categories Object](https://lunchmoney.dev/#categories-object)
  - [Get All Categories](https://lunchmoney.dev/#get-all-categories)
  - [Get Single Category](https://lunchmoney.dev/#get-single-category)
  - [Create Category](https://lunchmoney.dev/#create-category)
  - [Create Category Group](https://lunchmoney.dev/#create-category-group)
  - [Update Category](https://lunchmoney.dev/#update-category)
  - [Add to Category Group](https://lunchmoney.dev/#add-to-category-group)
  - [Delete Category](https://lunchmoney.dev/#delete-category)
  - [Force Delete Category](https://lunchmoney.dev/#force-delete-category)
- [Tags](https://lunchmoney.dev/#tags)  - [Tags Object](https://lunchmoney.dev/#tags-object)
  - [Get All Tags](https://lunchmoney.dev/#get-all-tags)
- [Transactions](https://lunchmoney.dev/#transactions)  - [Transaction Object](https://lunchmoney.dev/#transaction-object)
  - [Get All Transactions](https://lunchmoney.dev/#get-all-transactions)
  - [Get Single Transaction](https://lunchmoney.dev/#get-single-transaction)
  - [Insert Transactions](https://lunchmoney.dev/#insert-transactions)
  - [Update Transaction](https://lunchmoney.dev/#update-transaction)
  - [Unsplit Transactions](https://lunchmoney.dev/#unsplit-transactions)
  - [Get Transaction Group](https://lunchmoney.dev/#get-transaction-group)
  - [Create Transaction Group](https://lunchmoney.dev/#create-transaction-group)
  - [Delete Transaction Group](https://lunchmoney.dev/#delete-transaction-group)
- [Recurring Expenses](https://lunchmoney.dev/#recurring-expenses)  - [Recurring Expenses Object](https://lunchmoney.dev/#recurring-expenses-object)
  - [Get Recurring Expenses](https://lunchmoney.dev/#get-recurring-expenses)
- [Recurring Items](https://lunchmoney.dev/#recurring-items)  - [Recurring Items Object](https://lunchmoney.dev/#recurring-items-object)
  - [Summarized Transaction Object](https://lunchmoney.dev/#summarized-transaction-object)
  - [Get Recurring Items](https://lunchmoney.dev/#get-recurring-items)
- [Budget](https://lunchmoney.dev/#budget)  - [Budget Object](https://lunchmoney.dev/#budget-object)
  - [Data Object](https://lunchmoney.dev/#data-object)
  - [Config Object](https://lunchmoney.dev/#config-object)
  - [Get Budget Summary](https://lunchmoney.dev/#get-budget-summary)
  - [Upsert Budget](https://lunchmoney.dev/#upsert-budget)
  - [Remove Budget](https://lunchmoney.dev/#remove-budget)
- [Assets](https://lunchmoney.dev/#assets)  - [Assets Object](https://lunchmoney.dev/#assets-object)
  - [Get All Assets](https://lunchmoney.dev/#get-all-assets)
  - [Create Asset](https://lunchmoney.dev/#create-asset)
  - [Update Asset](https://lunchmoney.dev/#update-asset)
- [Plaid Accounts](https://lunchmoney.dev/#plaid-accounts)  - [Plaid Accounts Object](https://lunchmoney.dev/#plaid-accounts-object)
  - [Get All Plaid Accounts](https://lunchmoney.dev/#get-all-plaid-accounts)
  - [Trigger Fetch from Plaid](https://lunchmoney.dev/#trigger-fetch-from-plaid)
- [Crypto](https://lunchmoney.dev/#crypto)  - [Crypto Object](https://lunchmoney.dev/#crypto-object)
  - [Get All Crypto](https://lunchmoney.dev/#get-all-crypto)
  - [Update Manual Crypto Asset](https://lunchmoney.dev/#update-manual-crypto-asset)
- [Appendix](https://lunchmoney.dev/#appendix)  - [Supported Currencies](https://lunchmoney.dev/#supported-currencies)

- [View on GitHub](https://github.com/lunch-money/developers)

# Getting Started

Welcome to the Lunch Money developer API! We created this to enable the user and the community to build rich plug-ins to complement their Lunch Money experience.

* * *

## Current Status

The developer API is officially in open public beta. Based on feedback received we have begun design on a v2 API.

During this time, please use this API at your own risk as and be aware that changes made to your data via the API are irreversible.

If you would like to review and provide feedback on the v2 API design in progress, please [email our developer advocate](mailto:jp@lunchmoney.app).

You can also [join the Lunch Money community on Discord](https://lunchmoney.app/discord) and provide feedback in the [Developer API Channel](https://discord.com/channels/842337014556262411/1134594318414389258).

You can find these docs [on Github](https://github.com/lunch-money/developers), so if you see a mistake or something that could be improved, feel free to open a pull request!

## Connecting to the Lunch Money API

### Connect to the server

The Lunch Money API endpoint is: `https://dev.lunchmoney.app`

For POST requests, ensure you set Content-Type to application/json

## Authentication

> Use Bearer Tokens in your requests like this:
>
> Recommended

```
Copy to Clipboard
https://dev.lunchmoney.app/v1/categories

with the Authorization header field set to Bearer YOURACCESSTOKEN
```

> Not Recommended

```
Copy to Clipboard
https://dev.lunchmoney.app/v1/categories?access_token=YOURACCESSTOKEN
```

Lunch Money API requests are authenticated using the Bearer Token authentication method.

### Getting an access token

Get your access token by going to [the developers page in the Lunch Money app](https://my.lunchmoney.app/developers).

## What should I build?

**Great question!** We’ve tried to expose the minimum endpoints needed to enable you to build powerful products and extensions.

Here are a few ideas of what you can build:

### Basic use cases

**Integration with your bank**

Does your bank offer an API? You can build a bridge between Lunch Money and your bank to import transactions automatically.

**Sync Lunch Money data to your personal interface**

If you have your own spreadsheet or other interface, use the API to sync data for personalized viewing and analytics.

### Specific use cases with high demand:

**Amazon receipt matcher**

Do you make a lot of Amazon purchases? I'm sure by now you know how frustrating it is to try to identify exactly what the expense is for! Build an Amazon receipt matcher that pulls in your Amazon purchase history and matches on transactions in Lunch Money and updates the notes.

Note: apparently Amazon’s API doesn't expose consumer transactions, so to achieve this, you may need to employ another method of getting transaction details (ideas: email forwarder, chrome extension/screen scraper…)

**Venmo integration via email**

The lack of a Venmo and Plaid integration is frustrating for many of our users and is largely out of our control. Since Venmo sends an email notification every time you send or receive money, build a service that enables users to forward their Venmo notification emails for parsing and insertion into Lunch Money!

**Zillow integration**

Create an integration that automatically updates the value of a real estate property in Lunch Money.

* * *

# Awesome Projects

If you are looking for inspiration, or just want to make sure you aren't building something that already exists you can find a list of [awesome Lunch Money projects on GitHub](https://github.com/lunch-money/awesome-lunchmoney).

You can also [join the Lunch Money community on Discord](https://lunchmoney.app/discord) and check out the [Show and Tell channel](https://discord.com/channels/842337014556262411/1134597088504729780) to see what projects community members are sharing.

Did you create something with the Lunch Money API? Let us know and we'll add it to this list!

* * *

# Changelog

A log of changes. Breaking changes will be denoted with 🚨

## Feb 6, 2025

- The [Assets Object](https://lunchmoney.dev/#assets-object) and [Plaid Accounts Object](https://lunchmoney.dev/#plaid-accounts-object) now include a `to_base` property which shows the account balance converted to the user's primary currency.

## Feb 3, 2025

- The [Update Transaction Object](https://lunchmoney.dev/#update-transaction-object) now accepts a `plaid_account_id` allowing developers to update existing transactions associated with plaid accounts or to move transactions to a plaid account if the "Allow Modifications to Transactions" property is set.
- The bug in the [GET /transactions/{id}](https://lunchmoney.dev/#get-single-transaction) endpoint where the `debit_as_negative` query param was ignored has been fixed.

## Dec 20, 2024

- The [Transaction Insert Object](https://lunchmoney.dev/#transaction-object-to-insert) now accepts a `plaid_account_id` allowing developers to insert transactions associated with plaid accounts if the "Allow Modifications to Transactions" property is set.
- The bug that prevented users from inserting transactions with the same `asset_id`/`external_id` as a previously deleted transaction has been fixed.

## June 15, 2024

- New endpoint: [GET /v1/recurring\_items](https://lunchmoney.dev/#get-recurring-items)
- Deprecated the [GET /v1/recurring\_expenses](https://lunchmoney.dev/#get-recurring-expenses) endpoint in favor of the new recurring\_items endpoint

## March 27, 2024

### Updated

- 🚨 Deprecated `transaction_id` in [Recurring Expenses Object](https://lunchmoney.dev/#recurring-expenses-object) (temporarily... it will come back in another form)
- 🚨 Deprecated special statuses for transactions (`recurring` and `recurring_suggested`)

## January 18, 2024

### New

- New endpoint: [GET /v1/transactions/group](https://lunchmoney.dev/#get-transaction-group)
- New fields for [Transaction object](https://lunchmoney.dev/#transaction-object) and deprecated query parameter (`group_id`) and fields (`type`, `subtype`, `quantity`, `fee`, `price`)

## December 20, 2023

### New

- New endpoint: [POST /v1/plaid\_accounts/fetch](https://lunchmoney.dev/#trigger-fetch-from-plaid) (experimental)

## October 8, 2023

### Updated

- New fields for [GET /v1/categories](https://lunchmoney.dev/#get-all-categories): order
- New option for [GET /v1/categories](https://lunchmoney.dev/#get-all-categories): format (flattened or nested)

## June 22, 2022

### New

- New endpoint: [POST /v1/transactions/unsplit](https://lunchmoney.dev/#unsplit-transactions)

## June 4, 2022

### New

- Lots of new endpoints for [categories](https://lunchmoney.dev/#categories) with support for [category groups](https://lunchmoney.dev/#create-category-group)

## August 31, 2021

### Updated

- New fields for [GET /v1/budgets](https://lunchmoney.dev/#get-budget-summary): config

## June 9, 2021

### New

- New endpoint: [POST /v1/transactions/group](https://lunchmoney.dev/#create-transaction-group)
- New endpoint: [DELETE /v1/transactions/group/:transaction\_id](https://lunchmoney.dev/#delete-transaction-group)

### Updated

- New option for [POST /v1/transactions](https://lunchmoney.dev/#insert-transactions) and [PUT /v1/transactions](https://lunchmoney.dev/#update-transaction): skip\_balance\_update
- New fields for [GET /v1/transactions](https://lunchmoney.dev/#get-all-transactions): original\_name, type, subtype, fees, price, quantity
- New filter options for [GET /v1/transactions](https://lunchmoney.dev/#get-all-transactions): status, is\_group, group\_id

## May 27, 2021

### New

- New endpoint: [GET /v1/budgets](https://lunchmoney.dev/#get-budget-summary)
- New endpoint: [GET /v1/crypto](https://lunchmoney.dev/#get-all-crypto)
- New endpoint: [PUT /v1/crypto/manual/:id](https://lunchmoney.dev/#update-manual-crypto-asset)

### Updated

- New fields for [GET /v1/assets](https://lunchmoney.dev/#get-all-assets): display\_name and closed\_on

## March 28, 2020

### New

- Pagination options for [GET /v1/transactions](https://lunchmoney.dev/#get-all-transactions): limit and offset
- Filter options for [GET /v1/transactions](https://lunchmoney.dev/#get-all-transactions): asset\_id, recurring\_id, plaid\_account\_id, tag\_id, category\_id
- New endpoint: [GET /v1/budget](https://lunchmoney.dev/#get-all-tags)

### Updated

- Support for tags in [PUT /v1/transactions/:id](https://lunchmoney.dev/#update-transaction) and [POST /v1/transactions](https://lunchmoney.dev/#insert-transactions)
- 🚨Split object for [splitting transactions](https://lunchmoney.dev/#update-transaction) is moved out of the Transactions object and to a higher-level. We will still support the split property for a few more weeks before removing it completely.

* * *

# FAQ

## The endpoint I need is not listed. Can you add it?

If you would like a specific endpoint which is not currently supported, please let us know by emailing [support@lunchmoney.app](mailto:support@lunchmoney.app) and stating your use case.

## What currencies are supported?

Check [here](https://lunchmoney.dev/#supported-currencies) for a list of all the currencies we currently support. If a currency is missing, let us know via email and we’ll try to get it added!

## I’ve built something! Now what?

Awesome! Please share with us via email about what you built! If you are willing to share your code, we encourage you to open-source your tool/plug-in so others in the Lunch Money community can benefit and we'll add it to our [Awesome Projects](https://lunchmoney.dev/#awesome-projects) page.

## Where can I get support?

[Join our Discord community](https://discord.gg/vSz6jjZuj8) and chat with us in the `💻-developer-api` channel! For account-specific issues, email us at [support@lunchmoney.app](mailto:support@lunchmoney.app).

* * *

# User

## User Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| user\_id | number | false | Unique identifier for user |
| user\_name | string | false | User's name |
| user\_email | string | false | User's email |
| account\_id | number | false | Unique identifier for the associated budgeting account |
| budget\_name | string | false | Name of the associated budgeting account |
| primary\_currency | string | false | Primary currency from user's settings |
| api\_key\_label | string | true | User-defined label of the developer API key used. Returns null if nothing has been set. |

## Get User

Use this endpoint to get details on the current user.

```
Copy to Clipboard
{
  "user_name": "User 1",
  "user_email": "user-1@lunchmoney.dev",
  "user_id": 18328,
  "account_id": 18221,
  "budget_name": "🏠 Family budget",
  "primary_currency": "usd",
  "api_key_label": "Side project dev key"
}
```

### HTTP Request

`GET https://dev.lunchmoney.app/v1/me`

* * *

# Categories

## Categories Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | false | A unique identifier for the category. |
| name | string | false | The name of the category. Must be between 1 and 40 characters. |
| description | string | true | The description of the category. Must not exceed 140 characters. |
| is\_income | boolean | false | If true, the transactions in this category will be treated as income. |
| exclude\_from\_budget | boolean | false | If true, the transactions in this category will be excluded from the budget. |
| exclude\_from\_totals | boolean | false | If true, the transactions in this category will be excluded from totals. |
| archived | boolean | true | If true, the category is archived and not displayed in relevant areas of the Lunch Money app. |
| archived\_on | string | true | The date and time of when the category was last archived (in the ISO 8601 extended format). |
| updated\_at | string | true | The date and time of when the category was last updated (in the ISO 8601 extended format). |
| created\_at | string | true | The date and time of when the category was created (in the ISO 8601 extended format). |
| is\_group | boolean | false | If true, the category is a group that can be a parent to other categories. |
| group\_id | number | true | The ID of a category group (or null if the category doesn't belong to a category group). |
| order | number | true | Numerical ordering of categories |
| children | array of objects | true | For category groups, this will populate with the categories nested within and include id, name, description and created\_at fields. |
| group\_category\_name | string | true | For grouped categories, the name of the category group |

## Get All Categories

Use this endpoint to get a flattened list of all categories in alphabetical order associated with the user's account.

```
Copy to Clipboard
{
  "categories": [\
    {\
      "id": 83,\
      "name": "Test 1",\
      "description": "Test description",\
      "is_income": false,\
      "exclude_from_budget": true,\
      "exclude_from_totals": false,\
      "updated_at": "2020-01-28T09:49:03.225Z",\
      "created_at": "2020-01-28T09:49:03.225Z",\
      "is_group": false,\
      "group_id": null,\
      "order": 0\
    },\
    {\
      "id": 84,\
      "name": "Test 2",\
      "description": null,\
      "is_income": true,\
      "exclude_from_budget": false,\
      "exclude_from_totals": true,\
      "updated_at": "2020-01-28T09:49:03.238Z",\
      "created_at": "2020-01-28T09:49:03.238Z",\
      "is_group": true,\
      "group_id": 83,\
      "order": 1,\
      "children": [\
        {\
          "id": 315162,\
          "name": "Alcohol, Bars",\
          "description": null,\
          "created_at": "2022-03-06T20:11:36.066Z"\
        },\
        {\
          "id": 315169,\
          "name": "Groceries",\
          "description": null,\
          "created_at": "2022-03-06T20:11:36.120Z"\
        },\
        {\
          "id": 315172,\
          "name": "Restaurants",\
          "description": null,\
          "created_at": "2022-03-06T20:11:36.146Z"\
        }\
      ]\
    }\
  ]
}
```

### HTTP Request

`GET https://dev.lunchmoney.app/v1/categories`

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| format | string | false | flattened | Can either `flattened` or `nested`. If `flattened`, returns a singular array of categories, ordered alphabetically. If `nested`, returns top-level categories (either category groups or categories not part of a category group) in an array. Subcategories are nested within the category group under the property `children`. |

## Get Single Category

Use this endpoint to get hydrated details on a single category. Note that if this category is part of a category group, its properties (is\_income, exclude\_from\_budget, exclude\_from\_totals) will inherit from the category group.

```
Copy to Clipboard
{
  "id": 315358,
  "name": "Food & Drink",
  "description": null,
  "is_income": false,
  "exclude_from_budget": false,
  "exclude_from_totals": false,
  "archived": false,
  "archived_on": null,
  "is_group": true,
  "group_id": null,
  "order": 5,
  "children": [\
    {\
      "id": 315162,\
      "name": "Alcohol, Bars",\
      "description": null,\
      "created_at": "2022-03-06T20:11:36.066Z"\
    },\
    {\
      "id": 315169,\
      "name": "Groceries",\
      "description": null,\
      "created_at": "2022-03-06T20:11:36.120Z"\
    },\
    {\
      "id": 315172,\
      "name": "Restaurants",\
      "description": null,\
      "created_at": "2022-03-06T20:11:36.146Z"\
    }\
  ]
}
```

### HTTP Request

`GET https://dev.lunchmoney.app/v1/categories/:category_id`

## Create Category

Use this endpoint to create a single category

> Example 200 Response
>
> Returns the ID of the newly-created category

```
Copy to Clipboard
{
  "category_id": 26213
}
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{ "error": "Missing category name." }
```

```
Copy to Clipboard
{ "error": "Category name must be less than 40 characters." }
```

```
Copy to Clipboard
{ "error": "Category description must be less than 140 characters." }
```

```
Copy to Clipboard
{
  "error": "Operation error occurred. Please try again or contact support@lunchmoney.app for assistance."
}
```

### HTTP Request

`POST https://dev.lunchmoney.app/v1/categories`

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| name | string | true | - | Name of category. Must be between 1 and 40 characters. |
| description | string | false | - | Description of category. Must be less than 140 categories. |
| is\_income | boolean | false | false | Whether or not transactions in this category should be treated as income. |
| exclude\_from\_budget | boolean | false | false | Whether or not transactions in this category should be excluded from budgets. |
| exclude\_from\_totals | boolean | false | false | Whether or not transactions in this category should be excluded from calculated totals. |
| archived | boolean | false | false | Whether or not category should be archived. |
| group\_id | number | false | - | Assigns the newly-created category to an existing category group. |

## Create Category Group

Use this endpoint to create a single category group

> Example 200 Response
>
> Returns the ID of the newly-created category group

```
Copy to Clipboard
{
  "category_id": 26213
}
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{ "error": "Missing category name." }
```

```
Copy to Clipboard
{
  "error": "A category with the same name (sample_duplicate_name) already exists."
}
```

```
Copy to Clipboard
{
  "error": "The following category id(s) could not be added as a group because you do not have permissions for this category, or it is already a category group: 3893"
}
```

### HTTP Request

`POST https://dev.lunchmoney.app/v1/categories/group`

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| name | string | true | - | Name of category. Must be between 1 and 40 characters. |
| description | string | false | - | Description of category. Must be less than 140 categories. |
| is\_income | boolean | false | false | Whether or not transactions in this category should be treated as income. |
| exclude\_from\_budget | boolean | false | false | Whether or not transactions in this category should be excluded from budgets. |
| exclude\_from\_totals | boolean | false | false | Whether or not transactions in this category should be excluded from calculated totals. |
| category\_ids | array of numbers | false | - | Array of category\_id to include in the category group. |
| new\_categories | array of strings | false | - | Array of strings representing new categories to create and subsequently include in the category group. |

## Update Category

Use this endpoint to update the properties for a single category or category group

> Example 200 Response
>
> If successfully updated, returns true

```
Copy to Clipboard
true
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{ "error": "No valid fields to update for this category." }
```

```
Copy to Clipboard
{ "error": "You may not set the is_group property for an existing category." }
```

```
Copy to Clipboard
{
  "error": "This category cannot be assigned a group because it is a category group."
}
```

```
Copy to Clipboard
{
  "error": "Operation error occurred. Please try again or contact support@lunchmoney.app for assistance."
}
```

### HTTP Request

`PUT https://dev.lunchmoney.app/v1/categories/:category_id`

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| name | string | false | - | Name of category. Must be between 1 and 40 characters. |
| description | string | false | - | Description of category. Must be less than 140 categories. |
| is\_income | boolean | false | false | Whether or not transactions in this category should be treated as income. |
| exclude\_from\_budget | boolean | false | false | Whether or not transactions in this category should be excluded from budgets. |
| exclude\_from\_totals | boolean | false | false | Whether or not transactions in this category should be excluded from calculated totals. |
| archived | boolean | false | false | Whether or not category should be archived. |
| group\_id | number | false | false | For a category, set the group\_id to include it in a category group |

## Add to Category Group

Use this endpoint to add categories (either existing or new) to a single category group

> Example 200 Response
>
> Returns the hydrated object for the category group

```
Copy to Clipboard
{
  "id": 315358,
  "name": "Food & Drink",
  "description": null,
  "is_income": false,
  "exclude_from_budget": false,
  "exclude_from_totals": false,
  "is_group": true,
  "group_id": null,
  "children": [\
    {\
      "id": 315162,\
      "name": "Alcohol, Bars",\
      "description": null,\
      "created_at": "2022-03-06T20:11:36.066Z"\
    },\
    {\
      "id": 315164,\
      "name": "Coffee Shops",\
      "description": null,\
      "created_at": "2022-03-06T20:11:36.082Z"\
    },\
    {\
      "id": 315169,\
      "name": "Groceries",\
      "description": null,\
      "created_at": "2022-03-06T20:11:36.120Z"\
    },\
    {\
      "id": 315172,\
      "name": "Restaurants",\
      "description": null,\
      "created_at": "2022-03-06T20:11:36.146Z"\
    }\
  ]
}
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{
  "error": "The following category id(s) could not be added as a group because you do not have permissions for this category, or it is already a category group: 3280"
}
```

```
Copy to Clipboard
{
  "error": "Operation error occurred. Please try again or contact support@lunchmoney.app for assistance."
}
```

### HTTP Request

`POST https://dev.lunchmoney.app/v1/categories/group/:group_id/add`

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| category\_ids | array of numbers | false | - | Array of category\_id to include in the category group. |
| new\_categories | array of strings | false | - | Array of strings representing new categories to create and subsequently include in the category group. |

## Delete Category

Use this endpoint to delete a single category or category group. This will only work if there are no dependencies, such as existing budgets for the category, categorized transactions, categorized recurring items, etc. If there are dependents, this endpoint will return what the dependents are and how many there are.

> Example 200 Response
>
> If successfully deleted, returns true

```
Copy to Clipboard
true
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{
  "dependents": {
    "category_name": "Food & Drink",
    "budget": 4,
    "category_rules": 0,
    "transactions": 43,
    "children": 7,
    "recurring": 0
  }
}
```

### HTTP Request

`DELETE https://dev.lunchmoney.app/v1/categories/:category_id`

## Force Delete Category

Use this endpoint to force delete a single category or category group and along with it, disassociate the category from any transactions, recurring items, budgets, etc.

_Note: it is best practice to first try the `Delete Category` endpoint to ensure you don't accidentally delete any data. Disassociation/deletion of the data arising from this endpoint is irreversible!_

> Example 200 Response
>
> If successfully deleted, returns true

```
Copy to Clipboard
true
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{
  "error": "Operation error occurred. Please try again or contact support@lunchmoney.app for assistance."
}
```

### HTTP Request

`DELETE https://dev.lunchmoney.app/v1/categories/:category_id/force`

* * *

# Tags

## Tags Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | false | Unique identifier for tag |
| name | string | false | User-defined name of tag |
| description | string | true | User-defined description of tag |
| archived | boolean | false | If true, the tag will not show up when creating or updating transactions in the Lunch Money app |

## Get All Tags

Use this endpoint to get a list of all tags associated with the user's account.

```
Copy to Clipboard
[\
    {\
        "id": 1807,\
        "name": "Wedding",\
        "description": "All wedding-related expenses",\
        "archived": false\
    },\
    {\
        "id": 1808,\
        "name": "Honeymoon",\
        "description": "All honeymoon-related expenses",\
        "archived": true\
    }\
]
```

### HTTP Request

`GET https://dev.lunchmoney.app/v1/tags`

* * *

# Transactions

## Transaction Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | false | Unique identifier for transaction |
| date | string | false | Date of transaction in ISO 8601 format |
| payee | string | false | Name of payee. If recurring\_id is not null, this field will show the payee of associated recurring expense instead of the original transaction payee |
| amount | string | false | Amount of the transaction in numeric format to 4 decimal places |
| currency | string | false | Three-letter lowercase currency code of the transaction in ISO 4217 format |
| to\_base | number | false | The amount converted to the user's primary currency. If the multicurrency feature is not being used, to\_base and amount will be the same. |
| category\_id | number | true | Unique identifier of associated category (see Categories) |
| category\_name | string | true | Name of category associated with transaction |
| category\_group\_id | number | true | Unique identifier of associated category group, if any |
| category\_group\_name | string | true | Name of category group associated with transaction, if any |
| is\_income | boolean | false | Based on the associated category's property, denotes if transaction is treated as income |
| exclude\_from\_budget | boolean | false | Based on the associated category's property, denotes if transaction is excluded from budget |
| exclude\_from\_totals | boolean | false | Based on the associated category's property, denotes if transaction is excluded from totals |
| created\_at | string | false | The date and time of when the transaction was created (in the ISO 8601 extended format). |
| updated\_at | string | false | The date and time of when the transaction was last updated (in the ISO 8601 extended format). |
| status | string | true | One of the following: <br>- cleared: User has reviewed the transaction<br>- uncleared: User has not yet reviewed the transaction<br>- pending: Imported transaction is marked as pending. This should be a temporary state.<br> Note: special statuses for recurring items have been deprecated. |
| is\_pending | boolean | false | Denotes if transaction is pending (not posted) |
| notes | string | true | User-entered transaction notes If recurring\_id is not null, this field will be description of associated recurring expense |
| original\_name | string | true | The transactions original name before any payee name updates. For synced transactions, this is the raw original payee name from your bank. |
| recurring\_id | number | true | Unique identifier of associated recurring item, or null for non-recurring transactions |
| recurring\_payee | string | true | The payee of associated recurring expense instead of the original transaction, or null for non-recurring transactions |
| recurring\_description | string | true | Description of associated recurring item, or null for non-recurring transactions |
| recurring\_cadence | string | true | Cadence of associated recurring item (one of `once a week`, `every 2 weeks`, `twice a month`, `monthly`, `every 2 months`, `every 3 months`, `every 4 months`, `twice a year`, `yearly`) , or null for non-recurring transactions |
| recurring\_type | string | true | Type of associated recurring (one of `cleared`, `suggested`, `dismissed`), or null for non-recurring transactions |
| recurring\_amount | string | true | Amount of associated recurring item in numeric format to 4 decimals, or null for non-recurring transactions |
| recurring\_currency | number | true | Currency of associated recurring item, or null for non-recurring transactions |
| parent\_id | number | true | Exists if this is a split transaction. Denotes the transaction ID of the original transaction. |
| has\_children | boolean | false | True if this transaction is a parent transaction and is split into 2 or more other transactions |
| group\_id | number | true | Exists if this transaction is part of a group. Denotes the parent’s transaction ID |
| is\_group | boolean | false | True if this transaction represents a group of transactions. If so, amount and currency represent the totalled amount of transactions bearing this transaction’s id as their group\_id. Amount is calculated based on the user’s primary currency. |
| asset\_id | number | true | Unique identifier of associated manually-managed account (see Assets) Note: plaid\_account\_id and asset\_id cannot both exist for a transaction |
| asset\_institution\_name | string | true | Institution name of associated manually-managed account |
| asset\_name | string | true | Name of associated manually-managed account |
| asset\_display\_name | string | true | Display name of associated manually-managed account |
| asset\_status | string | true | Status of associated manually-managed account (one of `active`, `closed`) |
| plaid\_account\_id | number | true | Unique identifier of associated Plaid account (see Plaid Accounts) Note: plaid\_account\_id and asset\_id cannot both exist for a transaction |
| plaid\_account\_name | string | true | Name of associated Plaid account |
| plaid\_account\_mask | string | true | Mask of associated Plaid account |
| institution\_name | string | true | Institution name of associated Plaid account |
| plaid\_account\_display\_name | string | true | Display name of associated Plaid account |
| plaid\_metadata | string | true | Metadata associated with imported transaction from Plaid |
| source | string | false | Source of the transaction (one of `api`, `csv`, `manual`,`merge`,`plaid`,`recurring`,`rule`,`user`) |
| display\_name | string | false | Display name for payee for transaction based on whether or not it is linked to a recurring item. If linked, returns `recurring_payee` field. Otherwise, returns the `payee` field. |
| display\_notes | string | true | Display notes for transaction based on whether or not it is linked to a recurring item. If linked, returns `recurring_notes` field. Otherwise, returns the `notes` field. |
| account\_display\_name | string | false | Display name for associated account (manual or Plaid). If this is a synced account, returns `plaid_account_display_name` or `asset_display_name`. |
| tags | Tag\[\] | false | Array of Tag objects |
| children | Transaction\[\] | true | This property exists only on a transaction with the `is_group` property set to `true`. On a grouped transaction, this will be an array of Transaction objects for the transactions that make up the group. These objects are slimmed down to the more essential fields, and contain an extra field called `formatted_date` that contains the date of transaction in ISO 8601 format |
| external\_id | string | true | User-defined external ID for any manually-entered or imported transaction. External ID cannot be accessed or changed for Plaid-imported transactions. External ID must be unique by asset\_id. Max 75 characters. |
| original\_date | string | true | DEPRECATED |
| type | string | true | DEPRECATED |
| subtype | string | true | DEPRECATED |
| fees | string | true | DEPRECATED |
| price | string | true | DEPRECATED |
| quantity | string | true | DEPRECATED |

## Get All Transactions

Use this endpoint to retrieve all transactions between a date range.

> Example 200 Response

```
Copy to Clipboard
{
  "transactions": [\
    {\
      "id": 246946944,\
      "date": "2023-07-18",\
      "amount": "53.1900",\
      "currency": "usd",\
      "to_base": 53.19,\
      "payee": "Amazon",\
      "category_id": 315172,\
      "category_name": "Restaurants",\
      "category_group_id": 315358,\
      "category_group_name": "Food & Drink",\
      "is_income": false,\
      "exclude_from_budget": false,\
      "exclude_from_totals": false,\
      "created_at": "2023-09-09T08:43:05.875Z",\
      "updated_at": "2023-10-09T06:07:03.105Z",\
      "status": "cleared",\
      "is_pending": false,\
      "notes": null,\
      "original_name": null,\
      "recurring_id": null,\
      "recurring_payee": null,\
      "recurring_description": null,\
      "recurring_cadence": null,\
      "recurring_type": null,\
      "recurring_amount": null,\
      "recurring_currency": null,\
      "parent_id": 225508713,\
      "has_children": false,\
      "group_id": null,\
      "is_group": false,\
      "asset_id": null,\
      "asset_institution_name": null,\
      "asset_name": null,\
      "asset_display_name": null,\
      "asset_status": null,\
      "plaid_account_id": 76602,\
      "plaid_account_name": "Amazon Whole Foods Visa",\
      "plaid_account_mask": "6299",\
      "institution_name": "Chase",\
      "plaid_account_display_name": "Amazon Whole Foods Visa",\
      "plaid_metadata": null,\
      "plaid_category": null,\
      "source": null,\
      "display_name": "Amazon",\
      "display_notes": null,\
      "account_display_name": "Amazon Whole Foods Visa",\
      "tags": [\
        {\
          "name": "Amazon",\
          "id": 76543\
        }\
      ],\
      "external_id": null\
    },\
    {\
      "id": 246946943,\
      "date": "2023-07-18",\
      "amount": "12.2100",\
      "currency": "usd",\
      "to_base": 12.21,\
      "payee": "Frelard Tamales",\
      "category_id": 315172,\
      "category_name": "Restaurants",\
      "category_group_id": 315358,\
      "category_group_name": "Food & Drink",\
      "is_income": false,\
      "exclude_from_budget": false,\
      "exclude_from_totals": false,\
      "created_at": "2023-09-09T08:43:05.818Z",\
      "updated_at": "2023-10-09T06:07:03.529Z",\
      "status": "cleared",\
      "is_pending": false,\
      "notes": null,\
      "original_name": null,\
      "recurring_id": null,\
      "recurring_payee": null,\
      "recurring_description": null,\
      "recurring_cadence": null,\
      "recurring_type": null,\
      "recurring_amount": null,\
      "recurring_currency": null,\
      "parent_id": 225588844,\
      "has_children": false,\
      "group_id": null,\
      "is_group": true,\
      "asset_id": null,\
      "asset_institution_name": null,\
      "asset_name": null,\
      "asset_display_name": null,\
      "asset_status": null,\
      "plaid_account_id": 54174,\
      "plaid_account_name": "Amex -11005",\
      "plaid_account_mask": "1005",\
      "institution_name": "American Express",\
      "plaid_account_display_name": "Amex Plat",\
      "plaid_metadata": null,\
      "plaid_category": null,\
      "source": null,\
      "display_name": "Frelard Tamales",\
      "display_notes": null,\
      "account_display_name": "Amex Plat",\
      "tags": [],\
      "children": [\
        {\
          "id": 246946948,\
          "payee": "Child Transaction One",\
          "amount": "-33.6000",\
          "currency": "cad",\
          "date": "2023-08-10",\
          "formatted_date": "2023-09-10",\
          "notes": null,\
          "asset_id": 7409,\
          "plaid_account_id": null,\
          "to_base": -33.6\
        },\
        {\
          "id": 246946948,\
          "payee": "Child Transaction Two",\
          "amount": "-33.6000",\
          "currency": "cad",\
          "date": "2023-08-10",\
          "formatted_date": "2023-09-10",\
          "notes": null,\
          "asset_id": 7409,\
          "plaid_account_id": null,\
          "to_base": -33.6\
        }\
      ]\
      "external_id": null\
    }\
  ],
  "has_more": true
}
```

> Example 404 Response

```
Copy to Clipboard
{ "error": "Both start_date and end_date must be specified." }
```

Returns list of Transaction objects and a `has_more` indicator. If no query parameters are set, this endpoint will return transactions for the current calendar month (see `start_date` and `end_date`)

### HTTP Request

`GET https://dev.lunchmoney.app/v1/transactions`

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| tag\_id | number | false | - | Filter by tag. Only accepts IDs, not names. |
| recurring\_id | number | false | - | Filter by recurring expense |
| plaid\_account\_id | number | false | - | Filter by Plaid account |
| category\_id | number | false | - | Filter by category. Will also match category groups. |
| asset\_id | number | false | - | Filter by asset |
| is\_group | boolean | false | - | Filter by group (returns transaction groups) |
| status | string | false | - | Filter by status (Can be `cleared` or `uncleared`. Note: special statuses for recurring items have been deprecated.) |
| start\_date | string | false | - | Denotes the beginning of the time period to fetch transactions for. Defaults to beginning of current month. Required if end\_date exists. Format: YYYY-MM-DD. |
| end\_date | string | false | - | Denotes the end of the time period you'd like to get transactions for. Defaults to end of current month. Required if start\_date exists. Format: YYYY-MM-DD. |
| debit\_as\_negative | boolean | false | false | Pass in true if you’d like expenses to be returned as negative amounts and credits as positive amounts. Defaults to false. |
| pending | boolean | false | false | Pass in true if you’d like to include imported transactions with a pending status. |
| offset | number | false | - | Sets the offset for the records returned |
| limit | number | false | 1000 | Sets the maximum number of records to return. |
| group\_id | number | false | - | DEPRECATED (Use [GET /v1/transactions-group](https://lunchmoney.dev/#get-transaction-group) instead) |

## Get Single Transaction

Use this endpoint to retrieve details about a specific transaction by ID.

> Example 200 Response

```
Copy to Clipboard
{
  "id": 480887173,
  "date": "2023-11-29",
  "amount": "-14.1800",
  "currency": "usd",
  "to_base": -14.18,
  "payee": "Walmart",
  "category_id": 315295,
  "category_name": "Health, Medical",
  "category_group_id": 315357,
  "category_group_name": "Personal",
  "is_income": false,
  "exclude_from_budget": false,
  "exclude_from_totals": false,
  "created_at": "2023-11-30T22:10:57.820Z",
  "updated_at": "2023-11-30T23:59:56.587Z",
  "status": "cleared",
  "is_pending": false,
  "notes": null,
  "original_name": "Walmart",
  "recurring_id": null,
  "recurring_payee": null,
  "recurring_description": null,
  "recurring_cadence": null,
  "recurring_type": null,
  "recurring_amount": null,
  "recurring_currency": null,
  "parent_id": null,
  "has_children": null,
  "group_id": 481307164,
  "is_group": false,
  "asset_id": null,
  "asset_institution_name": null,
  "asset_name": null,
  "asset_display_name": null,
  "asset_status": null,
  "plaid_account_id": 54174,
  "plaid_account_name": "Amex 1002",
  "plaid_account_mask": "1005",
  "institution_name": "American Express",
  "plaid_account_display_name": "Amex Plat",
  "plaid_metadata": "{\"account_id\":\"fMKfypkyRXSXvpJor4vPTg6OP7wD4afmEjv6N\",\"account_owner\":\"1005\",\"amount\":-14.18,\"authorized_date\":\"2023-11-28\",\"authorized_datetime\":null,\"category\":[\"Shops\",\"Supermarkets and Groceries\"],\"category_id\":\"19047000\",\"check_number\":null,\"counterparties\":[{\"confidence_level\":\"VERY_HIGH\",\"entity_id\":\"O5W5j4dN9OR3E6ypQmjdkWZZRoXEzVMz2ByWM\",\"logo_url\":\"https://plaid-merchant-logos.plaid.com/walmart_1100.png\",\"name\":\"Walmart\",\"type\":\"merchant\",\"website\":\"walmart.com\"}],\"date\":\"2023-11-29\",\"datetime\":null,\"iso_currency_code\":\"USD\",\"location\":{\"address\":null,\"city\":null,\"country\":null,\"lat\":null,\"lon\":null,\"postal_code\":null,\"region\":null,\"store_number\":null},\"logo_url\":\"https://plaid-merchant-logos.plaid.com/walmart_1100.png\",\"merchant_entity_id\":\"O5W5j4dN9OR3E6ypQmjdkWZZRoXEzVMz2ByWM\",\"merchant_name\":\"Walmart\",\"name\":\"Walmart\",\"payment_channel\":\"other\",\"payment_meta\":{\"by_order_of\":null,\"payee\":null,\"payer\":null,\"payment_method\":null,\"payment_processor\":null,\"ppd_id\":null,\"reason\":null,\"reference_number\":\"320233330735688096\"},\"pending\":false,\"pending_transaction_id\":null,\"personal_finance_category\":{\"confidence_level\":\"VERY_HIGH\",\"detailed\":\"GENERAL_MERCHANDISE_SUPERSTORES\",\"primary\":\"GENERAL_MERCHANDISE\"},\"personal_finance_category_icon_url\":\"https://plaid-category-icons.plaid.com/PFC_GENERAL_MERCHANDISE.png\",\"transaction_code\":null,\"transaction_id\":\"rmQdnefvAndbfHN5mZ4y703C3vdjk7mozCw1OarL\",\"transaction_type\":\"place\",\"unofficial_currency_code\":null,\"website\":\"walmart.com\"}",
  "plaid_category": "GENERAL_MERCHANDISE_SUPERSTORES",
  "source": "plaid",
  "display_name": "Walmart",
  "display_notes": null,
  "account_display_name": "Amex Plat",
  "tags": [],
  "external_id": null
}
```

> Example 404 Response

```
Copy to Clipboard
{ "error": "Transaction ID not found." }
```

Returns a single Transaction object

### HTTP Request

`GET https://dev.lunchmoney.app/v1/transactions/:transaction_id`

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| debit\_as\_negative | boolean | false | false | Pass in true if you’d like expenses to be returned as negative amounts and credits as positive amounts. Defaults to false. |

## Insert Transactions

Use this endpoint to insert one or more transactions at once. The maximum number of transactions per requests is 500.

> Example 200 Response
>
> Upon success, IDs of inserted transactions will be returned in an array.

```
Copy to Clipboard
{
  "ids": [54, 55, 56, 57]
}
```

> Example 404 Response
>
> An array of errors will be returned denoting reason why parameters were deemed invalid.

```
Copy to Clipboard
{
  "error": [\
    "Transaction 0 is missing date.",\
    "Transaction 0 is missing amount.",\
    "Transaction 1 status must be either cleared or uncleared: null"\
  ]
}
```

### HTTP Request

`POST https://dev.lunchmoney.app/v1/transactions`

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| transactions | array | true | - | List of transactions to insert (see below) |
| apply\_rules | boolean | false | false | If true, will apply account’s existing rules to the inserted transactions. Defaults to false. |
| skip\_duplicates | boolean | false | false | If true, the system will automatically dedupe based on transaction date, payee and amount. Note that deduping by external\_id will occur regardless of this flag. |
| check\_for\_recurring | boolean | false | false | If true, will check new transactions for occurrences of new monthly expenses. Defaults to false. |
| debit\_as\_negative | boolean | false | false | If true, will assume negative amount values denote expenses and positive amount values denote credits. Defaults to false. |
| skip\_balance\_update | boolean | false | true | If true, will skip updating balance if an asset\_id is present for any of the transactions. |

### Transaction Object to Insert

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| date | string | true | Must be in ISO 8601 format (YYYY-MM-DD). |
| amount | number/string | true | Numeric value of amount. i.e. $4.25 should be denoted as 4.25. |
| category\_id | number | false | Unique identifier for associated category\_id. Category must be associated with the same account and must not be a category group. |
| payee | string | false | Max 140 characters |
| currency | string | false | Three-letter lowercase currency code in ISO 4217 format. The code sent must exist in our database. Defaults to user account's primary currency. |
| asset\_id | number | false | Unique identifier for associated asset (manually-managed account). Asset must be associated with the same account. When set `plaid_account_id` may not be set. |
| plaid\_account\_id | number | false | Unique identifier for associated plaid account. This must have the "Allow Modifications to Transactions" option set. When set `asset_id` may not be set. |
| recurring\_id | number | false | Unique identifier for associated recurring expense. Recurring expense must be associated with the same account. |
| notes | string | false | Max 350 characters |
| status | string | false | Must be either cleared or uncleared. (Note: special statuses for recurring items have been deprecated.) Defaults to uncleared. |
| external\_id | string | false | User-defined external ID for transaction. Max 75 characters. External IDs must be unique within the same asset\_id. |
| tags | Array of numbers and/or strings | false | Passing in a number will attempt to match by ID. If no matching tag ID is found, an error will be thrown. Passing in a string will attempt to match by string. If no matching tag name is found, a new tag will be created. |

## Update Transaction

Use this endpoint to update a single transaction. You may also use this to split an existing transaction.

> Example 200 Response
>
> If a split was part of the request, an array of newly-created split transactions will be returned.

```
Copy to Clipboard
{
  "updated": true,
  "split": [58, 59]
}
```

> Example 404 Response
>
> An array of errors will be returned denoting reason why parameters were deemed invalid.

```
Copy to Clipboard
{ "error": ["This transaction doesn't exist or you don't have access to it."] }
```

```
Copy to Clipboard
{
  "error": [\
    "You cannot change the amount for this transaction because it was automatically imported.",\
    "You cannot assign an asset_id for this transaction because it was automatically imported."\
  ]
}
```

### HTTP Request

`PUT https://dev.lunchmoney.app/v1/transactions/:transaction_id`

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| split | Split\[\] | see description | - | Defines the split of a transaction. You may not split an already-split transaction, recurring transaction, or group transaction. (see Split object below). If passing an array of split objects to this parameter, the transaction parameter is not required. |
| transaction | object | see description | - | The transaction update object (see Update Transaction object below). Must include an `id` matching an existing transaction. If passing a transaction object to this parameter, the split parameter is not required. |
| debit\_as\_negative | boolean | false | false | If true, will assume negative amount values denote expenses and positive amount values denote credits. Defaults to false. |
| skip\_balance\_update | boolean | false | true | If false, will skip updating balance if an asset\_id is present for any of the transactions. |

### Update Transaction Object

| Key | Type | Description |
| --- | --- | --- |
| date | string | Must be in ISO 8601 format (YYYY-MM-DD). |
| category\_id | number | Unique identifier for associated category\_id. Category must belong to the account associated with the API Token used in the request and must not be a category group. |
| payee | string | Max 140 characters |
| amount | number or string | You may only update this if this transaction was not created from an automatic import, i.e. if this transaction is not associated with a plaid\_account\_id |
| currency | string | You may only update this if this transaction was not created from an automatic import, i.e. if this transaction is not associated with a plaid\_account\_id. Defaults to user account's primary currency. |
| asset\_id | number | Unique identifier for associated asset (manually-managed account). Asset must belong to the account associated with the API Token used in the request. You may not update this if this transaction currently belongs to a Plaid synced account that does not have the "Allow Modifications to Transactions" property set. This may not be set if plaid\_account\_id is also set. |
| plaid\_account\_id | number | Unique identifier for a synced (Plaid) account. Account must belong to the account associated with the API Token used in the request and have the "Allow Modifications to Transactions" property set. This may not be set if asset\_id is also set. |
| recurring\_id | number | Unique identifier for associated recurring expense. Recurring expense must be associated with the same account. |
| notes | string | Max 350 characters |
| status | string | Must be either cleared or uncleared. Defaults to uncleared. (Note: special statuses for recurring items have been deprecated.) Defaults to uncleared. |
| external\_id | string | User-defined external ID for transaction. Max 75 characters. External IDs must be unique within the same asset\_id. You may only update this if this transaction was not created from an automatic import, i.e. if this transaction is not associated with a plaid\_account\_id |
| tags | array of numbers and/or strings | Input must be an array, or error will be thrown. Passing in a number will attempt to match by ID. If no matching tag ID is found, an error will be thrown. Passing in a string will attempt to match by string. If no matching tag name is found, a new tag will be created. Pass in `null` to remove all tags. |

### Split Object

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| payee | string | false | Max 140 characters. Sets to original payee if none defined |
| date | string | false | Must be in ISO 8601 format (YYYY-MM-DD). Sets to original date if none defined |
| category\_id | number | false | Unique identifier for associated category\_id. Category must be associated with the same account. Sets to original category if none defined |
| notes | string | false | Sets to original notes if none defined |
| amount | number/string | true | Individual amount of split. Currency will inherit from parent transaction. All amounts must sum up to parent transaction amount. |

## Unsplit Transactions

Use this endpoint to unsplit one or more transactions.

> Example 200 Response

```
Copy to Clipboard
[84389, 23212, 43333]
```

> Example 404 Response

```
Copy to Clipboard
{
  "error": "The following transaction ids are not valid to unsplit: 1232, 1233, 1234"
}
```

Returns an array of IDs of deleted transactions

### HTTP Request

`POST https://dev.lunchmoney.app/v1/transactions/unsplit`

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| parent\_ids | array of numbers | true | - | Array of transaction IDs to unsplit. If one transaction is unsplittable, no transaction will be unsplit. |
| remove\_parents | boolean | false | false | If true, deletes the original parent transaction as well. Note, this is not reversible! |

## Get Transaction Group

Use this endpoint to get the parent transaction and associated children transactions of a transaction group.

> Example 200 Response

```
Copy to Clipboard
{
  "id": 481307164,
  "date": "2023-11-29",
  "amount": "0",
  "currency": "usd",
  "to_base": 0,
  "payee": "Walmart+",
  "category_id": 315174,
  "category_name": "General",
  "category_group_id": 315362,
  "category_group_name": "Shopping",
  "is_income": false,
  "exclude_from_budget": false,
  "exclude_from_totals": false,
  "created_at": "2023-11-30T23:59:56.584Z",
  "updated_at": "2023-11-30T23:59:56.584Z",
  "status": "cleared",
  "is_pending": false,
  "notes": null,
  "original_name": null,
  "recurring_id": null,
  "recurring_payee": null,
  "recurring_description": null,
  "recurring_cadence": null,
  "recurring_type": null,
  "recurring_amount": null,
  "recurring_currency": null,
  "parent_id": null,
  "has_children": null,
  "group_id": null,
  "is_group": true,
  "asset_id": null,
  "asset_institution_name": null,
  "asset_name": null,
  "asset_display_name": null,
  "asset_status": null,
  "plaid_account_id": null,
  "plaid_account_name": null,
  "plaid_account_mask": null,
  "institution_name": null,
  "plaid_account_display_name": null,
  "plaid_metadata": null,
  "plaid_category": null,
  "source": null,
  "display_name": "Walmart+",
  "display_notes": null,
  "account_display_name": " ",
  "tags": [],
  "children": [\
    {\
      "id": 480887173,\
      "payee": "Walmart",\
      "amount": "-14.1800",\
      "currency": "usd",\
      "date": "2023-11-29",\
      "formatted_date": "2023-11-29",\
      "notes": null,\
      "asset_id": null,\
      "plaid_account_id": 54174,\
      "to_base": -14.18\
    },\
    {\
      "id": 480887180,\
      "payee": "Walmart",\
      "amount": "14.1800",\
      "currency": "usd",\
      "date": "2023-11-28",\
      "formatted_date": "2023-11-28",\
      "notes": null,\
      "asset_id": null,\
      "plaid_account_id": 54174,\
      "to_base": 14.18\
    }\
  ],
  "external_id": null
}
```

> Example 404 Response

```
Copy to Clipboard
{
  "error": [\
    "Transaction 35360525 is not a transaction group, or part of a transaction group."\
  ]
}
```

Returns the hydrated parent transaction of a transaction group

### HTTP Request

`GET https://dev.lunchmoney.app/v1/transactions/group`

### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| transaction\_id | number | true | Transaction ID of either the parent or any of the children in the transaction group |

## Create Transaction Group

Use this endpoint to create a transaction group of two or more transactions.

> Example 200 Response

```
Copy to Clipboard
84389
```

> Example 404 Response

```
Copy to Clipboard
{
  "error": [\
    "Transaction 35360525 is in a transaction group already (35717487) and cannot be added to another transaction group."\
  ]
}
```

Returns the ID of the newly created transaction group

### HTTP Request

`POST https://dev.lunchmoney.app/v1/transactions/group`

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| date | string | true | - | Date for the grouped transaction |
| payee | string | true | - | Payee name for the grouped transaction |
| category\_id | number | false | - | Category for the grouped transaction |
| notes | string | false | - | Notes for the grouped transaction |
| tags | array | false | - | Array of tag IDs for the grouped transaction |
| transactions | array | true | - | Array of transaction IDs to be part of the transaction group |

## Delete Transaction Group

Use this endpoint to delete a transaction group. The transactions within the group will not be removed.

> Example 200 Response

```
Copy to Clipboard
{ "transactions": [121232, 324324, 545455] }
```

> Example 404 Response

```
Copy to Clipboard
{ "error": ["No transactions found for this group_id 35717487."] }
```

Returns the IDs of the transactions that were part of the deleted group

### HTTP Request

`DELETE https://dev.lunchmoney.app/v1/transactions/group/:transaction_id`

* * *

# Recurring Expenses

This endpoint has been deprecated in favor of [Recurring Items](https://lunchmoney.dev/#recurring-items)

## Recurring Expenses Object

| Attribute | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | false | Unique identifier for recurring expense |
| start\_date | string | true | Denotes when recurring expense starts occurring in ISO 8601 format. If null, then this recurring expense will show up for all time before end\_date |
| end\_date | string | true | Denotes when recurring expense stops occurring in ISO 8601 format. If null, then this recurring expense has no set end date and will show up for all months after start\_date |
| cadence | string | false | One of:<br>- monthly<br>- twice a month<br>- once a week<br>- every 3 months<br>- every 4 months<br>- twice a year<br>- yearly |
| payee | string | false | Payee of the recurring expense |
| amount | number | false | Amount of the recurring expense in numeric format to 4 decimal places |
| currency | string | false | Three-letter lowercase currency code for the recurring expense in ISO 4217 format |
| description | string | true | If any, represents the user-entered description of the recurring expense |
| billing\_date | string | false | Expected billing date for this recurring expense for this month in ISO 8601 format |
| type | string | false | This can be one of two values: <br>- cleared: The recurring expense has been reviewed by the user<br>- suggested: The recurring expense is suggested by the system; the user has yet to review/clear it |
| original\_name | string | true | If any, represents the original name of the recurring expense as denoted by the transaction that triggered its creation |
| source | string | false | This can be one of three values:<br>- manual: User created this recurring expense manually from the Recurring Expenses page<br>- transaction: User created this by converting a transaction from the Transactions page<br>- system: Recurring expense was created by the system on transaction import<br>- Some older recurring expenses may not have a source. |
| plaid\_account\_id | number | true | If any, denotes the plaid account associated with the creation of this recurring expense (see Plaid Accounts) |
| asset\_id | number | true | If any, denotes the manually-managed account (i.e. asset) associated with the creation of this recurring expense (see Assets) |
| category\_id | number | true | If any, denotes the unique identifier for the associated category to this recurring expense |
| created\_at | string | false | The date and time of when the recurring expense was created (in the ISO 8601 extended format). |

## Get Recurring Expenses

It is no longer recommended to use this endpoint to retrieve a list of recurring expenses to expect for a specified period. Use the [GET /v1/recurring\_items](https://lunchmoney.dev/#get-recurring-items) endpoint instead.

Every month, a different set of recurring expenses is expected. This is because recurring expenses can be once a year, twice a year, every 4 months, etc.

If a recurring expense is listed as “twice a month”, then that recurring expense will be returned twice, each with a different billing date based on when the system believes that recurring expense transaction is to be expected. If the recurring expense is listed as “once a week”, then that recurring expense will be returned in this list as many times as there are weeks for the specified month.

In the same vein, if a recurring expense that began last month is set to “Every 3 months”, then that recurring expense will not show up in the results for this month.

> Example 200 Response
>
> Returns a list of Recurring Expense objects

```
Copy to Clipboard
{
  "recurring_expenses": [\
    {\
      "id": 264,\
      "start_date": "2020-01-01",\
      "end_date": null,\
      "cadence": "twice a month",\
      "payee": "Test 5",\
      "amount": "-122.0000",\
      "currency": "cad",\
      "created_at": "2020-01-30T07:58:43.944Z",\
      "description": null,\
      "billing_date": "2020-01-01",\
      "type": "cleared",\
      "original_name": null,\
      "source": "manual",\
      "plaid_account_id": null,\
      "asset_id": null\
    },\
    {\
      "id": 262,\
      "start_date": "2020-01-01",\
      "end_date": null,\
      "cadence": "monthly",\
      "payee": "Test 2",\
      "amount": "-32.4500",\
      "currency": "usd",\
      "created_at": "2020-01-30T07:58:43.921Z",\
      "description": "Test description 2",\
      "billing_date": "2020-01-03",\
      "type": "cleared",\
      "original_name": null,\
      "source": "manual",\
      "plaid_account_id": null,\
      "asset_id": null\
    },\
    {\
      "id": 264,\
      "start_date": "2020-01-01",\
      "end_date": null,\
      "cadence": "twice a month",\
      "payee": "Test 5",\
      "amount": "-122.0000",\
      "currency": "cad",\
      "created_at": "2020-01-30T07:58:43.944Z",\
      "description": null,\
      "billing_date": "2020-01-15",\
      "type": "cleared",\
      "original_name": null,\
      "source": "manual",\
      "plaid_account_id": null,\
      "asset_id": null\
    }\
  ]
}
```

> Example 404 Response

```
Copy to Clipboard
{ "error": "Invalid start_date. Must be in format YYYY-MM-DD" }
```

### HTTP Request

`GET https://dev.lunchmoney.app/v1/recurring_expenses`

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| start\_date | string | false | First day of the current month | Accepts a string in ISO-8601 short format. Whatever your start date, the system will automatically return recurring expenses expected for that month. For instance, if you input 2020-01-25, the system will return recurring expenses which are to be expected between 2020-01-01 to 2020-01-31. |
| debit\_as\_negative | boolean | false | false | Pass in true if you’d like expenses to be returned as negative amounts and credits as positive amounts. |

* * *

# Recurring Items

## Recurring Items Object

| Attribute | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | false | Unique identifier for recurring item |
| start\_date | string | true | Denotes when recurring item starts occurring in ISO 8601 format. If null, then this recurring item will show up for all time before end\_date |
| end\_date | string | true | Denotes when recurring item stops occurring in ISO 8601 format. If null, then this recurring item has no set end date and will show up for all months after start\_date |
| payee | string | false | Payee or payer of the recurring item |
| currency | string | false | Three-letter lowercase currency code for the recurring item in ISO 4217 format |
| created\_by | number | false | The id of the user who created this recurring item. |
| created\_at | string | false | The date and time of when the recurring item was created (in the ISO 8601 extended format). |
| updated\_at | string | false | The date and time of when the recurring item was updated (in the ISO 8601 extended format). |
| billing\_date | string | false | Initial date that a transaction associated with this recurring item occurred. This date is used in conjunction with values of `quantity` and `granularity` to determine the expected dates of recurring transactions in the period. |
| original\_name | string | true | If any, represents the original name of the recurring item as denoted by the transaction that triggered its creation |
| description | string | true | If any, represents the user-entered description of the recurring item |
| plaid\_account\_id | number | true | If any, denotes the plaid account associated with the creation of this recurring item (see Plaid Accounts) |
| asset\_id | number | true | If any, denotes the manually-managed account (i.e. asset) associated with the creation of this recurring item (see Assets) |
| source | string | false | This can be one of four values:<br>- manual: User created this recurring item manually from the Recurring Items page<br>- transaction: User created this by converting a transaction from the Transactions page<br>- system: Recurring item was created by the system on transaction import<br>- null: Some older recurring items may not have a source. |
| notes | string | true | If any, the user-entered notes for the recurring item |
| amount | number | false | Amount of the recurring item in numeric format to 4 decimal places. For recurring items with flexible amounts, this is the average of the specified min and max amounts. |
| category\_id | number | true | If any, denotes the unique identifier for the associated category to this recurring item |
| category\_group\_id | number | true | If any, denotes the unique identifier of associated category group |
| is\_income | boolean | false | Based on the associated category's property, denotes if the recurring transaction is treated as income |
| exclude\_from\_totals | boolean | false | Based on the associated category's property, denotes if the recurring transaction is excluded from totals |
| granularity | string | false | The unit of time used to define the cadence of the recurring item <br>One of:<br>- day<br>- week<br>- month<br>- year |
| quantity | number | true | The number of granularity units between each recurrence |
| occurrences | object | false | An object which contains dates as keys and lists as values. The dates will include all the dates in the month that a recurring item is expected, as well as the last date in the previous period and the first date in the next period. The value for each key is a list of [Summarized Transaction Objects](https://lunchmoney.dev/#summarized-transaction-object) that matched the recurring item for that date (if any) |
| transactions\_within\_range | list | true | A list of all the [Summarized Transaction Objects](https://lunchmoney.dev/#summarized-transaction-object) for transactions that that have occurred in the query month for the recurring item (if any) |
| missing\_dates\_within\_range | list | true | A list of date strings when a recurring transaction is expected but has not (yet) occurred. |
| date | string | true | Denotes the value of the `start_date` query parameter, or if none was provided, the date when the request was made. This indicates the month used by the system when populating the response. |
| to\_base | number | false | The amount converted to the user's primary currency. If the multicurrency feature is not being used, to\_base and amount will be the same. |

## Summarized Transaction Object

This object, which includes a subset of fields from the Transaction Object, may be included in the list of transactions associated with a date in the `occurrences` object, or in the `transactions_within_range` list.

| Attribute | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | false | Unique identifier for the transaction that matched this recurring item |
| date | string | false | Date of transaction in ISO 8601 format |
| amount | string | false | Amount of the transaction in numeric format to 4 decimal places |
| currency | string | false | Three-letter lowercase currency code of the transaction in ISO 4217 format |
| payee | string | false | Payee or payer of the recurring item |
| category\_id | number | true | Unique identifier of associated category (see Categories) |
| recurring\_id | number | true | Unique identifier of associated recurring item |
| to\_base | number | false | The amount converted to the user's primary currency. If the multicurrency feature is not being used, to\_base and amount will be the same. |

## Get Recurring Items

Use this endpoint to retrieve a list of recurring items to expect for a specified month.

A different set of recurring items is expected every month. These can be once a year, twice a year, every four months, etc.

If a recurring item is listed as “twice a month,” then the recurring item object returned will have an `occurrences` attribute populated by the different billing dates the system believes recurring transactions should occur, including the two dates in the current month, the last transaction date prior to the month, and the next transaction date after the month.

If the recurring item is listed as “once a week,” then the recurring item object returned will have an `occurrences` object populated with as many times as there are weeks for the specified month, along with the last transaction from the previous month and the next transaction for the next month.

In the same vein, if a recurring item that began last month is set to “Every 3 months”, then that recurring item object that occurred will not include any dates for this month.

> Example 200 Response
>
> Returns a list of Recurring Item objects

````
Copy to Clipboard
[\
    {\
        "id": 940537,\
        "start_date": null,\
        "end_date": null,\
        "payee": "Weekly Income",\
        "currency": "usd",\
        "created_at": "2024-05-27T12:48:33.777Z",\
        "updated_at": "2024-05-27T12:48:33.777Z",\
        "billing_date": "2024-05-01",\
        "original_name": null,\
        "description": null,\
        "plaid_account_id": null,\
        "asset_id": null,\
        "source": "manual",\
        "amount": "-200.0000",\
        "notes": null,\
        "category_id": 911979,\
        "category_group_id": null,\
        "is_income": true,\
        "exclude_from_totals": false,\
        "granularity": "weeks",\
        "quantity": 1,\
        "occurrences": {\
            "2024-05-29": [\
                {\
                    "id": 2178542342,\
                    "date": "2024-05-29",\
                    "amount": "-200",\
                    "currency": "usd",\
                    "payee": "Weekly Income",\
                    "category_id": 911979,\
                    "recurring_id": 940537,\
                    "to_base": -200\
                }\
            ],\
            "2024-06-05": [\
                {\
                    "id": 2178538493,\
                    "date": "2024-06-05",\
                    "amount": "-200",\
                    "currency": "usd",\
                    "payee": "Weekly Income",\
                    "category_id": 911979,\
                    "recurring_id": 940537,\
                    "to_base": -200\
                }\
            ],\
            "2024-06-12": [],\
            "2024-06-19": [],\
            "2024-06-26": [],\
            "2024-07-03": []\
        },\
        "transactions_within_range": [\
                {\
                    "id": 2178538493,\
                    "date": "2024-06-05",\
                    "amount": "-200",\
                    "currency": "usd",\
                    "payee": "Weekly Income",\
                    "category_id": 911979,\
                    "recurring_id": 940537,\
                    "to_base": -200\
                }\
        ],\
        "missing_dates_within_range": [\
            "2024-06-12",\
            "2024-06-19",\
            "2024-06-26"\
        ],\
        "date": "2024-06-04",\
        "to_base": -200\
    },\
    {\
        "id": 838965,\
        "start_date": null,\
        "end_date": null,\
        "payee": "Google Fi",\
        "currency": "usd",\
        "created_at": "2024-04-05T20:02:22.698Z",\
        "updated_at": "2024-04-05T20:02:22.698Z",\
        "billing_date": "2024-01-25",\
        "original_name": null,\
        "description": "Cell phone plan",\
        "plaid_account_id": null,\
        "asset_id": 109419,\
        "source": "manual",\
        "amount": "50.0000",\
        "notes": null,\
        "category_id": 911972,\
        "category_group_id": null,\
        "is_income": false,\
        "exclude_from_totals": false,\
        "granularity": "months",\
        "quantity": 1,\
        "occurrences": {\
            "2024-05-25": [\
                {\
                    "id": 21781233,\
                    "date": "2024-05-25",\
                    "amount": "50.0000",\
                    "currency": "usd",\
                    "payee": "Google Fi",\
                    "category_id": 911972,\
                    "recurring_id": 838965,\
                    "to_base": 50\
                }\
            ],\
            "2024-06-25": [],\
            "2024-07-25": []\
        },\
        "transactions_within_range": [],\
        "missing_dates_within_range": [\
            "2024-06-25"\
        ],\
        "date": "2024-06-04",\
        "to_base": 50\
    },\
    {\
        "id": 838963,\
        "start_date": null,\
        "end_date": null,\
        "payee": "Geico",\
        "currency": "usd",\
        "created_at": "2024-04-05T20:02:22.244Z",\
        "updated_at": "2024-04-05T20:02:22.244Z",\
        "billing_date": "2024-01-01",\
        "original_name": null,\
        "description": "Car insurance",\
        "plaid_account_id": null,\
        "asset_id": 109419,\
        "source": "manual",\
        "amount": "145.0000",\
        "notes": null,\
        "category_id": 911972,\
        "category_group_id": null,\
        "is_income": false,\
        "exclude_from_totals": false,\
        "granularity": "months",\
        "quantity": 1,\
        "occurrences": {\
            "2024-06-01": [],\
            "2024-07-01": []\
        },\
        "transactions_within_range": [],\
        "missing_dates_within_range": [\
            "2024-06-01"\
        ],\
        "date": "2024-06-04",\
        "to_base": 145\
    }\
]```

> Example 404 Response

```json
{ "error": "Invalid start_date. Must be in format YYYY-MM-DD" }
````

### HTTP Request

`GET https://dev.lunchmoney.app/v1/recurring_items`

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| start\_date | string | false | First day of the current month | Accepts a string in ISO-8601 short format. If not set the recurring items for the current month are returned. If set denotes the starting month of the date range to return |
| end\_date | string | false | none | Required if start\_date is set. Must be a date later than start\_date. Denotes the end month of the date range to return |
| debit\_as\_negative | boolean | false | false | Pass in true if you’d like items to be returned as negative amounts and credits as positive amounts. |

* * *

# Budget

## Budget Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| category\_name | string | false | Name of the category, will be "Uncategorized" if no category is assigned |
| category\_id | number | true | Unique identifier for category, can be null when `category_name` is "Uncategorized" |
| category\_group\_name | string | true | Name of the category group, if applicable |
| group\_id | number | true | Unique identifier for category group |
| is\_group | boolean | true | If true, this category is a group |
| is\_income | boolean | false | If true, this category is an income category (category properties are set in the app via the Categories page) |
| exclude\_from\_budget | boolean | false | If true, this category is excluded from budget (category properties are set in the app via the Categories page) |
| exclude\_from\_totals | boolean | false | If true, this category is excluded from totals (category properties are set in the app via the Categories page) |
| data | Data\[\] | false | For each month with budget or category spending data, there is a data object with the key set to the month in format YYYY-MM-DD. For properties, see Data object below. |
| config | object | true | Object representing the category's budget suggestion configuration |
| order | number | false | Numerical ordering of budgets |
| archived | boolean | false | True if the category is archived and not displayed in relevant areas of the Lunch Money app. |
| recurring | object | true | Returns a list object that contains an array of Recurring Expenses objects (just the `payee`, `amount`, `currency`, and `to_base` fields) that affect this budget |

## Data Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| budget\_amount | number | true | The budget amount, as set by the user. If empty, no budget has been set. |
| budget\_currency | string | true | The budget currency, as set by the user. If empty, no budget has been set. |
| budget\_to\_base | number | true | The budget converted to the user's primary currency. If the multicurrency feature is not being used, budget\_to\_base and budget\_amount will be the same. If empty, no budget has been set. |
| spending\_to\_base | number | false | The total amount spent in this category for this time period in the user's primary currency |
| num\_transactions | number | false | Number of transactions that make up "spending\_to\_base" |
| is\_automated | boolean | true | If true, the budget\_amount is only a suggestion based on the set config. If not present, it is false (meaning this is a locked in budget) |

## Config Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| config\_id | number | false | Unique identifier for config |
| cadence | string | false | One of:<br>- monthly<br>- twice a month<br>- once a week<br>- every 3 months<br>- every 4 months<br>- twice a year<br>- yearly |
| amount | number | false | Amount in numeric format |
| currency | string | false | Three-letter lowercase currency code for the recurring expense in ISO 4217 format |
| to\_base | number | false | The amount converted to the user's primary currency. |
| auto\_suggest | string | false | One of:<br>- budgeted<br>- fixed<br>- fixed-rollover<br>- spent |

## Get Budget Summary

Use this endpoint to get full details on the budgets for all budgetable categories between a certain time period. The budgeted and spending amounts will be broken down by month.

> Example 200 Response

```
Copy to Clipboard
[\
    {\
        "category_name": "Food",\
        "category_id": 34476,\
        "category_group_name": null,\
        "group_id": null,\
        "is_group": true,\
        "is_income": false,\
        "exclude_from_budget": false,\
        "exclude_from_totals": false,\
        "data": {\
            "2020-09-01": {\
                "num_transactions": 23,\
                "spending_to_base": 373.51,\
                "budget_to_base": 376.08,\
                "budget_amount": 376.08,\
                "budget_currency": "usd",\
                "is_automated": true,\
            },\
            "2020-08-01": {\
                "num_transactions": 23,\
                "spending_to_base": 123.92,\
                "budget_to_base": 300,\
                "budget_amount": 300,\
                "budget_currency": "usd",\
            },\
            "2020-07-01": {\
                "num_transactions": 23,\
                "spending_to_base": 228.66,\
                "budget_to_base": 300,\
                "budget_amount": 300,\
                "budget_currency": "usd",\
            }\
        },\
        "config": {\
            "config_id": 9,\
            "cadence": "monthly",\
            "amount": 300,\
            "currency": "usd",\
            "to_base": 300,\
            "auto_suggest": "fixed-rollover"\
        },\
        "order": 0,\
        "archived": false,\
        "recurring": null\
    },\
    {\
        "category_name": "Alcohol & Bars",\
        "category_id": 26,\
        "category_group_name": "Food",\
        "group_id": 34476,\
        "is_group": null,\
        "is_income": false,\
        "exclude_from_budget": false,\
        "exclude_from_totals": false,\
        "data": {\
            "2020-09-01": {\
                "spending_to_base": 270.86,\
                "num_transactions": 14\
            },\
            "2020-08-01": {\
                "spending_to_base": 79.53,\
                "num_transactions": 8\
            },\
            "2020-07-01": {\
                "spending_to_base": 149.61,\
                "num_transactions": 8\
            }\
        },\
        "config": null,\
        "archived": false,\
        "order": 1,\
        "recurring": {\
            "list": [\
                {\
                    "payee": "Recurring Payee",\
                    "amount": "20.000",\
                    "currency": "cad",\
                    "to_base": 20\
                }\
            ]\
        }\
    }\
]
```

### HTTP Request

`GET https://dev.lunchmoney.app/v1/budgets`

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| start\_date | string | true | - | Start date for the budget period. Lunch Money currently only supports monthly budgets, so your date should be the start of a month (eg. 2021-04-01) |
| end\_date | string | true | - | End date for the budget period. Lunch Money currently only supports monthly budgets, so your date should be the end of a month (eg. 2021-04-30) |
| currency | string | false | - | Currency for the budgeted amount (optional). If empty, will default to your primary currency |

## Upsert Budget

Use this endpoint to update an existing budget or insert a new budget for a particular category and date.

Note: Lunch Money currently only supports monthly budgets, so your date must always be the start of a month (eg. 2021-04-01)

> Example 200 Response

If this is a sub-category, the response will include the updated category group's budget. This is because setting a sub-category may also update the category group's overall budget.

```
Copy to Clipboard
{
    "category_group": {
        "category_id": 34476,
        "amount": 100,
        "currency": "usd",
        "start_date": "2021-06-01"
    }
}
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{ "error": "Budget must be greater than or equal to the sum of sub-category budgets ($10.01)." }
```

### HTTP Request

`PUT https://dev.lunchmoney.app/v1/budgets`

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| start\_date | string | true | - | Start date for the budget period. Lunch Money currently only supports monthly budgets, so your date must always be the start of a month (eg. 2021-04-01) |
| category\_id | number | true | - | Unique identifier for the category |
| amount | number | true | - | Amount for budget |
| currency | string | false | - | Currency for the budgeted amount (optional). If empty, will default to your primary currency |

## Remove Budget

Use this endpoint to unset an existing budget for a particular category in a particular month.

> Example 200 Response

```
Copy to Clipboard
true
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{ "error": "start_date must be a valid date in format YYYY-MM-01" }
```

### HTTP Request

`DELETE https://dev.lunchmoney.app/v1/budgets`

### Query Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| start\_date | string | true | - | Start date for the budget period. Lunch Money currently only supports monthly budgets, so your date must always be the start of a month (eg. 2021-04-01) |
| category\_id | number | true | - | Unique identifier for the category |

* * *

# Assets

## Assets Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | false | Unique identifier for asset |
| type\_name | string | false | Primary type of the asset. Must be one of:<br>- cash<br>- credit<br>- investment<br>- real estate<br>- loan<br>- vehicle<br>- cryptocurrency<br>- employee compensation<br>- other liability<br>- other asset |
| subtype\_name | string | true | Optional asset subtype. Examples include:<br>- retirement<br>- checking<br>- savings<br>- prepaid credit card |
| name | string | false | Name of the asset |
| display\_name | string | true | Display name of the asset (as set by user) |
| balance | string | false | Current balance of the asset in numeric format to 4 decimal places |
| to\_base | number | true | The balance converted to the user's primary currency |
| balance\_as\_of | string | false | Date/time the balance was last updated in ISO 8601 extended format |
| closed\_on | string | true | The date this asset was closed (optional) |
| currency | string | false | Three-letter lowercase currency code of the balance in ISO 4217 format |
| institution\_name | string | true | Name of institution holding the asset |
| exclude\_transactions | boolean | false | If true, this asset will not show up as an option for assignment when creating transactions manually. |
| created\_at | string | false | Date/time the asset was created in ISO 8601 extended format |

## Get All Assets

Use this endpoint to get a list of all manually-managed assets associated with the user's account.

> Example 200 Response

```
Copy to Clipboard
{
"assets": [\
    {\
      "id": 72,\
      "type_name": "cash",\
      "subtype_name": "physical cash",\
      "name": "Test Asset 1",\
      "balance": "1201.0100",\
      "to_base": 1020.85,\
      "balance_as_of": "2020-01-26T12:27:22.000Z",\
      "currency": "cad",\
      "institution_name": "Bank of Me",\
      "exclude_transactions": false,\
      "created_at": "2020-01-26T12:27:22.726Z"\
    },\
    {\
      "id": 73,\
      "type_name": "credit",\
      "subtype_name": "credit card",\
      "name": "Test Asset 2",\
      "balance": "0.0000",\
      "to_base": 0,\
      "balance_as_of": "2020-01-26T12:27:22.000Z",\
      "currency": "usd",\
      "institution_name": "Bank of You",\
      "exclude_transactions": false,\
      "created_at": "2020-01-26T12:27:22.744Z"\
    },\
    {\
      "id": 74,\
      "type_name": "vehicle",\
      "subtype_name": "automobile",\
      "name": "Test Asset 3",\
      "balance": "99999999999.0000",\
      "to_base": 657179189.99,\
      "balance_as_of": "2020-01-26T12:27:22.000Z",\
      "currency": "jpy",\
      "institution_name": "Bank of Mom",\
      "exclude_transactions": false,\
      "created_at": "2020-01-26T12:27:22.755Z"\
    },\
    {\
      "id": 75,\
      "type_name": "loan",\
      "subtype_name": null,\
      "name": "Test Asset 4",\
      "balance": "10101010101.0000",\
      "to_base": 307687460.61,\
      "balance_as_of": "2020-01-26T12:27:22.000Z",\
      "currency": "twd",\
      "institution_name": null,\
      "exclude_transactions": true,\
      "created_at": "2020-01-26T12:27:22.765Z"\
    }\
]
}
```

### HTTP Request

`GET https://dev.lunchmoney.app/v1/assets`

## Create Asset

Use this endpoint to create a single (manually-managed) asset.

> Example 200 Response

```
Copy to Clipboard
{
"id": 34061,
"type_name": "depository",
"subtype_name": null,
"name": "My Test Asset",
"display_name": null,
"balance": "67.2100",
"to_base": 47.05,
"balance_as_of": "2022-05-29T21:35:36.557Z",
"closed_on": null,
"created_at": "2022-05-29T21:35:36.564Z",
"currency": "cad",
"institution_name": null,
"exclude_transactions": false
}
```

### HTTP Request

`POST https://dev.lunchmoney.app/v1/assets`

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| type\_name | string | true | - | Must be one of: cash, credit, investment, other, real estate, loan, vehicle, cryptocurrency, employee compensation |
| subtype\_name | string | false | - | Max 25 characters |
| name | string | true | - | Max 45 characters |
| display\_name | string | false | - | Display name of the asset (as set by user) |
| balance | string | true | - | Numeric value of the current balance of the account. Do not include any special characters aside from a decimal point! |
| balance\_as\_of | string | false | Current timestamp | Has no effect if balance is not defined. If balance is defined, but balance\_as\_of is not supplied or is invalid, current timestamp will be used. |
| currency | string | false | User's primary currency | Three-letter lowercase currency in ISO 4217 format. The code sent must exist in our database. Defaults to user's primary currency. |
| institution\_name | string | false | - | Max 50 characters |
| closed\_on | string | false | - | The date this asset was closed |
| exclude\_transactions | boolean | false | false | If true, this asset will not show up as an option for assignment when creating transactions manually |

## Update Asset

Use this endpoint to update a single asset.

> Example 200 Response

```
Copy to Clipboard
{
"id": 12,
"type_name": "cash",
"subtype_name": "savings",
"name": "TD Savings Account",
"balance": "28658.5300",
"to_base": 20061.34,
"balance_as_of": "2020-03-10T05:17:23.856Z",
"currency": "cad",
"institution_name": "TD Bank",
"exclude_transactions": false,
"created_at": "2019-08-10T22:46:19.486Z"
}
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{
"errors": [\
    "type_name must be one of: cash, credit, investment, other, real estate, loan, vehicle, cryptocurrency, employee compensation"\
]
}
```

### HTTP Request

`PUT https://dev.lunchmoney.app/v1/assets/:id`

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| type\_name | string | false | - | Must be one of: cash, credit, investment, other, real estate, loan, vehicle, cryptocurrency, employee compensation |
| subtype\_name | string | false | - | Max 25 characters |
| name | string | false | - | Max 45 characters |
| display\_name | string | false | - | Display name of the asset (as set by user) |
| balance | string | false | - | Numeric value of the current balance of the account. Do not include any special characters aside from a decimal point! |
| balance\_as\_of | string | false | Current timestamp | Has no effect if balance is not defined. If balance is defined, but balance\_as\_of is not supplied or is invalid, current timestamp will be used. |
| currency | string | false | User's primary currency | Three-letter lowercase currency in ISO 4217 format. The code sent must exist in our database. Defaults to user's primary currency. |
| institution\_name | string | false | - | Max 50 characters |
| closed\_on | string | false | - | The date this asset was closed |
| exclude\_transactions | boolean | false | false | If true, this asset will not show up as an option for assignment when creating transactions manually |

* * *

# Plaid Accounts

## Plaid Accounts Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | false | Unique identifier of Plaid account |
| date\_linked | string | false | Date account was first linked in ISO 8601 format |
| name | string | false | Name of the account. Can be overridden by the user. Field is originally set by Plaid. |
| display\_name | string | false | Display name of the account, if not set it will return a concatenated string of institution and account name. |
| type | string | false | Primary type of account. Typically one of:<br>- credit<br>- depository<br>- brokerage<br>- cash<br>- loan<br>- Investment<br> This field is set by Plaid and cannot be altered. |
| subtype | string | true | Optional subtype name of account. This field is set by Plaid and cannot be altered. |
| mask | string | false | Mask (last 3 to 4 digits of account) of account. This field is set by Plaid and cannot be altered. |
| institution\_name | string | false | Name of institution associated with account. This field is set by Plaid and cannot be altered. |
| status | string | false | Denotes the current status of the account within Lunch Money. Must be one of:<br>- active: Account is active and in good state<br>- inactive: Account marked inactive from user. No transactions fetched or balance update for this account.<br>- relink: Account needs to be relinked with Plaid.<br>- syncing: Account is awaiting first import of transactions<br>- error: Account is in error with Plaid<br>- not found: Account is in error with Plaid<br>- not supported: Account is in error with Plaid |
| balance | string | false | Current balance of the account in numeric format to 4 decimal places. This field is set by Plaid and cannot be altered, |
| to\_base | number | true | The balance converted to the user's primary currency |
| currency | string | false | Currency of account balance in ISO 4217 format. This field is set by Plaid and cannot be altered. |
| balance\_last\_update | string | false | Date balance was last updated in ISO 8601 extended format. This field is set by Plaid and cannot be altered. |
| limit | number | true | Optional credit limit of the account. This field is set by Plaid and cannot be altered. |
| import\_start\_date | string | true | Date of earliest date allowed for importing transactions. Transactions earlier than this date are not imported. |
| last\_import | string | true | Timestamp in ISO 8601 extended format of the last time Lunch Money imported new data from Plaid for this account. |
| last\_fetch | string | true | Timestamp in ISO 8601 extended format of the last successful check from Lunch Money for updated data or timestamps from Plaid in ISO 8601 extended format (not necessarily date of last successful import) |
| plaid\_last\_successful\_update | string | false | Timestamp in ISO 8601 extended format of the last time Plaid successfully connected with institution for new transaction updates, regardless of whether any new data was available in the update. |

## Get All Plaid Accounts

Use this endpoint to get a list of all synced Plaid accounts associated with the user's account.

> Example 200 Response

```
Copy to Clipboard
{
"plaid_accounts": [\
    {\
      "id": 91,\
      "date_linked": "2020-01-28",\
      "name": "401k",\
      "display_name": "",\
      "type": "brokerage",\
      "subtype": "401k",\
      "mask": "7468",\
      "institution_name": "Vanguard",\
      "status": "inactive",\
      "limit": null,\
      "balance": "12345.6700",\
      "to_base": 12345.67,\
      "currency": "usd",\
      "balance_last_update": "2020-01-27T01:38:11.862Z",\
      "import_start_date": "2023-01-01",\
      "last_import": "2019-09-04T12:57:09.190Z",\
      "last_fetch": "2020-01-28T01:38:11.862Z",\
      "plaid_last_successful_update": "2020-01-27T01:38:11.862Z",\
    },\
    {\
      "id": 89,\
      "date_linked": "2020-01-28",\
      "name": "Freedom",\
      "display_name": "Freedom Card",\
      "type": "credit",\
      "subtype": "credit card",\
      "mask": "1973",\
      "institution_name": "Chase",\
      "status": "active",\
      "limit": 15000,\
      "balance": "0.0000",\
      "to_base": 0,\
      "currency": "usd",\
      "balance_last_update": "2023-01-27T01:38:07.460Z",\
      "import_start_date": "2023-01-01",\
      "last_import": "2023-01-24T12:57:03.250Z",\
      "last_fetch": "2023-01-28T01:38:11.862Z",\
      "plaid_last_successful_update": "2023-01-27T01:38:11.862Z",\
    }\
]
}
```

Plaid Accounts are individual bank accounts that you have linked to Lunch Money via Plaid. You may link one bank but one bank might contain 4 accounts. Each of these accounts is a Plaid Account.

### HTTP Request

`GET https://dev.lunchmoney.app/v1/plaid_accounts`

## Trigger Fetch from Plaid

_This is an experimental endpoint and parameters and/or response may change._

Use this endpoint to trigger a fetch for latest data from Plaid.

> Example 200 Response

```
Copy to Clipboard
true
```

Returns true if there were eligible Plaid accounts to trigger a fetch for. Eligible accounts are those who `last_fetch` value is over 1 minute ago. (Although the limit is every minute, please use this endpoint sparingly!)

Note that fetching from Plaid is a background job. This endpoint simply queues up the job. You may track the `plaid_last_successful_update`, `last_fetch` and `last_import` properties to verify the results of the fetch.

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| start\_date | string | false | - | Start date for fetch (ignored if end\_date is null) |
| end\_date | string | false | - | End date for fetch (ignored if start\_date is null) |
| plaid\_account\_id | number | false | - | Specific ID of a plaid account to fetch. If left empty, endpoint will trigger a fetch for all eligible accounts |

### HTTP Request

`POST https://dev.lunchmoney.app/v1/plaid_accounts/fetch`

* * *

# Crypto

## Crypto Object

| Attribute Name | Type | Nullable | Description |
| --- | --- | --- | --- |
| id | number | true | Unique identifier for a manual crypto account (no ID for synced accounts) |
| zabo\_account\_id | number | true | Unique identifier for a synced crypto account (no ID for manual accounts, multiple currencies may have the same zabo\_account\_id) |
| source | string | false | One of:<br>- `synced`: this account is synced via a wallet, exchange, etc.<br>- `manual`: this account balance is managed manually |
| name | string | false | Name of the crypto asset |
| display\_name | string | true | Display name of the crypto asset (as set by user) |
| balance | string | false | Current balance |
| balance\_as\_of | string | false | Date/time the balance was last updated in ISO 8601 extended format |
| currency | string | false | Abbreviation for the cryptocurrency |
| status | string | false | The current status of the crypto account. Either active or in error. |
| institution\_name | string | true | Name of provider holding the asset |
| created\_at | string | false | Date/time the asset was created in ISO 8601 extended format |
| to\_base | number | true | The balance converted to the user's primary currency. |

## Get All Crypto

Use this endpoint to get a list of all cryptocurrency assets associated with the user's account. Both crypto balances from synced and manual accounts will be returned.

> Example 200 Response

```
Copy to Clipboard
{
    "crypto": [\
        {\
            "zabo_account_id": 544,\
            "source": "synced",\
            "created_at": "2020-07-27T11:53:02.722Z",\
            "name": "Dogecoin",\
            "display_name": null,\
            "balance": "1.902383849000000000",\
            "balance_as_of": "2021-05-21T00:05:36.000Z",\
            "currency": "doge",\
            "status": "active",\
            "institution_name": "MetaMask"\
        },\
        {\
            "id": 152,\
            "source": "manual",\
            "created_at": "2021-04-03T04:16:48.230Z",\
            "name": "Ether",\
            "display_name": "BlockFi - ETH",\
            "balance": "5.391445130000000000",\
            "balance_as_of": "2021-05-20T16:57:00.000Z",\
            "currency": "ETH",\
            "status": "active",\
            "institution_name": "BlockFi"\
        },\
    ]
}
```

### HTTP Request

`GET https://dev.lunchmoney.app/v1/crypto`

## Update Manual Crypto Asset

Use this endpoint to update a single manually-managed crypto asset (does not include assets received from syncing with your wallet/exchange/etc). These are denoted by `source: manual` from the GET call above.

> Example 200 Response

```
Copy to Clipboard
{
    "id": 1,
    "source": "manual",
    "created_at": "2021-02-10T05:57:34.305Z",
    "name": "Shiba Token",
    "display_name": "SHIB",
    "balance": "12.000000000000000000",
    "currency": "SHIB",
    "status": "active",
    "institution_name": null
}
```

> Example Error Response (sends as 200)

```
Copy to Clipboard
{ "errors": [ "currency is invalid for crypto: fakecoin. It may not be supported yet. Request to get it supported via the app or support@lunchmoney.app" ] }
```

### HTTP Request

`PUT https://dev.lunchmoney.app/v1/crypto/manual/:id`

### Body Parameters

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| name | string | false | - | Official or full name of the account. Max 45 characters |
| display\_name | string | false | - | Display name for the account. Max 25 characters |
| institution\_name | string | false | - | Name of provider that holds the account. Max 50 characters |
| balance | number | false | - | Numeric value of the current balance of the account. Do not include any special characters aside from a decimal point! |
| currency | string | false | - | Cryptocurrency that is supported for manual tracking in our database |

* * *

# Appendix

## Supported Currencies

> Supported Currencies in Lunch Money

```
Copy to Clipboard
aed
afn
all
amd
ang
aoa
ars
aud
awg
azn
bam
bbd
bdt
bgn
bhd
bif
bmd
bnd
bob
brl
bsd
btc
btn
bwp
byn
bzd
cad
cdf
chf
clp
cny
cop
crc
cuc
cup
cve
czk
djf
dkk
dop
dzd
egp
ern
etb
eur
fjd
fkp
gbp
gel
ggp
ghs
gip
gmd
gnf
gtq
gyd
hkd
hnl
hrk
htg
huf
idr
ils
imp
inr
iqd
irr
isk
jep
jmd
jod
jpy
kes
kgs
khr
kmf
kpw
krw
kwd
kyd
kzt
lak
lbp
lkr
lrd
lsl
ltl
lvl
lyd
mad
mdl
mga
mkd
mmk
mnt
mop
mro
mur
mvr
mwk
mxn
myr
mzn
nad
ngn
nio
nok
npr
nzd
omr
pab
pen
pgk
php
pkr
pln
pyg
qar
ron
rsd
rub
rwf
sar
sbd
scr
sdg
sek
sgd
shp
sll
sos
srd
std
svc
syp
szl
thb
tjs
tmt
tnd
top
try
ttd
twd
tzs
uah
ugx
usd
uyu
uzs
vef
vnd
vuv
wst
xaf
xcd
xof
xpf
yer
zar
zmw
zwl
```

Here you'll find a list of currently supported currencies in Lunch Money. If your currency is missing, please let us know via email at [support@lunchmoney.app](mailto:support@lunchmoney.app) and we'll work on getting it added.
