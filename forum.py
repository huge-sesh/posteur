""" some classes for holding data about threads and posts, 
__repr__ is used for displaying to the end user though """

class Thread(object):
  def __init__(self, id):
    self.id = id
    self.author = 'author'
    self.title = "thread name"
    self.unread = -1

  def unread_zero(self):
    self.unread = 0

  def unread_str(self):
    if (self.unread == -1):
      return '    '
    if (self.unread > 99):
      return 'lots'
    else:
      return ' %2d ' % self.unread

class Post(object):
  def __init__(self, id):
    self.id = id
    self.message = ''
    self.author = 'author'

  def get_id(self):
    return self.id

  def open_quote(self):
    """ needed to assign this from a lambda """
    self.message += '{'
