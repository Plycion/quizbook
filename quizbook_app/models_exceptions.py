class Error(Exception):
   """Base class for other exceptions"""
   pass

class PracticeIsEmptyException(Error):
   """Raised when a practice is empty"""
   pass

class TokenExistsException(Error):
   """Raised when a token alreay exists"""
   pass