import datetime
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from config import settings

class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
    secret = settings.SECRET_KEY
    print(f"DEBUG: AuthHandler Secret Key loaded: '{secret}' (Length: {len(secret)})")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        return self.pwd_context.verify(
            plain_password,
            hashed_password
        )

    def encode_token(self, user_id: str, username: str) -> str:
        payload = {
            "exp": datetime.datetime.now(datetime.timezone.utc)
                   + datetime.timedelta(minutes=30),
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "sub": {"user_id": user_id, "username": username},
        }

        print(f"DEBUG: Encoding with secret (length {len(self.secret)}): '{self.secret[:5]}...{self.secret[-5:]}'")
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_token(self, token: str):
        try:
            print(f"DEBUG: Decoding with secret (length {len(self.secret)}): '{self.secret[:5]}...{self.secret[-5:]}'")
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=["HS256"]
            )
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Signature has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    def auth_wrapper(
        self,
        auth: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        return self.decode_token(auth.credentials)

auth_handler = AuthHandler()