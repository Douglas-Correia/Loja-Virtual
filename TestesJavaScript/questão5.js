// Questão 5: Escreva um código JavaScript que cria um array de números inteiros, itera sobre o array e exibe a soma de todos os números pares.

const array = [5, 6, 3, 4, 7, 9, 2, 12, 8];
let soma = 0;

for (const item of array) {
    if (item % 2 === 0) {
        soma += item;
    }
}

document.body.innerText = `A soma dos números pares é ${soma}`;