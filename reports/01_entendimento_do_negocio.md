# Etapas 1 e 2 — Entendimento do negócio e definição da target

> Estas etapas são conceituais (pensamento analítico, sem código). Os números citados vêm da análise feita nos notebooks.

---

## Etapa 1 — Entendimento do negócio

### Qual problema de negócio está sendo resolvido?

A empresa cresceu rápido no e-commerce, mas a satisfação dos clientes **varia muito** e, hoje, ela só descobre se o cliente ficou satisfeito **depois** que a jornada termina, quando a pesquisa de NPS é respondida. Nesse momento, o problema já aconteceu e o cliente já formou sua opinião.

O problema, portanto, é duplo:

1. **Entender** quais fatores operacionais (pedido, logística, atendimento) realmente influenciam a satisfação.
2. **Antecipar** a insatisfação, para agir **antes** da pesquisa, e não apenas medir o estrago depois.

Em uma frase: *transformar dados operacionais em alertas e prioridades de ação para melhorar a experiência do cliente de forma preventiva.*

### Por que o NPS é importante para um e-commerce?

- **Concorrência a um clique:** no e-commerce, trocar de loja custa quase nada. A experiência é um dos poucos diferenciais que retêm o cliente.
- **Recompra é a base da rentabilidade:** adquirir um cliente novo (mídia paga, marketplace, cupons) custa muito mais do que manter um atual. Na nossa base, **100% dos promotores recompraram em 30 dias, contra 0% dos detratores**.
- **Reputação pública:** avaliações em marketplaces, no Reclame Aqui e em redes sociais influenciam diretamente a conversão de novos clientes.
- **Indicador simples e comparável:** o NPS é uma métrica única, fácil de acompanhar pela liderança e comparável com o mercado.

### Quais áreas poderiam se beneficiar desses insights?

| Área | Como usaria os insights |
|---|---|
| **Logística** | Priorizar a redução de atrasos (fator nº 1), renegociar SLA com transportadoras, avisar o cliente proativamente sobre atrasos. |
| **Atendimento (SAC)** | Resolver no primeiro contato, priorizar clientes com várias reclamações, reduzir o tempo de resolução. |
| **CRM / Retenção** | Agir com clientes em risco antes da pesquisa (contato proativo, compensação, cupom de reconquista). |
| **Produto / Tecnologia** | Melhorar o rastreamento do pedido, a comunicação de prazos e o autoatendimento. |
| **Pricing / Comercial** | Entender que desconto e frete **não** compensam uma experiência ruim, evitando gastar margem onde não há retorno. |
| **Estratégia / Diretoria** | Acompanhar um "NPS previsto" e decidir investimentos com base em impacto estimado. |

### Reflexão: como o NPS impacta...

**Recompra:** clientes promotores tendem a voltar a comprar com mais frequência e com ticket maior. Na base analisada, a relação é muito forte: **nenhum detrator recomprou em 30 dias**, contra 38% dos neutros e 100% dos promotores. Um NPS baixo significa receita recorrente perdida.

**Boca a boca:** promotores indicam a marca de forma espontânea, o que gera aquisição "gratuita". Detratores fazem o contrário: reclamam em redes sociais, no Reclame Aqui e nas avaliações dos marketplaces, e cada comentário negativo afasta potenciais clientes. No digital, o boca a boca é **escalável e permanente** (fica registrado).

**Market share:** no e-commerce, a participação de mercado depende de **conquistar e reter**. Um NPS baixo aumenta o *churn* e o custo de aquisição (é preciso gastar mais com mídia para repor os clientes perdidos). Já um NPS alto reduz o custo de aquisição pela indicação e aumenta o valor do cliente ao longo do tempo (*LTV*). No médio prazo, empresas com melhor experiência tendem a ganhar participação das concorrentes.

### Quais indicadores de mercado poderiam complementar a análise?

- **Benchmarks de NPS do setor** (varejo e e-commerce), para saber se -80 está muito distante da média do mercado (está).
- **SLA logístico do mercado:** prazo médio e taxa de entrega no prazo dos concorrentes e das transportadoras.
- **Reputação pública:** nota e índice de solução no Reclame Aqui e notas nos marketplaces.
- **Indicadores de atendimento:** taxa de resolução no primeiro contato (FCR) e tempo médio de resposta.
- **Indicadores de negócio:** taxa de recompra, churn, CAC (custo de aquisição), LTV e ticket médio.
- **Concorrência:** prazo de entrega prometido, política de frete e de troca dos principais concorrentes.
- **Sazonalidade:** períodos como Black Friday e Natal, quando o volume e os atrasos aumentam.

---

## Etapa 2 — Definição da target

### Qual variável representa a satisfação do cliente?

**`nps_score`**, a nota de 0 a 10 que o cliente dá para a pergunta *"o quanto você recomendaria a empresa para um amigo?"*.

A partir dela derivamos:
- `nps_category`: **Detrator** (0 a 6), **Neutro** (7 e 8) e **Promotor** (9 e 10), segundo a regra oficial do NPS;
- `is_detractor`: 1 se o cliente for detrator, 0 caso contrário.

### Por que ela foi escolhida?

- É a **métrica oficial** de satisfação usada pela empresa e citada no problema de negócio.
- É uma medida **padronizada** e comparável com o mercado.
- Está diretamente ligada a **comportamento**: na base, ela praticamente determina a recompra.
- Permite duas abordagens: prever a **nota** (regressão) ou a **categoria** (classificação).

O `csat_internal_score` também mede satisfação, mas é um indicador interno, não é o indicador estratégico pedido pelo negócio e, por ser coletado junto ou depois da experiência, **não pode ser usado para prever o NPS**.

### Em que momento da jornada essa informação é coletada?

**Depois do encerramento da jornada de compra**, ou seja, após a entrega e eventuais interações com o atendimento. É exatamente esse o problema: quando a nota chega, não dá mais tempo de agir sobre aquele pedido. Por isso, o objetivo do modelo é **prever** a nota com dados disponíveis **antes** da pesquisa.

### Existe algum risco de usar essa variável de forma inadequada?

Sim, vários:

1. **Vazamento de dados (*data leakage*):** usar no modelo variáveis que só existem depois da pesquisa (como `repeat_purchase_30d` e `csat_internal_score`) gera um modelo que "parece ótimo" no teste, mas é inútil na prática.
2. **Viés de resposta:** nem todo cliente responde à pesquisa. Normalmente quem está muito satisfeito ou muito insatisfeito responde mais. A base pode não representar todos os clientes.
3. **Tratar a nota como "exata":** a diferença entre um 6 e um 7 é pequena para o cliente, mas muda a categoria (detrator vs. neutro). Decisões não devem depender de diferenças mínimas de nota.
4. **Olhar só a média:** o NPS é calculado por **proporções** (% promotores - % detratores). Uma nota média pode subir sem que o NPS mude.
5. **Escala da base:** a base traz notas com casas decimais, diferente da pesquisa real (notas inteiras). Usamos limites contínuos (< 7, < 9) para classificar.
6. **Uso individual punitivo:** o NPS previsto deve ser usado para **ajudar** o cliente (ação proativa), e não para tratar clientes de forma diferente de maneira injusta ou para punir equipes sem considerar o contexto.
7. **Metas mal desenhadas:** se as equipes forem cobradas só pelo NPS, podem surgir incentivos errados (ex.: pedir nota alta ao cliente, enviar a pesquisa só para quem parece satisfeito).
