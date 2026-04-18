

import pandas as pd
import numpy as np
from datetime import timedelta

# Try importing Prophet, gracefully fallback if not installed/available
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("WARNING: 'prophet' library is not installed. Falling back to Moving Average forecasting.")


def generate_forecast(df, material_id, forecast_days=30):
    """
    Generate a time-series forecast for a specific material.
    Uses Prophet if available and if historical data >= 10 days.
    Otherwise, uses a simple moving average fallback.
    
    Args:
        df: Pandas DataFrame containing historical consumption
        material_id: String ID of the material to isolate
        forecast_days: Number of days to predict into the future
        
    Returns:
        DataFrame with future dates and forecasted consumption (yhat, yhat_lower, yhat_upper)
    """
    
    # Isolate data for the specific material
    mat_df = df[df['Material_ID'] == material_id].copy()
    
    # Preprocess: group by date to ensure daily frequency
    mat_df['Posting_Date'] = pd.to_datetime(mat_df['Posting_Date'])
    mat_df = mat_df.groupby('Posting_Date')['Quantity_Consumed'].sum().reset_index()
    
    # Set index and resample to fill missing days with 0
    mat_df = mat_df.set_index('Posting_Date').resample('D').sum().fillna(0).reset_index()
    
    # Format for Prophet
    prophet_df = mat_df.rename(columns={'Posting_Date': 'ds', 'Quantity_Consumed': 'y'})
    
    num_historical_days = len(prophet_df)
    last_date = prophet_df['ds'].max()
    
    # Create future dataframe structure
    future_dates = [last_date + timedelta(days=i) for i in range(1, forecast_days + 1)]
    forecast_df = pd.DataFrame({'ds': future_dates})
    
    if PROPHET_AVAILABLE and num_historical_days >= 10:
        # User requested Prophet engine
        model = Prophet(daily_seasonality=False, yearly_seasonality=True, weekly_seasonality=True)
        model.fit(prophet_df)
        
        # We only want to forecast the future
        future = model.make_future_dataframe(periods=forecast_days, freq='D')
        
        forecast = model.predict(future)
        
        # Isolate only the actual future predictions (we don't need historical fit here)
        future_forecast = forecast[forecast['ds'] > last_date].copy()
        
        # Constrain predictions to be non-negative (can't have negative consumption)
        future_forecast['yhat'] = future_forecast['yhat'].clip(lower=0)
        future_forecast['yhat_lower'] = future_forecast['yhat_lower'].clip(lower=0)
        future_forecast['yhat_upper'] = future_forecast['yhat_upper'].clip(lower=0)
        
        return future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        
    else:
        # Fallback Engine (Moving Average)
        print(f"Info: Using Moving Average fallback for {material_id}. (Prophet={PROPHET_AVAILABLE}, Days={num_historical_days})")
        
        # Calculate 30-day moving average of historical data
        avg_consumption = prophet_df['y'].rolling(window=min(30, max(1, num_historical_days)), min_periods=1).mean().iloc[-1]
        
        # Create dummy confidence intervals
        variance = prophet_df['y'].std() if num_historical_days > 1 else 0
        
        forecast_df['yhat'] = max(0, avg_consumption)
        forecast_df['yhat_lower'] = max(0, avg_consumption - variance)
        forecast_df['yhat_upper'] = avg_consumption + variance
        
        return forecast_df
