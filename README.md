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


## Preparations

### Local development environment

The following instructions are for Ubuntu 20.04, but you can get the gist from it...

Get the source code:
```bash
git clone https://github.com/tmarlok88/wedding-rsvp.git
```

Setup serverless:
```bash

#install nodejs (it must be >= 12.0)
curl -sL https://deb.nodesource.com/setup_14.x -o nodesource_setup.sh
bash nodesource_setup.sh
sudo apt-get install -y nodejs npm

#install serverless framework and the required plugins for the project
sudo npm install -g serverless

change to the source
sls plugin install --name serverless-python-requirements
sls plugin install --name serverless-wsgi
sls plugin install --name serverless-finch
sls plugin install --name serverless-plugin-additional-stacks
sls plugin install --name serverless-domain-manager
```

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

### Embed Google Maps with location

1. Enable the Maps Javascript API: https://console.cloud.google.com/apis/
2. get an API key: https://developers.google.com/maps/documentation/embed/map-generator#enable-api-sdk
3. It might be a good idea to restrict the API key to our web address, and to the Maps Javascript API.
4. Create an environment variable called MAPS_API_KEY and set its value to the API key just created
5. customize the maps map in the `rsvp_content.yaml`

### Google calendar event

If you want to assign a Google calendar event to the "Save the date" button, simply create the event
in your calendar, and use the "Publish event" function. This will give you a link.
You have to configure the `basic_data.calendar_event_link` in the `rsvp_content.yaml` to this link.

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


## Deployment

### Deploy permanent resources

There are resources shared between environments, which should be preserved. We have to deploy those before
working on any specific environment:

```bash
serverless deploy additionalstacks
```

### Deploy the stack

The application can be deployed to a specific environment with the following command
(you might have to wait up to 30 minutes):

```bash
serverless deploy --stage <stage>
```

### Deploy static content

We can synchronize the static content with the following command:
```bash
serverless client deploy --stage <stage>
```

### Teardown

If you don't want to host the infrastructure anymore, then you can remove it easily:

```bash
# remove the serverless stack
serverless remove --stage <stage>

# remove the permanent resources
serverless remove additionalstacks
```


CI/CD pipeline


```
main

  │
  │
  │
  │
  │
  │
  │                                ┌───────────────────────────────────────────────────────────────────────┐
  │                                │                                                                       │
  │                                │                                                                       │
  │                 feature│branch │                                                                       │
  │                        │       │                                                                       │
  ├────────────────────────┤       ▼                                                                       │
  │                        │       ┌─────────────────────────────────────────────────────┐                 │
  │                        │       │                                                     │                 │
  │                        │       │                                                     │                 │
  │                        │       │                                                     │                 │
  │                        │       ▼                                                     │                 │
  │                        ├────commit                                                   │                 │
  │                        │       │                   commit pipeline                   │                 │
  │                        │       │              ┌────────────────────┐                 │                 │
  │                        │       └─────────────►│   lint             │                 │                 │
  │                        │                      │     │              │                 │                 │
  │                        │                      │     ▼              │                 │                 │
  │                        │                      │   unit test        │                 │                 │
  │                        │                      │                    │                 │                 │
  │                        │                      │                    │                 │                 │
  │                        │                      └────────────────────┘                 │                 │
  │                        │                                                             │                 │
  │                        │                                                             │                 │
  │                        │                         dev_deploy pipeline                 │                 │
  │                        ├───────open PR        ┌────────────────────┐                 │                 │
  │                        │         │            │                    │                 │                 │
  │                        │         │            │   deploy to dev    │                 │                 │
  │                        │         └───────────►│                    │                 │                 │
  │                        │                      │                    │                 │                 │
  │                        │                      │                    │                 │                 │
  │                        │                      │                    │                 │                 │
  │                        │                      │                    │                 │                 │
  │                        │                      │                    │                 │                 │
  │                        │                      │                    │                 │                 │
  │                        │                      └────────────────────┘                 │                 │
  │                        ├───────something must                                        │                 │
  │                        │       be fixed──────────────────────────────────────────────┘                 │
  │                        │                                                                               │
  │                        │                                                                               │
  │                        │                                                                               │
  │                        │                                                                               │
  │                        │                         merge pipeline                                        │
  │                        ├────────LGTM label     ┌─────────────────────┐                                 │
  │                        │           │           │  E2E tests          │                                 │
  │                        │           │           │    │                │                                 │
  │                        │           │           │    ▼                │                                 │
  │                        │           └──────────►│  personalize        │                                 │
  │                        │                       │    │                │                                 │
  │                        │                       │    ▼                │                                 │
  ├──────────────────────▲─┘                       │  deploy to stage    │                                 │
  │                      │                         │    │                │                                 │
  │                      │      if OK              │    ▼                │      if failed                  │
  │                      └─────────────────────────┤  smoke test stage   ├─────────────────────────────────┘
  │                             merge              │                     │      remove LGTM tag
  │                                                └─────────────────────┘
  │
  │
  │
  ├───────── add version tag
  │
  │
  │
  │                                          release pipeline
  │                                      ┌───────────────────────┐
  ├───────── create release │            │                       │
  │                         └───────────►│  deploy to production │
  │                                      │                       │
  │                                      │                       │
  │                                      │  smoke test           │
  │                                      │                       │
  │                                      │                       │
  │                                      │                       │
  │                                      │                       │
  │                                      │                       │
  │                                      │                       │
                                         └───────────────────────┘
```