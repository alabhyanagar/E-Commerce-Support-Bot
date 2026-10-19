"""
mock_db.py - E-Commerce Mock Database & Helper Tools
Simulates backend order management, support ticketing, and inventory catalog.
"""

# ---------------------------------------------------------------------------
# MOCK DATABASE DATA
# ---------------------------------------------------------------------------

MOCK_ORDERS = {
    "ORD1001": {
        "user_id": "user_101",
        "product_name": "Wireless Noise-Cancelling Headphones",
        "price": "₹4,999",
        "status": "In Transit",
        "expected_delivery": "Tomorrow by 8 PM",
        "courier": "Ekart Logistics (TRK987654)",
        "can_cancel": True
    },
    "ORD1002": {
        "user_id": "user_101",
        "product_name": "Mechanical Gaming Keyboard",
        "price": "₹2,499",
        "status": "Delivered",
        "delivery_date": "2 days ago",
        "return_eligible_until": "5 days left",
        "can_cancel": False
    },
    "ORD1003": {
        "user_id": "user_102",
        "product_name": "Smart Fitness Watch V2",
        "price": "₹2,999",
        "status": "Processing",
        "expected_delivery": "3 days from now",
        "courier": "BlueDart (TRK112233)",
        "can_cancel": True
    }
}

MOCK_TICKETS = {
    "TCK501": {
        "user_id": "user_101",
        "order_id": "ORD1002",
        "issue": "Received damaged outer box packaging",
        "status": "In Progress - Assigned to Support Agent",
        "created_at": "Yesterday, 10:30 AM"
    }
}

MOCK_PRODUCTS = [
    {
        "id": "PROD01",
        "name": "UltraBook Laptop 15-inch",
        "category": "Electronics",
        "price": "₹55,000",
        "stock": "In Stock",
        "description": "Intel Core i5, 16GB RAM, 512GB SSD, Anti-Glare Display."
    },
    {
        "id": "PROD02",
        "name": "Wireless Noise-Cancelling Headphones",
        "category": "Audio",
        "price": "₹4,999",
        "stock": "In Stock",
        "description": "Active Noise Cancellation, 30-hour battery life, Bluetooth 5.2."
    },
    {
        "id": "PROD03",
        "name": "Mechanical Gaming Keyboard",
        "category": "Peripherals",
        "price": "₹2,499",
        "stock": "In Stock",
        "description": "RGB Backlit, Tactile Blue Switches, Detachable USB-C."
    },
    {
        "id": "PROD04",
        "name": "Smart Fitness Watch V2",
        "category": "Wearables",
        "price": "₹2,999",
        "stock": "In Stock",
        "description": "Heart Rate & SpO2 Monitor, AMOLED Display, 7-day Battery."
    },
    {
        "id": "PROD05",
        "name": "Ergonomic Office Chair",
        "category": "Furniture",
        "price": "₹7,499",
        "stock": "Out of Stock",
        "description": "Adjustable Lumbar Support, Breathable Mesh Back, 3D Armrests."
    }
]

# ---------------------------------------------------------------------------
# FUNCTION TOOLS (Called by Agent / UI)
# ---------------------------------------------------------------------------

def get_order_details(order_id: str) -> dict:
    """Retrieves live order status, tracking, and delivery details by Order ID."""
    clean_id = order_id.strip().upper()
    if clean_id in MOCK_ORDERS:
        return {"success": True, "order_info": MOCK_ORDERS[clean_id]}
    return {
        "success": False,
        "message": f"Order ID '{order_id}' was not found. Please double-check your order number."
    }


def raise_support_ticket(user_id: str, order_id: str, issue_description: str) -> dict:
    """Creates a formal customer support ticket for damaged goods, returns, or refunds."""
    clean_order_id = order_id.strip().upper()
    ticket_id = f"TCK{len(MOCK_TICKETS) + 501}"
    
    new_ticket = {
        "user_id": user_id,
        "order_id": clean_order_id,
        "issue": issue_description,
        "status": "Open - Pending Support Specialist Review",
        "created_at": "Just now"
    }
    MOCK_TICKETS[ticket_id] = new_ticket
    
    return {
        "success": True,
        "ticket_id": ticket_id,
        "details": new_ticket,
        "message": f"Support ticket {ticket_id} created successfully!"
    }


def get_ticket_status(ticket_id: str) -> dict:
    """Retrieves current status and updates for a specific support ticket ID."""
    clean_id = ticket_id.strip().upper()
    if clean_id in MOCK_TICKETS:
        return {"success": True, "ticket_info": MOCK_TICKETS[clean_id]}
    return {
        "success": False,
        "message": f"Ticket ID '{ticket_id}' not found in our records."
    }


def search_products(query: str) -> dict:
    """Searches the product catalog by name, category, or keyword."""
    q_lower = query.lower().strip()
    results = [
        p for p in MOCK_PRODUCTS 
        if q_lower in p["name"].lower() or q_lower in p["category"].lower() or q_lower in p["description"].lower()
    ]
    if results:
        return {"success": True, "count": len(results), "products": results}
    return {
        "success": False,
        "message": f"No products matching '{query}' were found in our store."
    }