from datetime import datetime
#1 Record when an analysis occurs
from src.config import LOG

def log_analysis(table, revenue, lowstock):
    x = datetime.now()
    log_time = x.strftime("%I:%M:%S %p  %a %b-%d-%Y")
    message = (
    f"\nanalysis logged: {log_time}"
    #or f"Run time: {x:%c}"
    f"\nRecords analysed: {len(table)}"
#shows numbers of rows top down
    f"\nTotal recorded revenue: {revenue}"
    f"\nNumber of low stock products: {len(lowstock)}\n\n"
    )
#shows number of rows top down of dataframe table low_stock
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, mode="a") as log:
        log.write(message)
