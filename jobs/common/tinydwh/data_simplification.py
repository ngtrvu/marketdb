from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd


# RDP Algorithm from previous example
def rdp_simplify(points, epsilon):
    if len(points) <= 2:
        return points
    
    line_start, line_end = points[0], points[-1]
    t_start, c_start = line_start
    t_end, c_end = line_end
    
    if t_start == t_end:
        return [line_start]
    
    max_dist = 0
    max_idx = 0
    
    for i in range(1, len(points) - 1):
        t, c = points[i]
        t_norm = (t - t_start) / (t_end - t_start)
        c_proj = c_start + t_norm * (c_end - c_start)
        dist = abs(c - c_proj)
        
        if dist > max_dist:
            max_dist = dist
            max_idx = i
    
    if max_dist > epsilon:
        first_part = rdp_simplify(points[:max_idx + 1], epsilon)
        second_part = rdp_simplify(points[max_idx:], epsilon)
        return first_part[:-1] + second_part
    else:
        return [line_start, line_end]

def simplify_chart_data(chart, epsilon=0.01):
    """
    Simplifies the chart data using the RDP algorithm.
    epsilon: The tolerance for simplification 0.01 is ok for stock prices
    """
    # Convert chart data to (t, c) pairs
    points = [(i, item["c"]) for i, item in enumerate(chart)]
    
    # Normalize the data
    t_vals = np.array([p[0] for p in points])
    c_vals = np.array([p[1] for p in points])
    
    t_range = t_vals.max() - t_vals.min() if t_vals.max() != t_vals.min() else 1
    c_range = c_vals.max() - c_vals.min() if c_vals.max() != c_vals.min() else 1
    
    normalized_points = [
        ((t - t_vals.min()) / t_range, (c - c_vals.min()) / c_range) 
        for t, c in points
    ]
    
    # Apply RDP algorithm
    simplified_points = rdp_simplify(normalized_points, epsilon)
    
    # Convert back to original scale
    original_scale_points = [
        (int(t * t_range + t_vals.min()), c * c_range + c_vals.min())
        for t, c in simplified_points
    ]
    
    # Reconstruct chart format
    simplified_chart = []
    for idx, c in original_scale_points:
        if 0 <= idx < len(chart):
            simplified_chart.append({
                "c": c,
                "t": chart[idx]["t"],
                "original_idx": idx
            })
    
    return simplified_chart

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    """Here's a simple example of how to use the above functions to generate synthetic stock data,
    apply the RDP algorithm for data simplification, and visualize the results."""
    # 1. Generate synthetic stock data
    num_trading_days = 5 * 250  # 5 years with approx. 250 trading days per year
    start_date = datetime(2020, 1, 1)

    # Function to generate trading dates (excluding weekends)
    def generate_trading_dates(start_date, num_days):
        trading_dates = []
        current_date = start_date
        
        while len(trading_dates) < num_days:
            # Skip weekends (5 = Saturday, 6 = Sunday)
            if current_date.weekday() < 5:
                trading_dates.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_dates

    trading_dates = generate_trading_dates(start_date, num_trading_days)

    # Generate prices between 10,000 and 150,000
    # Using a random walk with trends and volatility changes
    base_price = 50000
    prices = [base_price]

    # Add some realistic market behaviors
    for i in range(1, num_trading_days):
        # Random factors to create trends and volatility
        trend_factor = np.sin(i/200) * 2000  # Long-term trends
        volatility = 1000 + 500 * np.cos(i/100)  # Changing volatility
        
        # Random daily movement
        daily_change = np.random.normal(trend_factor, volatility)
        
        # Add some crashes and rallies
        if random.random() < 0.002:  # 0.2% chance of a market event
            event_magnitude = random.choice([-0.15, -0.10, 0.10, 0.15])  # Crash or rally
            daily_change += prices[-1] * event_magnitude
        
        # Calculate new price
        new_price = max(10000, min(150000, prices[-1] + daily_change))
        prices.append(new_price)

    # Create the chart data in the specified format
    chart = [
        {
            "c": price, 
            "t": d.timestamp()
        } for price, d in zip(prices, trading_dates)
    ]

    # 2. Apply the data reduction with different epsilon values
    epsilon_values = [0.002, 0.01, 0.05]
    simplified_charts = {}

    for epsilon in epsilon_values:
        simplified_charts[epsilon] = simplify_chart_data(chart, epsilon)

    # 3. Visualize the results
    plt.figure(figsize=(14, 10))

    # Original data
    plt.subplot(2, 2, 1)
    plt.plot([datetime.fromtimestamp(item["t"]) for item in chart], 
            [item["c"] for item in chart], 
            label=f'Original ({len(chart)} points)')
    plt.title('Original Time Series')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # Plot reduced data with different epsilon values
    positions = [(2, 2, 2), (2, 2, 3), (2, 2, 4)]

    for i, (epsilon, position) in enumerate(zip(epsilon_values, positions)):
        simplified = simplified_charts[epsilon]
        
        plt.subplot(*position)
        
        # Plot original as light line
        plt.plot([datetime.fromtimestamp(item["t"]) for item in chart], 
                [item["c"] for item in chart], 
                color='lightgray', linewidth=1)
        
        # Plot simplified as darker points and lines
        plt.plot([datetime.fromtimestamp(item["t"]) for item in simplified], 
                [item["c"] for item in simplified], 
                'ro-', markersize=3, linewidth=1,
                label=f'Reduced (ε={epsilon}, {len(simplified)} points)')
        
        reduction_pct = (1 - len(simplified) / len(chart)) * 100
        plt.title(f'Epsilon = {epsilon} (Reduction: {reduction_pct:.1f}%)')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)

    plt.tight_layout()
    plt.savefig('time_series_reduction.png')

    # Display stats
    print("Data Reduction Statistics:")
    print(f"Original data points: {len(chart)}")
    for epsilon in epsilon_values:
        simplified = simplified_charts[epsilon]
        reduction_pct = (1 - len(simplified) / len(chart)) * 100
        print(f"Epsilon = {epsilon}: {len(simplified)} points ({reduction_pct:.1f}% reduction)")

    # Generate a table of results for demonstration
    results_table = pd.DataFrame({
        'Epsilon': epsilon_values,
        'Points Remaining': [len(simplified_charts[e]) for e in epsilon_values],
        'Original Points': [len(chart)] * len(epsilon_values),
        'Reduction %': [(1 - len(simplified_charts[e]) / len(chart)) * 100 for e in epsilon_values]
    })

    print("\nResults Table:")
    print(results_table)