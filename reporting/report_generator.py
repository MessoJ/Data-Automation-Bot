"""
Report Generator for creating data reports and visualizations.

This module provides functionality for generating various reports:
- Daily/weekly/monthly summary reports
- Trend analysis reports
- Anomaly detection reports
- Custom reports based on specified parameters
"""

import logging
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
import csv

import data_automation_bot.config as config
from data_automation_bot.database.db_manager import DatabaseManager
from data_automation_bot.utils.helpers import handle_exceptions, ensure_directory_exists

class ReportGenerator:
    """Class for generating data reports and visualizations."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save generated reports. Defaults to config value.
        """
        self.output_dir = output_dir or config.REPORT_OUTPUT_DIR
        self.db_manager = DatabaseManager()
        
        # Ensure output directory exists
        ensure_directory_exists(self.output_dir)
        
        # Set default plotting style
        sns.set_style("whitegrid")
        plt.rcParams["figure.figsize"] = (12, 8)
        
        logging.debug(f"Initialized ReportGenerator with output directory: {self.output_dir}")
    
    @handle_exceptions
    def generate_daily_report(self, data_type: Optional[str] = None, 
                             report_format: str = None) -> str:
        """
        Generate a daily summary report for the previous day.
        
        Args:
            data_type: Optional filter for specific data type.
            report_format: Output format (csv, json, html, pdf). Defaults to config value.
            
        Returns:
            Path to the generated report file.
        """
        report_format = report_format or config.DEFAULT_REPORT_FORMAT
        
        # Define date range for yesterday
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=1)
        
        report_title = f"Daily Report - {start_date.strftime(config.REPORT_DATE_FORMAT)}"
        if data_type:
            report_title += f" - {data_type}"
        
        # Fetch data for the report
        data = self.db_manager.get_data(
            data_type=data_type,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Increase limit for daily reports
        )
        
        if not data:
            logging.warning(f"No data available for daily report on {start_date.strftime(config.REPORT_DATE_FORMAT)}")
            return self._generate_empty_report(report_title, report_format)
        
        # Create report
        return self._generate_report(data, report_title, report_format)
    
    @handle_exceptions
    def generate_weekly_report(self, data_type: Optional[str] = None, 
                              report_format: str = None) -> str:
        """
        Generate a weekly summary report for the previous week.
        
        Args:
            data_type: Optional filter for specific data type.
            report_format: Output format (csv, json, html, pdf). Defaults to config value.
            
        Returns:
            Path to the generated report file.
        """
        report_format = report_format or config.DEFAULT_REPORT_FORMAT
        
        # Define date range for the previous week
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=7)
        
        report_title = f"Weekly Report - {start_date.strftime(config.REPORT_DATE_FORMAT)} to {end_date.strftime(config.REPORT_DATE_FORMAT)}"
        if data_type:
            report_title += f" - {data_type}"
        
        # Fetch data for the report
        data = self.db_manager.get_data(
            data_type=data_type,
            start_date=start_date,
            end_date=end_date,
            limit=50000  # Increase limit for weekly reports
        )
        
        if not data:
            logging.warning(f"No data available for weekly report from {start_date.strftime(config.REPORT_DATE_FORMAT)}")
            return self._generate_empty_report(report_title, report_format)
        
        # Create report
        return self._generate_report(data, report_title, report_format)
    
    @handle_exceptions
    def generate_trend_report(self, data_type: str, 
                             days: int = 30,
                             report_format: str = None) -> str:
        """
        Generate a trend analysis report for a specific data type.
        
        Args:
            data_type: Data type to analyze.
            days: Number of days to include in the trend analysis.
            report_format: Output format (csv, json, html, pdf). Defaults to config value.
            
        Returns:
            Path to the generated report file.
        """
        report_format = report_format or config.DEFAULT_REPORT_FORMAT
        
        # Define date range
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days)
        
        report_title = f"Trend Report - {data_type} - {days} days"
        
        # Fetch data for the report
        data = self.db_manager.get_data(
            data_type=data_type,
            start_date=start_date,
            end_date=end_date,
            limit=100000  # Large limit for trend analysis
        )
        
        if not data:
            logging.warning(f"No data available for trend report on {data_type}")
            return self._generate_empty_report(report_title, report_format)
        
        # For trend reports, we need to process the data differently
        df = pd.DataFrame(data)
        
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Group by day
        df['date'] = df['timestamp'].dt.date
        daily_data = df.groupby('date').agg({
            'value': ['mean', 'min', 'max', 'std', 'count']
        }).reset_index()
        
        # Flatten the column hierarchy
        daily_data.columns = ['date', 'mean_value', 'min_value', 'max_value', 'std_value', 'count']
        
        # Generate trend visualizations
        viz_file = self._generate_trend_visualization(daily_data, data_type, days)
        
        # Convert back to records for report generation
        trend_data = daily_data.to_dict(orient='records')
        
        # Create report with visualization reference
        report_data = {
            'summary': {
                'data_type': data_type,
                'days_analyzed': days,
                'total_records': len(data),
                'date_range': f"{start_date.strftime(config.REPORT_DATE_FORMAT)} to {end_date.strftime(config.REPORT_DATE_FORMAT)}",
                'visualization_file': os.path.basename(viz_file) if viz_file else None
            },
            'trend_data': trend_data
        }
        
        return self._generate_report([report_data], report_title, report_format, include_viz=True)
    
    def _generate_trend_visualization(self, daily_data: pd.DataFrame, 
                                     data_type: str, days: int) -> Optional[str]:
        """
        Generate visualization for trend report.
        
        Args:
            daily_data: DataFrame with daily aggregated data.
            data_type: Data type being analyzed.
            days: Number of days in the analysis.
            
        Returns:
            Path to the generated visualization file, or None if generation failed.
        """
        try:
            # Create a multi-panel figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Plot 1: Daily mean values with min/max range
            ax1.plot(daily_data['date'], daily_data['mean_value'], 'b-', label='Mean Value')
            ax1.fill_between(
                daily_data['date'], 
                daily_data['min_value'], 
                daily_data['max_value'], 
                alpha=0.2, 
                color='b',
                label='Min-Max Range'
            )
            
            # Format the plot
            ax1.set_title(f"{data_type} - Daily Values (Last {days} Days)")
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Value')
            ax1.grid(True)
            ax1.legend()
            
            # Plot 2: Daily record count
            ax2.bar(daily_data['date'], daily_data['count'], color='green')
            ax2.set_title(f"{data_type} - Daily Record Count")
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Record Count')
            ax2.grid(True)
            
            # Adjust layout and save
            plt.tight_layout()
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            viz_filename = f"trend_{data_type.replace(' ', '_')}_{timestamp}.png"
            viz_path = os.path.join(self.output_dir, viz_filename)
            
            # Save the figure
            plt.savefig(viz_path, dpi=100)
            plt.close(fig)
            
            logging.info(f"Generated trend visualization: {viz_path}")
            return viz_path
            
        except Exception as e:
            logging.error(f"Failed to generate trend visualization: {str(e)}")
            return None
    
    def _generate_report(self, data: List[Dict[str, Any]], title: str, 
                        format: str, include_viz: bool = False) -> str:
        """
        Generate a report in the specified format.
        
        Args:
            data: Data to include in the report.
            title: Report title.
            format: Output format (csv, json, html, pdf).
            include_viz: Whether to include visualizations.
            
        Returns:
            Path to the generated report file.
        """
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Create safe filename
        safe_title = title.replace(' ', '_').replace('-', '_').lower()
        filename = f"{safe_title}_{timestamp}"
        
        # Generate report based on format
        if format.lower() == 'csv':
            return self._generate_csv_report(data, filename)
        elif format.lower() == 'json':
            return self._generate_json_report(data, filename)
        elif format.lower() == 'html':
            return self._generate_html_report(data, title, filename, include_viz)
        else:
            # Default to JSON if format not supported
            logging.warning(f"Unsupported report format: {format}, using JSON instead")
            return self._generate_json_report(data, filename)
    
    def _generate_empty_report(self, title: str, format: str) -> str:
        """
        Generate an empty report when no data is available.
        
        Args:
            title: Report title.
            format: Output format.
            
        Returns:
            Path to the generated empty report file.
        """
        empty_data = [{
            'message': 'No data available for this report',
            'report_time': datetime.now().isoformat()
        }]
        
        return self._generate_report(empty_data, title, format)
    
    def _generate_csv_report(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Generate a CSV report.
        
        Args:
            data: Data to include in the report.
            filename: Base filename without extension.
            
        Returns:
            Path to the generated CSV file.
        """
        file_path = os.path.join(self.output_dir, f"{filename}.csv")
        
        # Convert data to DataFrame for easier CSV writing
        if data and 'metadata' in data[0]:
            # Flatten metadata for CSV format
            flattened_data = []
            for record in data:
                flat_record = record.copy()
                metadata = flat_record.pop('metadata', {}) or {}
                
                # Add metadata fields with prefix
                for key, value in metadata.items():
                    if isinstance(value, (dict, list)):
                        # Skip complex nested structures
                        continue
                    flat_record[f"metadata_{key}"] = value
                
                flattened_data.append(flat_record)
            
            df = pd.DataFrame(flattened_data)
        else:
            df = pd.DataFrame(data)
        
        # Write to CSV
        df.to_csv(file_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
        
        logging.info(f"Generated CSV report: {file_path}")
        return file_path
    
    def _generate_json_report(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Generate a JSON report.
        
        Args:
            data: Data to include in the report.
            filename: Base filename without extension.
            
        Returns:
            Path to the generated JSON file.
        """
        file_path = os.path.join(self.output_dir, f"{filename}.json")
        
        # Create report structure
        report = {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'record_count': len(data)
            },
            'data': data
        }
        
        # Write to JSON file
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logging.info(f"Generated JSON report: {file_path}")
        return file_path
    
    def _generate_html_report(self, data: List[Dict[str, Any]], title: str,
                             filename: str, include_viz: bool = False) -> str:
        """
        Generate an HTML report.
        
        Args:
            data: Data to include in the report.
            title: Report title.
            filename: Base filename without extension.
            include_viz: Whether to include visualizations.
            
        Returns:
            Path to the generated HTML file.
        """
        file_path = os.path.join(self.output_dir, f"{filename}.html")
        
        # Convert data to DataFrame
        if data and isinstance(data[0], dict) and 'summary' in data[0] and 'trend_data' in data[0]:
            # Handle trend report data
            summary = data[0]['summary']
            trend_data = data[0]['trend_data']
            df = pd.DataFrame(trend_data)
            
            # Create HTML content
            html_content = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                f"<title>{title}</title>",
                "<style>",
                "body { font-family: Arial, sans-serif; margin: 20px; }",
                "h1 { color: #2c3e50; }",
                "table { border-collapse: collapse; width: 100%; }",
                "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "th { background-color: #f2f2f2; }",
                "tr:nth-child(even) { background-color: #f9f9f9; }",
                ".summary { background-color: #eef; padding: 10px; border-radius: 5px; margin-bottom: 20px; }",
                ".viz { text-align: center; margin: 20px 0; }",
                "</style>",
                "</head>",
                "<body>",
                f"<h1>{title}</h1>",
                "<div class='summary'>",
                "<h2>Summary</h2>",
                "<ul>"
            ]
            
            # Add summary items
            for key, value in summary.items():
                html_content.append(f"<li><strong>{key}:</strong> {value}</li>")
            
            html_content.append("</ul>")
            html_content.append("</div>")
            
            # Add visualization if available
            if include_viz and summary.get('visualization_file'):
                viz_file = summary['visualization_file']
                html_content.append("<div class='viz'>")
                html_content.append(f"<img src='{viz_file}' alt='Trend Visualization'>")
                html_content.append("</div>")
            
            # Add table
            html_content.append("<h2>Trend Data</h2>")
            html_content.append(df.to_html(index=False))
            
        else:
            # Regular data report
            df = pd.DataFrame(data)
            
            # Create HTML content
            html_content = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                f"<title>{title}</title>",
                "<style>",
                "body { font-family: Arial, sans-serif; margin: 20px; }",
                "h1 { color: #2c3e50; }",
                "table { border-collapse: collapse; width: 100%; }",
                "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "th { background-color: #f2f2f2; }",
                "tr:nth-child(even) { background-color: #f9f9f9; }",
                "</style>",
                "</head>",
                "<body>",
                f"<h1>{title}</h1>",
                f"<p>Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
                f"<p>Total records: {len(data)}</p>",
                "<h2>Data</h2>"
            ]
            
            # Convert DataFrame to HTML table
            html_content.append(df.to_html(index=False))
        
        # Close HTML tags
        html_content.extend(["</body>", "</html>"])
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write('\n'.join(html_content))
        
        logging.info(f"Generated HTML report: {file_path}")
        return file_path
