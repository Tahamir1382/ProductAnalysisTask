import pandas as pd
import matplotlib.pyplot as plt
import json
from tqdm import tqdm

# load the data from Excel files
views_df = pd.read_excel('advertisement_views_history_anon.xlsx')
boost_df = pd.read_excel('boost_anon.xlsx')

# convert 'applied_at' to datetime format
boost_df['applied_at'] = pd.to_datetime(boost_df['applied_at'])

# merge the two DataFrames on 'advertisement_id'
merged_df = pd.merge(views_df, boost_df, on='advertisement_id', how='inner')


# function to parse the visits history
def parse_visits_history(visits_history):
    try:
        # Convert the string representation of dictionary to actual dictionary
        if isinstance(visits_history, str):
            visits = json.loads(visits_history)
        elif isinstance(visits_history, dict):
            visits = visits_history
        else:
            visits = {}
    except:
        visits = {}
    return visits


# Function to categorize views into before and after boost
def categorize_views(row):
    applied_at = row['applied_at']
    views = parse_visits_history(row['visits_history'])

    # Convert the keys to datetime and sort them
    converted_views = {}

    # Loop through each item in the original views dictionary
    for date, count in views.items():
        # Convert the date string to a pandas datetime object
        converted_date = pd.to_datetime(date)
        # Add the converted date and its count to the new dictionary
        converted_views[converted_date] = count

    # replace the original views dictionary with the new one
    views = converted_views
    sorted_dates = sorted(views.keys())

    # Check if sorted_dates is empty
    if len(sorted_dates) == 0:
        # If its empty, create a pandas Series with zeros for the required fields and return it
        return pd.Series({
            'views_before': 0,
            'views_after': 0,
            'avg_views_before': 0,
            'avg_views_after': 0
        })

    # Determine the time frame after boost
    start_after = applied_at
    # Finding the last date
    end_after = sorted_dates[-1]
    after_period_days = (end_after - start_after).days

    # Calculate views and average views after boost
    # Use an empty array to store the views after the boost
    after_boost_views = []

    # Iterate over the items in the views dictionary
    for date, count in views.items():
        # Check if the date is within the specified range
        if start_after <= date <= end_after:
            # If the date is within the range, add the count to the after_views list
            after_boost_views.append(count)

    total_after_views = sum(after_boost_views)
    avg_after_views = total_after_views / len(after_boost_views) if after_boost_views else 0

    # Determine the time frame before boost application
    end_before = applied_at - pd.Timedelta(days=1)
    start_before = applied_at - pd.Timedelta(days=after_period_days + 1)

    #calculate views and average views before boost application
    # Use an empty array to store the views after the boost
    before_boost_views = []
    # Iterate over the items in the views dictionary
    for date, count in views.items():
        # Check if the date is within the specified range
        if start_before <= date <= end_before:
            # If the date is within the range, add the count to the beforee_views list
            before_boost_views.append(count)

    total_before_views = sum(before_boost_views)
    avg_before_views = total_before_views / len(before_boost_views) if before_boost_views else 0

    return pd.Series({
        'views_before': total_before_views,
        'views_after': total_after_views,
        'avg_views_before': avg_before_views,
        'avg_views_after': avg_after_views
    })


# apply the function to categorize views
# show progress bar to observe advancements
tqdm.pandas(desc="Categorizing views")
view_counts = merged_df.progress_apply(categorize_views, axis=1)
merged_df = pd.concat([merged_df, view_counts], axis=1)

# Handle edge cases
merged_df['views_before'] = merged_df['views_before'].fillna(0)
merged_df['views_after'] = merged_df['views_after'].fillna(0)
merged_df['avg_views_before'] = merged_df['avg_views_before'].fillna(0)
merged_df['avg_views_after'] = merged_df['avg_views_after'].fillna(0)

# Group data by boost types (plan_id)
grouped = merged_df.groupby('plan_id')

for plan_id, group in grouped:
    # Calculate the average views before and after the boost for each boost type
    average_views_before = group['avg_views_before'].mean()
    average_views_after = group['avg_views_after'].mean()

    # Calculate the change in views
    change_in_views = average_views_after - average_views_before
    percentage_change_in_views = (change_in_views / average_views_before) * 100

    print(f"Boost Type: {plan_id}")
    print(f"  Average views before boost: {average_views_before}")
    print(f"  Average views after boost: {average_views_after}")
    print(f"  Change in views after boost: {change_in_views}")
    print(f"  Percentage change in views after boost: {percentage_change_in_views:.2f}%")

    # Visualization
    plt.figure(figsize=(6, 6))

    # Bar plot for average views before and after boost
    plt.subplot(1, 1, 1)
    plt.bar(['Before Boost', 'After Boost'], [average_views_before, average_views_after], color=['blue', 'green'])
    plt.xlabel('Stage')
    plt.ylabel('Average Views')
    plt.title(f'Average Views Before and After Boost (Type: {plan_id})')

    plt.tight_layout()

    # Save plot as image
    plt.savefig(f'boost_type_{plan_id}.png')
    plt.close()

print("Process completed and plots saved.")
