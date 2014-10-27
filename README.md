# OGP ODWG Standards Stream Inventory

Scripts used by the [Open Government Partnership](http://www.opengovpartnership.org/) (OGP) [Open Data Working Group](http://www.opengovpartnership.org/get-involved/join-working-group) Standards Stream to build an inventory of de jure and de facto open data standards.

## Usage

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

Read a report on license usage:

    ./manage.py report --licenses

Read a report on media type usage:

    ./manage.py report --media-types

## Bugs? Questions?

This project's main repository is on GitHub: [http://github.com/opennorth/inventory](http://github.com/opennorth/inventory), where your contributions, forks, bug reports, feature requests, and feedback are greatly welcomed.

Copyright (c) 2014 Open North Inc., released under the MIT license
