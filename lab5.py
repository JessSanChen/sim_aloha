# MIT 6.02 Lab 5 Check-In: http://web.mit.edu/6.02/www/f2010/handouts/labs/lab5.py

##################################################
##
## Code to submit task to server.  Do not change.
##
##################################################

import tkinter as Tkinter


class Dialog(Tkinter.Toplevel):
    def __init__(self, parent, title=None):
        Tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title: self.title(title)
        self.parent = parent

        body = Tkinter.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):
        return None

    # add standard button box
    def buttonbox(self):
        box = Tkinter.Frame(self)
        w = Tkinter.Button(box, text="Ok", width=10, command=self.ok, default=Tkinter.ACTIVE)
        w.pack(side=Tkinter.LEFT, padx=5, pady=5)
        box.pack()

    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    # command hooks
    def validate(self):
        return 1  # override

    def apply(self):
        pass  # override


# ask user for Athena username and MIT ID
class SubmitDialog(Dialog):
    def __init__(self, parent, error=None, title=None):
        self.error = error
        self.athena_name = None
        self.mit_id = None
        Dialog.__init__(self, parent, title=title)

    def body(self, master):
        row = 0
        if self.error:
            l = Tkinter.Label(master, text=self.error,
                              anchor=Tkinter.W, justify=Tkinter.LEFT, fg="red")
            l.grid(row=row, sticky=Tkinter.W, columnspan=2)
            row += 1
        Tkinter.Label(master, text="Athena username:").grid(row=row, sticky=Tkinter.E)
        self.e1 = Tkinter.Entry(master)
        self.e1.grid(row=row, column=1)

        row += 1
        Tkinter.Label(master, text="MIT ID:").grid(row=row, sticky=Tkinter.E)
        self.e2 = Tkinter.Entry(master)
        self.e2.grid(row=row, column=1)

        return self.e1  # initial focus

    # add standard button box
    def buttonbox(self):
        box = Tkinter.Frame(self)
        w = Tkinter.Button(box, text="Submit", width=10, command=self.ok,
                           default=Tkinter.ACTIVE)
        w.pack(side=Tkinter.LEFT, padx=5, pady=5)
        w = Tkinter.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=Tkinter.LEFT, padx=5, pady=5)
        box.pack()

    def apply(self):
        self.athena_name = self.e1.get()
        self.mit_id = self.e2.get()


# Let user know what server said
class MessageDialog(Dialog):
    def __init__(self, parent, message='', title=None):
        self.message = message
        Dialog.__init__(self, parent, title=title)

    def body(self, master):
        l = Tkinter.Label(master, text=self.message, anchor=Tkinter.W, justify=Tkinter.LEFT)
        l.grid(row=0)


# return contents of file as a string
def file_contents(fname):
    # use universal mode to ensure cross-platform consistency in hash
    f = open(fname, 'U')
    result = f.read()
    f.close()
    return result


import hashlib


def digest(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


# if verify(f) indicates points have been earned, submit results
# to server if requested to do so
import inspect, os, urllib, urllib.request as urllib2


def checkoff(f, task='???', submit=True):
    tasks = ('L5_1', 'L5_2', 'L5_3', 'L5_4', 'L5_5')
    if task in tasks:
        points = 'tba'
    else:
        raise ValueError("task must be one of %s" % ", ".join(tasks))

    if submit and points:
        root = Tkinter.Tk();  # root.withdraw()
        error = None
        while submit:
            sd = SubmitDialog(root, error=error, title="Submit Task %s?" % task)
            if sd.athena_name:
                if isinstance(f, str):
                    fname = os.path.abspath(f)
                else:
                    fname = os.path.abspath(inspect.getsourcefile(f))
                post = {
                    'user': sd.athena_name,
                    'id': sd.mit_id,
                    'task': task,
                    'digest': digest(file_contents(os.path.abspath(inspect.getsourcefile(checkoff)))),
                    'points': points,
                    'filename': fname,
                    'file': file_contents(fname)
                }
                try:
                    response = urllib2.urlopen('http://scripts.mit.edu/~6.02/currentsemester/submit_task.cgi',
                                               urllib.urlencode(post)).read()
                except Exception as e:
                    response = 'Error\n' + str(e)
                if response.startswith('Error\n'):
                    error = response[6:]
                else:
                    MessageDialog(root, message=response, title='Submission response')
                    break
            else:
                break

        root.destroy()