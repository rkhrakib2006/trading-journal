import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

def parse_mt5_file(file_bytes, filename):
    """
    Parses HTML or CSV exported from MT5 Terminal.
    Returns a list of dictionaries representing trades.
    """
    trades = []
    
    if filename.endswith('.html') or filename.endswith('.html'):
        # Parse HTML
        soup = BeautifulSoup(file_bytes, 'html.parser')
        tables = soup.find_all('table')
        if not tables:
            return []
        
        # MT5 usually dumps history in the first table
        df = pd.read_html(str(tables[0]))[0]
        
    elif filename.endswith('.csv'):
        # Parse CSV
        # MT5 CSV format is usually semicolon separated ";"
        try:
            df = pd.read_csv(file_bytes, sep=';')
        except:
            df = pd.read_csv(file_bytes)
    
    # Clean up column names (MT5 often adds spaces)
    df.columns = df.columns.str.strip()
    
    # Standardize Column Mapping (MT5 headers vary by language, 
    # this is a generic mapping for "English" MT5 Export)
    # You may need to adjust keys based on your specific MT5 Language settings
    
    mapping = {
        'Time': 'entry_time',
        'Time.1': 'exit_time', # MT5 often splits time into entry/exit
        'Symbol': 'symbol',
        'Type': 'trade_type',
        'Volume': 'lot_size',
        'Profit': 'profit_loss',
        'Commission': 'commission',
        'Ticket': 'ticket_number'
    }

    # Filter valid columns only
    available_cols = [c for c in mapping.keys() if c in df.columns]
    if not available_cols:
        return []

    # Process rows
    for index, row in df.iterrows():
        try:
            # Simple parser logic - converts row to dict
            t_data = {}
            for col in available_cols:
                val = row[col]
                
                # Type conversions
                if 'time' in col.lower():
                    # Handle various date formats
                    try:
                        val = pd.to_datetime(val)
                    except: continue
                elif col == 'Volume':
                    val = float(val.replace(',', '.'))
                elif col == 'Profit':
                    val = float(str(val).replace(',', '.'))
                
                t_data[mapping[col]] = val
            
            if 'entry_time' in t_data and 'exit_time' in t_data:
                trades.append(t_data)
        except Exception as e:
            print(f"Error parsing row {index}: {e}")
            continue
            
    return trades
