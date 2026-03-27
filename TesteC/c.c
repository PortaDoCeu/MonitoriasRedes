#include <stdio.h>

typedef struct {
    int aula;
    char conteudo[20];
    int valor = 0;
} Aula;

void alterarValor(Aula *aula){
    if(aula->valor<10){
        aula->valor += 1;
    }
}

int main(){
    Aula aula1;
    aula1.aula = 0;
    aula1.conteudo = "C";
    printf("Aula = %d, Valor = %d", aula1.aula, aula1.valor);
}