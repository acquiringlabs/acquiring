# 10. Exceptions Can Express Domain Concepts Too

Date: 2024-04-28

Relates to [5 - Maybe functions considered harmful](/architecture/decisions/0005-maybe-functions-considered-harmful)
and DDD's [Ubiquitous Langugage](https://martinfowler.com/bliki/UbiquitousLanguage.html).

## Errors in the Database signal alternative paths in the domain

An important consequence of avoiding Maybe functions is that the exceptions raised inside a function that does not
return None can express concepts related to the domain.

An Integrity error in the database may signal that the `PaymentOperation` being added already exists! Therefore, the error
raised needs to express that, rather than bubbling up an error associated with the database engine or the ORM.

The error must be defined as part of the domain.

In this project, error definition is inspired by Django's approach: they belong to the entity. That is, in the previous
example, a `PaymentOperation.Duplicated` error would be raised.

Being rigorous about domain concepts also means being specific about what software errors imply for the domain model.
