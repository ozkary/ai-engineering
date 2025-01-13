import plotly.express as px
import matplotlib.pyplot as pltLib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime, timedelta
import json

def generate_ar_eyepiece_data(sample_size=50) -> pd.DataFrame:
  """
  Generates sample data for AR eyepiece manufacturing with multiple measurements and quality attributes, 
  including a timestamp for each measurement.

  Args:
    sample_size: Number of samples to generate.

  Returns:
    pandas.DataFrame: DataFrame containing sample data with columns:
      - 'Timestamp': Timestamp for each measurement.
      - 'Sample_ID': Unique sample identifier.
      - 'Focal_Length': Simulated focal length measurement.
      - 'Curvature': Simulated curvature measurement.
      - 'Angle': Simulated angle measurement.
      - 'Clarity': Simulated clarity score (0-10).
      - 'Distortion': Simulated distortion score (0-10).
      - 'Durability': Simulated durability score (0-10). 
  """

  # Define base values and introduce variations
  base_focal_length = 50.0
  base_curvature = 2.5 
  base_angle = 45.0
  base_clarity = 9.0 
  base_distortion = 1.0
  base_durability = 8.0

  focal_length_variation = np.random.normal(loc=0, scale=0.5, size=sample_size)
  curvature_variation = np.random.normal(loc=0, scale=0.05, size=sample_size)
  angle_variation = np.random.normal(loc=0, scale=0.2, size=sample_size)
  clarity_variation = np.random.normal(loc=0, scale=0.5, size=sample_size)
  distortion_variation = np.random.normal(loc=0, scale=0.2, size=sample_size)
  durability_variation = np.random.normal(loc=0, scale=0.3, size=sample_size)

  # Introduce outliers
  outlier_indices_focal_length = np.random.choice(sample_size, size=2, replace=False)
  outlier_indices_curvature = np.random.choice(sample_size, size=1, replace=False)
  outlier_indices_angle = np.random.choice(sample_size, size=3, replace=False)
  outlier_indices_clarity = np.random.choice(sample_size, size=1, replace=False)
  outlier_indices_distortion = np.random.choice(sample_size, size=2, replace=False)
  outlier_indices_durability = np.random.choice(sample_size, size=2, replace=False)

  focal_length_variation[outlier_indices_focal_length] += 3 
  curvature_variation[outlier_indices_curvature] -= 0.15
  angle_variation[outlier_indices_angle] += 0.5
  clarity_variation[outlier_indices_clarity] -= 1.0
  distortion_variation[outlier_indices_distortion] += 0.4
  durability_variation[outlier_indices_durability] -= 1.0

  # Generate timestamps with 1-second intervals
  start_time = datetime.now()
  timestamps = [start_time + timedelta(seconds=i) for i in range(sample_size)]

  # Create the DataFrame
  data = pd.DataFrame({
      'Timestamp': timestamps,
      'Sample_ID': range(1, sample_size + 1),
      'Focal_Length': base_focal_length + focal_length_variation,
      'Curvature': base_curvature + curvature_variation,
      'Angle': base_angle + angle_variation,
      'Clarity': base_clarity + clarity_variation,
      'Distortion': base_distortion + distortion_variation,
      'Durability': base_durability + durability_variation,
  })

  # Define control limits (example values - adjust based on your specific specifications)
  data['Focal_Length_UCL'] = base_focal_length + 3 * 0.5 
  data['Focal_Length_LCL'] = base_focal_length - 3 * 0.5
  data['Curvature_UCL'] = base_curvature + 3 * 0.05
  data['Curvature_LCL'] = base_curvature - 3 * 0.05
  data['Angle_UCL'] = base_angle + 3 * 0.2
  data['Angle_LCL'] = base_angle - 3 * 0.2
  data['Clarity_UCL'] = base_clarity - 1.0  # Assuming a lower limit for Clarity (e.g., 8.0)
  data['Clarity_LCL'] = base_clarity - 2.0  # Assuming a lower limit for Clarity (e.g., 7.0)
  data['Distortion_UCL'] = base_distortion + 0.3  # Assuming an upper limit for Distortion (e.g., 1.3)
  data['Distortion_LCL'] = base_distortion - 0.3  # Assuming a lower limit for Distortion (e.g., 0.7)
  data['Durability_UCL'] = base_durability - 1.0  # Assuming a lower limit for Durability (e.g., 7.0)
  data['Durability_LCL'] = base_durability - 2.0  # Assuming a lower limit for Durability (e.g., 6.0)

  return data

dpi = 100

def get_plot():
    width = 650
    height = 450
    
    figure_w = width / dpi
    figure_h = height / dpi

    pltLib.figure(figsize=(figure_w, figure_h), dpi=dpi)
    return pltLib



