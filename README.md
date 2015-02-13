# OGP ODWG Standards Stream Inventory

Scripts used by the [Open Government Partnership](http://www.opengovpartnership.org/) (OGP) [Open Data Working Group](http://www.opengovpartnership.org/get-involved/join-working-group) Standards Stream to build an inventory of de jure and de facto open data standards.

## Usage

    bundle
    mkvirtualenv inventory
    pip install -r requirements.txt
    createdb inventory
    ./manage.py migrate

Scrape all CKAN APIs:

    ./manage.py scrape

Scrape select CKAN APIs:

    ./manage.py scrape ca us

Normalize licenses and media types:

    ./manage.py normalize --licenses --media-types

Read reports on the usage of licenses, media types, DCAT, Project Open Data Metadata Schema, Schema.org:

    ./manage.py report --licenses
    ./manage.py report --media-types
    ./manage.py report --dcat --silent
    ./manage.py report --pod --silent
    ./manage.py report --schemaorg --silent


Copyright (c) 2014 Open North Inc., released under the MIT license
