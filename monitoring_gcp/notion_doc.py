import os
import logging
from datetime import datetime
import uuid
from google.cloud import tasks_v2
import google.auth
from googleapiclient.discovery import build

# Configure logging for local execution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gcp_notion_sync.log')
    ]
)
logger = logging.getLogger(__name__)

os.chdir('/Users/mo/Library/Mobile Documents/com~apple~CloudDocs/cloud_agent/puppy')    
from packages.capsule import CapsuleNotion
from packages.firestore import Firestore
from packages.notion import Notion
from packages.tasks import Tasks

class GCP_update_notion:
    def __init__(self):
        logger.info("Initializing GCP_update_notion class")
        self.database_id = '1da0fcf3-8494-80b2-bb66-d3f76c0c01d0'
        self.list_collection = ['memory-bank', 'system', 'references', 'develop']
        self.writer = Notion().writer
        self.firestore_icon = 'https://www.notion.so/icons/archive_blue.svg'
        self.queue_icon = 'https://www.notion.so/icons/arrow-down-line_green.svg'
        self.functions_icon = 'https://www.notion.so/icons/priority-high_purple.svg'
        self.run_icon = 'https://www.notion.so/icons/priority-high_yellow.svg'
        self.project = "digital-africa-rainbow"
        self.location = "europe-west1"  # e.g. "us-central1"
        self.parent = f"projects/{self.project}/locations/{self.location}"
        
        logger.info(f"Using project: {self.project}")
        logger.info(f"Using location: {self.location}")
        
        try:
            # Use Google Auth default credentials
            self.credentials, self.project = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            logger.info("Google Auth default credentials loaded successfully")
            logger.info(f"Using project: {self.project}")
        except Exception as e:
            logger.error(f"Failed to load Google Auth default credentials: {e}")
            raise

    def get_page_id(self, name):
        logger.debug(f"Looking up page ID for name: {name}")
        filter_ = lambda name: {
                "property": "Name",  # Adjust to your title property name
                "title": {
                    "equals": f"{name}"
                }
            }
        try:
            response = Notion().pull.query_database(self.database_id, filter_(name))
            # Handle the response properly - check if it has 'results' key
            if isinstance(response, dict) and 'results' in response:
                page = response['results']
                if page:
                    page_id = page[0]['id']
                    logger.debug(f"Found page ID: {page_id} for name: {name}")
                    return page_id
                else:
                    logger.warning(f"No page found for name: {name}")
                    return None
            else:
                logger.error(f"Unexpected response format from Notion API: {response}")
                return None
        except Exception as e:
            logger.error(f"Error looking up page ID for {name}: {e}")
            return None

    def extract_date(self, iso_timestamp: str) -> str:
        # Truncate to microseconds and parse
        try:
            dt = datetime.strptime(iso_timestamp[:26], "%Y-%m-%dT%H:%M:%S.%f")
            return dt.strftime("%Y-%m-%d")
        except Exception as e:
            logger.error(f"Error extracting date from {iso_timestamp}: {e}")
            return "Unknown"
            
    def system_firestore_update(self):
        logger.info("Starting Firestore system update")
        # List all top-level collections
        for database in self.list_collection:
            logger.info(f"Processing Firestore database: {database}")
            try:
                db = Firestore(database=database).client
                collections = db.collections()
                collection_count = 0
                for collection in collections:
                    logger.info(f"Processing collection: {collection.id} in database: {database}")
                    self.update_collection(collection, database)
                    collection_count += 1
                logger.info(f"Completed processing {collection_count} collections in database: {database}")
            except Exception as e:
                logger.error(f"Error processing Firestore database {database}: {e}")
                
    def update_collection(self, collection, database):
        logger.debug(f"Updating collection: {collection.id} in database: {database}")
        try:
            properties = {'Ressource': {
                                        'type': 'select',
                                        'select': {
                                                    'name': 'Firestore',
                                                    }},
                                        'Type': {
                                                    'type': 'select',
                                                    'select': {
                                                        'name': 'primitive',
                                                        }
                                                    }}
            properties['Description'] = self.writer.text(f"Database: {database}")
            properties['Name'] = self.writer.title(collection.id)
            params = {
                'database': self.database_id,
                'properties': properties,
                'process_name': 'firestore_collection_update',
                'page_id': self.get_page_id(collection.id), 
                'icon': self.firestore_icon
            }
            CapsuleNotion(**params).enqueue()
            logger.info(f"Successfully queued Firestore collection update for: {collection.id}")
        except Exception as e:
            logger.error(f"Error updating collection {collection.id}: {e}")
            
    def system_queue_update(self):
        logger.info("Starting Cloud Tasks queue update")
        try:
            tasks_client = Tasks().client
            # List all queues
            queues = tasks_client.list_queues(parent=self.parent)
            queue_count = 0
            # Display name and settings
            for queue in queues:
                logger.info(f"Processing queue: {queue.name}")
                self.update_queue(queue)
                queue_count += 1
            logger.info(f"Completed processing {queue_count} queues")
        except Exception as e:
            logger.error(f"Error in system_queue_update: {e}")
            
    def update_queue(self, queue):
        logger.debug(f"Updating queue: {queue.name}")
        try:
            description = list()
            #description.append(f"\nQueue: {queue.name}")
            description.append(f"  State: {queue.state.name}")
            description.append(f"  Rate Limits:")
            description.append(f"    Max dispatches per second: {queue.rate_limits.max_dispatches_per_second}")
            description.append(f"    Max burst size: {queue.rate_limits.max_burst_size}")
            description.append(f"    Max concurrent dispatches: {queue.rate_limits.max_concurrent_dispatches}")
            description.append(f"  Retry Config:")
            description.append(f"    Max attempts: {queue.retry_config.max_attempts}")
            description.append(f"    Max retry duration: {queue.retry_config.max_retry_duration}")
            description.append(f"    Min backoff: {queue.retry_config.min_backoff}")
            description.append(f"    Max backoff: {queue.retry_config.max_backoff}")
            description.append(f"  Logging Sample Rate: {queue.stackdriver_logging_config.sampling_ratio}")
            description = '\n'.join(description)
            
            properties = {
                            'Name': self.writer.title(queue.name.split('/')[-1]),
                            'Ressource': self.writer.select('queue'),
                            'Type': self.writer.select('primitive'),
                            'Description': self.writer.text(description)
                        }
            params = {
                        'database': self.database_id,
                        'properties': properties,
                        'process_name': 'queue_notion_update',
                        'page_id': self.get_page_id(properties['Name']), 
                        'icon': self.queue_icon
                    }
            CapsuleNotion(**params).enqueue()
            logger.info(f"Successfully queued queue update for: {queue.name.split('/')[-1]}")
        except Exception as e:
            logger.error(f"Error updating queue {queue.name}: {e}")
    
    def system_functions_update(self):
        logger.info("Starting Cloud Functions update")
        try:
            # Build the Cloud Functions API client (for 1st gen)
            functions_service = build("cloudfunctions", "v2", credentials=self.credentials)
            # Fetch the list of functions
            total_functions = 0
            for project in ['digital-africa-fuze', 'digital-africa-rainbow']:
                logger.info(f"Processing Cloud Functions for project: {project}")
                parent = f"projects/{project}/locations/-"
                response = functions_service.projects().locations().functions().list(parent=parent).execute()
                project_functions = 0
                for function in filter(lambda x: x['state'] != 'FAILED', response.get("functions", [])):
                    logger.info(f"Processing function: {function['name']} (state: {function['state']})")
                    self.update_function(function)
                    project_functions += 1
                logger.info(f"Completed processing {project_functions} functions in project: {project}")
                total_functions += project_functions
            logger.info(f"Completed processing {total_functions} total functions across all projects")
            return response
        except Exception as e:
            logger.error(f"Error in system_functions_update: {e}")
            return None
    
    def update_function(self, function):    
        logger.debug(f"Updating function: {function['name']}")
        try:
            trigger_info = function.get("eventTrigger")
            service_config = function.get("serviceConfig", {})
            available_memory = service_config.get("availableMemory", "Not specified")
            service_account = service_config.get("serviceAccountEmail", "default (App Engine)")

            properties = {  
                'Name':  self.writer.title(function['name'].split('/')[-1]),
                'Description': self.writer.text(
                    function['name'] + '\n' +
                    service_account + '\n' +
                    function['state'] + '\t' +
                    self.extract_date(function['updateTime']) + '\n' +
                    'Available Memory: ' + available_memory
                ),
                'Path': self.writer.text(function['name']),
                'Ressource': self.writer.select('function'),
            }
            if trigger_info:
                trigger_type = trigger_info["eventType"]
                resource = trigger_info.get("eventFilters", [])
                properties['Trigger'] = self.writer.text(f"Trigger Type: {trigger_type}\nEvent Filters: {resource}")
                logger.debug(f"Function {function['name']} has event trigger: {trigger_type}")
            else:
                # No eventTrigger usually means HTTP
                properties['URL'] = self.writer.text(function['url'])
                properties['Trigger'] = self.writer.text(f"Trigger Type: HTTP\n{function['url']}")
                logger.debug(f"Function {function['name']} has HTTP trigger: {function['url']}")
            
            params = {
                        'database': self.database_id,
                        'properties': properties,
                        'process_name': 'functions_notion_update',
                        'page_id': self.get_page_id(function['name'].split('/')[-1]), 
                        'icon': self.functions_icon
                            }
            CapsuleNotion(**params).enqueue()
            logger.info(f"Successfully queued function update for: {function['name'].split('/')[-1]}")
        except Exception as e:
            logger.error(f"Error updating function {function['name']}: {e}")
                
    def run(self):
        logger.info("=" * 50)
        logger.info("Starting GCP to Notion synchronization")
        logger.info("=" * 50)
        
        start_time = datetime.now()
        
        try:
            logger.info("Step 1: Updating Firestore collections")
            self.system_firestore_update()
            
            logger.info("Step 2: Updating Cloud Tasks queues")
            self.system_queue_update()
            
            logger.info("Step 3: Updating Cloud Functions")
            self.system_functions_update()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("=" * 50)
            logger.info(f"GCP to Notion synchronization completed successfully")
            logger.info(f"Total execution time: {duration}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Fatal error during synchronization: {e}")
            raise
        
GCP_update_notion().run()