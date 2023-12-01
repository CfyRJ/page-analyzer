CREATE TABLE IF NOT EXISTS urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255),
    created_at timestamp
);
CREATE TABLE IF NOT EXISTS url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES table_urls (id),
    status_code integer,
    h1 varchar(255),
    title varchar(255),
    description text,
    created_at timestamp
);


-- SELECT url_id, MAX(created_at) AS created_at FROM url_checks GROUP BY url_id;
-- SELECT url_checks.url_id, status_code, url_checks.created_at FROM url_checks JOIN (SELECT url_id, MAX(created_at) AS created_at FROM url_checks GROUP BY url_id) AS tab ON url_checks.url_id=tab.url_id AND url_checks.created_at=tab.created_at;

-- SELECT id, name, t.created_at, status_code
-- FROM table_urls JOIN (
--     SELECT url_checks.url_id, status_code, url_checks.created_at
--     FROM url_checks JOIN (
--         SELECT url_id, MAX(created_at) AS created_at
--         FROM url_checks GROUP BY url_id) AS tab
--     ON url_checks.url_id = tab.url_id
--     AND url_checks.created_at = tab.created_at) AS t
-- ON id = t.url_id ORDER BY id DESC;
