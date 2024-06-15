import pandas as pd
import matplotlib.pyplot as plt

# Load the boost data from Excel file
boost_df = pd.read_excel('boost_anon.xlsx')

# Convert 'applied_at' to datetime format
boost_df['applied_at'] = pd.to_datetime(boost_df['applied_at'])

# Extract the hour from the 'applied_at' datetime
boost_df['hour'] = boost_df['applied_at'].dt.hour

# Count the number of boosts sold per hour
hourly_boosts = boost_df['hour'].value_counts().sort_index()

# Plot the number of boosts sold per hour using a scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(hourly_boosts.index, hourly_boosts.values, alpha=0.5)
plt.xticks(range(24))
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Boosts Sold')
plt.title('Number of Boosts Sold by Hour of the Day')
plt.grid(True)
plt.savefig('hourly_boosts_sold_scatter.png')
plt.close()

print("Scatter plot saved as 'hourly_boosts_sold_scatter.png'.")
