# mock-device
Mocked IoT devices for testing purposes

## Request file format (JSON)
```
{
    'id': constant_string,
    'timestamp': posix_timestamp,
    'blood_pressure': {
        'systolic': float,
        'diastolic': float,
    },
    'pulse': float,
    'saturation': float,
    'electrodermal_response': float,
    'body_temperature': float,
    'blood_glucose_content': float,
    'blood_alcohol_content': float,
    'cholesterol': {
        'ldl': float,
        'hdl': float,
    },
    'steps': integer,
    'gps': {
        'latitude': float,
        'longitude': float,
    },
    'birth': {
        'year': year,
        'month': month,
        'day': day,
    }
}
```

## To-do
- [x] Parameter generation
  - [x] Blood pressure systolic
  - [x] Blood pressure diastolic
  - [x] Pulse
  - [x] Body temperature
  - [x] Saturation
  - [x] Blood glucose content
  - [x] Electrodermal response
  - [x] Blood alcohol content
  - [x] Steps
  - [x] Cholesterol
    - [x] LDL
    - [x] HDL
  - [x] GPS coordinates
    - [x] Longitude
    - [x] Latitude
  - [x] Date of birth
    - [x] Year
    - [x] Month
    - [x] Day
- [ ] Parameter updates
  - [ ] Blood pressure systolic
  - [ ] Blood pressure diastolic
  - [ ] Pulse
  - [ ] Body temperature
  - [ ] Saturation
  - [ ] Blood glucose content
  - [ ] Electrodermal response
  - [ ] Blood alcohol content
  - [ ] Steps
  - [ ] Cholesterol
    - [ ] LDL
    - [ ] HDL
  - [x] GPS coordinates
    - [x] Longitude
    - [x] Latitude
- [x] REST Client
- [x] Startup script (to run devices simultaneously)
