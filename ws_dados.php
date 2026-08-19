<?php
//erros
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Origin: *"); // Permite requisições de outros domínios/front-end
header("Access-Control-Allow-Methods: GET");
//parametros para o get do banco de dados
//url: https://royalblue-turtle-204261.hostingersite.com/ws_dados.php?tipoDado=J&credential=123456&referenciaInicial=2023-01-01&referenciaFinal=2023-12-31
$_GET['tipoDado'] = isset($_GET['tipoDado']) ? $_GET['tipoDado'] : 'J';//json
$_GET['credential'] = isset($_GET['credential']) ? $_GET['credential'] : '';
$_GET['referenciaInicial'] = isset($_GET['referenciaInicial']) ? $_GET['referenciaInicial'] : '';
$_GET['referenciaFinal'] = isset($_GET['referenciaFinal']) ? $_GET['referenciaFinal'] : '';

//parâmetros de conexão com o banco de dados
$host = 'localhost';
$username = 'XXXXXXXXXX';
$password = 'XXXXXXXXXX';
$db_name = 'XXXXXXXXXX';

//conexão com o banco de dados
try {
    // Instancia o PDO
    $pdo = new PDO("mysql:host={$host};dbname={$db_name};charset=utf8", $username, $password);
    
    // Configura o PDO para lançar exceções em caso de erros
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // Configura para retornar os dados como array associativo por padrão
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

} catch (PDOException $e) {
    // Retorna erro 500 se não conseguir conectar
    http_response_code(500);
    echo json_encode([
        "status" => "error",
        "message" => "Erro na conexão com o banco de dados: " . $e->getMessage()
    ]);
    exit;
}

// 3. Captura dos Parâmetros via GET (com valores padrão/segurança)
$loja_id = isset($_GET['loja_id']) ? intval($_GET['loja_id']) : null;
$faixa_etaria = isset($_GET['faixa_etaria']) ? trim($_GET['faixa_etaria']) : null;
$regiao = isset($_GET['regiao']) ? trim($_GET['regiao']) : null;

// 4. Montagem Dinâmica da Consulta SQL com JOINs
$sql = "SELECT 
            v.id AS venda_id,
            v.data_venda,
            v.valor_total,
            v.faixa_etaria,
            v.genero,
            v.nivel_fidelidade,
            p.nome AS produto,
            p.categoria AS produto_categoria,
            l.nome AS loja,
            l.cidade,
            l.estado,
            l.regiao
        FROM vendas_publico v
        INNER JOIN produtos p ON v.produto_id = p.id
        INNER JOIN lojas l ON v.loja_id = l.id
        WHERE 1=1";

$params = [];

// Adiciona filtros se forem informados no GET
if ($loja_id) {
    $sql .= " AND v.loja_id = :loja_id";
    $params[':loja_id'] = $loja_id;
}

if ($faixa_etaria) {
    $sql .= " AND v.faixa_etaria = :faixa_etaria";
    $params[':faixa_etaria'] = $faixa_etaria;
}

if ($regiao) {
    $sql .= " AND l.regiao = :regiao";
    $params[':regiao'] = $regiao;
}

$sql .= " ORDER BY v.data_venda DESC";

// 5. Execução do Query Preparado
try {
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $dados = $stmt->fetchAll();

    // 6. Retorno dos Dados em Formato JSON
    http_response_code(200);
    echo json_encode([
        "status" => "success",
        "total_registros" => count($dados),
        "data" => $dados
    ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        "status" => "error",
        "message" => "Erro ao executar consulta: " . $e->getMessage()
    ]);
}


?>
