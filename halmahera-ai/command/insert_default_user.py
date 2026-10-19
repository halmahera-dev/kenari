import asyncio
import asyncpg
from datetime import datetime
import hashlib

DATABASE_URL = "postgresql://neondb_owner:npg_QlZRKn6aEJW1@ep-gentle-hill-a110pntw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def hash_password(password: str) -> str:
    """Hash password dengan salt"""
    salt = "bcd90c42ceead7b8f9c231234567890a"
    return hashlib.sha256(f"{password}:{salt}".encode()).hexdigest() + ":" + salt

async def insert_default_user():
    """Insert default user ke database"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Data user
        user_id = "HdaynXVC0R3JGKaBlSJCB4zPu1IvwLRV"
        email = "felip@gmail.com"
        name = "Felip"
        password = "Felip123!@#"
        hashed_password = hash_password(password)
        
        # Insert user
        await conn.execute("""
            INSERT INTO "user" (id, name, email, email_verified, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (id) DO NOTHING
        """, user_id, name, email, True, datetime.now(), datetime.now())
        
        # Insert account credential
        account_id = "credential_account_id_123"
        await conn.execute("""
            INSERT INTO account (id, account_id, provider_id, user_id, password, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO NOTHING
        """, account_id, user_id, "credential", user_id, hashed_password, datetime.now(), datetime.now())
        
        print(f"✅ Default user berhasil diinsert:")
        print(f"   User ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Name: {name}")
        print(f"   Password: {password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(insert_default_user())