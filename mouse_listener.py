import datetime
import pynput
from pynput.mouse import Listener


class MouseListener(object):
  def __init__(self):
    self.time_stamp = []
    self.listener = None

  def on_click(self, x, y, button, pressed):
    if button == pynput.mouse.Button.left:
      print("OK {}{}{}".format(x, y, button))
      dt = datetime.datetime.now()
      unix_ts_utc = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
      self.time_stamp.append(int(unix_ts_utc))

  def stop(self):
    self.listener.stop()

  def start(self):
    self.listener = Listener(on_click=self.on_click)
