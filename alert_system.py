import pandas as pd
from datetime import datetime, date

def calculate_alerts(forecast_df, current_stock, safety_stock, lead_time_days):
    """
    Calculates the predicted depletion date and reorder trigger date based on forecasted consumption.
    
    Args:
        forecast_df: DataFrame output from engine.generate_forecast containing ['ds', 'yhat']
        current_stock: The current unrestricted physical inventory (float/int)
        safety_stock: The minimum threshold requirement (float/int)
        lead_time_days: Number of days required for vendor delivery (int)
        
    Returns:
        dict: Alert metrics and status
    """
    # Ensure current stock logic starts from today
    simulated_stock = current_stock
    depletion_date = None
    
    # Sort forecast just to be safe
    forecast_df = forecast_df.sort_values('ds')
    
    for i, row in forecast_df.iterrows():
        consumption = row['yhat']
        simulated_stock -= consumption
        
        if simulated_stock <= safety_stock:
            depletion_date = row['ds'].date()
            break
            
    # If it never drops below safety stock in the forecast window (e.g. 30 days)
    if depletion_date is None:
        return {
            'predicted_depletion_date': '30+ Days',
            'reorder_trigger_date': 'N/A',
            'status': 'STOCK OK',
            'days_until_safety_stock': '> 30'
        }
        
    # Calculate reorder trigger date
    reorder_date = depletion_date - pd.Timedelta(days=lead_time_days)
    today = date.today()
    
    days_until_safety = (depletion_date - today).days
    
    # Determine the actionable status
    if reorder_date <= today:
        status = 'CRITICAL: REORDER NOW'
    elif (reorder_date - today).days <= 3:
        status = 'WARNING: PLAN REORDER'
    else:
        status = 'STOCK OK'
        
    return {
        'predicted_depletion_date': depletion_date,
        'reorder_trigger_date': reorder_date,
        'status': status,
        'days_until_safety_stock': max(0, days_until_safety)
    }
