-- List candidate licenses to add to normalize.py.
SELECT division_id, license_id, license_url, license_title, COUNT(*)
  FROM inventory_dataset
  WHERE license = ''
    AND (
      license_id != ''
      OR license_url != ''
      OR license_title != ''
    )
  GROUP BY division_id, license_id, license_url, license_title
  ORDER BY division_id;

-- Some license identifiers look generic but are unique to catalogs.
-- Check that they remain unique.
SELECT division_id, license_id
  FROM inventory_dataset
  WHERE license_id IN (
    -- IE
    'gov-copyright',
    'marine',
    'psi',
    -- FI
    'other',
    -- GR
    'OKD Compliant::Creative Commons Attribution',
    -- NL
    'creative-commons-attribution-cc-by-'
  )
  GROUP BY division_id, license_id
  ORDER BY license_id;

SELECT division_id, license_title
  FROM inventory_dataset
  WHERE license_title IN (
    -- AU
    'cc-by-sa',
    -- EE
    'Creative Commons BY 3.0',
    -- NL
    'cc-by'
  )
  GROUP BY division_id, license_title
  ORDER BY license_title;



-- List the most common license per country.
SELECT o.division_id, o.license
  FROM inventory_dataset o
  GROUP BY o.division_id, o.license
  HAVING COUNT(*) = (
    SELECT MAX(c) FROM
      (
        SELECT division_id, license, COUNT(*) c
          FROM inventory_dataset
          GROUP BY division_id, license
      ) i
    WHERE i.division_id = o.division_id
  )
  ORDER BY o.license;

-- List the most common internationally reusable license per country.
SELECT o.division_id, o.license
  FROM inventory_dataset o
  GROUP BY o.division_id, o.license
  HAVING COUNT(*) = (
    SELECT MAX(c) FROM
      (
        SELECT division_id, license, COUNT(*) c
          FROM inventory_dataset
          WHERE license LIKE '%creativecommons%'
            OR license LIKE '%opendatacommons%'
            OR license LIKE '%freecreations%'
          GROUP BY division_id, license
      ) i
    WHERE i.division_id = o.division_id
  )
  ORDER BY o.license;

-- List countries with a single license.
SELECT o.division_id, o.license
  FROM inventory_dataset o
  WHERE
    o.division_id IN (
      SELECT m.division_id
        FROM inventory_dataset m
        GROUP BY m.division_id
        HAVING COUNT(*) = (
          SELECT MAX(c) FROM
            (
              SELECT division_id, license, COUNT(*) c
                FROM inventory_dataset
                GROUP BY division_id, license
            ) i
          WHERE i.division_id = m.division_id
        )
    )
    AND o.license != ''
    AND o.license NOT LIKE '%example%'
  GROUP BY o.division_id, o.license
  ORDER BY o.division_id;



-- Investigate NL distributions without accessURL.
SELECT COUNT(*)
  FROM inventory_dataset
  WHERE division_id = 'ocd-division/country:nl';

SELECT COUNT(DISTINCT(d.id))
  FROM inventory_dataset d
  INNER JOIN inventory_distribution i
    ON i.dataset_id = d.id
  WHERE "accessURL" = ''
    AND i.division_id = 'ocd-division/country:nl';

SELECT d.name, COUNT(*) c
  FROM inventory_dataset d
  INNER JOIN inventory_distribution i
    ON i.dataset_id = d.id
  WHERE d.id IN (
    SELECT d.id
      FROM inventory_dataset d
      INNER JOIN inventory_distribution i
        ON i.dataset_id = d.id
      WHERE "accessURL" = ''
        AND i.division_id = 'ocd-division/country:nl'
    )
    AND "landingPage" NOT LIKE '%nationaalgeoregister.nl/geonetwork%'
  GROUP BY d.name
  ORDER BY c;



-- Explore metadata values, to see if any structure or vocabulary is used.

-- ISO 639?
SELECT division_id, COUNT(*), language
  FROM inventory_dataset
  WHERE language != ''
  GROUP BY division_id, language
  ORDER BY division_id, language;
-- ISO 8601?
SELECT division_id, COUNT(*), temporal
  FROM inventory_dataset
  WHERE temporal != ''
  GROUP BY division_id, temporal
  ORDER BY division_id, temporal;

-- Structure?
SELECT division_id, COUNT(*), spatial
  FROM inventory_dataset
  WHERE spatial != ''
  GROUP BY division_id, spatial
  ORDER BY division_id, spatial;
SELECT division_id, COUNT(*), "contactPoint"
  FROM inventory_dataset
  WHERE "contactPoint" != ''
  GROUP BY division_id, "contactPoint"
  ORDER BY division_id, "contactPoint";

-- Vocabulary?
SELECT division_id, COUNT(*), "accrualPeriodicity"
  FROM inventory_dataset
  WHERE "accrualPeriodicity" != ''
  GROUP BY division_id, "accrualPeriodicity"
  ORDER BY division_id, "accrualPeriodicity";
SELECT division_id, COUNT(*), publisher
  FROM inventory_dataset
  WHERE publisher != ''
  GROUP BY division_id, publisher
  ORDER BY division_id, publisher;
SELECT division_id, COUNT(*), theme
  FROM inventory_dataset
  WHERE theme != '{}'
  GROUP BY division_id, theme
  ORDER BY division_id, theme;
SELECT division_id, COUNT(*), keyword
  FROM inventory_dataset
  WHERE keyword != '{}'
  GROUP BY division_id, keyword
  ORDER BY division_id, keyword;

-- Scheme?
SELECT division_id, COUNT(*), identifier
  FROM inventory_dataset
  WHERE identifier != ''
  GROUP BY division_id, identifier
  ORDER BY division_id, identifier;
