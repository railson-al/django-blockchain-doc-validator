const DocumentRegistry = artifacts.require("DocumentRegistry");

contract("DocumentRegistry", accounts => {
  it("deve registrar um documento", async () => {
    const instance = await DocumentRegistry.deployed();
    const documentHash = web3.utils.sha3("documento_exemplo");

    // Chama a função para registrar o documento
    await instance.registerDocument(documentHash, { from: accounts[0] });

    // Verifica se o documento está registrado
    const isRegistered = await instance.verifyDocument(documentHash);
    assert.isTrue(isRegistered, "O documento não foi registrado corretamente.");
  });

  it("não deve registrar o mesmo documento duas vezes", async () => {
    const instance = await DocumentRegistry.deployed();
    const documentHash = web3.utils.sha3("documento_exemplo");

    try {
      // Tenta registrar o mesmo documento novamente
      await instance.registerDocument(documentHash, { from: accounts[0] });
      assert.fail("Deveria ter lançado um erro ao registrar o mesmo documento.");
    } catch (error) {
      assert.include(error.message, "Document already registered", "Erro esperado não ocorreu.");
    }
  });
});