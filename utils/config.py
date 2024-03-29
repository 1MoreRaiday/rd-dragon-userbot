import environs

env = environs.Env()
env.read_env("./.env")

api_id = env.int("API_ID")
api_hash = env.str("API_HASH")

db_type = env.str("DATABASE_TYPE")
db_url = env.str("DATABASE_URL", "")
db_name = env.str("DATABASE_NAME")
persistence_path = env.str("PERSISTENCE_PATH", "./") + ('/' if not env.str("PERSISTENCE_PATH").endswith('/') else '')

test_server = env.bool("TEST_SERVER", False)
modules_repo_branch = env.str("MODULES_REPO_BRANCH", "master")
