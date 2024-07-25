
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
import socket
import threading
from tkinter import filedialog as fd
from tkinter import messagebox
import time


HEADER_SIZE=10

class Chat:
    def __init__(self, master):
        self.master = master
        
        self.master.title("Socket Chat")
        self.master.geometry("+50+50")
        self.master.resizable(0, 0)
        
        self.emojis=["\U0001f649","\U0001F648","\U0001F923","\U0001f975",
                     "\U0001F601","\U0001F605","\U0001F602","\U0001f608",
                     "\U0001f970","\U0001f60D","\U0001f929","\U0001f61B",
                     "\U0001f911","\U0001f610","\U0001f612"]

        self.Recibo=False
        self.Envio=False
        self.Conectado=False


        # ---------------------- Socket --------------------------
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)


        # ------------------------ FRAMES -----------------------------
        frm1 = tk.LabelFrame(self.master, text="Conexion")
        frm2 = tk.Frame(self.master)
        frm3 = tk.LabelFrame(self.master, text="Enviar mensaje")
        frm1.pack(padx=5, pady=5, anchor=tk.W)
        frm2.pack(padx=5, pady=5, fill='y', expand=True)
        frm3.pack(padx=5, pady=5)

        # ------------------------ FRAME 1 ----------------------------
        self.lblUser = tk.Label(frm1, text="Nickname")
        self.lblIP= tk.Label(frm1, text="IP")
        self.lblPort= tk.Label(frm1, text="Port")
        self.InUser=tk.Entry(frm1)
        self.InIP=tk.Entry(frm1)
        self.InPort=tk.Entry(frm1)
        self.lblSpace = tk.Label(frm1, text="")
        self.btnConnect = ttk.Button(frm1, text="Conectar", width=16, command=self.conectar)
        self.lblUser.grid(row=0, column=0, padx=5, pady=5)
        self.InUser.grid(row=0, column=1, padx=5, pady=5)
        self.lblSpace.grid(row=0,column=2, padx=30, pady=5)
        self.btnConnect.grid(row=0, column=3, padx=5, pady=5)
        self.lblIP.grid(row=1,column=0, padx=5, pady=5)
        self.InIP.grid(row=1,column=1, padx=5, pady=5)
        self.lblPort.grid(row=2,column=0, padx=5, pady=5)
        self.InPort.grid(row=2,column=1, padx=5, pady=5)

        # ------------------------ FRAME 2 ---------------------------
        self.txtChat = ScrolledText(frm2, height=25, width=50, wrap=tk.WORD, state='disabled')
        self.txtChat.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        # ------------------------ FRAME 3 --------------------------
        self.lblText = tk.Label(frm3, text="Texto:")
        self.inText = tk.Entry(frm3, width=35, state='disabled')
        self.btnSend = ttk.Button(frm3, text="Enviar", width=12, state='disabled')
        self.btnImg = ttk.Combobox(frm3, width=3, state="disabled", values=self.emojis)

        self.lblText.grid(row=0, column=0, padx=5, pady=5)
        self.inText.grid(row=0, column=1, padx=5, pady=5)
        self.btnSend.grid(row=0, column=2, padx=5, pady=5)
        self.btnImg.grid(row=0,column=3, padx=5,pady=5)

        # --------------------------- StatusBar -----------------------
        self.statusBar = tk.Label(self.master, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusBar.pack(side=tk.BOTTOM, fill=tk.X)

        # ------------- Control del boton "X" de la ventana -----------
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar)
        #----------------Evento Enter----------------------------------
        self.inText.bind("<Return>",self.enter)

        self.btnImg.bind("<<ComboboxSelected>>",self.Emoji)

    def enter(self,event):
        self.enviar()

    def Emoji(self, event):
        self.inText.insert("end",self.btnImg.get())
        pass

    def enviar(self):
        try:
            strData =self.inText.get()
            tiempo=time.strftime("%I:%M:%S %p", time.localtime())
            self.Envio=True
            tilde=['á','í','é','ó','ú','Á','É','Í','Ó','Ú']
            cuentaEmo=0
            cuentaTilde=0
            for i in strData:
                if i in self.emojis:
                    cuentaEmo+=1
                elif i in tilde:
                    cuentaTilde+=1

            if strData.isalnum()==True:
                mensaje=f"{self.usuario}-{tiempo}: {strData}"
                data_len = len(mensaje)+cuentaTilde
                self.sock.send(f"{data_len:<{HEADER_SIZE}}{mensaje}".encode('utf-8'))
                self.inText.delete(0,"end")

            elif strData.isspace()==True or strData=="":
                pass

            else:
                mensaje=f"{self.usuario}-{tiempo}: {strData}"
                data_len = len(mensaje)+1+cuentaTilde+3*(cuentaEmo)
                self.sock.send(f"{data_len:<{HEADER_SIZE}}{mensaje}".encode('utf-8'))
                self.inText.delete(0,"end")
                pass

        except:
            pass

    def recibir(self):

        try:

            while True:
                data_header=self.sock.recv(HEADER_SIZE)

                if not data_header:
                    break
                else:
                    data=self.sock.recv(int(data_header))
                    self.txtChat.config(state="normal")

                    if data.decode("utf-8").split("-")[0]==self.usuario:
                        self.txtChat.insert(tk.INSERT,data.decode("utf-8")+"\n","blue")
                        self.txtChat.tag_config("blue",foreground='blue')

                    else:
                        self.txtChat.insert(tk.INSERT,data.decode("utf-8")+"\n","#f50057")
                        self.txtChat.tag_config("#f50057",foreground='#f50057')
                        self.Recibo=True
                    self.txtChat.config(state="disabled")
                    self.txtChat.see(tk.END)

        except:
            pass
    def conectar(self):
        if len(self.InIP.get())==0 or len(self.InPort.get())==0 or len(self.InUser.get())==0:
            messagebox.showwarning("Warning","Complete todos los campos")

        else:
            try:
                self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.sock.connect((self.InIP.get(),int(self.InPort.get())))
                #self.sock.connect(("127.0.0.1",5000))
                threading.Thread(target=self.recibir, daemon=True).start()
                threading.Thread(target=self.Status, daemon=True).start()
                if len(self.InUser.get())==0:
                    self.usuario="User"
                else:
                    self.usuario=self.InUser.get()

                self.btnConnect.config(text="Desconectar",command=self.desconectar)
                self.btnImg.config(state="normal")
                self.btnSend.config(state="normal",command=self.enviar)
                self.inText.config(state="normal")
                self.InUser.config(state="disabled")
                self.InPort.config(state="disabled")
                self.InIP.config(state="disabled")
                self.Conectado=True


            except:
                messagebox.showerror("Error de conexion", f"No pudo conectarse a la dirección {self.InIP.get()} \n que está en el puerto {self.InPort.get()} \n Ya jalaste")
                pass


    def desconectar(self):

        self.InUser.config(state="normal")
        self.InPort.config(state="normal")
        self.InIP.config(state="normal")
        self.inText.config(state="disabled")
        self.btnSend.config(state="disabled")
        self.btnImg.config(state="normal")
        self.btnImg.config(state="disabled")
        self.inText.config(state="disabled")
        self.btnConnect.config(text="Conectar",command=self.conectar)
        self.sock.send(f"{6:<{HEADER_SIZE}}FINISH".encode('utf-8'))


    def cerrar(self):
        try:
            self.desconectar()
        except:
            pass

        self.master.destroy()

    def Status (self):
        while True:
            if self.Recibo:
                self.statusBar.config(text="Recibiendo mensaje")
                time.sleep(1)
                self.statusBar.config(text="")
                self.Recibo=False
            if self.Envio:
                self.statusBar.config(text="Enviando mensaje")
                time.sleep(1)
                self.statusBar.config(text="")
                self.Envio=False
            if self.Conectado:
                self.statusBar.config(text="Conectando...")
                time.sleep(1)
                self.statusBar.config(text="")
                self.Conectado=False
        pass


root = tk.Tk()
app = Chat(root)
root.mainloop()