from test.support import EnvironmentVarGuard

env = EnvironmentVarGuard()
env.set('DYNAMO_TABLE', 'test_table')
env.set('AWS_REGION', 'fake-region')


def save_guest(guest_data: dict):
    with env:
        import context
        g = context.app.model.Guest.Guest(**guest_data)
        g.save()
        return g.id


def list_guests():
    with env:
        import context
        return [guest for guest in context.app.model.Guest.Guest().scan()]


def clear_all_guests():
    with env:
        import context
        for guest in context.app.model.Guest.Guest().scan():
            guest.delete()
