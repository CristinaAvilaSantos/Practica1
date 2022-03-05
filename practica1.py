from multiprocessing import Process, BoundedSemaphore, Semaphore, Lock, current_process, Value, Array
from time import sleep
from random import randint, random

N = 100
K = 10
NPROD = 3



def delay(factor = 3):
    sleep(random()/factor)
    
def ord_insercion(lista, dato):
    todo_ceros = True
    for i in range(len(lista)):
        if lista[i] != 0: 
            todo_ceros = False
        else:
            lista[0] = dato
            break
        if dato <= lista[i] and todo_ceros == False:  
            j = i+1
            while j > 0 and dato < lista[j-1]:
                for k in range(len(lista)-1, i, -1):
                    lista[k] = lista[k-1]
                lista[j] = lista[j-1]
                j -= 1
                lista[j] = dato  
            break
        elif dato > lista[i] and lista[i+1] == 0:
            lista[i+1] = dato
            break
    print(lista) 
    return lista
   
   
def produce_values(producidos, data, mutex):
    mutex.acquire()
    try:
        delay(5)
        i = 1
        x = 0
        while i > 0 and i < K:
            if producidos[i] == 0:
                producidos[i] = data + randint(1, 20)
                x = producidos[i]
                break
            i += 1
    finally:
        mutex.release()
    return x
        
def get_minvalues(producidos, mutex):
    mutex.acquire()
    try:
        menor = 10**6
        pmenor = -1
        for i in range(K):
            if producidos[i] > 0:
                if producidos[i] < menor:
                    pmenor = i
                    menor = producidos[i]
        if pmenor != -1 :
           menor = producidos[pmenor]
           producidos[pmenor] = 0
        else: 
           menor = -1
           print(f"{current_process().name} = -1")
    finally:
        mutex.release()
    return menor
            
            
def producer(producidos, empty, non_empty, mutex):
    x = 0
    for v in range(N):
        print (f"{current_process().name} produciendo")
        delay(6)
        empty.acquire()
        x = produce_values(producidos, x, mutex)
        print(list(producidos))       
        print(f"Productor {current_process().name} ha producido", x,v)
        delay(10)
        non_empty.release()  
 
def consumer(producidos, resultados, empty, non_empty, mutex):
    print ('entra en consumer')
    for v in range(N):
        non_empty.acquire()
        print ('Desalmacenando el menor')
        dato = get_minvalues(producidos, mutex)
        empty.release()
        print (f"colocando {dato}")
        resultados = ord_insercion(list(resultados), dato)
        print(f"lista final=", list(resultados))


def main():
    resultados = Array('i', N)
    producidos = Array('i', K)
    index = Value('i', 0)
    menor = producidos[0]
   
    for i in range(K-1):
        producidos[i]=producidos[i+1]
        
    non_empty = Semaphore(0)
    empty = BoundedSemaphore(K)
    mutex = Lock()

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(producidos, empty, non_empty, mutex))
                for i in range(NPROD) ]

    conslst = [Process(target=consumer,
                      name=f"cons_{i}",
                      args=(producidos, resultados, empty, non_empty, mutex)) ]
          
    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()

if __name__ == '__main__':
    main()

