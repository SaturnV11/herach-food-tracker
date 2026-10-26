# Herach Food Tracker

Aplicação web/PWA em português brasileiro, mobile-first, com sete telas, IndexedDB, service worker, API autenticada e banco SQLite. Sem dependências de produção ou etapa de build. Requer **Node.js 24 ou superior**.

## Instalar e executar

Abra um terminal nesta pasta:

```powershell
node server.mjs
```

Abra **http://localhost:4173**. Alternativamente execute `iniciar.cmd` no Windows. Não é necessário executar npm install. Se npm estiver instalado, `npm start` equivale ao comando acima.

```powershell
node --test tests/domain.test.mjs tests/server.test.mjs tests/validation.test.mjs tests/offline.test.mjs
node --check public/app.js
node --check server.mjs
```

`PORT` altera a porta, `HOST` altera o endereço de escuta e `DB_PATH` altera a localização do banco. Por padrão o servidor só atende este computador. Para usar no celular, hospede em servidor Node com **HTTPS**, volume persistente para o banco e proxy reverso. HTTPS é necessário para service worker e instalação PWA fora de localhost. Configure `COOKIE_SECURE=1` em HTTPS e encaminhe `X-Forwarded-Proto: https` pelo proxy confiável. O proxy deve preservar Host e sobrescrever cabeçalhos encaminhados. A aplicação não configura certificado, domínio ou hospedagem automaticamente.

## Primeira utilização

O cardápio já foi importado do arquivo real `../output/pdf/Herach_Cardapio_Semanal_Enxuto.pdf` e está disponível em **Cardápio → Abrir PDF original**. A extração está reproduzível em `extract_menu.py` (requer pypdf apenas para reimportar). Nenhum arquivo em `sources/` foi alterado.

O PDF informa alimentos, quantidades e carboidratos estimados por refeição. Ele **não informa nutrientes individuais**. Por isso calorias, proteínas, carboidratos, gorduras e fibras dos alimentos começam ausentes. Não se distribuem os carboidratos estimados da refeição entre os alimentos, pois isso inventaria precisão.

1. Em **Alimentos e receitas**, edite os alimentos com a composição do rótulo e sua base (por exemplo, nutrientes por 100 ml). Campo vazio é desconhecido; zero é zero conhecido. Cadastre a marca/fonte do leite, que já está identificado no catálogo em ml.
2. Em **Hoje**, marque itens consumidos ou use “•••” para ajustar quantidade, substituir alimento, marcar “não consumi” ou voltar a pendente. “Registrar tudo” registra somente pendências; “Desfazer” torna os itens da refeição pendentes. Registros parciais existentes são respeitados ao completar a refeição.
3. Adicione extras pelo botão fixo. Os atalhos de leite abrem uma confirmação de quantidade/alimento; leite de todas as refeições e extras soma no total diário.
4. Encerre o dia quando terminar; reabra para editar. Encerrar não resolve pendências automaticamente. O check da refeição significa registro completo, incluindo itens não consumidos.
5. Em **Semana**, veja os três indicadores. Calorias/proteína ficam cinza enquanto o dia estiver aberto, incompleto ou tiver nutrientes ausentes. Somente dias encerrados e completos recebem classificação pelas faixas. O indicador de refeições mostra 0/4 a 4/4 independentemente de metas.
6. Em **Configurações**, ajuste metas, faixas e atalhos. A vigência cria uma nova versão para novos dias. Dias iniciados preservam a meta e o plano de quando foram registrados pela primeira vez. Editar um plano afeta os próximos dias ainda não iniciados.
7. **Calculadoras** oferece nutrientes por porção e conversão cru/preparado com rendimento informado. **Compras** soma as porções planejadas da semana, com checks locais. Não converte automaticamente peso preparado em cru e não inclui extras.

Receitas aceitam vários ingredientes, rendimento final e unidade. Nutrientes ausentes em qualquer ingrediente continuam ausentes naquele nutriente da receita. O rendimento deve ser medido e informado. O registro de consumo guarda cópia da composição e da versão da receita; editar o catálogo não altera registros anteriores.

Os 2.600 kcal e 150 g de proteína são referências do guia, não metas clínicas personalizadas. A aplicação não calcula nem recomenda doses de insulina e não inclui acompanhamento esportivo.

## Offline e instalação PWA

Após a primeira abertura online, o service worker armazena a interface e o PDF; o IndexedDB mantém catálogo, dias, snapshots e fila de operações. Fechar e reabrir o navegador preserva os dados. Login e sincronização precisam de conexão; registrar, editar, calcular, consultar e exportar funcionam offline. Aguarde o primeiro carregamento terminar antes de desconectar.

No Chrome/Edge para Android, use “Instalar aplicativo” ou “Adicionar à tela inicial”. No Safari do iPhone, Compartilhar → Adicionar à Tela de Início. A disponibilidade depende do navegador e de HTTPS. A instalação no sistema operacional não foi automatizada. Limpar dados do site ou usar navegação privada pode remover os registros; exporte backups JSON regularmente. Não existe promessa de armazenamento permanente do navegador.

## Sincronização autenticada

