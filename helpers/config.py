import dotenv
import os

dotenv.load_dotenv()

# asana
asana_token = os.getenv("ASANA_TOKEN")
workspace_gid = os.getenv("WORKSPACE_GID")  
team_gid = os.getenv('TEAM_GID')

# webhook server
wb_server_url = os.getenv("WH_SERVER_URL")

# database
db_user = os.getenv('DB_USER')
db_host = os.getenv('DB_HOST')
db_pass = os.getenv('DB_PASS')
database = os.getenv('DATABASE')
