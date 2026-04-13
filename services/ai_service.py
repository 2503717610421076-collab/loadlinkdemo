def group_orders(orders, driver_capacity):
    """
    Mock function for Gemini AI order grouping.
    In production, this would send the orders and driver capacity to Gemini
    to find the optimal combination that minimizes the Detour Delta.
    """
    grouped = []
    current_weight = 0
    for order in orders:
        if current_weight + order.weight <= driver_capacity:
            grouped.append(order)
            current_weight += order.weight
    return grouped
