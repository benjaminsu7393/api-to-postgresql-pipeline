DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price NUMERIC(10,2),
    category TEXT,
    stock INTEGER
);