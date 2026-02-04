# Testing

## Setup

1. Copy `test_config.json.example` to `test_config.json`:
   ```bash
   cp tests/test_config.json.example tests/test_config.json
   ```

2. Edit `test_config.json` with your device details:
   ```json
   {
     "host": "192.168.1.100",
     "user_type": "Professional",
     "password": "password"
   }
   ```

   Valid `user_type` values: `"User"`, `"Professional"`, or `"Renson Technician"`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Tests

Run all tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=custom_components.renson_embedded tests/
```

Run specific test file:
```bash
pytest tests/test_client.py
```

## Notes

- `test_config.json` is ignored by git to prevent committing credentials
- Tests will be skipped if `test_config.json` is not found
- Tests require a real Renson device to be available on the network
