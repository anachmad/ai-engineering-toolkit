"""Bounded, declarative requirement ID formats selected explicitly by a project."""
import json
import re
from pathlib import Path

TYPES = {'BO', 'BR', 'KPI', 'PR', 'FR', 'NFR', 'ADR'}
PREFIX = re.compile(r'[A-Z][A-Z0-9-]{0,15}')


def load(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'schema_version', 'formats'} or type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ValueError('Invalid ID format configuration schema')
    formats = data['formats']
    if not isinstance(formats, dict) or not formats or not set(formats) <= TYPES:
        raise ValueError('ID formats must be a nonempty object using BO, BR, KPI, PR, FR, NFR or ADR')
    for kind, rules in formats.items():
        if not isinstance(rules, list) or not 1 <= len(rules) <= 32:
            raise ValueError(f'{kind} formats must be a list of 1–32 rules')
        seen = set()
        for rule in rules:
            if not isinstance(rule, dict) or set(rule) != {'prefix', 'digits'}:
                raise ValueError(f'Invalid {kind} ID rule')
            prefix, digits = rule['prefix'], rule['digits']
            if not isinstance(prefix, str) or not PREFIX.fullmatch(prefix) or prefix[-1].isdigit() or type(digits) is not int or not 1 <= digits <= 12:
                raise ValueError(f'Invalid {kind} prefix or digit count')
            key = (prefix, digits)
            if key in seen:
                raise ValueError(f'Duplicate {kind} format')
            seen.add(key)
    return formats


def matches(value, kind, formats, default_pattern):
    if formats and kind in formats:
        for rule in formats[kind]:
            if value.startswith(rule['prefix']):
                tail = value[len(rule['prefix']):]
                if len(tail) == rule['digits'] and re.fullmatch('[0-9]+', tail):
                    return True
        return False
    return bool(re.fullmatch(default_pattern, value))
