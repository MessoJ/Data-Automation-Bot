import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import logging
from jinja2 import Environment, FileSystemLoader
import webbrowser

from ..database.db_manager import DatabaseManager
from ..utils.helpers import ensure_directory_exists

class ReportGenerator:
    def __init__(self, config):
        """
        Initialize the report generator with configuration settings.
        
        Parameters:
        -----------
        config : dict
            Configuration dictionary with report settings
        """
        self.config = config
        self.db_manager = DatabaseManager(config['database'])
        self.report_dir = config['reporting']['output_directory']
        ensure_directory_exists(self.report_dir)
        
        # Set up Jinja2 for HTML template rendering
        template_dir = config['reporting'].get('template_directory', 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        self.logger = logging.getLogger(__name__)
        
    def generate_daily_report(self, date=None):
        """
        Generate a daily report based on processed data.
        
        Parameters:
        -----------
        date : datetime.date, optional
            The date for which to generate the report. Defaults to today.
            
        Returns:
        --------
        str
            Path to the generated report
        """
        if date is None:
            date = datetime.now().date()
            
        self.logger.info(f"Generating daily report for {date}")
        
        # Query data from database
        query = f"""
        SELECT * FROM processed_data 
        WHERE DATE(timestamp) = '{date}'
        """
        data = self.db_manager.execute_query(query)
        
        if data.empty:
            self.logger.warning(f"No data available for {date}")
            return None
            
        # Generate report components
        summary_stats = self._generate_summary_stats(data)
        charts = self._generate_charts(data)
        
        # Create HTML report
        report_path = self._create_html_report(date, data, summary_stats, charts)
        
        # Optionally create PDF version
        if self.config['reporting'].get('generate_pdf', False):
            pdf_path = self._convert_to_pdf(report_path)
            
        self.logger.info(f"Report generated successfully: {report_path}")
        return report_path
    
    def _generate_summary_stats(self, data):
        """
        Generate summary statistics from the data.
        
        Parameters:
        -----------
        data : pandas.DataFrame
            The data to analyze
            
        Returns:
        --------
        dict
            Dictionary containing summary statistics
        """
        summary = {
            'total_records': len(data),
            'average_values': data.mean().to_dict(),
            'min_values': data.min().to_dict(),
            'max_values': data.max().to_dict(),
            'missing_data_percentage': (data.isnull().sum() / len(data) * 100).to_dict()
        }
        
        # Add more domain-specific metrics as needed
        
        return summary
    
    def _generate_charts(self, data):
        """
        Generate charts for the report.
        
        Parameters:
        -----------
        data : pandas.DataFrame
            The data to visualize
            
        Returns:
        --------
        list
            List of paths to generated chart images
        """
        charts_dir = os.path.join(self.report_dir, 'charts')
        ensure_directory_exists(charts_dir)
        
        chart_paths = []
        
        # Example: Time series chart
        if 'timestamp' in data.columns:
            plt.figure(figsize=(10, 6))
            time_series_data = data.set_index('timestamp').sort_index()
            for column in self.config['reporting'].get('chart_columns', []):
                if column in time_series_data.columns:
                    time_series_data[column].plot()
            
            plt.title('Time Series Analysis')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.legend()
            plt.tight_layout()
            
            chart_path = os.path.join(charts_dir, 'time_series.png')
            plt.savefig(chart_path)
            plt.close()
            chart_paths.append(chart_path)
        
        # Example: Distribution chart
        for column in self.config['reporting'].get('distribution_columns', []):
            if column in data.columns and data[column].dtype in ['int64', 'float64']:
                plt.figure(figsize=(8, 5))
                data[column].hist(bins=20)
                plt.title(f'Distribution of {column}')
                plt.xlabel(column)
                plt.ylabel('Frequency')
                plt.tight_layout()
                
                chart_path = os.path.join(charts_dir, f'{column}_distribution.png')
                plt.savefig(chart_path)
                plt.close()
                chart_paths.append(chart_path)
        
        return chart_paths
    
    def _create_html_report(self, date, data, summary_stats, chart_paths):
        """
        Create an HTML report using Jinja2 templates.
        
        Parameters:
        -----------
        date : datetime.date
            The date of the report
        data : pandas.DataFrame
            The data used in the report
        summary_stats : dict
            Summary statistics
        chart_paths : list
            Paths to chart images
            
        Returns:
        --------
        str
            Path to the generated HTML report
        """
        template = self.jinja_env.get_template('daily_report.html')
        
        # Convert chart paths to relative paths for the HTML
        chart_names = [os.path.basename(path) for path in chart_paths]
        
        # Render the HTML
        html_content = template.render(
            report_date=date,
            summary_stats=summary_stats,
            chart_names=chart_names,
            data_sample=data.head(10).to_html(classes='table table-striped'),
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Write HTML to file
        report_filename = f"daily_report_{date.strftime('%Y-%m-%d')}.html"
        report_path = os.path.join(self.report_dir, report_filename)
        
        with open(report_path, 'w') as f:
            f.write(html_content)
            
        return report_path
    
    def _convert_to_pdf(self, html_path):
        """
        Convert HTML report to PDF.
        
        Parameters:
        -----------
        html_path : str
            Path to the HTML report
            
        Returns:
        --------
        str
            Path to the generated PDF
        """
        # You could use libraries like weasyprint, pdfkit, or reportlab here
        # For this example, we'll just log a message
        pdf_path = html_path.replace('.html', '.pdf')
        self.logger.info(f"PDF conversion would save to: {pdf_path}")
        self.logger.warning("PDF conversion not implemented - would require additional libraries")
        
        return pdf_path
    
    def email_report(self, report_path, recipients):
        """
        Email the generated report to recipients.
        
        Parameters:
        -----------
        report_path : str
            Path to the report file
        recipients : list
            List of email addresses
            
        Returns:
        --------
        bool
            Success status
        """
        # Implementation would depend on your email setup
        # Could use smtplib or an email service API
        self.logger.info(f"Would email report {report_path} to {recipients}")
        self.logger.warning("Email functionality not implemented")
        
        return True
    
    def open_report(self, report_path):
        """
        Open the report in the default web browser.
        
        Parameters:
        -----------
        report_path : str
            Path to the report file
            
        Returns:
        --------
        bool
            Success status
        """
        if os.path.exists(report_path):
            webbrowser.open('file://' + os.path.abspath(report_path))
            return True
        else:
            self.logger.error(f"Report file not found: {report_path}")
            return False
