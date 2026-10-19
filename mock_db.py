# mock_db.py - Simulated Backend Database for HelloQ

MOCK_USERS = {
    "user_101": {
        "name": "Alex Taylor",
        "email": "alex.taylor@example.com",
        "tier": "Gold",
        "subscription_active": True,
        "super_likes_remaining": 0,  # Bugged/Unsynced state for demo
        "discreet_mode": False
    },
    "user_102": {
        "name": "Jordan Smith",
        "email": "jordan.s@example.com",
        "tier": "Free",
        "subscription_active": False,
        "super_likes_remaining": 0,
        "discreet_mode": True
    }
}

def get_user_account(user_id: str) -> dict:
    """Fetch user profile and subscription details from the database."""
    user = MOCK_USERS.get(user_id)
    if not user:
        return {"error": f"User ID {user_id} not found."}
    return user

def trigger_restore_purchases(user_id: str) -> dict:
    """Simulates restoring purchases and syncing daily perks (e.g., refreshing Super Likes)."""
    user = MOCK_USERS.get(user_id)
    if not user:
        return {"error": f"User ID {user_id} not found."}
    
    if user["subscription_active"]:
        user["super_likes_remaining"] = 5
        return {
            "status": "success",
            "message": f"Successfully restored purchases for {user['name']}. Tier: {user['tier']}. Daily Super Likes reset to 5."
        }
    else:
        return {
            "status": "failed",
            "message": f"No active subscription found for user {user['name']}. Please upgrade to Gold or Platinum."
        }