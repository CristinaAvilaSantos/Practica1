from multiprocessing import Process, Semaphore, Lock, Value, Array
from time import sleep
from random import randint, random

N = 4
NPROD = 2
K = NPROD * 4


def delay(factor = 3):
    sleep(random()/factor)

def anadir(resultados, v, mutex, index):
    mutex.acquire()
    try:
        resultados[index.value] = v
        index.value += 1
    finally:
        mutex.release()
                        

def add(producidos, v, mutex, pid):
    mutex.acquire()
    try:
        producidos[pid] = v
    finally:
        mutex.release()
                    
                    
def get_minvalues(producidos, mutex):
    mutex.acquire()
    try:
        menor = 10**6
        pmenor = -1
        i = 1
        for i in range(NPROD):
            if (producidos[i] !=1) and (producidos[i] < menor):
                pmenor = i
                menor = producidos[i]
    finally:
        mutex.release()
    return pmenor
            
            
def producer(l, producidos, empty, nonEmpty, mutex, pid):
    x = 0
    for i in range(l):
        print (f"productor {pid} produciendo")
        delay(6)
        empty.acquire()
        x += randint(0,20)
        add(producidos,x, mutex, pid)
        print(f"Productor {pid} ha producido", x)
        delay(10)
        nonEmpty.release()  
    empty.acquire()
    producidos[pid] = -1
    nonEmpty.release()
 
def consumer(producidos, resultados, empty, non_empty, mutex, index):
    print ('entra en consumer')
    for i in range(NPROD):
        non_empty[i].acquire()
    while (-1) in resultados:
        minP = get_minvalues(producidos, mutex)
        anadir(resultados, producidos[minP], mutex, index)
        print(resultados[:])
        empty[minP].release()
        print (f"consumer  consumiendo {producidos[minP]}")
        non_empty[minP].acquire()


def main():
    resultados = Array('i', K)
    producidos = Array('i', NPROD)
    index = Value('i', 0)
    
    for i in range(NPROD):
        producidos[i] = -1
   
    for i in range(K):
        resultados[i] = -1
        
    non_empty = []			
    empty = []				
    mutex = Lock()
    
    for i in range(NPROD):
        empty.append(Semaphore())
        non_empty.append(Semaphore())

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(N, producidos, empty[i], non_empty[i], mutex, i))
                for i in range(NPROD) ]

    conslst = [Process(target=consumer,
                      name=f"cons_{i}",
                      args=(producidos, resultados, empty, non_empty, mutex, index)) ]
          
    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()

if __name__ == '__main__':
    main()

