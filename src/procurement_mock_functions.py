# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 18:02:37 2026

@author: Kamila Dudzińska

Supporting module with functions

Dataset: Procurement Department 
Contain: Data from SAP Ariba - Material POs
Characteristics: 2500 records,
                 outliers 0,04%, 
                 null values < 0,02%
Goal:   script created for procurement specialist and expert, who want to train 
        data analysis skills in Python/Pandas. The dataset reflects the SAP
        Ariba architecture. 
        
Module with functions
        
"""

# IMPORT MODULES
import random
from datetime import datetime, timedelta
import procurement_mock_functions


# FUNCTIONS


def weighted_choice(choices):
     """
    Selects a random value from weighted ranges.

    This function calculates the order amount by taking business-defined
    weights into account. It ensures that most orders fall into low-budget
    categories (tactical sourcing), reflecting realistic procurement behavior.

    Args:
        choices (list[tuple[int, int, float]]): 
            A list of tuples in the form (low, high, weight), where:
              - low: lower bound of the range
              - high: upper bound of the range
              - weight: probability weight for that range

    Returns:
        int: A randomly selected integer within the chosen range.

    Example:
        >>> weighted_choice([(100, 500, 0.6), (501, 2000, 0.3), (2001, 10000, 0.1)])
        347
    """
    
    total = sum(w for _, _, w in choices)
    r = random.uniform(0, total)                #floating-point number from zero to total 0.87
    upto = 0                                    #upto = counter
    #  dolny zakres, górny zakres, waga
    for low, high, weight in choices:           
        if upto + weight >= r:                  #check the range for weight
            if low == high:                     
                return low                      
            return random.randint(low, high)    #return low and high
        upto += weight
    return choices[-1][1]


# generate PO number
def generate_po_number(existing:int) -> int:
    '''
    Generates an order number in the range 6000000000 - 6000999999, 
    according to the SAP ARIBA standard.

    This function genertes a random PO number from the mentioned range.

    Args:
        existing (list[int]): 
            A list of already generated PO numbers to avoid duplicates.

    Returns:
        int: A unique PO number within the specified range.

    Example:
        >>> existing = [6000000001, 6000000002]
        >>> generate_po_number(existing)
        6000000347
    '''
  
    while True:
        num = random.randint(6000000000, 6000999999)
        if num not in existing:
            return num


# generate delivery date
def generate_delivery_date(creation_date:datetime, today:datetime) -> datetime:
    '''
    Randomly generates a delivery date based on the create date and PT 
    within a range of up to 60 days.

    This function randomly selects a delivery date within a range of up to 60 days
    from the creation date. It ensures that the generated date is realistic for
    procurement processes and avoids invalid edge cases.

    Args:
        creation_date (datetime): 
            The date when the purchase order was created.
        today (datetime): 
            The current date used as a reference point for validation.

    Returns:
        datetime | None: 
            A randomly generated delivery date within the allowed range.
            Returns None if the generated date is invalid.

    Example:
        >>> generate_delivery_date(datetime(2026, 3, 1), datetime(2026, 3, 25))
        datetime.datetime(2026, 3, 19, 0, 0)
    '''
    random_days = random.randint(1, 60)
    delivery_date = creation_date + timedelta(days=random_days)
    delivery_date.strftime("%d-%m-%Y")
    if delivery_date == delivery_date + timedelta(days=42):
        return None
    return delivery_date
    

# generate delivery date
def generate_invoice_date(delivery_date:datetime, today:datetime) -> tuple[str | None, int]:
    '''
    Randomly generates an invoice date based on the delivery date and PT 
    within a range of up to 90 days.

    Args:
        delivery_date (datetime | str): 
            The delivery date as a datetime object or string in format "%d.%m.%Y".
        today (datetime): 
            The current date used for validation or reference.

    Returns:
        tuple[str | None, int]: 
            A tuple containing:
              - The invoice date formatted as "%d.%m.%Y" (or None if invalid).
              - The payment term in days (integer between 10 and 90).

    Example:
        >>> generate_invoice_date(datetime(2026, 3, 25), datetime(2026, 4, 1))
        ('23.05.2026', 59)
    '''
  
    if delivery_date is None: 
        return None, 0
    
    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, "%d.%m.%Y")
              
    payment_terms = random.randint(10, 90)
    invoice_date = delivery_date + timedelta(days=payment_terms)
    invoice_date: str  = invoice_date.strftime("%d.%m.%Y")
    
    return invoice_date, payment_terms


def calculate_invoice_amount(amount:float, order_status:str, invoice_status:str) -> float:
    '''
    Return the invoice amount. In 80% it is the same as PO amount (2 way match)
    and in 20% there is a small variation, which needs further clarification.

    Args:
        delivery_date (datetime | str): 
            The delivery date as a datetime object or string in format "%d.%m.%Y".
        today (datetime): 
            The current date used for validation or reference.

    Returns:
        tuple[str | None, int]: 
            A tuple containing:
              - The invoice date formatted as "%d.%m.%Y" (or None if invalid).
              - The payment term in days (integer between 10 and 90).

    Example:
        >>> generate_invoice_date(datetime(2026, 3, 25), datetime(2026, 4, 1))
        ('23.05.2026', 59)
        
    '''
  
    if amount is None or amount <=0:
        return None
    
    #80% zgodne z amount
    if invoice_status != 'hold' and random.random() > 0.20:
        return round(amount, 2)
    elif invoice_status == 'hold' and order_status in ['received', 'ordered']:
        variation = random.uniform(0.80, 1.20)
        return round(amount * variation, 2)
    else:
        return amount
    

def get_order_status(delivery_date: datetime | str | None, today: datetime) -> str:
    """
    Returns order status based on delivery date logic.

    This function evaluates the delivery date and returns a realistic order status
    according to procurement workflow rules. It handles missing, string, and datetime
    inputs, and applies weighted probabilities to simulate real-world status distribution.

    Logic overview:
        1. If delivery date is missing or invalid, returns either "ordered" or "confirmed".
        2. If delivery date is within the last 10 days, returns either "received" or "invoiced".
        3. Otherwise, defaults to "confirmed" or "ordered" based on weighted random choice.

    Args:
        delivery_date (datetime | str | None): 
            The delivery date of the purchase order. Can be a datetime object, 
            a string in format "%d-%m-%Y", or None.
        today (datetime): 
            The current date used as a reference point for comparison.

    Returns:
        str: 
            The simulated order status ("ordered", "confirmed", "received", or "invoiced").

    Example:
        >>> get_order_status(datetime(2026, 8, 10), datetime(2026, 8, 14))
        'received'
        >>> get_order_status(None, datetime(2026, 8, 14))
        'ordered'
    """

    # --- 1. Pusta data dostawy -> tylko "ordered" lub "confirmed"
    if delivery_date is None or delivery_date == "" or str(delivery_date).lower() == "nan":
        return random.choices(
            population=["ordered", "confirmed"],
            weights=[91, 9],
            k=1
        )[0]

    # --- 2. Jeśli mamy string, zamieniamy na datetime
    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, "%d-%m-%Y")

    # --- 3. Granica 10 dni temu
    ten_days_ago = today - timedelta(days=10)

    # --- 4. Delivery Date w ostatnich 10 dniach (do dziś)
    if ten_days_ago <= delivery_date <= today:
        return random.choices(
            population=["received", "invoiced"],
            weights=[51, 49],
            k=1
        )[0]

    # --- 5. Delivery Date starsza niż 10 dni
    if delivery_date < ten_days_ago:
        return random.choices(
            population=["received", "confirmed", "invoiced"],
            weights=[70, 8, 21],
            k=1
        )[0]

    # --- 6. Delivery Date w przyszłości (awaryjnie)
    return "ordered"


def generate_invoice_number(existing_inv:str) ->str:
    '''
    Generates unique invoice number in the specified format.

    Args:
        existing_inv (list[str]): 
            A list of already generated invoice numbers to avoid duplicates.

    Returns:
        str: 
            A unique invoice number formatted as `FV/YYYY/MM/NNNN`.

    Example:
        >>> existing_inv = ["FV/2026/03/0914", "FV/2026/07/0452"]
        >>> generate_invoice_number(existing_inv)
        'FV/2026/12/0831'
    '''

    while True:
        year = '2026'
        month = f"{random.randint(1,12):02d}"
        random_num = f'{random.randint(1,999):04d}'
        random_inv = f'FV/{year}/{month}/{random_num}' 
        if random_inv not in existing_inv:
            return random_inv
    
    
                























