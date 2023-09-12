import numpy as np
import plotly.express as px

# Generate random data
np.random.seed(42)
n_points = 100
x = np.random.rand(n_points)
y = np.random.rand(n_points)
z = np.random.rand(n_points)

# Create a 3D scatter plot
fig = px.scatter_3d(x=x, y=y, z=z)

# Customize the appearance and interactivity
fig.update_traces(marker=dict(size=5, color='blue'), selector=dict(mode='markers'))
fig.update_layout(scene=dict(aspectmode="cube"))

# Show the interactive plot
fig.show()
