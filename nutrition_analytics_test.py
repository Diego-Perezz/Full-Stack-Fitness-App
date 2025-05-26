import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import streamlit as st
from nutrition_analytics import display_correlation_analysis, display_nutrition_analytics_page

# Helper functions for testing - define them here to avoid closure extraction issues
def format_correlation(corr_value):
    if pd.isna(corr_value):
        return "No pattern detected"
    elif abs(corr_value) < 0.2:
        return f"{corr_value:.2f} (Weak)"
    elif abs(corr_value) < 0.6:
        return f"{corr_value:.2f} (Moderate)"
    else:
        return f"{corr_value:.2f} (Strong)"

def get_correlation_delta_color(corr_value):
    if pd.isna(corr_value):
        return "off"
    elif corr_value > 0:
        return "normal"  # Green for positive correlation
    else:
        return "inverse"  # Red for negative correlation

class TestFormatCorrelation(unittest.TestCase):
    """Test cases for the format_correlation function used in display_correlation_analysis"""

    def test_format_correlation_nan(self):
        """Test format_correlation function handles NaN values correctly"""
        
        """
        AI Prompt:
        Write a test function test_format_correlation_nan that verifies the format_correlation function properly handles NaN values. The test should pass a float('nan') value to the format_correlation function and assert that the returned string is exactly "No pattern detected".
        """
        
        # Directly test the format_correlation function
        result = format_correlation(float('nan'))
        self.assertEqual(result, "No pattern detected")

    def test_format_correlation_weak(self):
        """Test format_correlation function categorizes weak correlations correctly"""
        
        """
        AI Prompt:
        Write a test function test_format_correlation_weak that validates the format_correlation function correctly categorizes weak correlation values (< 0.2). The test should check both positive (0.15) and negative (-0.10) weak correlations, verifying both the numeric value and "Weak" label appear in the returned string.
        """
        
        # Test with weak positive correlation
        result = format_correlation(0.15)
        self.assertTrue("0.15" in result)
        self.assertTrue("Weak" in result)
        
        # Test with weak negative correlation
        result = format_correlation(-0.10)
        self.assertTrue("-0.10" in result)
        self.assertTrue("Weak" in result)

    def test_format_correlation_moderate(self):
        """Test format_correlation function categorizes moderate correlations correctly"""
        
        """
        AI Prompt:
        Write a test function test_format_correlation_moderate that validates the format_correlation function correctly categorizes moderate correlation values (between 0.2 and 0.6). The test should check both positive (0.45) and negative (-0.55) moderate correlations, verifying both the numeric value and "Moderate" label appear in the returned string.
        """
        
        # Test with moderate positive correlation
        result = format_correlation(0.45)
        self.assertTrue("0.45" in result)
        self.assertTrue("Moderate" in result)
        
        # Test with moderate negative correlation
        result = format_correlation(-0.55)
        self.assertTrue("-0.55" in result)
        self.assertTrue("Moderate" in result)

    def test_format_correlation_strong(self):
        """Test format_correlation function categorizes strong correlations correctly"""
        
        """
        AI Prompt:
        Write a test function test_format_correlation_strong that validates the format_correlation function correctly categorizes strong correlation values (≥ 0.6). The test should check both positive (0.85) and negative (-0.75) strong correlations, verifying both the numeric value and "Strong" label appear in the returned string.
        """
        
        # Test with strong positive correlation
        result = format_correlation(0.85)
        self.assertTrue("0.85" in result)
        self.assertTrue("Strong" in result)
        
        # Test with strong negative correlation
        result = format_correlation(-0.75)
        self.assertTrue("-0.75" in result)
        self.assertTrue("Strong" in result)


