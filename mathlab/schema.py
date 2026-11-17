"""Machine-readable lesson-card domains derived from the same authored catalog."""
from .catalog import catalog


def lesson_card_schema():
    variants = []
    for lesson in catalog():
        params = {p['id']: {'type': p['type'], 'minimum': p['min'], 'maximum': p['max'],
                            'default': p['default'], 'title': p['label']}
                  for p in lesson['parameters']}
        variants.append({'type': 'object', 'additionalProperties': False,
                         'required': ['schema', 'lesson', 'params'],
                         'properties': {'schema': {'const': 'x3d.mathlab.lesson-card/1'},
                                        'lesson': {'const': lesson['id']},
                                        'params': {'type': 'object', 'additionalProperties': False,
                                                   'properties': params},
                                        'prediction': {'type': 'string', 'maxLength': 2000}}})
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            'title': 'X3D Math Lab parameter card',
            'description': 'Known lesson configurations. Missing parameters take catalog defaults. Geometry is regenerated.',
            'oneOf': variants}