def create_control_chart(df: pd.DataFrame, label: str, ts = 'Timestamp'): 
  
    # Calculate control limits (mean +/- 3 times standard deviation for simplicity)
    mean_value = df[label].mean()
    std_dev = df[label].std()
    upper_limit = mean_value + 3 * std_dev
    lower_limit = mean_value - 3 * std_dev
    data = df[label]

    # Create control chart
    plt = get_plot()

    plt.plot(df[ts], data, label=label)
    plt.axhline(y=upper_limit, color='r', linestyle='--', label='Upper Control Limit')
    plt.axhline(y=lower_limit, color='g', linestyle='--', label='Lower Control Limit')

    # Customize the plot
    title = f'Control Chart {label}'
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel(label)
    plt.legend()
    plt.grid(True)

    # Rotate the date labels vertically
    plt.xticks(rotation='vertical')

    # fig.show()
    img_name = f'{label}_control_chart.png'

     # Adjust figure size     
    plt.savefig(img_name, dpi=dpi)    

    chartInfo = {
        'chart type': 'control chart',
        'title': title,
        'data': data.tolist(),        
        'upper limit': upper_limit,
        'lower limit': lower_limit
    }
    return chartInfo

def create_bell_curve_chart(df: pd.DataFrame, label: str, ts = 'Timestamp'):
    
    # Calculate mean and standard deviation
    mean_value = df[label].mean()
    std_dev = df[label].std()

    # Generate x values for the bell curve
    x_values = np.linspace(mean_value - 3 * std_dev, mean_value + 3 * std_dev, 1000)
    # Calculate corresponding y values using the normal distribution
    y_values = norm.pdf(x_values, mean_value, std_dev)

    # Create bell curve chart
    plt = get_plot()
    
    # Plot the bell curve
    plt.plot(x_values, y_values, label='Bell Curve')

    # Annotate mean, std
    plt.scatter([mean_value], [0], color='red', marker='o')
    plt.annotate('Mean', xy=(mean_value, 0), xytext=(mean_value, 0.02), ha='center', va='bottom', color='red')
    
    plt.scatter([mean_value + std_dev], [0], color='green', marker='o')
    plt.annotate('1 Std Dev', xy=(mean_value + std_dev, 0), xytext=(mean_value + std_dev, 0.02), ha='center', va='bottom', color='green')

    plt.scatter([mean_value - std_dev], [0], color='blue', marker='o')
    plt.annotate('-1 Std Dev', xy=(mean_value - std_dev, 0), xytext=(mean_value - std_dev, 0.02), ha='center', va='bottom', color='blue')

    # Customize plot
    title = f'Bell Curve Chart with Mean and Std for {label}'
    plt.title(title)
    plt.xlabel(label)
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)

    # Save the plot as an image
    img_name = f'{label}_bell_curve_chart.png'
     # Adjust figure size     
    plt.savefig(img_name, dpi=dpi)    
    
    chartInfo = {
        'chart type': 'bell curve chart',
        'title': title,        
        'x values': x_values.tolist(),
        'y values': y_values.tolist(),
        'mean': mean_value,
        'std dev': std_dev        
    }
    return chartInfo


def create_histogram_bell_curve_chart(df: pd.DataFrame, label: str):
        
    data = df[label]

    plt = get_plot()

    # Create histogram
    plt.hist(data, bins=20, density=True, color='skyblue', edgecolor='black', alpha=0.7, label='Histogram')

    # Fit a normal distribution to the data
    mu, std = norm.fit(data)

    # Plot the bell curve
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
        
    plt.plot(x, p, 'k', linewidth=2, label=f'Fit results:\n$\mu={mu:.2f}$, $\sigma={std:.2f}$')

    # Customize the plot
    title = f'Histogram with Bell Curve Overlay {label}'
    plt.title(title)
    plt.xlabel(label)
    plt.ylabel('Density')
    plt.legend()

    # Show the plot
    # plt.show()
    img_name = f'{label}_histogram_bell_curve_chart.png'    
    plt.savefig(img_name, dpi=dpi)
    
    chartInfo = {
        'chart type': 'histogram bell curve chart',
        'title': title,
        'data': data.tolist(),
        'mu': mu,
        'std': std,
        'x': x.tolist(),
        'p': p.tolist()        
    }
    return chartInfo

def create_box_plot(df: pd.DataFrame, labels: list):
        
    data = df[labels]    

    plt = get_plot()

    # Create box plot
    plt.boxplot(data.values, tick_labels=labels)

    # Customize the plot
    title = f'Box Plot of AR Eyepiece Measurements {" ".join(labels)}'
    plt.title(title)
    plt.xlabel('Measurements')
    plt.ylabel('Values')
    plt.grid(True) 

    # Show the plot
    # plt.show()
    img_name = f'box_plot.png'    
    plt.savefig(img_name, dpi=dpi)
    
    chartInfo = {
        'chart type': 'box plot',
        'title': title,
        'measurement': labels,
        'data': data.values.tolist(),
        'tick labels': labels.tolist()        
    }
    return chartInfo