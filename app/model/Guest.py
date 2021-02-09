import os
import uuid

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb_attributes import UUIDAttribute
from flask_login import UserMixin


class Guest(Model, UserMixin):
    class Meta:
        table_name = os.getenv("DYNAMO_TABLE")
        region = os.getenv("AWS_REGION")
        host = os.getenv("AWS_ENDPOINT_URL", None)

    id = UUIDAttribute(hash_key=True, default=uuid.uuid4)
    email = UnicodeAttribute(range_key=True)
    name = UnicodeAttribute()
    food_allergies = UnicodeAttribute(null=True)
    favourite_music = UnicodeAttribute(null=True)
    last_viewed = UTCDateTimeAttribute(null=True)
    last_responded = UTCDateTimeAttribute(null=True)
    number_of_guests = NumberAttribute(null=True)
    notes = UnicodeAttribute(null=True)
    will_attend = BooleanAttribute(null=True)
    filled_by_admin = BooleanAttribute(default=False)

    def get_id(self):
        return str(self.id)

