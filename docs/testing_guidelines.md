# Testing Guidelines for Glad Tidings School Portal

## Overview

This document outlines the testing practices for the Glad Tidings School Management Portal project. Following these guidelines ensures consistent, reliable, and maintainable tests across the application.

## Test Structure

We use a combination of Django's testing framework and pytest for our testing needs. Tests are organized by app and further divided by test type.

### Directory Structure

```
app_name/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── test_api.py
```

### Test Categories

We categorize tests using pytest markers:

- `url` - Testing URL routing and access permissions
- `security` - Testing security features like authentication, authorization, etc.
- `responsive` - Testing responsive design aspects
- `features` - Testing core application features
- `performance` - Testing performance-related aspects
- `forms` - Testing form validation and submission
- `mobile` - Testing mobile-specific functionality
- `api` - Testing API endpoints

### Test Types

We distinguish between different test types:

- `unit` - Isolated tests for individual components
- `integration` - Tests that verify interactions between components

## Writing Tests

### Naming Conventions

- Test files should be named `test_*.py`
- Test classes should be named `*Tests`
- Test methods should be named `test_*` and clearly describe what they test

### Test Organization

- Group related tests in test classes
- Use descriptive method names
- Add docstrings to test methods explaining what they verify

### Fixtures

Use pytest fixtures for test setup:

```python
@pytest.fixture
def sample_user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )

def test_user_authentication(sample_user):
    # Test using the fixture
    pass
```

## Running Tests

### Local Development

```bash
# Using pytest
python -m pytest

# With coverage
coverage run -m pytest
coverage report
coverage html
```

### Specific Test Categories

```bash
# Run only unit tests
python -m pytest -m unit

# Run only URL tests
python -m pytest -m url
```

### CI/CD Pipeline

Tests are automatically run in the CI/CD pipeline on every push to the main branch and pull requests. The pipeline:

1. Installs all required dependencies
2. Runs linting (flake8)
3. Runs tests with coverage
4. Reports test coverage

## Best Practices

1. **Keep tests isolated** - Tests should not rely on other tests to run
2. **Clean up after tests** - Use `setUp` and `tearDown` or fixtures to clean up test data
3. **Test edge cases** - Include both happy and error paths
4. **Use assertions effectively** - Use the most specific assertion for the job
5. **Write deterministic tests** - Tests should produce the same result when run repeatedly
6. **Keep tests fast** - Slow tests slow down development
7. **Use client for view tests** - Use Django test client for testing views

## Common Testing Patterns

### Testing Models

```python
def test_model_creation(self):
    obj = ModelName.objects.create(field="value")
    self.assertEqual(obj.field, "value")
    
def test_model_str_method(self):
    obj = ModelName.objects.create(field="value")
    self.assertEqual(str(obj), "expected string value")
```

### Testing Views

```python
def test_view_requires_login(self):
    response = self.client.get(reverse('view_name'))
    self.assertRedirects(response, '/login/?next=/expected-path/')
    
def test_authenticated_view_access(self):
    self.client.login(username='user', password='pass')
    response = self.client.get(reverse('view_name'))
    self.assertEqual(response.status_code, 200)
```

### Testing Forms

```python
def test_form_validation(self):
    form = MyForm(data={'field': 'invalid value'})
    self.assertFalse(form.is_valid())
    self.assertIn('field', form.errors)
    
def test_form_save(self):
    form = MyForm(data={'field': 'valid value'})
    self.assertTrue(form.is_valid())
    instance = form.save()
    self.assertEqual(instance.field, 'valid value')
```
