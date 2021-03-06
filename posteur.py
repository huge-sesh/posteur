import mechanize.mechanize as mechanize
from parsers import ThreadParser, ForumParser
from view import UnixView
import getpass
import traceback
from motd import motd

class Posteur(object):
  def __init__(self):
    self.browser = mechanize.Browser()
    self.forumid = None
    self.threadid = None
    self.thread_parser = ThreadParser()
    self.forum_parser = ForumParser()
    self.view = UnixView()

  def login(self):
    """login to the forums"""
    #TODO: detect when login fails
    self.browser.open('http://forums.somethingawful.com/account.php?action=loginform')
    self.browser.select_form(predicate = lambda form: form.action == 'http://forums.somethingawful.com/account.php')
    self.browser['username'] = raw_input('username: ')
    self.browser['password'] = getpass.unix_getpass('password: ')
    response = self.browser.submit().read()
    return response.find('BAD PASSWORD') == -1

  def forum(self, forumid = None):
    """get thread list for the forum requested"""
    if forumid != None:
      self.forumid = forumid
    if self.forumid == None:
      print('no prior forum to refresh')
      return
    response = self.browser.open('http://forums.somethingawful.com/forumdisplay.php?forumid=%d' % self.forumid)
    threads = self.forum_parser.read_forum(response.read())
    threads = threads[-26:]
    self.threads = {}
    alpha = ord('a') + len(threads)
    for t in threads:
      alpha -= 1
      self.threads[chr(alpha)] = t
    self.view.print_threads(threads)

  def thread(self, alpha):
    """read a thread"""
    
    if alpha != None:
      thread = self.threads[alpha]
      self.threadid = thread.id
      response = self.browser.open('http://forums.somethingawful.com/showthread.php?threadid=%d&goto=lastpost' % self.threadid)
    else:
      response = self.browser.open('http://forums.somethingawful.com/showthread.php?threadid=%d&goto=lastpost' % self.threadid)
    posts = self.thread_parser.read_thread(response.read())
    posts = posts[-26:]
    self.posts = {}
    alpha = ord('a') + len(posts)
    for post in posts:
      alpha -= 1
      self.posts[chr(alpha)] = post
    self.view.print_posts(posts)

  def post(self, message, quoteid):
    """post a message to the last read thread"""

    if quoteid != None:
      self.browser.open('http://forums.somethingawful.com/newreply.php?action=newreply&postid=%d' % (quoteid))
    else:
      self.browser.open('http://forums.somethingawful.com/newreply.php?action=newreply&threadid=%d' % (self.threadid))
    self.browser.select_form(predicate = lambda form: form.action == 'http://forums.somethingawful.com/newreply.php')
    self.browser['message'] += message
    self.browser.submit()
    print('posted, refreshing thread...')
    self.thread(None)

  def repl(self):
    """simple repl, could be a lot better"""
    
    while True:
      try: 
        command = raw_input('>')
        words = command.split()
        if (len(words) == 0):
          continue

        #forum request
        if words[0] == 'f':
          if (len(words) > 1):
            self.forum(int(words[1]))
          else:
            self.forum()

        #thread request
        elif words[0] == 't':
          if (len(words) > 1):
            self.thread(words[1])
          else:
            self.thread(None)

        #post to last thread
        elif words[0] == 'p':
            self.post(command[2:], None)

        #quote a post
        elif words[0] == 'q':
          if (len(words) == 1):
            print('quote which post?')
          elif self.posts.get(words[1]) != None:
            self.post(command[4:], self.posts[words[1]].id)
          else:
            print('no match for ['+words[1]+'] in: '+self.posts.keys())

        else:
          print('what?')

      #continue on exception unless ^D or ^C
      except (KeyboardInterrupt, EOFError):
        break
      except Exception:
        traceback.print_exc()

if __name__ == '__main__':
  p = Posteur()
  print(motd)
  while not p.login():
    print('login failed')
  p.repl()
