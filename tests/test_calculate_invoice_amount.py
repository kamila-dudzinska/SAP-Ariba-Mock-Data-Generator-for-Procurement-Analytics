# -*- coding: utf-8 -*-

import pandas as pd
import os

print(os.getcwd())

# %%
#zmiana working directory
new_dir = r"C:\Users\lila_\Desktop\GitHub\sap_mock_dataset\src"
os.chdir(new_dir)
print(new_dir)

# %%
"""
Created on Sat Aug 15 17:11:51 2026

@author: lila_
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 1 :18:36 2026

@author: @author: Kamila Dudzińska
Project: Tests for SAP-Ariba-Mock-Data-Generator-for-Procurement-Analytics script
Goal:   check, if the function works correctly
"""
import pytest
import random
from unittest.mock import patch
from procurement_mock_functions import calculate_invoice_amount


def test_amount_none_or_negative():
    #czy None is None
    assert calculate_invoice_amount(None, "ordered", "entered") is None
    # czy jesli amount na minusie to bedzie None
    assert calculate_invoice_amount(-20, "ordered", "entered") is None
    #czy jesli amount = 0 to bedzie None
    assert calculate_invoice_amount(0, "ordered", "entered") is None
    


# w funkcji prosimy, aby kwota faktury zgadzala się z kwota PO w 80 procentach
@patch("procurement_mock_functions.random.random", return_value=0.80)              #0.80 > 0.20
def test_amount_match_PO_amount(mock_random):
    result = calculate_invoice_amount(1300.12, "received", "entered")
    assert result == 1300.12



# w funkcji prosimy, aby kwota faktury nie zgadzala się z kwota PO w 20 procentach
@patch("procurement_mock_functions.random.random", return_value = 0.10)            #0.10 < 0.20
def test_amount_not_match_PO_amount(mock_random):
    result= calculate_invoice_amount(100.00, "recieved", "hold")
    assert result != 1000.0

@patch("procurement_mock_functions.random.random", return_value = 0.60)  
# invoice_status == 'hold', ale order_status nie jest 'received' ani 'ordered'
def test_amount_wrong_po_status(mock_random):
    result= calculate_invoice_amount(200.00, "pending approval", "hold")
    assert result == 200.00
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    