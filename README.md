# Jubside #

Velkommen til siden for Nabla-jubileumet 2022!

All python-kode, html, css, javascript og andre statiske filer som har med (ikke enda opprettede) jubileum.nabla.no skal ligge her.

Backenddelen av nettsiden er skrevet i [django](http://djangoproject.org).

## Systemavhengigheter (garantert ikke oppdatert etter kort tid)

* python 3.4 (eller nyere)

## Mappestruktur ##
- jubside -- settings og base-html for hele siden, deler av forside (avhengig av arrangement fra events)
- user -- django-appen for hvordan brukerkontoer fungerer (opprettelse, rettigheter, osv.)
- events -- django-appen for arrangement
- album -- django-app som gir oss album...

## Kjøre siden ##
* Klone repoet
* Sett opp et virtual environment
* pip install -r requirements.txt
