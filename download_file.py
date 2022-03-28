import socket
import threading

IP = socket.gethostbyname(socket.gethostname())

class DownloadFile:
    def __init__(self):
        self.sequence = 0

    def start_download(self,address ,name):
        self.address = address
        self.name =  name
        self.udp = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
        self.udp.bind((IP , 0))
        threading.Thread(target=self.download).start()


    #stop and wait
    def download(self):

        try:
            file = open(f'data/{self.name}','rb')
        except Exception as e:
            print(e)
            return


        packets = []
        data_len = 0
        while True :
            data = file.read(500)
            if not data:
                break
            packets.append(data)
            data_len += len(data)



        self.udp.settimeout(2)
        while self.sequence < data_len:

            self.udp.send(packets[0])


            current_seq = self.sequence
            while current_seq == self.sequence:
               # try:

                   data ,address =  self.udp.recv(1024)
                    #if the packet is acked
                       # self.sequence += len(packets.pop(0))
                #exec Exception as e:
                 #'sending again'



        #print('dowenload done')




