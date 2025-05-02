"""Custom types for the Zendesk Sell tap."""

from singer_sdk import typing as th

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
ArrayType = th.ArrayType
DateTimeType = th.DateTimeType(nullable=True)
DateType = th.DateType(nullable=True)
StringType = th.StringType(nullable=True)
BooleanType = th.BooleanType(nullable=True)
IntegerType = th.IntegerType(nullable=True)
NumberType = th.NumberType(nullable=True)

AddressType = ObjectType(
    Property("line1", StringType, nullable=True),
    Property("city", StringType, nullable=True),
    Property("postal_code", StringType, nullable=True),
    Property("state", StringType, nullable=True),
    Property("country", StringType, nullable=True),
    nullable=True,
)
