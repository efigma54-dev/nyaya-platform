from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the Firebase JWT token from the Authorization header.
    Returns the decoded token dictionary containing user claims (e.g., uid, email).
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Firebase token: {str(e)}"
        )

async def admin_required(user: dict = Depends(get_current_user)):
    """
    Checks if the authenticated Firebase user has the 'admin' custom claim.
    """
    is_admin = user.get("admin", False)
    if not is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return user
