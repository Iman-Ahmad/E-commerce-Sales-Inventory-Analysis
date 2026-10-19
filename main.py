
import pandas as pd


# ==========================================
# 1. LOAD DATA
# ==========================================

def load_data(file_path):
    """Load product data from a CSV file."""
    return pd.read_csv(file_path)


# ==========================================
# 2. CLEAN AND VALIDATE DATA
# ==========================================

def clean_data(products_df):
    """Clean product data and handle missing values."""

    # Standardize category names
    products_df["category"] = (
        products_df["category"]
        .str.strip()
        .str.title()
    )

    # Convert prices to numeric values
    products_df["price"] = (
        products_df["price"]
        .astype(str)
        .str.replace(" USD", "", regex=False)
    )

    products_df["price"] = pd.to_numeric(
        products_df["price"],
        errors="coerce"
    )

    # Ensure quantity is numeric
    products_df["quantity"] = pd.to_numeric(
        products_df["quantity"],
        errors="coerce"
    )

    # Remove duplicate rows
    products_df = products_df.drop_duplicates().copy()

    # Fill missing prices using the median of each category
    category_medians = products_df.groupby("category")["price"].transform(
        "median"
    )

    products_df["price"] = products_df["price"].fillna(category_medians)

    # Validate cleaned data
    print("\n--- Data Quality Check ---")
    print("Missing values per column:")
    print(products_df.isna().sum())

    print("\nDuplicate rows:", products_df.duplicated().sum())

    return products_df


# ==========================================
# 3. INVENTORY ANALYSIS
# ==========================================

def analyze_inventory(products_df):
    """Calculate stock value and summarize inventory."""

    # Calculate stock value for each product
    products_df["stock_value"] = (
        products_df["price"] * products_df["quantity"]
    )

    # Total value of all inventory
    total_stock_value = products_df["stock_value"].sum()

    # Stock value grouped by category
    stock_value_by_category = (
        products_df.groupby("category")["stock_value"].sum()
    )

    # Product with the highest stock value
    highest_value_index = products_df["stock_value"].idxmax()
    highest_value_product = products_df.loc[highest_value_index]

    # Summary of inventory metrics by category
    category_summary = products_df.groupby("category").agg(
        total_products=("name", "count"),
        total_quantity=("quantity", "sum"),
        average_price=("price", "mean"),
        total_stock_value=("stock_value", "sum"),
        in_stock_products=("quantity", lambda x: (x > 0).sum()),
        out_of_stock_products=("quantity", lambda x: (x == 0).sum()),
    )

    # Calculate percentages for each category
    category_summary["in_stock_percentage"] = (
        category_summary["in_stock_products"]
        / category_summary["total_products"]
        * 100
    )

    category_summary["out_of_stock_percentage"] = (
        category_summary["out_of_stock_products"]
        / category_summary["total_products"]
        * 100
    )

    category_summary["stock_value_share_percentage"] = (
        category_summary["total_stock_value"]
        / total_stock_value
        * 100
        if total_stock_value != 0
        else 0
    )

    return (
        products_df,
        total_stock_value,
        stock_value_by_category,
        highest_value_product,
        category_summary,
    )


# ==========================================
# 4. DISPLAY RESULTS
# ==========================================

def display_results(
    products_df,
    total_stock_value,
    stock_value_by_category,
    highest_value_product,
    category_summary,
):
    """Display key inventory analysis results."""

    print("\n--- Inventory Analysis ---")

    print("\nStock value per product:")
    print(products_df[["name", "category", "stock_value"]])

    print("\nTotal stock value:")
    print(f"${total_stock_value:,.2f}")

    print("\nProduct with the highest stock value:")
    print(highest_value_product[["name", "category", "stock_value"]])

    print("\nStock value by category:")
    print(stock_value_by_category.round(2))

    print("\n--- Category Summary ---")
    print(category_summary.round(2))

    highest_stock_share_category = (
        category_summary["stock_value_share_percentage"].idxmax()
    )

    print("\nCategory with the highest share of total stock value:")
    print(
        f"{highest_stock_share_category}: "
        f"{category_summary.loc[highest_stock_share_category, 'stock_value_share_percentage']:.2f}%"
    )


# ==========================================
# 5. RUN THE ANALYSIS
# ==========================================

def main():
    products_df = load_data("products.csv")

    products_df = clean_data(products_df)

    (
        products_df,
        total_stock_value,
        stock_value_by_category,
        highest_value_product,
        category_summary,
    ) = analyze_inventory(products_df)

    display_results(
        products_df,
        total_stock_value,
        stock_value_by_category,
        highest_value_product,
        category_summary,
    )


if __name__ == "__main__":
    main()
