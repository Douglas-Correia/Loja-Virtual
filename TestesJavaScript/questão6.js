// Questão 6: Explique o que é uma "função de callback" em JavaScript e forneça um exemplo de uso prático.

const btn = document.querySelector("#btn");
const pTexto = document.querySelector("#texto");

btn.addEventListener('click', ()=>{
    const texto = 'Olá, a função de callback é exatamente está função que estou dentro, pois ela serve para ser adicionada a um evento, ou se somente for adicionada para ser executada em algum mento só do código.';

    pTexto.innerHTML = texto;
})