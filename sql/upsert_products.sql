INSERT INTO products (
    product_id,
    title,
    price,
    category,
    stock
)
SELECT
    product_id,
    title,
    price,
    category,
    stock
FROM products_staging

ON CONFLICT (product_id)
DO UPDATE SET
    title = EXCLUDED.title,
    price = EXCLUDED.price,
    category = EXCLUDED.category,
    stock = EXCLUDED.stock;