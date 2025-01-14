from collections import defaultdict

def analyze_customer_data(form_data):
    results = []
    previous_entries = defaultdict(list)  # To track previous entries for each Customer-Product pair

    for data in form_data:
        customer_name = data['Customer Name']
        products = data['Products']
        
        actions = []

        for product in products:
            product_name = product['Product Name']
            quantity = product['Quantity']
            price = product['Price']

            # Track previous entries for the customer-product pair
            key = (customer_name, product_name)
            if key in previous_entries:
                previous_quantity, previous_date = previous_entries[key]

                # Calculate the difference in quantity
                quantity_diff = previous_quantity - quantity
                if quantity_diff > 0:
                    actions.append(f"{product_name}: Reorder")
                elif quantity_diff < 0:
                    actions.append(f"{product_name}: Needs Promo")

                # Update the previous entry for this customer-product pair with the current entry
                previous_entries[key] = (quantity, data['Date'])
            else:
                # If it's the first entry for this customer-product pair, store it
                previous_entries[key] = (quantity, data['Date'])

        # If there are actions for this customer, add them to the results
        if actions:
            results.append({
                "Customer Name": customer_name,
                "Actions": "; ".join(actions)
            })
    
    return results if results else None
