import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    """work with categories"""
    def get_categories(self): # get all categories
        categories = self.cursor.execute(
            "SELECT id, category_name FROM categories;"
        )
        return categories.fetchall()

    def add_categories(self, new_category):
        try:
            self.cursor.execute(
                "INSERT INTO categories (category_name) VALUES (?)",
                (new_category,)
            )
            self.conn.commit()
            return True
        except:
            return False

    def rename_categories(self, old_name, new_name):
        try:
            self.cursor.execute(
                "UPDATE categories SET category_name = ? WHERE category_name = ?",
                (new_name, old_name)
            )
            self.conn.commit()
            return True
        except:
            return False

    def delete_categories(self, name):
        try:
            self.cursor.execute(
                "DELETE FROM categories WHERE category_name = ?",
                (name,)
            )
            self.conn.commit()
            return True
        except:
            return False

    def check_category_exists(self, name):
        ls = self.cursor.execute(
            "SELECT category_name FROM categories WHERE category_name = ?", (name,)
        ).fetchall()
        if not ls:
            return True
        else:
            return False

    # work with products
    def add_product(self, title, text, image, price, phone, cat_id, us_id):
        try:
            self.cursor.execute(
                "INSERT INTO products (product_title, product_text, product_image, product_price, product_phone, product_category, product_owner)"
                "VALUES (?, ?, ?, ?, ?, ?, ?)", (title, text, image, price, phone, cat_id, us_id)
            )
            self.conn.commit()
            return True
        except:
            return False

    def get_last_product(self, u_id):
        products = self.cursor.execute(
            f"SELECT id, product_title, product_image, product_text, product_price, product_phone FROM products WHERE product_owner = ? ORDER BY id desc limit 1",
            (u_id,)
        )

        return products.fetchone()

    def get_all_products(self, cat_id=None):
        if cat_id is None:
            products = self.cursor.execute(
                "SELECT id, product_title, product_image, product_text, product_price, product_phone FROM products"
            )
        else:
            products = self.cursor.execute(
                "SELECT id, product_title, product_image, product_text, product_price, product_phone FROM products "
                "where product_category = ?",
                (cat_id,)
            )
        return products.fetchall()

