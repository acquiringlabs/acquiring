# 4. Reduce Doctests to a minimum

Date: 2024-04-11

## I've changed my mind about doctests

I used to be sold on [doctests](https://docs.python.org/3/library/doctest.html).

In this project, initially, I had doctests for all the decision logic functions, and a few more.
It was so easy to have the tests right next to the code itself. Not for very complex tests, but for the simple stuff it was great.

What I've realized is that choosing doctests means missing out on many things that are straightforward with pytests.

For starters, I can't use the debugger. And I spend 90% of my development time in the debugger.

But also, tests are cleaner and more complete. For the decision logic tests, for example, I can parametrize all possible
statuses in one function, but I can't do that in doctests.

I've tested this hypothesis over the last few days. What would happen if I refactor the doctests?

As you might guess, I've become convinced with the changes. This codebase will see very few doctests from now on.