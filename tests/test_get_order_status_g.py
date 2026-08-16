# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 1 :18:36 2026

@author: @author: Kamila Dudzińska
Project: Tests for SAP-Ariba-Mock-Data-Generator-for-Procurement-Analytics script
Goal:   check, if the function works correctly
"""
# %%

import pytest
import random
from datetime import datetime
from unittest.mock import patch
from procurement_mock_functions import get_order_status


@patch("procurement_mock_functions.random.choices", return_value=["ordered"])
def test_delivery_date_missing(mock_choices):
    today = datetime(2026, 3, 4)

    assert get_order_status(None, today) == "ordered"
    assert get_order_status("", today) == "ordered"
    assert get_order_status("nan", today) == "ordered"
    assert get_order_status("NaN", today) == "ordered"


@patch("procurement_mock_functions.random.choices", return_value=["received"])
def test_delivery_date_recent(mock_choices):
    today = datetime(2026, 3, 20)
    delivery_date = datetime(2026, 3, 15)  # 5 dni temu

    assert get_order_status(delivery_date, today) == "received"
    
    
    
@patch("procurement_mock_functions.random.choices", return_value=["invoiced"])
def test_delivery_date_old(mock_choices):
   today = datetime(2026, 4, 26)   
   delivery_date = datetime(2026, 4, 14)
   
   assert get_order_status(delivery_date, today) == "invoiced"






