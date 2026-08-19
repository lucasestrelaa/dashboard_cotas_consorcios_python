-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Tempo de geração: 19/08/2026 às 16:52
-- Versão do servidor: 11.8.8-MariaDB-log
-- Versão do PHP: 7.2.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Banco de dados: `u856143160_dados`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `fluxo_loja`
--

CREATE TABLE `fluxo_loja` (
  `id` int(11) NOT NULL,
  `loja_id` int(11) NOT NULL,
  `data_registro` date NOT NULL,
  `fluxo_visitantes` int(11) NOT NULL COMMENT 'Quantidade total de pessoas que entraram na loja',
  `tme` int(11) NOT NULL COMMENT 'Tempo Médio de Espera em segundos',
  `tmi` int(11) NOT NULL COMMENT 'Tempo Médio de Interação/Atendimento em segundos',
  `taxa_conversao` decimal(5,2) DEFAULT NULL COMMENT 'Percentual de visitantes que compraram (%)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Despejando dados para a tabela `fluxo_loja`
--

INSERT INTO `fluxo_loja` (`id`, `loja_id`, `data_registro`, `fluxo_visitantes`, `tme`, `tmi`, `taxa_conversao`) VALUES
(1, 1, '2026-08-10', 1200, 180, 420, 15.50),
(2, 1, '2026-08-11', 1350, 210, 390, 18.20),
(3, 2, '2026-08-10', 850, 120, 300, 22.00),
(4, 3, '2026-08-10', 960, 150, 350, 12.80),
(5, 4, '2026-08-10', 1100, 240, 480, 14.10);

-- --------------------------------------------------------

--
-- Estrutura para tabela `lojas`
--

CREATE TABLE `lojas` (
  `id` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `cidade` varchar(100) NOT NULL,
  `estado` char(2) NOT NULL,
  `regiao` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Despejando dados para a tabela `lojas`
--

INSERT INTO `lojas` (`id`, `nome`, `cidade`, `estado`, `regiao`) VALUES
(1, 'Loja Centro', 'São Paulo', 'SP', 'Sudeste'),
(2, 'Loja Shopping Beira Mar', 'Florianópolis', 'SC', 'Sul'),
(3, 'Loja Savassi', 'Belo Horizonte', 'MG', 'Sudeste'),
(4, 'Loja Barra', 'Salvador', 'BA', 'Nordeste');

-- --------------------------------------------------------

--
-- Estrutura para tabela `produtos`
--

CREATE TABLE `produtos` (
  `id` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `categoria` varchar(50) NOT NULL,
  `preco_unitario` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Despejando dados para a tabela `produtos`
--

INSERT INTO `produtos` (`id`, `nome`, `categoria`, `preco_unitario`) VALUES
(1, 'Smartphone X', 'Eletrônicos', 2500.00),
(2, 'Tênis Performance', 'Calçados', 450.00),
(3, 'Cadeira Ergonômica', 'Móveis', 890.00),
(4, 'Fone Bluetooth', 'Acessórios', 200.00);

-- --------------------------------------------------------

--
-- Estrutura para tabela `vendas_publico`
--

CREATE TABLE `vendas_publico` (
  `id` int(11) NOT NULL,
  `loja_id` int(11) NOT NULL,
  `produto_id` int(11) NOT NULL,
  `data_venda` datetime NOT NULL,
  `valor_total` decimal(10,2) NOT NULL,
  `faixa_etaria` varchar(20) NOT NULL COMMENT 'Ex: 18-25, 26-35, 36-50, 50+',
  `genero` varchar(20) NOT NULL COMMENT 'Feminino, Masculino, Outro',
  `nivel_fidelidade` varchar(20) NOT NULL COMMENT 'Novo, Ocasional, VIP'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Despejando dados para a tabela `vendas_publico`
--

INSERT INTO `vendas_publico` (`id`, `loja_id`, `produto_id`, `data_venda`, `valor_total`, `faixa_etaria`, `genero`, `nivel_fidelidade`) VALUES
(1, 1, 1, '2026-08-10 10:15:00', 2500.00, '26-35', 'Masculino', 'VIP'),
(2, 1, 2, '2026-08-10 11:30:00', 450.00, '18-25', 'Feminino', 'Novo'),
(3, 2, 3, '2026-08-10 14:20:00', 890.00, '36-50', 'Feminino', 'Ocasional'),
(4, 3, 4, '2026-08-10 15:45:00', 200.00, '18-25', 'Masculino', 'Novo'),
(5, 4, 1, '2026-08-10 16:10:00', 2500.00, '26-35', 'Feminino', 'VIP'),
(6, 1, 4, '2026-08-11 09:50:00', 200.00, '50+', 'Masculino', 'Ocasional');

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `fluxo_loja`
--
ALTER TABLE `fluxo_loja`
  ADD PRIMARY KEY (`id`),
  ADD KEY `loja_id` (`loja_id`);

--
-- Índices de tabela `lojas`
--
ALTER TABLE `lojas`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `produtos`
--
ALTER TABLE `produtos`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `vendas_publico`
--
ALTER TABLE `vendas_publico`
  ADD PRIMARY KEY (`id`),
  ADD KEY `loja_id` (`loja_id`),
  ADD KEY `produto_id` (`produto_id`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `fluxo_loja`
--
ALTER TABLE `fluxo_loja`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de tabela `lojas`
--
ALTER TABLE `lojas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de tabela `produtos`
--
ALTER TABLE `produtos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de tabela `vendas_publico`
--
ALTER TABLE `vendas_publico`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Restrições para tabelas despejadas
--

--
-- Restrições para tabelas `fluxo_loja`
--
ALTER TABLE `fluxo_loja`
  ADD CONSTRAINT `fluxo_loja_ibfk_1` FOREIGN KEY (`loja_id`) REFERENCES `lojas` (`id`);

--
-- Restrições para tabelas `vendas_publico`
--
ALTER TABLE `vendas_publico`
  ADD CONSTRAINT `vendas_publico_ibfk_1` FOREIGN KEY (`loja_id`) REFERENCES `lojas` (`id`),
  ADD CONSTRAINT `vendas_publico_ibfk_2` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`);
COMMIT;
