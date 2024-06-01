# Changelog

Follows the format of [Common-Changelog](https://common-changelog.org)

## 0.4.0 - 2024-06-01 [Alpha Release]

### Changed

- Rename PaymentFlow as PaymentSaga (alvaro)
- Implement PaymentOperation model in storage/sqlalchemy and its associated Repository (alvaro)
- Ensure immutability of Wide events (Transaction, BlockEvent, PaymentOperation) (alvaro)
- Added FakeUnitOfWork and FakeRepository protocols to improve type system for tests (alvaro)

### Added

### Fixed

- Expose created_at for BlockEvent and PaymentOperation
- Rename Token.created_at to timestamp (see ADR 14. created_at are internal datetimes, timestamps are external)
- Remove non-init fields from repr in dataclasses that implemented them (alvaro)
- Fix faking raw data using json (alvaro)

_First release._

## 0.3.0 - 2024-05-17 [Alpha Release]

### Added

- Added protocols for all domain entities, PaymentFlow service class, Block class, Unit of Work class
[protocols folder](acquiring/protocols/__init__.py) (alvaro).

- Added OperationTypeEnum and OperationStatusEnum [enums file](acquiring/enums.py) (alvaro).

- Added domain entities PaymentAttempt, PaymentMethod, PaymentOperation, BlockEvent, Transaction
[domain folder](acquiring/domain/__init__.py) (alvaro).
- Added domain value objects Item, Token [domain folder](acquiring/domain/__init__.py) (alvaro).

- Added PaymentFlow service class [flow file](acquiring/domain/flow.py)  (alvaro).
    - Added auxiliary decorators payment_operation_type, refresh_payment_method, wrapped_by_transaction,
wrapped_by_block_events [flow file](acquiring/domain/flow.py) (alvaro).
    - Added decision logic functions (can_<operation_type>) [decision logic file](acquiring/domain/decision_logic.py) (alvaro).

- Added support for SqlAlchemy and Django ORMs via Unit of Work pattern (alvaro).
    - Added SqlAlchemyUnitOfWork [file](acquiring/storage/sqlalchemy/unit_of_work.py) and DjangoUnitOfWork
[file](acquiring/storage/django/unit_of_work.py)  (alvaro).
- Added Migration files and Models for domain entities and value objects (alvaro).
