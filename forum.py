""" some classes for holding data about threads and posts, 
__repr__ is used for displaying to the end user though """

class Thread:
  def __init__(self, id):
    self.id = id
    self.author = 'author'
    self.title = "thread name"
    self.unread = -1

  def unread_zero(self):
    self.unread = 0

  def __repr__(self):
    unread = ' %2d ' % self.unread
    if (self.unread == -1):
      unread = '    '
    if (self.unread > 99):
      unread = 'lots'
    return '%s| %s | %s' % (unread, self.title, self.author)

class Post:
  def __init__(self, id):
    self.id = id
    self.message = ''
    self.author = 'author'

  def get_id(self):
    return self.id

  def open_quote(self):
    """ needed to assign this from a lambda """
    self.message += '{'

  def __repr__(self):
    return ' %s: %s' % (self.author, self.message)
