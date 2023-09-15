// Questão 3: Como você define uma função em JavaScript e qual é a diferença entre uma função nomeada e uma função anônima?

function somar(num1, num2){
    const soma = num1 + num2;
    return soma
}

somar(5, 5);

document.querySelector("#mostrar-texto").addEventListener('click', () => {
    let textoHtml = document.querySelector("#texto");
    const texto = 'Hello, World!';

    textoHtml.innerHTML = texto;
});

// A diferença da função anômima é que você pode assimilar de forma mais prática associando a um botão sem precisar declarar o nome da função.