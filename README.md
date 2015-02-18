# OGP ODWG Standards Stream Inventory

Scripts used by the [Open Government Partnership](http://www.opengovpartnership.org/) (OGP) [Open Data Working Group](http://www.opengovpartnership.org/get-involved/join-working-group) Standards Stream to build an inventory of de jure and de facto open data standards.

## Usage

    bundle
    mkvirtualenv inventory
    pip install -r requirements.txt
    createdb inventory
    ./manage.py migrate

Scrape all catalogs:

    ./manage.py scrape

Scrape selected catalogs:

    ./manage.py scrape ca us

Normalize licenses and media types:

    ./manage.py normalize --licenses --media-types

Retrieve HTTP headers for CSV files:

    ./manage.py headers --media_type text/csv

Validate CSV files (must run headers command first):

    ./manage.py validate

Read reports on the usage of licenses, media types, catalog structures, DCAT, Project Open Data Metadata Schema, Schema.org, data federation:

    ./manage.py report --dcat --silent
    ./manage.py report --pod --silent
    ./manage.py report --schemaorg --silent
    ./manage.py report --federation --silent
    ./manage.py report --licenses
    ./manage.py report --media-types

Copyright (c) 2014 Open North Inc., released under the MIT license
