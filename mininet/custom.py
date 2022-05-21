import os
os.environ['TZ'] = 'Asia/Shanghai'
import datetime
import csv
from math import fabs
from random import randint,uniform


class StatusInfo:
    def __init__(self, bandWidth, clients_num, datagram_size, datagram_num, window_size=None):
        self._bw = bandWidth
        self._cn = clients_num
        self._dg = datagram_size
        self._dg_num = datagram_num
        self._wd_size = window_size

    def getBandWidth(self):
        return self._bw
    
    def getClientsNum(self):
        return self._cn

    def getWindowSize(self):
        return self._wd_size

    def getDatagramSize(self):
        return self._dg

    def getDatagramNum(self):
        return self._dg_num

    def formServerCmd(self):
        cmd = ''
        if self.getWindowSize() is not None:
            cmd +=  ' -w %d '%(self.getWindowSize()) 
        return cmd

    def formClientCmd(self):
        # + ' -n %d '%(self.getDatagramNum()) 
        cmd = ''
        if self.getClientsNum() is not None:
            cmd += ' -P %d '%(self.getClientsNum())
        if self.getBandWidth() is not None:
            cmd += ' -b %s '%(self.getBandWidth()) 
        if self.getDatagramSize() is not None:
            cmd +=  '-l %d '%(self.getDatagramSize()) 
        
        return cmd

# enum: server status
NORMAL = 0
DISK_ERROR = 1
NETWORK_ERROR = 2
SERVER_ERROR = 3
BW_ERROR = 4
CONCURRENCY_ERROR = 5

# param of normal status
Base_client_num = 3
Base_datagram_size = 1000
Base_datagram_num = 10 #invalid param
#datagrams = bandwith * datagram_size
statusInfo_dict = {
    # no error
    ## tested
    NORMAL :            StatusInfo( bandWidth='3000K', 
                                    clients_num=Base_client_num,      
                                    datagram_size=Base_datagram_size*30, 
                                    datagram_num=Base_datagram_num),
    # disk full
    ## tested
    DISK_ERROR :        StatusInfo( bandWidth='3000K', 
                                    clients_num=Base_client_num,    
                                    datagram_size=Base_datagram_size*30, 
                                    datagram_num=Base_datagram_num,
                                    window_size=Base_datagram_size//20), 
    # network broken
    ## tested
    NETWORK_ERROR :     StatusInfo( bandWidth='10000M',  
                                    clients_num=Base_client_num,      
                                    datagram_size=Base_datagram_size*50, 
                                    datagram_num=Base_datagram_num), 
    # server down
    ## tested
    SERVER_ERROR :      StatusInfo( bandWidth='1000M', 
                                    clients_num=Base_client_num,        
                                    datagram_size=Base_datagram_size, 
                                    datagram_num=Base_datagram_num), 
    # bandwidth broken
    BW_ERROR :          StatusInfo( bandWidth='100K',
                                    clients_num=Base_client_num,     
                                    datagram_size=Base_datagram_size, 
                                    datagram_num=Base_datagram_num),
    # too many clients
    CONCURRENCY_ERROR : StatusInfo( bandWidth='1M', 
                                    clients_num=Base_client_num*10,    
                                    datagram_size=Base_datagram_size, 
                                    datagram_num=Base_datagram_num)
}

def translate_status(status):
    status_str = {
        NORMAL : 'NORMAL',
        DISK_ERROR : 'DISK_ERROR',
        NETWORK_ERROR : 'NETWORK_ERROR',
        SERVER_ERROR : 'SERVER_ERROR',
        BW_ERROR : 'BW_ERROR',
        CONCURRENCY_ERROR : 'CONCURRENCY_ERROR'
    }
    return status_str[status]

def csv_write(data_list, path):
    csv_writer= csv.writer(open(path,'w'))
    for data in data_list:
        csv_writer.writerow(data)

def form_timestamp(base_time,sec):
    next_sec = base_time + datetime.timedelta(seconds=sec)
    return next_sec.strftime('%Y%m%d%H%M%S') 

def generate_OOD_data():
    start_time = datetime.datetime.now()
    data_list = []
    for secs in range(0,300):
        timestamp = form_timestamp(start_time, secs)
        server_ip = '10.0.0.1'
        server_port = '5001'
        client_ip = '10.0.0.2'
        client_port = randint(10000,99999)
        thread_ID = 1
        interval_sec = "%d.0-%d.0"%(secs,secs+1)
        transfer_bits = randint(-50000, 50000)
        bandwidth_bits = transfer_bits*8
        jitter_ms = '%.3f' % (float(randint(-100, 100))/100)
        cnt_datagrams = randint(-100, 100)
        while cnt_datagrams == 0:
            cnt_datagrams = randint(-100, 100)
        cnt_missingdatagrams = randint(-fabs(cnt_datagrams), fabs(cnt_datagrams))
        cnt_errorrate = 100*cnt_missingdatagrams/cnt_datagrams
        cnt_outoforders = randint(-fabs(cnt_datagrams/2), fabs(cnt_datagrams/2))

        data_list.append(
            (
                timestamp, server_ip,server_port, 
                client_ip, client_port, thread_ID, 
                interval_sec, transfer_bits, bandwidth_bits, 
                jitter_ms, cnt_missingdatagrams, cnt_datagrams, 
                cnt_errorrate,cnt_outoforders
            )
        )
    
    target_dir = '/home/mininet/log/OOD_log_csv'
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    path = os.path.join(target_dir, 'OOD_server.log')
    csv_write(data_list, path)

if __name__ == '__main__':
    generate_OOD_data()