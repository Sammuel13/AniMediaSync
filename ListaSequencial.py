from random import shuffle

class PosicaoInvalidaException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class ValorInexistenteException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class Lista:
    def __init__(self):
        self.__dado = []

    def estaVazia(self):
        return True if len(self.__dado)==0 else False

    def tamanho(self):
        return len(self.__dado)

    def elemento(self, posicao):
        try:
            assert posicao > 0
            return self.__dado[posicao-1]
        except IndexError:
            raise PosicaoInvalidaException(f'Posicao {posicao} invalida para a Lista')
        except TypeError:
            raise PosicaoInvalidaException(f'O tipo de dado para posicao não é um número inteiro')
        except AssertionError:
            raise PosicaoInvalidaException(f'A posicao não pode ser um número negativo')
        except:
            raise

    def modificar(self, posicao, valor):
        try:
            assert posicao > 0
            self.__dado[posicao-1] = valor
        except IndexError:
            raise PosicaoInvalidaException(f'Posicao {posicao} invalida para a Lista')
        except TypeError:
            raise PosicaoInvalidaException(f'O tipo de dado para posicao não é um número inteiro')
        except AssertionError:
            raise PosicaoInvalidaException(f'A posicao não pode ser um número negativo')
        except:
            raise

    def busca(self, valor):
        try:
            return self.__dado.index(valor) + 1
        except ValueError:
            raise ValorInexistenteException(f'O valor {valor} não está armazenado na lista')
        except:
            raise

    def inserir(self, valor, posicao=None):
        if not posicao: posicao = self.tamanho()
        
        try:
            assert posicao > 0
            self.__dado.insert(posicao-1,valor)
        except IndexError:
            raise PosicaoInvalidaException(f'Posicao {posicao} invalida para a Lista')
        except TypeError:
            raise PosicaoInvalidaException(f'O tipo de dado para posicao não é um número inteiro')
        except AssertionError:
            raise PosicaoInvalidaException(f'A posicao não pode ser um número negativo')
        except:
            raise

    def remover(self, posicao):
        try:
            assert posicao > 0
            if (len(self.__dado)==0):
                raise PosicaoInvalidaException(f'A lista está vazia! Não é possivel remover elementos')
            valor = self.__dado[posicao-1]
            del self.__dado[posicao-1]
            return valor
        except IndexError:
            raise PosicaoInvalidaException(f'Posicao {posicao} invalida para remoção')
        except TypeError:
            raise PosicaoInvalidaException(f'O tipo de dado para posicao não é um número inteiro')
        except AssertionError:
            raise PosicaoInvalidaException(f'A posicao não pode ser um número negativo')
        except:
            raise

    def imprimir(self):
        print('Lista: ',end='')
        print(self.__dado)

    def __str__(self):
        return self.__dado.__str__()

    # new methods
    def clear(self):
        if len(self.__dado)==0: # estaVazia()
            raise
        self.__dado.clear()

    def shuffle(self):
        if len(self.__dado)<1:
            raise
        shuffle(self.__dado)

    def next(self):
        if len(self.__dado)<1:
            raise
        return self.__dado.pop(0)

    def removeDupps(self):
        toRemove = []
        self.__dado.reverse() # to remove the newers one first
        for i in range(len(self.__dado)-1): # tamanho
            if self.__dado[i] in self.__dado[i+1:]:
                toRemove.append(i)
        toRemove.reverse()
        for j in toRemove:
            self.__dado.pop(j)
        return self.__dado.reverse()
    
    def realocate(self, videofrom, videoto):
        auxiliar_node = self.__dado.pop(videofrom-1) # elemento() remover()
        self.__dado.insert(videoto-1,auxiliar_node) # inserir()

# TESTING ZONE
# teste = Lista()
# # [1, 2, 2, 3, 5, 4, 1, 6, 2, 7, 8]
# teste.inserir(1,1)
# teste.inserir(2,2)
# teste.inserir(3,2)
# teste.inserir(4,3)
# teste.inserir(5,5)  #TODO improved the inserir to not ask for a index
# teste.inserir(6,4)  #TODO insert more videos at once "youtube... .../video.mp4 youtube..."
# teste.inserir(7,1) 
# teste.inserir(8,6)
# teste.inserir(9,2)
# teste.inserir(10,7)
# teste.inserir(11,8)
# print(teste)
# teste.removeDupps()
# print(teste)
# teste.realocate(4,5)
# print(teste)
# teste.shuffle()
# print(teste)
# print(teste.next(),teste)