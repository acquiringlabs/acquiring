# Acquiring

Payment Orchestration Library for Python.

## Overview

Acquiring aspires to be a flexible and effective toolkit for building applications that handle money.

Some reasons you might want to check it out:

- Stable interface via single PaymentFlow class.
- Flexible internals that can be customized for any payment method, existing AND non-existing.
- Platform agnostic (really!), meant to be plugged into your existing Django project easily.
- Support for all database engines under the Django umbrella.
- The creator is a very nice guy!

## Requirements

- One of the supported versions of Python
- A spirit of adventure

## Installation

Install using pip...

```sh
pip install acquiring
```

Add 'acquiring' to your INSTALLED_APPS setting.

```python
INSTALLED_APPS = [
    ...
    'acquiring',
]
```

## Local development

This project relies on Docker as the main way to test and develop. You can `docker compose build` and be ready to roll.

## Funding

This project was created by Alvaro Duran. You can support his work or give him words of encouragement
by subscribing to [Money In Transit](http://news.alvaroduran.com/), the weekly newsletter that bridges the gap
between payments strategy and technology execution.

Speaking of, a few of the ideas that inspired this project were initially installments of Money in Transit:

- [Advice I Wish I Had Known When I Built My First Payment Application](https://news.alvaroduran.com/p/advice-i-wish-i-had-known-when-i)
- [Pizza Place Payments](https://news.alvaroduran.com/p/pizza-place-payments)
- [A Taxonomy of Payment Methods](https://news.alvaroduran.com/p/a-taxonomy-of-payment-methods)
- [Nobody Gets Fired for Choosing Java](https://news.alvaroduran.com/p/nobody-gets-fired-for-choosing-java)
- [Gumroad Wallet, a $100M Opportunity](https://news.alvaroduran.com/p/gumroad-wallet-a-100m-opportunity)
