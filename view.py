import os, struct
import fcntl, termios
import sys

class UnixView:
  def __init__(self):
    self.size = self.get_size()

  def print_threads(self, threads):
    self.size = self.get_size()
    author_width = 0
    for thread in threads:
      if len(thread.author) > author_width:
        author_width = len(thread.author)
    title_width = self.size[1] - 12 - author_width

    alpha = ord('a') + len(threads)
    for thread in threads:
      alpha -= 1
      title = thread.title[:title_width]
      pad = title_width - len(title)
      line = '%%c | %%s %%%ds|%%s| %%s' % pad
      print(line % (chr(alpha), title, '', thread.unread_str(), thread.author))

  def print_posts(self, posts):
    self.size = self.get_size()
    alpha = ord('a') + len(posts)
    for post in posts:
      alpha -= 1

      message_width = self.size[1] - 4 - len(post.author) - 2
      print('%c | %s: %s' % (chr(alpha), post.author, post.message[:message_width]))
      position = message_width
      message_width = self.size[1] - 6
      while position < len(post.message):
        print('      %s' % (post.message[position:position+message_width]))
        position += message_width
      #print ('' + chr(alpha) + ' |' + post.__repr__())

  def get_size(self):
    """
    returns (lines:int, cols:int)
    """
    import os, struct
    def ioctl_GWINSZ(fd):
        import fcntl, termios
        return struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, "1234"))
    # try stdin, stdout, stderr
    for fd in (0, 1, 2):
        try:
            return ioctl_GWINSZ(fd)
        except:
            pass
    # try os.ctermid()
    try:
        fd = os.open(os.ctermid(), os.O_RDONLY)
        try:
            return ioctl_GWINSZ(fd)
        finally:
            os.close(fd)
    except:
        pass
    # try `stty size`
    try:
        return tuple(int(x) for x in os.popen("stty size", "r").read().split())
    except:
        pass
    # try environment variables
    try:
        return tuple(int(os.getenv(var)) for var in ("LINES", "COLUMNS"))
    except:
        pass
    # i give up. return default.
    return (25, 80)
