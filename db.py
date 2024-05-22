from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://viktor:3ZohDVKsdcn3@127.0.0.1:5432/uplaim"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
new_session = async_sessionmaker(engine, expire_on_commit=False)

