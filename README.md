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

## Deployment

Deploy the stack
```bash
sls deploy
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
