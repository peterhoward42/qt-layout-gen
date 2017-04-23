import hashlib

from PySide.QtCore import QObject
from PySide.QtGui import QApplication, qApp, QCloseEvent
from qtlayoutbuilder.api.build import build_from_multi_line_string


class CancellableRunner(QObject):
    """
    Runs long-running tasks, in the main GUI thread without blocking the event
    loop, as multiple, repeated calls to your provided mini-task function. 
    It triggers the event loop to process any pending events from the GUI after 
    each call to the mini-function.
    
    Your mini-task callback should:
    - Complete fairly quickly.
    - Signal the whole-task completion by returning True (complete) or False 
     (incomplete)
     
    The arguments passed to your mini-task callback are:
    - A count that starts at zero and increments on each call.
    - The object you provide as user_data to the constructor. This is a good
      place to preserve state across calls.
    
    You cancel a running long-running task by sending it a QCloseEvent. E.g.
    
        def some_button_click_handler():
            qApp.instance().notify(my_cancellable_runner, QCloseEvent())
    """

    def __init__(self, mini_task_callback, user_data):
        super(CancellableRunner, self).__init__()
        self._callback = mini_task_callback
        self._user_data = user_data
        self._cancelled = False

    def run(self):
        finished = False
        count = 0
        while not finished:
            if self._cancelled:
                self._cancelled = False
                break
            finished = self._callback(count, self._user_data)
            count += 1
            qApp.instance().processEvents()

    def event(self, *args, **kwargs):
        # Handle the close event.
        self._cancelled = True
        return True

def do_small_bit_of_operation(count, my_data):
    if count > 30:
        return True # done
    LOTS = 100000
    v = 0.0
    while v < LOTS:
        v += 1
        hashlib.sha256(b'foo').hexdigest()
    return False # Not finished

runner = CancellableRunner(do_small_bit_of_operation, 42)

def launch():
    print 'launching'
    runner.run()
    print 'done'

def cancel():
    cancel_evt = QCloseEvent()
    qApp.instance().notify(runner, cancel_evt)

def main():
    QApplication([])
    layouts_created = build_from_multi_line_string("""
            page            QWidget
              layout        QVBoxLayout
                launch_btn  QPushButton(launch)
                cancel_btn  QPushButton(cancel)
        """)
    launch_btn = layouts_created.get_element('page.layout.launch_btn')
    cancel_btn = layouts_created.get_element('page.layout.cancel_btn')

    launch_btn.clicked.connect(launch)
    cancel_btn.clicked.connect(cancel)

    page = layouts_created.get_element('page')

    page.show()
    qApp.exec_()

main()

