def format_val(val, unit="", multiplier=1, is_percent=False):
    if val is None or val == "N/A": return "N/A"
    try:
        num = float(val) * multiplier
        if is_percent:
            return f"{num*100:.2f}%"
        
        # Auto-scaling logic if no specific unit is forced (or if unit was passed as a hint but we want auto)
        # However, the requirement is "do an automatic check... choose the unit".
        # So we will ignore the `unit` arg if it was used for scaling previously, or use it as a suffix if it captures something else?
        # The prompt implies replacing the manual 'B'/'M' with automatic detection.
        # So I will prioritize automatic detection based on magnitude.
        
        abs_num = abs(num)
        if abs_num >= 1e12:
            return f"${num/1e12:.2f} Trillion"
        elif abs_num >= 1e9:
            return f"${num/1e9:.2f} Billion"
        elif abs_num >= 1e6:
            return f"${num/1e6:.2f} Million"
        else:
            return f"{num:,.2f}"
            
    except Exception as e:
        print(e)
        return "N/A"

# Test cases
test_values = [
    (2.5e12, "Trillion"),
    (1.1e11, "Billion"), # 110 Billion
    (5.5e9, "Billion"),
    (9.9e8, "Million"), # 990 Million
    (1.2e6, "Million"),
    (500000, "500k"),
    (100, "Small"),
    (0.05, "Small decimal"),
    (None, "None"),
]

print("--- Testing Formatting Logic ---")
for val, desc in test_values:
    formatted = format_val(val)
    print(f"Value: {val} ({desc}) -> {formatted}")

print("\n--- Testing Percentages ---")
print(f"0.156 -> {format_val(0.156, is_percent=True)}")

print("\n--- Testing Explicit Multiplier (if needed) ---")
# If legacy code passed multiplier, we should still respect it before formatting? 
# The original code had `multiplier` param.
print(f"100 * 2 -> {format_val(100, multiplier=2)}")
