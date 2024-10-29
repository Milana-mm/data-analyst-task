import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------
# load cleaned tables
books = pd.read_csv("./temp/cleaned_books.csv")
checkouts = pd.read_csv("./temp/cleaned_checkouts.csv")
customers = pd.read_csv("./temp/cleaned_customers.csv")
libraries = pd.read_csv("./temp/cleaned_libraries.csv")

# join tables
merged_df = checkouts \
    .merge(books, left_on="book_id", right_on="id", how="left", suffixes=('', '_book')) \
    .merge(customers, left_on="patron_id", right_on="id", how="left", suffixes=('', '_patron')) \
    .merge(libraries, left_on="library_id", right_on="id", how="left", suffixes=('', '_library'))

# -- test
# print("Merged DataFrame:")
# print(merged_df.head())

# create a new column: city+postal, remove decimal
merged_df['zipcode'] = merged_df['zipcode'].astype(int)
merged_df['city_postal'] = merged_df['customer_city'] + ' - ' + merged_df['zipcode'].astype(str)
merged_df = merged_df.sort_values(by='customer_city')

# group by - to get counts
count_by_category_late = merged_df.groupby(['customer_city', 'education', 'late']).size().unstack(fill_value=0)
# calculate late ratio for group by combination
count_by_category_late['late_ratio'] = count_by_category_late.get(1, 0) / (
    count_by_category_late.get(1, 0) + count_by_category_late.get(0, 0)
)
# reshape for heatmap: pivot table - x-axis and y-axis
heatmap_data = count_by_category_late['late_ratio'].unstack()


# -----------
# create a subplot
fig = make_subplots(rows=2, cols=2,
                    subplot_titles=("Scatter Plot of Target vs Dim Param 1",
                                    "Scatter Plot of Target vs Dim Param 2"))

# -----------
# Scatter Plot 1

# Assign colors based on 'late' values
# Create a new column: city+postal, remove decimal
# merged_df['zipcode'] = merged_df['zipcode'].astype(int)
# merged_df['city_postal'] = merged_df['customer_city'] + ' - ' + merged_df['zipcode'].astype(str)
# merged_df = merged_df.sort_values(by='customer_city')

merged_df['color'] = merged_df['late'].map({0: '#5ab4ac', 1: 'lightcoral'})

fig.add_trace(go.Scatter(x=merged_df['days_until_returned'],
                         y=merged_df['city_postal'],
                         mode='markers',
                         marker=dict(
                             color=merged_df['color'],
                             # size=10                    # Adjust marker size if needed
                         ),
                         name='Dim Param 1',
                         text=merged_df['late'].astype(str),
                         textfont=dict(
                             color='white'
                         )
                         ), row=1, col=1)

# -----------
# Scatter Plot 2
# Assign colors based on 'late' values
merged_df['color'] = merged_df['late'].map({0: '#5ab4ac', 1: 'lightcoral'})

# Group by city_postal and late status and count IDs
count_by_late = merged_df.groupby(['city_postal', 'late']).size().unstack(fill_value=0)

fig.add_trace(go.Bar(
    x=count_by_late.index,
    y=count_by_late[1],  # Count for late = 1
    name='Late = 1',
    marker=dict(color='lightcoral'),  # Red for late = 1
), row=1, col=2)

fig.add_trace(go.Bar(
    x=count_by_late.index,
    y=count_by_late[0],  # Count for late = 0
    name='Late = 0',
    marker=dict(color='#5ab4ac'),  # Green for late = 0
), row=1, col=2)


# -----------
# Scatter Plot 3
# Heatmap trace
fig.add_trace(go.Heatmap(
    z=heatmap_data.values,           # Late ratio values
    x=heatmap_data.columns,          # Education categories (x-axis)
    y=heatmap_data.index,            # Gender categories (y-axis)
    colorscale='Pinkyl',               # Use a color scale where intensity reflects late ratio
    colorbar=dict(
        title='Late Ratio',
        titlefont=dict(color='white'),
        tickfont=dict(color='white'),
        x=0.2,                 # Adjusted to fit within the plot area horizontally
        y=0.4,                 # Centered vertically within the subplot
        len=0.3,               # Shortened color bar length
        orientation='h',       # Vertical orientation (can change to 'h' if needed)
        xanchor='center',      # Anchor position to help align within plot
        yanchor='middle'
    )
), row=2, col=1)


# -----------
# Scatter Plot 4
# Assign colors based on 'late' values
merged_df['color'] = merged_df['late'].map({0: '#5ab4ac', 1: 'lightcoral'})

fig.add_trace(go.Scatter(x=merged_df['zipcode'],
                         y=merged_df['customer_city'],
                         mode='markers',
                         marker=dict(
                             color=merged_df['color']
                         ),
                         name='Dim Param 2',
                         textfont=dict(
                             color='white'  # Change all text color to white
                         ),
                         ),
              row=2, col=2)

# -----------
# Update layout
fig.update_layout(title_text="Multiple Scatter Plots",
                  # showlegend=True,
                  legend=dict(
                      font=dict(color='white')  # Set legend text color
                  ),
                  # xaxis_title='Category',
                  # yaxis_title='Values',
                  barmode="stack",  # Stack bars on top of each other
                  height=1400, width=1900,
                  paper_bgcolor='#1c9099',  # Outer background color#1f2c56
                  plot_bgcolor='#e5f5f9',  # Plot area background color,
                  # font=dict(color="white"),  # Font color for contrast on blue
                  )

# Configure x and y axis for individual subplots to ensure white color for all text
for axis in ['xaxis', 'yaxis', 'xaxis2', 'yaxis2', 'xaxis3', 'yaxis3', 'xaxis4', 'yaxis4']:
    fig.update_layout({axis: dict(titlefont=dict(color='white'), tickfont=dict(color='white'))})

# Show the figure
fig.show()
