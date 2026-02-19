# Data Quality Skill

## Overview
Implement data quality checks to ensure accurate and reliable data.

## Data Quality Dimensions

| Dimension | Description | Check |
|-----------|-------------|-------|
| Completeness | All required fields populated | Null checks |
| Accuracy | Data is correct | Validation rules |
| Consistency | Data is consistent across sources | Cross-reference |
| Timeliness | Data is up-to-date | Timestamp checks |
| Uniqueness | No duplicate records | Deduplication |

## Validation Rules
```python
VALIDATION_RULES = {
    'customer': {
        'phone': {
            'required': True,
            'pattern': r'^[6-9]\d{9}$',
            'message': 'Invalid Indian phone number'
        },
        'name': {
            'required': True,
            'min_length': 2,
            'max_length': 100
        },
        'gender': {
            'required': True,
            'enum': ['male', 'female']
        }
    }
}
```

## Data Validation
```python
def validate_customer(data: dict) -> tuple[bool, list]:
    errors = []

    if not re.match(r'^[6-9]\d{9}$', data.get('phone', '')):
        errors.append('Invalid phone number')

    if len(data.get('name', '')) < 2:
        errors.append('Name too short')

    return len(errors) == 0, errors
```

## Data Quality Score
```python
def calculate_quality_score(salon_id: str) -> float:
    customers = get_all_customers(salon_id)
    total_fields = len(customers) * 10
    complete_fields = count_complete_fields(customers)
    return (complete_fields / total_fields) * 100
```
