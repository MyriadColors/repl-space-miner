"""
Rust-like Result type for error handling in the cargo system.

This module provides a generic Result<T, E> type that enables explicit error
handling throughout the cargo system, replacing exceptions and None returns
with a more structured approach.
"""

from typing import Generic, TypeVar, Optional, Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum


T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


class CargoError(Enum):
    """Enumeration of cargo operation errors."""
    INSUFFICIENT_SPACE = "insufficient_space"
    INVALID_QUANTITY = "invalid_quantity"
    ITEM_NOT_FOUND = "item_not_found"
    NEGATIVE_QUANTITY = "negative_quantity"
    NEGATIVE_PRICE = "negative_price"
    UNKNOWN_ITEM_TYPE = "unknown_item_type"
    SERIALIZATION_ERROR = "serialization_error"
    DESERIALIZATION_ERROR = "deserialization_error"
    VALIDATION_ERROR = "validation_error"


@dataclass
class CargoErrorDetails:
    """Detailed error information for cargo operations."""
    error_type: CargoError
    message: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class Result(Generic[T, E]):
    """
    Rust-like Result type for error handling.
    
    A Result<T, E> represents either success (Ok) with a value of type T,
    or failure (Err) with an error of type E.
    """
    _value: Optional[T] = None
    _error: Optional[E] = None
    _is_ok: bool = False
    
    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        """Create a successful Result."""
        return cls(_value=value, _is_ok=True)
    
    @classmethod
    def err(cls, error: E) -> 'Result[T, E]':
        """Create an error Result."""
        return cls(_error=error, _is_ok=False)
    
    def is_ok(self) -> bool:
        """Check if Result is successful."""
        return self._is_ok
    
    def is_err(self) -> bool:
        """Check if Result is an error."""
        return not self._is_ok
    
    def unwrap(self) -> T:
        """
        Get the value, raising an exception if error.
        
        Raises:
            RuntimeError: If called on an error Result
        """
        if self._is_ok:
            return self._value  # type: ignore
        raise RuntimeError(f"Called unwrap on error Result: {self._error}")
    
    def unwrap_or(self, default: T) -> T:
        """Get the value or return default if error."""
        return self._value if self._is_ok else default  # type: ignore
    
    def unwrap_err(self) -> E:
        """
        Get the error, raising an exception if ok.
        
        Raises:
            RuntimeError: If called on a successful Result
        """
        if not self._is_ok:
            return self._error  # type: ignore
        raise RuntimeError("Called unwrap_err on ok Result")
    
    def map(self, func: Callable[[T], U]) -> 'Result[U, E]':
        """
        Transform the value if ok, otherwise return error.
        
        Args:
            func: Function to transform the value
            
        Returns:
            Result with transformed value or original error
        """
        if self._is_ok:
            try:
                return Result.ok(func(self._value))  # type: ignore
            except Exception as e:
                # If the mapping function fails, we need to handle it
                # For now, we'll re-raise, but this could be improved
                raise e
        return Result.err(self._error)  # type: ignore
    
    def and_then(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """
        Chain operations that return Results.
        
        Args:
            func: Function that takes the value and returns a Result
            
        Returns:
            Result from the function or original error
        """
        if self._is_ok:
            return func(self._value)  # type: ignore
        return Result.err(self._error)  # type: ignore
    
    def or_else(self, func: Callable[[E], 'Result[T, E]']) -> 'Result[T, E]':
        """
        Chain operations on error values.
        
        Args:
            func: Function that takes the error and returns a Result
            
        Returns:
            Original Result if ok, or Result from function if error
        """
        if self._is_ok:
            return self
        return func(self._error)  # type: ignore
    
    def __repr__(self) -> str:
        """String representation of Result."""
        if self._is_ok:
            return f"Result.ok({self._value!r})"
        else:
            return f"Result.err({self._error!r})"
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another Result."""
        if not isinstance(other, Result):
            return False
        
        if self._is_ok != other._is_ok:
            return False
        
        if self._is_ok:
            return self._value == other._value
        else:
            return self._error == other._error


# Type aliases for common Result types used in cargo system
CargoResult = Result[T, CargoErrorDetails]
VoidResult = Result[None, CargoErrorDetails]