import threading
import tkinter as tk
from tkinter import ttk
from har_download import ProxyManager
# from mouse_listener import MouseListener
from api_filter import ApiFilter
from api_analyser import ApiAnalyser
from systest_entity_generator import SystestEntityGenerator


class GUI(object):
  def __init__(self):
    self.har_download_object = None
    self.root = tk.Tk()
    # set the background colour of GUI window
    self.root.configure(background='light green')
    # set the title of GUI window
    self.root.title("RAW")
    # set the configuration of GUI window
    self.root.geometry("500x300")
    self.message = tk.Label(self.root, text="", bg="light green")
    # create a Form label
    self.pc_ip = tk.Label(self.root, text="PC IP", bg="light green")
    # create a Name label
    self.port = tk.Label(self.root, text="PORT", bg="light green")
    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .
    self.pc_ip.grid(row=0, column=0)
    self.port.grid(row=1, column=0)
    # create a text entry box
    # for typing the information
    self.pc_ip_field = tk.Entry(self.root)
    self.port_field = tk.Entry(self.root)
    # bind method of widget is used for
    # the binding the function with the events
    # whenever the enter key is pressed
    # then call the focus1 function
    self.pc_ip_field.bind("<Return>", self.focus1)
    # whenever the enter key is pressed
    # then call the focus2 function
    self.port_field.bind("<Return>", self.focus2)
    # grid method is used for placing
    # the widgets at respective positions
    # in table like structure .
    self.pc_ip_field.grid(row=0, column=1, ipadx="100")
    self.port_field.grid(row=1, column=1, ipadx="100")
    # create a Submit Button and place into the self.root window
    radio_options = tk.Frame(self.root)
    # set the background colour of GUI window
    radio_options.grid(row=2, column=1)

    self.test_case_value = tk.StringVar(self.root, "1")
    self.functional = tk.Radiobutton(radio_options, text="Functional",
                                     value="1",
                                     variable=self.test_case_value,
                                     background='light green')
    self.functional.grid(row=0, column=0)
    self.systemic = tk.Radiobutton(radio_options, text="Systemic", value="2",
                                   variable=self.test_case_value,
                                   background='light green')
    self.systemic.grid(row=0, column=1)
    self.locust = tk.Radiobutton(radio_options, text="Locust", value="3",
                                 variable=self.test_case_value,
                                 background='light green')
    self.locust.grid(row=0, column=2)
    button_options = tk.Frame(self.root, pady=5)
    button_options.grid(row=3, column=1)
    button_options.config(bg="light green")

    self.start_button = ttk.Button(button_options, text="Start",
                                   command=self.start)
    self.stop_button = ttk.Button(button_options, text="Stop",
                                  command=self.stop,
                                  )
    self.start_button.grid(row=0, column=0)
    self.stop_button.grid(row=0, column=1)
    self.message.grid(row=4, column=1)

    # start the GUI
    self.root.mainloop()
    # self.mouse_listener = MouseListener()
    # self.api_analyser = ApiAnalyser()

  def focus1(self, event):
    self.pc_ip_field.focus_set()

  def focus2(self, event):
    # set focus on the sem_field box
    self.port_field.focus_set()

  def clear(self):
    # clear the content of text entry box
    self.pc_ip_field.delete(0, tk.END)
    self.port_field.delete(0, tk.END)

  def start(self):
    print("Start Execution")
    self.message.config(text="")
    self.test_type = self.test_case_value.get()

    if (self.pc_ip_field.get() == "" and
        self.port_field.get() == ""):
      print ("Empty input")
      self.message.config(text="Please enter PC IP and Port")
    else:
      self.start_button.config(state="disabled")
      self.pc_ip_value = self.pc_ip_field.get()
      self.port_value = self.port_field.get()
      print("Test case {}".format(self.test_type))
      print("PC IP {}".format(self.pc_ip_value))
      print("Port {}".format(self.port_value))

      self.har_download_object = ProxyManager()
      self.download_thread = threading.Thread(
        target=self.har_download_object.sniff_api, args=(self.pc_ip_value,
                                                         self.port_value,))
      self.download_thread.start()
    # self.mouse_listener.start()
    # with self.mouse_listener.listener as listener:
    #   listener.join()

  def stop(self):
    print("stop Execution")
    self.stop_button.config(state="disabled")
    self.har_download_object.stop_sniffing()
    self.download_thread.join()
    file_location = self.har_download_object.har_file_name
    # self.mouse_listener.stop()
    self.api_filter = ApiFilter("{}.har".format(file_location),
                                self.pc_ip_value)
    filtered_api_list = self.api_filter.api_filter()
    self.api_analyser= ApiAnalyser(filtered_api_list)
    analysed_api_file_name = self.api_analyser.analyse_api()
    print analysed_api_file_name
    # pprint.pprint(analysed_api_list)
    if self.test_type == "1":
      # Call functional script generator
      print ("Functional test")
    elif self.test_type == "2":
      sys_generator = SystestEntityGenerator(analysed_api_file_name)
      sys_generator.get_data()
    else:
      print ("Config for locust is created : {}".format(analysed_api_file_name))

    self.start_button.config(state="normal")
    self.stop_button.config(state="normal")
    # set focus on the name_field box
    self.pc_ip_field.focus_set()
    self.message.config(text="Success")
    # call the clear() function
    self.clear()


gui = GUI()
