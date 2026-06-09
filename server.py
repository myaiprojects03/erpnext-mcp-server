from fastmcp import FastMCP
from erpnext_client import ERPNextClient, ERPNextError

mcp = FastMCP("erpnext-mcp")
erp = ERPNextClient()


def _safe(fn):
    """Wrap tool body to convert exceptions into user-facing error dicts."""
    try:
        return fn()
    except ERPNextError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {type(e).__name__}: {e}"}


@mcp.tool()
def get_outstanding_invoices(customer: str | None = None, limit: int = 20):
    """
    Fetch outstanding (unpaid, partly paid, or overdue) sales invoices from ERPNext.

    Args:
        customer: Optional customer name to filter by.
        limit: Maximum number of invoices to return (default 20).

    Returns a list of invoice records with name, customer, grand_total, outstanding_amount, due_date, and status.
    """
    def run():
        filters = [["status", "in", ["Unpaid", "Overdue", "Partly Paid"]]]
        if customer:
            filters.append(["customer", "=", customer])
        fields = ["name", "customer", "grand_total", "outstanding_amount",
                  "due_date", "status", "posting_date"]
        return erp.get_list("Sales Invoice", filters=filters, fields=fields, limit=limit)
    return _safe(run)


@mcp.tool()
def create_customer(
    customer_name: str,
    customer_type: str = "Company",
    customer_group: str = "Commercial",
    territory: str = "All Territories",
):
    """
    Create a new customer record in ERPNext.

    Args:
        customer_name: Display name for the customer.
        customer_type: 'Company' or 'Individual'. Defaults to 'Company'.
        customer_group: Customer group classification. Defaults to 'Commercial'.
        territory: Territory the customer belongs to. Defaults to 'All Territories'.

    Returns the created customer record.
    """
    def run():
        payload = {
            "customer_name": customer_name,
            "customer_type": customer_type,
            "customer_group": customer_group,
            "territory": territory,
        }
        return erp.create_doc("Customer", payload)
    return _safe(run)


@mcp.tool()
def get_stock_summary(item_code: str | None = None, warehouse: str | None = None, limit: int = 50):
    """
    Get a stock summary across warehouses, optionally filtered by item or warehouse.

    Args:
        item_code: Optional item code to filter by.
        warehouse: Optional warehouse name to filter by.
        limit: Maximum number of stock rows to return (default 50).

    Returns a list of stock balance records with item_code, warehouse, actual_qty, and stock_value.
    """
    def run():
        filters = []
        if item_code:
            filters.append(["item_code", "=", item_code])
        if warehouse:
            filters.append(["warehouse", "=", warehouse])
        fields = ["item_code", "warehouse", "actual_qty", "stock_value"]
        return erp.get_list("Bin", filters=filters or None, fields=fields, limit=limit)
    return _safe(run)

@mcp.tool()
def search_products(query: str, limit: int = 20):
    """
    Search the product catalog by item name or item code.

    Args:
        query: Search term to match against item name.
        limit: Maximum number of results to return (default 20).

    Returns a list of matching items with item_code, item_name, item_group, standard_rate, and stock_uom.
    """
    def run():
        filters = [
            ["disabled", "=", 0],
            ["item_name", "like", f"%{query}%"],
        ]
        fields = ["item_code", "item_name", "item_group", "standard_rate", "stock_uom"]
        return erp.get_list("Item", filters=filters, fields=fields, limit=limit)
    return _safe(run)


@mcp.tool()
def get_sales_report(from_date: str, to_date: str, customer: str | None = None):
    """
    Generate a sales summary between two dates (inclusive).

    Args:
        from_date: Start date in YYYY-MM-DD format.
        to_date: End date in YYYY-MM-DD format.
        customer: Optional customer name to filter by.

    Returns total invoice count, total sales, total outstanding, and full invoice breakdown.
    """
    def run():
        filters = [
            ["docstatus", "=", 1],
            ["posting_date", "between", [from_date, to_date]],
        ]
        if customer:
            filters.append(["customer", "=", customer])
        fields = ["name", "customer", "posting_date", "grand_total", "outstanding_amount", "status"]
        invoices = erp.get_list("Sales Invoice", filters=filters, fields=fields, limit=500)
        total_sales = sum(inv.get("grand_total", 0) for inv in invoices)
        total_outstanding = sum(inv.get("outstanding_amount", 0) for inv in invoices)
        return {
            "from_date": from_date,
            "to_date": to_date,
            "customer_filter": customer,
            "total_invoices": len(invoices),
            "total_sales": round(total_sales, 2),
            "total_outstanding": round(total_outstanding, 2),
            "invoices": invoices,
        }
    return _safe(run)

if __name__ == "__main__":
    mcp.run()