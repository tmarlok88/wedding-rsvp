# Wedding-rsvp

This is an E-RSVP written for my wedding, but open sourced it
(maybe it could be useful for others).

The whole page can fit into the AWS Free tier
(assuming you won't invite tens of thousands of guests).
The only thing you have to pay for, is the domain name (if you need one).

## Features

* E-mail invitation to the guests
* Export the page to PDF (in case anyone wants to print it) 
* Personal response page with the following fields:
  * Number of guests
  * Food allergies
  * Favourite music
  * Anything else
* Ability to unsubscribe
* Admin page
  * See who viewed their RSVP page
  * See the responses
  * Send out invite e-mails in bulk, or individually
  * Fill out responses for guests who couldn't use the web
* Import guest list from CSV

## Development

`>= node12`

### ReCaptcha support

Since the Admin page authentication is a simple password, and the Guest "authentication" is a URL parameter,
it is a good idea to protect them from brute-forcing.

This can be done, by using ReCAPTCHA.

The first step is to register a v2 ReCAPTCHA here: <https://www.google.com/recaptcha/admin>
You have to list the domain names of the deployment (it can be changed later).

The next step is to register these environment variables (before deploy)

* USE_RECAPTCHA_FOR_ADMIN - If you'd like to enable captcha for admin login
* USE_RECAPTCHA_FOR_GUEST - If you'd like to usa a captcha for the guest page (highly recommended)
* RECAPTCHA_PUBLIC_KEY = The public key provided by google after the registration
* RECAPTCHA_PRIVATE_KEY = The private key provided by google after the registration


### Secret management

We don't use any particular secret store for the sake of simplicity, but in order to avoid hard-coding a secret
into the source code, we need to feed them as an environment variable during serverless deploy:

```bash
export FLASK_SECRET='changeme'
export ADMIN_PASSWORD_HASH=$(python3 -c 'from werkzeug.security import generate_password_hash; print(generate_password_hash("password"))')
sls deploy
```

## Testing

### Preparations

We need to install the test dependencies:

```bash
pip install -r test-requirements.txt
```

for the E2E tests, you should install the following packages (for Firefox and Chromium):
```bash
apt-get install firefox-geckodriver chromium-chromedriver
```

### E2E tests

End-to-end test are used to test the application from and end-user perspective.
They can be executed against a local test environment with mocked dependencies,
or a deployed staging environment as well. 

Running in local environment:

```bash
cd tests/e2e
nose2

# For coverage report:
nose2 --with-coverage --coverage ../../app/
```

### Unit tests

unit tests can be run with nose2 from the tests/unit directory. Like this:

```bash
cd tests/unit
nose2

# For coverage report:
nose2 --with-coverage --coverage ../../app/
```

## Development

### Translations

I use Flask-Babel for localization and internationalization of strings. Here, I'll provide
a short howto for using it. Here is a more complete writeup on the subject: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n

#### Adding a new string

If we want to add a new string to the app which needs to be localized, we have to mark it
in the code:

```python
from flask_babel import _
flash(_('Your post is now live!'))
```

After adding a new string we have to extract the string:

```bash
pybabel extract -F babel.cfg -k _l -o messages.pot .
```

Now we have to regenerate the catalogs:

```bash
pybabel update -i messages.pot -d app/translations
```

Now you have to edit the generated `.po` file, with a text editor and fill in the translations.

After you are done with editing the file, compile it:

```bash
pybabel compile -d app/translations
```

#### Adding a new language

You need to add the language code to the `config.py`:

```python
class Config(object):
  #(...)
  LANGUAGES = ['en', 'hu', 'de']
```

Initialize the `.po` file:

```bash
pybabel init -i messages.pot -d app/translations -l de
```

Edit the generated `.po` file, and recompile the catalog:

```bash
pybabel compile -d app/translations
```
