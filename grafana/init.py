import os
import time
import requests
import json
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GrafanaInitializer:
    def __init__(self):
        self.grafana_url = os.getenv('GRAFANA_URL', 'http://localhost:3000')
        self.grafana_user = os.getenv('GRAFANA_ADMIN_USER', 'admin')
        self.grafana_password = os.getenv('GRAFANA_ADMIN_PASSWORD', 'admin')
        self.postgres_host = os.getenv('POSTGRES_HOST', 'postgres')
        self.postgres_port = os.getenv('POSTGRES_PORT', '5432')
        self.postgres_db = os.getenv('POSTGRES_DB', 'mental_health')
        self.postgres_user = os.getenv('POSTGRES_USER', 'newton')
        self.postgres_password = os.getenv('POSTGRES_PASSWORD', 'Admin')
        
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        self.session = requests.Session()
        self.session.auth = (self.grafana_user, self.grafana_password)
        
    def wait_for_grafana(self, max_retries: int = 30, delay: int = 5) -> bool:
        """Wait for Grafana to become available."""
        for i in range(max_retries):
            try:
                response = self.session.get(f"{self.grafana_url}/api/health")
                if response.status_code == 200:
                    logger.info("Grafana is available")
                    return True
            except requests.exceptions.RequestException:
                pass
            logger.info(f"Waiting for Grafana to become available (attempt {i + 1}/{max_retries})")
            time.sleep(delay)
        return False

    def setup_datasource(self) -> None:
        """Configure PostgreSQL as a data source."""
        datasource_config = {
            "name": "PostgreSQL",
            "type": "postgres",
            "url": f"{self.postgres_host}:{self.postgres_port}",
            "access": "proxy",
            "basicAuth": False,
            "database": self.postgres_db,
            "user": self.postgres_user,
            "secureJsonData": {
                "password": self.postgres_password
            },
            "jsonData": {
                "sslmode": "disable",
                "maxOpenConns": 100,
                "maxIdleConns": 100,
                "connMaxLifetime": 14400,
                "postgresVersion": 1300,
                "timescaledb": False
            }
        }

        response = self.session.post(
            f"{self.grafana_url}/api/datasources",
            json=datasource_config
        )
        
        if response.status_code == 200:
            logger.info("PostgreSQL datasource configured successfully")
        else:
            logger.error(f"Failed to configure datasource: {response.text}")

    def create_dashboards(self) -> None:
        """Initialize Grafana dashboards for system monitoring."""
        # System Performance Dashboard
        performance_dashboard = {
            "dashboard": {
                "title": "Mental Health Assistant Performance",
                "timezone": "browser",
                "panels": [
                    # Response Time Panel
                    {
                        "title": "Average Response Time",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "targets": [{
                            "rawSql": """
                            SELECT
                                timestamp as time,
                                avg(response_time) as "Response Time"
                            FROM conversations
                            WHERE $__timeFilter(timestamp)
                            GROUP BY timestamp
                            ORDER BY timestamp
                            """,
                            "format": "time_series"
                        }]
                    },
                    # Model Usage Panel
                    {
                        "title": "Model Usage Distribution",
                        "type": "piechart",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "targets": [{
                            "rawSql": """
                            SELECT
                                model_used as metric,
                                count(*) as value
                            FROM conversations
                            WHERE $__timeFilter(timestamp)
                            GROUP BY model_used
                            """
                        }]
                    },
                    # Token Usage Panel
                    {
                        "title": "Average Token Usage",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                        "targets": [{
                            "rawSql": """
                            SELECT
                                timestamp as time,
                                avg(total_tokens) as "Total Tokens",
                                avg(prompt_tokens) as "Prompt Tokens",
                                avg(completion_tokens) as "Completion Tokens"
                            FROM conversations
                            WHERE $__timeFilter(timestamp)
                            GROUP BY timestamp
                            ORDER BY timestamp
                            """,
                            "format": "time_series"
                        }]
                    }
                ],
                "refresh": "5s"
            }
        }

        # User Feedback Dashboard
        feedback_dashboard = {
            "dashboard": {
                "title": "User Feedback Analysis",
                "timezone": "browser",
                "panels": [
                    # Feedback Distribution
                    {
                        "title": "Feedback Distribution",
                        "type": "stat",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "targets": [{
                            "rawSql": """
                            SELECT
                                sum(case when feedback > 0 then 1 else 0 end) as "Positive",
                                sum(case when feedback < 0 then 1 else 0 end) as "Negative"
                            FROM feedback
                            WHERE $__timeFilter(timestamp)
                            """
                        }]
                    },
                    # Relevance Distribution
                    {
                        "title": "Answer Relevance Distribution",
                        "type": "piechart",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "targets": [{
                            "rawSql": """
                            SELECT
                                relevance as metric,
                                count(*) as value
                            FROM conversations
                            WHERE $__timeFilter(timestamp)
                            GROUP BY relevance
                            """
                        }]
                    },
                    # Feedback Timeline
                    {
                        "title": "Feedback Timeline",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                        "targets": [{
                            "rawSql": """
                            SELECT
                                date_trunc('hour', timestamp) as time,
                                count(*) FILTER (WHERE feedback > 0) as "Positive",
                                count(*) FILTER (WHERE feedback < 0) as "Negative"
                            FROM feedback
                            WHERE $__timeFilter(timestamp)
                            GROUP BY date_trunc('hour', timestamp)
                            ORDER BY time
                            """,
                            "format": "time_series"
                        }]
                    }
                ],
                "refresh": "5s"
            }
        }

        # Create dashboards
        for dashboard in [performance_dashboard, feedback_dashboard]:
            response = self.session.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=dashboard
            )
            
            if response.status_code == 200:
                logger.info(f"Dashboard '{dashboard['dashboard']['title']}' created successfully")
            else:
                logger.error(f"Failed to create dashboard: {response.text}")

def main():
    initializer = GrafanaInitializer()
    
    # Wait for Grafana to become available
    if not initializer.wait_for_grafana():
        logger.error("Grafana is not available after maximum retries")
        return
    
    # Set up data source and dashboards
    try:
        initializer.setup_datasource()
        initializer.create_dashboards()
        logger.info("Grafana initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Grafana: {str(e)}")

if __name__ == "__main__":
    main()