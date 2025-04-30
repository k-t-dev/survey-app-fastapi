# 非同期接続プールの作成
from asyncpg.pool import create_pool
import asyncpg

class Database:
    def __init__(self):
        self.pool = None
        
        #AWS
        # Prod
        self.postgres_user = "postgres"
        self.postgres_host = "survey-app-db.cnkc4u0qycdj.ap-northeast-1.rds.amazonaws.com"
        self.postgres_password = "cynwyz-mowPu8-wefbuq"
        self.postgres_db = "postgres"
        self.postgres_port ="5432"
        
        #Local
        # self.postgres_user = "myuser"
        # self.postgres_password = "mypassword"
        # self.postgres_host = "localhost"
        # self.postgres_port = "5432"
        # self.postgres_db = "mydatabase"
        

    async def connect(self):
        """Create the connection pool."""
        self.pool = await create_pool(
            user=self.postgres_user,
            password=self.postgres_password,
            database=self.postgres_db,
            host=self.postgres_host,
            port=self.postgres_port
        )

    async def close(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()

    async def get_connection(self):
        """Acquire a connection from the pool."""
        return await self.pool.acquire()

# Instance of the Database
db = Database()

