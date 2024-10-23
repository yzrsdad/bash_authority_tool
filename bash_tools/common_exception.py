class common_exceptions:
    class DangerousCommandException(Exception):
        def __init__(self, user_name, command, arguments):
            self.user_name = user_name
            self.command = command
            self.arguments = arguments
            self.message = f"{user_name} dangerous command '{command}' in arguments: {', '.join(arguments)}"
            super().__init__(self.message)

        def __str__(self):
            return self.message

    class UserNotFoundException(Exception):
        def __init__(self, user_name):
            self.user_name = user_name
            self.message = f"User '{user_name}' not found."
            super().__init__(self.message)

        def __str__(self):
            return self.message

    class PermissionDeniedException(Exception):
        def __init__(self, user_name, command, arguments, message):
            self.user_name = user_name
            self.command = command
            self.arguments = arguments
            if arguments is None:
                self.message = f"Permission denied for user '{user_name}' to execute '{command}'\n "
                if message:
                    self.message += f"Suggestion: {message}"
            else:
                self.message = f"Permission denied for user '{user_name}' to execute '{command}'  in arguments: {', '.join(arguments)}\n"
                if message:
                    self.message += f"Suggestion: {message}"
            super().__init__(self.message)

        def __str__(self):
            return self.message
