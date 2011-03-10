from HTMLParser import HTMLParser
from forum import Thread, Post

class ParserBase(HTMLParser):
  """base class for ThreadParser and ForumParser
  to get data out, attach listeners that are a tuple like
  (tagname, attribute name, attribute value, function(parser, attributes)
  and it'll fire the function when it hits a matching tag.  set the parser's mode
  in the function to grab data, it'll automatically have the mode cleared when the
  parser leaves the tag's scope"""

  def __init__(self):
    HTMLParser.__init__(self)
    self.listeners = []
    self.depth = 0

  def set_mode(self, mode):
    self.mode = mode
    self.depth = 0

  def handle_starttag(self, tag, attrs):
    if tag == 'img':
      # this was erroneously changing the tag depth count
      return

    self.depth = self.depth + 1
    for listener in self.listeners:
      if tag == listener[0]:
        for attr in attrs:
          if attr[0] == listener[1] and attr[1] == listener[2]:
             listener[3](self, attrs)

  def handle_endtag(self, tag):
    if self.mode == None:
      return
    self.depth = self.depth - 1
    if self.depth < 0:
      self.set_mode(None)

class ThreadParser(ParserBase):
  """call read_thread with a html string to get back a list of posts"""

  def __init__(self):
    ParserBase.__init__(self)
    self.listeners.append(('table', 'class', 'post', ThreadParser.handle_postid))
    self.listeners.append(('dt', 'class', 'author', lambda parser, attrs: parser.set_mode('author')))
    self.listeners.append(('td', 'class', 'postbody', lambda parser, attrs: parser.set_mode('postbody')))

    #TODO: add a link to the attachment to the end of the message
    self.listeners.append(('p', 'class', 'attachment', lambda parser, attrs: parser.set_mode(None)))
    self.listeners.append(('div', 'class', 'bbc-block', lambda parser, attrs: parser.post.open_quote()))
    self.post = None

  def handle_endtag(self, tag):
    if tag == 'blockquote' and self.post != None:
      self.post.message += ' }'
    ParserBase.handle_endtag(self, tag)

  def handle_postid(self, attrs):
    for attr in attrs:
      if attr[0] == 'id':
        postid = int(attr[1][4:])
        self.posts.append(Post(postid))
        self.post = self.posts[-1]
        return

  def read_thread(self, str):
    self.reset()
    self.feed(str)
    self.close()
    return self.posts

  def reset(self):
    self.posts = []
    self.post = None
    self.mode = None
    ParserBase.reset(self)

  def handle_data(self, data):
    if self.mode == 'author':
      self.post.author = data
      self.set_mode(None)
    elif self.mode == 'postbody':
      data = data.strip()
      if data != '':
        if self.post.message != '' and self.post.message[-1] != ' ':
          self.post.message += ' '
        self.post.message += data
    
class ForumParser(ParserBase):
  """call read_forum with an html string to get back a list of threads"""

  def __init__(self):
    ParserBase.__init__(self)
    self.listeners.append(('a', 'class', 'thread_title', lambda parser, attrs: parser.set_mode('thread_title')))
    self.listeners.append(('td', 'class', 'author', lambda parser, attrs: parser.set_mode('author')))
    self.listeners.append(('a', 'class', 'count', lambda parser, attrs: parser.set_mode('unread')))
    self.listeners.append(('a', 'class', 'x', lambda parser, attrs: parser.thread.unread_zero()))
    self.listeners.append(('tr', 'class', 'thread', ForumParser.handle_threadid))
    self.listeners.append(('tr', 'class', 'thread seen', ForumParser.handle_threadid))
    self.threads = []

  def handle_threadid(self, attrs):
    for attr in attrs:
      if attr[0] == 'id':
        threadid = int(attr[1][6:])
        self.threads.append(Thread(threadid))
        self.thread = self.threads[-1]

  def read_forum(self, str):
    self.reset()
    self.feed(str)
    self.close()
    self.threads.reverse()
    return self.threads

  def reset(self):
    ParserBase.reset(self)
    self.set_mode(None)
    self.threads = []
    
  def handle_data(self, data):
    if self.mode == 'thread_title':
      self.thread.title = data
      self.set_mode(None)
    elif self.mode == 'author':
      self.thread.author = data
      self.set_mode(None)
    elif self.mode == 'unread':
      self.thread.unread = int(data)
      self.set_mode(None)
