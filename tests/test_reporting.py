"""
Tests for the reporting module.
"""
import unittest
import os
import pandas as pd
import json
from unittest.mock import patch, MagicMock, mock_open
from data_automation_bot.reporting.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    """Test cases for the ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test configuration
        self.test_config = {
            'reporting': {
                'output_dir': './test_reports',
                'templates_dir': './test_templates',
                'default_format': 'csv'
            }
        }
        
        # Create a sample DataFrame for testing
        self.sample_df = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=5),
            'product': ['Product A', 'Product B', 'Product A', 'Product C', 'Product B'],
            'revenue': [1000, 1500, 1200, 800, 1700],
            'cost': [600, 900, 650, 500, 950],
            'profit': [400, 600, 550, 300, 750]
        })
        
        # Initialize ReportGenerator with patched config
        with patch('data_automation_bot.config.Config.get_config', return_value=self.test_config):
            self.report_generator = ReportGenerator()
    
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_generate_csv_report(self, mock_makedirs, mock_exists):
        """Test generating a CSV report."""
        # Mock the open function
        mock_csv_file = mock_open()
        
        with patch('builtins.open', mock_csv_file):
            with patch('pandas.DataFrame.to_csv') as mock_to_csv:
                result = self.report_generator.generate_report(
                    self.sample_df,
                    'sales_report',
                    report_format='csv'
                )
                
                # Check if to_csv was called
                mock_to_csv.assert_called_once()
                
                # Verify return value has expected format
                self.assertTrue('file_path' in result)
                self.assertTrue(result['file_path'].endswith('.csv'))
    
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    def test_generate_json_report(self, mock_makedirs, mock_exists):
        """Test generating a JSON report."""
        # Mock the open function
        mock_json_file = mock_open()
        
        with patch('builtins.open', mock_json_file):
            with patch('json.dump') as mock_json_dump:
                result = self.report_generator.generate_report(
                    self.sample_df,
                    'sales_report',
                    report_format='json'
                )
                
                # Check if json.dump was called
                mock_json_dump.assert_called_once()
                
                # Verify return value has expected format
                self.assertTrue('file_path' in result)
                self.assertTrue(result['file_path'].endswith('.json'))
    
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.savefig')
    def test_generate_chart(self, mock_savefig, mock_figure, mock_makedirs, mock_exists):
        """Test generating a chart."""
        # Mock the plot objects
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_figure.return_value = mock_fig
        mock_fig.add_subplot.return_value = mock_ax
        
        # Generate a chart
        result = self.report_generator.generate_chart(
            self.sample_df,
            chart_type='bar',
            x_column='product',
            y_column='revenue',
            title='Revenue by Product',
            output_name='revenue_chart'
        )
        
        # Check if savefig was called
        mock_savefig.assert_called_once()
        
        # Verify return value has expected format
        self.assertTrue('file_path' in result)
        self.assertTrue(result['file_path'].endswith('.png'))
    
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    @patch('pandas.DataFrame.to_excel')
    def test_generate_excel_report(self, mock_to_excel, mock_makedirs, mock_exists):
        """Test generating an Excel report."""
        # Generate an Excel report
        result = self.report_generator.generate_report(
            self.sample_df,
            'sales_report',
            report_format='excel'
        )
        
        # Check if to_excel was called
        mock_to_excel.assert_called_once()
        
        # Verify return value has expected format
        self.assertTrue('file_path' in result)
        self.assertTrue(result['file_path'].endswith('.xlsx'))
    
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data='Template: {{ title }} - {{ data_summary }}')
    @patch('jinja2.Template')
    def test_generate_html_report(self, mock_template, mock_file, mock_makedirs, mock_exists):
        """Test generating an HTML report using a template."""
        # Mock template rendering
        mock_template_instance = MagicMock()
        mock_template.return_value = mock_template_instance
        mock_template_instance.render.return_value = '<html>Rendered Report</html>'
        
        # Generate an HTML report
        with patch('jinja2.FileSystemLoader'):
            with patch('jinja2.Environment'):
                result = self.report_generator.generate_html_report(
                    self.sample_df,
                    'sales_report',
                    template_name='report_template.html',
                    context={
                        'title': 'Sales Report',
                        'data_summary': 'Summary of sales data'
                    }
                )
                
                # Check if template.render was called
                mock_template_instance.render.assert_called_once()
                
                # Verify return value has expected format
                self.assertTrue('file_path' in result)
                self.assertTrue(result['file_path'].endswith('.html'))
    
    @patch('os.path.exists', return_value=True)
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pandas.DataFrame.to_html')
    def test_generate_dashboard(self, mock_to_html, mock_file, mock_makedirs, mock_exists):
        """Test generating a simple dashboard with multiple visualizations."""
        # Mock dataframe.to_html
        mock_to_html.return_value = '<table>DataFrame HTML</table>'
        
        # Mock chart generation
        with patch.object(ReportGenerator, 'generate_chart') as mock_generate_chart:
            mock_generate_chart.side_effect = [
                {'file_path': 'chart1.png'},
                {'file_path': 'chart2.png'}
            ]
            
            # Generate a dashboard
            result = self.report_generator.generate_dashboard(
                'sales_dashboard',
                charts=[
                    {
                        'dataframe': self.sample_df,
                        'chart_type': 'bar',
                        'x_column': 'product',
                        'y_column': 'revenue',
                        'title': 'Revenue by Product'
                    },
                    {
                        'dataframe': self.sample_df,
                        'chart_type': 'line',
                        'x_column': 'date',
                        'y_column': 'profit',
                        'title': 'Profit Trend'
                    }
                ],
                tables=[
                    {
                        'dataframe': self.sample_df,
                        'title': 'Sales Data'
                    }
                ],
                dashboard_title='Sales Overview Dashboard'
            )
            
            # Verify generate_chart was called twice
            self.assertEqual(mock_generate_chart.call_count, 2)
            
            # Verify return value has expected format
            self.assertTrue('file_path' in result)
            self.assertTrue(result['file_path'].endswith('.html'))
    
    def test_aggregate_for_report(self):
        """Test data aggregation for reports."""
        # Aggregate data for report
        result_df = self.report_generator.aggregate_for_report(
            self.sample_df,
            group_by='product',
            metrics=['revenue', 'cost', 'profit'],
            aggregations=['sum', 'mean']
        )
        
        # Verify the resulting dataframe has the expected columns
        expected_columns = [
            'revenue_sum', 'revenue_mean', 
            'cost_sum', 'cost_mean', 
            'profit_sum', 'profit_mean'
        ]
        
        for column in expected_columns:
            self.assertTrue(column in result_df.columns)
        
        # Verify the aggregation worked correctly
        product_a_rows = self.sample_df[self.sample_df['product'] == 'Product A']
        expected_revenue_sum = product_a_rows['revenue'].sum()
        self.assertEqual(result_df.loc['Product A', 'revenue_sum'], expected_revenue_sum)
    
    def tearDown(self):
        """Clean up after tests."""
        pass

if __name__ == '__main__':
    unittest.main()
