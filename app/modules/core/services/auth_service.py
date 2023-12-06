class AuthService:
    def __init__(self, user_repo: UserRepository, token_service: TokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email=email)
        if not user:
            raise UserNotFoundException
        if not user.check_password(password):
            raise InvalidPasswordException
        return user

    async def login(self, email: str, password: str) -> Token:
        user = await self.authenticate(email=email, password=password)
        return await self.token_service.create_access_token_for_user(user=user)

    async def register(self, email: str, password: str) -> Token:
        user = await self.user_repo.create_user(email=email, password=password)
        return await self.token_service.create_access_token_for_user(user=user)