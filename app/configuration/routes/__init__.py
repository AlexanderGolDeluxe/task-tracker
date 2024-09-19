from app.configuration.routes.routes import Routes
from app.core.routes import auth, base, task, user

__routes__ = Routes(
    routers=(auth.router, base.router, task.router, user.router))
