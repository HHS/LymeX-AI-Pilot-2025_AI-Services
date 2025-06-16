from redis.asyncio import Redis
from src.environment import environment


redis_client = Redis(
    host=environment.redis_host,
    port=environment.redis_port,
    db=environment.redis_db,
)
