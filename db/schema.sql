DROP TABLE IF EXISTS readings;
DROP TABLE IF EXISTS bins;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    sku         TEXT,
    notes       TEXT
);

CREATE TABLE bins (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    label         TEXT NOT NULL,           -- e.g. "Bin A3"
    product_id    INTEGER,                 -- FK to products.id
    max_qty       INTEGER NOT NULL,
    low_threshold INTEGER NOT NULL,
    roi_x         INTEGER NOT NULL,
    roi_y         INTEGER NOT NULL,
    roi_w         INTEGER NOT NULL,
    roi_h         INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE readings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id     INTEGER NOT NULL,
    qty        INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (bin_id) REFERENCES bins(id)
);
