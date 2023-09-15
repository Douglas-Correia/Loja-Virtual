// Questão 2: Escreva um código JavaScript que verifica se um número é par ou ímpar e exibe uma mensagem correspondente.

function impar_par(num){
    if(num % 2 == 0){
        document.body.innerText = `O ${num} é par.`;
    }
    else{
        document.body.innerText = `O ${num} é impar.`;
    }
}

impar_par(6);
console.log(impar_par);