from test.support import EnvironmentVarGuard

env = EnvironmentVarGuard()
env.set('DYNAMO_TABLE', 'test_table')
env.set('AWS_REGION', 'fake-region')

EXAMPLE_GUEST_1 = {'name': 'Mick Jagger',
                   'email': 'fake@mail.com',
                   'will_attend': True,
                   'favourite_music': 'Rolling Stones',
                   'food_allergies': 'coke',
                   'number_of_guests': 5,
                   'notes': 'I\'ll try to pop in'}

EXAMPLE_GUEST_2 = {'name': 'Bruce Dickinson',
                   'email': 'real@mail.com',
                   'will_attend': False,
                   'favourite_music': 'Belga',
                   'food_allergies': 'sunshine - I\'m a vampire',
                   'number_of_guests': 0}


def create_guest(guest_data: dict):
    with env:
        from tests import context
        return context.app.model.Guest.Guest(**guest_data)


def save_guest(guest_data: dict):
    guest = create_guest(guest_data)
    guest.save()
    return guest


def list_guests():
    with env:
        from tests import context
        return [guest for guest in context.app.model.Guest.Guest().scan()]


def get_guest(guest_id):
    with env:
        from tests import context
        return context.app.model.Guest.Guest.scan(context.app.model.Guest.Guest.id == guest_id).next()


def clear_all_guests():
    with env:
        from tests import context
        for guest in context.app.model.Guest.Guest().scan():
            guest.delete()
