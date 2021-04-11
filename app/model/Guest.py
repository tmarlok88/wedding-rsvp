import os
import uuid

from flask_login import UserMixin
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb.exceptions import DoesNotExist
from pynamodb.models import Model
from pynamodb_attributes import UUIDAttribute


class Guest(Model, UserMixin):
    class Meta:
        table_name = os.getenv("DYNAMO_TABLE")
        region = os.getenv("AWS_REGION")
        host = os.getenv("AWS_ENDPOINT_URL", None)

    id = UUIDAttribute(hash_key=True, default=uuid.uuid4)
    email = UnicodeAttribute()
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

    @staticmethod
    def find(guest_id: str):
        try:
            return Guest.get(guest_id)
        except DoesNotExist:
            return None

    @staticmethod
    def find_multi_id(guest_ids: list) -> iter:
        try:
            return Guest.batch_get(guest_ids)
        except DoesNotExist:
            return []
