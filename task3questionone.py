import pandas as pd
import json
from tqdm import tqdm
import matplotlib.pyplot as plt

# read the data from Excel files
views_df = pd.read_excel('advertisement_views_history_anon.xlsx')
boost_df = pd.read_excel('boost_anon.xlsx')

# Convert 'applied_at' to datetime format
boost_df['applied_at'] = pd.to_datetime(boost_df['applied_at'])

# Merge the two DataFrames on 'advertisement_id'
merged_df = pd.merge(views_df, boost_df, on='advertisement_id', how='inner')


# Function to parse the visits history
def parse_visits_history(visits_history):
    try:
        if isinstance(visits_history, str):
            visits = json.loads(visits_history)
        elif isinstance(visits_history, dict):
            visits = visits_history
        else:
            visits = {}
    except:
        visits = {}
    return visits


# Function to calculate views before and after boost
def calculate_views_change(row):
    applied_at = row['applied_at']
    views = parse_visits_history(row['visits_history'])

    if not views:
        return pd.Series({
            'views_before': 0,
            'views_after': 0,
            'avg_views_before': 0,
            'avg_views_after': 0
        })

    date_strings = views.keys()

    # Convert the date strings to datetime objects
    date_times = [pd.to_datetime(date) for date in date_strings]

    # Sort the datetime objects
    sorted_dates = sorted(date_times)


    if len(sorted_dates) == 0:
        return pd.Series({
            'views_before': 0,
            'views_after': 0,
            'avg_views_before': 0,
            'avg_views_after': 0
        })

    max_date = sorted_dates[-1]
    period = max_date - applied_at
    before_period_end = applied_at - period

    before_views = []
    after_views = []

    for date, count in views.items():
        date = pd.to_datetime(date)
        if before_period_end <= date < applied_at:
            before_views.append(count)
        if applied_at <= date <= max_date:
            after_views.append(count)

    before_boost = sum(before_views)
    after_boost = sum(after_views)

    num_days_before = (applied_at - before_period_end).days
    num_days_after = (max_date - applied_at).days

    avg_views_before = before_boost / num_days_before if num_days_before > 0 else 0
    avg_views_after = after_boost / num_days_after if num_days_after > 0 else 0

    return pd.Series({
        'views_before': before_boost,
        'views_after': after_boost,
        'avg_views_before': avg_views_before,
        'avg_views_after': avg_views_after
    })


# Apply the function to calculate views change
# show the progress bar
tqdm.pandas(desc="Calculating views change")
views_change = merged_df.progress_apply(calculate_views_change, axis=1)
merged_df = pd.concat([merged_df, views_change], axis=1)

# Handle edge cases
merged_df['views_before'] = merged_df['views_before'].fillna(0)
merged_df['views_after'] = merged_df['views_after'].fillna(0)

# Calculate the change in views
merged_df['change_in_views'] = merged_df['views_after'] - merged_df['views_before']

# Remove statistical outliers wtih IQR method
Q1 = merged_df['change_in_views'].quantile(0.25)
Q3 = merged_df['change_in_views'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
filtered_df = merged_df[(merged_df['change_in_views'] >= lower_bound) & (merged_df['change_in_views'] <= upper_bound)]

# Group by advertisement and calculate the average change in views
boost_effectiveness = filtered_df.groupby('advertisement_id')['change_in_views'].mean().reset_index()

# Plot the results
plt.figure(figsize=(12, 6))
plt.hist(boost_effectiveness['change_in_views'], bins=30, alpha=0.75, color='blue', edgecolor='black')
plt.xlabel('Change in Views')
plt.ylabel('Frequency')
plt.title('Distribution of Change in Views After Boost')
plt.grid(True)
plt.tight_layout()

# Save the plot as an image
plt.savefig('boost_effectiveness_analysis.png')
plt.close()

print("Plot saved as 'boost_effectiveness_analysis.png'.")