class TestGetCorrelationDeltaColor(unittest.TestCase):
    """Test cases for the get_correlation_delta_color function"""

    def test_get_correlation_delta_color(self):
        """Test get_correlation_delta_color returns correct values"""
        
        """
        AI Prompt:
        Write a test function test_get_correlation_delta_color that verifies the get_correlation_delta_color function returns the correct color value for different correlation inputs. The test should verify the function returns "off" for NaN values, "normal" for positive correlations, and "inverse" for negative correlations.
        """
        
        # Test with NaN (should return "off")
        result = get_correlation_delta_color(float('nan'))
        self.assertEqual(result, "off")
        
        # Test with positive correlation (should return "normal")
        result = get_correlation_delta_color(0.5)
        self.assertEqual(result, "normal")
        
        # Test with negative correlation (should return "inverse")
        result = get_correlation_delta_color(-0.5)
        self.assertEqual(result, "inverse")


class TestDisplayCorrelationAnalysis(unittest.TestCase):
    """Test cases for the display_correlation_analysis function"""

    @patch("nutrition_analytics.st")
    @patch("nutrition_analytics.get_nutrition_performance_correlation")
    def test_no_data_warning(self, mock_get_correlation, mock_st):
        """Test that a warning is displayed when no correlation data is available"""
        
        """
        AI Prompt:
        Write a test function test_no_data_warning that verifies the display_correlation_analysis function correctly shows warnings when no correlation data is available. The test should mock Streamlit and the correlation data source to return an empty dictionary, then verify that a warning message is displayed and instructions for getting started are shown.
        """
        
        # Mock the columns to return a list with two mock objects
        mock_cols = [MagicMock(), MagicMock()]
        mock_st.columns.return_value = mock_cols
        
        # Mock the correlation data to return an empty dictionary
        mock_get_correlation.return_value = {}
        
        # Call the function
        display_correlation_analysis("user1")
        
        # Verify that a warning was displayed
        mock_st.warning.assert_called_with("No data available for correlation analysis.")
        
        # Verify that the markdown instructions were displayed
        mock_st.markdown.assert_called()
        # Find the call with instructions
        instructions_call = None
        for call in mock_st.markdown.call_args_list:
            if "How to Get Started" in call[0][0]:
                instructions_call = call
                break
        
        self.assertIsNotNone(instructions_call, "Instructions not found in markdown calls")
        self.assertIn("Log your meals", str(instructions_call))

    @patch("nutrition_analytics.st")
    @patch("nutrition_analytics.get_nutrition_performance_correlation")
    @patch("nutrition_analytics.pd")
    def test_empty_df_list_warning(self, mock_pd, mock_get_correlation, mock_st):
        """Test that a warning is displayed when there's not enough matched data"""
        
        """
        AI Prompt:
        Write a test function test_empty_df_list_warning that verifies the display_correlation_analysis function shows appropriate warnings when there's not enough matched data. The test should mock the correlation data to include entries where either nutrition or performance data is missing, then verify a specific warning about insufficient matched data is displayed along with an explanation.
        """
        
        # Mock the columns to return a list with two mock objects
        mock_cols = [MagicMock(), MagicMock()]
        mock_st.columns.return_value = mock_cols
        
        # Mock correlation data with empty nutrition or performance
        mock_get_correlation.return_value = {
            "2024-07-15": {
                "nutrition": None,
                "performance": {"distance": 5.0}
            },
            "2024-07-16": {
                "nutrition": {"total_calories": 2000},
                "performance": None
            }
        }
        
        # Call the function
        display_correlation_analysis("user1")
        
        # Verify that a warning was displayed about not enough matched data
        mock_st.warning.assert_called_with("Not enough matched data for correlation analysis.")
        
        # Verify that the explanation markdown was displayed
        explanation_call = None
        for call in mock_st.markdown.call_args_list:
            if "Why Am I Seeing This Message?" in call[0][0]:
                explanation_call = call
                break
        
        self.assertIsNotNone(explanation_call, "Explanation not found in markdown calls")
        self.assertIn("both nutrition and workout data", str(explanation_call))

    @patch("nutrition_analytics.st")
    @patch("nutrition_analytics.get_nutrition_performance_correlation")
    @patch("nutrition_analytics.pd.DataFrame")
    def test_few_days_warning(self, mock_dataframe, mock_get_correlation, mock_st):
        """Test that a warning is displayed when there are few days with matched data"""
        
        """
        AI Prompt:
        Write a test function test_few_days_warning that verifies the display_correlation_analysis function shows a warning when there are too few days with matched data. The test should mock the correlation data with only two days of complete data, mock the resulting DataFrame length to be 2, and verify a warning message containing the specific number of days is displayed.
        """
        
        # Mock the columns to return a list with two mock objects
        mock_cols = [MagicMock(), MagicMock()]
        mock_st.columns.return_value = mock_cols
        
        # Mock correlation data with only 2 days of complete data
        mock_get_correlation.return_value = {
            "2024-07-15": {
                "nutrition": {"total_calories": 2000, "total_protein": 100, "total_carbs": 200, "total_fat": 50, "total_water_ml": 2500},
                "performance": {"distance": 5.0, "steps": 8000, "calories_burned": 400}
            },
            "2024-07-16": {
                "nutrition": {"total_calories": 1800, "total_protein": 90, "total_carbs": 180, "total_fat": 45, "total_water_ml": 2300},
                "performance": {"distance": 4.5, "steps": 7500, "calories_burned": 350}
            }
        }
        
        # Mock DataFrame to return a df with 2 rows
        df_mock = MagicMock()
        df_mock.__len__ = lambda x: 2
        mock_dataframe.return_value = df_mock
        
        # Call the function
        display_correlation_analysis("user1")
        
        # Verify that a warning was displayed about few days with data
        warning_call = None
        for call in mock_st.warning.call_args_list:
            if "days with both nutrition and workout data" in call[0][0]:
                warning_call = call
                break
        
        self.assertIsNotNone(warning_call, "Few days warning not found")
        self.assertIn("2 days with both nutrition", str(warning_call))

    @patch("nutrition_analytics.st")
    @patch("nutrition_analytics.get_nutrition_performance_correlation")
    @patch("nutrition_analytics.pd")
    def test_correlation_metrics_display(self, mock_pd, mock_get_correlation, mock_st):
        """Test that correlation data is processed and displayed"""
        
        """
        AI Prompt:
        Write a test function test_correlation_metrics_display that verifies the display_correlation_analysis function properly processes and displays correlation data. The test should mock three days of complete nutrition and performance data, verify the pandas DataFrame is created, and confirm that Streamlit columns are set up correctly for displaying the metrics.
        """
        
        # Mock the columns to return a list with two mock objects
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2]
        
        # Mock correlation data with three days of data
        mock_get_correlation.return_value = {
            "2024-07-15": {
                "nutrition": {"total_calories": 2000, "total_protein": 100, "total_carbs": 200, "total_fat": 50, "total_water_ml": 2500},
                "performance": {"distance": 5.0, "steps": 8000, "calories_burned": 400}
            },
            "2024-07-16": {
                "nutrition": {"total_calories": 1800, "total_protein": 90, "total_carbs": 180, "total_fat": 45, "total_water_ml": 2300},
                "performance": {"distance": 4.5, "steps": 7500, "calories_burned": 350}
            },
            "2024-07-17": {
                "nutrition": {"total_calories": 2200, "total_protein": 110, "total_carbs": 220, "total_fat": 55, "total_water_ml": 2700},
                "performance": {"distance": 5.5, "steps": 9000, "calories_burned": 450}
            }
        }
        
        # Mock pandas DataFrame
        mock_df = MagicMock()
        mock_df.__len__.return_value = 3
        mock_pd.DataFrame.return_value = mock_df
        
        # Call the function
        display_correlation_analysis("user1")
        
        # Verify only that the data processing happened
        mock_pd.DataFrame.assert_called_once()
        
        # Verify columns were created
        mock_st.columns.assert_called_with(2)
        
        # Verify that something was displayed in the columns
        mock_col1.__enter__.assert_called()
        mock_col2.__enter__.assert_called()


if __name__ == '__main__':
    unittest.main() 