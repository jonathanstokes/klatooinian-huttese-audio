# Roll20 Unit Tests

This directory contains unit tests for the Roll20 integration module.

## Running Tests

Run all Roll20 tests:
```bash
poetry run pytest tests/unit/test_roll20/ -v
```

Run specific test file:
```bash
poetry run pytest tests/unit/test_roll20/test_client.py -v
```

Run specific test class:
```bash
poetry run pytest tests/unit/test_roll20/test_client.py::TestRoll20ClientImport -v
```

Run specific test:
```bash
poetry run pytest tests/unit/test_roll20/test_client.py::TestRoll20ClientImport::test_import_client_module -v
```

## Test Coverage

### `test_client.py`

#### TestRoll20ClientImport
- **test_import_client_module**: Verifies client module compiles without syntax errors
- **test_import_config_module**: Verifies config module compiles without syntax errors
- **test_client_class_exists**: Verifies Roll20Client class can be imported

#### TestRoll20ClientStructure
- **test_client_instantiation**: Verifies Roll20Client can be instantiated with correct initial state
- **test_client_has_required_methods**: Verifies all required methods exist
- **test_client_methods_are_async**: Verifies methods are async coroutines

#### TestRoll20Config
- **test_config_requires_env_vars**: Verifies config raises error when env vars missing
- **test_config_with_valid_env_vars**: Verifies config loads env vars correctly
- **test_config_campaign_url_property**: Verifies campaign URL is generated correctly
- **test_config_login_url_property**: Verifies login URL is correct

#### TestRoll20ClientLogic
- **test_login_when_already_logged_in**: Verifies login returns early if already logged in
- **test_launch_game_requires_login**: Verifies launch_game raises error if not logged in
- **test_launch_game_when_already_loaded**: Verifies launch_game returns early if already loaded
- **test_close_resets_state**: Verifies close() resets all client state

## What These Tests Catch

1. **Syntax Errors**: Import tests will fail if there are Python syntax errors
2. **Missing Methods**: Structure tests will fail if required methods are missing
3. **Type Errors**: Tests verify methods are async when they should be
4. **Logic Errors**: Tests verify basic state management logic
5. **Configuration Errors**: Tests verify config validation works correctly

## What These Tests Don't Cover

These are **unit tests** that don't require a browser or network connection. They don't test:
- Actual browser automation
- Network requests to Roll20
- DOM element selection
- Login flow with real credentials

For integration testing with a real browser, use:
```bash
python -m src.roll20.test_client --headful
```

## Adding New Tests

When adding new functionality to the Roll20 client:

1. Add import tests for new modules
2. Add structure tests for new classes/methods
3. Add logic tests for new state management
4. Keep tests fast and isolated (no network/browser)

