#!/usr/bin/python
import os
import sys
import threading

# Globals
output = '/home/mininet/output'




def main():
    tm_file = sys.argv[1]
    os.system('pkill -9 iperf3')
    os.system('rm -rf ' + output)
    os.system('mkdir ' + output)
    threads = []
    for i,line in enumerate(open(tm_file)):
        src = line.split()[0]
        dst = line.split()[1].strip()
        t = threading.Thread(target=gen_flow, args=(src,dst, i))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

    os.system('pkill -9 iperf3')
    print '*** Terminated iperf3 processes.'
    print 'Flows: ' + str(i)
    calculate_total_throughput(i + 1)


def gen_flow(src, dst, i):
    print src, dst, i
    src_ip = '10.0.0.' + src
    dst_ip = '10.0.0.' + dst
    print src_ip + ' --> ' + dst_ip
    cmd = 'iperf3 -s -D -p ' + str(20000 + i)
    exec_ssh(dst_ip, cmd)
    cmd = 'iperf3 -c ' + dst_ip + ' -p ' + str(20000 + i) + ' -B ' + src_ip + ' -i 0 --cport ' + str(30000 + i) + ' > ' + output + '/flow' + str(i) 
    #print cmd
    exec_ssh(src_ip, cmd)
        


def exec_ssh(host, cmd):
    os.system('ssh  -o "StrictHostKeyChecking no" ' + host + ' " ' + cmd +  ' "')
    
def calculate_total_throughput(num_flows):
    s = 0
    print '\nOutput:\n-------'
    for i in range(num_flows):
        outfile = output + '/flow' + str(i)
        #print outfile
        t = read_throughput(outfile)
        if t < 0: 
            print 'Flow ' + str(i) + ': ---'
        else:
            print 'Flow ' + str(i) + ': ' + str(t) + ' Mbits/sec'
            s += t
    print '\nTotal: ' + str(s) + ' Mbits/sec\n'
        
def read_throughput(fname):
    mbps  = 0
    for line in open(fname):
        tokens = line.split()
        for i,t in enumerate(tokens):
            if t == 'Gbits/sec':
                return float(tokens[i - 1]) * 1024

            elif t == 'Mbits/sec':
                return float(tokens[i - 1])
            elif t == 'Kbits/sec':
                return float(tokens[i - 1]) / 1024
    return -1


if __name__ == "__main__":
    main()
