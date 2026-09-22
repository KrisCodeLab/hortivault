"""
Validierung des ankommenden Datenpaketes unter verwendung von jsonschema.
Unvollständige sowie falsch strukturierte Datenpakete werden verworfen. 

"""
from jsonschema import validate, ValidationError


UNIT_SCHEMA = {
    "type": "string",

    "enum": [
        "celsius",
        "percent",
        "lux",
        "i2c_raw",
        "adc_raw",
        "raw_ds"
    ],
}


VALUE_SCHEMA = {
    "type": "object",

    "properties": {
        "value": {"type": ["number", "null"]},
        "unit": UNIT_SCHEMA
    },

    "required": ["value", "unit"],
    "additionalProperties": False
}


MEASUREMENT_GROUP_SCHEMA = {
    "type": "object",

    "properties": {
        "temperature": VALUE_SCHEMA,
        "humidity": VALUE_SCHEMA,
        "moisture": VALUE_SCHEMA,
        "light": VALUE_SCHEMA
    },

    "minProperties": 1,
    "additionalProperties": False
}


MEASUREMENTS_SCHEMA = {
    "type": "object",

    "properties": {
        "real": MEASUREMENT_GROUP_SCHEMA,
        "raw": MEASUREMENT_GROUP_SCHEMA,
        "is_test": {"type": "boolean"}
    },

    "required": ["real", "raw", "is_test"],
    "additionalProperties": False
}


SENSOR_SCHEMA = {
    "type": "object",

    "properties": {
        "display_name": {"type": "string"},
        "measurements": MEASUREMENTS_SCHEMA
    },

    "required": ["display_name", "measurements"],
    "additionalProperties": False
}


PACKET_SCHEMA = {
    "type": "object",
    "minProperties": 1,

    "patternProperties": {
        r"^sensor_[0-9]+$": SENSOR_SCHEMA
    },

    "additionalProperties": False
}


def packet_validator(data_pack):
    try:
        validate(instance=data_pack, schema=PACKET_SCHEMA)
        return True

    except ValidationError as e:
        print(f"[ERROR]: Übertragungsfehler, Messpaket nicht valide: {e.message}")
        return False


if __name__ == "__main__":

    import json

    string_pack = '''
    {
        "sensor_01": {
            "display_name": "Boden Feuchte",
            "measurements": {
                "real": {
                    "moisture": {
                        "value": 3.3,
                        "unit": "percent"
                    }
                },
                "raw": {
                    "moisture": {
                        "value": 2558,
                        "unit": "adc_raw"
                    }
                },
                "is_test": false
            }
        }
    }
    '''

    parsed_pack = json.loads(string_pack)

    print(packet_validator(parsed_pack))