Em Configurações, crie uma conta com e-mail e senha de pelo menos 12 caracteres, ou entre e clique **Sincronizar agora**. É uma implementação real de autenticação própria, não uma conexão com conta Google/OpenAI. A sincronização é **manual**; a fila permanece offline até a próxima sincronização solicitada. Não usa credenciais externas.

Senhas passam por scrypt com salt exclusivo. Sessões usam tokens aleatórios, com apenas o hash no banco; cookie HttpOnly, SameSite=Strict e validade de 30 dias. O servidor verifica a origem em alterações e limita tentativas de autenticação por endereço. Todas as consultas de registros e operações têm escopo do usuário autenticado. Use perfis de navegador separados para contas diferentes: o perfil local é vinculado ao primeiro e-mail sincronizado e recusa outra conta.

Cada alteração tem UUID de operação e revisão-base. O banco aplica o lote em transação. Repetir um UUID confirma a operação sem reaplicá-la. Se a mesma chave mudou em outro dispositivo desde a revisão-base, o lote é recusado sem escrita parcial. A unidade de conflito é um dia inteiro ou o catálogo inteiro; não há fusão automática de itens concorrentes. Dados locais pendentes são preservados durante a resposta da sincronização.

Ao encontrar conflito, exporte backup e use a seção de resolução em Configurações. “Manter versão deste dispositivo” reenvia as alterações locais contra a revisão atual; “Usar versão do servidor” descarta as pendências locais e usa a versão remota. Ao começar em outro dispositivo com dados já existentes na conta, prefira “Usar versão do servidor”.

### API

| Método | Rota | Corpo / resposta |
|---|---|---|
| POST | `/api/register` | `{email,password}`; cria conta e sessão |
| POST | `/api/login` | `{email,password}`; cria sessão |
| POST | `/api/logout` | `{}`; invalida sessão |
| GET | `/api/me` | e-mail da conta autenticada |
| GET | `/api/sync` | `{revision,entries,acked}` |
| POST | `/api/sync` | `{operations:[{id,key,baseRevision,value}]}` |

`key` é `catalog` ou `day:AAAA-MM-DD`. Valores seguem schema v1, validado por `public/validation.js` tanto na importação quanto na API. Erros usam status HTTP e `{error}`. Conflito responde `{conflict:true,revision,acked:[],entries:{}}`. Lotes têm limite de 2.000 operações e 8 MB; sincronize regularmente. Não há CORS entre origens: a API atende na mesma origem da interface.

SQLite em `data/herach.sqlite`, com WAL, tabelas `users`, `sessions`, `entries` e `operations`. Não versione o banco. Faça backup consistente via SQLite backup/VACUUM INTO, ou pare o servidor antes de copiar o banco e seus arquivos associados. Use uma instância com volume persistente; múltiplas réplicas precisam de coordenação de armazenamento.

## Exportação

- **CSV**: histórico completo, itens pendentes/não consumidos/consumidos e extras; valores calculados usando snapshots; desconhecidos em branco; separador `;`, UTF-8 com BOM, aspas escapadas e proteção contra fórmulas.
- **PDF**: Configurações → Imprimir / salvar PDF. Abre relatório próprio de todos os dias registrados, refeições, extras, totais parciais e versão da meta. Escolha “Salvar como PDF” na impressão do navegador. Não usa serviço externo. Não produz download binário de PDF automaticamente.
- **JSON**: backup integral; a restauração valida o schema, pede confirmação e substitui dados locais. Credenciais de sessão não entram no arquivo. O vínculo de conta do navegador não é alterado pela importação.

## Camadas e arquivos

| Arquivo | Responsabilidade |
|---|---|
| `public/app.js`, `style.css`, `index.html` | sete telas, formulários e acessibilidade |
| `public/domain.js` | porções, snapshots, totais, metas, cores, receitas, compras e CSV |
| `public/validation.js` | contratos e validação nas fronteiras |
| `public/store.js` | IndexedDB, fila offline e cliente de sincronização |
| `public/sw.js`, `manifest.webmanifest` | cache offline e instalação PWA |
| `server.mjs` | HTTP, autenticação, API, transações SQLite |
| `public/seed.json`, `cardapio.pdf` | catálogo e cardápio de origem |
| `tests/` | cálculos, snapshots, autenticação, conflitos, idempotência e validação |

## Integrações e limites da entrega

Funcionam localmente o servidor, banco, autenticação, sincronização entre navegadores que acessem a mesma instância, persistência offline e exportação. Não foram configurados hospedagem pública, HTTPS, provedor de e-mail, recuperação/verificação de e-mail, login social, base nutricional externa, leitura automática de rótulos ou observabilidade externa. O catálogo precisa de dados nutricionais fornecidos pelo usuário. A importação PDF inicial é uma transcrição específica do documento disponível, não um parser genérico de qualquer PDF.

A aplicação trata os registros como dados pessoais e não envia nada a serviços externos. O servidor e o armazenamento local não implementam criptografia em repouso; proteja o dispositivo, o volume e seus backups. Conta local não substitui os controles da hospedagem. Para disponibilização na internet, configure HTTPS, cookies seguros, política de backup e recuperação de conta conforme sua operação.

Verificação executada: 20 testes automatizados aprovados, incluindo testes de domínio/API e conferência da interface no navegador. Instalação PWA em Android/iOS, impressão em cada navegador, e modo avião em aparelho físico exigem validação no dispositivo de destino.
