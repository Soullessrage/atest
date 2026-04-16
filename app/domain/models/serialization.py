from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, get_args, get_origin

T = TypeVar("T")


def serialize_value(value: Any) -> Any:
    if is_dataclass(value):
        return serialize_dataclass(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    return value


def serialize_dataclass(instance: object) -> Dict[str, Any]:
    if not is_dataclass(instance):
        raise ValueError("serialize_dataclass expects a dataclass instance")

    output: Dict[str, Any] = {}
    for field_def in fields(instance):
        output[field_def.name] = serialize_value(getattr(instance, field_def.name))
    return output


def _resolve_optional(field_type: Any) -> Any:
    origin = get_origin(field_type)
    if origin is Union:
        args = [arg for arg in get_args(field_type) if arg is not type(None)]
        return args[0] if args else Any
    return field_type


def deserialize_value(value: Any, target_type: Any) -> Any:
    if value is None:
        return None

    resolved_type = _resolve_optional(target_type)
    origin = get_origin(resolved_type)

    if origin is list:
        item_type = get_args(resolved_type)[0] if get_args(resolved_type) else Any
        return [deserialize_value(item, item_type) for item in value]

    if origin is dict:
        key_type, val_type = get_args(resolved_type) if get_args(resolved_type) else (Any, Any)
        return {
            deserialize_value(k, key_type): deserialize_value(v, val_type)
            for k, v in value.items()
        }

    if isinstance(resolved_type, type) and issubclass(resolved_type, Enum):
        return resolved_type(value)

    if resolved_type is datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    if is_dataclass(resolved_type) and isinstance(value, dict):
        return deserialize_dataclass(resolved_type, value)

    return value


def deserialize_dataclass(cls: Type[T], data: Dict[str, Any]) -> T:
    if not is_dataclass(cls):
        raise ValueError("deserialize_dataclass expects a dataclass class")

    resolved: Dict[str, Any] = {}
    for field_def in fields(cls):
        raw_value = data.get(field_def.name)
        resolved[field_def.name] = deserialize_value(raw_value, field_def.type)
    return cls(**resolved)
