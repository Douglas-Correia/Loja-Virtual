//Questão 4: Explique o conceito de "escopo" em JavaScript e como ele se relaciona com variáveis declaradas com var, let e const.

var variavelGlobal = 'Escopo Global'; 
const elementoGlobal = document.createElement('p');
elementoGlobal.innerText = variavelGlobal;
document.body.appendChild(elementoGlobal);

const cpf = 54365467; // Não posso trocar esse valor
const elementoConst = document.createElement('p');
elementoConst.innerText = cpf;
document.body.appendChild(elementoConst);

function funcao(){
    let variavelGlobal = 'Escopo Local'; // Essa variavél é diferente da var

    const elementoLocal = document.createElement('p');
    elementoLocal.innerText = variavelGlobal;

    document.body.appendChild(elementoLocal);
}

funcao();