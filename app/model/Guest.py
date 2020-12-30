import os
import uuid

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute, NumberAttribute


class Guest(Model):
    class Meta:
        table_name = os.getenv("DYNAMO_TABLE")
        region = os.getenv("AWS_REGION")
    id = UnicodeAttribute(hash_key=True, default_for_new=uuid.uuid4())
    email = UnicodeAttribute(range_key=True)
    name = UnicodeAttribute()
    food_allergies = UnicodeAttribute()
    last_viewed = UTCDateTimeAttribute()
    last_responded = UTCDateTimeAttribute()
    number_of_guests = NumberAttribute()
    notes = UnicodeAttribute()
    will_attend = BooleanAttribute()
